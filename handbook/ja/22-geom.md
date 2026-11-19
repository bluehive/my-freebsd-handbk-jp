<a id="geom"></a>
# 第22章 GEOM: モジュラーディスク変換フレームワーク（GEOM: Modular Disk Transformation Framework）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/geom/)の「Chapter 22. GEOM: Modular Disk Transformation Framework」（既存 TOC ID 21）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/geom/_index.adoc`）に基づいて日本語へ意訳したものです。（※作業中ドラフト）

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` は一般ユーザーのプロンプトを示します。

<a id="geom-synopsis"></a>
## 概要

FreeBSD の GEOM フレームワークは、プロバイダ（`/dev` 配下のディスクデバイス）を通じて、マスターブートレコード（MBR）や BSD ラベルなどのクラスへのアクセスと制御を可能にします。GEOM はさまざまなソフトウェア RAID 構成に対応しており、OS やシステムユーティリティに対して透過的なアクセスを提供します。

本章では、FreeBSD の GEOM フレームワーク配下でディスクを扱う方法を説明します。対象には、構成管理にこのフレームワークを利用する主要な RAID 制御ユーティリティも含まれます。本章は RAID 構成全般の網羅的な解説ではなく、GEOM が対応している RAID の分類のみを扱います。

本章を読むと、次の内容を学べます。

* GEOM を通じて利用できる RAID の種類
* ベースユーティリティを使って各種 RAID レベルを構成・保守・操作する方法
* GEOM を通じてディスクデバイスのミラーリング、ストライピング、暗号化、リモート接続を行う方法
* GEOM フレームワークに接続されたディスクのトラブルシューティング方法

本章を読む前に、次の内容を理解しておいてください。

* FreeBSD がディスクデバイスをどのように扱うか（[Storage](21-disks.md#disks)）
* 新しいカーネルを設定してインストールする方法（[FreeBSD カーネルの設定](09-kernelconfig.md#kernelconfig)）

<a id="geom-striping"></a>
## RAID0 - ストライピング

ストライピングは、複数のディスクドライブを 1 つのボリュームにまとめる手法です。ハードウェア RAID コントローラを使って実行することもできますが、GEOM ディスクサブシステムは、RAID ディスクコントローラを使わずに RAID0 とも呼ばれるディスクストライピングをソフトウェアでサポートしています。

RAID0 では、データをブロックに分割してアレイ内のすべてのドライブへ分散して書き込みます。次の図のように、1 台のディスクに 256k を書き込むのを待つ代わりに、アレイ内の 4 台のディスクそれぞれへ 64k ずつ同時に書き込めるため、優れた I/O 性能が得られます。複数のディスクコントローラを併用すると、この性能をさらに引き上げることができます。

![ディスクストライピングの図解](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/geom/striping.png)

RAID0 ストライプでは、I/O リクエストをインターリーブして複数ディスクへ並列に読み書きするため、すべてのディスクが同じサイズでなければなりません。

> **注**: RAID0 には**冗長性がありません**。つまり、アレイ内のディスクが 1 台でも故障すると、ディスク上のデータはすべて失われます。重要なデータを扱う場合は、リモートのシステムやデバイスへ定期的にバックアップを保存する運用を用意してください。

汎用ディスクを使い、FreeBSD システム上に GEOM ベースのソフトウェア RAID0 を作成する手順は次のとおりです。ストライプの作成後、既存のストライプを操作する方法の詳細は `gstripe(8)` を参照してください。

**手順: 未フォーマットの ATA ディスクでストライプを作成する**

1. `geom_stripe.ko` モジュールを読み込みます。

```shell
# kldload geom_stripe
```

2. 適切なマウントポイントがあることを確認します。このボリュームをルートパーティションにする場合は、一時的に `/mnt` などの別のマウントポイントを使います。
3. ストライプ化するディスクのデバイス名を確認し、新しいストライプデバイスを作成します。たとえば、未使用かつ未パーティションの 2 台の ATA ディスク `/dev/ad2` と `/dev/ad3` をストライプ化する場合は次のようにします。

> **訳注**: 例中の `/dev/ad2`・`/dev/ad3` は旧来の ATA ドライバに基づくデバイス名です。近年の FreeBSD（CAM ベースの ATA ドライバ）では `ada2` のように `adaX` として認識されますが、コマンド例は固定原文のまま保持しています。

```shell
# gstripe label -v st0 /dev/ad2 /dev/ad3
Metadata value stored on /dev/ad2.
Metadata value stored on /dev/ad3.
Done.
```

4. 新しいボリュームに標準ラベル（パーティションテーブル）を書き込み、デフォルトのブートストラップコードをインストールします。

```shell
# bsdlabel -wB /dev/stripe/st0
```

5. この処理により、`/dev/stripe` 内に `st0` に加えて `st0a` と `st0c` の 2 つのデバイスが作成されます。この段階で、`newfs` を使って `st0a` 上に UFS ファイルシステムを作成できます。

```shell
# newfs -U /dev/stripe/st0a
```

   画面に多くの数値が流れたあと、数秒で処理が完了します。これでボリュームが作成され、マウントできる状態になります。

6. 作成したディスクストライプを手動でマウントするには次のようにします。

```shell
# mount /dev/stripe/st0a /mnt
```

7. 起動時にこのストライプファイルシステムを自動マウントするには、`/etc/fstab` にボリューム情報を記述します。次の例では、`stripe` という名前の恒久的なマウントポイントを作成しています。

```shell
# mkdir /stripe
# echo "/dev/stripe/st0a /stripe ufs rw 2 2" \
>> /etc/fstab
```

8. システム初期化時に `geom_stripe.ko` モジュールを自動読み込みするため、`/boot/loader.conf` に次の行を追加します。

```shell
# echo 'geom_stripe_load="YES"' >> /boot/loader.conf
```

<a id="geom-mirror"></a>
## RAID1 - ミラーリング

RAID1（*ミラーリング*）は、同じデータを複数のディスクドライブに書き込む手法です。ミラーは通常、ドライブの故障によるデータ損失を防ぐために使われます。ミラー内の各ドライブにはまったく同じデータのコピーが保持されます。個々のドライブが故障してもミラーは動作を続け、正常に機能している残りのドライブからデータを提供します。コンピュータは稼働し続けるため、管理者はユーザーへのサービスを中断せずに故障したドライブを交換する時間を確保できます。

以下の例では、よくある 2 つの状況を取り上げます。1 つ目は、2 台の新しいドライブからミラーを作成し、既存の単一ドライブの置き換えとして使う方法です。2 つ目は、1 台の新しいドライブ上にミラーを作成して古いドライブのデータをコピーし、そのあとで古いドライブをミラーに組み込む方法です。後者の手順はやや複雑ですが、新しいドライブが 1 台だけで済みます。

従来、ミラー内の 2 台のドライブには同一のモデルと容量のものを使うのが一般的ですが、`gmirror(8)` では必須ではありません。容量の異なるドライブでミラーを作成した場合、ミラーの容量はミラー内で最小のドライブの容量と同じになります。大きいドライブの余剰領域は使われません。また、あとからミラーに組み込むドライブは、すでにミラー内にある最小のドライブ以上の容量が必要です。

> **警告**: ここで紹介するミラーリング手順は非破壊的ですが、重要なディスク操作を行う場合と同様に、まずフルバックアップを取得してください。

> **警告**: これらの手順ではファイルシステムのコピーに `dump(8)` を使用していますが、ソフトアップデートジャーナリング（soft updates journaling）が有効なファイルシステムでは動作しません。ソフトアップデートジャーナリングの確認方法と無効化については `tunefs(8)` を参照してください。

<a id="geom-mirror-metadata"></a>
### メタデータの問題

多くのディスクシステムは、各ディスクの末尾にメタデータを保存します。ミラー用にディスクを再利用する前に、古いメタデータを消去しておくべきです。問題の大半は、特に 2 種類の残留メタデータ、すなわち GPT パーティションテーブルと以前のミラーの古いメタデータによって引き起こされます。

GPT のメタデータは `gpart(8)` で消去できます。次の例では、ディスク `ada8` からプライマリとバックアップの両方の GPT パーティションテーブルを消去します。

```shell
# gpart destroy -F ada8
```

`gmirror(8)` を使えば、稼働中のミラーからディスクを切り離し、メタデータを消去する操作を 1 ステップで行えます。次の例では、稼働中のミラー `gm4` からディスク `ada8` を削除しています。

```shell
# gmirror remove gm4 ada8
```

ミラーが動作していない状態で古いミラーのメタデータがディスクに残っている場合は、`gmirror clear` を使って削除します。

```shell
# gmirror clear ada8
```

`gmirror(8)` はディスク末尾に 1 ブロックのメタデータを保存します。GPT パーティション方式もディスク末尾にメタデータを保存するため、GPT ディスク全体を `gmirror(8)` でミラーリングすることは推奨されません。ここでは、ディスク先頭にのみパーティションテーブルを保存し、ミラーメタデータと競合しない MBR パーティション方式を使用します。

<a id="geom-mirror-two-new-disks"></a>
### 2 台の新しいディスクでミラーを作成する

この例では、単一のディスク `ada0` にすでに FreeBSD がインストールされており、2 台の新しいディスク `ada1` と `ada2` がシステムに接続されているものとします。これら 2 台のディスク上に新しいミラーを作成し、古い単一ディスクの置き換えとして使用します。

`geom_mirror.ko` カーネルモジュールは、カーネルに組み込むか、起動時または実行時に読み込む必要があります。ここではまず手動でカーネルモジュールを読み込みます。

```shell
# gmirror load
```

2 台の新しいドライブでミラーを作成します。

```shell
# gmirror label -v gm0 /dev/ada1 /dev/ada2
```

`gm0` は、新しいミラーに割り当てた任意のデバイス名です。ミラーが開始されると、このデバイス名は `/dev/mirror/` 配下に現れます。

これで、`gpart(8)` を使ってミラー上に MBR と bsdlabel のパーティションテーブルを作成できるようになります。この例では、`/`、スワップ、`/var`、`/tmp`、`/usr` のパーティションを分ける伝統的なファイルシステム構成を使います。`/` とスワップだけの単一構成でも動作します。

ミラー上のパーティションは既存ディスクのものと同じサイズである必要はありませんが、`ada0` 上にすでにあるすべてのデータを収容できる大きさでなければなりません。

```shell
# gpart create -s MBR mirror/gm0
# gpart add -t freebsd -a 4k mirror/gm0
# gpart show mirror/gm0
=>       63  156301423  mirror/gm0  MBR  (74G)
         63         63                    - free -  (31k)
        126  156301299                 1  freebsd  (74G)
  156301425         61                    - free -  (30k)
