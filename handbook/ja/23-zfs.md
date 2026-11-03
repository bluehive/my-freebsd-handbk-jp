<a id="zfs"></a>
# 第23章 Z File System（ZFS）

> 翻訳作業中：本ファイルは導入・クイックスタートまでの作業稿です。ZFS章全体は未完了です。

ZFSは、従来のストレージ管理の課題を解決するために設計された高度なファイルシステムです。Sun Microsystemsで開発が始まり、現在のオープンソース開発は[OpenZFSプロジェクト](https://openzfs.org)が担っています。

主な設計目標は三つあります。

- **データの完全性**：データとともに[チェックサム](#zfs-term-checksum)を保存し、読み取り時に再計算して照合します。不一致を検出すると、追加の複製、ミラー、パリティなどの冗長情報があれば修復を試みます。チェックサムだけで、失われたデータを必ず復元できるわけではありません。
- **プール化したストレージ**：物理デバイスをプールへまとめ、各ファイルシステムやボリュームはそこから容量を使います。デバイスを追加すれば、共有する容量を増やせます。
- **性能**：メモリ上の読み取りキャッシュ[ARC](#zfs-term-arc)、補助デバイス上の読み取りキャッシュ[L2ARC](#zfs-term-l2arc)、同期書き込みを扱う[ZIL](#zfs-term-zil)などを利用します。原文はZILを同期書き込みキャッシュと呼びますが、汎用の書き込みキャッシュというより、同期書き込みの回復に使うインテントログです。詳しくは後述します。

機能の一覧と用語は[ZFSの機能と用語](#zfs-term)を参照してください。

<a id="zfs-differences"></a>
## ZFSは何が違うのか

ZFSはファイルシステムだけでなく、従来は別々だったボリューム管理も一体化しています。UFSのような従来のファイルシステムは、ハードウェアRAIDやGEOMで複数ディスクをまとめても、通常は一つの論理デバイスとして扱います。ZFSはその下の構成を把握し、複数のファイルシステムが同じプールの空き容量を共有できます。

プールへストレージを追加すると、その容量は各ファイルシステムでも利用できるようになります。各ファイルシステムに固定の領域を先に切り出しておく方式とは異なります。ただし、クォータや予約などの制約は別途適用されます。

データセットごとに異なるプロパティも設定できます。一つの巨大なファイルシステムにまとめるより、用途別に分けて圧縮や保存方針などを管理しやすいことも利点です。

<a id="zfs-quickstart"></a>
## クイックスタート

インストーラは、システムのルートをZFSへ置くRoot-on-ZFSに対応しています。[インストール時のZFS設定](02-bsdinstall.md#bsdinstall-part-zfs)を参照してください。ここでは、稼働中のシステムへ追加のプールとデータセットを作る手順を説明します。

起動時にZFSを扱うサービスを有効にします。

```shell
# sysrc zfs_enable="YES"
```

`/etc/rc.conf` に `zfs_enable="YES"` が設定されます。`service zfs enable` でも同じ有効化設定を行えます。続いてサービスを起動します。

```shell
# service zfs start
```

以下の例は、SATAディスク `ada0`、`ada1`、`ada2` を想定しています。SCSI/SASなら通常 `da`、NVMeなら原文では `nda` を使います。**名前は例なので、実際のデバイスと用途を確認してください。パーティション作成・プール作成・破棄の操作は、既存データを失う原因になります。**

<a id="zfs-quickstart-single-disk-pool"></a>
### 単一ディスクのプール

まず空のディスクにGPTを作り、`freebsd-zfs` パーティションから単一ディスクのプールを作ります。この例にはディスク故障に備える冗長性がありません。

```shell
# gpart create -s gpt ada1
# gpart add -t freebsd-zfs ada1
# zpool create example /dev/ada1p1
```

`df` で確認します。

```shell
# df /example
Filesystem     1K-blocks    Used    Avail Capacity  Mounted on
example         17547136       0 17547136     0%    /example
```

`example` が作成・マウントされ、ファイルシステムとして使える状態です。ファイルを作って確かめます。

```shell
# cd /example
# ls
# touch testfile
# ls -al
total 4
drwxr-xr-x   2 root  wheel    3 Aug 29 23:15 .
drwxr-xr-x  21 root  wheel  512 Aug 29 23:12 ..
-rw-r--r--   1 root  wheel    0 Aug 29 23:15 testfile
```

次は圧縮を有効にしたデータセットを作る例です。

```shell
# zfs create example/compressed
# zfs set compression=gzip example/compressed
```

`/example/compressed` へ大きなファイルをコピーして試せます。圧縮を無効にするには次を使います。プロパティの変更は今後書くデータへ適用され、既存データ全体をその場で書き換える操作ではありません。

```shell
# zfs set compression=off example/compressed
```

アンマウントしてdfで確認します。

```shell
# zfs umount example/compressed
# df
Filesystem   1K-blocks    Used    Avail Capacity  Mounted on
example       17547008       0 17547008     0%    /example
```

再び利用するにはマウントします。

```shell
# zfs mount example/compressed
# df
Filesystem         1K-blocks    Used    Avail Capacity  Mounted on
example             17547008       0 17547008     0%    /example
example/compressed  17547008       0 17547008     0%    /example/compressed
```

`mount` でも、プール内のファイルシステムとマウント先を確認できます。

```shell
# mount
/dev/ada0p1 on / (ufs, local)
devfs on /dev (devfs, local)
/dev/ada0p2 on /usr (ufs, local, soft-updates)
example on /example (zfs, local)
example/compressed on /example/compressed (zfs, local)
```

作成後は通常のファイルシステムとして使え、必要な機能をデータセット単位で設定できます。次は `data` を作り、各データブロックを2コピー保存する例です。**同じプール内の追加コピーは、別媒体へのバックアップやディスク全体の故障への冗長化の代わりにはなりません。**

```shell
# zfs create example/data
# zfs set copies=2 example/data
```

使用量と空き容量を表示します。

```shell
# df
Filesystem        1K-blocks    Used    Avail Capacity  Mounted on
/dev/ada0p1         2026030  235234  1628714    13%    /
devfs                     1       1        0   100%    /dev
/dev/ada0p2        54098308 1032864 48737580     2%    /usr
example            17547008       0 17547008     0%    /example
example/compressed 17547008       0 17547008     0%    /example/compressed
example/data       17547008       0 17547008     0%    /example/data
```

各ファイルシステムが同じプールの空き容量を使うため、例では同じ空き容量が見えます。パーティションごとに容量を固定配分する必要を減らせますが、ZFSにもブロックデバイスを提供するボリュームという機能はあります。

不要になったファイルシステムとプールを破棄する例です。**保存内容を失う操作なので、必要なデータがないことを確認してから実行します。**

```shell
# zfs destroy example/compressed
# zfs destroy example/data
# zpool destroy example
```

<a id="zfs-quickstart-raid-z"></a>
### RAID-Z

ディスクは故障するため、ZFSはミラーやRAID-Zによる冗長化を提供します。RAID-Zは、パリティを利用して、ミラーより容量効率を高められる場合があります。原文は3台以上の構成を説明しています。

以下は3台の空ディスクへGPTと `freebsd-zfs` パーティションを作り、`raidz` を指定する例です。**既存のOSやデータがあるディスクには実行しないでください。**

```shell
# gpart create -s gpt ada0
# gpart add -t freebsd-zfs ada0
# gpart create -s gpt ada1
# gpart add -t freebsd-zfs ada1
# gpart create -s gpt ada2
# gpart add -t freebsd-zfs ada2
# zpool create storage raidz ada0p1 ada1p1 ada2p1
```

原文は一つのRAID-Zグループを3〜9台程度とし、10台以上なら小さいグループへ分ける構成も検討するよう勧めています。2台ならミラーが選択肢です。これはすべての負荷・機器に最適な台数を決める規則ではありません。詳細は `zpool(8)` と後述の構成説明を確認してください。

作ったstorageプールに、homeデータセットを追加します。

```shell
# zfs create storage/home
```

追加コピーと圧縮を設定します。

```shell
# zfs set copies=2 storage/home
# zfs set compression=gzip storage/home
```

原文は、ユーザーデータをコピーしてホームディレクトリへのリンクを作る例として、次を掲載しています。**この例は `/home` と `/usr/home` を再帰削除します。そのまま実行せず、元データとコピーの検証、隠しファイル、既存マウントやリンク、ログイン中ユーザーへの影響を確認し、復旧可能な状態で移行してください。** `*` では通常、直下のドットで始まる項目をコピーしない点にも注意します。

```shell
# cp -rp /home/* /storage/home
# rm -rf /home /usr/home
# ln -s /storage/home /home
# ln -s /storage/home /usr/home
```

移行後は `/storage/home` を使う構成になり、新しいユーザーを作成してログインできるか確認します。

後で戻せるよう、スナップショットを作成します。

```shell
# zfs snapshot storage/home@2026-07-11
```

スナップショットは単一ファイル・ディレクトリではなく、データセットのある時点を記録します。`@` の前がファイルシステムまたはボリューム、後ろがスナップショット名です。重要な変更前にはバックアップも確保します。次のロールバックでは、指定時点より後の変更が失われるため、戻す範囲を確認してください。

```shell
# zfs rollback storage/home@2026-07-11
```

ファイルシステムの `.zfs/snapshot` からスナップショット一覧を確認できます。

```shell
# ls /storage/home/.zfs/snapshot
```

定期取得はスクリプト化できますが、保持する間の変更に応じて容量を消費します。不要なスナップショットを削除する例です。

```shell
# zfs destroy storage/home@2026-07-11
```

テスト後、データセット自体のマウント先を `/home` に設定する原文の例です。先ほど作ったリンクを含め、既存のマウント先の状態を整理してから適用します。

```shell
# zfs set mountpoint=/home storage/home
```

`mount` と `df` で実際の接続先を確認します。

```shell
# mount
/dev/ada0p1 on / (ufs, local)
devfs on /dev (devfs, local)
/dev/ada0p2 on /usr (ufs, local, soft-updates)
storage on /storage (zfs, local)
storage/home on /home (zfs, local)
# df
Filesystem   1K-blocks    Used    Avail Capacity  Mounted on
/dev/ada0p1    2026030  235240  1628708    13%    /
devfs                1       1        0   100%    /dev
/dev/ada0p2   54098308 1032826 48737618     2%    /usr
storage       26320512       0 26320512     0%    /storage
storage/home  26320512       0 26320512     0%    /home
```

日次のperiodic処理で状態報告を受けるには、`/etc/periodic.conf` に次を追加します。

```text
daily_status_zfs_enable="YES"
```

periodicでは[定期的なスクラブ](#zfs-zpool-scrub)も設定できます。

<a id="zfs-quickstart-recovering-raid-z"></a>
### RAID-Zの障害から復旧する

プールの状態を確認します。

```shell
# zpool status -x
```

すべて正常なら次の表示になります。

```text
all pools are healthy
```

一つのデバイスがオフラインの場合などは、次のように表示されます。

```text
  pool: storage
 state: DEGRADED
status: One or more devices has been taken offline by the administrator.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Online the device using 'zpool online' or replace the device with
        'zpool replace'.
  scan: none requested
config:

        NAME        STATE     READ WRITE CKSUM
        storage     DEGRADED     0     0     0
          raidz1-0  DEGRADED     0     0     0
            ada0p1  ONLINE       0     0     0
            ada1p1  OFFLINE      0     0     0
            ada2p1  ONLINE       0     0     0

errors: No known data errors
```

この例のOFFLINEは、管理者が次の操作で `ada1p1` を切り離した状態です。実際の故障と、管理操作によるオフラインを区別します。

```shell
# zpool offline storage ada1p1
```

原文はコンピュータを停止して対象ディスクを交換し、新しいディスクに同じ用途のGPTと `freebsd-zfs` パーティションを作り直す手順を説明しています。交換後に起動し、次の操作で置き換えます。デバイス名が変わる構成では、対象を取り違えないよう確認します。

```shell
# zpool replace storage ada1p1
```

`-x` を付けずに対象プールを表示し、resilverと状態を確認します。

```shell
# zpool status storage
  pool: storage
 state: ONLINE
  scan: resilvered 3.21G in 00:04:36 with 0 errors on Sat Jul 11 10:32:19 2026
config:

        NAME        STATE     READ WRITE CKSUM
        storage     ONLINE       0     0     0
          raidz1-0  ONLINE       0     0     0
            ada0p1  ONLINE       0     0     0
            ada1p1  ONLINE       0     0     0
            ada2p1  ONLINE       0     0     0

errors: No known data errors
```

例では再構築がエラーなく終わり、全デバイスがONLINEへ戻っています。

<a id="zfs-quickstart-data-verification"></a>
### データの検証

ZFSは、作成時から有効になるチェックサムで保存データを検証します。**チェックサムの無効化は推奨されません。** 少ない保存容量で完全性を確認でき、多くのZFS機能もチェックサムを前提とします。原文は無効化しても目立った性能向上はないと注意しています。

プール全体の保存データを読み、チェックサムを確認する処理を**スクラブ**と呼びます。

```shell
# zpool scrub storage
```

時間は保存量や機器の性能などに依存し、I/O負荷がかかります。一つのプールで同時に動くスクラブは一つです。終了後に状態を確認します。

```shell
# zpool status storage
  pool: storage
 state: ONLINE
  scan: scrub repaired 0B in 00:19:16 with 0 errors on Sat Jul 11 10:32:19 2026
config:

        NAME        STATE     READ WRITE CKSUM
        storage     ONLINE       0     0     0
          raidz1-0  ONLINE       0     0     0
            ada0p1  ONLINE       0     0     0
            ada1p1  ONLINE       0     0     0
            ada2p1  ONLINE       0     0     0

errors: No known data errors
```

前回の完了日時とエラーの有無を見て、次の実施時期を判断します。冗長な正常データがあれば修復できますが、検出したすべての破損を必ず修復できるわけではありません。
