<a id="virtualization"></a>
# 仮想化（Virtualization）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/)の「Chapter 25. Virtualization」（既存 TOC ID 24）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/virtualization/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 本リポジトリで未翻訳の章への相互参照は、公式 FreeBSD Handbook（英語版）の該当ページへリンクしています。また、掲載されているコマンド例や設定例は原文どおり保持しており、作業中の実機検証は行っていません。

<a id="virtualization-synopsis"></a>
## 概要

仮想化ソフトウェアを使うと、1 台のコンピュータ上で複数のオペレーティングシステムを同時に実行できます。
PC 向けのこうしたソフトウェアシステムでは、多くの場合、仮想化ソフトウェアを動かすホストオペレーティングシステムがあり、その上で任意の数のゲストオペレーティングシステムを実行する構成をとります。

この章を読むと、次のことがわかります。

* ホストオペレーティングシステムとゲストオペレーティングシステムの違い。
* 次の仮想化プラットフォーム上への FreeBSD のインストール方法。
  * Parallels Desktop（Apple® macOS®）
  * VMware Fusion（Apple® macOS®）
  * VirtualBox™（Microsoft® Windows®、Intel® ベース Apple® macOS®、Linux）
  * QEMU（FreeBSD）
  * bhyve（FreeBSD）
* 仮想化環境下で最高の性能を引き出すための FreeBSD システムのチューニング方法。

この章を読む前に、次の前提知識を確認してください。

