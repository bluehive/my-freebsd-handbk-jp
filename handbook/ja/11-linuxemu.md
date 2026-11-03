<a id="linuxemu"></a>
# 第11章 Linuxバイナリ互換機能

> **状態:** 意訳ドラフト。固定原文の全節・コマンド・設定・出力例を照合しています。Linuxアプリや各ユーザーランドの実機検証は未実施です。
> **原文:** [Linux Binary Compatibility](https://docs.freebsd.org/en/books/handbook/linuxemu/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/11-linuxemu.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **章番号:** 本リポジトリでは第11章、固定上流では第12章です。
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

原文にはCentOS 7、Ubuntuの古いリリース、libc.so.4などの歴史的な例もあります。サポート状況と利用する版の依存関係を確認し、異なるディストリビューションのファイルやリポジトリを無計画に混在させないでください。`#` はroot、`%` は一般ユーザーのプロンプトです。

<a id="linuxemu-synopsis"></a>
## この章で行うこと

FreeBSDは、Linuxバイナリを変更せず動かすための任意の互換機能を備えます。一般にLinuxulatorと呼ばれ、x86の32／64ビットとAArch64で利用できます。

LinuxのすべてのOS機能が実装されるわけではありません。特にハードウェアやシステム管理に密接なcgroups・namespacesなどに制約があります。[追加ソフトウェアの導入](04-ports.md)を理解したうえで、互換機能の有効化、Linuxの共有ライブラリとアプリの導入、実装上の仕組みを学びます。

<a id="linuxemu-lbc-install"></a>
## Linux ABIを有効にする

既定では `linux(4)` の互換機能は無効です。起動時に有効にします。

```shell
# sysrc linux_enable="YES"
```

再起動せず使い始めるには次を実行します。

```shell
# service linux start
```

静的リンクのLinuxバイナリなら、これだけで動作する場合があります。linuxサービスは必要なカーネルモジュールを読み込み、Linuxアプリが期待するファイルシステムを `/compat/linux` 配下へマウントします。アプリは通常のFreeBSDプログラムのように起動でき、プロセスとして追跡・デバッグできます。

現時点の内容を確認します。

```shell
# ls -l /compat/linux/
```

原文例ではdev・proc・sysだけが用意されています。

```text
total 1
dr-xr-xr-x  13 root  wheel  512 Apr 11 19:12 dev
dr-xr-xr-x   1 root  wheel    0 Apr 11 21:03 proc
dr-xr-xr-x   1 root  wheel    0 Apr 11 21:03 sys
```

<a id="linux-userlands"></a>
## Linuxユーザーランドを用意する

動的にリンクする通常のLinuxソフトウェアには、ABIだけでなくLinux側のライブラリなどが必要です。Portsに用意されたアプリならpkgが必要なユーザーランドも依存先として導入できます。

Sublime Text 4を依存ライブラリとともに入れる原文例です。

```shell
# pkg install linux-sublime-text4
```

<a id="linuxemu-rockylinux"></a>
### Rocky Linuxのベースをパッケージで入れる

Rocky Linux 9由来のユーザーランドを導入します。

```shell
# pkg install linux_base-rl9
```

`emulators/linux_base-rl9` は `/compat/linux` へ配置します。

```shell
# ls -l /compat/linux/
```

導入後の原文例です。ライブラリや設定などが追加されます。

```text
total 36
drwxr-xr-x   2 root wheel  512 Oct  9 17:28 afs
lrwxr-xr-x   1 root wheel    7 May 16  2022 bin -> usr/bin
drwxr-xr-x   3 root wheel  512 Oct  9 17:28 dev
drwxr-xr-x  24 root wheel 1536 Oct  9 17:28 etc
lrwxr-xr-x   1 root wheel    7 May 16  2022 lib -> usr/lib
lrwxr-xr-x   1 root wheel    9 May 16  2022 lib64 -> usr/lib64
drwxr-xr-x   2 root wheel  512 Oct  9 17:28 opt
drwxr-xr-x   2 root wheel  512 Oct  9 17:28 proc
lrwxr-xr-x   1 root wheel    8 Oct  1 03:11 run -> /var/run
lrwxr-xr-x   1 root wheel    8 May 16  2022 sbin -> usr/sbin
drwxr-xr-x   2 root wheel  512 Oct  9 17:28 srv
drwxr-xr-x   2 root wheel  512 Oct  9 17:28 sys
drwxr-xr-x   8 root wheel  512 Oct  9 17:28 usr
drwxr-xr-x  16 root wheel  512 Oct  9 17:28 var
```

<a id="linuxemu-centos"></a>
### CentOSのベース：旧来の方法

> **原文の警告:** `emulators/linux_base-c7` は上流の終了に伴って非推奨となり、セキュリティ更新を受けません。原文は32ビット互換性が必要な場合を除き、[Rocky Linuxのベース](#linuxemu-rockylinux)を推奨しています。

以下は旧来の手順です。

```shell
# pkg install linux_base-c7
```

CentOS 7由来のファイルを `/compat/linux` へ置きます。

```shell
# ls -l /compat/linux/
```

配置の原文例です。

```text
total 30
lrwxr-xr-x   1 root  wheel    7 Apr 11  2018 bin -> usr/bin
drwxr-xr-x  13 root  wheel  512 Apr 11 21:10 dev
drwxr-xr-x  25 root  wheel   64 Apr 11 21:10 etc
lrwxr-xr-x   1 root  wheel    7 Apr 11  2018 lib -> usr/lib
lrwxr-xr-x   1 root  wheel    9 Apr 11  2018 lib64 -> usr/lib64
drwxr-xr-x   2 root  wheel    2 Apr 11 21:10 opt
dr-xr-xr-x   1 root  wheel    0 Apr 11 21:25 proc
lrwxr-xr-x   1 root  wheel    8 Feb 18 02:10 run -> /var/run
lrwxr-xr-x   1 root  wheel    8 Apr 11  2018 sbin -> usr/sbin
drwxr-xr-x   2 root  wheel    2 Apr 11 21:10 srv
dr-xr-xr-x   1 root  wheel    0 Apr 11 21:25 sys
drwxr-xr-x   8 root  wheel    9 Apr 11 21:10 usr
drwxr-xr-x  16 root  wheel   17 Apr 11 21:10 var
```

<a id="linuxemu-debootstrap"></a>
### debootstrapでDebian／Ubuntuを用意する

Linuxの共有ライブラリを用意する別の方法が `sysutils/debootstrap` です。DebianやUbuntuのユーザーランド一式を構築できます。

```shell
# pkg install debootstrap
```

先にLinux ABIを有効にします。原文ではUbuntu jammyを `/compat/ubuntu` に作る例を使います。

```shell
# debootstrap jammy /compat/ubuntu
```

`/compat/linux` に作ることも技術的には可能ですが、既存のLinuxベースパッケージと衝突するおそれがあります。ディストリビューションや版に対応する別ディレクトリを使います。

取得・検証・初期設定が進む原文例です。

```text
I: Retrieving InRelease
I: Checking Release signature
I: Valid Release signature (key id F6ECB3762474EDA9D21B7022871920D1991BC93C)
I: Retrieving Packages
I: Validating Packages
I: Resolving dependencies of required packages...
I: Resolving dependencies of base packages...
I: Checking component main on http://archive.ubuntu.com/ubuntu...
[...]
I: Configuring console-setup...
I: Configuring kbd...
I: Configuring ubuntu-minimal...
I: Configuring libc-bin...
I: Configuring ca-certificates...
I: Base system installed successfully.
```

続いて必要なマウントを `/etc/fstab` に設定します。ホームを共有しX11アプリを使う場合の例は次のとおりです。`/home` と `/tmp` はnullfsで共有します。

```shell
# Device        Mountpoint              FStype          Options                      Dump    Pass#
devfs           /compat/ubuntu/dev      devfs           rw,late                      0       0
tmpfs           /compat/ubuntu/dev/shm  tmpfs           rw,late,size=1g,mode=1777    0       0
fdescfs         /compat/ubuntu/dev/fd   fdescfs         rw,late,linrdlnk             0       0
linprocfs       /compat/ubuntu/proc     linprocfs       rw,late                      0       0
linsysfs        /compat/ubuntu/sys      linsysfs        rw,late                      0       0
/tmp            /compat/ubuntu/tmp      nullfs          rw,late                      0       0
/home           /compat/ubuntu/home     nullfs          rw,late                      0       0
```

設定したlateマウントを適用します。

```shell
# mount -al
```

ユーザーランドへ入ります。

```shell
# chroot /compat/ubuntu /bin/bash
```

Linux環境として報告される識別情報を確認します。

```shell
# uname -s -r -m
```

```text
Linux 5.15.0 x86_64
```

> **訳注:** このLinuxの版表示は互換環境が報告する値です。別のLinuxカーネルを起動したわけではなく、FreeBSDのカーネル上で動きます。

chroot内では通常のUbuntuに近い操作ができますが、systemdは動作せず、原文はserviceコマンドによる操作を案内しています。

不足するAPTリポジトリは `/compat/ubuntu/etc/apt/sources.list` に追加します。amd64向けの原文例です。

```text
deb http://archive.ubuntu.com/ubuntu jammy main universe restricted multiverse
deb http://security.ubuntu.com/ubuntu/ jammy-security universe multiverse restricted main
deb http://archive.ubuntu.com/ubuntu jammy-backports universe multiverse restricted main
deb http://archive.ubuntu.com/ubuntu jammy-updates universe multiverse restricted main
```

arm64向けとして原文にある別の例です。

```text
deb http://ports.ubuntu.com/ubuntu-ports bionic main universe restricted multiverse
```

> **訳注:** amd64例はjammy、arm64例はbionicという別リリースです。これらは固定原文の例で、同じユーザーランドへ混ぜる手順ではありません。構築したリリースとアーキテクチャに合う取得元へ揃えます。

<a id="linuxemu-advanced"></a>
## 追加の設定

Linux互換機能に関するsysctl一覧は `linux(4)` を参照します。アプリによって必要なファイルシステムが異なります。通常は `/etc/rc.d/linux` がマウントしますが、自動処理を止める設定は次です。

```text
sysrc linux_mounts_enable="NO"
```

rcスクリプトのマウントは、別のchrootやjail内からはそのまま利用できません。必要ならその環境用にfstabへ記述します。

```text
devfs      /compat/linux/dev      devfs      rw,late                    0  0
tmpfs      /compat/linux/dev/shm  tmpfs      rw,late,size=1g,mode=1777  0  0
fdescfs    /compat/linux/dev/fd   fdescfs    rw,late,linrdlnk           0  0
linprocfs  /compat/linux/proc     linprocfs  rw,late                    0  0
linsysfs   /compat/linux/sys      linsysfs   rw,late                    0  0
```

32／64ビット両方に対応する現在の互換機能を、独自カーネルへ静的に組み込む方法はないと、原文は説明しています。

<a id="linuxemu-libs-manually"></a>
### 不足する共有ライブラリを手動で置く

debootstrapで作った環境では、前節の方法とそのディストリビューションの管理方式を使います。ここは従来の `/compat/linux` へ手動でライブラリを補う説明です。

不足を報告するバイナリがあれば、**同じCPUアーキテクチャのLinuxシステム**でlddを使い、必要な共有ライブラリを調べます。Doomが入ったLinuxでの原文例です。

```shell
% ldd linuxdoom
```

```text
libXt.so.3 (DLL Jump 3.1) => /usr/X11/lib/libXt.so.3.1.0
libX11.so.3 (DLL Jump 3.1) => /usr/X11/lib/libX11.so.3.1.0
libc.so.4 (DLL Jump 4.5pl26) => /lib/libc.so.4.6.29
```

出力の最後の列のファイルを、FreeBSDの `/compat/linux` を先頭に付けた場所へコピーし、最初の列の名前から実体へのシンボリックリンクを作ります。

```text
/compat/linux/usr/X11/lib/libXt.so.3.1.0
/compat/linux/usr/X11/lib/libXt.so.3 -> libXt.so.3.1.0
/compat/linux/usr/X11/lib/libX11.so.3.1.0
/compat/linux/usr/X11/lib/libX11.so.3 -> libX11.so.3.1.0
/compat/linux/lib/libc.so.4.6.29
/compat/linux/lib/libc.so.4 -> libc.so.4.6.29
```

同じ主要リビジョンのライブラリがあれば、少し古い副版でも利用できる場合があります。原文の既存ファイルの例です。

```text
/compat/linux/lib/libc.so.4.6.27
/compat/linux/lib/libc.so.4 -> libc.so.4.6.27
```

要求された、少し新しい版の例です。

```text
libc.so.4 (DLL Jump 4.5pl26) -> libc.so.4.6.29
```

原文は、リンク先も更新すれば新しい方へ置き換えられると説明しています。

```text
/compat/linux/lib/libc.so.4.6.29
/compat/linux/lib/libc.so.4 -> libc.so.4.6.29
```

これは古いlibc.so.4の例です。現在のライブラリのABIやシンボルの互換性を、末尾の数字だけで判断するものではありません。必要な一式が揃うと、新しいアプリのたびに追加する作業は減ります。

<a id="chapter-11-heading-10"></a>
### ELFファイルをLinux用として識別させる

カーネルはELFヘッダーのbrand、既知のインタープリターのパス、ELF notesなどでLinuxバイナリを識別します。原文は既定でbrandのないELFもLinuxとみなすと説明しています。

識別できない場合の例です。

```shell
% ./my-linux-elf-binary
```

```text
ELF binary type not known
Abort
```

`brandelf(1)` でLinux用だと示せます。

```shell
% brandelf -t Linux my-linux-elf-binary
```

<a id="chapter-11-heading-11"></a>
### RPM形式のアプリを展開する

`archivers/rpm4` を導入した後、rootでRPMの内容を `/compat/linux` へ展開する原文例です。

```shell
# cd /compat/linux
# rpm2cpio < /path/to/linux.archive.rpm | cpio -id
```

必要なら導入したELFへbrandelfを使います。この方法はパッケージ管理された導入ではないため、原文はきれいにアンインストールできなくなる点を注意しています。

<a id="chapter-11-heading-12"></a>
### 名前解決を調整する

DNSが使えず、次のような古いリゾルバーのエラーが出る場合の原文の対処です。

```text
resolv+: "bind" is an invalid keyword resolv+:
"hosts" is an invalid keyword
```

`/compat/linux/etc/host.conf` を設定します。

```text
order hosts, bind
multi on
```

hostsを先、DNSを後に使います。この互換側のファイルがない場合、ホストの `/etc/host.conf` を探してエラーになることがあります。DNSサーバーをresolv.confに設定していなければbindを除きます。これは原文の対象とするリゾルバー向けの説明で、ディストリビューション固有の名前解決設定とも照合します。

<a id="linuxemu-misc"></a>
### 実装の詳しい説明

Linuxバイナリ互換機能の実装は、別記事の [Linux emulation in FreeBSD](https://docs.freebsd.org/en/articles/linux-emulation/)でも説明されています。