```

```shell
# gpart create -s BSD mirror/gm0s1
# gpart add -t freebsd-ufs  -a 4k -s 2g mirror/gm0s1
# gpart add -t freebsd-swap -a 4k -s 4g mirror/gm0s1
# gpart add -t freebsd-ufs  -a 4k -s 2g mirror/gm0s1
# gpart add -t freebsd-ufs  -a 4k -s 1g mirror/gm0s1
# gpart add -t freebsd-ufs  -a 4k mirror/gm0s1
# gpart show mirror/gm0s1
=>        0  156301299  mirror/gm0s1  BSD  (74G)
          0          2                      - free -  (1.0k)
          2    4194304                   1  freebsd-ufs  (2.0G)
    4194306    8388608                   2  freebsd-swap (4.0G)
   12582914    4194304                   4  freebsd-ufs  (2.0G)
   16777218    2097152                   5  freebsd-ufs  (1.0G)
   18874370  137426928                   6  freebsd-ufs  (65G)
  156301298          1                      - free -  (512B)
```

MBR と bsdlabel にブートコードをインストールし、アクティブスライスを設定して、ミラーから起動できるようにします。

```shell
# gpart bootcode -b /boot/mbr mirror/gm0
# gpart set -a active -i 1 mirror/gm0
# gpart bootcode -b /boot/boot mirror/gm0s1
```

ソフトアップデートを有効にして、新しいミラー上のファイルシステムをフォーマットします。

```shell
# newfs -U /dev/mirror/gm0s1a
# newfs -U /dev/mirror/gm0s1d
# newfs -U /dev/mirror/gm0s1e
# newfs -U /dev/mirror/gm0s1f
```

これで、`dump(8)` と `restore(8)` を使って元の `ada0` ディスクからミラーへファイルシステムをコピーできます。

```shell
# mount /dev/mirror/gm0s1a /mnt
# dump -C16 -b64 -0aL -f - / | (cd /mnt && restore -rf -)
# mount /dev/mirror/gm0s1d /mnt/var
# mount /dev/mirror/gm0s1e /mnt/tmp
# mount /dev/mirror/gm0s1f /mnt/usr
# dump -C16 -b64 -0aL -f - /var | (cd /mnt/var && restore -rf -)
# dump -C16 -b64 -0aL -f - /tmp | (cd /mnt/tmp && restore -rf -)
# dump -C16 -b64 -0aL -f - /usr | (cd /mnt/usr && restore -rf -)
```

`/mnt/etc/fstab` を編集して、新しいミラーのファイルシステムを指すようにします。

```
# Device		Mountpoint	FStype	Options	Dump	Pass#
/dev/mirror/gm0s1a	/		ufs	rw	1	1
/dev/mirror/gm0s1b	none		swap	sw	0	0
/dev/mirror/gm0s1d	/var		ufs	rw	2	2
/dev/mirror/gm0s1e	/tmp		ufs	rw	2	2
/dev/mirror/gm0s1f	/usr		ufs	rw	2	2
```

`geom_mirror.ko` カーネルモジュールがカーネルに組み込まれていない場合は、起動時に読み込むよう `/mnt/boot/loader.conf` を編集します。

```
geom_mirror_load="YES"
```

システムを再起動して新しいミラーをテストし、すべてのデータがコピーされていることを確認します。BIOS からはミラーが 2 台の独立したドライブとして見えます。ドライブの内容は同一であるため、どちらを起動元に選んでも構いません。

起動時に問題が起きた場合は、[トラブルシューティング](#gmirror-troubleshooting)を参照してください。電源を切って元の `ada0` ディスクを取り外しておけば、オフラインバックアップとして保管できます。

運用中、このミラーは元の単一ドライブとまったく同じように振る舞います。

<a id="geom-mirror-existing-drive"></a>
### 既存のドライブを使ってミラーを作成する

この例では、単一のディスク `ada0` にすでに FreeBSD がインストールされており、新しいディスク `ada1` がシステムに接続されているものとします。新しいディスク上に 1 台構成のミラーを作成して既存システムをそこへコピーし、そのあとで古いディスクをミラーに組み込みます。`gmirror` は各ディスクの末尾に 512 バイトのメタデータブロックを置く必要があり、既存の `ada0` は通常すべての領域がすでに割り当て済みであるため、このようなやや複雑な手順が必要になります。

`geom_mirror.ko` カーネルモジュールを読み込みます。

```shell
# gmirror load
```

`diskinfo` で元のディスクのメディアサイズを確認します。

```shell
# diskinfo -v ada0 | head -n3
/dev/ada0
        512             # sectorsize
        1000204821504   # mediasize in bytes (931G)