* [UNIX® と FreeBSD の基本](03-basics.md#basics)を理解していること。
* [FreeBSD のインストール方法](02-bsdinstall.md#bsdinstall)を知っていること。
* [ネットワーク接続の設定方法](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)を知っていること。
* [追加のサードパーティ製ソフトウェアのインストール方法](04-ports.md#ports)を知っていること。

<a id="virtualization-guest-parallelsdesktop"></a>
## macOS® 用 Parallels Desktop 上のゲストとしての FreeBSD

Parallels Desktop for Mac® は、macOS® 10.14.6 以降を実行する Apple® Mac® コンピュータ向けの商用ソフトウェア製品です。
FreeBSD はゲストオペレーティングシステムとして完全にサポートされています。
macOS® に Parallels をインストールしたら、仮想マシンを設定し、目的のゲストオペレーティングシステムをインストールします。

<a id="virtualization-guest-parallelsdesktop-install"></a>
### Mac® 上の Parallels Desktop への FreeBSD のインストール

Parallels に FreeBSD をインストールする最初の手順は、FreeBSD インストール用の新しい仮想マシンを作成することです。

**Install Windows or another OS from a DVD or image file** を選択して先へ進みます。

![Install Windows or another OS from a DVD or image file を選択した Parallels セットアップウィザード](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd1.png)

FreeBSD のイメージファイルを選択します。

![FreeBSD イメージファイルを選択した Parallels セットアップウィザード](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd2.png)

オペレーティングシステムとして **Other** を選択します。

> **警告**: FreeBSD を選択すると、起動時にブートエラーが発生します。

![オペレーティングシステムとして Other を選択した Parallels セットアップウィザード](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd3.png)

仮想マシンに名前を付け、**Customize settings before installation** にチェックを入れます。

![インストール前に設定をカスタマイズするチェックボックスにチェックを入れた Parallels セットアップウィザード](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd4.png)

設定ウィンドウが開いたら、**Hardware** タブへ移動し、**Boot order** を選んで **Advanced** をクリックします。
次に、**BIOS** として **EFI 64-bit** を選択します。

![BIOS として EFI 64-bit を選択した Parallels セットアップウィザード](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd5.png)

**OK** をクリックし、設定ウィンドウを閉じてから **Continue** をクリックします。

![新しい仮想マシンの概要を表示した Parallels セットアップウィザード](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd6.png)

仮想マシンが自動的に起動します。
一般的な手順に従って FreeBSD をインストールしてください。

![Parallels 上で起動した FreeBSD](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/parallels-freebsd7.png)

<a id="virtualization-guest-parallels-configure"></a>
### Parallels 上での FreeBSD の設定

macOS® X 上の Parallels に FreeBSD を正常にインストールできたら、仮想化環境での動作を最適化するためにいくつかの設定を行えます。

1. ブートローダ変数の設定

   最も重要な手順は、Parallels 環境下での FreeBSD の CPU 使用率を下げるために調整可能変数 `kern.hz` の値を小さくすることです。
   これを行うには、`/boot/loader.conf` に次の行を追加します。

   ```
   kern.hz=100
   ```

   この設定を行わない場合、アイドル状態の FreeBSD Parallels ゲストはシングルプロセッサ iMac® の CPU をおよそ 15% 消費します。
   この変更により、使用率は 5% 近くに下がります。

   FreeBSD 14.0 以降をインストールしていて、それでも CPU 使用率が高い場合は、`/boot/loader.conf` に次の行も追加してください。

   ```
   debug.acpi.disabled="ged"
   ```

2. 新しいカーネルコンフィグレーションファイルの作成

   カスタムカーネルコンフィグレーションファイルからは、すべての SCSI、FireWire、および USB デバイスドライバを削除できます。
   Parallels は `ed(4)` ドライバが使用する仮想ネットワークアダプタを提供するため、`ed(4)` と `miibus(4)` 以外のすべてのネットワークデバイスもカーネルから削除できます。

3. ネットワークの設定

   最も基本的なネットワーク構成では、DHCP を使って仮想マシンをホスト Mac® と同じローカルエリアネットワークに接続します。
   これは `/etc/rc.conf` に `ifconfig_ed0="DHCP"` を追加することで実現できます。
   より高度なネットワーク設定については、[高度なネットワーク（Advanced Networking）](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)を参照してください。

<a id="virtualization-guest-vmware"></a>
## macOS® 用 VMware Fusion 上のゲストとしての FreeBSD

VMware Fusion for Mac® は、macOS® 12 以降を実行する Apple® Mac® コンピュータ向けの商用ソフトウェア製品です。
FreeBSD はゲストオペレーティングシステムとして完全にサポートされています。
macOS® に VMware Fusion をインストールしたら、仮想マシンを設定し、目的のゲストオペレーティングシステムをインストールできます。

<a id="virtualization-guest-vmware-install"></a>
### VMware Fusion への FreeBSD のインストール

最初の手順は、VMware Fusion を起動して仮想マシンライブラリ（Virtual Machine Library）を開くことです。
**+->New** をクリックして仮想マシンを作成します。

![VMware Fusion で新規仮想マシンを作成する画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd01.png)

これにより新規仮想マシンアシスタント（New Virtual Machine Assistant）が起動します。
**Create a custom virtual machine** を選択し、**Continue** をクリックして先へ進みます。

![カスタム仮想マシンの作成を選択する画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd02.png)

プロンプトが表示されたら、**Operating System** として **Other** を選択し、**Version** として **FreeBSD X** または **FreeBSD X 64-bit** のいずれかを選択します。

![オペレーティングシステムとバージョンの選択画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd03.png)

ファームウェアを選択します（UEFI を推奨）。

![ファームウェアの選択画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd04.png)

**Create a new virtual disk** を選択し、**Continue** をクリックします。

![新しい仮想ディスクの作成を選択する画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd05.png)

構成を確認し、**Finish** をクリックします。

![仮想マシン構成の確認画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd06.png)

仮想マシンの名前と保存先ディレクトリを選択します。

![仮想マシン名と保存先の選択画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd07.png)

`command+E` を押して仮想マシンの設定を開き、**CD/DVD** をクリックします。

![仮想マシン設定の CD/DVD 項目](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd08.png)

FreeBSD の ISO イメージ、または CD/DVD を選択します。

![FreeBSD ISO イメージの選択画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd09.png)

仮想マシンを起動します。

![仮想マシンの起動画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd10.png)

通常どおり FreeBSD をインストールします。

![FreeBSD のインストール画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd11.png)

インストールが完了したら、メモリ使用量や仮想マシンに割り当てる CPU 数など、仮想マシンの設定を変更できます。

> **注記**: 仮想マシンの実行中は、システムハードウェア（System Hardware）の設定を変更できません。

![仮想マシンのシステムハードウェア設定画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd12.png)

CD-ROM デバイスの状態です。
通常、CD/DVD/ISO が不要になったら仮想マシンから接続を解除します。

![CD-ROM デバイスの接続状態](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd09.png)

最後に変更するのは、仮想マシンのネットワーク接続方法です。
ホスト以外のマシンからも仮想マシンへ接続できるようにするには、**Connect directly to the physical network (Bridged)** を選択します。
一方、仮想マシンからインターネットへアクセスできればよく、ネットワーク側から仮想マシンへアクセスさせない場合は、**Share the host's internet connection (NAT)** が適しています。

![仮想マシンのネットワーク設定画面](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/vmware-freebsd13.png)

設定を変更したら、新しくインストールした FreeBSD 仮想マシンを起動します。

<a id="virtualization-guest-vmware-configure"></a>
### VMware Fusion 上での FreeBSD の設定

macOS® X 上の VMware Fusion に FreeBSD を正常にインストールできたら、仮想化環境での動作を最適化するためにいくつかの設定を行えます。

1. ブートローダ変数の設定

   最も重要な手順は、VMware Fusion 環境下での FreeBSD の CPU 使用率を下げるために調整可能変数 `kern.hz` の値を小さくすることです。
   これを行うには、`/boot/loader.conf` に次の行を追加します。

   ```
   kern.hz=100
   ```

   この設定を行わない場合、アイドル状態の FreeBSD VMware Fusion ゲストはシングルプロセッサ iMac® の CPU をおよそ 15% 消費します。
   この変更により、使用率は 5% 近くに下がります。

2. 新しいカーネルコンフィグレーションファイルの作成

   カスタムカーネルコンフィグレーションファイルからは、すべての FireWire および USB デバイスドライバを削除できます。
   VMware Fusion は `em(4)` ドライバが使用する仮想ネットワークアダプタを提供するため、`em(4)` 以外のすべてのネットワークデバイスをカーネルから削除できます。

3. ネットワークの設定

   最も基本的なネットワーク構成では、DHCP を使って仮想マシンをホスト Mac® と同じローカルエリアネットワークに接続します。
   これは `/etc/rc.conf` に `ifconfig_em0="DHCP"` を追加することで実現できます。
   より高度なネットワーク設定については、[高度なネットワーク（Advanced Networking）](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)を参照してください。

4. ドライバと open-vm-tools のインストール

   VMware 上で FreeBSD を快適に動作させるため、ドライバをインストールします。

   ```shell
   # pkg install xf86-video-vmware xf86-input-vmmouse open-vm-tools
   ```

> **注記**: `xf86` パッケージは x86 系 FreeBSD ゲストでのみ利用できます。

1. マウスの有効化

   仮想マシン内でマウスの使用に問題が報告されることがあります。
   `/boot/loader.conf` に次を追記するとマウスを有効にできる場合があります。

   ```
   # ums_load=“YES”
   ```

> **訳注**: 原文のコード例には行頭の `#` と全角引用符（`“` `”`）が含まれているため原文どおり保持しています。実際に設定を有効にする際は、`#` を外し半角の二重引用符を使って `ums_load="YES"` としてください。

<a id="virtualization-guest-virtualbox"></a>
## VirtualBox™ 上のゲストとしての FreeBSD

FreeBSD は VirtualBox™ 上のゲストとして良好に動作します。
この仮想化ソフトウェアは、FreeBSD 自身を含むほとんどの一般的なオペレーティングシステムで利用できます。

VirtualBox™ Guest Additions は次の機能を提供します。

* クリップボードの共有
* マウスポインタの統合
* ホストとの時刻同期
* ウィンドウのスケーリング
* シームレスモード

Xorg を実行する場合は、Guest Additions をインストールする前に、仮想マシン設定の Display セクションにある Screen 設定を **VBoxSVGA** に設定してください。
VMSVGA は VMware ゲスト向けであり FreeBSD では使用できないため、選択しないでください。
VMSVGA を選ぶと Xorg が正常に動作しません。
VBoxSVGA にはこの問題がなく、X11 をエラーなく実行できます。

> **注記**: 以下のコマンドは FreeBSD ゲスト側で実行します。

FreeBSD ゲストに `emulators/virtualbox-ose-additions` パッケージまたは port をインストールします。
port からインストールする場合は次のように実行します。

```shell
# cd /usr/ports/emulators/virtualbox-ose-additions && make install clean
```

`/etc/rc.conf` に次の行を追加します。

```
vboxguest_enable="YES"
vboxservice_enable="YES"
```

`ntpd(8)` または `ntpdate(8)` を使用する場合は、ホストとの時刻同期を無効化します。

```
vboxservice_flags="--disable-timesync"
```

Xorg は `vboxvideo` ドライバを自動的に認識します。
`/etc/X11/xorg.conf` に手動で記述することもできます。

```
Section "Device"
	Identifier "Card0"
	Driver "vboxvideo"
	VendorName "InnoTek Systemberatung GmbH"
	BoardName "VirtualBox Graphics Adapter"
EndSection
```

`vboxmouse` ドライバを使用するには、`/etc/X11/xorg.conf` のマウスセクションを調整します。

```
Section "InputDevice"
	Identifier "Mouse0"
	Driver "vboxmouse"
EndSection
```

ホストと仮想マシン間でファイルをやり取りするための共有フォルダは、`mount_vboxvfs` を使ってマウントすることでアクセスできます。
共有フォルダはホスト側で VirtualBox GUI または `vboxmanage` を使って作成できます。
たとえば、_BSDBox_ という名前の仮想マシン向けに、`/mnt/bsdboxshare` を _myshare_ という名前で共有フォルダとして作成するには、次のように実行します。

```shell
# vboxmanage sharedfolder add 'BSDBox' --name myshare --hostpath /mnt/bsdboxshare
```

共有フォルダ名にスペースを含めてはいけない点に注意してください。
ゲストシステム内から共有フォルダをマウントするには、次のように実行します。

```shell
# mount_vboxvfs -w myshare /mnt
```

<a id="virtualization-host-virtualbox"></a>
## VirtualBox™ をホストとする FreeBSD

VirtualBox™ は活発に開発されている完全な仮想化パッケージであり、Windows®、macOS®、Linux®、FreeBSD などほとんどのオペレーティングシステムで利用できます。
Windows® ゲストと UNIX® 系ゲストのどちらも同じように動作させることができます。
オープンソースソフトウェアとして公開されていますが、クローズドソースのコンポーネントが別の拡張パック（extension pack）として提供されています。
これらのコンポーネントには USB 2.0 デバイスのサポートなどが含まれます。
詳細は [VirtualBox™ Wiki の Downloads ページ](http://www.virtualbox.org/wiki/Downloads)を参照してください。
現時点では、これらの拡張機能は FreeBSD 向けには提供されていません。

<a id="virtualization-virtualbox-install"></a>
### VirtualBox™ のインストール

VirtualBox™ は FreeBSD のパッケージまたは port として `emulators/virtualbox-ose` に用意されています。
port を使ってインストールするには、次のコマンドを実行します。

```shell
# cd /usr/ports/emulators/virtualbox-ose
# make install clean
```

port の設定メニューにある便利なオプションの 1 つに、`GuestAdditions` プログラム群があります。
これにより、ゲストオペレーティングシステムでさまざまな便利機能（ホストとゲスト間で特別なキーボードショートカットを押さずにマウスを共有できるマウスポインタ統合や、特に Windows® ゲストでの高速なビデオ描画など）を利用できるようになります。
Guest Additions は、ゲストのインストール完了後に **Devices** メニューから利用できます。

VirtualBox™ を初めて起動する前に、いくつかの設定変更が必要です。
port をインストールすると `/boot/modules` にカーネルモジュールが配置されるため、実行中のカーネルへ読み込む必要があります。

```shell
# kldload vboxdrv
```

再起動後も常にこのモジュールが読み込まれるようにするには、`/boot/loader.conf` に次の行を追加します。

```
vboxdrv_load="YES"
```

ブリッジネットワークやホストオンリーネットワークを可能にするカーネルモジュールを使用するには、`/etc/rc.conf` に次の行を追加してコンピュータを再起動します。

```
vboxnet_enable="YES"
```

VirtualBox™ のインストール時に `vboxusers` グループが作成されます。
VirtualBox™ にアクセスする必要があるユーザーは、すべてこのグループのメンバーとして追加する必要があります。
新しいメンバーを追加するには `pw` を使用できます。

```shell
# pw groupmod vboxusers -m username
```

`/dev/vboxnetctl` の既定のパーミッションは制限が厳しいため、ブリッジネットワークを使う場合は変更する必要があります。

```shell
# chown root:vboxusers /dev/vboxnetctl
# chmod 0660 /dev/vboxnetctl
```

このパーミッション変更を永続化するには、`/etc/devfs.conf` に次の行を追加します。

```
own     vboxnetctl root:vboxusers
perm    vboxnetctl 0660
```

VirtualBox™ を起動するには、Xorg セッションから次のように入力します。

```shell
% VirtualBox
```

VirtualBox™ の設定や使用方法の詳細は、[公式 Web サイト](http://www.virtualbox.org)を参照してください。
FreeBSD 固有の情報やトラブルシューティング手順については、[FreeBSD Wiki の該当ページ](http://wiki.FreeBSD.org/VirtualBox)を参照してください。

<a id="virtualization-virtualbox-usb-support"></a>
### VirtualBox™ の USB サポート

VirtualBox™ は、USB デバイスをゲストオペレーティングシステムへパススルーするように設定できます。
USB 2.0 および 3.0 デバイスに対応する拡張パックが FreeBSD で利用できるようになるまでは、OSE 版のホストコントローラは USB 1.1 デバイスのエミュレーションに制限されます。

マシンに接続された USB デバイスを VirtualBox™ が認識できるようにするには、ユーザーが `operator` グループのメンバーである必要があります。

```shell
# pw groupmod operator -m username
```

次に、`/etc/devfs.rules` に以下の内容を追加します（ファイルが存在しない場合は新規作成します）。

```
[system=10]
add path 'usb/*' mode 0660 group operator
```

これらの新しいルールを読み込むため、`/etc/rc.conf` に次の行を追加します。

```
devfs_system_ruleset="system"
```

その後、devfs を再起動します。

```shell
# service devfs restart
```

これらの変更を有効にするため、ログインセッションと VirtualBox™ を再起動し、必要に応じて USB フィルタを作成してください。

<a id="virtualization-virtualbox-host-dvd-cd-access"></a>
### VirtualBox™ のホスト DVD/CD アクセス

ゲストからホストの DVD/CD ドライブへアクセスするには、物理ドライブを共有します。
VirtualBox™ 内では、仮想マシンの Settings にある Storage ウィンドウから設定します。
必要であれば、最初に空の IDE CD/DVD デバイスを作成します。
次に、仮想 CD/DVD ドライブ選択のポップアップメニューからホストドライブ（Host Drive）を選びます。
すると `Passthrough` というチェックボックスが表示されます。これを有効にすると、仮想マシンがハードウェアを直接利用できるようになります。
たとえば、音楽 CD の再生やライティング機能はこのオプションを選択した場合にのみ動作します。

ユーザーが VirtualBox™ の DVD/CD 機能を使用できるようにするには、`/dev/xpt0`、`/dev/cdN`、および `/dev/passN` へのアクセス権が必要です。
通常は、ユーザーを `operator` グループのメンバーにすることで対応します。
これらのデバイスへのパーミッションは、`/etc/devfs.conf` に次の行を追加して調整する必要があります。

```
perm cd* 0660
perm xpt0 0660
perm pass* 0660
```

```shell
# service devfs restart
```
