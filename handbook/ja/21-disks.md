<a id="disks"></a>
# 第21章 ストレージ（Storage）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/disks/)の「Chapter 21. Storage」（既存 TOC ID 20）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/disks/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` は一般ユーザーのプロンプトを示します。

<a id="disks-synopsis"></a>
## 概要

本章では、FreeBSD でディスクや記憶媒体を扱う方法を説明します。対象には SCSI および IDE ディスク、CD／DVD メディア、メモリをバックエンドとするディスク（メモリディスク）、USB ストレージデバイスが含まれます。

本章を読むと、次の内容を学べます。

* FreeBSD システムにハードディスクを追加する方法
* FreeBSD 上でディスクパーティションのサイズを拡張する方法
* USB ストレージデバイスを使えるように FreeBSD を設定する方法
* FreeBSD システムで CD や DVD メディアを使う方法
* FreeBSD で利用できるバックアッププログラムの使い方
* メモリディスクの設定方法
* ファイルシステムスナップショットとは何か、および効率的な使い方
* クォータを使ってディスク容量の使用量を制限する方法
* 攻撃者から保護するためにディスクやスワップを暗号化する方法
* 高可用性ストレージネットワーク（HAST）を構成する方法

本章を読む前に、次の内容を理解しておいてください。

* [新しい FreeBSD カーネルを設定してインストールする方法](09-kernelconfig.md#kernelconfig)

<a id="disks-adding"></a>
## ディスクの追加

この節では、現在ドライブを 1 台だけ搭載しているマシンに、新しい SATA ディスクを追加する手順を説明します。はじめにコンピュータの電源を切り、コンピュータ本体・コントローラ・ドライブ各メーカーの指示に従ってドライブを取り付けます。その後、システムを再起動して `root` になります。

新しいディスクが認識されているかを確認するため、`/var/run/dmesg.boot` を調べます。この例では、新しく追加した SATA ドライブが `ada1` として認識されているものとします。

ここでは、新しいディスク全体に 1 つの大きなパーティションを作成します。パーティション方式には、古く機能面で制約のある MBR 方式ではなく、[GPT](https://en.wikipedia.org/wiki/GUID_Partition_Table) 方式を使います。

> **注**: 追加するディスクが空でない場合は、`gpart delete` で古いパーティション情報を削除できます。詳細は `gpart(8)` を参照してください。

パーティション方式を作成し、その上に 1 つのパーティションを追加します。ハードウェアブロックサイズが大きい新しいディスクで性能を向上させるため、パーティションの境界は 1 メガバイト単位にアラインメントします。

```shell
# gpart create -s GPT ada1
# gpart add -t freebsd-ufs -a 1M ada1
```

用途によっては、複数の小さなパーティションに分けたい場合もあります。ディスク全体より小さいパーティションを作成するオプションについては `gpart(8)` を参照してください。

ディスクのパーティション情報は `gpart show` で確認できます。

```shell
% gpart show ada1
=>        34  1465146988  ada1  GPT  (699G)
          34        2014        - free -  (1.0M)
        2048  1465143296     1  freebsd-ufs  (699G)
  1465145344        1678        - free -  (839K)
```

新しいディスク上のパーティションにファイルシステムを作成します。

```shell
# newfs -U /dev/ada1p1
```

元のディスクのファイルシステム上で新しいディスクをマウントする場所（*マウントポイント*）として、空のディレクトリを作成します。

```shell
# mkdir /newdisk
```

最後に、起動時に新しいディスクが自動的にマウントされるよう、`/etc/fstab` にエントリを追加します。

```
/dev/ada1p1	/newdisk	ufs	rw	2	2
```

システムを再起動せずに、手動で新しいディスクをマウントすることもできます。

```shell
# mount /newdisk
```

<a id="disks-growing"></a>
## ディスクのサイズ変更と拡張

ディスクに既存のデータを変更しないまま、容量だけを増やせる場合があります。仮想マシンで仮想ディスクが小さすぎると分かり、後から拡張するときによく起きる状況です。また、USB メモリにディスクイメージを書き込んだものの、容量全体を使い切っていない場合も同様です。ここでは、増えた容量を活用するためにディスク上の領域をサイズ変更、つまり *拡張（grow）* する手順を説明します。

まず `/var/run/dmesg.boot` を調べて、サイズ変更するディスクのデバイス名を確認します。この例では、システムに SATA ディスクが 1 台だけあるため、ドライブは `ada0` として認識されています。

ディスク上のパーティション一覧を表示し、現在の構成を確認します。

```shell
# gpart show ada0
=>      34  83886013  ada0  GPT  (48G) [CORRUPT]
        34       128     1  freebsd-boot  (64k)
       162  79691648     2  freebsd-ufs  (38G)
  79691810   4194236     3  freebsd-swap  (2G)
  83886046         1        - free -  (512B)
```

> **注**: [GPT](https://en.wikipedia.org/wiki/GUID_Partition_Table) パーティション方式でフォーマットされたディスクでは、バックアップ用の GPT パーティションテーブルがドライブの末尾に位置しなくなるため、「corrupted（破損）」と表示されることがあります。バックアップ用パーティションテーブルは `gpart` で修復します。

```shell
# gpart recover ada0
ada0 recovered
```

これで、ディスク上の追加領域を新しいパーティションに使ったり、既存のパーティションを拡張したりできるようになりました。

```shell
# gpart show ada0
=>       34  102399933  ada0  GPT  (48G)
         34        128     1  freebsd-boot  (64k)
        162   79691648     2  freebsd-ufs  (38G)
   79691810    4194236     3  freebsd-swap  (2G)
   83886046   18513921        - free -  (8.8G)
```

パーティションを拡張できるのは、連続した空き領域（contiguous free space）に対してだけです。この例ではディスクの最後のパーティションがスワップパーティションですが、拡張したいのは 2 番目のパーティションです。スワップパーティションには一時的なデータしか入っていないため、いったんスワップを無効にして削除し、2 番目のパーティションを拡張してから 3 番目のパーティションを作り直しても問題ありません。

スワップパーティションを無効にします。

```shell
# swapoff /dev/ada0p3
```

`-i` フラグで番号を指定し、ディスク *ada0* から 3 番目のパーティションを削除します。

```shell
# gpart delete -i 3 ada0
ada0p3 deleted
# gpart show ada0
=>       34  102399933  ada0  GPT  (48G)
         34        128     1  freebsd-boot  (64k)
        162   79691648     2  freebsd-ufs  (38G)
   79691810   22708157        - free -  (10G)
```

> **警告**: マウント中のファイルシステムがあるパーティションテーブルを変更すると、データ損失の危険があります。以下の手順は、ライブ CD-ROM や USB デバイスから起動し、ファイルシステムをアンマウントした状態で行うのが最善です。どうしても必要な場合に限り、GEOM の安全機能を無効にしたうえでマウント中のファイルシステムをサイズ変更できます。

```shell
# sysctl kern.geom.debugflags=16
```

希望するサイズのスワップパーティションを作り直す余地を残しつつ、パーティションのサイズを変更します。サイズ変更するパーティションは `-i` で、新しい希望サイズは `-s` で指定します。必要に応じて、パーティションのアラインメントを `-a` で指定します。この操作で変わるのはパーティションのサイズだけであり、パーティション内のファイルシステムは別の手順で拡張します。

```shell
# gpart resize -i 2 -s 47G -a 4k ada0
ada0p2 resized
# gpart show ada0
=>       34  102399933  ada0  GPT  (48G)
         34        128     1  freebsd-boot  (64k)
        162   98566144     2  freebsd-ufs  (47G)
   98566306    3833661        - free -  (1.8G)
```

スワップパーティションを作成し直し、有効化します。`-s` でサイズを指定しない場合、残りの空き領域がすべて使われます。

```shell
# gpart add -t freebsd-swap -a 4k ada0
ada0p3 added
# gpart show ada0
=>       34  102399933  ada0  GPT  (48G)
         34        128     1  freebsd-boot  (64k)
        162   98566144     2  freebsd-ufs  (47G)
   98566306    3833661     3  freebsd-swap  (1.8G)
# swapon /dev/ada0p3
```

サイズ変更したパーティションの新しい容量を使えるよう、UFS ファイルシステムを拡張します。

```shell
# growfs /dev/ada0p2
Device is mounted read-write; resizing will result in temporary write suspension for /.
It's strongly recommended to make a backup before growing the file system.
OK to grow file system on /dev/ada0p2, mounted on /, from 38GB to 47GB? [Yes/No] Yes
super-block backups (for fsck -b #) at:
 80781312, 82063552, 83345792, 84628032, 85910272, 87192512, 88474752,
 89756992, 91039232, 92321472, 93603712, 94885952, 96168192, 97450432
```

ファイルシステムが ZFS の場合は、`-e` を付けて `online` サブコマンドを実行するとサイズ変更が行われます。

```shell
# zpool online -e zroot /dev/ada0p2
```

これでパーティションとその上のファイルシステムの両方がサイズ変更され、新しく利用可能になったディスク領域を使えるようになりました。

<a id="usb-disks"></a>
## USB ストレージデバイス

ハードディスク、USB メモリ、CD／DVD ライターなど、多くの外付けストレージ機器は USB（Universal Serial Bus）を使用します。FreeBSD は USB 1.x、2.0、および 3.0 デバイスに対応しています。

> **注**: USB 3.0 サポートは Haswell（Lynx Point）チップセットなど一部のハードウェアと互換性がありません。FreeBSD の起動時に `failed with error 19` というメッセージが表示される場合は、システムの BIOS で xHCI/USB3 を無効にしてください。

USB ストレージデバイスのサポートは `GENERIC` カーネルに組み込まれています。カスタムカーネルを使う場合は、カーネル設定ファイルに次の行が含まれていることを確認してください。

```
device scbus	# SCSI bus (required for ATA/SCSI)
device da	# Direct Access (disks)
device pass	# Passthrough device (direct ATA/SCSI access)
device uhci	# provides USB 1.x support
device ohci	# provides USB 1.x support
device ehci	# provides USB 2.0 support
device xhci	# provides USB 3.0 support
device usb	# USB Bus (required)
device umass	# Disks/Mass storage - Requires scbus and da
device cd	# needed for CD and DVD burners
```

FreeBSD は `umass(4)` ドライバを使い、SCSI サブシステム経由で USB ストレージデバイスにアクセスします。システムからはすべての USB デバイスが SCSI デバイスとして見えるため、USB デバイスが CD や DVD ライターである場合は、カスタムカーネル設定ファイルに `device atapicam` を *含めないでください*。

この節の残りでは、USB ストレージデバイスが FreeBSD に認識されているかを確認する方法と、デバイスを使えるように設定する方法を説明します。

<a id="chapter-21-heading-06"></a>
### デバイスの設定

USB 設定をテストするため、USB デバイスを接続します。システムメッセージバッファにドライブが表示されることを `dmesg` で確認します。次のような出力になります。

```shell
umass0: <STECH Simple Drive, class 0/0, rev 2.00/1.04, addr 3> on usbus0
umass0:  SCSI over Bulk-Only; quirks = 0x0100
umass0:4:0:-1: Attached to scbus4
da0 at umass-sim0 bus 0 scbus4 target 0 lun 0
da0: <STECH Simple Drive 1.04> Fixed Direct Access SCSI-4 device
da0: Serial Number WD-WXE508CAN263
da0: 40.000MB/s transfers
da0: 152627MB (312581808 512 byte sectors: 255H 63S/T 19457C)
da0: quirks=0x2<NO_6_BYTE>
```

ブランド名、デバイスノード（`da0`）、転送速度、容量はデバイスによって異なります。

USB デバイスは SCSI デバイスとして認識されるため、`camcontrol` を使ってシステムに接続されている USB ストレージデバイスの一覧を表示できます。

```shell
# camcontrol devlist
<STECH Simple Drive 1.04>          at scbus4 target 0 lun 0 (pass3,da0)
```

代わりに、`usbconfig` を使ってデバイスを一覧表示することもできます。このコマンドの詳細は `usbconfig(8)` を参照してください。

```shell
# usbconfig
ugen0.3: <Simple Drive STECH> at usbus0, cfg=0 md=HOST spd=HIGH (480Mbps) pwr=ON (2mA)
```

デバイスがまだフォーマットされていない場合は、[「ディスクの追加」](#disks-adding)を参照して USB ドライブのパーティション作成とフォーマットを行ってください。すでにファイルシステムが作成されている場合は、[「ファイルシステムのマウントとアンマウント」](03-basics.md#mount-unmount)の手順に従って `root` でマウントできます。

> **警告**: 以下で説明する `vfs.usermount` を有効にして、信頼できないユーザーに任意のメディアのマウントを許可することは、セキュリティの観点からは安全とは言えません。ほとんどのファイルシステムは、悪意のあるデバイスからシステムを守るようには設計されていません。

一般ユーザーがデバイスをマウントできるようにする 1 つの方法は、`pw(8)` を使ってデバイスを利用するすべてのユーザーを `operator` グループのメンバーにすることです。次に、`/etc/devfs.rules` に以下の行を追加し、`operator` がデバイスの読み書きを行えるようにします。

```
[localrules=5]
add path 'da*' mode 0660 group operator
```

> **注**: システムに内蔵 SCSI ディスクも搭載されている場合は、2 行目を次のように変更します。

```
add path 'da[3-9]*' mode 0660 group operator
```

> これにより、最初の 3 台の SCSI ディスク（`da0` から `da2`）は `operator` グループに属さないように除外されます。*3* の部分は内蔵 SCSI ディスクの台数に置き換えてください。このファイルの詳細は `devfs.rules(5)` を参照してください。

続いて、`/etc/rc.conf` でこのルールセットを有効にします。

```
devfs_system_ruleset="localrules"
```

その後、`/etc/sysctl.conf` に次の行を追加して、一般ユーザーによるファイルシステムのマウントを許可するようシステムに設定します。

```
vfs.usermount=1
```

この設定は次回の再起動後から有効になるため、今すぐ反映するには `sysctl` を使ってこの変数を設定します。

```shell
# sysctl vfs.usermount=1
vfs.usermount: 0 -> 1
```

最後の手順は、ファイルシステムをマウントするディレクトリを作成することです。このディレクトリは、ファイルシステムをマウントするユーザーが所有している必要があります。1 つの方法として、`root` が `/mnt/username` のようなそのユーザー所有のサブディレクトリを作成します。次の例では、*username* をユーザーのログイン名、*usergroup* をそのユーザーのプライマリグループに置き換えてください。

```shell
# mkdir /mnt/username
# chown username:usergroup /mnt/username
```

ここで USB メモリを接続し、デバイス `/dev/da0s1` が現れたとします。デバイスが FAT ファイルシステムでフォーマットされている場合、ユーザーは次のコマンドでマウントできます。

```shell
% mount -t msdosfs -o -m=644,-M=755 /dev/da0s1 /mnt/username
```

デバイスを取り外す前には、*必ず* 先にアンマウントしなければなりません。

```shell
% umount /mnt/username
```

デバイスを取り外した後、システムメッセージバッファには次のようなメッセージが表示されます。

```shell
umass0: at uhub3, port 2, addr 3 (disconnected)
da0 at umass-sim0 bus 0 scbus4 target 0 lun 0
da0: <STECH Simple Drive 1.04> s/n WD-WXE508CAN263          detached
(da0:umass-sim0:0:0:0): Periph destroyed
```

<a id="chapter-21-heading-07"></a>
### リムーバブルメディアの自動マウント

`/etc/auto_master` の次の行のコメントを外すことで、USB デバイスを自動的にマウントできます。

```shell
/media		-media		-nosuid
```

次に、`/etc/devd.conf` に以下の行を追加します。

```shell
notify 100 {
	match "system" "GEOM";
	match "subsystem" "DEV";
	action "/usr/sbin/automount -c";
};
```

すでに `autofs(5)` と `devd(8)` が起動している場合は、設定を再読み込みします。

```shell
# service automount restart
# service devd restart
```

`/etc/rc.conf` に次の行を追加すると、起動時に `autofs(5)` を自動的に開始するよう設定できます。

```
autofs_enable="YES"
```

`autofs(5)` を利用するには `devd(8)` が有効になっている必要があります（既定で有効です）。

次のコマンドでサービスをすぐに開始します。

```shell
# service automount start
# service automountd start
# service autounmountd start
# service devd start
```

自動マウント可能なファイルシステムは、それぞれ `/media/` 配下のディレクトリとして現れます。ディレクトリ名はファイルシステムのラベルから付けられます。ラベルがない場合は、デバイスノード名がディレクトリ名になります。

ファイルシステムは最初のアクセス時に透過的にマウントされ、一定時間アクセスがないとアンマウントされます。自動マウントされたドライブを手動でアンマウントすることもできます。

```shell
# automount -fu
```

この仕組みは通常、メモリカードや USB メモリに対して使われます。光学ドライブや iSCSI LUN を含む、あらゆるブロックデバイスで利用できます。

<a id="creating-cds"></a>
## CD メディアの作成と利用

コンパクトディスク（CD）メディアには、従来のディスクとは異なるいくつかの特徴があります。トラック間でヘッドを移動させる遅延なしに、連続してデータを読み出せるように設計されています。CD メディアにもトラックという概念はありますが、それはディスクの物理的な構造ではなく、連続して読み出されるデータの区画を指します。ISO 9660 ファイルシステムは、こうした違いに対応するために設計されました。

FreeBSD の Ports Collection には、音楽 CD やデータ CD を書き込んだり複製したりするためのユーティリティがいくつか用意されています。この節では、いくつかのコマンドラインユーティリティの使い方を紹介します。グラフィカルなインターフェースを備えた CD 書き込みソフトウェアを使いたい場合は、`sysutils/xcdroast` や `sysutils/k3b` のパッケージまたは port のインストールを検討してください。

<a id="atapicam"></a>
### 対応デバイス

`GENERIC` カーネルは、SCSI、USB、および ATAPI の CD リーダー／ライターに対応しています。カスタムカーネルを使う場合、カーネル設定ファイルに含める必要があるオプションはデバイスの種類によって異なります。

SCSI ライターの場合は、次のオプションが含まれていることを確認してください。

```
device scbus	# SCSI bus (required for ATA/SCSI)
device da	# Direct Access (disks)
device pass	# Passthrough device (direct ATA/SCSI access)
device cd	# needed for CD and DVD burners
```

USB ライターの場合は、次のオプションが含まれていることを確認してください。

```
device scbus	# SCSI bus (required for ATA/SCSI)
device da	# Direct Access (disks)
device pass	# Passthrough device (direct ATA/SCSI access)
device cd	# needed for CD and DVD burners
device uhci	# provides USB 1.x support
device ohci	# provides USB 1.x support
device ehci	# provides USB 2.0 support
device xhci	# provides USB 3.0 support
device usb	# USB Bus (required)
device umass	# Disks/Mass storage - Requires scbus and da
```

ATAPI ライターの場合は、次のオプションが含まれていることを確認してください。

```
device ata	# Legacy ATA/SATA controllers
device scbus	# SCSI bus (required for ATA/SCSI)
device pass	# Passthrough device (direct ATA/SCSI access)
device cd	# needed for CD and DVD burners
```

> **注**: 10.x より前のバージョンの FreeBSD で ATAPI デバイスを使う場合は、カーネル設定ファイルに次の行も必要です。

```
device atapicam
```

> あるいは、`/boot/loader.conf` に次の行を追加して起動時にこのドライバを読み込むこともできます。

```
atapicam_load="YES"
```

> このドライバは起動時にしか読み込めないため、システムの再起動が必要になります。

FreeBSD がデバイスを認識しているかを確認するには、`dmesg` を実行して該当デバイスのエントリを探します。10.x より前のシステムでは、出力の最初の行にあるデバイス名は `cd0` ではなく `acd0` になります。

```shell
% dmesg | grep cd
cd0 at ahcich1 bus 0 scbus1 target 0 lun 0
cd0: <HL-DT-ST DVDRAM GU70N LT20> Removable CD-ROM SCSI-0 device
cd0: Serial Number M3OD3S34152
cd0: 150.000MB/s transfers (SATA 1.x, UDMA6, ATAPI 12bytes, PIO 8192bytes)
cd0: Attempt to query device size failed: NOT READY, Medium not present - tray closed
```

<a id="cdrecord"></a>
### CD の書き込み

FreeBSD では、`cdrecord` を使って CD に書き込むことができます。このコマンドは `sysutils/cdrtools` パッケージまたは port でインストールされます。

`cdrecord` には多くのオプションがありますが、基本的な使い方は単純です。書き込む ISO ファイルの名前を指定し、システムに複数のライターがある場合は使用するデバイス名も指定します。

```shell
# cdrecord dev=device imagefile.iso
```

ライターのデバイス名を調べるには `-scanbus` を使います。次のような結果が得られます。

```shell
# cdrecord -scanbus
ProDVD-ProBD-Clone 3.00 (amd64-unknown-freebsd10.0) Copyright (C) 1995-2010 Jörg Schilling
Using libscg version 'schily-0.9'
scsibus0:
        0,0,0     0) 'SEAGATE ' 'ST39236LW       ' '0004' Disk
        0,1,0     1) 'SEAGATE ' 'ST39173W        ' '5958' Disk
        0,2,0     2) *
        0,3,0     3) 'iomega  ' 'jaz 1GB         ' 'J.86' Removable Disk
        0,4,0     4) 'NEC     ' 'CD-ROM DRIVE:466' '1.26' Removable CD-ROM
        0,5,0     5) *
        0,6,0     6) *
        0,7,0     7) *
scsibus1:
        1,0,0   100) *
        1,1,0   101) *
        1,2,0   102) *
        1,3,0   103) *
        1,4,0   104) *
        1,5,0   105) 'YAMAHA  ' 'CRW4260         ' '1.0q' Removable CD-ROM
        1,6,0   106) 'ARTEC   ' 'AM12S           ' '1.06' Scanner
        1,7,0   107) *
```

CD ライターのエントリを見つけ、カンマで区切られた 3 つの数字を `dev` の値として指定します。この例では Yamaha 製ライターのデバイスが `1,5,0` なので、このデバイスを指定するには `dev=1,5,0` と入力します。この値の他の指定方法や、オーディオトラックの書き込み・書き込み速度の制御については、`cdrecord` のマニュアルページを参照してください。

代わりに、次のコマンドを実行してライターのデバイスアドレスを取得することもできます。

```shell
# camcontrol devlist
<MATSHITA CDRW/DVD UJDA740 1.00>   at scbus1 target 0 lun 0 (cd0,pass0)
```

`scbus`、`target`、`lun` の数値を使います。この例では、デバイス名として `1,0,0` を指定します。

<a id="mkisofs"></a>
### ISO ファイルシステムへのデータ書き込み

データ CD を作成するには、CD のトラックとなるデータファイルをあらかじめ準備してから CD に書き込む必要があります。FreeBSD では `sysutils/cdrtools` を入れると `mkisofs` がインストールされ、UNIX® ファイルシステム上のディレクトリツリーをイメージ化した ISO 9660 ファイルシステムを作成できます。最も簡単な使い方は、作成する ISO ファイルの名前と、ISO 9660 ファイルシステムに含めるファイル群のパスを指定する方法です。

```shell
# mkisofs -o imagefile.iso /path/to/tree
```

このコマンドは、指定されたパス内のファイル名を標準 ISO 9660 ファイルシステムの制限に合う名前へ変換し、ISO ファイルシステムの規格を満たさないファイルは除外します。

標準規格の制約を緩和するためのオプションがいくつか用意されています。特に、`-R` は UNIX® システムで一般的な Rock Ridge 拡張を有効にし、`-J` は Microsoft® システムで使われる Joliet 拡張を有効にします。

FreeBSD システム専用で使う CD であれば、`-U` を使ってファイル名に関するすべての制限を無効にできます。`-R` と併用すると、たとえ ISO 9660 標準に違反していても、指定した FreeBSD ディレクトリツリーと同一のファイルシステムイメージが作成されます。

一般的によく使われるもう 1 つのオプションが `-b` です。これは「El Torito」方式の起動可能 CD を作成する際に、ブートイメージの場所を指定するために使います。このオプションには、CD に書き込むツリーの先頭から見たブートイメージへのパスを引数として渡します。既定では、`mkisofs` は「フロッピーディスクエミュレーション」モードで ISO イメージを作成するため、ブートイメージのサイズが正確に 1200、1440、または 2880 KB であることを前提とします。FreeBSD の配布メディアで使われているような一部のブートローダはエミュレーションモードを使用しません。その場合は `-no-emul-boot` を指定する必要があります。たとえば、`/tmp/myboot` に起動可能な FreeBSD システムがあり、そのブートイメージが `/tmp/myboot/boot/cdboot` にあるなら、次のコマンドで `/tmp/bootable.iso` を作成できます。

```shell
# mkisofs -R -no-emul-boot -b boot/cdboot -o /tmp/bootable.iso /tmp/myboot
```

作成された ISO イメージは、次のようにメモリディスクとしてマウントできます。

```shell
# mdconfig -a -t vnode -f /tmp/bootable.iso -u 0
# mount -t cd9660 /dev/md0 /mnt
```

その後、`/mnt` と `/tmp/myboot` が同一であることを確認できます。

`mkisofs` には、動作を細かく調整するためのオプションが他にも多数あります。詳細は `mkisofs(8)` を参照してください。

> **注**: データ CD をコピーして、`mkisofs` で作成したイメージファイルと機能的に同等のイメージファイルを作ることもできます。それには、入力ファイルにデバイス名、出力ファイルに作成する ISO ファイル名を指定して `dd` を使います。

```shell
# dd if=/dev/cd0 of=file.iso bs=2048
```

> こうして作成したイメージファイルは、[「CD の書き込み」](#cdrecord)の説明に従って CD へ書き込めます。

<a id="mounting-cd"></a>
### データ CD の利用

ISO を CD に書き込んだら、ファイルシステムの種類、CD が入っているデバイス名、および既存のマウントポイントを指定してマウントできます。

```shell
# mount -t cd9660 /dev/cd0 /mnt
```

`mount` は既定でファイルシステムの種類を `ufs` とみなすため、データ CD をマウントするときに `-t cd9660` を付けないと `Incorrect super block` エラーが発生します。

どのデータ CD もこの方法でマウントできますが、特定の ISO 9660 拡張を使ったディスクでは挙動がおかしくなることがあります。たとえば Joliet ディスクでは、すべてのファイル名が 2 バイトの Unicode 文字で格納されます。英語以外の文字が疑問符（`?`）として表示される場合は、`-C` でローカルの文字セットを指定してください。詳細は `mount_cd9660(8)` を参照してください。

> **注**: `-C` を使ってこの文字変換を行うには、カーネルに `cd9660_iconv.ko` モジュールが読み込まれている必要があります。これには `loader.conf` に次の行を追加してマシンを再起動するか、`kldload` で直接モジュールを読み込みます。

```
cd9660_iconv_load="YES"
```

データ CD をマウントしようとしたときに、まれに `Device not configured` と表示されることがあります。これは通常、CD ドライブがトレイ内のディスクをまだ検出していないか、バス上でドライブが見えていないことを意味します。CD ドライブがメディアを検出するまで数秒かかることがあるため、少し待ってみてください。

場合によっては、バスリセットへの応答が間に合わず、SCSI CD ドライブが見落とされることもあります。これを解決するには、既定の SCSI 遅延時間を増やしたカスタムカーネルを作成します。カスタムカーネルの設定ファイルに次のオプションを追加し、[「カスタムカーネルの構築とインストール」](09-kernelconfig.md#kernelconfig-building)の手順に従ってカーネルを再構築してください。

```
options SCSI_DELAY=15000
```

これにより、起動時に SCSI バスが 15 秒間待機するようになり、CD ドライブがバスリセットに応答する十分な時間が確保されます。

> **注**: ISO 9660 ファイルシステムを作成せず、ファイルを直接 CD に書き込むこともできます。これは生データ（raw data）CD の書き込みと呼ばれ、バックアップ目的で行う人もいます。
>
> この種のディスクは通常のデータ CD のようにマウントすることはできません。書き込んだデータを取り出すには、生のデバイスノードから直接読み出す必要があります。たとえば、次のコマンドは 2 台目の CD デバイス上にある圧縮 tar ファイルを現在の作業ディレクトリへ展開します。

```shell
# tar xzvf /dev/cd1
```

> データ CD としてマウントできるようにするには、`mkisofs` を使ってデータを書き込む必要があります。

<a id="duplicating-audiocds"></a>
### 音楽 CD の複製

音楽 CD を複製するには、CD からオーディオデータを一連のファイルとして抽出し、それらのファイルを空の CD に書き込みます。

[「手順：音楽 CD の複製」](#using-cdrecord)で、音楽 CD を複製して書き込む方法を説明します。FreeBSD のバージョンが 10.0 未満でデバイスが ATAPI の場合は、[「対応デバイス」](#atapicam)の手順に従って先に `atapicam` モジュールを読み込んでおく必要があります。

<a id="using-cdrecord"></a>
**手順：音楽 CD の複製**

1. `sysutils/cdrtools` パッケージまたは port を入れると `cdda2wav` がインストールされます。このコマンドを使ってすべてのオーディオトラックを抽出し、各トラックを現在の作業ディレクトリに個別の WAV ファイルとして書き出します。

```shell
% cdda2wav -vall -B -Owav
```

   システムに CD デバイスが 1 台しかない場合は、デバイス名を指定する必要はありません。デバイスの指定方法や、このコマンドで利用できるその他のオプションについては `cdda2wav` のマニュアルページを参照してください。

2. `cdrecord` を使って `.wav` ファイルを書き込みます。

```shell
% cdrecord -v dev=2,0 -dao -useinfo  *.wav
```

   *2,0* の部分は、[「CD の書き込み」](#cdrecord)で説明したとおり適切な値に設定してください。

<a id="creating-dvds"></a>
## DVD メディアの作成と利用

CD と比べて、DVD は次世代の光メディア記録技術です。DVD はどの CD よりも多くのデータを記録でき、映像配布の標準となっています。

記録可能な DVD には、物理的な記録形式として次の 5 種類があります。

* DVD-R: 最初に登場した記録可能 DVD 形式です。DVD-R 規格は [DVD Forum](http://www.dvdforum.org/forum.shtml) によって策定されています。この形式は 1 回のみ書き込み可能（ライトワンス）です。
* DVD-RW: DVD-R 規格の書き換え可能版です。DVD-RW はおよそ 1000 回書き換えできます。
* DVD-RAM: リムーバブルハードドライブのように扱える書き換え可能な形式です。ただし、DVD-RAM 形式に対応する DVD ライターは限られているため、ほとんどの DVD-ROM ドライブや DVD-Video プレーヤーとは互換性がありません。DVD-RAM の使い方の詳細は[「DVD-RAM の利用」](#creating-dvd-ram)を参照してください。
* DVD+RW: [DVD+RW Alliance](https://en.wikipedia.org/wiki/DVD%2BRW_Alliance) によって策定された書き換え可能な形式です。DVD+RW はおよそ 1000 回書き換えできます。
* DVD+R: DVD+RW 形式の 1 回書き込み専用（ライトワンス）版です。

片面 1 層の記録可能 DVD には最大 4,700,000,000 バイトを記録できます。1 キロバイトを 1024 バイトとして計算すると、実際には 4.38 GB（4485 MB）になります。

> **注**: 物理メディアとアプリケーション（記録形式）は区別して考える必要があります。たとえば DVD-Video は特定のファイル配置規格であり、DVD-R、DVD+R、DVD-RW など記録可能な DVD 物理メディアのいずれにも書き込むことができます。メディアの種類を選ぶ前に、ライターと DVD-Video プレーヤーの双方がそのメディアに対応していることを確認してください。

<a id="chapter-21-heading-15"></a>
### 設定

DVD の記録を行うには `growisofs(1)` を使います。このコマンドは、すべての DVD メディア形式に対応する `sysutils/dvd+rw-tools` ユーティリティ群に含まれています。

これらのツールは SCSI サブシステム経由でデバイスにアクセスするため、[ATAPI/CAM サポート](#atapicam)をカーネルに読み込むか静的に組み込んでおく必要があります。ライターが USB 接続の場合はこのサポートは不要です。USB デバイスの設定詳細は[「USB ストレージデバイス」](#usb-disks)を参照してください。

また、ATAPI デバイスでは `/boot/loader.conf` に次の行を追加して DMA アクセスを有効にする必要があります。

```
hw.ata.atapi_dma="1"
```

dvd+rw-tools を使用する前に、[Hardware Compatibility Notes](http://fy.chalmers.se/~appro/linux/DVD+RW/hcn.html) を確認してください。

> **注**: グラフィカルユーザーインターフェースを使いたい場合は、`growisofs(1)` やその他の多くの書き込みツールに対して使いやすいフロントエンドを提供する `sysutils/k3b` の利用を検討してください。

<a id="chapter-21-heading-16"></a>
### データ DVD の書き込み

`growisofs(1)` は [mkisofs](#mkisofs) のフロントエンドであるため、ファイルシステム構造の作成と DVD への書き込みを行う際に `mkisofs(8)` を呼び出します。したがって、書き込み処理の前にデータの ISO イメージを別途作成しておく必要はありません。

`/path/to/data` のデータを DVD+R または DVD-R に書き込むには、次のコマンドを使います。

```shell
# growisofs -dvd-compat -Z /dev/cd0 -J -R /path/to/data
```

この例では、Joliet 拡張と Rock Ridge 拡張を備えた ISO 9660 ファイルシステムを作成するため、`mkisofs(8)` に `-J -R` を渡しています。詳細は `mkisofs(8)` を参照してください。

最初のセッションを記録するときは、シングルセッションでもマルチセッションでも `-Z` を使います。*/dev/cd0* の部分は DVD デバイスの名前に置き換えてください。`-dvd-compat` を指定すると、ディスクがクローズされ、それ以上追記できなくなります。これにより、DVD-ROM ドライブとのメディア互換性も高まります。

*imagefile.iso* のようにあらかじめ作成済みのイメージを書き込むには、次のようにします。

```shell
# growisofs -dvd-compat -Z /dev/cd0=imagefile.iso
```

書き込み速度は、使用するメディアとドライブに応じて自動的に検出・設定されます。書き込み速度を強制的に指定したい場合は `-speed=` を使います。使用例は `growisofs(1)` を参照してください。

> **注**: 4.38 GB を超えるファイルを扱うには、`mkisofs(8)` および `growisofs(1)` などの関連プログラムすべてに `-udf -iso-level 3` を渡して、UDF/ISO-9660 ハイブリッドファイルシステムを作成する必要があります。これが必要なのは、ISO イメージファイルを新規作成するとき、またはファイルをディスクへ直接書き込むときだけです。この方法で作成したディスクは `mount_udf(8)` を使って UDF ファイルシステムとしてマウントしなければならないため、UDF に対応したオペレーティングシステムでしか利用できません。未対応の環境では、ファイルが破損しているように見えます。
>
> この種類の ISO ファイルを作成するには次のようにします。

```shell
% mkisofs -R -J -udf -iso-level 3 -o imagefile.iso /path/to/data
```

> ファイルをディスクへ直接書き込むには次のようにします。

```shell
# growisofs -dvd-compat -udf -iso-level 3 -Z /dev/cd0 -J -R /path/to/data
```

> ISO イメージにすでに大きなファイルが含まれている場合、そのイメージをディスクに書き込む際に `growisofs(1)` へ追加のオプションを渡す必要はありません。
>
> また、`mkisofs(8)` を含む `sysutils/cdrtools` は最新のバージョンを使ってください。古いバージョンでは大容量ファイルに対応していない場合があります。最新版でも動作しない場合は、`sysutils/cdrtools-devel` をインストールしてその `mkisofs(8)` を参照してください。

<a id="chapter-21-heading-17"></a>
### DVD-Video の書き込み

DVD-Video は、ISO 9660 と micro-UDF（M-UDF）仕様に基づく特殊なファイル配置規格です。DVD-Video は固有のデータ構造階層を持つため、DVD をオーサリングするには `multimedia/dvdauthor` などの専用プログラムが必要です。

DVD-Video ファイルシステムのイメージがすでにある場合は、他のイメージと同じ方法で書き込めます。`dvdauthor` を使って DVD を作成し、その結果が `/path/to/video` にある場合は、次のコマンドで DVD-Video を書き込みます。

```shell
# growisofs -Z /dev/cd0 -dvd-video /path/to/video
```

`-dvd-video` は `mkisofs(8)` に渡され、DVD-Video ファイルシステム構造を作成するよう指示します。このオプションを指定すると、`growisofs(1)` の `-dvd-compat` オプションも暗黙のうちに有効になります。

<a id="chapter-21-heading-18"></a>
### DVD+RW の利用

CD-RW とは異なり、未使用の DVD+RW は初めて使う前にフォーマットする必要があります。適切なタイミングで `growisofs(1)` に自動でフォーマットさせることが *推奨* されています。ただし、`dvd+rw-format` を使って DVD+RW をフォーマットすることもできます。

```shell
# dvd+rw-format /dev/cd0
```

この操作は一度だけ実行してください。フォーマットが必要なのは未使用の DVD+RW メディアだけです。一度フォーマットすれば、その後は通常どおり DVD+RW に書き込めます。

DVD+RW にデータを追記するのではなく、まったく新しいファイルシステムを書き込む場合でも、事前にメディアを消去する必要はありません。代わりに、次のように以前の記録を上書きします。

```shell
# growisofs -Z /dev/cd0 -J -R /path/to/newdata
```

DVD+RW 形式は、以前の記録へのデータ追記に対応しています。この操作はマルチセッション書き込みとはみなされず、新しいセッションを既存のセッションへ統合する形になります。`growisofs(1)` はメディア上にある ISO 9660 ファイルシステムを *拡張（grow）* します。

たとえば、DVD+RW にデータを追記するには次のようにします。

```shell
# growisofs -M /dev/cd0 -J -R /path/to/nextdata
```

次回以降の書き込みでは、最初のセッションを書き込んだときと同じ `mkisofs(8)` オプションを使用してください。

> **注**: DVD-ROM ドライブとのメディア互換性を高めるため、`-dvd-compat` を指定してください。DVD+RW を使う場合、このオプションを指定してもデータの追記は妨げられません。

メディアを消去するには、次のようにします。

```shell
# growisofs -Z /dev/cd0=/dev/zero
```

<a id="chapter-21-heading-19"></a>
### DVD-RW の利用

DVD-RW は、インクリメンタルシーケンシャル（incremental sequential）とリストリクテッドオーバーライト（restricted overwrite）の 2 つのディスク形式を受け付けます。既定では、DVD-RW ディスクはシーケンシャル形式になっています。

未使用の DVD-RW はフォーマットせずにそのまま書き込めます。ただし、使用済みのシーケンシャル形式 DVD-RW に新しい初回セッションを書き込む前には消去が必要です。

シーケンシャルモードの DVD-RW を消去するには、次のようにします。

```shell
# dvd+rw-format -blank=full /dev/cd0
```

> **注**: `-blank=full` による完全消去は、1 倍速メディアで約 1 時間かかります。DVD-RW を Disk-At-Once（DAO）モードで記録する場合は、`-blank` を使って高速消去を行えます。DAO モードで DVD-RW に書き込むには、次のコマンドを使います。

```shell
# growisofs -use-the-force-luke=dao -Z /dev/cd0=imagefile.iso
```

> `growisofs(1)` は高速消去されたメディアを自動的に検出し、DAO 書き込みを試みるため、通常 `-use-the-force-luke=dao` は不要です。
>
> なお、リストリクテッドオーバーライトモードは既定のインクリメンタルシーケンシャル形式よりも柔軟であるため、DVD-RW ではどの用途でもリストリクテッドオーバーライトモードを使うほうがよいでしょう。

シーケンシャル形式の DVD-RW にデータを書き込むには、他の DVD 形式と同じ手順を使います。

```shell
# growisofs -Z /dev/cd0 -J -R /path/to/data
```

以前の記録にデータを追記するには、`growisofs(1)` で `-M` を使います。ただし、インクリメンタルシーケンシャルモードの DVD-RW にデータを追記すると、ディスク上に新しいセッションが作成され、結果はマルチセッションディスクになります。

リストリクテッドオーバーライト形式の DVD-RW では、新しい初回セッションの前に消去する必要はありません。代わりに `-Z` でディスクを上書きします。また、ディスクに書き込まれている既存の ISO 9660 ファイルシステムを `-M` で拡張することも可能です。この結果はシングルセッションの DVD になります。

DVD-RW をリストリクテッドオーバーライト形式にするには、次のコマンドを実行します。

```shell
# dvd+rw-format /dev/cd0
```

シーケンシャル形式に戻すには、次のようにします。

```shell
# dvd+rw-format -blank=full /dev/cd0
```

<a id="chapter-21-heading-20"></a>
### マルチセッション

マルチセッション DVD に対応している DVD-ROM ドライブは少なく、ほとんどの場合は最初のセッションしか読み取りません。DVD+R、DVD-R、およびシーケンシャル形式の DVD-RW は複数セッションに対応できます。DVD+RW およびリストリクテッドオーバーライト形式の DVD-RW にはマルチセッションという概念がありません。

DVD+R、DVD-R、またはシーケンシャル形式の DVD-RW にクローズしていない初回セッションを書き込んだ後で次のコマンドを使うと、ディスクに新しいセッションが追加されます。

```shell
# growisofs -M /dev/cd0 -J -R /path/to/nextdata
```

DVD+RW またはリストリクテッドオーバーライトモードの DVD-RW でこのコマンドを使うと、新しいセッションを既存のセッションへ統合しながらデータを追記します。結果はシングルセッションディスクになります。これらのメディアで初回書き込み後にデータを追加する際はこの方法を使います。

> **注**: 各セッションの間にはセッションの終了と開始を示す領域が消費されるため、メディア容量を最適に使うには一度にまとまった量のデータを追加してください。セッション数の上限は、DVD+R で 154、DVD-R で約 2000、DVD+R Double Layer で 127 です。

<a id="chapter-21-heading-21"></a>
### 詳細情報

DVD の詳細情報を取得するには、指定したドライブにディスクを入れた状態で `dvd+rw-mediainfo /dev/cd0` を実行します。

dvd+rw-tools のさらなる情報は、`growisofs(1)`、[dvd+rw-tools Web サイト](http://fy.chalmers.se/~appro/linux/DVD+RW/)、および [cdwrite メーリングリスト](http://lists.debian.org/cdwrite/)アーカイブを参照してください。

> **注**: dvd+rw-tools の使用に関する問題報告（PR）を作成する際は、必ず `dvd+rw-mediainfo` の出力を含めてください。

<a id="creating-dvd-ram"></a>
### DVD-RAM の利用

DVD-RAM ライターは SCSI または ATAPI インターフェースのいずれかを使用します。ATAPI デバイスの場合、`/boot/loader.conf` に次の行を追加して DMA アクセスを有効にする必要があります。

```
hw.ata.atapi_dma="1"
```

DVD-RAM はリムーバブルハードドライブのように扱えます。他のハードドライブと同様、使用前に DVD-RAM をフォーマットする必要があります。この例では、ディスク領域全体を標準の UFS2 ファイルシステムでフォーマットします。

```shell
# dd if=/dev/zero of=/dev/acd0 bs=2k count=1
# bsdlabel -Bw acd0
# newfs /dev/acd0
```

DVD デバイス `acd0` の部分は環境に合わせて変更してください。

DVD-RAM をフォーマットしたら、通常のハードドライブと同じようにマウントできます。

```shell
# mount /dev/acd0 /mnt
```

マウントすると、DVD-RAM は読み書きの両方が可能になります。

<a id="floppies"></a>
## フロッピーディスクの作成と利用

この節では、FreeBSD で 3.5 インチフロッピーディスクをフォーマットする方法を説明します。

**手順：フロッピーをフォーマットする手順**

フロッピーディスクは使用する前にローレベルフォーマットを行う必要があります。通常はベンダーによって済まされていますが、フォーマットを行うことでメディアの健全性を確認できます。FreeBSD でフロッピーディスクをローレベルフォーマットするには `fdformat(8)` を使います。このユーティリティを実行する際は、ディスクの良否を判断する手がかりになるため、エラーメッセージが出ていないか注意してください。

1. フロッピーをフォーマットするには、新しい 3.5 インチフロッピーディスクを 1 台目のフロッピードライブに挿入し、次のコマンドを実行します。

```shell
# /usr/sbin/fdformat -f 1440 /dev/fd0
```

2. ディスクをローレベルフォーマットした後、システムがディスクのサイズとジオメトリを判別できるようディスクラベルを作成します。対応しているジオメトリ値は `/etc/disktab` に一覧表示されています。

   ディスクラベルを書き込むには `bsdlabel(8)` を使います。

```shell
# /sbin/bsdlabel -B -w /dev/fd0 fd1440
```

3. これで、ファイルシステムによるハイレベルフォーマットを行う準備が整いました。フロッピーのファイルシステムには UFS または FAT のいずれも使えますが、通常は FAT のほうがフロッピーに適しています。

   フロッピーを FAT でフォーマットするには、次のコマンドを実行します。

```shell
# /sbin/newfs_msdos /dev/fd0
```

これでディスクを使用する準備が整いました。フロッピーを使うには `mount_msdosfs(8)` でマウントします。また、Ports Collection から `emulators/mtools` をインストールして使うこともできます。

<a id="backup-basics"></a>
## バックアップの基本

ディスク障害、誤ったファイル削除、予期しないファイル破損、あるいはオンサイトのバックアップも含めたマシン全体の破壊から復旧できるようにするには、バックアップ計画を立てて実施することが不可欠です。

バックアップの種類やスケジュールは、データの重要性、ファイル復元に求められる粒度、許容できるダウンタイムに応じて変わります。考えられるバックアップ手法には次のようなものがあります。

* システム全体のアーカイブを作成し、オフサイトの恒久的なメディアへバックアップする。上記のすべての問題から保護できますが、特に非特権ユーザーにとって復元が遅く手間がかかります。
* ファイルシステムのスナップショット。削除されたファイルや以前のバージョンのファイルを復元するのに便利です。
* スケジュール実行される `net/rsync` を使い、ネットワーク上の別のシステムとファイルシステム全体またはディスク全体のコピーを同期する。
* ハードウェアまたはソフトウェア RAID。ディスク故障時のダウンタイムを最小化または回避できます。

通常は、これらのバックアップ手法を組み合わせて使います。たとえば、毎週のフルシステムバックアップを自動スケジュールしてオフサイトに保管しつつ、1 時間ごとの ZFS スナップショットで補完する構成が考えられます。さらに、ファイルの編集や削除を行う前に、個別のディレクトリやファイルを手動でバックアップすることもできます。

この節では、FreeBSD システムでバックアップを作成・管理するために利用できるいくつかのユーティリティを説明します。

<a id="chapter-21-heading-25"></a>
### ファイルシステムのバックアップ

ファイルシステムをバックアップする伝統的な UNIX® プログラムは、バックアップを作成する `dump(8)` と、バックアップを復元する `restore(8)` です。これらのユーティリティはファイルシステムが作るファイル・リンク・ディレクトリという抽象化の下層、すなわちディスクブロックレベルで動作します。他のバックアップソフトウェアとは異なり、`dump` はファイルシステム全体をバックアップするため、ファイルシステムの一部だけや、複数のファイルシステムにまたがるディレクトリツリーをバックアップすることはできません。`dump` はファイルやディレクトリを書き出すのではなく、それらを構成する生のデータブロックを書き出します。

> **注**: ルートディレクトリに対して `dump` を実行しても、`/home` や `/usr` などの多くのディレクトリはバックアップされません。これらは通常、別のファイルシステムへのマウントポイント、またはそれらのファイルシステムへのシンボリックリンクだからです。

データを復元する際、`restore` は既定で `/tmp/` に一時ファイルを保存します。`/tmp` が小さいリカバリディスクを使う場合は、復元を成功させるために十分な空き容量があるディレクトリへ `TMPDIR` を設定してください。

`dump` を使う際は、1975 年頃の AT&T UNIX® Version 6 時代の名残となる特有の挙動がある点に注意してください。既定のパラメータは、他のメディアや現代の高密度テープではなく、9 トラックテープへのバックアップを想定しています。これらの既定値はコマンドラインで上書きする必要があります。

ネットワーク経由で別のシステムや、別のコンピュータに接続されたテープドライブへファイルシステムをバックアップすることも可能です。この目的には `rdump(8)` と `rrestore(8)` ユーティリティも使えますが、これらは安全とはみなされていません。

代わりに、SSH 接続越しに `dump` と `restore` をより安全に使うことができます。次の例では、`/usr` の圧縮フルバックアップを作成し、SSH 接続経由で指定したホストへバックアップファイルを送信しています。

**例：ssh 経由での `dump` の使用**

```shell
# /sbin/dump -0uan -f - /usr | gzip -2 | ssh -c blowfish \
          targetuser@targetmachine.example.com dd of=/mybigfiles/dump-usr-l0.gz
```

> **訳注**: 原文の例では `ssh -c blowfish` が使われていますが、近年の OpenSSH では Blowfish 暗号は削除されているため、実際の環境では利用可能な暗号方式を指定するか `-c` オプションを省略する必要があります（コマンド例は固定原文どおり保持しています）。

次の例では、SSH 接続経由でリモートシステム上のテープドライブにバックアップを書き込むため、`RSH` を設定しています。

**例：`RSH` を設定して ssh 経由で `dump` を使用**

```shell
# env RSH=/usr/bin/ssh /sbin/dump -0uan -f targetuser@targetmachine.example.com:/dev/sa0 /usr
```

> **ヒント**: [Z ファイルシステム（ZFS）](23-zfs.md#zfs)を使っているシステムでは、`zfs(8)` を使ってスナップショットを作成したり、リモートシステムとの間で[送受信](23-zfs.md#zfs-zfs-send)したりすることができます。

<a id="chapter-21-heading-26"></a>
### ディレクトリのバックアップ

必要に応じて特定のファイルやディレクトリをバックアップ・復元するための組み込みユーティリティがいくつか用意されています。

ディレクトリ内のすべてのファイルをバックアップするには、`tar(1)` が適しています。このユーティリティは AT&T UNIX® Version 6 にまでさかのぼり、既定ではローカルのテープデバイスへ再帰的にバックアップする動作を想定しています。オプションを指定すれば、代わりにバックアップファイル名を指定できます。

次の例では、現在のディレクトリの圧縮バックアップを作成し、`/tmp/mybackup.tgz` に保存します。バックアップファイルを作成する際は、バックアップ対象のディレクトリと同じ場所にバックアップを保存しないよう注意してください。

**例：`tar` による現在のディレクトリのバックアップ**

```shell
# tar czvf /tmp/mybackup.tgz .
```

バックアップ全体を復元するには、復元先のディレクトリへ `cd` し、バックアップファイル名を指定します。復元先ディレクトリにあるより新しいバージョンのファイルは上書きされる点に注意してください。迷った場合は、一時ディレクトリに復元するか、バックアップ内の復元したいファイル名を指定してください。

**例：`tar` による現在のディレクトリの復元**

```shell
# tar xzvf /tmp/mybackup.tgz
```

`tar(1)` には多数のオプションがあり、マニュアルページで説明されています。このユーティリティは除外パターンにも対応しており、指定ディレクトリのバックアップ時やバックアップからの復元時に含めないファイルを指定できます。

指定したファイルとディレクトリのリストを使ってバックアップを作成するには、`cpio(1)` が適しています。`tar` とは異なり、`cpio` にはディレクトリツリーをたどる機能がないため、バックアップ対象のファイル一覧を明示的に渡す必要があります。

たとえば、ファイル一覧は `ls` や `find` で作成できます。次の例では、現在のディレクトリの再帰的な一覧を作成し、それを `cpio` へパイプで渡して `/tmp/mybackup.cpio` という出力バックアップファイルを作成します。

**例：`ls` と `cpio` を使った現在のディレクトリの再帰的バックアップ**

```shell
# ls -R | cpio -ovF /tmp/mybackup.cpio
```

`tar` と `cpio` が提供する機能の橋渡しをするバックアップユーティリティが `pax(1)` です。長年の間にさまざまな版の `tar` と `cpio` の間でわずかな非互換が生じたため、POSIX® が `pax` を策定しました。`pax` は各種の `cpio` 形式や `tar` 形式の多くを読み書きでき、独自の新しい形式にも対応しています。

ここまでの例に相当する `pax` のコマンドは次のようになります。

**例：`pax` による現在のディレクトリのバックアップ**

```shell
# pax -wf /tmp/mybackup.pax .
```

<a id="backups-tapebackups"></a>
### バックアップへのデータテープの利用

テープ技術は進化を続けていますが、現代のバックアップシステムではオフサイトバックアップとローカルのリムーバブルメディアを組み合わせるのが一般的です。FreeBSD は、LTO や DAT など SCSI を使うあらゆるテープドライブに対応しています。SATA および USB のテープドライブへの対応は限定的です。

SCSI テープデバイスに対して、FreeBSD は `sa(4)` ドライバと `/dev/sa0`、`/dev/nsa0`、`/dev/esa0` デバイスを使用します。物理デバイス名は `/dev/sa0` です。`/dev/nsa0` を使うと、バックアップアプリケーションがファイルを書き込んだ後にテープを巻き戻さないため、1 本のテープに複数のファイルを書き込めます。`/dev/esa0` を使うと、デバイスを閉じた後にテープが排出（イジェクト）されます。

FreeBSD では、テープ上のファイルをシークしたり、テープ制御マークを書き込んだりといったテープドライブの操作に `mt` を使います。たとえば、新しいファイルを書き込む前に最初の 3 つのファイルをスキップして保護するには、次のようにします。

```shell
# mt -f /dev/nsa0 fsf 3
```

このユーティリティは多くの操作に対応しています。詳細は `mt(1)` を参照してください。

`tar` を使ってテープに 1 つのファイルを書き込むには、テープデバイス名とバックアップするファイルを指定します。

```shell
# tar cvf /dev/sa0 file
```

テープ上の `tar` アーカイブから現在のディレクトリへファイルを復元するには、次のようにします。

```shell
# tar xvf /dev/sa0
```

UFS ファイルシステムをバックアップするには `dump` を使います。次の例では、完了後にテープを巻き戻さずに `/usr` をバックアップします。

```shell
# dump -0aL -b64 -f /dev/nsa0 /usr
```

テープ上の `dump` ファイルから現在のディレクトリへ対話的にファイルを復元するには、次のようにします。

```shell
# restore -i -f /dev/nsa0
```

<a id="backups-programs-amanda"></a>
### サードパーティ製バックアップユーティリティ

FreeBSD の Ports Collection には、バックアップ作成のスケジュール化やテープバックアップの簡素化を行い、バックアップをより簡単かつ便利にするサードパーティ製ユーティリティが多数用意されています。これらのアプリケーションの多くはクライアント／サーバ型であり、単一システムやネットワーク上の全コンピュータのバックアップを自動化できます。

よく使われるユーティリティには次のものがあります。

* Amanda（`misc/amanda-server` および `misc/amanda-client`）
* Bacula（`sysutils/bacula13-server` および `sysutils/bacula13-client`）
* Bareos（`sysutils/bareos-server` および `sysutils/bareos-client`）
* `net/rsync`
* `sysutils/duply`
* `sysutils/duplicity`

<a id="chapter-21-heading-29"></a>
### 緊急時の復旧

定期的なバックアップに加えて、緊急時の備えとして次の手順を実施しておくことを推奨します。

以下のコマンドの出力を印刷したものを作成しておきます。

* `gpart show`
* `more /etc/fstab`
* `pkg prime-list`
* `dmesg`

この印刷物とインストールメディアのコピーを安全な場所に保管します。緊急の復旧が必要になった場合は、インストールメディアから起動して `Live CD` を選択し、レスキューシェルに入ります。このレスキューモードを使えば、システムの現在の状態を確認し、必要に応じてディスクを再フォーマットしてバックアップからデータを復元できます。

次に、レスキューシェルとバックアップのテストを行います。その手順をメモに記録し、メディア、印刷物、バックアップと一緒に保管してください。緊急復旧のプレッシャー下で作業するとき、このメモがあれば誤ってバックアップを破壊してしまう事態を防げます。

さらに安全性を高めるため、最新のバックアップはコンピュータやディスクドライブから物理的に十分離れた遠隔地にも保管してください。

<a id="disks-virtual"></a>
## メモリディスク

FreeBSD は物理ディスクに加えて、メモリディスクの作成と利用にも対応しています。メモリディスクの用途の 1 つとして、ISO ファイルシステムを CD や DVD に焼いてからマウントするという手間をかけずに、直接その中身へアクセスする方法があります。

FreeBSD では、`md(4)` ドライバがメモリディスクのサポートを提供します。`GENERIC` カーネルにはこのドライバが含まれています。カスタムカーネル設定ファイルを使う場合は、次の行が含まれていることを確認してください。

```
device md
```

<a id="disks-mdconfig"></a>
### 既存イメージの接続と切り離し

既存のファイルシステムイメージをマウントするには、`mdconfig` を使って ISO ファイル名と空いているユニット番号を指定します。次に、そのユニット番号を指定して既存のマウントポイントへマウントします。マウントが完了すると、ISO 内のファイルがそのマウントポイントに表示されます。次の例では、*diskimage.iso* をメモリデバイス `/dev/md0` に接続し、そのメモリデバイスを `/mnt` にマウントしています。

```shell
# mdconfig -f diskimage.iso -u 0
# mount -t cd9660 /dev/md0 /mnt
```

ISO 形式をマウントするために `-t cd9660` を指定している点に注目してください。`-u` でユニット番号を指定しない場合、`mdconfig` は未使用のメモリデバイスを自動的に割り当て、割り当てられたユニット名（たとえば `md4`）を出力します。このコマンドとオプションの詳細は `mdconfig(8)` を参照してください。

メモリディスクを使い終えたら、そのリソースをシステムへ解放する必要があります。まずファイルシステムをアンマウントし、次に `mdconfig` を使ってシステムからディスクを切り離してリソースを解放します。上の例に続けて実行する場合は次のようになります。

```shell
# umount /mnt
# mdconfig -d -u 0
```

システムにまだメモリディスクが接続されているかどうかを確認するには、`mdconfig -l` を実行します。

<a id="disks-md-freebsd5"></a>
### ファイルまたはメモリをバックエンドとするメモリディスクの作成

FreeBSD は、記憶領域をハードディスク上またはメモリ上のいずれかから割り当てるメモリディスクにも対応しています。前者は一般にファイルバックエンド（file-backed）ファイルシステム、後者はメモリバックエンド（memory-backed）ファイルシステムと呼ばれます。どちらも `mdconfig` を使って作成できます。

新しいメモリバックエンドファイルシステムを作成するには、タイプに `swap` を指定し、作成するメモリディスクのサイズを指定します。その後、通常どおりファイルシステムでメモリディスクをフォーマットしてマウントします。次の例では、ユニット `1` に 5 MB のメモリディスクを作成し、マウントする前に UFS ファイルシステムでフォーマットしています。

```shell
# mdconfig -a -t swap -s 5m -u 1
# newfs -U md1
/dev/md1: 5.0MB (10240 sectors) block size 16384, fragment size 2048
        using 4 cylinder groups of 1.27MB, 81 blks, 192 inodes.
        with soft updates
super-block backups (for fsck -b #) at:
 160, 2752, 5344, 7936
# mount /dev/md1 /mnt
# df /mnt
Filesystem 1K-blocks Used Avail Capacity  Mounted on
/dev/md1        4718    4  4338     0%    /mnt
```

新しいファイルバックエンドメモリディスクを作成するには、まず使用するディスク領域を確保します。次の例では、`newimage` という名前の空の 5 MB ファイルを作成しています。

```shell
# dd if=/dev/zero of=newimage bs=1k count=5k
5120+0 records in
5120+0 records out
```

次に、そのファイルをメモリディスクに接続し、メモリディスクにラベルを付けて UFS ファイルシステムでフォーマットし、マウントしてファイルバックエンドディスクのサイズを確認します。

```shell
# mdconfig -f newimage -u 0
# bsdlabel -w md0 auto
# newfs -U md0a
/dev/md0a: 5.0MB (10224 sectors) block size 16384, fragment size 2048
        using 4 cylinder groups of 1.25MB, 80 blks, 192 inodes.
super-block backups (for fsck -b #) at:
 160, 2720, 5280, 7840
# mount /dev/md0a /mnt
# df /mnt
Filesystem 1K-blocks Used Avail Capacity  Mounted on
/dev/md0a       4710    4  4330     0%    /mnt
```

`mdconfig` を使ってファイルバックエンドまたはメモリバックエンドのファイルシステムを作成するには、いくつかのコマンドを実行する必要があります。FreeBSD には `mdmfs` も付属しており、これを使うとメモリディスクの設定、UFS ファイルシステムでのフォーマット、マウントを自動的に行ってくれます。たとえば、`dd` で *newimage* を作成した後に次の 1 つのコマンドを実行すると、上に示した `bsdlabel`、`newfs`、`mount` コマンドを順に実行するのと同じ結果になります。

```shell
# mdmfs -F newimage -s 5m md0 /mnt
```

代わりに `mdmfs` で新しいメモリベースのメモリディスクを作成するには、次の 1 つのコマンドを使います。

```shell
# mdmfs -s 5m md1 /mnt
```

ユニット番号を指定しない場合、`mdmfs` は未使用のメモリデバイスを自動的に選択します。`mdmfs` の詳細は `mdmfs(8)` を参照してください。

<a id="snapshots"></a>
## ファイルシステムのスナップショット

FreeBSD は、ソフトアップデート（soft updates）と連携して動作する機能として、ファイルシステムのスナップショットを提供しています。

UFS スナップショットを使うと、指定したファイルシステムのイメージを作成し、それを 1 つのファイルとして扱うことができます。[Z ファイルシステム（ZFS）](23-zfs.md#zfs)を使っている場合のスナップショットの利用方法については、[「スナップショットの管理」](23-zfs.md#zfs-zfs-snapshot)を参照してください。

スナップショットファイルは操作対象のファイルシステム内に作成する必要があり、ファイルシステムごとに最大 20 個までしか作成できません。有効なスナップショットはスーパーブロックに記録されるため、アンマウント／再マウントやシステム再起動をまたいでも保持されます。不要になったスナップショットは `rm(1)` で削除できます。スナップショットは任意の順序で削除できますが、別のスナップショットが解放されたブロックを参照している可能性があるため、使用していた領域がすべて回収されるとは限りません。

スナップショットファイルを最初に作成した直後、`mksnap_ffs(8)` によって変更不可の `snapshot` ファイルフラグが設定されます。`unlink(1)` はスナップショットファイルに対して例外を設けており、削除できるようになっています。

スナップショットは `mount(8)` を使って作成します。`/var` のスナップショットをファイル `/var/snapshot/snap` に作成するには、次のコマンドを使います。

```shell
# mount -u -o snapshot /var/snapshot/snap /var
```

代わりに、`mksnap_ffs(8)` を使ってスナップショットを作成することもできます。

```shell
# mksnap_ffs /var /var/snapshot/snap
```

`/var` などのファイルシステム上にあるスナップショットファイルを探すには、`find(1)` を使います。

```shell
# find /var -flags snapshot
```

作成したスナップショットには、いくつかの用途があります。

* スナップショットファイルを CD やテープに転送できるため、バックアップ目的でスナップショットを利用する管理者もいます。
* ファイルシステム整合性検査プログラム `fsck(8)` をスナップショットに対して実行できます。マウント時にファイルシステムがクリーンだったとすれば、常にクリーンで変化しない結果が得られるはずです。
* スナップショットに対して `dump(8)` を実行すると、スナップショット作成時点のファイルシステムとタイムスタンプに整合したダンプファイルを生成できます。また、`dump(8)` で `-L` を指定すると、スナップショットの取得、ダンプイメージの作成、スナップショットの削除を 1 つのコマンドで行えます。
* スナップショットをファイルシステムの凍結イメージとしてマウントできます。スナップショット `/var/snapshot/snap` を `mount(8)` でマウントするには次のように実行します。

```shell
# mdconfig -a -t vnode -o readonly -f /var/snapshot/snap -u 4
# mount -r /dev/md4 /mnt
```

これで凍結された `/var` が `/mnt` 経由で参照できるようになりました。すべての内容は、スナップショットを作成した時点とまったく同じ状態で現れます。唯一の例外は、それより前に作成されたスナップショットがサイズ 0 のファイルとして見える点です。スナップショットをアンマウントするには、次のようにします。

```shell
# umount /mnt
# mdconfig -d -u 4
```

`softupdates` とファイルシステムスナップショットに関する技術論文などの詳細は、Marshall Kirk McKusick 氏の Web サイト（[https://www.mckusick.com/](https://www.mckusick.com/)）を参照してください。

<a id="quotas"></a>
## ディスククォータ

ディスククォータを使うと、ファイルシステムごとにユーザーやグループのメンバーが割り当てられるディスク容量やファイル数を制限できます。これにより、1 人のユーザーや特定のグループが利用可能なディスク容量をすべて使い切ってしまうのを防げます。

この節では、UFS ファイルシステムでディスククォータを設定する方法を説明します。ZFS ファイルシステムでクォータを設定する方法については、[「データセット、ユーザー、グループのクォータ」](23-zfs.md#zfs-zfs-quota)を参照してください。

<a id="chapter-21-heading-35"></a>
### ディスククォータの有効化

FreeBSD カーネルがディスククォータに対応しているかを確認するには、次のようにします。

```shell
% sysctl kern.features.ufs_quota
kern.features.ufs_quota: 1
```

この例では、`1` がクォータに対応していることを示しています。値が `0` だった場合は、カスタムカーネル設定ファイルに次の行を追加し、[「FreeBSD カーネルの設定」](09-kernelconfig.md#kernelconfig)の手順に従ってカーネルを再構築してください。

```
options QUOTA
```

次に、`/etc/rc.conf` でディスククォータを有効にします。

```
quota_enable="YES"
```

通常、起動時には各ファイルシステムのクォータの整合性が `quotacheck(8)` によって検査されます。このプログラムは、クォータデータベース内のデータがファイルシステム上のデータを正しく反映していることを保証します。しかし、この処理は時間がかかり、システムの起動時間に大きく影響します。この手順をスキップするには、`/etc/rc.conf` に次の変数を追加します。

```
check_quotas="NO"
```

最後に、`/etc/fstab` を編集してファイルシステム単位でディスククォータを有効にします。あるファイルシステムでユーザー単位のクォータを有効にするには、そのファイルシステムの `/etc/fstab` エントリのオプション欄に `userquota` を追加します。例を示します。

```
/dev/da1s2g   /home    ufs rw,userquota 1 2
```

グループクォータを有効にするには、代わりに `groupquota` を使います。ユーザークォータとグループクォータの両方を有効にするには、オプションをカンマで区切ります。

```
/dev/da1s2g    /home    ufs rw,userquota,groupquota 1 2
```

既定では、クォータファイルはファイルシステムのルートディレクトリに `quota.user` および `quota.group` という名前で保存されます。詳細は `fstab(5)` を参照してください。クォータファイルの保存場所を別の場所に変更することは推奨されません。

設定が完了したらシステムを再起動します。すると `/etc/rc` が適切なコマンドを自動実行し、`/etc/fstab` で有効にしたすべてのクォータについて初期クォータファイルを作成します。

通常の運用では、`quotacheck(8)`、`quotaon(8)`、`quotaoff(8)` を手動で実行する必要はありません。ただし、動作を理解しておくためにこれらのマニュアルページには目を通しておくとよいでしょう。

<a id="chapter-21-heading-36"></a>
### クォータ制限の設定

クォータが有効になっていることを確認するには、次のコマンドを実行します。

```shell
# quota -v
```

クォータが有効な各ファイルシステムについて、ディスク使用量と現在のクォータ制限が 1 行の要約として表示されるはずです。

これで `edquota` を使ってクォータ制限を割り当てる準備が整いました。

ユーザーやグループが割り当てられるディスク容量や作成できるファイル数を制限するために、いくつかの選択肢があります。割り当てはディスク容量（ブロッククォータ）、ファイル数（inode クォータ）、またはその両方の組み合わせで制限できます。さらに、それぞれの制限はハード制限（hard limit）とソフト制限（soft limit）の 2 つに分かれています。

ハード制限は超えることができません。ユーザーがハード制限に達すると、そのユーザーはそのファイルシステム上でそれ以上領域を割り当てられなくなります。たとえば、あるファイルシステムでハード制限が 500 KB のユーザーが現在 490 KB を使用している場合、追加で割り当てられるのは 10 KB までです。さらに 11 KB を割り当てようとすると失敗します。

ソフト制限は、猶予期間（grace period、既定では 1 週間）と呼ばれる限られた時間だけ超えることができます。猶予期間を超えて制限を上回った状態が続くと、ソフト制限はハード制限へと切り替わり、それ以上の割り当てが許可されなくなります。ユーザーがソフト制限を下回る状態に戻ると、猶予期間はリセットされます。

次の例では、`test` アカウントのクォータを編集しています。`edquota` を起動すると、クォータ制限を編集するために環境変数 `EDITOR` で指定されたエディタが開きます。既定のエディタは vi に設定されています。

```shell
# edquota -u test
Quotas for user test:
/usr: kbytes in use: 65, limits (soft = 50, hard = 75)
        inodes in use: 7, limits (soft = 50, hard = 60)
/usr/var: kbytes in use: 0, limits (soft = 50, hard = 75)
        inodes in use: 0, limits (soft = 50, hard = 60)
```

クォータが有効な各ファイルシステムについて、通常 2 行が表示されます。1 行はブロック制限、もう 1 行は inode 制限を表します。クォータ制限を変更するにはこれらの値を書き換えます。たとえば、`/usr` のブロック制限をソフト制限 `500`、ハード制限 `600` に引き上げるには、該当行の値を次のように変更します。

```
/usr: kbytes in use: 65, limits (soft = 500, hard = 600)
```

新しいクォータ制限はエディタを終了した時点で有効になります。

ある範囲のユーザーに対して同じクォータ制限を設定したい場合もあります。それには、まず 1 人のユーザーに希望するクォータ制限を割り当て、次に `-p` を使ってそのクォータを指定した範囲のユーザー ID（UID）へ複製します。次のコマンドは、UID `10,000` から `19,999` までに対して同じクォータ制限を複製します。

```shell
# edquota -p test 10000-19999
```

詳細は `edquota(8)` を参照してください。

<a id="chapter-21-heading-37"></a>
### クォータ制限とディスク使用量の確認

個々のユーザーやグループのクォータとディスク使用量を確認するには `quota(1)` を使います。一般ユーザーが確認できるのは、自分自身のクォータと自分が所属するグループのクォータだけです。すべてのユーザーとグループのクォータを閲覧できるのはスーパーユーザーのみです。クォータが有効なファイルシステム全体のクォータとディスク使用量の要約を取得するには `repquota(8)` を使います。

通常、ユーザーがそのファイルシステム上でディスク領域をまったく使用していない場合、クォータ制限が割り当てられていても `quota` の出力には表示されません。そのようなファイルシステムも表示するには `-v` を使います。次に、2 つのファイルシステムにクォータ制限が設定されているユーザーに対する `quota -v` の出力例を示します。

```
Disk quotas for user test (uid 1002):
     Filesystem  usage    quota   limit   grace   files   quota   limit   grace
           /usr      65*     50      75   5days       7      50      60
       /usr/var       0      50      75               0      50      60
```

この例では、ユーザーは現在 `/usr` 上でソフト制限の 50 KB を 15 KB 上回っており、猶予期間が残り 5 日間となっています。アスタリスク `*` は、そのユーザーが現在クォータ制限を超過していることを示します。

<a id="chapter-21-heading-38"></a>
### NFS 上でのクォータ

クォータは NFS サーバ上のクォータサブシステムによって強制されます。`rpc.rquotad(8)` デーモンを使うと、NFS クライアント上の `quota` コマンドからクォータ情報を取得できるようになり、クライアント側のユーザーも自分のクォータ統計を確認できます。

NFS サーバ上で `/etc/inetd.conf` の次の行から `#` を削除して `rpc.rquotad` を有効にします。

```
rquotad/1      dgram rpc/udp wait root /usr/libexec/rpc.rquotad rpc.rquotad
```

その後、`inetd` を再起動します。

```shell
# service inetd restart
```

<a id="disks-encrypting"></a>
## ディスクパーティションの暗号化

FreeBSD は、オンライン時の不正なデータアクセスに対して優れた保護機能を備えています。OS が稼働しコンピュータの電源が入っている間は、ファイルパーミッションと[必須アクセス制御（MAC）](19-mac.md#mac)によって権限のないユーザーによるデータアクセスを防げます。しかし、攻撃者がコンピュータへ物理的にアクセスでき、ハードドライブを取り外して別のシステムへ移し、データをコピー・解析できる場合、OS が強制するパーミッションは無力になります。

攻撃者がどのような経緯でハードドライブや電源の切れたコンピュータを手に入れたとしても、FreeBSD に組み込まれている GEOM ベースの暗号化サブシステムを使えば、十分な資源を持つ執拗な攻撃者からさえファイルシステム上のデータを保護できます。個々のファイルを暗号化する方式とは異なり、組み込みの `gbde` および `geli` ユーティリティを使うとファイルシステム全体を透過的に暗号化できます。平文のデータがハードドライブのプラッタに書き込まれることは一切ありません。

この節では、FreeBSD 上に暗号化ファイルシステムを作成する方法を説明します。最初に `gbde` を使う手順を示し、続いて `geli` を使った同じ例を示します。

> **警告**: GBDE によるディスク暗号化は非推奨となり、FreeBSD 15.0 で削除されました。

<a id="chapter-21-heading-40"></a>
### gbde によるディスク暗号化

`gbde(4)` 機能の目的は、*コールド* 状態のストレージデバイスの内容へ攻撃者がアクセスすることを極めて困難にすることにあります。ただし、コンピュータが起動してストレージデバイスが接続された状態で侵害された場合や、攻撃者が有効なパスフレーズを入手した場合は、ストレージデバイスの内容を保護できません。したがって、システム稼働中の物理的なセキュリティを確保することと、暗号化機構で使うパスフレーズを守ることが重要です。

この機能は、各ディスクセクタに格納されたデータを保護するために複数の防壁を備えています。ディスクセクタの内容は CBC モードの 128 ビット AES で暗号化され、ディスク上のセクタごとに異なる AES 鍵が使われます。ユーザーが指定したパスフレーズからセクタ鍵を導出する仕組みなどの暗号設計の詳細は、`gbde(4)` を参照してください。

FreeBSD には gbde 用のカーネルモジュールが用意されており、次のコマンドで読み込めます。

```shell
# kldload geom_bde
```

カスタムカーネル設定ファイルを使う場合は、次の行が含まれていることを確認してください。

`options GEOM_BDE`

次の例では、システムに新しいハードドライブを追加し、`/private` としてマウントする単一の暗号化パーティションを作成する手順を示します。

**手順：gbde でパーティションを暗号化する**

1. 新しいハードドライブの追加

   [「ディスクの追加」](#disks-adding)の説明に従ってシステムに新しいドライブを取り付けます。この例では、新しいハードドライブのパーティションが `/dev/ad4s1c` として追加され、`/dev/ad0s1*` が既存の標準的な FreeBSD パーティションを表しているものとします。

```shell
# ls /dev/ad*
/dev/ad0        /dev/ad0s1b     /dev/ad0s1e     /dev/ad4s1
/dev/ad0s1      /dev/ad0s1c     /dev/ad0s1f     /dev/ad4s1c
/dev/ad0s1a     /dev/ad0s1d     /dev/ad4
```

2. `gbde` ロックファイルを格納するディレクトリの作成

```shell
# mkdir /etc/gbde
```

   gbde ロックファイルには、gbde が暗号化パーティションにアクセスするために必要な情報が含まれています。ロックファイルにアクセスできない場合、ソフトウェアでサポートされていない大幅な手動介入なしには暗号化パーティション内のデータを復号できなくなります。暗号化パーティションごとに別々のロックファイルを使用します。

3. `gbde` パーティションの初期化

   gbde パーティションは、使用する前に初期化する必要があります。この初期化は一度だけ行えば十分です。次のコマンドを実行すると既定のエディタが開き、テンプレート内の各種設定オプションを指定できます。UFS ファイルシステムで使う場合は、`sector_size` を 2048 に設定します。

```shell
# gbde init /dev/ad4s1c -i -L /etc/gbde/ad4s1c.lock
#
# Sector size is the smallest unit of data which can be read or written.
# Making it too small decreases performance and decreases available space.
# Making it too large may prevent filesystems from working.  512 is the
# minimum and always safe.  For UFS, use the fragment size
#
sector_size	=	2048
[...]
```

   編集内容を保存すると、データを保護するためのパスフレーズを 2 回入力するよう求められます。2 回とも同じパスフレーズを入力しなければなりません。gbde がデータを保護できるかどうかは、ひとえにパスフレーズの強度にかかっています。覚えやすく安全なパスフレーズを選ぶコツについては、[http://world.std.com/~reinhold/diceware.htm](http://world.std.com/~reinhold/diceware.html) を参照してください。

   この初期化によって gbde パーティション用のロックファイルが作成されます。この例では `/etc/gbde/ad4s1c.lock` に保存されます。`/etc/rc.d/gbde` 起動スクリプトで正しく検出されるよう、ロックファイルの名前は「.lock」で終わらなければなりません。

> **注意（CAUTION）**: ロックファイルは、暗号化パーティションの内容と一緒に *必ず* バックアップしておかなければなりません。ロックファイルが失われると、正当な所有者であっても暗号化パーティション上のデータにアクセスできなくなります。

4. 暗号化パーティションをカーネルへ接続

```shell
# gbde attach /dev/ad4s1c -l /etc/gbde/ad4s1c.lock
```

   このコマンドを実行すると、暗号化パーティションの初期化時に設定したパスフレーズの入力を求められます。すると、新しい暗号化デバイスが `/dev` 配下に `/dev/device_name.bde` として現れます。

```shell
# ls /dev/ad*
/dev/ad0        /dev/ad0s1b     /dev/ad0s1e     /dev/ad4s1
/dev/ad0s1      /dev/ad0s1c     /dev/ad0s1f     /dev/ad4s1c
/dev/ad0s1a     /dev/ad0s1d     /dev/ad4        /dev/ad4s1c.bde
```

5. 暗号化デバイス上にファイルシステムを作成

   暗号化デバイスがカーネルに接続されたら、そのデバイス上にファイルシステムを作成できます。次の例では、ソフトアップデートを有効にして UFS ファイルシステムを作成します。必ず `.bde` 拡張子が付いたパーティションを指定してください。

```shell
# newfs -U /dev/ad4s1c.bde
```

6. 暗号化パーティションのマウント

   マウントポイントを作成し、暗号化ファイルシステムをマウントします。

```shell
# mkdir /private
# mount /dev/ad4s1c.bde /private
```

7. 暗号化ファイルシステムが利用可能になったことの確認

   これで暗号化ファイルシステムが見え、利用できる状態になっているはずです。

```shell
% df -H
Filesystem        Size   Used  Avail Capacity  Mounted on
/dev/ad0s1a      1037M    72M   883M     8%    /
/devfs            1.0K   1.0K     0B   100%    /dev
/dev/ad0s1f       8.1G    55K   7.5G     0%    /home
/dev/ad0s1e      1037M   1.1M   953M     0%    /tmp
/dev/ad0s1d       6.1G   1.9G   3.7G    35%    /usr
/dev/ad4s1c.bde   150G   4.1K   138G     0%    /private
```

システムを再起動するたびに、暗号化ファイルシステムを使用する前には、カーネルへの再接続、エラー検査、マウントを手動でやり直す必要があります。これらの手順を自動化するには、`/etc/rc.conf` に次の行を追加します。

```
gbde_autoattach_all="YES"
gbde_devices="ad4s1c"
gbde_lockdir="/etc/gbde"
```

この設定を使う場合、起動時にコンソールからパスフレーズを入力する必要があります。正しいパスフレーズを入力すると、暗号化パーティションが自動的にマウントされます。その他の gbde 起動オプションについては `rc.conf(5)` を参照してください。

<a id="disks-encrypting-geli"></a>
### `geli` によるディスク暗号化

`geli` を使うことで、別の暗号化 GEOM クラスも利用できます。この制御ユーティリティはいくつかの追加機能を備えており、暗号処理に異なる方式を採用しています。主な機能は次のとおりです。

* `crypto(9)` フレームワークを利用し、暗号化ハードウェアが利用可能な場合は自動的に使用します。
* AES-XTS、AES-CBC、Camellia-CBC など複数の暗号アルゴリズムに対応しています。
* ルートパーティションを暗号化できます。暗号化されたルートパーティションにアクセスするためのパスフレーズは、システム起動時に求められます。
* 2 つの独立した鍵を使用できます。
* 単純なセクタ単位の暗号化を行うため高速です。
* マスターキーのバックアップと復元ができます。ユーザーが鍵を失っても、バックアップから鍵を復元してデータへアクセスできます。
* ワンタイムのランダム鍵でディスクを接続でき、スワップパーティションや一時ファイルシステムに便利です。

さらなる機能や使用例は `geli(8)` を参照してください。

次の例では、`/private` にマウントする暗号化プロバイダのマスターキーの一部として使うキーファイルを生成する方法を説明します。キーファイルはマスターキーの暗号化に使うランダムデータを提供し、マスターキーはさらにパスフレーズでも保護されます。プロバイダのセクタサイズは 4 KB にします。ここでは、`geli` プロバイダへの接続、ファイルシステムの作成、マウント、利用、そして最後の切り離しまでの一連の手順を示します。

**手順：`geli` でパーティションを暗号化する**

1. `geli` サポートの読み込み

   `geli` のサポートは読み込み可能なカーネルモジュールとして提供されています。起動時にモジュールを自動読み込みするように設定するには、`/boot/loader.conf` に次の行を追加します。

```
geom_eli_load="YES"
```

   今すぐカーネルモジュールを読み込むには、次のようにします。

```shell
# kldload geom_eli
```

   カスタムカーネルを使う場合は、カーネル設定ファイルに次の行が含まれていることを確認してください。

```
options GEOM_ELI
device crypto
```

2. マスターキーの生成

   次のコマンドは、すべてのデータの暗号化に使われるマスターキーを生成します。この鍵は後から変更できません。マスターキーは直接使うのではなく、1 つ以上のユーザーキーで暗号化されます。ユーザーキーは、ファイル（`/root/da2.key`）から読み取るランダムバイト列やパスフレーズの任意の組み合わせで構成されます。この例では、キーファイルのデータ元として `/dev/random` を使用します。また、性能向上のため、プロバイダ（`/dev/da2.eli`）のセクタサイズを 4 KB に設定します。

```shell
# dd if=/dev/random of=/root/da2.key bs=64 count=1
# geli init -K /root/da2.key -s 4096 /dev/da2
Enter new passphrase:
Reenter new passphrase:
```

   パスフレーズとキーファイルの両方を併用することは必須ではなく、マスターキーを保護する手段としてどちらか一方だけを使うこともできます。

   キーファイルとして「-」を指定すると、標準入力が使われます。たとえば次のコマンドでは、3 つのキーファイルを使用しています。（訳注: 原文は「3 つのキーファイルを生成する」と書いていますが、この例は既存の3つのキーファイルを指定して使うものです）

```shell
# cat keyfile1 keyfile2 keyfile3 | geli init -K - /dev/da2
```

3. 生成した鍵を使ったプロバイダの接続

   プロバイダを接続するには、キーファイル、ディスク名、およびパスフレーズを指定します。

```shell
# geli attach -k /root/da2.key /dev/da2
Enter passphrase:
```

   これにより、`.eli` 拡張子の付いた新しいデバイスが作成されます。

```shell
# ls /dev/da2*
/dev/da2  /dev/da2.eli
```

4. 新しいファイルシステムの作成

   次に、そのデバイスを UFS ファイルシステムでフォーマットし、既存のマウントポイントにマウントします。

```shell
# dd if=/dev/random of=/dev/da2.eli bs=1m
# newfs /dev/da2.eli
# mount /dev/da2.eli /private
```

   これで暗号化ファイルシステムが利用できるようになっているはずです。

```shell
# df -H
Filesystem     Size   Used  Avail Capacity  Mounted on
/dev/ad0s1a    248M    89M   139M    38%    /
/devfs         1.0K   1.0K     0B   100%    /dev
/dev/ad0s1f    7.7G   2.3G   4.9G    32%    /usr
/dev/ad0s1d    989M   1.5M   909M     0%    /tmp
/dev/ad0s1e    3.9G   1.3G   2.3G    35%    /var
/dev/da2.eli   150G   4.1K   138G     0%    /private
```

暗号化パーティションでの作業が終わり、`/private` パーティションが不要になったら、アンマウントしてカーネルから `geli` 暗号化パーティションを切り離し、コールド状態にしておくのが賢明です。

```shell
# umount /private
# geli detach da2.eli
```

起動時に `geli` 暗号化デバイスのマウントを簡素化するための `rc.d` スクリプトが用意されています。この例では、`/etc/rc.conf` に次の行を追加します。

```
geli_devices="da2"
geli_da2_flags="-k /root/da2.key"
```

これにより、`/dev/da2` がマスターキー `/root/da2.key` を使う `geli` プロバイダとして設定されます。システムをシャットダウンする前には、プロバイダがカーネルから自動的に切り離されます。起動処理の際には、プロバイダを接続する前にこのスクリプトがパスフレーズの入力を求めます。パスワードプロンプトの前後に他のカーネルメッセージが表示される場合があるため、起動処理が止まったように見えたら、他のメッセージの中にパスワードプロンプトが出ていないか注意深く確認してください。正しいパスフレーズを入力するとプロバイダが接続され、その後（通常は `/etc/fstab` のエントリに従って）ファイルシステムがマウントされます。起動時にファイルシステムをマウントする設定方法については、[「ファイルシステムのマウントとアンマウント」](03-basics.md#mount-unmount)を参照してください。

<a id="swap-encrypting"></a>
## スワップの暗号化

ディスクパーティションの暗号化と同様に、スワップ領域の暗号化も機密情報を保護するために使われます。パスワードを扱うアプリケーションを考えてみてください。それらのパスワードが物理メモリ上にとどまっている間はディスクに書き出されず、再起動すれば消去されます。しかし、FreeBSD がメモリを解放するためにメモリページをスワップアウトし始めると、パスワードが暗号化されないままディスクに書き込まれる可能性があります。スワップ領域を暗号化することは、こうした状況への有効な対策になります。

この節では、`gbde(8)` または `geli(8)` 暗号化を使って暗号化スワップパーティションを設定する方法を説明します。ここでは `/dev/ada0s1b` がスワップパーティションであるものとします。

<a id="chapter-21-heading-43"></a>
### 暗号化スワップの設定

スワップパーティションは既定では暗号化されていないため、設定を続ける前に機密データを消去しておく必要があります。現在のスワップパーティションをランダムなデータで上書きするには、次のコマンドを実行します。

```shell
# dd if=/dev/random of=/dev/ada0s1b bs=1m
```

`gbde(8)` を使ってスワップパーティションを暗号化するには、`/etc/fstab` のスワップ行に `.bde` 接尾辞を追加します。

```
# Device		Mountpoint	FStype	Options		Dump	Pass#
/dev/ada0s1b.bde	none		swap	sw		0	0
```

代わりに `geli(8)` を使ってスワップパーティションを暗号化する場合は、ワンタイム鍵でデバイスを初期化します。

```shell
# geom eli onetime -d /dev/ada0s1b
```

その後、`.eli` 接尾辞を付けたデバイスの行を `/etc/fstab` に追加します。

```
# Device		Mountpoint	FStype	Options		Dump	Pass#
/dev/ada0s1b.eli	none		swap	sw		0	0
```

既定では、`geli(8)` は鍵長 128 ビットの AES アルゴリズムを使用します。通常は既定の設定で十分です。必要に応じて、`/etc/fstab` のオプション欄でこれらの既定値を変更できます。指定できるフラグは次のとおりです。

* `aalgo`: 暗号化されたデータが改ざんされていないことを保証するためのデータ整合性検証アルゴリズム。対応しているアルゴリズムの一覧は `geli(8)` を参照してください。
* `ealgo`: データを保護するために使用する暗号化アルゴリズム。対応しているアルゴリズムの一覧は `geli(8)` を参照してください。
* `keylen`: 暗号化アルゴリズムで使用する鍵の長さ。各暗号化アルゴリズムが対応している鍵長については `geli(8)` を参照してください。
* `sectorsize`: 暗号化前にデータを分割するブロックのサイズ。セクタサイズを大きくすると性能が向上する代わりに、ストレージのオーバーヘッドが増えます。推奨サイズは 4096 バイトです。

次の例では、鍵長 128 ビットの AES-XTS アルゴリズムとセクタサイズ 4 キロバイトを使って暗号化スワップパーティションを設定しています。

```
# Device		Mountpoint	FStype	Options				Dump	Pass#
/dev/ada0s1b.eli	none		swap	sw,ealgo=AES-XTS,keylen=128,sectorsize=4096	0	0
```

<a id="chapter-21-heading-44"></a>
### 暗号化スワップの検証

システムを再起動した後、`swapinfo` を使って暗号化スワップが正しく動作しているかを確認できます。

`gbde(8)` を使っている場合は次のようになります。

```shell
% swapinfo
Device          1K-blocks     Used    Avail Capacity
/dev/ada0s1b.bde   542720        0   542720     0
```

`geli(8)` を使っている場合は次のようになります。

```shell
% swapinfo
Device          1K-blocks     Used    Avail Capacity
/dev/ada0s1b.eli   542720        0   542720     0
```

<a id="disks-hast"></a>
## 高可用性ストレージ（HAST）

ミッションクリティカルな業務アプリケーションでは高可用性が主要な要件の 1 つであり、高可用性ストレージはそのような環境における中核的な構成要素です。FreeBSD の HAST（Highly Available STorage）フレームワークを使うと、TCP/IP ネットワークで接続された物理的に離れた複数のマシン間で、同じデータを透過的に保存できます。HAST はネットワークベースの RAID1（ミラー）と考えることができ、GNU/Linux® プラットフォームで使われている DRBD® ストレージシステムに似ています。CARP など FreeBSD の他の高可用性機能と組み合わせることで、ハードウェア障害に耐性を持つ高可用性ストレージクラスタを構築できます。

HAST の主な特徴は次のとおりです。

* ローカルハードドライブ上の I/O エラーを隠蔽するために使用できる。
* FreeBSD がサポートするあらゆるファイルシステムで動作し、ファイルシステムに依存しない。
* ノードのダウンタイム中に変更されたブロックだけを同期するため、効率的かつ高速に再同期できる。
* すでに運用中の環境にも導入して、冗長性を追加できる。
* CARP、Heartbeat などのツールと組み合わせて、堅牢で耐久性のあるストレージシステムを構築できる。

この節を読むと、次の内容を学べます。

* HAST とは何か、どのように動作し、どのような機能を提供するか
* FreeBSD で HAST を設定して使う方法
* 堅牢なストレージシステムを構築するために CARP と `devd(8)` を連携させる方法

この節を読む前に、次の内容を理解しておいてください。

* UNIX® と FreeBSD の基本（[FreeBSD の基本](03-basics.md#basics)）
* ネットワークインターフェースやその他の FreeBSD コアサブシステムの設定方法（[設定とチューニング](13-config.md#config-tuning)）
* FreeBSD のネットワークに関する十分な理解（[ネットワーク通信](https://docs.freebsd.org/en/books/handbook/partiv/#network-communication)）

HAST プロジェクトは、[https://www.omc.net/](https://www.omc.net/) と [https://www.transip.nl/](https://www.transip.nl/) の支援を受けて The FreeBSD Foundation により後援されました。

<a id="chapter-21-heading-46"></a>
### HAST の動作

HAST は、*プライマリ（primary）* ノードと *セカンダリ（secondary）* ノードという 2 台の物理マシン間で、同期型のブロックレベルレプリケーションを提供します。この 2 台のマシンを合わせてクラスタと呼びます。

HAST はプライマリ-セカンダリ構成で動作するため、任意の時点でアクティブになれるのはクラスタ内のノードのうち 1 台だけです。*アクティブ* とも呼ばれるプライマリノードが、HAST 管理対象デバイスへのすべての I/O 要求を処理します。セカンダリノードはプライマリノードから自動的に同期されます。

HAST システムの物理的な構成要素は、プライマリノード上のローカルディスクと、リモートのセカンダリノード上のディスクです。

HAST はブロックレベルで同期的に動作するため、ファイルシステムやアプリケーションからは透過的に見えます。HAST は他のツールやアプリケーションが利用できるよう、`/dev/hast/` 配下に通常の GEOM プロバイダを提供します。HAST が提供するデバイスを使うことと、生のディスクやパーティションを使うこととの間に違いはありません。

書き込み、削除、フラッシュの各操作は、ローカルディスクと、TCP/IP 経由でリモートディスクの両方へ送信されます。読み取り操作は、ローカルディスクが最新でない場合や I/O エラーが発生した場合を除き、ローカルディスクから処理されます。最新でない場合やエラーが起きた場合は、読み取り操作がセカンダリノードへ送られます。

HAST は障害からの迅速な復旧を目指しています。そのため、ノード停止後の同期時間を短縮することが重要です。高速な同期を実現するため、HAST はダーティエクステント（dirty extents）のビットマップをディスク上で管理しており、初回同期を除き、通常の同期ではその部分だけを同期します。

同期の扱い方にはいくつかの方法があり、HAST では異なる同期方式に対応するために複数のレプリケーションモードを実装しています。

* *memsync*: ローカルの書き込み操作が完了し、リモートノードがデータの到着を確認応答（acknowledge）した時点で（ただし実際にデータを書き込む前に）書き込み操作を完了として報告するモードです。リモートノード上のデータは、確認応答を返した直後に書き込まれます。このモードは遅延を抑えつつ高い信頼性を確保することを目的としており、既定のモードとなっています。
* *fullsync*: ローカルの書き込みとリモートの書き込みの両方が完了した時点で、書き込み操作を完了として報告するモードです。最も安全ですが、最も低速なレプリケーションモードです。
* *async*: ローカルの書き込みが完了した時点で書き込み操作を完了として報告するモードです。最も高速ですが、最も危険なレプリケーションモードです。他のモードでは遅延が大きすぎる遠隔ノードへレプリケートする場合にのみ使用してください。

<a id="chapter-21-heading-47"></a>
### HAST の設定

HAST フレームワークは次のコンポーネントで構成されています。

* データ同期を提供する `hastd(8)` デーモン。このデーモンを起動すると、`geom_gate.ko` が自動的に読み込まれます。
* ユーザーランド管理ユーティリティ `hastctl(8)`。
* `hast.conf(5)` 設定ファイル。このファイルは `hastd` を起動する前に存在していなければなりません。

`GEOM_GATE` サポートをカーネルへ静的に組み込みたい場合は、カスタムカーネル設定ファイルに次の行を追加し、[「FreeBSD カーネルの設定」](09-kernelconfig.md#kernelconfig)の手順に従ってカーネルを再構築してください。

```
options	GEOM_GATE
```

次の例では、2 台のノードをプライマリ-セカンダリ構成で設定し、HAST を使って両者間でデータをレプリケートする方法を説明します。ノードの名前と IP アドレスは、それぞれ `hasta`（`172.16.0.1`）と `hastb`（`172.16.0.2`）とします。両ノードには HAST 運用専用の同じサイズのハードドライブ `/dev/ad6` があるものとします。HAST プール（リソースや `/dev/hast/` 配下の GEOM プロバイダとも呼ばれます）の名前は `test` とします。

HAST の設定は `/etc/hast.conf` で行います。このファイルは両ノードで同一でなければなりません。最も単純な設定は次のとおりです。

```
resource test {
	on hasta {
		local /dev/ad6
		remote 172.16.0.2
	}
	on hastb {
		local /dev/ad6
		remote 172.16.0.1
	}
}
```

より高度な設定については `hast.conf(5)` を参照してください。

> **ヒント**: `/etc/hosts` またはローカル DNS で名前解決できるように定義されていれば、`remote` 文にホスト名を指定することもできます。

両ノードに設定ファイルを用意したら、HAST プールを作成できます。両ノードで次のコマンドを実行し、ローカルディスクに初期メタデータを書き込んで `hastd(8)` を起動します。

```shell
# hastctl create test
# service hastd onestart
```

> **注**: 既存のファイルシステムがある GEOM プロバイダを使ったり、既存のストレージを HAST 管理プールへ変換したりすることは *できません*。この手順ではプロバイダ上に一定のメタデータを書き込む必要があり、既存のプロバイダにはそのための十分な空き領域がないためです。

HAST ノードの `primary` または `secondary` の役割は、管理者または Heartbeat などのソフトウェアが `hastctl(8)` を使って選択します。プライマリノード `hasta` で次のコマンドを実行します。

```shell
# hastctl role primary test
```

セカンダリノード `hastb` では次のコマンドを実行します。

```shell
# hastctl role secondary test
```

各ノードで `hastctl` を実行して結果を確認します。

```shell
# hastctl status test
```

出力の `status` 行を確認してください。もし `degraded` と表示されていれば、設定ファイルに誤りがあります。各ノードで `complete` と表示されていれば、ノード間の同期が開始されたことを意味します。`hastctl status` が報告する `dirty` エクステントが 0 バイトになると同期完了です。

次の手順では、GEOM プロバイダ上にファイルシステムを作成してマウントします。これは `primary` ノード上で実行しなければなりません。ハードドライブのサイズによっては、ファイルシステムの作成に数分かかることがあります。次の例では、`/dev/hast/test` 上に UFS ファイルシステムを作成しています。

```shell
# newfs -U /dev/hast/test
# mkdir /hast/test
# mount /dev/hast/test /hast/test
```

HAST フレームワークを適切に設定できたら、最後の手順としてシステム起動時に HAST が自動的に開始されるようにします。`/etc/rc.conf` に次の行を追加します。

```
hastd_enable="YES"
```

<a id="chapter-21-heading-48"></a>
#### フェイルオーバー設定

この例の目標は、どちらのノードが故障しても耐えられる堅牢なストレージシステムを構築することです。プライマリノードに障害が発生した場合、セカンダリノードがシームレスに引き継ぎ、ファイルシステムを検査してマウントし、データを 1 ビットも失うことなく運用を継続できるようにします。

この目的を達成するため、IP 層での自動フェイルオーバーを提供する Common Address Redundancy Protocol（CARP）を使用します。CARP を使うと、同じネットワークセグメント上の複数のホストで 1 つの IP アドレスを共有できます。[「Common Address Redundancy Protocol (CARP)」](https://docs.freebsd.org/en/books/handbook/advanced-networking/#carp)の文書に従って、クラスタの両ノードで CARP を設定してください。この例では、各ノードが独自の管理用 IP アドレスに加えて共有 IP アドレス *172.16.0.254* を持つものとします。クラスタのプライマリ HAST ノードは、プライマリ CARP ノードでもなければなりません。

前の節で作成した HAST プールは、ネットワーク上の他のホストへエクスポートできる状態になっています。共有 IP アドレス *172.16.0.254* を使い、NFS や Samba 経由でエクスポートできます。残る未解決の課題は、プライマリノードが故障した際の自動フェイルオーバーだけです。

CARP インターフェースが起動（up）または停止（down）すると、FreeBSD オペレーティングシステムは `devd(8)` イベントを生成するため、CARP インターフェースの状態変化を監視できます。CARP インターフェースの状態変化は、いずれかのノードが故障したか、オンラインに復帰したことを示します。これらの状態変化イベントを利用することで、HAST のフェイルオーバーを自動的に処理するスクリプトを実行できます。

CARP インターフェースの状態変化を捕捉するため、各ノードの `/etc/devd.conf` に次の設定を追加します。`<vhid>` は仮想ホスト ID に、`<ifname>` は関連するインターフェース名に置き換えてください。

```
notify 30 {
	match "system" "CARP";
	match "subsystem" "<vhid>@<ifname>";
	match "type" "MASTER";
	action "/usr/local/sbin/carp-hast-switch primary";
};

notify 30 {
	match "system" "CARP";
	match "subsystem" "<vhid>@<ifname>";
	match "type" "BACKUP";
	action "/usr/local/sbin/carp-hast-switch secondary";
};
```

新しい設定を有効にするため、両ノードで `devd(8)` を再起動します。

```shell
# service devd restart
```

指定したインターフェースの状態が起動または停止によって変化すると、システムが通知を生成し、`devd(8)` サブシステムが指定された自動フェイルオーバースクリプト `/usr/local/sbin/carp-hast-switch` を実行できるようになります。この設定の詳細は `devd.conf(5)` を参照してください。

自動フェイルオーバースクリプトの例を次に示します。

```
#!/bin/sh

# Original script by Freddie Cash <fjwcash@gmail.com>
# Modified by Michael W. Lucas <mwlucas@BlackHelicopters.org>
# and Viktor Petersson <vpetersson@wireload.net>

# The names of the HAST resources, as listed in /etc/hast.conf
resources="test"

# delay in mounting HAST resource after becoming primary
# make your best guess
delay=3

# logging
log="local0.debug"
name="carp-hast"

# end of user configurable stuff

case "$1" in
	primary)
		logger -p $log -t $name "Switching to primary provider for ${resources}."
		sleep ${delay}

		# Wait for any "hastd secondary" processes to stop
		for disk in ${resources}; do
			while $( pgrep -lf "hastd: ${disk} \(secondary\)" > /dev/null 2>&1 ); do
				sleep 1
			done

			# Switch role for each disk
			hastctl role primary ${disk}
			if [ $? -ne 0 ]; then
				logger -p $log -t $name "Unable to change role to primary for resource ${disk}."
				exit 1
			fi
		done

		# Wait for the /dev/hast/* devices to appear
		for disk in ${resources}; do
			for I in $( jot 60 ); do
				[ -c "/dev/hast/${disk}" ] && break
				sleep 0.5
			done

			if [ ! -c "/dev/hast/${disk}" ]; then
				logger -p $log -t $name "GEOM provider /dev/hast/${disk} did not appear."
				exit 1
			fi
		done

		logger -p $log -t $name "Role for HAST resources ${resources} switched to primary."

		logger -p $log -t $name "Mounting disks."
		for disk in ${resources}; do
			mkdir -p /hast/${disk}
			fsck -p -y -t ufs /dev/hast/${disk}
			mount /dev/hast/${disk} /hast/${disk}
		done

	;;

	secondary)
		logger -p $log -t $name "Switching to secondary provider for ${resources}."

		# Switch roles for the HAST resources
		for disk in ${resources}; do
			if ! mount | grep -q "^/dev/hast/${disk} on "
			then
			else
				umount -f /hast/${disk}
			fi
			sleep $delay
			hastctl role secondary ${disk} 2>&1
			if [ $? -ne 0 ]; then
				logger -p $log -t $name "Unable to switch role to secondary for resource ${disk}."
				exit 1
			fi
			logger -p $log -t $name "Role switched to secondary for resource ${disk}."
		done
	;;
esac
```

> **訳注**: 上記スクリプトの `secondary)` 節にある `if ! mount | grep -q ... then` の直後に本体がなく `else` が続く構文は、固定原文どおり保持しています。`/bin/sh` では空の `then` 節は構文エラーとなるため、実際に使用する場合は `if mount | grep -q "^/dev/hast/${disk} on "; then umount -f /hast/${disk}; fi`（または `:` を置く）のように修正が必要です。

要約すると、このスクリプトはノードがプライマリになったときに次の処理を実行します。

* 他方のノードで HAST プールをプライマリに昇格させる（訳注: 上記スクリプトが実際に行うのは、自ノード上での `hastctl role primary` の実行です。原文の記述はスクリプトの動作と一致しないため、ここでは原文どおりに訳したうえで補足しています）。
* HAST プール上のファイルシステムを検査する。
* プールをマウントする。

ノードがセカンダリになったときは次の処理を実行します。

* HAST プールをアンマウントする。
* HAST プールをセカンダリへ降格させる。

> **注意（CAUTION）**: これは概念実証（proof of concept）として示した単なるサンプルスクリプトです。想定しうるすべてのシナリオに対応しているわけではなく、たとえば必要なサービスの起動や停止を行うなど、必要に応じて拡張・変更して利用できます。

> **ヒント**: この例では標準の UFS ファイルシステムを使用しました。復旧に要する時間を短縮したい場合は、代わりにジャーナリングを有効にした UFS または ZFS ファイルシステムを使用できます。

高可用性ストレージはローカルで使用するだけでなく、[NFS](https://docs.freebsd.org/en/books/handbook/network-servers/#network-nfs)、[iSCSI](https://docs.freebsd.org/en/books/handbook/network-servers/#network-iscsi)、`sshfs(1)`、あるいは Ports のプログラム（たとえば `net/samba419`）を通じてネットワーク上の他のコンピュータへ共有することもできます。

追加の例を含むより詳しい情報は、[https://wiki.FreeBSD.org/HAST](https://wiki.FreeBSD.org/HAST) を参照してください。

<a id="chapter-21-heading-49"></a>
### トラブルシューティング

通常、HAST は問題なく動作します。しかし、他のあらゆるソフトウェア製品と同様、期待どおりに動作しない場合もあります。問題の原因はさまざまですが、基本原則として、クラスタのノード間で時刻が同期されていることを確認してください。

HAST のトラブルシューティングを行う際は、`hastd` に `-d` を付けて起動し、`hastd(8)` のデバッグレベルを上げる必要があります。この引数は複数回指定してデバッグレベルをさらに上げることができます。また、`hastd` をフォアグラウンドで起動する `-F` の使用も検討してください。

<a id="disks-hast-sb"></a>
#### スプリットブレイン状態からの復旧

*スプリットブレイン（Split-brain）* は、クラスタのノード同士が通信できなくなり、両方のノードがプライマリとして構成されてしまったときに発生します。これは、両方のノードがデータに対して互いに矛盾する変更を行えてしまうため危険な状態です。この問題はシステム管理者が手動で修正しなければなりません。

管理者は、どちらのノードにより重要な変更があるかを判断するか、手動でマージを行う必要があります。その後、壊れたデータを持つ側のノードで HAST に完全同期を実行させます。そのためには、再同期が必要なノード上で次のコマンドを実行します。

```shell
# hastctl role init test
# hastctl create test
# hastctl role secondary test
```