```

新しいディスク上にミラーを作成します。ミラーの容量が元の `ada0` ドライブより大きくならないようにするため、`gnop(8)` を使って同じサイズの仮想ドライブを作成します。このドライブはデータを保存するものではなく、ミラーのサイズを制限する目的でのみ使います。`gmirror(8)` でミラーを作成すると、たとえ新しい `ada1` ドライブの容量が大きくても、容量は `gzero.nop` のサイズに制限されます。2 行目の `1000204821504` は、上の `diskinfo` が示した `ada0` のメディアサイズと一致している点に注意してください。

```shell
# geom zero load
# gnop create -s 1000204821504 gzero
# gmirror label -v gm0 gzero.nop ada1
# gmirror forget gm0
```

`gzero.nop` はデータを保存しないため、ミラーからは接続されていないと認識されます。接続されていないコンポーネントを「忘れる（forget）」よう指示することで、`gzero.nop` への参照が取り除かれます。その結果、単一のディスク `ada1` のみを含むミラーデバイスができあがります。

`gm0` を作成したあと、`ada0` のパーティションテーブルを確認します。次の出力は 1 TB ドライブの例です。ドライブの末尾に未割り当て領域が少し残っている場合は、`ada0` から新しいミラーへ内容をそのままコピーできます。

しかし、次の出力のようにディスク上のすべての領域が割り当てられている場合は、ディスク末尾に 512 バイトのミラーメタデータを置く空きがありません。

```shell
# gpart show ada0
=>        63  1953525105        ada0  MBR  (931G)
          63  1953525105           1  freebsd  [active]  (931G)
