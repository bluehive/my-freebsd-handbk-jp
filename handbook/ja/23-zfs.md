<a id="zfs"></a>
# 第23章 Z File System（ZFS）

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

<a id="zfs-zpool"></a>
## zpoolによるプール管理

ZFSの主な管理コマンドは二つです。`zpool` はプールと、それを構成するディスクの追加・削除・交換などを扱います。[zfsコマンド](#zfs-zfs)は、ファイルシステムやボリュームといったデータセットを作成・削除・管理します。

<a id="zfs-zpool-create"></a>
### ストレージプールを作成・破棄する

作成時に重要なのは、物理ディスクをどの種類の[vdev](#zfs-term-vdev)へまとめるかです。冗長性、容量、性能に影響します。構成を後から変えられる場合もありますが、変更には時間とI/O帯域が必要です。

ミラーにはディスクを追加でき、単独ディスクのvdevをミラーへ変更することもできます。RAID-Zは[RAID-Z拡張](#zfs-zpool-raidz-expansion)で一台ずつ増やせますが、OpenZFS 2.3以降が必要で、FreeBSDでは15.0から利用できます。新しいvdevの追加でプールを増やせる一方、[トップレベルvdevの削除](#zfs-zpool-attach)には制約があります。

`freebsd-zfs` 型のGPTパーティションを二つ使い、ミラーを作る例です。**以下のデバイスは例であり、既存の必要なデータを含まないことを確認してから操作します。**

```shell
# zpool create mypool mirror /dev/ada1p1 /dev/ada2p1
# zpool status
  pool: mypool
 state: ONLINE
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada1p1  ONLINE       0     0     0
            ada2p1  ONLINE       0     0     0

errors: No known data errors
```

一度に複数vdevを指定するときは、各グループの前に種類を記載します。次は二つのミラーからなるプールです。

```shell
# zpool create mypool mirror /dev/ada1p1 /dev/ada2p1 mirror /dev/ada3p1 /dev/ada4p1
# zpool status
  pool: mypool
 state: ONLINE
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada1p1  ONLINE       0     0     0
            ada2p1  ONLINE       0     0     0
          mirror-1  ONLINE       0     0     0
            ada3p1  ONLINE       0     0     0
            ada4p1  ONLINE       0     0     0

errors: No known data errors
```

ディスク全体だけでなく、パーティションも利用できます。同じディスクにブートコードや別用途の領域を置け、プールを構成するディスクから起動することも可能です。原文は、FreeBSDではパーティションを使うこと自体による性能上の不利はないと説明しています。

公称容量いっぱいより少し小さいパーティションを作っておけば、後の交換品が同じ公称容量でも実容量がわずかに小さい場合に、収まる余地を残せます。次は六つのパーティションを使う[RAID-Z2](#zfs-term-vdev-raidz)の例です。

```shell
# zpool create mypool raidz2 /dev/ada0p1 /dev/ada1p1 /dev/ada2p1 /dev/ada3p1 /dev/ada4p1 /dev/ada5p1
# zpool status
  pool: mypool
 state: ONLINE
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          raidz2-0  ONLINE       0     0     0
            ada0p1  ONLINE       0     0     0
            ada1p1  ONLINE       0     0     0
            ada2p1  ONLINE       0     0     0
            ada3p1  ONLINE       0     0     0
            ada4p1  ONLINE       0     0     0
            ada5p1  ONLINE       0     0     0

errors: No known data errors
```

最小書き込みのサイズと位置合わせには、セクタサイズの2を底とする対数である `ashift` を使います。通常はデバイスの報告値から決定しますが、内部では4096バイトなのに互換性のため512バイトと報告する機器もあります。その場合に4096バイト境界を指定する例です。

```shell
# zpool create -o ashift=12 mypool mirror /dev/ada1p1 /dev/ada2p1
```

`vfs.zfs.vdev.min_auto_ashift=12` をsysctlで設定する方法もあり、後の `zpool add` や `zpool attach` にも適用できます。**ashiftはプール全体ではなく各vdevの属性で、作成後に変更できません。** データを保存する前に確認します。

不要なプールの破棄には、その中のファイルシステムをアンマウントする必要があります。使用中なら通常は失敗し、プールは残ります。`-f` で強制できますが、開いたファイルを使うアプリケーションの動作が不定になるおそれがあります。破棄は内容を失う操作なので、必要なデータと利用中の処理を確認してから行います。

<a id="zfs-zpool-props"></a>
### プールのプロパティ

プールにも状態を示すプロパティと、動作を指定するプロパティがあります。すべてを見るには `zpool get all mypool`、個別に見るには名前を指定します。

```shell
# zpool get health,capacity mypool
NAME    PROPERTY  VALUE   SOURCE
mypool  health    ONLINE  -
mypool  capacity  27%     -
```

書き込み可能な値は `zpool set` で変更します。

```shell
# zpool set comment="Backup pool" mypool
# zpool get comment mypool
NAME    PROPERTY  VALUE        SOURCE
mypool  comment   Backup pool  local
```

`size`、`capacity`、`fragmentation`、`health` などは読み取り専用です。一方、`autoexpand` は[容量の自動拡張](#zfs-zpool-online)、`autoreplace` は[スペアへの自動交換](#zfs-zpool-spares)、`autotrim` は[TRIM](#zfs-zpool-trim)、`compatibility` は[ほかのシステムとの互換性](#zfs-zpool-upgrade)に関係します。作成時は `zpool create -o` でも指定できます。全プロパティは `zpoolprops(7)` を参照してください。

<a id="zfs-zpool-attach"></a>
### デバイスを追加・取り外しする

ディスクを増やす方法は、既存vdevへ `zpool attach` で追加する方法と、新しいvdevを `zpool add` でプールへ追加する方法です。vdevの種類で制約が異なり、RAID-Zは[専用の拡張機能](#zfs-zpool-raidz-expansion)を使います。

単独ディスクは破損を検出しても、正常な別コピーがなければ修復できません。`copies` による追加コピーは不良セクタのような局所障害からの復旧に役立つ場合がありますが、ミラーやRAID-Zと同じ故障保護ではありません。

`zpool attach` で単独ディスクをミラーにしたり、ミラーへさらにディスクを加えて冗長性や読み取り性能を高めたりできます。パーティションを使うなら、`gpart backup`・`gpart restore` などで対応する配置を用意します。次は `ada0p3` に `ada1p3` を付けてミラーへ変える例です。

```shell
# zpool status
  pool: mypool
 state: ONLINE
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          ada0p3    ONLINE       0     0     0

errors: No known data errors
# zpool attach mypool ada0p3 ada1p3
Make sure to wait until resilver is done before rebooting.
# gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ada1
partcode written to ada1p1
bootcode written to ada1
# zpool status
  pool: mypool
 state: ONLINE
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Sat Jul 11 11:15:25 2026
        738M scanned at 105M/s, 522M issued at 74.6M/s, 781M total
        522M resilvered, 66.84% done, 00:00:03 to go
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0  (resilvering)

errors: No known data errors
# zpool status
  pool: mypool
 state: ONLINE
  scan: resilvered 781M in 00:00:16 with 0 errors on Sat Jul 11 11:18:36 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0

errors: No known data errors
```

**再起動はresilverの完了を待ちます。** ブートプールなら、新しいディスクの起動設定も必要です。掲載する `pmbr`・`gptzfsboot` の書き込みはBIOS/GPT構成の例であり、UEFIなどの別方式へそのまま流用しないでください。

既存vdevを増やせない場合などは、別のvdevを追加します。書き込みをvdev間へ分散することで性能・容量を増やせますが、冗長性は各vdevがそれぞれ提供します。**ミラーやRAID-Zのプールへ冗長性のないデータvdevを加えると、その一台の故障がプール全体の喪失につながります。** 種類の混在も可能ですが、原文は推奨していません。

二つのミラーvdevへ分散する構成は、RAID 10に似ています。原文は各vdevの空きが同時に尽きるよう容量配分を調整すると説明し、空き容量に差が大きいと、空きの多いvdevへ書き込みが偏って性能が下がる場合があるとしています。

次は、既存ミラーへディスクを付け足すのではなく、**新たなミラーvdevをプールへ追加する**例です。

```shell
# zpool status
  pool: mypool
 state: ONLINE
  scan: resilvered 781M in 00:00:16 with 0 errors on Sat Jul 11 12:11:56 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0

errors: No known data errors
# zpool add mypool mirror ada2p3 ada3p3
# gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ada2
partcode written to ada2p1
bootcode written to ada2
# gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ada3
partcode written to ada3p1
bootcode written to ada3
# zpool status
  pool: mypool
 state: ONLINE
  scan: resilvered 781M in 00:00:16 with 0 errors on Sat Jul 11 09:58:28 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
          mirror-1  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0
            ada3p3  ONLINE       0     0     0

errors: No known data errors
```

専用のログ・キャッシュデバイスも `zpool add` で追加します。[ログvdev](#zfs-term-vdev-log)は、ZILを低遅延の別デバイスへ置き、データベースやNFSなどの同期書き込みを助けます。ログをミラーにしない場合、ログデバイスの故障とシステム停止が重なると、直近の同期書き込みを失う危険があります。[ZILとSLOG](#zfs-advanced-zil-slog)も参照してください。

[キャッシュvdev](#zfs-term-vdev-cache)は、ARCの二次キャッシュであるL2ARCを高速な媒体へ置きます。読めなければ本来のプールから取得できるため、キャッシュデバイスの冗長性は必須ではありません。原文ではL2ARCは既定で再起動後も保持されると説明しています。

ミラーのログとNVMeキャッシュを追加する例です。

```shell
# zpool add mypool log mirror ada4p2 ada5p2
# zpool add mypool cache nda0p2
# zpool status mypool
  pool: mypool
 state: ONLINE
  scan: resilvered 781M in 00:00:16 with 0 errors on Sat Jul 11 09:58:28 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
          mirror-1  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0
            ada3p3  ONLINE       0     0     0
        logs
          mirror-2  ONLINE       0     0     0
            ada4p2  ONLINE       0     0     0
            ada5p2  ONLINE       0     0     0
        cache
          nda0p2    ONLINE       0     0     0

errors: No known data errors
```

ミラーから一台を外すには `zpool detach` を使います。三重ミラーから一台を外す例です。

```shell
# zpool status
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:11 with 0 errors on Sat Jul 11 03:14:02 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0

errors: No known data errors
# zpool detach mypool ada2p3
# zpool status
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:11 with 0 errors on Sat Jul 11 03:14:02 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0

errors: No known data errors
```

最後の一台だけになると、ミラーとしての冗長性を失います。そのディスクが故障すればプール全体に影響します。

トップレベルvdev全体の削除は `zpool remove` です。割り当て済みデータをほかのvdevへ退避してから取り外します。スペア、キャッシュ、ログ、special、dedupや、単独ディスク・ミラーのデータvdevが対象になります。ただし、**トップレベルにRAID-Zを含むプールのデータvdevは削除できず、トップレベルvdev間のashiftも揃っている必要があります。**

退避はオンラインで進み、`zpool status` で確認できます。完了後も、旧位置から新位置への対応表をメモリに保持します。表は小さいものの残り続けるため、事前に `zpool remove -n` で見積もれます。二つあるミラーの一つを削除する例です。

```shell
# zpool remove mypool mirror-1
# zpool status mypool
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:11 with 0 errors on Sat Jul 11 03:14:02 2026
remove: Evacuation of mirror in progress since Sat Jul 11 10:15:31 2026
        1.71G copied out of 2.32G at 111M/s, 73.71% done, 0h0m to go
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
          mirror-1  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0
            ada3p3  ONLINE       0     0     0

errors: No known data errors
# zpool status mypool
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:11 with 0 errors on Sat Jul 11 03:14:02 2026
remove: Removal of vdev 1 copied 2.32G in 0h0m, completed on Sat Jul 11 10:15:53 2026
        10.9K memory used for removed device mappings
config:

        NAME          STATE     READ WRITE CKSUM
        mypool        ONLINE       0     0     0
          mirror-0    ONLINE       0     0     0
            ada0p3    ONLINE       0     0     0
            ada1p3    ONLINE       0     0     0
          indirect-1  ONLINE       0     0     0

errors: No known data errors
```

`indirect-1` は移動済みブロックの対応を表す項目で、ディスクを持ちません。進行中の削除は `zpool remove -s` で取り消せます。

<a id="zfs-zpool-raidz-expansion"></a>
### RAID-Zを拡張する

既存のRAID-Z vdevへ、一台ずつディスクを追加できます。パリティの段数は変わりません。**OpenZFS 2.3以降、FreeBSDでは15.0以降が必要です。** 古い版で作ったプールは、拡張前に `zpool upgrade` で `raidz_expansion` 機能を有効にする必要があります。アップグレード時の互換性は[後述](#zfs-zpool-upgrade)を確認してください。

`zpool status` に表示されるRAID-Z vdev名と、新しいディスクを指定します。

```shell
# zpool attach mypool raidz2-0 ada6p3
```

既存データは、プールを利用できる状態のまま、増えたディスクへ再配置されます。`-w` を付ければ完了までコマンドを待機させられます。状態の `expand:` 行で進捗を確認できます。

```shell
# zpool status mypool
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 06:14:36 with 0 errors on Sat Jul 11 04:31:19 2026
expand: expansion of raidz2-0 in progress since Sat Jul 11 09:42:12 2026
        1.83T / 5.36T copied at 186M/s, 34.14% done, 05:31:43 to go
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          raidz2-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0
            ada3p3  ONLINE       0     0     0
            ada4p3  ONLINE       0     0     0
            ada5p3  ONLINE       0     0     0
            ada6p3  ONLINE       0     0     0

errors: No known data errors
```

完了後、新しい容量が利用可能になります。

```shell
# zpool status mypool | grep expand:
expand: expanded raidz2-0 copied 5.36T in 08:23:35, on Sat Jul 11 18:05:47 2026
```

**拡張前のブロックは、元のデータ対パリティ比を保ちます。** 新しい構成の容量効率を全面的に得るのは拡張後に書いたデータです。古いデータも、たとえば[zfs rewrite](#zfs-zfs-rewrite)で書き直せば、新しい効率を利用できます。複数台を増やす場合も一台ずつ実施します。

<a id="zfs-zpool-draid"></a>
### dRAIDプール

[dRAID](#zfs-term-vdev-draid)は、スペアの容量をvdev全体へ分散するRAID-Zの変種です。内部のRAID-Zグループと分散スペアを全ディスクへ配置し、故障時には残るディスクを並列に読み書きして分散スペアへ再構築します。一台のスペアだけへ再構築するより、時間を短縮できます。故障ディスクを交換した後は、分散スペアから交換品へ再構築し、保護を戻します。多数のディスクで再構築が長時間になる用途を主に想定しています。

構成の表記は `zpoolconcepts(7)` に従います。

```text
draid[parity][:datad][:childrenc][:sparess]
```

`parity` はパリティ段数1〜3（既定1）、`data` は冗長グループごとのデータデバイス数（既定8）、`children` は全ディスク数の照合用、`spares` は分散スペア数（既定0）です。次は24台、二重パリティ、グループ当たりデータ8、分散スペア2の例です。

```shell
# zpool create mypool draid2:8d:24c:2s ada0 ada1 ada2 ada3 ada4 ada5 ada6 ada7 ada8 ada9 ada10 ada11 ada12 ada13 ada14 ada15 ada16 ada17 ada18 ada19 ada20 ada21 ada22 ada23
```

分散スペアはstatusの `spares` に表示され、最初のvdevの最初のスペアなら `draid2-0-0` のような名前になります。

dRAIDは、容量効率と引き換えに再構築を速めます。固定幅のストライプを使い、小さな書き込みをゼロで埋めるため、データ8台・4KBセクタの既定例では最小割り当てが32KBになります。小ブロックの多い用途では容量と圧縮効率に不利です。スペア容量も故障の有無によらず先に確保します。[special vdev](#zfs-zpool-special)へメタデータや小ブロックを分けると、その損失を軽減できます。原文は少数ディスクならRAID-Zを適した選択肢としています。

<a id="zfs-zpool-special"></a>
### 特殊な割り当てクラス

[special vdev](#zfs-term-vdev-special)は、間接ブロック、dnodeなどのメタデータと、設定に応じて小さなデータブロックを保存します。dedup vdevは[重複排除](#zfs-term-deduplication)のテーブル用です。これらを高速なNVMeミラーなどへ置くと、低速ディスクのプールでも、ディレクトリの走査、zfs list、重複排除の検索などを速められる場合があります。

ミラーのspecial vdevを追加する例です。

```shell
# zpool add mypool special mirror nda0 nda1
```

新しく割り当てるメタデータがそこへ置かれます。既存分は、書き直されるまでは元の場所に残ります。

`special_small_blocks` は、指定サイズ以下のデータブロックもspecialへ配置する設定です。

```shell
# zfs set special_small_blocks=16K mypool/projects
```

0ならデータブロックの特別配置を無効にします。原文ではFreeBSD 14.xの範囲を512バイト〜1MBの2のべき乗、15.0では最大ブロックサイズの16MBまでとしています。データセットのrecordsizeと同じ値なら、そのデータセットの全データブロックが対象になります。specialが満杯なら、通常クラスへ割り当てが戻ります。

**special vdevはキャッシュではありません。そこに割り当てたメタデータの唯一の保存先となるため、それを失うとプールを失います。** special・dedupにも、ミラーなどでデータvdevに見合う冗長性を持たせます。

削除は[zpool removeの制約](#zfs-zpool-attach)に従います。specialとデータvdevでセクタサイズが異なると、ashift一致の条件により外せないことがあります。

<a id="zfs-zpool-status"></a>
### プールの状態を確認する

デバイスのオフライン化や、読み取り・書き込み・チェックサムのエラーが起きると、状態と対応するカウンタへ反映されます。`zpool status` は、各デバイスとプール全体の状態、推奨される対応、前回のスクラブなどを表示します。

```shell
# zpool status
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 02:25:36 with 0 errors on Sat Jul 11 06:51:26 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          raidz2-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0
            ada3p3  ONLINE       0     0     0
            ada4p3  ONLINE       0     0     0
            ada5p3  ONLINE       0     0     0

errors: No known data errors
```

目的に応じて表示を変えられます。

- `-v`：前回の完全なスクラブ以降に見つかったデータエラーの詳細。影響するファイル名なども表示します。
- `-x`：問題のある、または利用できないプールだけを表示します。
- `-s`：末端vdevごとに、30秒以内に完了しなかった遅いI/Oの回数を表示します。
- `-e`：正常でないvdevだけを表示します。原文ではFreeBSD 14.1以降が対象です。
- `-p`：丸めた表示ではなく、解析しやすい正確な数値を表示します。
- `-t`：vdevごとのTRIM状況を表示します。

全オプションは `zpool-status(8)` を参照してください。

<a id="zfs-zpool-clear"></a>
### エラー状態をクリアする

ZFSは検出したエラーをカウンタへ加算します。`zpool clear mypool` はエラー状態とカウンタをリセットします。古いエラーを残すと、自動監視で新たな異常を区別しにくくなる場合があります。ただし、クリアは故障原因を直す操作ではありません。原因の調査・対処と、新たなエラーが出ないかの確認を合わせて行います。

<a id="zfs-zpool-replace"></a>
### 正常に動くデバイスを交換する

古いディスクがまだ動いている間に新しいディスクへ交換する場合は、コピーが終わるまで古い方を残せます。先に切り離すより冗長性を保ちやすく、喪失リスクを抑えられます。`zpool replace` は交換品へデータを再構築し、完了後に旧デバイスを外します。大きな交換品なら、[条件が揃えば容量も拡張](#zfs-zpool-online)できます。

動作中の一台を交換する例です。**resilver完了前には再起動しないようにします。**

```shell
# zpool status
  pool: mypool
 state: ONLINE
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0

errors: No known data errors
# zpool replace mypool ada1p3 ada2p3
Make sure to wait until resilvering finishes before rebooting.

When booting from the pool 'mypool', update the boot code on the newly attached disk 'ada2p3'.

Assuming GPT partitioning is used and ada0 is the new boot disk, use the following command:

        gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ada0
# gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ada2
# zpool status
  pool: mypool
 state: ONLINE
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Sat Jul 11 14:21:35 2026
        781M / 781M scanned, 604M / 781M issued at 101M/s
        604M resilvered, 77.39% done, 00:00:01 to go
config:

        NAME             STATE     READ WRITE CKSUM
        mypool           ONLINE       0     0     0
          mirror-0       ONLINE       0     0     0
            ada0p3       ONLINE       0     0     0
            replacing-1  ONLINE       0     0     0
              ada1p3     ONLINE       0     0     0
              ada2p3     ONLINE       0     0     0  (resilvering)

errors: No known data errors
# zpool status
  pool: mypool
 state: ONLINE
  scan: resilvered 781M in 00:00:17 with 0 errors on Sat Jul 11 14:21:52 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0

errors: No known data errors
```

原文の出力内には、新しいディスクをada0とする案内と、実際に交換するada2へのコマンドが混在しています。**ブートコードの対象はこの文字列をそのまま信じず、実機の交換先を確認してください。** 掲載のpmbr・gptzfsbootはBIOS/GPT用で、UEFIでは起動方式に合った設定が必要です。

ミラーでの `replace`・`attach` に `-s` を付けると、通常のhealing resilverではなく**sequential resilver**を使えます。ディスク順にコピーし、各ブロックのチェックサム検証をその場で行わないことで、冗長性を早く回復します。その後、検証のためのスクラブが自動的に始まります。原文ではミラーとdRAIDが対応し、RAID-Zは対象外です。進行中のresilverを最初からやり直すには `zpool resilver mypool` を使います。

<a id="zfs-zpool-resilver"></a>
### 故障したデバイスに対処する

冗長性が残っていれば、一台が故障してもvdevはDEGRADED状態でデータを利用できることがあります。欠けたデータを残りから復元するため、性能は低下する場合があります。故障品を交換してresilverを行い、データを新しいデバイスへ再構築すれば、正常なONLINE状態へ戻せます。

冗長性がない、または故障数が保護範囲を超えた場合は、プールがFAULTEDとなり利用できなくなります。十分なデバイスを再接続できなければ、バックアップからの復旧が必要です。

見つからない旧デバイスがGUIDで表示される場合は、その識別子を交換元として指定できます。原文本文は「新しいディスクのGUID」と表現していますが、以下の例は `was /dev/ada1p3` と表示された**旧デバイス**を識別しています。交換品のデバイス名が同じなら、新デバイスの引数を省略できる場合もあります。

```shell
# zpool status
  pool: mypool
 state: DEGRADED
status: One or more devices could not be opened.  Sufficient replicas exist for
        the pool to continue functioning in a degraded state.
action: Attach the missing device and online it using 'zpool online'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-2Q
config:

        NAME                    STATE     READ WRITE CKSUM
        mypool                  DEGRADED     0     0     0
          mirror-0              DEGRADED     0     0     0
            ada0p3              ONLINE       0     0     0
            316502962686821739  UNAVAIL      0     0     0  was /dev/ada1p3

errors: No known data errors
# zpool replace mypool 316502962686821739 ada2p3
# zpool status
  pool: mypool
 state: DEGRADED
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Sat Jul 11 14:52:21 2026
        781M / 781M scanned, 641M / 781M issued at 128M/s
        640M resilvered, 82.04% done, 00:00:01 to go
config:

        NAME                        STATE     READ WRITE CKSUM
        mypool                      DEGRADED     0     0     0
          mirror-0                  DEGRADED     0     0     0
            ada0p3                  ONLINE       0     0     0
            replacing-1             UNAVAIL      0     0     0
              15732067398082357289  UNAVAIL      0     0     0  was /dev/ada1p3/old
              ada2p3                ONLINE       0     0     0  (resilvering)

errors: No known data errors
# zpool status
  pool: mypool
 state: ONLINE
  scan: resilvered 781M in 00:00:17 with 0 errors on Sat Jul 11 14:52:38 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0

errors: No known data errors
```

進行中の状態と完了を確認し、正常な冗長性へ戻ったことを確かめます。

<a id="zfs-zpool-spares"></a>
### ホットスペアとzfsdによる自動交換

冗長なvdevを持つプールには、故障時に使う[ホットスペア](#zfs-term-vdev-spare)を登録できます。交換対象以上の容量が必要です。作成時なら `spare` の後に指定し、既存プールなら次のように追加します。

```shell
# zpool add mypool spare ada3p3
# zpool status
  pool: mypool
 state: ONLINE
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
        spares
          ada3p3    AVAIL

errors: No known data errors
```

待機中はAVAILと表示されます。手動で使うには、故障したデバイスとスペアをreplaceへ指定します。

```shell
# zpool replace mypool ada1p3 ada3p3
# zpool status
  pool: mypool
 state: DEGRADED
status: One or more devices could not be opened.  Sufficient replicas exist for
        the pool to continue functioning in a degraded state.
action: Attach the missing device and online it using 'zpool online'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-2Q
  scan: resilvered 781M in 00:00:21 with 0 errors on Sat Jul 11 09:14:33 2026
config:

        NAME          STATE     READ WRITE CKSUM
        mypool        DEGRADED     0     0     0
          mirror-0    DEGRADED     0     0     0
            ada0p3    ONLINE       0     0     0
            spare-1   DEGRADED     0     0     0
              ada1p3  UNAVAIL      0     0     0  cannot open
              ada3p3  ONLINE       0     0     0
        spares
          ada3p3      INUSE     currently in use

errors: No known data errors
```

スペアへの交換は一時的な状態です。故障品を恒久的な交換品へ置き換え、そのresilverが終わったら、`zpool detach mypool ada3p3` でスペアを待機へ戻します。反対にスペアを恒久メンバーにするなら、故障した側を `zpool detach mypool ada1p3` で外します。取り外す対象を混同しないでください。

既定でoffの `autoreplace` は、以前のメンバーと同じ物理位置へ新ディスクが現れたとき、自動交換を行うためのプロパティです。

```shell
# zpool set autoreplace=on mypool
```

FreeBSDでは、autoreplaceを含む障害への自動対応を、基本システムの `zfsd(8)` が担います。既定では有効でないので、利用する場合は有効化して起動します。

```shell
# sysrc zfsd_enable="YES"
# service zfsd start
```

原文が挙げるzfsdの処理は次のとおりです。しきい値は固定原文の説明です。

- 冗長vdevからデバイスが消えたり、DEGRADED・FAULTEDになったりするとスペアを使います。
- 60秒間にI/Oエラーが50回超、または遅延I/Oが8回超ならFAULTEDとし、スペアを使います。
- 60秒間にチェックサムエラーが50回超ならDEGRADEDとし、スペアを使います。
- デバイスが戻るとオンライン化し、不在中の変更をresilverします。
- autoreplaceがonなら、同じ物理位置の新ディスクへ交換します。
- 恒久交換品のresilverが完了するとスペアを待機へ戻します。

LinuxのOpenZFSで使うZEDと、FreeBSDのzfsdを混同しないでください。ZEDはFreeBSDの一部ではありません。

判断の基になるイベントは `zpool events` で確認でき、`-v` は詳細、`-f` は新規イベントの継続表示です。イベントは `devd(8)` にも渡されます。`/etc/devd/zfs.conf` にはログ記録のルールがあり、異常時のメール通知などを追加する際のひな型にもなります。

<a id="zfs-zpool-scrub"></a>
### プールをスクラブする

原文は、定期的に、目安として少なくとも月一回の[スクラブ](#zfs-term-scrub)を勧めています。ディスク負荷で性能が下がるため、繁忙時間を避けたり、[I/Oスケジューラの調整](#zfs-advanced-tuning)で影響を抑えたりします。

```shell
# zpool scrub mypool
# zpool status
  pool: mypool
 state: ONLINE
  scan: scrub in progress since Sat Jul 11 20:52:54 2026
        130G / 8.60T scanned at 649M/s, 116G / 8.60T issued at 580M/s
        0B repaired, 1.32% done, 04:15:41 to go
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          raidz2-0  ONLINE       0     0     0
            ada0p3  ONLINE       0     0     0
            ada1p3  ONLINE       0     0     0
            ada2p3  ONLINE       0     0     0
            ada3p3  ONLINE       0     0     0
            ada4p3  ONLINE       0     0     0
            ada5p3  ONLINE       0     0     0

errors: No known data errors
```

作業を妨げる場合は `zpool scrub -p mypool` で一時停止し、`zpool scrub mypool` で続きから再開できます。中止は `-s`、完了まで待機するには `-w` を使います。

既知のエラーだけを再確認する**error scrub**は `zpool scrub -e mypool` です。全体より早く終わりますが、全領域を検査する代わりではありません。OpenZFS 2.2、FreeBSDでは14.0以降が必要です。

periodicで、前回から35日を超えたプールを自動スクラブするには、`/etc/periodic.conf` に追加します。

```text
daily_scrub_zfs_enable="YES"
```

間隔は `daily_scrub_zfs_default_threshold="日数"` で変更でき、プール別の設定は `periodic.conf(5)` を参照します。`daily_status_zfs_enable="YES"` は日次報告へ状態確認を加える別の設定です。

<a id="zfs-zpool-selfheal"></a>
### 自己修復

ZFSは、読み取ったデータのチェックサムが一致しなければ、ミラーなどの正常なコピーを読み直します。正しいデータをアプリケーションへ渡し、壊れた側も修復できます。通常の運用中に管理者の介入なしで進む点が自己修復の利点です。長期間読まないアーカイブでも、定期スクラブで潜在的な破損を探せます。ZFSでは、この処理のために従来のfsckのような検査・修復ツールを別途実行する必要はありません。

以下は**破損を意図的に起こす教材用の例**です。専用の試験用ディスク以外で試さないでください。まずミラープールを作ります。

```shell
# zpool create healer mirror /dev/ada0p1 /dev/ada1p1
# zpool status healer
  pool: healer
 state: ONLINE
config:

    NAME        STATE     READ WRITE CKSUM
    healer      ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
       ada0p1   ONLINE       0     0     0
       ada1p1   ONLINE       0     0     0

errors: No known data errors
# zpool list
NAME     SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
healer   960M   111K   960M        -         -     0%     0%  1.00x    ONLINE  -
```

データを置き、比較用のチェックサムを取る原文の例です。

```shell
# cp /some/important/data /healer
# zpool list
NAME     SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
healer   960M  67.7M   892M        -         -     0%     7%  1.00x    ONLINE  -
# sha1 /healer > checksum.txt
# cat checksum.txt
SHA1 (/healer) = 2753eff56d77d9a536ece6694bf0a82740344d1f
```

**訳注：** 上では `/healer` をディレクトリとして使う一方、`sha1 /healer` を単一ファイルのように扱っています。ディレクトリ配下の全ファイルをこの指定だけで検証することはできません。実際に比較するなら、保存した対象ファイルのパスを使い、比較対象が同じであることを確認します。

自動修復されないよう一度exportし、一方へランダムデータを書き、その後importする原文の例です。

**以下のddは既存内容を破壊します。通常運用のプール、必要なデータを持つディスク、同じディスクの別パーティションに他のファイルシステムがある環境では実行しないでください。対象は試験プールの構成デバイスに限り、バックアップが存在し、復元できることを事前に検証する必要があります。**

```shell
# zpool export healer
# dd if=/dev/random of=/dev/ada1p1 bs=1m count=200
200+0 records in
200+0 records out
209715200 bytes transferred in 62.992162 secs (3329227 bytes/sec)
# zpool import healer
```

破損が検出されると、CKSUMが増えます。例では正常なada0p1から読み出せるため、アプリケーションには誤ったデータを渡していません。

```shell
# zpool status healer
  pool: healer
 state: ONLINE
status: One or more devices has experienced an unrecoverable error.  An
        attempt was made to correct the error.  Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
        using 'zpool clear' or replace the device with 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
config:

    NAME        STATE     READ WRITE CKSUM
    healer      ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
       ada0p1   ONLINE       0     0     0
       ada1p1   ONLINE       0     0     1

errors: No known data errors
```

元と同じデータを読めることを確認するチェックサム比較の例です。前述のパスの食い違いに注意してください。

```shell
# sha1 /healer >> checksum.txt
# cat checksum.txt
SHA1 (/healer) = 2753eff56d77d9a536ece6694bf0a82740344d1f
SHA1 (/healer) = 2753eff56d77d9a536ece6694bf0a82740344d1f
```

この動作には、修復に使える十分な冗長性が必要です。単一デバイスだけでは、正常な別コピーがない破損を自己修復できません。チェックサムを無効にしないでください。

破損した領域を全体的に確認・修復するため、スクラブを実行します。

```shell
# zpool scrub healer
# zpool status healer
  pool: healer
 state: ONLINE
status: One or more devices has experienced an unrecoverable error.  An
        attempt was made to correct the error.  Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
        using 'zpool clear' or replace the device with 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
  scan: scrub in progress since Sat Jul 11 10:34:02 2026
        40.8M scanned at 20.4M/s, 24.9M issued at 12.4M/s, 67.0M total
        9.63M repaired, 37.16% done, 00:00:03 to go
config:

    NAME        STATE     READ WRITE CKSUM
    healer      ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
       ada0p1   ONLINE       0     0     0
       ada1p1   ONLINE       0     0   627  (repairing)

errors: No known data errors
```

`repairing` は、正常な側から壊れた側へ修復中であることを示します。完了後の例です。

```shell
# zpool status healer
  pool: healer
 state: ONLINE
status: One or more devices has experienced an unrecoverable error.  An
        attempt was made to correct the error.  Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
        using 'zpool clear' or replace the device with 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
  scan: scrub repaired 66.5M in 00:00:06 with 0 errors on Sat Jul 11 10:34:08 2026
config:

    NAME        STATE     READ WRITE CKSUM
    healer      ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
       ada0p1   ONLINE       0     0     0
       ada1p1   ONLINE       0     0 2.72K

errors: No known data errors
```

修復が終わり、データが正常であることを確認した後、記録されたエラー状態をクリアします。

```shell
# zpool clear healer
# zpool status healer
  pool: healer
 state: ONLINE
  scan: scrub repaired 66.5M in 00:00:06 with 0 errors on Sat Jul 11 10:34:08 2026
config:

    NAME        STATE     READ WRITE CKSUM
    healer      ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
       ada0p1   ONLINE       0     0     0
       ada1p1   ONLINE       0     0     0

errors: No known data errors
```

カウンタが0へ戻ったことを確認します。クリアしただけで元の故障が直ったと判断しないでください。

<a id="zfs-zpool-trim"></a>
### TRIMと初期化

SSDやシンプロビジョニングされたストレージには、不要になった領域を通知することで性能を維持しやすくなります。対応するデバイスへTRIM・UNMAPを送る操作です。

```shell
# zpool trim mypool
```

一台なら `zpool trim mypool nda0p3` のように指定します。`-w` は完了待機、`-c` は中止、`-s` は一時停止で、通常のtrimを再実行すると再開します。対応機器の `--secure` は、通知した領域のデータ消去を機器へ要求するsecure TRIMです。プール内の全データの消去や、任意の機器での消去保証を意味するものではありません。

進捗は `status -t` で表示できます。

```shell
# zpool status -t mypool
  pool: mypool
 state: ONLINE
  scan: scrub repaired 0B in 00:12:33 with 0 errors on Sat Jul 11 03:31:11 2026
config:

    NAME        STATE     READ WRITE CKSUM
    mypool      ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
        nda0p3  ONLINE       0     0     0  (23% trimmed, started at Sat Jul 11 09:15:04 2026)
        nda1p3  ONLINE       0     0     0  (22% trimmed, started at Sat Jul 11 09:15:04 2026)

errors: No known data errors
```

継続的に小さなTRIMを送るには、次を設定します。

```shell
# zpool set autotrim=on mypool
```

自動TRIMは小さな解放領域を省く一方、継続した追加負荷も生じます。原文は多くのシステムで、autotrimをoffにして定期的な全体TRIMを使う方法がよいと説明しています。FreeBSD 14.1以降では、`/etc/periodic.conf` の `daily_trim_zfs_enable="YES"` で日次実行できます。実際の機器と負荷に合わせて判断します。

`zpool initialize` は、指定デバイスの未割り当て領域へパターンを書きます。デバイス名を省くと対象となる全デバイスへ実施します。シンプロビジョニング領域を先に割り当てて初回書き込みの遅延を抑えたり、新しい機器への書き込みを試したりする用途です。

```shell
# zpool initialize mypool
```

`-c` は中止、`-s` は一時停止、`-w` は完了待機、`-u` はデバイスから初期化状態の情報を取り除く指定です。詳しくは `zpool-trim(8)`、`zpool-initialize(8)` を参照してください。

<a id="zfs-zpool-checkpoint"></a>
### プールのチェックポイント

`zpool checkpoint` は、全データセットとプール構成を含む、プール全体の状態を保存します。OSの更新、新機能の有効化、データセットの再編などの前に、一時的に戻れる点を作るために使います。

```shell
# zpool checkpoint mypool
```

同時に保持できるのは一つです。以後の変更に応じて必要となる容量は、listのCKPOINTに表示されます。

```shell
# zpool list mypool
NAME     SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
mypool  4.50T  1.42T  3.08T     221M         -     4%    31%  1.00x    ONLINE  -
```

戻すときはexportし、チェックポイントへの巻き戻しを指定してimportします。

```shell
# zpool export mypool
# zpool import --rewind-to-checkpoint mypool
```

**作成後の変更は、後から作ったスナップショットやプロパティ変更も含めて失われます。** 不要なチェックポイントの破棄は次の操作です。`-w` は解放処理の完了を待ちます。

```shell
# zpool checkpoint -d -w mypool
```

保持中は、構成を変える `remove`、`attach`、`detach`、`split`、`reguid` が拒否されます。また、作成後に不要となったブロックも、チェックポイントを捨てるまで解放できず、長く保持すると容量を使い切る場合があります。

チェックポイントは短期間の管理操作の取り消しに向く機能です。同じディスク上にあり、巻き戻すと以後のすべてを失うため、[スナップショット](#zfs-zfs-snapshot)や別のバックアップの代わりではありません。詳細は `zpool-checkpoint(8)` を参照してください。

<a id="zfs-zpool-online"></a>
### プールの容量を増やす

冗長vdevの容量は、基本的に最も小さい構成デバイスに制約されます。小さいものを大容量へ交換し、resilverが終わると、条件が揃えば増えた容量を使えます。たとえば1TBと2TBのミラーは1TB相当ですが、1TB側を2TBへ交換して再構築すれば、2TB相当へ拡張できます。

既定では自動拡張しないため、交換前に `autoexpand` を設定する方法があります。

```shell
# zpool set autoexpand=on mypool
```

最後の小容量デバイスがなくなると拡張されます。自動設定を使わない場合は、各デバイスへ `zpool online -e` を実行し、全体で容量が使える状態にします。パーティションを使っているなら、その範囲も増えた容量を使える必要があります。

ディスク交換ではなくRAID-Zへ台数を追加する方法は[RAID-Z拡張](#zfs-zpool-raidz-expansion)を参照してください。

<a id="zfs-zpool-import"></a>
### プールをexport・importする

別のシステムへ移す前に**export**します。データセットをアンマウントし、プールがexportされたことをデバイスへ記録します。ほかのZFS対応OSや異なるアーキテクチャでimportできる場合もありますが、互換性の制約は `zpool(8)` を確認してください。

開いたファイルがある場合の `zpool export -f` は強制アンマウントを伴い、利用中のアプリケーションに予期しない動作を起こすおそれがあります。通常は利用を止めてからexportします。

```shell
# zpool export mypool
```

通常、importするとデータセットもマウントします。`-N` はマウントを抑止し、`-o` はそのimport用のプロパティ、`-o altroot=パス` はマウント先の先頭に付ける別のルートを指定します。正しくexportされていないプールには `-f` が必要な場合がありますが、**別ホストでまだ使っていないことを確かめずに強制importしないでください。** `-a` は他システムで使用中と見なされない対象をまとめてimportします。

復旧用の指定もあります。`-F` は古いトランザクショングループへ巻き戻し、直近の書き込みを失う可能性があります。`-m` は専用ログデバイスを失った場合のimportで、未反映の同期書き込みが失われる危険があります。`-o readonly=on` は書き込みを禁止して調査・救出に使います。`-R /mnt` は `altroot=/mnt` と `cachefile=none` を組み合わせ、稼働中システムのマウント先やプールキャッシュへの影響を抑えます。詳細は `zpool-import(8)` を確認します。

引数なしのimportで候補を表示します。

```shell
# zpool import
   pool: mypool
     id: 9930174748043525076
  state: ONLINE
 action: The pool can be imported using its name or numeric identifier.
 config:

        mypool    ONLINE
          ada0p1  ONLINE
```

別ルートを指定する例です。

```shell
# zpool import -o altroot=/mnt mypool
# zfs list
NAME                 USED  AVAIL  REFER  MOUNTPOINT
mypool               110K  47.0G    31K  /mnt/mypool
```

起動時には、`zfs_enable="YES"` で有効になったスクリプトが `/etc/zfs/zpool.cache` に記録されたプールをimportします。通常のimportでキャッシュへ登録されますが、`cachefile` が制御します。`cachefile=none` のプールは、再起動だけでは自動復帰しません。

<a id="zfs-zpool-import-geli"></a>
#### GELIで暗号化したプールのimport

インストーラの **Encrypt Disks** は、[ZFSネイティブ暗号化](#zfs-native-encryption)ではなく、[geli(8)によるパーティション暗号化](https://docs.freebsd.org/en/books/handbook/disks/#disks-encrypting-geli)を使います。インストール済みシステムではloaderがパスフレーズを求め、プロバイダを接続してからルートをマウントします。

救出メディアや別ホストから使う場合は、ZFS自体がGELIを解錠するわけではありません。プール内の各暗号化パーティションへgeli attachを行ってからimportします。

```shell
# geli attach ada0p4
Enter passphrase:
# zpool import -f -R /mnt zroot
```

対象は `gpart show` で確認します。原文の既定配置ではp4ですが、実際の配置を確認してください。非暗号化のブートプールを別に持つ旧構成は、その中の `/boot/encryption.key` も必要で、`geli attach -k /path/to/encryption.key` のように指定します。

<a id="zfs-zpool-upgrade"></a>
### プールをアップグレードする

FreeBSD更新後や、古いシステムのプールを取り込んだ後、新しいディスク形式の機能を使うにはプールも明示的に更新します。**古いZFS環境へ戻す必要がないか、先に判断してください。更新した機能を後から一般的にダウングレードすることはできません。**

現在の形式は単一のバージョン番号ではなく、`zpool-features(7)` の**feature flag**で管理します。enabledは利用を許可した状態、activeは実際にその機能に依存するデータを保存した状態です。enabledだけで未使用なら互換性に影響しませんが、activeになると、非対応ソフトウェアでimportできなくなります。active機能がすべて読み取り互換なら、読み取り専用で取り込める場合があります。

未有効の対応機能がある場合の表示です。

```shell
# zpool status mypool
  pool: mypool
 state: ONLINE
status: Some supported and requested features are not enabled on the pool.
        The pool can still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
        the pool may no longer be accessible by software that does not support
        the features. See zpool-features(7) for details.
  scan: scrub repaired 0B in 00:11:03 with 0 errors on Sat Jul 11 03:15:41 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            ada0p1  ONLINE       0     0     0
            ada1p1  ONLINE       0     0     0

errors: No known data errors
```

引数なしのupgradeは対象を一覧表示します。

```shell
# zpool upgrade
This system supports ZFS pool feature flags.

Some supported features are not enabled on the following pools. Once a
feature is enabled the pool may become incompatible with software
that does not support the feature. See zpool-features(7) for details.

Note that the pool 'compatibility' feature can be used to inhibit
feature upgrades.

POOL  FEATURE
---------------
mypool
      zilsaxattr
      head_errlog
      blake3
      block_cloning
      vdev_zaps_v2
```

`zpool upgrade -v` は、現在のシステムの対応機能と旧形式の番号を表示します。プール名を指定すると、利用可能な機能を有効化します。

```shell
# zpool upgrade mypool
This system supports ZFS pool feature flags.

Enabled the following features on 'mypool':
  zilsaxattr
  head_errlog
  blake3
  block_cloning
  vdev_zaps_v2
```

ほかのシステムとの互換性を維持するには、create・upgradeで有効にする範囲を `compatibility` で制限できます。

```shell
# zpool create -o compatibility=openzfs-2.1-freebsd mypool mirror /dev/ada0p1 /dev/ada1p1
```

既存プールへsetすることもでき、対応する定義ファイルは `/usr/share/zfs/compatibility.d` にあります。既定のoffは全機能を許可します。**この設定は、すでに有効な機能を無効へ戻しません。**

**プールから起動するシステムでは、新機能に対応する起動コード・loaderも必要です。** 原文はBIOS/GPTとUEFIの例を示しています。GPTというパーティション方式と、UEFIという起動方式は排他的ではないため、「GPTかEFIか」という二分法で判断しないでください。

従来のBIOS/GPT構成の例です。

```shell
# gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ada1
```

UEFIで、EFIシステムパーティションをマウントし、loaderを更新するamd64の例です。

```shell
# mount -t msdosfs /dev/ada1p1 /boot/efi
# cp /boot/loader.efi /boot/efi/efi/boot/BOOTX64.efi
# cp /boot/loader.efi /boot/efi/efi/freebsd/loader.efi
```

**対象パーティション、既存のマウント状態、ファームウェアが実際に参照するパスを確認してください。** ファイル名はアーキテクチャによって異なるので `uefi(8)` を参照します。起動に使う各ディスクへ反映します。`gpart(8)` も参照してください。

<a id="zfs-zpool-history"></a>
### プールの操作履歴を読む

ZFSは、プール作成、データセット作成、プロパティ変更、ディスク交換などの操作履歴をプール自身へ保存します。外部のログファイルではないため、プールを移動しても履歴を確認できます。

```shell
# zpool history
History for 'tank':
2026-07-11.10:24:05 zpool create tank mirror /dev/ada0p1 /dev/ada1p1
2026-07-11.18:50:58 zfs set atime=off tank
2026-07-11.18:51:09 zfs set checksum=fletcher4 tank
2026-07-11.18:51:18 zfs create tank/backup
```

日時付きで変更操作を表示し、zfs listのような参照操作は含みません。プール名を省略すると全プールが対象です。

`-i` はユーザー操作に加え、内部イベントも表示します。

```shell
# zpool history -i
History for 'tank':
2026-07-11.10:24:05 [txg:5] create pool version 5000; software version zfs-2.2.7-FreeBSD_gd75f9ee8b; uts myzfsbox 14.3-RELEASE 1403000 amd64
2026-07-11.18:50:53 [txg:50] set tank (21) atime=0
2026-07-11.18:50:58 zfs set atime=off tank
2026-07-11.18:51:04 [txg:53] set tank (21) checksum=7
2026-07-11.18:51:09 zfs set checksum=fletcher4 tank
2026-07-11.18:51:13 [txg:55] create tank/backup (39)
2026-07-11.18:51:18 zfs create tank/backup
```

`-l` はユーザーとホスト名などを加えます。

```shell
# zpool history -l
History for 'tank':
2026-07-11.10:24:05 zpool create tank mirror /dev/ada0p1 /dev/ada1p1 [user 0 (root) on myzfsbox:global]
2026-07-11.18:50:58 zfs set atime=off tank [user 0 (root) on myzfsbox:global]
2026-07-11.18:51:09 zfs set checksum=fletcher4 tank [user 0 (root) on myzfsbox:global]
2026-07-11.18:51:18 zfs create tank/backup [user 0 (root) on myzfsbox:global]
```

例ではrootがmyzfsboxで操作したことが分かります。別ホストへ移したプールでも、どのホストで行った変更か区別できます。両オプションを組み合わせると、調査時にさらに詳しく追えます。

<a id="zfs-zpool-iostat"></a>
### 性能を監視する

`zpool iostat` は、使用量と空き容量、毎秒の読み書き回数、転送量を表示します。既定では全プール、名前を指定すればそのプールだけを対象にします。

```shell
# zpool iostat
               capacity     operations    bandwidth
pool        alloc   free   read  write   read  write
----------  -----  -----  -----  -----  -----  -----
data         288G  1.53T      2     11  11.3K  57.1K
```

最後の引数に秒数を指定すると、その間隔で更新を続けます。さらに回数も指定でき、継続表示はCtrl+Cで終了します。`-v` は各デバイスの値も表示し、一台だけ遅くなっていないかを調べる手掛かりになります。

```shell
# zpool iostat -v
                            capacity     operations    bandwidth
pool                     alloc   free   read  write   read  write
-----------------------  -----  -----  -----  -----  -----  -----
data                      288G  1.53T      2     12  9.23K  61.5K
  mirror                  288G  1.53T      2     12  9.23K  61.5K
    ada1p1                   -      -      0      4  5.61K  61.7K
    ada2p1                   -      -      1      4  5.04K  61.7K
-----------------------  -----  -----  -----  -----  -----  -----
```

`-l` は平均遅延をディスク処理と各キューの待ち時間に分け、`-q` はvdevごとの待機・処理中I/O数、`-w` は遅延の分布、`-r` は末端vdevごとの要求サイズ分布を示します。

次の例では、同程度の回数を処理するミラーの二台で、ada1p1は数ミリ秒なのにada2p1は数百ミリ秒かかっています。

```shell
# zpool iostat -lv data
              capacity     operations     bandwidth    total_wait     disk_wait    syncq_wait    asyncq_wait  scrub   trim  rebuild
pool        alloc   free   read  write   read  write   read  write   read  write   read  write   read  write   wait   wait     wait
----------  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -------
data         288G  1.53T    156    212  19.4M  26.6M   14ms  186ms    5ms  184ms    1us    2us    8ms    2ms      -      -        -
  mirror-0   288G  1.53T    156    212  19.4M  26.6M   14ms  186ms    5ms  184ms    1us    2us    8ms    2ms      -      -        -
    ada1p1      -      -     79    106   9.7M  13.3M    3ms    5ms    3ms    4ms    1us    2us    1ms    1ms      -      -        -
    ada2p1      -      -     77    106   9.7M  13.3M  212ms  187ms  208ms  183ms    1us    2us   15ms    3ms      -      -        -
----------  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -----  -------
```

ミラーの書き込みは遅い側の完了を待つため、vdev全体が影響を受けます。statusにエラーがなくても、通常の負荷で遅延が高い場合、ディスク内部の再試行などを疑い、交換を検討する手掛かりになります。値だけで原因を断定せず、ほかの状態と合わせて調べます。

スクリプトでバックグラウンド処理を待つには、`zpool wait` を使えます。

```shell
# zpool wait -t scrub,resilver mypool
```

指定したscrub・resilverなどが進行していなくなると終了します。trim・removeなどの対象は `zpool-wait(8)` を参照してください。

OpenZFS 2.3以降、FreeBSDでは15.0以降の `zpool status`、`zpool list`、`zpool get`、`zfs list` は、`-j` によるJSON出力にも対応します。スクリプトでは、表示用の表を切り分けるより扱いやすい形式です。

<a id="zfs-zpool-split"></a>
### ミラープールを分割する

一つ以上のミラーvdevで構成するプールは、各ミラーの一台を切り離して、同じデータを持つ別のプールへ分割できます。特に指定しなければ各ミラーの最後のメンバーを使います。元プールの冗長性も変わるため、まず `-n` の試行で、実行せずに対象と結果を確認します。

<a id="zfs-zfs"></a>
## zfsによるデータセット管理

`zfs` コマンドは、プール内のデータセットを作成・削除・管理します。プールそのものの操作には[zpool](#zfs-zpool)を使います。

<a id="zfs-zfs-create"></a>
### データセットを作成・削除する

ZFSは、各ファイルシステムへ固定の容量を事前配分する必要がなく、プールの容量を共有して随時作成できます。圧縮、重複排除、キャッシュ、クォータ、読み取り専用、大小文字の扱い、共有、マウント先などを[データセット](#zfs-term-dataset)ごとに設定できます。

親子の階層を作り、親のプロパティを子へ継承できます。また、[権限委譲](#zfs-zfs-allow)、[レプリケーション](#zfs-zfs-send)、[スナップショット](#zfs-zfs-snapshot)、[jail](#zfs-zfs-jail)や削除を、それぞれの単位で扱えます。用途ごとに分ける利点がある一方、数百・数千と増えるとlistや起動時のマウントが遅くなることもあります。

LZ4圧縮を設定して作成する例です。

```shell
# zfs list
NAME                  USED  AVAIL  REFER  MOUNTPOINT
mypool                781M  93.2G   144K  none
mypool/ROOT           777M  93.2G   144K  none
mypool/ROOT/default   777M  93.2G   777M  /
mypool/tmp            176K  93.2G   176K  /tmp
mypool/usr            616K  93.2G   144K  /usr
mypool/usr/home       184K  93.2G   184K  /usr/home
mypool/usr/ports      144K  93.2G   144K  /usr/ports
mypool/usr/src        144K  93.2G   144K  /usr/src
mypool/var           1.20M  93.2G   608K  /var
mypool/var/crash      148K  93.2G   148K  /var/crash
mypool/var/log        178K  93.2G   178K  /var/log
mypool/var/mail       144K  93.2G   144K  /var/mail
mypool/var/tmp        152K  93.2G   152K  /var/tmp
# zfs create -o compress=lz4 mypool/usr/mydataset
# zfs list
NAME                   USED  AVAIL  REFER  MOUNTPOINT
mypool                 781M  93.2G   144K  none
mypool/ROOT            777M  93.2G   144K  none
mypool/ROOT/default    777M  93.2G   777M  /
mypool/tmp             176K  93.2G   176K  /tmp
mypool/usr             704K  93.2G   144K  /usr
mypool/usr/home        184K  93.2G   184K  /usr/home
mypool/usr/mydataset  87.5K  93.2G  87.5K  /usr/mydataset
mypool/usr/ports       144K  93.2G   144K  /usr/ports
mypool/usr/src         144K  93.2G   144K  /usr/src
mypool/var            1.20M  93.2G   610K  /var
mypool/var/crash       148K  93.2G   148K  /var/crash
mypool/var/log         178K  93.2G   178K  /var/log
mypool/var/mail        144K  93.2G   144K  /var/mail
mypool/var/tmp         152K  93.2G   152K  /var/tmp
```

削除は、配下の全ファイルを一つずつ走査・更新する処理と異なり、速やかに要求を受け付けられます。ただし内容を失うので対象を確認します。

```shell
# zfs list
NAME                   USED  AVAIL  REFER  MOUNTPOINT
mypool                 880M  93.1G   144K  none
mypool/ROOT            777M  93.1G   144K  none
mypool/ROOT/default    777M  93.1G   777M  /
mypool/tmp             176K  93.1G   176K  /tmp
mypool/usr             101M  93.1G   144K  /usr
mypool/usr/home        184K  93.1G   184K  /usr/home
mypool/usr/mydataset   100M  93.1G   100M  /usr/mydataset
mypool/usr/ports       144K  93.1G   144K  /usr/ports
mypool/usr/src         144K  93.1G   144K  /usr/src
mypool/var            1.20M  93.1G   610K  /var
mypool/var/crash       148K  93.1G   148K  /var/crash
mypool/var/log         178K  93.1G   178K  /var/log
mypool/var/mail        144K  93.1G   144K  /var/mail
mypool/var/tmp         152K  93.1G   152K  /var/tmp
# zfs destroy mypool/usr/mydataset
# zfs list
NAME                  USED  AVAIL  REFER  MOUNTPOINT
mypool                781M  93.2G   144K  none
mypool/ROOT           777M  93.2G   144K  none
mypool/ROOT/default   777M  93.2G   777M  /
mypool/tmp            176K  93.2G   176K  /tmp
mypool/usr            616K  93.2G   144K  /usr
mypool/usr/home       184K  93.2G   184K  /usr/home
mypool/usr/ports      144K  93.2G   144K  /usr/ports
mypool/usr/src        144K  93.2G   144K  /usr/src
mypool/var           1.21M  93.2G   612K  /var
mypool/var/crash      148K  93.2G   148K  /var/crash
mypool/var/log        178K  93.2G   178K  /var/log
mypool/var/mail       144K  93.2G   144K  /var/mail
mypool/var/tmp        152K  93.2G   152K  /var/tmp
```

容量の実際の回収は非同期に進み、数分かかることがあります。`zpool get freeing プール名` で未回収量、`zpool wait -t free プール名` で完了を待てます。

子データセットやスナップショットがあれば、そのままでは親を削除できません。`-r` は子も含めて再帰削除します。**まず `-n -v` で削除対象と解放見込みを表示し、実際には消さずに確認してください。**

<a id="zfs-zfs-volume"></a>
### ボリュームを作成・削除する

ボリューム（zvol）は、マウントするファイルシステムではなく、`/dev/zvol/プール名/データセット名` でブロックデバイスを公開する種類のデータセットです。別のファイルシステム、仮想マシンのディスク、iSCSIやHASTの提供先などに使えます。ファイルシステムを作らず生データを置くこともできます。

zvol側の圧縮などを利用し、その上に通常のファイルシステムを作る例です。以下のnewfsは、指定先の内容を新しいFATへ初期化します。

```shell
# zfs create -V 250m -o compression=on tank/fat32
# zfs list tank
NAME USED AVAIL REFER MOUNTPOINT
tank 258M  670M   31K /tank
# newfs_msdos -F32 /dev/zvol/tank/fat32
# mount -t msdosfs /dev/zvol/tank/fat32 /mnt
# df -h /mnt | grep fat32
Filesystem           Size Used Avail Capacity Mounted on
/dev/zvol/tank/fat32 249M  24k  249M     0%   /mnt
# mount | grep fat32
/dev/zvol/tank/fat32 on /mnt (msdosfs, local)
```

通常はボリューム全体分の容量を予約します。`-s` はそれを省く疎なボリューム、つまりシンプロビジョニングを作ります。

```shell
# zfs create -s -V 250g tank/bigdisk
```

プールの実容量を超えて見かけの容量を与えられますが、空きが不足するとENOSPCで書き込みが失敗します。利用側がそのエラーに耐えられる構成でのみ使ってください。

`volmode` は公開方法です。`full`（別名geom）はGEOMプロバイダとして最大限の機能を公開し、`dev` はパーティションを隠した単純なデバイスノード、`none` はOSへ公開しない指定です。noneでもスナップショット・クローン・複製を使えるため、転送先にもなります。既定のdefaultは、`zfs(4)` のシステム設定 `zvol_volmode` に従います。

bhyveの仮想ディスクや、`ctl.conf(5)` のLUNとして `ctld(8)` から提供するiSCSI領域にも向きます。

**ZFSボリュームをスワップにしないでください。** メモリ不足時に、メモリを解放するための書き込みをZFSが完了するにもメモリが必要となり、デッドロックするおそれがあります。原文の参照先は [OpenZFS issue #7734](https://github.com/openzfs/zfs/issues/7734)で、専用スワップパーティションの利用を勧めています。

削除方法は通常のデータセットと同様です。要求はすぐ終わっても、空き容量の回収はバックグラウンドで数分かかる場合があります。

<a id="zfs-zfs-rename"></a>
### データセット名を変更する

`zfs rename` は名前の変更だけでなく、同じプール内で親データセットを変える場合にも使います。親が変わると、継承するプロパティも変わります。通常はアンマウントして新しい場所へマウントし直すため、これを抑止するには `-u` を使います。

親と名前を同時に変える例です。

```shell
# zfs list
NAME                   USED  AVAIL  REFER  MOUNTPOINT
mypool                 780M  93.2G   144K  none
mypool/ROOT            777M  93.2G   144K  none
mypool/ROOT/default    777M  93.2G   777M  /
mypool/tmp             176K  93.2G   176K  /tmp
mypool/usr             704K  93.2G   144K  /usr
mypool/usr/home        184K  93.2G   184K  /usr/home
mypool/usr/mydataset  87.5K  93.2G  87.5K  /usr/mydataset
mypool/usr/ports       144K  93.2G   144K  /usr/ports
mypool/usr/src         144K  93.2G   144K  /usr/src
mypool/var            1.21M  93.2G   614K  /var
mypool/var/crash       148K  93.2G   148K  /var/crash
mypool/var/log         178K  93.2G   178K  /var/log
mypool/var/mail        144K  93.2G   144K  /var/mail
mypool/var/tmp         152K  93.2G   152K  /var/tmp
# zfs rename mypool/usr/mydataset mypool/var/newname
# zfs list
NAME                  USED  AVAIL  REFER  MOUNTPOINT
mypool                780M  93.2G   144K  none
mypool/ROOT           777M  93.2G   144K  none
mypool/ROOT/default   777M  93.2G   777M  /
mypool/tmp            176K  93.2G   176K  /tmp
mypool/usr            616K  93.2G   144K  /usr
mypool/usr/home       184K  93.2G   184K  /usr/home
mypool/usr/ports      144K  93.2G   144K  /usr/ports
mypool/usr/src        144K  93.2G   144K  /usr/src
mypool/var           1.29M  93.2G   614K  /var
mypool/var/crash      148K  93.2G   148K  /var/crash
mypool/var/log        178K  93.2G   178K  /var/log
mypool/var/mail       144K  93.2G   144K  /var/mail
mypool/var/newname   87.5K  93.2G  87.5K  /var/newname
mypool/var/tmp        152K  93.2G   152K  /var/tmp
```

スナップショットもrenameできますが、元となる親データセットを変更することはできません。`-r` を使うと、子データセットにある同じ名前のスナップショットも再帰的に変更します。

```shell
# zfs list -t snapshot
NAME                                USED  AVAIL  REFER  MOUNTPOINT
mypool/var/newname@first_snapshot      0      -  87.5K  -
# zfs rename mypool/var/newname@first_snapshot new_snapshot_name
# zfs list -t snapshot
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool/var/newname@new_snapshot_name      0      -  87.5K  -
```

<a id="zfs-zfs-set"></a>
### データセットのプロパティを設定する

多くのプロパティは親から継承しますが、`zfs set プロパティ=値 データセット` で個別に指定できます。利用可能な値はプロパティごとに異なり、getの説明や表示を確認します。継承に戻すには、対応するプロパティで `zfs inherit` を使います。

独自の情報も保存できます。標準のプロパティと区別するため、名前空間を `:` で区切ります。

```shell
# zfs set custom:costcenter=1234 tank
# zfs get custom:costcenter tank
NAME PROPERTY           VALUE SOURCE
tank custom:costcenter  1234  local
```

独自プロパティを子も含めて継承へ戻すには `inherit -r` を使います。親にも設定がなければ、値はなくなりますが、変更の履歴はプールに残ります。

```shell
# zfs inherit -r custom:costcenter tank
# zfs get custom:costcenter tank
NAME    PROPERTY           VALUE              SOURCE
tank    custom:costcenter  -                  -
# zfs get all tank | grep custom:costcenter
#
```

<a id="zfs-zfs-set-share"></a>
#### ネットワーク共有のプロパティ

FreeBSDのZFSは、`sharenfs` を通じて基本システムのNFSサーバと連携します。設定を `/etc/zfs/exports` へ書き、mountdは通常の `/etc/exports` と合わせて読みます。NFSサーバを有効にするため、`/etc/rc.conf` へ設定します。

```text
zfs_enable="YES"
nfs_server_enable="YES"
```

sharenfsにはon・off、または `exports(5)` のオプションを指定できます。現在の値を確認します。

```shell
# zfs get sharenfs mypool/usr/home
NAME             PROPERTY  VALUE    SOURCE
mypool/usr/home  sharenfs  on       local
```

共有を有効にする例です。

```shell
#  zfs set sharenfs=on mypool/usr/home
```

`-alldirs`、`-maproot`、`-network` などを指定することもできます。次の例はrootへのマッピングを含むので、許可するネットワークと権限を意図に合わせて判断してください。

```shell
#  zfs set sharenfs="-alldirs,-maproot=root,-network=192.168.1.0/24" mypool/usr/home
```

**FreeBSDではsharesmbは機能しません。** 共有ライブラリはNFSだけを実装しています。SMBは `net/samba422` などのパッケージを導入し、マウントされたデータセットのパスをSamba側で公開します。

<a id="zfs-zfs-acl"></a>
### NFSv4形式のACL

FreeBSDのZFSは、通常の所有者・グループ・その他の権限より細かく指定できるNFSv4形式のACLを保存できます。原文の既定の `acltype` はnfsv4です。ファイル・ディレクトリのACLは `getfacl(1)` と `setfacl(1)` で表示・変更します。

```shell
% getfacl /usr/home/alice/notes.txt
# file: /usr/home/alice/notes.txt
# owner: alice
# group: alice
            owner@:rw-p--aARWcCos:-------:allow
            group@:r-----a-R-c--s:-------:allow
         everyone@:r-----a-R-c--s:-------:allow
```

ユーザーbobへ書き込みなどを許可するallow項目を加える例です。

```shell
% setfacl -m u:bob:rwp::allow /usr/home/alice/notes.txt
```

`aclmode` は、chmodで通常のモードを変えた際にACLをどう扱うかを指定します。値はdiscard・groupmask・passthrough・restrictedで、既定のdiscardでは新しいモードに対応しないACL項目を除きます。

`aclinherit` は新しいファイル・ディレクトリが親から何を継承するかを指定します。値はdiscard・noallow・restricted・passthrough・passthrough-xです。既定のrestrictedでは、継承した項目からwrite_acl・write_ownerを取り除きます。詳しい構文と動作は `setfacl(1)` と `zfsprops(7)` を参照してください。

<a id="zfs-zfs-snapshot"></a>
### スナップショットの管理

[スナップショット](#zfs-term-snapshot)は、データセットのある時点の状態を読み取り専用で保持します。COWにより古いブロックを残せるため、作成時に内容を丸ごとコピーせず、短時間で作れます。その後変更・削除されたブロックも、スナップショットが参照する間は解放しません。変更量が増えると保持容量も増えます。

対象はファイルやディレクトリ単体ではなく、データセット全体の内容・権限などです。`-r` なら親子に同じ名前のスナップショットを一貫した時点で作れます。関連データが複数データセットにまたがる場合に役立ちます。ただし、アプリケーションのメモリ内状態まで保存する機能ではないため、必要に応じたアプリケーション側の整合性確保も別途考えます。

ソフトウェア導入や更新前に取得し、失敗したら以前の状態へ戻す用途に便利です。成功して不要になれば削除できます。大容量データをバックアップからすべて戻すより速く復旧できる場合がありますが、**同じプールにあるスナップショットは、プール全体を失う障害へのバックアップの代わりにはなりません。**

<a id="zfs-zfs-snapshot-creation"></a>
#### スナップショットを作成する

`zfs snapshot データセット@名前` で作成し、`-r` で子も含めます。次はプールのルートデータセットから再帰的に取得する例です。

```shell
# zfs list -t all
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool                                 780M  93.2G   144K  none
mypool/ROOT                            777M  93.2G   144K  none
mypool/ROOT/default                    777M  93.2G   777M  /
mypool/tmp                             176K  93.2G   176K  /tmp
mypool/usr                             616K  93.2G   144K  /usr
mypool/usr/home                        184K  93.2G   184K  /usr/home
mypool/usr/ports                       144K  93.2G   144K  /usr/ports
mypool/usr/src                         144K  93.2G   144K  /usr/src
mypool/var                            1.29M  93.2G   616K  /var
mypool/var/crash                       148K  93.2G   148K  /var/crash
mypool/var/log                         178K  93.2G   178K  /var/log
mypool/var/mail                        144K  93.2G   144K  /var/mail
mypool/var/newname                    87.5K  93.2G  87.5K  /var/newname
mypool/var/newname@new_snapshot_name      0      -  87.5K  -
mypool/var/tmp                         152K  93.2G   152K  /var/tmp
# zfs snapshot -r mypool@my_recursive_snapshot
# zfs list -t snapshot
NAME                                        USED  AVAIL  REFER  MOUNTPOINT
mypool@my_recursive_snapshot                   0      -   144K  -
mypool/ROOT@my_recursive_snapshot              0      -   144K  -
mypool/ROOT/default@my_recursive_snapshot      0      -   777M  -
mypool/tmp@my_recursive_snapshot               0      -   176K  -
mypool/usr@my_recursive_snapshot               0      -   144K  -
mypool/usr/home@my_recursive_snapshot          0      -   184K  -
mypool/usr/ports@my_recursive_snapshot         0      -   144K  -
mypool/usr/src@my_recursive_snapshot           0      -   144K  -
mypool/var@my_recursive_snapshot               0      -   616K  -
mypool/var/crash@my_recursive_snapshot         0      -   148K  -
mypool/var/log@my_recursive_snapshot           0      -   178K  -
mypool/var/mail@my_recursive_snapshot          0      -   144K  -
mypool/var/newname@new_snapshot_name           0      -  87.5K  -
mypool/var/newname@my_recursive_snapshot       0      -  87.5K  -
mypool/var/tmp@my_recursive_snapshot           0      -   152K  -
```

通常のzfs listにはスナップショットを表示しません。`-t snapshot` ならスナップショット、`-t all` ならファイルシステムなどと合わせて表示します。MOUNTPOINTやAVAILが `-` なのは、通常の書き込み可能なマウント先として扱わないためです。

```shell
# zfs list -rt all mypool/usr/home
NAME                                    USED  AVAIL  REFER  MOUNTPOINT
mypool/usr/home                         184K  93.2G   184K  /usr/home
mypool/usr/home@my_recursive_snapshot      0      -   184K  -
```

データを複製せず共有するため、作成直後の追加使用量は小さくなります。ファイルをコピーして次のスナップショットを作る例です。

```shell
# cp /etc/passwd /var/tmp
# zfs snapshot mypool/var/tmp@after_cp
# zfs list -rt all mypool/var/tmp
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool/var/tmp                         206K  93.2G   118K  /var/tmp
mypool/var/tmp@my_recursive_snapshot    88K      -   152K  -
mypool/var/tmp@after_cp                   0      -   118K  -
```

新しいものだけでなく、以前のスナップショットのUSEDも変わっています。USEDはそのスナップショットだけが参照する領域などの計算に依存するため、単純な「その時点のファイル合計サイズ」や、常に前後の差分そのものではありません。各スナップショットは、その時点の完全な論理状態を参照できます。

<a id="zfs-zfs-snapshot-diff"></a>
#### スナップショットを比較する

`zfs diff` は、スナップショット間や現在の内容との変更を調べます。誤削除したファイルがどの時点まで存在したかを探す手掛かりになります。一つだけ指定すると現在の内容と比較します。

```shell
# zfs list -rt all mypool/var/tmp
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool/var/tmp                         206K  93.2G   118K  /var/tmp
mypool/var/tmp@my_recursive_snapshot    88K      -   152K  -
mypool/var/tmp@after_cp                   0      -   118K  -
# zfs diff mypool/var/tmp@my_recursive_snapshot
M       /var/tmp/
+       /var/tmp/passwd
```

| 表示 | 変更 |
|---|---|
| `+` | パス・ファイルの追加 |
| `-` | 削除 |
| `M` | 変更 |
| `R` | 名前変更 |

例ではpasswdを追加し、その親ディレクトリも変更されています。二つのスナップショットを指定して比べることもできます。

```shell
# cp /var/tmp/passwd /var/tmp/passwd.copy
# zfs snapshot mypool/var/tmp@diff_snapshot
# zfs diff mypool/var/tmp@my_recursive_snapshot mypool/var/tmp@diff_snapshot
M       /var/tmp/
+       /var/tmp/passwd
+       /var/tmp/passwd.copy
# zfs diff mypool/var/tmp@my_recursive_snapshot mypool/var/tmp@after_cp
M       /var/tmp/
+       /var/tmp/passwd
```

複製先で受信済みの二時点を比較すれば、どの変更をバックアップしたかも調べられます。[レプリケーション](#zfs-zfs-send)も参照してください。

<a id="zfs-zfs-snapshot-rollback"></a>
#### スナップショットへ戻す

`zfs rollback スナップショット名` は、データセットを取得時点へ戻します。開発試験や更新の失敗、誤削除などの復旧に使えます。変更が多ければ時間がかかる場合もありますが、処理中も整合性を保ちます。**その時点より後の、対象データセットの変更は失われます。** 稼働中のアプリケーションの扱いも考え、必要な現在のデータを退避してから戻します。

原文は現在のスナップショットも取っておく方法を勧めますが、古い時点へ戻す際には後述のとおり新しいスナップショットを削除する場合があります。後の状態を残したいなら、単に同じデータセットへ新しいスナップショットを作るだけで十分とは考えず、クローンや別の保存先などで保持方法を確認してください。

次はワイルドカードで余分なファイルまで削除してしまった例です。

```shell
# zfs list -rt all mypool/var/tmp
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool/var/tmp                         262K  93.2G   120K  /var/tmp
mypool/var/tmp@my_recursive_snapshot    88K      -   152K  -
mypool/var/tmp@after_cp               53.5K      -   118K  -
mypool/var/tmp@diff_snapshot              0      -   120K  -
# ls /var/tmp
passwd          passwd.copy     vi.recover
# rm /var/tmp/passwd*
# ls /var/tmp
vi.recover
```

直前のスナップショットへ戻します。

```shell
# zfs rollback mypool/var/tmp@diff_snapshot
# ls /var/tmp
passwd          passwd.copy     vi.recover
```

さらに古い時点を指定すると、新しいスナップショットがあるため拒否されます。

```shell
# zfs list -rt snapshot mypool/var/tmp
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool/var/tmp@my_recursive_snapshot    88K      -   152K  -
mypool/var/tmp@after_cp               53.5K      -   118K  -
mypool/var/tmp@diff_snapshot              0      -   120K  -
# zfs rollback mypool/var/tmp@my_recursive_snapshot
cannot rollback to 'mypool/var/tmp@my_recursive_snapshot': more recent snapshots exist
use '-r' to force deletion of the following snapshots:
mypool/var/tmp@after_cp
mypool/var/tmp@diff_snapshot
```

戻すには、途中のスナップショットも捨てる必要があります。**`-r` は後のスナップショットを削除する確認を兼ねる指定です。そこにしかない必要な状態がないことを確認してください。**

```shell
# zfs rollback -r mypool/var/tmp@my_recursive_snapshot
# zfs list -rt snapshot mypool/var/tmp
NAME                                   USED  AVAIL  REFER  MOUNTPOINT
mypool/var/tmp@my_recursive_snapshot     8K      -   152K  -
# ls /var/tmp
vi.recover
```

一覧でも途中のスナップショットがなくなったことを確認できます。これは「内容だけを昔に戻し、以後の全スナップショットを保持する」操作ではありません。

<a id="zfs-zfs-snapshot-snapdir"></a>
#### スナップショットから個別ファイルを戻す

ファイルシステムの `.zfs/snapshot/スナップショット名` から、保存時点の内容へアクセスできます。既定では `.zfs` 自体はls -aでも表示されませんが、名前を指定すれば使えます。`snapdir=visible` にすると一覧にも出ます。

```shell
# zfs get snapdir mypool/var/tmp
NAME            PROPERTY  VALUE    SOURCE
mypool/var/tmp  snapdir   hidden   default
# ls -a /var/tmp
.               ..              passwd          vi.recover
# zfs set snapdir=visible mypool/var/tmp
# ls -a /var/tmp
.               ..              .zfs            passwd          vi.recover
```

全体のロールバックが不要なら、該当時点から必要なファイルだけをコピーできます。

```shell
# rm /var/tmp/passwd
# ls -a /var/tmp
.               ..              .zfs            vi.recover
# ls /var/tmp/.zfs/snapshot
after_cp                my_recursive_snapshot
# ls /var/tmp/.zfs/snapshot/after_cp
passwd          vi.recover
# cp /var/tmp/.zfs/snapshot/after_cp/passwd /var/tmp
```

hiddenでも `ls .zfs/snapshot` などの直接指定は可能です。表示するかどうかはデータセット単位で設定します。反対方向に、スナップショットへ書こうとしても拒否されます。

```shell
# cp /etc/rc.conf /var/tmp/.zfs/snapshot/after_cp/
cp: /var/tmp/.zfs/snapshot/after_cp/rc.conf: Read-only file system
```

スナップショットは読み取り専用なので、追加・削除で保存時点を変更できません。`used` は保持に使う容量、`written` は前のスナップショットからその時点までに書いたデータ量を調べるための値です。

不要なら `zfs destroy データセット@名前` で削除します。`-r` は子の同名スナップショットも対象です。まず `-n -v` で、対象と解放見込みを実際には削除せず確認します。

<a id="zfs-zfs-snapshot-hold"></a>
#### スナップショットをholdで保護する

[hold](#zfs-term-hold)は、任意のタグを付けてスナップショットの削除を防ぎます。削除要求はEBUSYで失敗し、異なるタグのholdを複数持てます。複製元と複製先の共通スナップショットなど、ほかの処理が依存するものの誤削除防止に便利です。共通の基点を失うと、全体転送のやり直しが必要になる場合があります。

`zfs hold タグ スナップショット` で設定します。`-r` は子の同名にも適用します。

```shell
# zfs hold keepme mypool/var/tmp@my_recursive_snapshot
# zfs destroy mypool/var/tmp@my_recursive_snapshot
cannot destroy snapshot mypool/var/tmp@my_recursive_snapshot: dataset is busy
```

付いているタグと日時はholdsで表示します。

```shell
# zfs holds mypool/var/tmp@my_recursive_snapshot
NAME                                  TAG     TIMESTAMP
mypool/var/tmp@my_recursive_snapshot  keepme  Sat Jul 11 09:41 2026
```

解除はreleaseです。最後のholdを外すと、ほかの依存関係がなければ削除できるようになります。

```shell
# zfs release keepme mypool/var/tmp@my_recursive_snapshot
# zfs destroy mypool/var/tmp@my_recursive_snapshot
```

詳細は `zfs-hold(8)` を参照してください。

<a id="zfs-zfs-bookmark"></a>
### ブックマーク

[ブックマーク](#zfs-term-bookmark)は、スナップショットの時点を記録しますが、そのデータ自体は保持しません。その後にどれだけ変更しても使用容量はごく小さく、古いブロックの解放を妨げず、増分sendの基点に使えます。

別プールへ転送した後、送信元ではブックマークを作ってスナップショットを削除すると、受信側にデータを残し、送信元の容量を回収できます。名前の区切りは、スナップショットの `@` に対し `#` を使います。

```shell
# zfs snapshot mypool/data@snap1
# zfs send mypool/data@snap1 | zfs receive backup/data
# zfs bookmark mypool/data@snap1 mypool/data#snap1bm
# zfs destroy mypool/data@snap1
```

一覧は `-t bookmark` で表示します。

```shell
# zfs list -t bookmark mypool/data
NAME                 USED  AVAIL  REFER  MOUNTPOINT
mypool/data#snap1bm     -      -   184K  -
```

次のスナップショットを作り、ブックマークを増分の基点として送ります。

```shell
# zfs snapshot mypool/data@snap2
# zfs send -i mypool/data#snap1bm mypool/data@snap2 | zfs receive backup/data
```

受信側に、ブックマークと対応する元のスナップショットbackup/data@snap1が残っていることが前提です。**ブックマークは基点の情報だけなので、マウント、ロールバック、ファイル復元はできません。** 詳細は `zfs-bookmark(8)` と[増分バックアップ](#zfs-send-incremental)を参照してください。

<a id="zfs-zfs-clones"></a>
### クローンを管理する

クローンは、スナップショットを基に、書き込み可能なデータセットを作る機能です。独自のプロパティとマウント先を持てますが、作成元スナップショットへの依存があるため、それを削除できなくなります。

`zfs promote` はこの依存関係を逆転させ、元スナップショットをクローン側へ移します。容量の計上先は変わりますが、データを丸ごとコピーし直す操作ではなく、実消費量が突然増えるわけではありません。クローンは、元のマウント先の子に限らず配置できます。

次のデータセットで例を示します。

```shell
# zfs list -rt all camino/home/joe
NAME                    USED  AVAIL  REFER  MOUNTPOINT
camino/home/joe         108K   1.3G    87K  /usr/home/joe
camino/home/joe@plans    21K      -  85.5K  -
camino/home/joe@backup    0K      -    87K  -
```

元を残して試験するため、書き込み可能なクローンを作ります。

```shell
# zfs clone camino/home/joe@backup camino/home/joenew
# ls /usr/home/joe*
/usr/home/joe:
backup.txz     plans.txt

/usr/home/joenew:
backup.txz     plans.txt
# df -h /usr/home
Filesystem          Size    Used   Avail Capacity  Mounted on
usr/home/joe        1.3G     31k    1.3G     0%    /usr/home/joe
usr/home/joenew     1.3G     31k    1.3G     0%    /usr/home/joenew
```

作成時点では元のスナップショットと同じ内容ですが、以後は元と独立して変更できます。`origin` で依存元を確認し、promote後に変わることを示します。

```shell
# zfs get origin camino/home/joenew
NAME                  PROPERTY  VALUE                     SOURCE
camino/home/joenew    origin    camino/home/joe@backup    -
# zfs promote camino/home/joenew
# zfs get origin camino/home/joenew
NAME                  PROPERTY  VALUE   SOURCE
camino/home/joenew    origin    -       -
```

原文はpromoteを「独立したデータセットになる」と説明していますが、**別媒体へ全ブロックを複製する処理ではありません。** スナップショットの所有と依存方向を変えるものです。元データセットと新しい方は、削除しなくても共存できます。

クローンにloader.confを加え、旧データセットを削除して名前を引き継ぐ例です。**旧側だけに残るデータや依存するスナップショットがないかを確認してから削除します。**

```shell
# cp /boot/defaults/loader.conf /usr/home/joenew
# zfs destroy -f camino/home/joe
# zfs rename camino/home/joenew camino/home/joe
# ls /usr/home/joe
backup.txz     loader.conf     plans.txt
# df -h /usr/home
Filesystem          Size    Used   Avail Capacity  Mounted on
usr/home/joe        1.3G    128k    1.3G     0%    /usr/home/joe
```

最終的なデータセットには、元スナップショットの内容と追加したファイルが入ります。アプリケーションを入れたjailのひな型をスナップショットにし、クローンへ個別の変更を加える用途などで、構築と管理の手間を減らせます。

<a id="zfs-zfs-block-cloning"></a>
### ファイル単位のブロッククローン

[ブロッククローン](#zfs-term-block-cloning)は、個々のファイルのコピーにもCOWを使います。対応するcpの `copy_file_range(2)` により、同じプール内のコピーでデータブロックを共有し、後でどちらかを変更した部分だけを書きます。条件が合えば、コピー直後の追加容量と所要時間を大きく減らせます。

[重複排除](#zfs-zfs-deduplication)のような大きいチェックサム表は必要ありませんが、共有するのはコピーの時点で、別々に同じ内容を書いただけではまとめません。また、データセットの[クローン](#zfs-zfs-clones)と違い、スナップショットやorigin関係は不要です。

OpenZFS 2.2、FreeBSDでは14.0からのblock_cloning機能が必要です。実際に作成するかは `vfs.zfs.bclone_enabled` が制御し、原文では14.xの既定は0、15.0は1です。0なら通常コピーへ戻ります。14.xで有効にする例です。

```shell
# sysctl vfs.zfs.bclone_enabled=1
vfs.zfs.bclone_enabled: 0 -> 1
```

再起動後も適用するには `/etc/sysctl.conf` に記載します。

```text
vfs.zfs.bclone_enabled=1
```

`bcloneused`、`bclonesaved`、`bcloneratio` で使用量、節約量、比率を確認できます。

```shell
# cp /var/tmp/database.dump /var/tmp/database.copy
# zpool list -o name,bcloneused,bclonesaved,bcloneratio mypool
NAME    BCLONE_USED  BCLONE_SAVED  BCLONE_RATIO
mypool         1.7G          1.7G         2.00x
```

<a id="zfs-zfs-send"></a>
### レプリケーション

同じ場所の一つのプールだけでは、盗難、災害、操作ミスなどによる喪失に備えられません。定期的に別の保存先へバックアップします。ZFSには、[スナップショット](#zfs-zfs-snapshot)をストリームへ変換する `zfs send` と、それを受け取る `zfs receive` があります。ローカルの別プールや、ネットワーク越しの別ホストへ転送できます。

以下ではmypoolを通常の利用先、backupを複製先とします。

```shell
# zpool list
NAME    SIZE  ALLOC   FREE   CKPOINT  EXPANDSZ   FRAG   CAP  DEDUP  HEALTH  ALTROOT
backup  960M    77K   896M         -         -     0%    0%  1.00x  ONLINE  -
mypool  984M  43.7M   940M         -         -     0%    4%  1.00x  ONLINE  -
```

ZFSが自動的に複製先へ切り替えるわけではなく、障害時の切り替えは管理者が別途行います。また、転送するのは取得した時点のデータで、その後の変更は含みません。まずスナップショットを作ります。

```shell
# zfs snapshot mypool@backup1
# zfs list -t snapshot
NAME                    USED  AVAIL  REFER  MOUNTPOINT
mypool@backup1             0      -  43.6M  -
```

sendの出力はバイナリのストリームなので、端末へ直接は書けません。

```shell
# zfs send mypool@backup1
Error: Stream can not be written to a terminal.
You must redirect standard output.
```

ファイルに保存する例です。増分ではない全体送信なので、スナップショットのUSED欄だけでなく、送信対象のデータを収める空きが必要です。

```shell
# zfs send mypool@backup1 > /backup/backup1
# zpool list
NAME    SIZE  ALLOC   FREE   CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
backup  960M  63.7M   896M         -         -     0%     6%  1.00x  ONLINE  -
mypool  984M  43.7M   940M         -         -     0%     4%  1.00x  ONLINE  -
```

この段階は、backup上に**ストリームファイル**を保存しています。cronで定期化することもできます。

別の方法として、receiveへパイプすると、複製先でデータセットとして使える形に戻せます。最初の全体受信には、受信先が新規・空であるなどの条件が必要です。既存データのある場所へ上書きしないよう確認します。

```shell
# zfs snapshot mypool@replica1
# zfs send -v mypool@replica1 | zfs receive backup/mypool
full send of mypool@replica1 estimated size is 50.1M
total estimated size is 50.1M
TIME        SENT   SNAPSHOT mypool@replica1
10:22:01   9.75M   mypool@replica1
10:22:02   25.4M   mypool@replica1

# zpool list
NAME    SIZE  ALLOC   FREE   CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
backup  960M  63.7M   896M         -         -     0%     6%  1.00x  ONLINE  -
mypool  984M  43.7M   940M         -         -     0%     4%  1.00x  ONLINE  -
```

転送が完了すれば、受信側のデータへ直接アクセスできます。この例のルートデータセットの送信だけで、子データセットもすべて送られるわけではありません。階層全体の転送は後述の `-R` を使います。

<a id="zfs-send-incremental"></a>
#### 増分バックアップ

`zfs send -i` は、二時点の違いだけを転送します。毎回全体を送り直すより、容量と時間を減らせます。まず新しいスナップショットを作ります。

```shell
# zfs snapshot mypool@replica2
# zfs list -t snapshot
NAME                    USED  AVAIL  REFER  MOUNTPOINT
mypool@replica1         5.72M      -  43.6M  -
mypool@replica2             0      -  44.1M  -
# zpool list
NAME    SIZE  ALLOC   FREE   CKPOINT  EXPANDSZ   FRAG   CAP  DEDUP  HEALTH  ALTROOT
backup  960M  61.7M   898M         -         -     0%    6%  1.00x  ONLINE  -
mypool  960M  50.2M   910M         -         -     0%    5%  1.00x  ONLINE  -
```

最初のreplica1が受信側にも存在することを確認し、replica1からreplica2までを送ります。

```shell
# zfs send -v -i mypool@replica1 mypool@replica2 | zfs receive backup/mypool
send from @replica1 to mypool@replica2 estimated size is 5.02M
total estimated size is 5.02M
TIME        SENT   SNAPSHOT mypool@replica2

# zpool list
NAME    SIZE  ALLOC   FREE   CKPOINT  EXPANDSZ   FRAG  CAP  DEDUP  HEALTH  ALTROOT
backup  960M  80.8M   879M         -         -     0%   8%  1.00x  ONLINE  -
mypool  960M  50.2M   910M         -         -     0%   5%  1.00x  ONLINE  -

# zfs list
NAME                         USED  AVAIL  REFER  MOUNTPOINT
backup                      55.4M   240G   152K  /backup
backup/mypool               55.3M   240G  55.2M  /backup/mypool
mypool                      55.6M  11.6G  55.0M  /mypool

# zfs list -t snapshot
NAME                                         USED  AVAIL  REFER  MOUNTPOINT
backup/mypool@replica1                       104K      -  50.2M  -
backup/mypool@replica2                          0      -  55.2M  -
mypool@replica1                             29.9K      -  50.0M  -
mypool@replica2                                 0      -  55.0M  -
```

低速な回線や転送量に応じた料金の環境でも、変更分だけなら効率的です。スナップショット自体は各時点の完全な状態を参照し、増分**ストリーム**が変更分だけを表す点を区別してください。

`-p` は圧縮、クォータ、マウント先などのプロパティも含め、`-R` は子データセットなどを含む複製パッケージを送ります。[送信オプション](#zfs-send-options)を確認し、自動化する際も共通の基点を保持します。

<a id="zfs-send-options"></a>
#### 送信ストリームのオプション

`-p` はデータセットのプロパティを含めます。`-R` は指定時点までのデータセット階層、スナップショット、クローン、プロパティを含む複製パッケージを作り、-pも含意します。`-v` は送信量などの進捗を表示します。[SSHの例](#zfs-send-ssh)では階層全体を送っています。

ブロックの形式を調整する指定もあります。

- `-L`：128KBを超えるブロックを分割せずに送ります。
- `-e`：embedded_data機能でブロックポインタ内へ収めた小さい内容に、WRITE_EMBEDDED形式を使い、コンパクトにします。
- `-c`：圧縮済みブロックを展開せず圧縮のまま送り、転送量と両側のCPU処理を減らします。
- `-w`：暗号化データセットをディスク上の形式のまま送り、送信時に鍵を読み込む必要もありません。[暗号化データセットの送信](#zfs-encrypted-send)を参照してください。非暗号化では-Lecと同等です。

原文は新しいプールで `-Lec` を基本的な組み合わせとして紹介しています。ただし、受信側がストリームで使う全機能へ対応する必要があり、未対応ならreceiveが拒否します。`zfs-send(8)`、`zpool-features(7)` で互換性を確認してください。

<a id="zfs-send-resume"></a>
#### 中断した転送を再開する

受信側に `-s` を指定すると、切断や再起動などで転送が途切れても、途中までの状態を保存して再開できます。

```shell
# zfs send -v mypool@replica1 | zfs receive -s backup/mypool
full send of mypool@replica1 estimated size is 50.1M
total estimated size is 50.1M
TIME        SENT   SNAPSHOT mypool@replica1
10:31:01   9.75M   mypool@replica1
^C
```

受信側の `receive_resume_token` に、対象と受信位置を表すトークンが残ります。これを送信側の `zfs send -t` へ渡します。

```shell
# zfs get -H -o value receive_resume_token backup/mypool
1-1211c4f4a-f8-789c636064000310a501c49c50360710a715e5e7a69766a63040c1eabb735735ce8f8d5420c0e5c9e8d4d3d28a5388e4d3d200
# zfs send -t $(zfs get -H -o value receive_resume_token backup/mypool) | zfs receive -s backup/mypool
```

この例は同じホストで値を取得しています。別ホスト間なら、受信側からトークンを取得して送信側へ渡す必要があります。再開が完了すると途中状態は消えます。それまでは容量を消費し、同じデータセットへの別の受信を妨げます。再開せず破棄するには次を使います。

```shell
# zfs receive -A backup/mypool
```

<a id="zfs-send-ssh"></a>
#### SSHで暗号化してバックアップを送る

通常の非暗号化データセットのsendストリームを、そのままネットワークへ送ると、通信路で内容を読まれる危険があります。SSHへパイプすれば通信を暗号化できます。受信先での保存も暗号化したままにするには、[ZFSネイティブ暗号化](#zfs-native-encryption)と[raw送信](#zfs-encrypted-send)を使います。通信の保護と保存の保護は別の話です。

自動化では、送受信ホスト間に鍵によるSSH認証を用意します。通常は強い権限が必要ですが、rootのSSHログインを開く代わりに、[権限委譲](#zfs-zfs-allow)で専用の一般ユーザーへ必要な操作を許可できます。SSH全般は[OpenSSH](https://docs.freebsd.org/en/books/handbook/security/#openssh)を参照してください。

送信側でsendとsnapshotを許可する例です。

```shell
# zfs allow -u someuser send,snapshot mypool
```

受信側はcreate・mount・receiveの権限と、マウント先の所有権を用意します。一般ユーザーのマウントを有効にする設定も含み、システム全体に影響するため、必要性を確認してください。

```shell
# sysctl vfs.usermount=1
vfs.usermount: 0 -> 1
# echo vfs.usermount=1 >> /etc/sysctl.conf
# zfs create recvpool/backup
# zfs allow -u someuser create,mount,receive recvpool/backup
# chown someuser /recvpool/backup
```

一般ユーザーとして再帰スナップショットを作り、backuphostへ転送する例です。

```shell
% zfs snapshot -r mypool/home@monday
% zfs send -R mypool/home@monday | ssh someuser@backuphost zfs recv -dvu recvpool/backup
```

`-R` はhomeと子、スナップショット、クローン、設定を含めます。受信の `-d` は送信元パスの先頭、通常はプール名を落とし、残りをrecvpool/backupの下へ接続します。`-u` は受信後にマウントしない指定、`-v` は詳細表示です。接続先には確認したIPアドレスや完全修飾ドメイン名を使います。

<a id="zfs-recv-corrective"></a>
#### 正常な複製から破損ブロックを修復する

冗長性が足りずスクラブで直せない破損でも、同じスナップショットの正常な複製が別プールにあれば、`zfs receive -c` の**corrective receive**で修復できる場合があります。ロールバックや名前変更をせず、ストリーム中の正常データから破損ブロックを直します。OpenZFS 2.2、FreeBSDでは14.0以降が必要です。

単一ディスクのプールで、恒久的なデータエラーを検出した例です。

```shell
# zpool status -v mypool
  pool: mypool
 state: ONLINE
status: One or more devices has experienced an error resulting in data
        corruption.  Applications may be affected.
action: Restore the file in question if possible.  Otherwise restore the
        entire pool from backup.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-8A
  scan: scrub repaired 0B in 00:01:22 with 1 errors on Sat Jul 11 09:14:37 2026
config:

        NAME        STATE     READ WRITE CKSUM
        mypool      ONLINE       0     0     0
          ada0      ONLINE       0     0     2

errors: Permanent errors have been detected in the following files:

        /mypool/reports/summary-2026.db
```

mypoolのreplica2が破損ブロックを参照し、backup側には同じスナップショットの正常なコピーがあるとします。そこから送り、修復後にスクラブで確認します。

```shell
# zfs send backup/mypool@replica2 | zfs receive -c mypool@replica2
# zpool scrub -w mypool
# zpool status mypool | grep errors:
errors: No known data errors
```

**同じスナップショットであることが必要です。** ストリームに含むデータブロックだけが対象で、メタデータや取得後の書き込みは修復できません。最後に必ずスクラブし、破損が残っていないか確認します。

<a id="zfs-zfs-quota"></a>
### データセット・ユーザー・グループのクォータ

[quota](#zfs-term-quota)はデータセットとその子・スナップショットを含む使用量、[refquota](#zfs-term-refquota)は子やスナップショットを除く、そのデータセット自身を制限します。[ユーザー](#zfs-term-userquota)・[グループ](#zfs-term-groupquota)別の制限も可能です。任意のディレクトリツリーをまとめるには後述のプロジェクトクォータを使います。

以下はユーザーが存在する例です。新しく作る場合は、先にホーム用データセットと `/home/bob` などのマウント先を用意し、アカウント作成時にそこをホームへ指定します。既存のホームを隠さず、所有者とグループを正しく設定します。

quotaを10Gにする例です。

```shell
# zfs set quota=10G storage/home/bob
```

refquotaを10Gにする例です。

```shell
# zfs set refquota=10G storage/home/bob
```

quotaの解除です。refquotaを設定した場合は、それも別に確認してください。

```shell
# zfs set quota=none storage/home/bob
```

ユーザー別は `userquota@ユーザー=容量` です。指定にはjoeのようなPOSIX名、789のような数値ID、joe.bloggs@example.comのようなSID名、S-1-123-456-789のようなSID数値形式を使えます。

```shell
# zfs set userquota@joe=50G storage/home/joe
```

解除はnoneです。

```shell
# zfs set userquota@joe=none storage/home/joe
```

ユーザークォータは `zfs get all` に列挙されません。一般ユーザーは通常ほかの人のクォータを見られず、userquota権限の委譲を受けたユーザーは全員分を表示・変更できます。

グループ別は `groupquota@グループ=容量` です。

```shell
# zfs set groupquota@firstgroup=50G storage/home
```

解除する例です。

```shell
# zfs set groupquota@firstgroup=none storage/home
```

一般ユーザーが確認できるのは通常、自分が所属するグループの値です。rootまたはgroupquota権限のあるユーザーは全体を表示・変更できます。

使用量と制限は `zfs userspace`、グループは `zfs groupspace` で調べられます。詳細は `zfs-userspace(8)` を参照してください。データセットquotaの確認例です。

```shell
# zfs get quota storage/home/bob
```

<a id="zfs-zfs-quota-project"></a>
#### プロジェクトクォータ

一つのデータセットに複数プロジェクトのツリーがあり、ユーザー別・データセット別では区切れない場合に使います。ファイルとディレクトリへ数値のプロジェクトIDを付け、同じIDの使用量を制限します。

既存のツリーへID 42を再帰的に設定し、新規ファイルや子ディレクトリへ継承させる例です。

```shell
# zfs project -s -p 42 -r /storage/proj
```

同じプロジェクトの容量を100Gへ制限します。

```shell
# zfs set projectquota@42=100G storage
```

使用量はprojectspaceで表示できます。

```shell
# zfs projectspace -o name,used,quota storage
NAME   USED  QUOTA
42    1.95G   100G
```

`projectobjquota` は同様にオブジェクト数を制限します。`zfs project -d` はディレクトリのID表示、`zfs project -C` はクリアです。`zfs-project(8)` と `zfsprops(7)` を参照してください。

<a id="zfs-zfs-reservation"></a>
### 容量を予約する

[reservation](#zfs-term-reservation)は、データセット向けに確保する容量を指定します。その分はほかのデータセットが使えなくなります。重要なデータやログ用の空きを確保する用途があります。

```shell
# zfs set reservation=10G storage/home/bob
```

解除するにはnoneを指定します。

```shell
# zfs set reservation=none storage/home/bob
```

子・スナップショットを除くデータセット自身向けの[refreservation](#zfs-term-refreservation)も同様の形式です。両方の設定を確認します。

```shell
# zfs get reservation storage/home/bob
# zfs get refreservation storage/home/bob
```

<a id="zfs-zfs-compression"></a>
### 圧縮

ZFSはブロックを透過的に圧縮し、容量を節約します。ディスクへ書く量が減るため、CPU処理との兼ね合いで実効的な速度が上がる場合もあります。原文は25%圧縮で125%の書き込み速度という例を挙げますが、削減率と倍率の定義が曖昧です。実際の効果は圧縮率・CPU・I/Oに依存し、一律の速度向上を保証しません。重複排除の大きな管理テーブルを必要としない点も利点です。

原文ではOpenZFS 2.2以降、新規プール・データセットの既定はcompression=onで、LZ4を選ぶとしています。LZ4は比較的軽量で、データの初期部分を試して十分な圧縮が見込めなければ早期中止し、既圧縮・圧縮不能なデータへのCPUの浪費を避けます。原文の目安は12.5%です。アルゴリズムの違いは[用語](#zfs-term-compression)を参照してください。

**変更は新しい書き込みへ適用され、既存データは書き直されるまで元の形式です。** [zfs rewrite](#zfs-zfs-rewrite)も参照してください。

```shell
# zfs get used,compressratio,compression,logicalused mypool/compressed_dataset
NAME                       PROPERTY       VALUE  SOURCE
mypool/compressed_dataset  used           449G   -
mypool/compressed_dataset  compressratio  1.11x  -
mypool/compressed_dataset  compression    lz4    local
mypool/compressed_dataset  logicalused    496G   -
```

例では物理的なusedが449G、圧縮前の論理量logicalusedが496G、比率が約1.11倍です。

ユーザークォータは圧縮後の実使用量を基準にします。同じ論理量でも、更新後に圧縮しにくくなると制限に達することがあります。逆に圧縮しやすければ、クォータより大きな論理量を保存できます。バックアップ容量をクォータから見積もる場合も、非圧縮の保存先へは収まらない可能性に注意してください。

<a id="zfs-zfs-compression-zstd"></a>
### Zstandard圧縮

OpenZFS 2.0で加わったZstandard（Zstd）は、一般にLZ4より高い圧縮率と、gzipより高速な処理を狙える方式です。多数のレベルで速度と圧縮率を調整でき、展開速度は圧縮レベルに左右されにくいため、一度書いて繰り返し読むデータにも適します。

圧縮済みの形をメモリへ保持するcompressed ARCにより、同じRAMにより多くのデータ・メタデータを置け、ヒット率を高められる場合があります。更新が多い用途でも圧縮が有利になることがあります。

通常のレベルは1〜19で、高いほど書き込み時の圧縮が重くなります。原文の既定はzstd-3です。10を超えるレベルはブロックごとの必要メモリが大きく、原文はRAMが16GB未満のシステムでの利用を避けるよう注意しています。

速度を優先するfast系列には、zstd-fast-1〜10、20〜100の10刻み、500・1000があります。速い設定ほど圧縮率は低くなります。

圧縮用メモリを確保できなければ、ブロックを非圧縮で保存します。特にメモリの少ない環境で高レベルを使うと起こり得ます。ZFSモジュールの読み込み以降の回数は `kstat.zfs.misc.zstd.compress_alloc_fail` で確認できます。

<a id="zfs-zfs-rewrite"></a>
### 既存データを書き直す

原文では、`zfs rewrite` はOpenZFS 2.4、FreeBSDでは15.0からの機能です。`compression`、`checksum`、`dedup`、`copies` などを変更しても、既存ブロックには遡って適用されません。従来のsend/receiveやファイルの往復コピーに代えて、既存ファイルのブロックを原子的な読み書き直しに相当する形で更新できます。

指定するのはデータセット名ではなく、**ファイルやディレクトリのパス**です。新しい圧縮方式を全体へ適用する例です。

```shell
# zfs set compression=zstd mypool/archive
# zfs rewrite -r /mypool/archive
```

`-v` は対象ファイルを表示し、`-x` は子データセットなどのマウント境界を越えません。`-o` と `-l` でファイル内の範囲を絞れます。recordsizeのように論理ブロックサイズを変える設定は、この書き直しでは変わりません。

新しいブロックを作るため、以前のスナップショットが古いブロックを保持すると容量が増えます。読み取り専用のスナップショット自体を書き直すこともできません。詳細は `zfs-rewrite(8)` を参照してください。

<a id="zfs-zfs-deduplication"></a>
### 重複排除

[重複排除](#zfs-term-deduplication)は、ブロックのチェックサムから同一内容を見つけ、データを重複保存する代わりに既存ブロックへの参照を追加します。重複が多いデータでは大きく容量を減らせますが、管理テーブルのメモリ負担が大きい機能です。原文は、まず圧縮で得られる効果を検討するよう勧めています。

dedupはプールではなく**データセットのプロパティ**です。

```shell
# zfs set dedup=on pool
```

この例はプールと同名のルートデータセットへ設定するため、子が継承します。実際に重複が多い対象へ絞ると、テーブルを小さくできます。有効化後に書くデータだけが対象で、既存分は自動的に重複排除されません。対応するFreeBSD 15.0ではrewriteで通し直せます。

```shell
# zpool list
NAME  SIZE ALLOC  FREE   CKPOINT  EXPANDSZ   FRAG   CAP   DEDUP   HEALTH   ALTROOT
pool 2.84G 2.19M 2.83G         -         -     0%    0%   1.00x   ONLINE   -
```

DEDUPの1.00xは、まだ節約がない状態です。システムの実行ファイルを三つのディレクトリへコピーする例です。実際に試すなら、対象データセット内の作業ディレクトリで行います。

```shell
# for d in dir1 dir2 dir3; do
> mkdir $d && cp -R /usr/bin $d &
> done
```

重複の効果を確認します。

```shell
# zpool list
NAME SIZE  ALLOC  FREE   CKPOINT  EXPANDSZ   FRAG  CAP   DEDUP   HEALTH   ALTROOT
pool 2.84G 20.9M 2.82G         -         -     0%   0%   3.00x   ONLINE   -
```

3.00xは、同じ内容の三コピーをおおむね一つ分のブロックで保持できた例です。ブロックを追跡するDDTが必要で、原文は重複排除対象1TBにつきRAM約5〜6GBという概算を示しています。実際はブロック数などに依存します。表がメモリへ収まらないと、参照のためのディスクI/Oで大きく遅くなる場合があります。

既存プールで節約見込みを試算する例です。

```shell
# zdb -S pool
Simulated DDT histogram:

bucket              allocated                       referenced
______   ______________________________   ______________________________
refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
------   ------   -----   -----   -----   ------   -----   -----   -----
     1    2.58M    289G    264G    264G    2.58M    289G    264G    264G
     2     206K   12.6G   10.4G   10.4G     430K   26.4G   21.6G   21.6G
     4    37.6K    692M    276M    276M     170K   3.04G   1.26G   1.26G
     8    2.18K   45.2M   19.4M   19.4M    20.0K    425M    176M    176M
    16      174   2.83M   1.20M   1.20M    3.33K   48.4M   20.4M   20.4M
    32       40   2.17M    222K    222K    1.70K   97.2M   9.91M   9.91M
    64        9     56K   10.5K   10.5K      865   4.96M    948K    948K
   128        2   9.50K      2K      2K      419   2.11M    438K    438K
   256        5   61.5K     12K     12K    1.90K   23.0M   4.47M   4.47M
    1K        2      1K      1K      1K    2.98K   1.49M   1.49M   1.49M
 Total    2.82M    303G    275G    275G    3.20M    319G    287G    287G

dedup = 1.05, compress = 1.11, copies = 1.00, dedup * compress / copies = 1.16
```

表示末尾は `dedup × compress ÷ copies` の組み合わせです。例の1.16は主に圧縮によるもので、dedup単独の1.05は小さい効果です。原文は「容量を全く節約しない」とも述べていますが、正確には、表示上は小さい節約でも、メモリやI/Oの費用に見合いにくいという判断です。

OpenZFS 2.3、FreeBSDでは15.0からの**fast dedup**は、更新をディスク上のログへまとめてからDDTへ反映し、ランダムI/Oを減らします。`dedup_table_quota` はDDTのディスク容量の上限で、到達すると新しい項目の追加を止めます。原文の既定autoでは、専用dedup vdevの容量を上限に使います。現在の表サイズは `dedup_table_size` で確認できます。

`zpool ddtprune -p 30 pool` は節約を生まない単一参照の古い項目から30%を取り除き、`-d 日数` ならその日数より古い単一参照を対象にします。`zpool status -DD pool` は参照数ごとの分布などを表示します。高速な[dedup vdev](#zfs-zpool-special)は表がRAMを超える場合の検索を助けます。

十分な節約が見込め、DDTを扱う資源が確保できる場合に重複排除を検討します。

<a id="zfs-zfs-jail"></a>
### ZFSとjail

`zfs jail` と `jailed` プロパティでデータセットを[jail](16-jails.md)へ渡せます。`zfs unjail` は接続を外します。jail内で制御するデータセットはjailedをonにします。ホスト側でそのデータセットのマウントを許すと、jail側が設定したマウント先によりホストの安全を損なう場合があるため、制限されています。

jailの管理者は委譲された部分木の中でマウント、子の作成、スナップショット、プロパティ変更などを行えます。`allow.mount`、`allow.mount.zfs`、2未満の `enforce_statfs` が必要です。詳細は `jail(8)` を参照します。

稼働中のmyjailへ渡す例です。

```shell
# zfs create mypool/jaildata
# zfs set jailed=on mypool/jaildata
# zfs jail myjail mypool/jaildata
```

jail内のzfs listへ現れ、管理できるようになります。`zfs unjail myjail mypool/jaildata` でホストへ制御を戻せます。詳細は `zfs-jail(8)` を参照してください。

FreeBSD 15.0では `zfs.dataset` パラメータで起動時の接続を自動化できます。先にjailed=onを設定し、allow.mount.zfsも許可します。

```text
myjail {
    path = "/usr/local/jails/myjail";
    host.hostname = "myjail.example.org";
    exec.start = "/bin/sh /etc/rc";
    exec.stop = "/bin/sh /etc/rc.shutdown";
    allow.mount;
    allow.mount.zfs;
    enforce_statfs = 1;
    zfs.dataset = "mypool/jaildata";
}
```

さらに `zfs.mount_snapshot=1` を許可すれば、委譲したファイルシステムの `.zfs` 配下でスナップショット内容にもアクセスできます。

<a id="zfs-zfs-allow"></a>
## 管理権限の委譲

一般ユーザーへ必要なZFS管理操作だけを許可できます。ホームのスナップショット管理、バックアップ担当者の送受信、容量統計だけを読むスクリプトなどが例です。サブコマンドや多くのプロパティごとに指定でき、権限を再委譲する能力も許可できます。

<a id="zfs-zfs-allow-create"></a>
### データセット作成を委譲する

`zfs allow someuser create mydataset` は、指定した親の下に子データセットを作る権限を与えます。ただし、作成時のマウントには別の条件もあります。一般ユーザーのマウントを `vfs.usermount=1` で許可し、そのユーザーがマウントポイントを所有している必要があります。システム側のマウント制限と、ZFSの委譲を両方確認します。

<a id="zfs-zfs-allow-allow"></a>
### 権限を再委譲する能力を許可する

`zfs allow someuser allow mydataset` は、そのデータセットや子について、自分が持つ権限を他ユーザーへ渡すことを許可します。snapshotとallowの両方があれば、snapshotを他ユーザーへ委譲できます。自分にない任意の管理権限まで作り出せるという意味ではありません。

<a id="zfs-native-encryption"></a>
## ZFSネイティブ暗号化

ZFSはデータセット単位の暗号化を提供します。FreeBSD固有のGELIを必要とせず、同じプール機能へ対応するほかのシステムでも使える利点があります。スナップショットやraw複製、スクラブなどは、内容を平文に戻さず実施でき、暗号化中も完全性検証や圧縮が機能します。

同じプールでも、ユーザーごとに異なる鍵・方法を使い、互いの鍵を共有せずに運用できます。ただし、**鍵を読み込んだ後のアクセスは通常のファイル権限でも制御します。暗号化だけで、同じホスト上の強い管理権限などから読み込み済みデータを隔離するわけではありません。**

主な制約を確認します。

- プール全体ではなくデータセット単位です。
- 固定原文では、FreeBSDのloaderはネイティブ暗号化データセットからの起動に未対応です。
- 作成時に有効化する必要があり、後から既存の非暗号化データセットをそのまま切り替えられません。
- 暗号方式、鍵長、モードは、設定後に変更できません。
- **すべてのメタデータを暗号化するわけではありません。**

暗号化する対象は、ファイル・zvolのデータ、ファイル属性、ACL、アクセス権ビット、ディレクトリ内容、FUIDマッピング、userused/groupused情報、重複排除されたデータです。

一方、プール構成と名前、データセット・スナップショットの名前、階層、プロパティ、ファイルサイズ、穴の情報、重複排除テーブルなどは暗号化されません。この区別により、鍵がなくてもスクラブなどの保守と破損検出・修復を行えます。

既存データを暗号化したい場合は、暗号化を有効にして作った別データセットへ移します。通常はパスフレーズなどで鍵をメモリへ読み込み、内容を利用可能にします。再び利用不能にするには、アンマウントに加え鍵のアンロードも必要です。

圧縮は暗号化より先に行います。通常の256ビットチェックサムに代え、暗号化では128ビットのチェックサムと暗号方式が提供する128ビットMACを使い、不正な変更の検出も行います。

重複排除は、暗号化データセットとそのスナップショット・クローンの範囲に限られます。プール全体で照合しないため情報漏えいを抑えますが、節約効率は下がり、同じブロックであることの情報とCPU負荷は残ります。embedded_dataとは併用できず、第三コピー用の位置を暗号化メタデータに使うため、copies=3も指定できません。

<a id="zfs-encrypted-dataset-creation"></a>
### 暗号化データセットを作る

`zfs create` の時点でencryption=onを指定します。作成後のsetでは遡って暗号化されません。パスフレーズを対話入力する例です。

```shell
# zfs create -o encryption=on -o keyformat=passphrase -o keylocation=prompt zroot/secretdata
Enter passphrase:
Re-enter passphrase:
```

8文字未満なら拒否されます。これは受け付ける最小長であり、安全なパスフレーズを保証する基準ではありません。二度の入力が一致すると作成・マウントされます。

内容は保存時に暗号化されますが、**非暗号化の場所へコピーすると平文として保存されます。** 必要ならマウント先を変えられます。

```shell
# zfs set mountpoint=/secretdata zroot/secretdata
# echo "Hello FreeBSD!" > /secretdata/message
# cat /secretdata/message
Hello FreeBSD!
```

鍵が読み込まれた現在は、通常のアクセス権を持つユーザーが読み書きできます。

<a id="zfs-encrypted-dataset-properties"></a>
### 暗号化のプロパティ

<a id="zfs-term-encryptionroot"></a>
<a id="zfs-term-keyformat"></a>
<a id="zfs-term-encryption"></a>
<a id="zfs-term-keystatus"></a>
<a id="zfs-term-keylocation"></a>
<a id="zfs-term-pbkdf2iters"></a>

暗号化方式と鍵の扱いを確認します。

```shell
# zfs get encryption,keylocation,keyformat zroot/secretdata
NAME              PROPERTY     VALUE        SOURCE
zroot/secretdata  encryption   aes-256-gcm  -
zroot/secretdata  keylocation  prompt       local
zroot/secretdata  keyformat    passphrase   -
```

例のaes-256-gcmは、固定原文でencryption=onが選ぶ方式です。encryptionやkeyformatは通常のzfs setでは変更できず、一部の鍵関連設定は[change-key](#zfs-change-encryption-key)を使います。

| プロパティ | 内容 |
|---|---|
| `encryptionroot` | 鍵を継承する元のデータセット。クローンは元と同じ鍵を使います。 |
| `keyformat` | raw・hex・passphrase。rawとhexは32バイトのランダム鍵を表します。hexはそれを16進数の表現で保持する点を区別します。 |
| `encryption` | 方式・鍵長・モード。off（既定）、on、aes-128-ccm、aes-192-ccm、aes-256-ccm、aes-128-gcm、aes-192-gcm、aes-256-gcmを指定でき、設定後は変更できません。暗号化データセット作成時にはkeyformatも指定します。 |
| `keystatus` | none・available・unavailableで鍵の状態を示します。 |
| `keylocation` | prompt、`file://path/to/file`、`http://some.address`、`https://other.address` などの読み込み元。 |
| `pbkdf2iters` | パスフレーズから鍵を導く反復回数。原文の既定は350000で、推測攻撃に必要な計算を増やすものです。計算資源の変化も踏まえて判断します。 |

<a id="zfs-unload-encryption-key"></a>
### 暗号鍵をアンロードする

内容を再び保護するには、**アンマウントだけでなく、メモリ上の鍵もアンロード**します。マウント中のunload-keyは拒否されます。

```shell
# zfs unmount zroot/secretdata
# zfs unload-key zroot/secretdata
```

繰り返すと、すでにアンロード済みというエラーになります。次に使う際は[鍵を読み込み](#zfs-load-encryption-key)、必要な認証を行います。

<a id="zfs-load-encryption-key"></a>
### 暗号鍵を読み込む

鍵を読み込む前の状態と、マウントの失敗例です。

```shell
# zfs get keystatus zroot/secretdata
NAME              PROPERTY   VALUE        SOURCE
zroot/secretdata  keystatus  unavailable  -
# zfs mount zroot/secretdata
cannot mount 'zroot/secretdata': encryption key not loaded
```

load-keyを実行し、パスフレーズを入力します。

```shell
# zfs load-key zroot/secretdata
Enter passphrase for 'zroot/secretdata':
# zfs get keystatus zroot/secretdata
NAME              PROPERTY   VALUE      SOURCE
zroot/secretdata  keystatus  available  -
```

availableになったらマウントします。

```shell
# zfs mount zroot/secretdata
# mount|grep secretdata
zroot/secretdata on /secretdata (zfs, local, noatime, nfsv4acls)
```

`-r` は複数の鍵を再帰的に読み込みます。すでに読み込み済みの鍵へ再実行するとエラーになります。

```shell
# zfs load-key zroot/secretdata
Key load error: Key already loaded for 'zroot/secretdata'.
```

keystatusでも確認できます。パスフレーズが正しいかだけを調べ、鍵を読み込まない試行には `-n` を使います。

<a id="zfs-change-encryption-key"></a>
### 鍵・パスフレーズを変更する

`zfs change-key` は、データ全体を暗号化し直さず、パスフレーズなどの鍵の保護方法を変更できます。

```shell
# zfs change-key zroot/secretdata
Enter new passphrase for 'zroot/secretdata':
Re-enter new passphrase for 'zroot/secretdata':
```

現在の鍵が読み込み済みであることが必要です。未読込でも新しい値を尋ねられた後に警告される場合があるので、先にkeystatusを確認します。

`-o` でkeylocation、keyformat、pbkdf2itersも変更できます。独自の鍵へ変更した子データセットは新しいencryption rootになり、`-i` は親の鍵の継承へ戻す指定です。親の鍵を変更すると、それを継承する子にも適用されます。子を分離するには、作成時に異なるkeyformatを使うか、子でchange-keyします。

暗号化クローンはoriginと同じ鍵を使います。keystatus・keyformat・keylocation・pbkdf2itersは、通常のプロパティのような単純な親子継承ではなく、encryptionrootの値に結び付きます。読み取り専用のencryptionrootで確認します。

**鍵の漏えいへの対処を、パスフレーズ変更だけで済ませないでください。** データを暗号化するマスターキー自体は同じで、新しい書き込みにも使います。攻撃者が旧ユーザー鍵と、それで保護されたマスターキーを取得していれば、change-key後も解読できる場合があります。以前の鍵情報がディスク上へ残る期間も一定ではありません。

原文はマスターキー漏えい時に、媒体を安全に消去して新しいプールを作り、バックアップから復元する方法を勧めています。別案として、新しい暗号化データセットへsend/receiveで移し、解放領域へsecure TRIM、非対応ならinitializeを行う方法も挙げています。ただし、**通常の初期化やデータ移行が、媒体の全履歴領域の安全な消去を保証するとは限りません。** 機器の消去機能と保証範囲を確認し、旧鍵の漏えいを解消できる方法として判断してください。

<a id="zfs-encrypted-send"></a>
### 暗号化データセットを送信する

暗号化データセットでもスナップショットを作れます。

```shell
# zfs snapshot zroot/secretdata@snap1
```

`zfs send -w` はraw送信です。暗号化ブロックをそのまま転送し、受信側は平文やパスフレーズを知る必要がありません。鍵を読み込まずバックアップでき、保存先を完全には信頼できない場合にも、内容を秘匿した形で置けます。ただし、保存先による削除や古いコピーへの差し替えまで防ぐものではありません。

```shell
# zfs send -w zroot/secretdata@snap1 | zfs recv backup/secret
```

`-w` を付けない送信は、復号した形式です。受信側で別の鍵により暗号化し直すこともできますが、その宛先へ以後rawの増分を継続できなくなる制約があります。通信路の保護は[SSH](#zfs-send-ssh)などで別途行います。

<a id="zfs-zfskeys"></a>
### 起動時に暗号鍵を読み込む

rcの `zfskeys` は、keylocationが `file://` の鍵ファイルを指すデータセットについて、プールimport後・マウント前に鍵を読み込みます。promptは対象外で、起動後に手動でload-keyします。

パスフレーズから鍵ファイルへ切り替える例です。ランダムな32バイトを作り、所有者だけが読めるようにしてchange-keyします。指定先に既存の鍵がないか確認してください。

```shell
# dd if=/dev/random of=/root/secretdata.key bs=32 count=1
# chmod 600 /root/secretdata.key
# zfs change-key -o keyformat=raw -o keylocation=file:///root/secretdata.key zroot/secretdata
```

サービスを有効にします。

```shell
# sysrc zfskeys_enable="YES"
```

既定ではfile://の全対象を読みます。限定するには空白区切りで列挙します。

```shell
# sysrc zfskeys_datasets="zroot/secretdata"
```

**鍵ファイルを読める人は復号できます。** root所有、モード600とし、暗号化されたルートや、起動時だけ接続する取り外し媒体など、保護した保存先へ置きます。データと鍵を同じ無保護の媒体へ置くと、暗号化の目的を果たせない場合があります。

<a id="zfs-boot-environments"></a>
## ブート環境

ブート環境は、FreeBSDのOSを含むデータセット階層の、起動可能なクローンです。Root-on-ZFSの標準配置では `zroot/ROOT` 以下にあり、稼働中の例は `zroot/ROOT/default` です。スナップショットとクローンで作るため、短時間で、変更が増えるまでは小さい追加容量で保持できます。

`bectl(8)` で管理します。大きなOS・パッケージ更新前に作る例です。

```shell
# bectl create beforeupgrade
# bectl list
BE            Active Mountpoint Space Created
default       NR     /          2.43G 2026-07-11 11:26
beforeupgrade -      -          328K  2026-07-11 11:31
```

ActiveのNは現在使用中、Rは次回再起動で選ばれる環境です。通常どおりfreebsd-updateやpkgで更新すると、現在の環境が変わり、beforeupgradeには以前の状態が残ります。

更新後に問題があれば、loaderの **Boot Environments** メニューからbeforeupgradeを選んで起動します。メニューの選択はその一回だけです。以後も使うにはactivateします。

```shell
# bectl activate beforeupgrade
```

`bectl activate -t 環境名` は次回一度だけで、遠隔システムの変更試験にも使えます。起動せず内容を調べたり修復したりするなら、一時的にマウントできます。

```shell
# bectl mount beforeupgrade
/tmp/be_mount.c1Xk
# bectl umount beforeupgrade
```

不要な環境は削除できます。対象に残したい状態がないことを確認します。

```shell
# bectl destroy beforeupgrade
```

原文は大きな更新前の作成を勧めています。ただし、次節の共有データセットまで戻るわけではなく、全体のバックアップの代わりではありません。

<a id="zfs-be-applications"></a>
### ブート環境とアプリケーション

ブート環境の対象は `zroot/ROOT` 以下です。原文の標準配置では `/usr/local` と `/var/db` も含むため、インストールしたパッケージ本体と管理情報をOSと一緒に戻せます。

一方、その外の `zroot/home`、`zroot/var/log`、`zroot/var/mail` などは共有され、古い環境へ戻しても内容は戻りません。この違いを踏まえて配置します。たとえば、巻き戻し後も維持したいPostgreSQLのデータを別データセットにする例です。

```shell
# zfs create -o mountpoint=/var/db/postgres zroot/pgdata
```

この構成では、サーバの実行ファイルだけが古い版へ戻り、データベース内容は残ります。**古いソフトウェアと新しいデータ形式の互換性も必要です。** 新環境で共有側へ書いたファイルも残るため、ブート環境は共有データセット自身のスナップショットやバックアップを置き換えません。

<a id="zfs-advanced"></a>
## 高度な設定

以降は負荷や機器に合わせた調整を扱います。固定原文の既定値・例を、すべてのシステムに適する値として一律に適用せず、測定しながら変更します。

<a id="zfs-advanced-tuning"></a>
### チューニング

FreeBSDは `vfs.zfs` 以下のsysctlでZFSを調整し、`zfs(4)` が各項目を説明しています。起動時から必要なものは `/boot/loader.conf`、実行時に変更可能なものはsysctlで試し、継続するなら `/etc/sysctl.conf` に記載します。以下の既定値は固定原文に基づきます。

| 項目 | 意味と判断のポイント |
|---|---|
| `vfs.zfs.arc.max` | ARCの上限。0は搭載メモリから自動決定。他の大きな処理と共用するなら上限を抑える方法があります。[ARC](#zfs-advanced-arc)も参照。実行時変更可能。 |
| `vfs.zfs.arc.min` | ARCの下限。0は小さい値を自動選択。増やすと他処理のメモリ要求でARCが極端に縮むのを抑えますが、その分ほかへ渡せる容量が減ります。実行時変更可能。 |
| `vfs.zfs.arc.meta_balance` | メタデータとファイル内容のキャッシュ配分。100を超えるほどメタデータを優先し、原文の既定は500。大量ファイルの処理などに向く場合があります。OpenZFS 2.2で削除されたmeta_limitに代わる指定。実行時変更可能。 |
| `vfs.zfs.vdev.min_auto_ashift` | 作成・追加時に自動選択するashiftの下限。9は2の9乗＝512バイト。4KBセクタなら12を検討し、書き込み増幅を避けます。[作成時の説明](#zfs-zpool-create)を参照。値はセクタサイズそのものではなく指数です。 |
| `vfs.zfs.prefetch.disable` | 0で先読み有効、1で無効、既定0。ランダム読み取りが多い場合は不要な読み込みを減らすと改善する可能性があります。実行時変更可能。 |
| `vfs.zfs.txg.timeout` | TXGを同期する間隔の上限、既定5秒。データ量によって早く同期する場合もあります。長くすると非同期書き込みを遅らせられますが、同期時に負荷が偏る場合があります。実行時変更可能。 |
| `vfs.zfs.l2arc.write_max` | L2ARCへの毎秒の書き込み上限。SSDの追加書き込みを抑えるためにも使います。実行時変更可能。 |
| `vfs.zfs.l2arc.write_boost` | 最初のキャッシュ追い出しまでwrite_maxへ加える量。空のL2ARCを早く温めるための指定です。実行時変更可能。 |
| `vfs.zfs.l2arc.rebuild_enabled` | 既定1で、import時にキャッシュのログからL2ARCを再構成し、再起動後も活用します。0なら空から開始。 |
| `vfs.zfs.vdev.max_active` | デバイスごとの同時I/O数の上限。大きいと転送量、小さいと遅延に有利になる場合があります。実行時変更可能。 |
| `vfs.zfs.vdev.*_min_active`・`*_max_active` | sync_read、sync_write、async_read、async_write、scrubなど、I/Oクラスごとの並列数。古い遅延ベースのscrub・resilver抑制に代わるものです。scrub_max_activeを上げれば早く終わる反面、通常I/Oの遅延が増える場合があります。 |
| `vfs.zfs.resilver_min_time_ms` | TXGのフラッシュ間でresilver処理に使う最小時間。既定3000ms。増やすと再構築を早められる場合がありますが通常処理へ影響します。実行時変更可能。 |

<a id="zfs-advanced-arc"></a>
### ARCの容量と監視

ARCは、最近または頻繁に使うデータ・メタデータをRAMへ置きます。必要に応じてarc.maxまで増え、ほかの処理がメモリを必要とすると縮みます。専用ストレージサーバでRAMの多くを使うこと自体は異常ではありません。圧縮されたブロックをそのまま保持し、参照時に展開するため、同じメモリへ多くの内容を保存できます。

topのARC欄や、`kstat.zfs.misc.arcstats` でサイズ、上限、ヒット・ミスなどを調べられます。

```shell
% sysctl kstat.zfs.misc.arcstats.size kstat.zfs.misc.arcstats.c_max kstat.zfs.misc.arcstats.hits kstat.zfs.misc.arcstats.misses
kstat.zfs.misc.arcstats.size: 8963041280
kstat.zfs.misc.arcstats.c_max: 15843122176
kstat.zfs.misc.arcstats.hits: 954912441
kstat.zfs.misc.arcstats.misses: 21356847
```

`filesystems/zfs-stats` も読みやすい統計を提供します。データベース、仮想マシン、jailなどとRAMを共有する場合、奪い合いで性能が不安定になることがあります。上限を設けると、ほかの用途へ予測可能な余裕を残せます。8Gを上限にするloader.confの例です。

```text
vfs.zfs.arc.max="8G"
```

sysctlでも変更できますが、温まったARCの縮小・解放は徐々に進む場合があります。

<a id="zfs-advanced-zil-slog"></a>
### 同期書き込み・ZIL・SLOG

fsyncやO_SYNCで同期書き込みを求めたアプリケーションへは、ZFSが対応するインテントログを安定した媒体へ記録してから完了を返します。全プールにZILがあり、通常は主データのvdev上へ置きます。非同期書き込みはZILを経由せず、次のTXGで反映します。

専用ログvdev、SLOGを低遅延の機器へ置く例です。

```shell
# zpool add mypool log mirror nda0 nda1
```

効果があるのは、データベースやNFSなど同期書き込みが多い用途です。非同期処理だけなら改善しません。ZILが保持するのは、主領域への反映までの数秒、概ね一TXG相当で、原文は数GBで十分な場合が多いと説明しています。実際には書き込み速度と保持量を見積もります。

電源断保護と低い持続書き込み遅延を備える機器を選び、ミラーにします。クラッシュ後にZILから未反映の同期書き込みを再生するため、ミラーでないSLOGの故障と停止が重なると、完了通知済みの内容を失う危険があります。

`sync` プロパティは次の意味です。

- standard：既定。同期はZIL、非同期は次のTXGで反映。
- always：全書き込みを同期として扱います。必要な同期を要求しないアプリケーションを補える場合がありますが、性能負担があります。
- disabled：同期要求も非同期として扱います。

**sync=disabledでは、安定媒体への保存前に完了を返します。** プールの構造が整合していても、クラッシュ時にはアプリケーションやNFSクライアントが保存済みと信じたデータを失います。原文はデータベース・NFS・重要データに使わないよう警告しています。

`logbias=latency` は既定で、SLOGによる低遅延を優先します。throughputは主プールへの同期データ書き込みを優先し、SLOGを遅延に敏感な用途へ残す設定です。詳細は `zfsprops(7)` を参照してください。

<a id="zfs-advanced-directio"></a>
### Direct I/O

OpenZFS 2.3、FreeBSDでは15.0以降が対象です。`direct` プロパティはO_DIRECT要求を扱います。

- standard（既定）：適切に整列したO_DIRECTの読み書きはARCを迂回します。
- always：整列した読み書きを常にdirectとして扱います。
- disabled：O_DIRECTを無視し、ARC経由にします。

非常に高速なNVMeや、独自キャッシュを持つデータベースでは、ARCへのコピーと二重キャッシュの費用を省き、転送量・メモリ利用を改善できる場合があります。チェックサムの検証は維持します。

直接書き込みはrecordsizeに沿った整列が必要です。合わない部分はARC経由へ戻されるため、指定するだけで全I/Oが迂回するわけではありません。全条件は `zfsprops(7)` を確認します。

<a id="zfs-advanced-recordsize"></a>
### recordsizeとvolblocksize

recordsizeはファイルの最大ブロックサイズで、原文の既定は128KBです。I/Oの大きさに合わせると、必要以上の読み書きを避けやすくなります。

小さいランダムI/Oのデータベースでは、ファイルを作る前にページサイズ、たとえば8KB・16KBへ合わせる方法があります。一方、大きいメディアやバックアップの順次I/Oなら、1Mでメタデータ負担を減らし圧縮を改善できる場合があります。用途に応じて測定します。

zvolはvolblocksizeを使い、原文の既定は16KBで、作成後に変えられません。recordsizeの変更も既存ファイルには適用されず、**zfs rewriteでも論理ブロックサイズは変更しません。** 新しい値で保存するには、ファイルを新しくコピーし直す必要があります。

<a id="zfs-links"></a>
## 参考資料

[OpenZFS Documentation](https://openzfs.github.io/openzfs-docs/)には性能・調整の解説があります。[OpenZFS](https://openzfs.org/)のサイトも参照してください。カーネル調整は `zfs(4)`、vdevとプール構成は `zpoolconcepts(7)`、データセットのプロパティは `zfsprops(7)` が説明しています。

Portsには自動化ツールもあります。原文が挙げるものは次のとおりです。

- `filesystems/zrepl`：push・pull型の複製、スナップショット管理、転送再開を備えるデーモン。
- `sysutils/sanoid`：ポリシーに基づくスナップショット管理。同梱のsyncoidでSSH複製を扱います。
- `filesystems/zfstools`：OpenSolarisのauto-snapshotに似たローテーションをcronから実行。
- `filesystems/zap`：設定ファイルに代わりZFSプロパティで指定する、簡単なスナップショット保守と遠隔複製。

<a id="zfs-term"></a>
## ZFSの機能と用語


ZFSはファイルシステムとボリューム管理を一体化し、稼働中に加えた容量を同じプールのデータセットで共有します。固定パーティションごとに空きを分散して持つ制約を減らします。以下に本章の主要な用語をまとめます。

<a id="zfs-term-pool"></a>

**pool：ストレージプール**

一つ以上のvdevをまとめ、ファイルシステムとブロックボリュームへ容量を提供する、ZFSの基本単位です。名前とGUIDで識別し、各データセットが残り容量を共有します。現在のOpenZFSはプール形式5000を基に、個々の機能をfeature flagで管理します。`zpool-features(7)` と[アップグレード](#zfs-zpool-upgrade)を参照してください。

<a id="zfs-term-vdev"></a>

**vdev：仮想デバイスの種類**

単独ディスクや、ミラー・RAID-Zなどでまとめたディスク群です。トップレベルのデータvdev間へデータを分散し、性能と容量を利用します。原文は最小サイズを64MBとしています。以下の種類があります。

<a id="zfs-term-vdev-disk"></a>

**Disk**

ディスク全体（`/dev/ada0`）またはパーティション（`/dev/ada0p3`）のブロックデバイスです。原文はFreeBSDではパーティションを使うこと自体の性能上の不利はなく、Solarisの推奨と異なると説明しています。**起動用プールでは、ディスク全体を使う方式は強く非推奨です。** 原文はミラー・RAID-Zでもパーティションを使うよう注意し、起動時の容量判定や起動コードの置き場を理由にしています。起動方式に合う領域を確保します。

<a id="zfs-term-vdev-file"></a>

**File**

通常のファイルも構成要素にでき、試験・実験に便利です。zpool createへファイルの絶対パスを指定します。

<a id="zfs-term-vdev-mirror"></a>

**Mirror**

mirrorキーワードの後へ二台以上を並べ、同じデータを各メンバーへ書きます。容量は最小のメンバーに制約され、一台が正常なら残りが故障してもデータを維持できる構成です。[attach](#zfs-zpool-attach)で単独vdevからミラーへ変更できます。

<a id="zfs-term-vdev-raidz"></a>

**RAID-Z**

RAID-5系のパリティ構成をCOWなどと組み合わせ、予期しない再起動によるデータとパリティの不一致、いわゆるwrite holeを避けます。RAID-Z1・Z2・Z3の数字はパリティ段数で、耐えられる故障数と容量効率の交換になります。1TBを四台のZ1なら概算3TB・一台故障まで、八台のZ3なら概算5TB・三台故障までです。冗長性が回復する前に許容数を超えて故障すればプールを失います。実際の利用可能量にはメタデータなどの差し引きもあります。

原文の従来の推奨は一グループ最大九台程度で、さらに多い場合は複数vdevへ分けます。八台のZ2を二組にして分散する構成はRAID 60に似ています。容量の概算は最小ディスク容量×データ担当台数です。一台ずつの[拡張](#zfs-zpool-raidz-expansion)はOpenZFS 2.3・FreeBSD 15.0以降が対象です。

<a id="zfs-term-vdev-draid"></a>

**dRAID**

固定幅のストライプで、データ・パリティ・スペア容量を全メンバーへ分散するRAID-Zの変種です。故障時は残り全体へ順次再構築し、一台の専用スペアだけへ書くより早く冗長性を回復できます。表記は `draid[parity][:datad][:childrenc][:sparess]`。`zpoolconcepts(7)` と[dRAIDプール](#zfs-zpool-draid)を参照してください。

<a id="zfs-term-vdev-spare"></a>

**Spare**

利用可能な予備ディスクを追跡する擬似vdevです。FreeBSDではzfsdを有効にすれば故障時に自動適用し、そうでなければzpool replaceで手動指定します。[ホットスペア](#zfs-zpool-spares)を参照してください。

<a id="zfs-term-vdev-log"></a>

**Log・SLOG**

全プールにあるZILを、主領域から別のデバイスへ移すためのvdevです。SSDなどの低遅延な機器は、データベースのような同期書き込みを改善できる場合があります。ミラーは可能ですがRAID-Zは使えず、複数のログデバイスがあれば負荷を分散します。[ZILとSLOG](#zfs-advanced-zil-slog)を参照してください。

<a id="zfs-term-vdev-cache"></a>

**Cache**

二次読み取りキャッシュL2ARCを追加します。キャッシュのミラーは作れませんが、失っても主プールのデータを読み直せるため、キャッシュ自体の故障で元データを失う構造ではありません。

<a id="zfs-term-vdev-special"></a>

**Special・Dedup**

メタデータ、小さいデータブロック、重複排除表を高速な媒体へ分ける割り当てクラスです。小ブロックはspecial_small_blocksで指定します。**主データの唯一の保存先にもなるため、キャッシュと異なり喪失はプール全体へ影響します。** データvdevに見合う冗長性を用意します。[特殊クラス](#zfs-zpool-special)を参照してください。

<a id="zfs-term-txg"></a>

**Transaction Group（TXG）**

変更ブロックをまとめ、整合性を保つ原子的な単位としてプールへ書く仕組みです。各TXGは一意の連続する64ビット識別子を持ち、同時に最大三つ、各段階に一つずつ存在できます。

**Open**は新しい書き込みを受け付けます。量やタイムアウトの上限に達すると次へ進み、必要に応じて受け入れを抑制します。**Quiescing**は保留中の操作の完了を短時間待ち、その間に次のOpenを作れます。**Syncing**はデータ、メタデータ、空間管理情報などを安定媒体へ複数回に分けて書きます。割り当てが新しいメタデータを生むため、新たな領域を使わない段階まで進め、整合した状態として確定します。

スナップショット・データセットの作成や削除などのsynctaskもTXGへ入り、uberblockの更新に合わせて完了します。管理操作の待ち時間を減らすため、必要なTXGを早くSyncingへ進めます。一つが完了すると、待っているQuiescingがSyncingへ進みます。

<a id="zfs-term-arc"></a>

**Adaptive Replacement Cache（ARC）**

メモリ上のキャッシュです。単純なLRUは最近使った順に保持し、いっぱいになると古いものを外します。ARCは、最近使ったMRU、頻繁に使うMFUと、それぞれから追い出した項目の履歴を持つghost listを使います。最近性と頻度を併用するため、全体走査のような一度きりの読み込みで、普段よく使う内容が一掃されにくくなります。

原文はghost listを「再登録を防ぐ」ものと単純化していますが、実データを残す一覧ではなく、過去の追い出しと再参照を追跡してキャッシュ配分を適応させるための履歴です。

<a id="zfs-term-l2arc"></a>

**L2ARC**

RAMのARCを補う任意の二次読み取りキャッシュです。SSDなどをcache vdevへ使い、主ディスクより早い読み込みを狙えます。RAMに収まらないDDTも、L2ARCに収まるなら主ディスクだけより早く参照できる場合があります。

OpenZFS 2.0から永続化に対応し、再起動時はデバイスのヘッダ情報から内容を再構成できます。SSDへの追加書き込みを抑えるため、毎秒の上限をwrite_maxで制御し、最初の追い出し前はwrite_boostを加えて温めます。[調整](#zfs-advanced-tuning)を参照してください。

<a id="zfs-term-zil"></a>

**ZFS Intent Log（ZIL）**

クラッシュ後に同期書き込みを再生するためのディスク上のログです。全プールが持ち、通常は主領域の一部を使います。同期完了の保証が必要な要求は、ログの安定保存後に完了を返し、その後のTXGで主領域へ反映します。専用SLOGを高速な媒体へ置くと同期負荷の遅延を抑えられますが、通常の非同期書き込みを一律に速めるキャッシュではありません。[同期書き込み](#zfs-advanced-zil-slog)を参照してください。

<a id="zfs-term-cow"></a>

**Copy-On-Write（COW）**

古いブロックを直接上書きせず、新しい場所へ書き、完了後に参照を切り替えます。途中で電源断などがあっても、未完成の更新を採用せず、最後に確定した整合状態を利用できます。そのため予期しない停止の後も、通常はfsckによる全体検査を必要としません。これはアプリケーションの一連のファイル更新全体が必ず原子的になる、または未同期の書き込みがすべて残るという保証ではありません。

<a id="zfs-term-dataset"></a>

**Dataset**

ファイルシステム、ボリューム、スナップショット、クローンなどの総称です。ルートもデータセットで、mypool/home、その子mypool/home/userのように階層を作り、親からプロパティを継承します。子で個別設定して上書きでき、管理を[委譲](#zfs-zfs-allow)することもできます。スナップショット名はmypool/home@名前のように区切ります。

<a id="zfs-term-filesystem"></a>

**File system**

ディレクトリ階層の所定の場所へマウントするデータセットです。ファイル・ディレクトリ、アクセス権、フラグなどのメタデータを持ちます。

<a id="zfs-term-volume"></a>

**Volume（zvol）**

ディスクのようなブロックデバイスとして公開するデータセットです。COW、スナップショット、クローン、チェックサムなどを利用でき、UFSなど別形式のファイルシステム、仮想ディスク、iSCSIの領域にも使えます。

<a id="zfs-term-snapshot"></a>

**Snapshot**

COWを利用し、ある時点のデータセットを一貫した状態で短時間に保持します。再帰取得なら子も含めます。現在の内容を変更しても、スナップショットが参照する古いブロックを解放しないことで過去を残し、現在側だけが使わなくなったブロックの分だけ保持容量が増えます。読み取り専用の内容から個別ファイルを戻したり、[rollback](#zfs-zfs-snapshot-rollback)したりできます。

データセットやスナップショットなどから不要になったブロックは、参照がなくなると回収できます。原文は全ブロックが参照カウンタを持つ形で説明していますが、実装をその単純な一種類のカウンタだけで捉える必要はありません。[hold](#zfs-zfs-snapshot-hold)は削除をEBUSYで止め、releaseで解除します。zvolにも取得・クローン・巻き戻しは可能ですが、ファイルシステムと同じようにスナップショットをディレクトリへ直接マウントするわけではありません。

<a id="zfs-term-clone"></a>

**Clone**

スナップショットから分岐した書き込み可能なデータセットです。作成時は内容を共有し、変更したブロックから追加容量を使います。originに依存するため、そのスナップショットを削除できません。promoteで依存方向と所有関係を逆転できます。データを全複製する操作ではありませんが、親子の使用量計上が変わり、クォータや予約へ影響する場合があります。

<a id="zfs-term-bookmark"></a>

**Bookmark**

スナップショットの時点を、データを保持せず記録します。送信元のスナップショットを捨てても、受信側に対応するものがあれば増分sendの基点に使えます。既存スナップショットから作成します。[ブックマーク](#zfs-zfs-bookmark)を参照してください。

<a id="zfs-term-hold"></a>

**Hold**

スナップショットを削除できなくする名前付きタグです。すべてをreleaseするまで削除はEBUSYになります。複製などが依存する基点を守るために使います。[hold](#zfs-zfs-snapshot-hold)を参照してください。

<a id="zfs-term-checksum"></a>

**Checksum**

読み取り時にデータを検証し、潜在的な破損を検出する値です。方式はデータセット単位で指定します。異常があればミラー・RAID-Zなどの正常な冗長情報から復旧を試み、scrubで全体を検査できます。

原文の方式一覧はfletcher2、fletcher4、sha256、sha512、skein、edonr、blake3（FreeBSD 14.0以降）です。fletcher系は高速で、暗号学的ハッシュはより低い衝突確率と処理費用の交換になります。原文のonはfletcher4を選び、重複排除ではsha256などの暗号学的ハッシュを使います。チェックサムの無効化は強く非推奨です。

<a id="zfs-term-compression"></a>

**Compression**

データセットごとに透過的に圧縮します。原文ではOpenZFS 2.2以降、新規のcompression=onはLZ4を選びます。今後の書き込みが対象で、容量だけでなく、読む・書くブロック量を減らして速度が向上する場合もあります。以下が主な方式です。

<a id="zfs-term-compression-lz4"></a>

**LZ4**

feature flag形式で加わった汎用的で軽量な方式です。原文はLZJBに比べ、圧縮できるデータで約50%、できないデータで3倍超、展開で約80%速いという比較を挙げ、近年のCPUの一コアで圧縮500MB/s超・展開1.5GB/s超という例も示しています。これらはデータとCPUに依存する目安で、使用環境の性能保証ではありません。

<a id="zfs-term-compression-zstd"></a>

**ZSTD**

LZ4より高い圧縮率を狙い、fast系列からzstd-19まで、速度との交換を選べます。[Zstandard](#zfs-zfs-compression-zstd)を参照してください。

<a id="zfs-term-compression-lzjb"></a>

**LZJB**

ZFSの開発者の一人Jeff Bonwickによる旧来の方式です。gzipより軽い処理を狙いますが、既定としてはLZ4へ置き換わり、原文は新規にLZ4やZstdを選ぶよう勧めています。

<a id="zfs-term-compression-gzip"></a>

**GZIP**

圧縮レベル1〜9で、CPU処理と保存容量の交換を選べます。実際のcompressionプロパティの値の綴りはzfsprops(7)で確認してください。

<a id="zfs-term-compression-zle"></a>

**ZLE**

Zero Length Encodingは連続したゼロだけを圧縮する方式です。大量のゼロ領域を含むデータに向きます。

<a id="zfs-term-copies"></a>

**Copies**

1より大きくすると、ファイルシステムやzvolのブロックを追加保存します。チェックサム不一致の局所的な破損から回復する手掛かりになりますが、**ディスク全体の喪失を防ぐものではありません。** 単独デバイスでも追加コピーは作れますが、別ディスクへのミラーと同じ保護ではありません。

<a id="zfs-term-deduplication"></a>

**Deduplication**

書き込み時にチェックサムを照合し、同じ内容があれば新たなデータではなく既存ブロックを参照します。DDTには一意のチェックサム、保存位置、参照数などを記録します。dedup=onはハッシュの一致で同一と扱い、verifyは内容をバイト単位でも比較し、衝突なら別々に保存します。

表のメモリ費用は大きく、原文の概算は対象1TBにRAM5〜6GBです。RAMへ収まらず、毎回ディスク参照が必要になると大きく遅くなります。L2ARCも中間層として使えます。原文はまず圧縮を検討するよう勧めています。OpenZFS 2.3・FreeBSD 15.0以降のfast dedupは更新をログへまとめ、ddtpruneによる整理、dedup_table_quotaによる上限設定にも対応します。[重複排除](#zfs-zfs-deduplication)を参照してください。

<a id="zfs-term-block-cloning"></a>

**Block Cloning**

対応するcpとcopy_file_rangeを通じ、個別ファイルのコピーで既存ブロックを共有します。変更まで追加容量が小さく、短時間でコピーできます。原文ではFreeBSD 15.0で既定有効です。bcloneused・bclonesaved・bcloneratioで効果を表示します。[ブロッククローン](#zfs-zfs-block-cloning)を参照してください。

<a id="zfs-term-scrub"></a>

**Scrub**

プールの保存ブロックを読み、メタデータに記録されたチェックサムで検証します。普段は読まないアーカイブの潜在的な破損も検出し、正常な冗長データがあれば修復します。fsckと同じ起動後の必須検査ではありませんが、原文は月一回以上を目安としています。-pで一時停止し、通常のscrub指定で再開できます。[スクラブ](#zfs-zpool-scrub)を参照してください。

<a id="zfs-term-checkpoint"></a>

**Checkpoint**

データセットだけでなく、プール全体の構成を含む一時点を保存します。import --rewind-to-checkpointで戻すと、それ以後の変更を失います。一度に一つだけです。原文の用語説明はvdevの追加・削除まで戻せるようにも読めますが、**保持中に禁止される構成変更があります。** 先の[チェックポイント節](#zfs-zpool-checkpoint)と実際の操作条件を確認します。

<a id="zfs-term-trim"></a>

**TRIM**

不要なブロックをSSDなどへ通知し、機器が前もって消去して書き込み性能を維持する助けにします。zpool trimで手動実行するか、autotrimで継続実行できます。[TRIM](#zfs-zpool-trim)を参照してください。

<a id="zfs-term-quota"></a>

**Dataset Quota**

データセット、子、双方のスナップショットを含む使用量の上限です。ZFSはデータセット・ユーザー・グループ別に使用量を計上でき、予約と組み合わせて配分を管理します。ボリュームにはquotaを使わず、volsizeが暗黙の上限です。

<a id="zfs-term-refquota"></a>

**Reference Quota**

子とスナップショットを除き、データセット自身が参照する容量へ適用する上限です。

<a id="zfs-term-userquota"></a>

**User Quota**

指定ユーザーの使用容量を制限します。圧縮後の実使用量との関係にも注意します。

<a id="zfs-term-groupquota"></a>

**Group Quota**

指定グループの使用容量を制限します。

<a id="zfs-term-reservation"></a>

**Dataset Reservation**

特定データセットとその子のために容量を確保します。たとえば10Gを指定すると、ほかが全空きを使い切るのを防ぎます。スナップショットと子の使用量も予約に含めて計上します。新しいシステムの配分計画、記録・復旧用領域の確保などに使えます。

<a id="zfs-term-refreservation"></a>

**Reference Reservation**

子やスナップショットを除く、データセット自身のための予約です。10Gを指定した対象以外が空きを消費しても、その対象用の予約を維持します。スナップショットを取るには、予約外にも必要な空きがなければなりません。子の使用量はこの予約を使いません。

<a id="zfs-term-boot-environment"></a>

**Boot Environment**

bectlで管理する、OSデータセットの起動可能なクローンです。更新前に作れば、問題時にloaderから既知の正常環境を選べます。[ブート環境](#zfs-boot-environments)を参照してください。

<a id="zfs-term-resilver"></a>

**Resilver**

交換品や再接続デバイスへ必要なデータを再構築します。ミラーは残るコピーから、RAID-Zは残るデータとパリティから復元します。通常のRAIDの全セクタ再構築と異なり、割り当て済みデータが中心です。-sによるsequential resilverはミラー・dRAIDをディスク順で早く構築し、チェックサム検証を後の自動スクラブへ回します。[故障対応](#zfs-zpool-resilver)を参照してください。

<a id="zfs-term-online"></a>

**ONLINE**

プール・vdevの構成デバイスが接続され正常に機能する状態です。個別デバイスでも正常な動作を示します。

<a id="zfs-term-offline"></a>

**OFFLINE**

管理者が意図的に切り離した状態です。交換準備や識別などで利用しますが、残る冗長性が十分か確認し、プールを利用不能にしないようにします。

<a id="zfs-term-degraded"></a>

**DEGRADED**

故障・不在のメンバーがあるものの、残る冗長性でプールを利用できる状態です。追加故障で復旧不能になる危険があります。接続を戻すか交換し、resilverを終えると正常へ戻せます。

<a id="zfs-term-faulted"></a>

**FAULTED**

冗長性を超える不在・故障などで利用できない状態です。必要なデバイスを再接続して回復できる場合もありますが、十分なデータを戻せなければバックアップから復旧します。

<a id="zfs-term-unavail"></a>

**UNAVAIL**

デバイスが見つからない、アクセスできないなどで開けない状態です。冗長性が残れば縮退して継続できますが、必要なトップレベルvdev自体が利用できなければ、プール内容も使えません。

<a id="zfs-term-removed"></a>

**REMOVED**

稼働中に物理的に取り外された状態です。検出は機器・プラットフォーム依存で、非対応の場合もあります。zfsdは再接続したデバイスをオンラインへ戻し、戻らなければ利用可能なスペアを適用します。