```

この場合は、パーティションテーブルを編集して `mirror/gm0` 上の容量を 1 セクタ分減らす必要があります。手順は後述します。

いずれの場合も、まず `gpart backup` と `gpart restore` を使ってプライマリディスクのパーティションテーブルをコピーします。

```shell
# gpart backup ada0 > table.ada0
# gpart backup ada0s1 > table.ada0s1
```

これらのコマンドにより、`table.ada0` と `table.ada0s1` の 2 つのファイルが作成されます。次の例は 1 TB ドライブのものです。

```shell
# cat table.ada0
MBR 4
1 freebsd         63 1953525105   [active]
```

```shell
# cat table.ada0s1
BSD 8
1  freebsd-ufs          0    4194304
2 freebsd-swap    4194304   33554432
4  freebsd-ufs   37748736   50331648
5  freebsd-ufs   88080384   41943040
6  freebsd-ufs  130023424  838860800
7  freebsd-ufs  968884224  984640881
```

ディスク末尾に空き領域がない場合は、スライスと最後のパーティションの両方のサイズを 1 セクタ減らす必要があります。2 つのファイルを編集し、スライスと最後のパーティションのサイズをそれぞれ 1 だけ小さくします。これは各一覧の末尾にある数値です。

```shell
# cat table.ada0
MBR 4
1 freebsd         63 1953525104   [active]
```

```shell
# cat table.ada0s1
BSD 8
1  freebsd-ufs          0    4194304
2 freebsd-swap    4194304   33554432
4  freebsd-ufs   37748736   50331648
5  freebsd-ufs   88080384   41943040
6  freebsd-ufs  130023424  838860800
7  freebsd-ufs  968884224  984640880
```

ディスク末尾に少なくとも 1 セクタの未割り当て領域があった場合は、これら 2 つのファイルを変更せずにそのまま使えます。

次に、パーティションテーブルを `mirror/gm0` へ復元します。

```shell
# gpart restore mirror/gm0 < table.ada0
# gpart restore mirror/gm0s1 < table.ada0s1
```

`gpart show` でパーティションテーブルを確認します。この例では、`/` に `gm0s1a`、`/var` に `gm0s1d`、`/usr` に `gm0s1e`、`/data1` に `gm0s1f`、`/data2` に `gm0s1g` が割り当てられています。

```shell
# gpart show mirror/gm0
=>        63  1953525104  mirror/gm0  MBR  (931G)
          63  1953525042           1  freebsd  [active]  (931G)
  1953525105          62              - free -  (31k)

# gpart show mirror/gm0s1
=>         0  1953525042  mirror/gm0s1  BSD  (931G)
           0     2097152             1  freebsd-ufs  (1.0G)
     2097152    16777216             2  freebsd-swap  (8.0G)
    18874368    41943040             4  freebsd-ufs  (20G)
    60817408    20971520             5  freebsd-ufs  (10G)
    81788928   629145600             6  freebsd-ufs  (300G)
   710934528  1242590514             7  freebsd-ufs  (592G)
  1953525042          63                - free -  (31k)
```

スライスと最後のパーティションの両方で、ディスク末尾に少なくとも 1 ブロックの空きがなければなりません。

これらの新しいパーティション上にファイルシステムを作成します。パーティションの数は元のディスク `ada0` に合わせて変わります。

```shell
# newfs -U /dev/mirror/gm0s1a
# newfs -U /dev/mirror/gm0s1d
# newfs -U /dev/mirror/gm0s1e
# newfs -U /dev/mirror/gm0s1f
# newfs -U /dev/mirror/gm0s1g
```

MBR と bsdlabel にブートコードをインストールし、アクティブスライスを設定して、ミラーから起動できるようにします。

```shell
# gpart bootcode -b /boot/mbr mirror/gm0
# gpart set -a active -i 1 mirror/gm0
# gpart bootcode -b /boot/boot mirror/gm0s1
```

ミラー上の新しいパーティションを使うように `/etc/fstab` を調整します。まず `/etc/fstab.orig` にコピーしてバックアップを取ります。

```shell
# cp /etc/fstab /etc/fstab.orig
```

`/etc/fstab` を編集し、`/dev/ada0` を `mirror/gm0` に置き換えます。

```
# Device		Mountpoint	FStype	Options	Dump	Pass#
/dev/mirror/gm0s1a	/		ufs	rw	1	1
/dev/mirror/gm0s1b	none		swap	sw	0	0
/dev/mirror/gm0s1d	/var		ufs	rw	2	2
/dev/mirror/gm0s1e	/usr		ufs	rw	2	2
/dev/mirror/gm0s1f	/data1		ufs	rw	2	2
/dev/mirror/gm0s1g	/data2		ufs	rw	2	2
```

`geom_mirror.ko` カーネルモジュールがカーネルに組み込まれていない場合は、起動時に読み込むよう `/boot/loader.conf` を編集します。

```
geom_mirror_load="YES"
```

これで、`dump(8)` と `restore(8)` を使って元のディスクからミラーへファイルシステムをコピーできます。`dump -L` でダンプされる各ファイルシステムでは最初にスナップショットが作成されるため、少し時間がかかる場合があります。

```shell
# mount /dev/mirror/gm0s1a /mnt
# dump -C16 -b64 -0aL -f - /    | (cd /mnt && restore -rf -)
# mount /dev/mirror/gm0s1d /mnt/var
# mount /dev/mirror/gm0s1e /mnt/usr
# mount /dev/mirror/gm0s1f /mnt/data1
# mount /dev/mirror/gm0s1g /mnt/data2
# dump -C16 -b64 -0aL -f - /usr | (cd /mnt/usr && restore -rf -)
# dump -C16 -b64 -0aL -f - /var | (cd /mnt/var && restore -rf -)
# dump -C16 -b64 -0aL -f - /data1 | (cd /mnt/data1 && restore -rf -)
# dump -C16 -b64 -0aL -f - /data2 | (cd /mnt/data2 && restore -rf -)
```

システムを再起動し、`ada1` から起動します。すべて正常に動作していれば、以前は `ada0` 上にあったのと同じデータを含む `mirror/gm0` からシステムが起動します。起動時に問題が起きた場合は、[トラブルシューティング](#gmirror-troubleshooting)を参照してください。

この時点では、ミラーはまだ単一の `ada1` ディスクだけで構成されています。

`mirror/gm0` から問題なく起動できたら、最後の手順として `ada0` をミラーに組み込みます。

> **重要**: `ada0` をミラーに組み込むと、以前の内容はミラーからのデータで上書きされます。`ada0` をミラーに追加する前に、`mirror/gm0` の内容が `ada0` と同じであることを必ず確認してください。事前に `dump(8)` と `restore(8)` でコピーした内容が `ada0` の内容と一致しない場合は、`/etc/fstab` を元に戻して `ada0` 上のファイルシステムをマウントするようにし、再起動して手順全体をはじめからやり直してください。

```shell
# gmirror insert gm0 ada0
GEOM_MIRROR: Device gm0: rebuilding provider ada0
```

2 台のディスク間の同期がただちに始まります。進捗は `gmirror status` で確認できます。

```shell
# gmirror status
      Name    Status  Components
mirror/gm0  DEGRADED  ada1 (ACTIVE)
                      ada0 (SYNCHRONIZING, 64%)
```

しばらくすると同期が完了します。

```shell
GEOM_MIRROR: Device gm0: rebuilding provider ada0 finished.
# gmirror status
      Name    Status  Components
mirror/gm0  COMPLETE  ada1 (ACTIVE)
                      ada0 (ACTIVE)
```

これで `mirror/gm0` は `ada0` と `ada1` の 2 台のディスクで構成され、内容は自動的に相互同期されます。運用上、`mirror/gm0` は元の単一ドライブとまったく同じように振る舞います。

<a id="gmirror-troubleshooting"></a>
### トラブルシューティング

システムが起動しなくなった場合は、新しいミラー構成ドライブのいずれかから起動するよう BIOS 設定の変更が必要になることがあります。どちらのミラードライブも同一のデータを含んでいるため、起動にはどちらを使っても構いません。

起動が次のメッセージで停止する場合は、ミラーデバイスに何らかの問題があります。

```shell
Mounting from ufs:/dev/mirror/gm0s1a failed with error 19.

Loader variables:
  vfs.root.mountfrom=ufs:/dev/mirror/gm0s1a
  vfs.root.mountfrom.options=rw

Manual root filesystem specification:
  <fstype>:<device> [options]
      Mount <device> using filesystem <fstype>
      and with the specified (optional) option list.

    e.g. ufs:/dev/da0s1a
        zfs:tank
        cd9660:/dev/acd0 ro
          (which is equivalent to: mount -t cd9660 -o ro /dev/acd0 /)

  ?               List valid disk boot devices
  .               Yield 1 second (for background tasks)
  <empty line>    Abort manual input

mountroot>
```

`/boot/loader.conf` で `geom_mirror.ko` モジュールを読み込み忘れると、この問題が起きます。修復するには、FreeBSD のインストールメディアから起動し、最初のプロンプトで `Shell` を選びます。次に、ミラーモジュールを読み込んでミラーデバイスをマウントします。

```shell
# gmirror load
# mount /dev/mirror/gm0s1a /mnt
```

`/mnt/boot/loader.conf` を編集し、ミラーモジュールを読み込む行を追加します。

```
geom_mirror_load="YES"
```

ファイルを保存して再起動します。

`error 19` を引き起こすその他の原因は、修復にもう少し手間がかかります。システムは `ada0` から起動できるはずですが、`/etc/fstab` が誤っている場合はシェルを選択するプロンプトが再度表示されます。ブートローダのプロンプトで `ufs:/dev/ada0s1a` と入力して `Enter` キーを押してください。`/etc/fstab` への編集を元に戻し、ミラーではなく元のディスク（`ada0`）からファイルシステムをマウントするようにします。システムを再起動し、手順をやり直してください。

```shell
Enter full pathname of shell or RETURN for /bin/sh:
# cp /etc/fstab.orig /etc/fstab
# shutdown -r now
```

<a id="chapter-22-heading-09"></a>
### ディスク故障からの復旧

ディスクミラーリングの利点は、個々のディスクが故障してもミラーのデータが失われない点にあります。上記の例では、`ada0` が故障してもミラーは動作を続け、正常に残っているドライブ `ada1` からデータを提供します。

故障したドライブを交換するには、システムをシャットダウンし、故障したドライブを同等以上の容量の新しいドライブへ物理的に交換します。メーカーがギガバイト単位でドライブ容量を表記する際の値はやや曖昧なため、確実に確認する唯一の方法は、`diskinfo -v` が表示する総セクタ数を比較することです。ミラーより大きい容量のドライブも使用できますが、新しいドライブの余剰領域は使われません。

コンピュータの電源を入れ直すと、ミラーは 1 台のドライブだけで「縮退（degraded）」モードで動作します。現在接続されていないドライブをミラーに忘れさせます。

```shell
# gmirror forget gm0
```

交換用ディスクから古いメタデータを消去するには、[メタデータの問題](#geom-mirror-metadata)の手順に従います。続いて、交換用ディスク（この例では `ada4`）をミラーに組み込みます。

```shell
# gmirror insert gm0 /dev/ada4
```

新しいドライブをミラーに組み込むと再同期が始まります。ミラーデータを新しいドライブへコピーするこの処理には時間がかかる場合があります。コピー中はミラーの性能が大幅に低下するため、新しいドライブの組み込みはコンピュータへの負荷が低い時間帯に行うのが最善です。

進捗状況は `gmirror status` で監視でき、同期中のドライブと完了率（パーセンテージ）が表示されます。再同期中のステータスは `DEGRADED` となり、処理が完了すると `COMPLETE` に変わります。
