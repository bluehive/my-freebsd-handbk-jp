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

<a id="qemu-virtualization-host-guest"></a>
## FreeBSD 上での QEMU による仮想化

[QEMU](https://www.qemu.org) は、完全にオープンソースソフトウェアとして開発されている汎用マシンエミュレータ兼仮想化ソフトウェアです。
大きく活発なコミュニティによって開発されており、FreeBSD、OpenBSD、NetBSD をはじめとする多くのオペレーティングシステムに対応しています。

[QEMU ドキュメント](https://www.qemu.org/docs/master/)より:

* QEMU はいくつかの異なる方法で使用できます。
  最も一般的なのはシステムエミュレーション（System Emulation）で、ゲスト OS を実行するためにマシン全体（CPU、メモリ、エミュレートされたデバイス）の仮想モデルを提供します。
  このモードでは CPU を完全にエミュレートすることもできますし、`KVM`、`Xen`、`Hypervisor.Framework` などのハイパーバイザと連携してゲストをホスト CPU 上で直接実行することもできます。

* QEMU の 2 つ目の利用方法はユーザーモードエミュレーション（User Mode Emulation）で、ある CPU 向けにコンパイルされたプロセスを別の CPU 上で起動できます。
  このモードでは CPU は常にエミュレートされます。

* QEMU はさらに、`qemu-img(1)` ディスクイメージユーティリティのようなスタンドアロンのコマンドラインユーティリティも多数提供しており、ディスクイメージの作成・変換・変更を行えます。

QEMU は `Arm™`、`i386`、`x86_64`、`MIPS™`、`s390X`、`SPARC™`（Sparc™ および Sparc64™）など幅広いアーキテクチャをエミュレートできます。
[QEMU System Emulator Targets](https://www.qemu.org/docs/master/system/targets.html#system-targets-ref) の一覧は定期的に更新されています。

この節では、FreeBSD 上でシステムエミュレーションおよびユーザーモードエミュレーションの両方に QEMU を使用する方法を説明し、QEMU コマンドおよびコマンドラインユーティリティの使用例を示します。

<a id="qemu-installing-qemu-software"></a>
### QEMU ソフトウェアのインストール

QEMU は FreeBSD のパッケージまたは port として `emulators/qemu` に用意されています。
パッケージビルドにはほとんどのユーザーにとって妥当なオプションと既定値が含まれており、推奨されるインストール方法です。

```shell
# pkg install qemu
```

パッケージのインストールにはいくつかの依存パッケージが含まれます。
インストールが完了したら、最もよく使用するホスト版の QEMU へのシンボリックリンクを作成します。
ホストが Intel™ または AMD™ の 64 ビットシステムであれば、次のようになります。

```shell
# ln -s /usr/local/bin/qemu-system-x86_64 /usr/local/bin/qemu
```

一般ユーザーとして次のコマンドを実行し、インストールをテストします。

```shell
% qemu
```

これにより QEMU のウィンドウが開き、ハードディスク、フロッピーディスク、DVD/CD、PXE からの起動が試みられます。
まだ何も設定していないためいくつかエラーが出力され、[図 1](#qemu-nullboot) のように「No bootable device」と表示されて止まります。
しかし、これによって QEMU ソフトウェアが正しくインストールされていることを確認できます。

<a id="qemu-nullboot"></a>
**図 1. 起動可能なイメージがない状態の QEMU**

![起動可能なイメージがない状態の QEMU](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd01.png)

<a id="qemu-virtual-machine-install"></a>
### 仮想マシンのインストール

> **注記**: QEMU は非常に活発に開発されています。
> バージョンによって機能やコマンドオプションが変更されることがあります。
> この節では、QEMU バージョン 9.0.1（2024 年夏）で作成した例を示しています。
> 不明な点がある場合は、常に [QEMU Documentation](https://www.qemu.org/docs/master/)、特にサポートされるビルドプラットフォーム・エミュレーション・非推奨機能・削除された機能へのリンクがある [About QEMU](https://www.qemu.org/docs/master/about/index.html) ページを参照してください。

以下の手順に従って、"**left**" と "**right**" という名前の 2 つの仮想マシンを作成します。
ほとんどのコマンドは root 権限なしで実行できます。

1. QEMU 作業用のテスト環境を作成します。

   ```shell
   % mkdir -p ~/QEMU  ~/QEMU/SCRIPTS  ~/QEMU/ISO  ~/QEMU/VM
   ```

   `SCRIPTS` ディレクトリは起動スクリプトやユーティリティ用です。
   `ISO` ディレクトリはゲストのブート用 ISO イメージ用です。
   `VM` ディレクトリには仮想マシンイメージ（`VM`）を配置します。

2. FreeBSD の最近の版を `~/QEMU/ISO` にダウンロードします。

   ```shell
   % cd ~/QEMU/ISO
   % fetch https://download.freebsd.org/releases/ISO-IMAGES/14.1/FreeBSD-14.1-RELEASE-amd64-bootonly.iso
   ```

   ダウンロードが完了したら、短縮用のシンボリックリンクを作成します。
   このリンクは後述の起動スクリプトで使用します。

   ```shell
   % ln -s FreeBSD-14.1-RELEASE-amd64-bootonly.iso  fbsd.iso
   ```

3. 仮想マシンを配置するディレクトリ（`~/QEMU/VM`）へ移動します。
   `qemu-img(1)` を実行して、"left" 仮想マシン用のディスクイメージを作成します。

   ```shell
   % cd ~/QEMU/VM
   % qemu-img create -f raw  left.img   15G
   ```

   QEMU の `raw` 形式は性能重視で設計されています。
   形式が単純でオーバーヘッドがないため高速であり、特に高性能・高スループットが求められる場面に適しています。
   スナップショットなどの追加機能が不要で最大性能を引き出したい場合に使用します。
   この形式は後述の "left" 仮想マシン用スクリプトで使用します。

   もう 1 つの形式は `qcow2` で、ディスク領域の管理に QEMU の「コピーオンライト（copy on write）」技術を使用します。
   この方式では最初から 15G 全体を確保する必要はなく、仮想マシンが直接管理するスタブ版だけを作成します。
   仮想マシンが書き込むにつれてディスクは動的に拡張されます。
   この形式はスナップショット、圧縮、暗号化に対応しています。
   開発やテストなど、これらの高度な機能が必要な場面で使用します。
   この形式は後述の "right" 仮想マシン用スクリプトで使用します。

   再び `qemu-img(1)` を実行し、`qcow2` を用いて "right" 仮想マシン用のディスクイメージを作成します。

   ```shell
   % qemu-img create -f qcow2 -o preallocation=full,cluster_size=512K,lazy_refcounts=on right.qcow2 20G
   ```

   ファイルの実際のサイズを確認するには次のように実行します。

   ```shell
   % du -Ah right.qcow2
   ```

4. 次のコマンドで両方の仮想マシン向けにネットワークを設定します。
   この例ではホストのネットワークインターフェースは `em0` です。
   必要に応じて、ホストシステムのインターフェースに合わせて変更してください。
   QEMU ゲスト仮想マシンが通信できるようにするため、ホストマシンを再起動するたびにこの設定を行う必要があります。

   ```shell
   # ifconfig tap0 create
   # ifconfig tap1 create
   # sysctl net.link.tap.up_on_open=1
   net.link.tap.up_on_open: 0 -> 1
   # sysctl net.link.tap.user_open=1
   net.link.tap.user_open: 0 -> 1
   # ifconfig bridge0 create
   # ifconfig bridge0 addm tap0 addm tap1 addm em0
   # ifconfig bridge0 up
   ```

   上記のコマンドは 2 つの `tap(4)` デバイス（`tap0`、`tap1`）と 1 つの `if_bridge(4)` デバイス（`bridge0`）を作成します。
   次に、`tap` デバイスとローカルホストのインターフェース（`em0`）を `bridge` に追加し、一般ユーザーが tap デバイスを開けるように 2 つの `sysctl(8)` エントリを設定します。
   これらのコマンドにより、仮想マシンがホスト上のネットワークスタックと通信できるようになります。

5. `~/QEMU/SCRIPTS` へ移動し、次のスクリプトを使って最初の仮想マシン "left" を起動します。
   このスクリプトは QEMU の raw ディスク形式を使用します。

   ```
   /usr/local/bin/qemu-system-x86_64  -monitor none \
     -cpu qemu64 \
     -vga std \
     -m 4096 \
     -smp 4   \
     -cdrom ../ISO/fbsd.iso \
     -boot order=cd,menu=on \
     -blockdev driver=file,aio=threads,node-name=imgleft,filename=../VM/left.img \
     -blockdev driver=raw,node-name=drive0,file=imgleft \
     -device virtio-blk-pci,drive=drive0,bootindex=1  \
     -netdev tap,id=nd0,ifname=tap0,script=no,downscript=no,br=bridge0 \
     -device e1000,netdev=nd0,mac=02:20:6c:65:66:74 \
     -name \"left\"
   ```

> **ヒント**: 上記の内容をファイル（たとえば `left.sh`）に保存し、`% /bin/sh left.sh` と実行するだけで起動できます。

QEMU は別ウィンドウで仮想マシンを起動し、[図 2](#qemu-newboot-loader-menu) のように FreeBSD の ISO を起動します。
`-cpu` や `-boot` などのすべてのコマンドオプションの詳細は、QEMU の man ページ `qemu(1)` に記載されています。

<a id="qemu-newboot-loader-menu"></a>
**図 2. FreeBSD ブートローダメニュー**

![FreeBSD ローダメニュー](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd02.png)

> **ヒント**: QEMU コンソールウィンドウ内でマウスをクリックすると、[図 3](#qemu-grab) のように QEMU がマウスを「捕捉（grab）」します。
> マウスを解放するには `Ctl`+`Alt`+`G` を押してください。

<a id="qemu-grab"></a>
**図 3. QEMU がマウスを捕捉した状態**

![QEMU がマウスを捕捉した状態](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd03.png)

> **注記**: FreeBSD 上では、QEMU の初回インストールがやや遅く感じられることがあります。
> これはエミュレータがディスクの初回使用時にファイルシステムのフォーマットやメタデータの書き込みを行うためです。
> 以降の操作は一般にずっと高速になります。

インストール中には次の点に注意してください。

* ファイルシステムには UFS を選択してください。
  ZFS はメモリ容量が小さい環境では十分な性能が出ません。
* ネットワークには DHCP を使用してください。
  ローカル LAN が対応している場合は、必要に応じて IPv6 も設定してください。
* 既定のユーザーを追加する際は、**wheel** グループのメンバーに含めてください。

インストールが完了すると、仮想マシンは新しくインストールされた FreeBSD イメージで再起動します。

`root` としてログインし、次のようにシステムを更新します。

```shell
# freebsd-update fetch
# freebsd-update install
# shutdown -r now
```

> **注記**: インストールが成功した後は、QEMU はインストーラではなくディスクにインストールされたオペレーティングシステムを起動します。

> **注記**: QEMU は `-runas` オプションに対応しています。
> セキュリティを高めるため、上記のスクリプト例に `"-runas user_name"` オプションを含めることができます。
> 詳細は `qemu(1)` を参照してください。

再び `root` としてログインし、必要なパッケージを追加します。
ゲスト内で X Window System を利用するには、後述の「X Window System の使用」節を参照してください。

これで "left" 仮想マシンのセットアップは完了です。

"right" 仮想マシンをインストールするには、次のスクリプトを実行します。
このスクリプトには、`tap1`、`format=qcow2`、イメージファイル名、MAC アドレス、端末ウィンドウ名に関する変更が反映されています。
必要に応じて、上記の注記で説明した `-runas` パラメータを含めてください。

```

/usr/local/bin/qemu-system-x86_64  -monitor none \
  -cpu qemu64 \
  -vga cirrus \
  -m 4096  -smp 4   \
  -cdrom ../ISO/fbsd.iso \
  -boot order=cd,menu=on \
  -drive if=none,id=drive0,cache=writeback,aio=threads,format=qcow2,discard=unmap,file=../VM/right.qcow2 \
  -device virtio-blk-pci,drive=drive0,bootindex=1  \
  -netdev tap,id=nd0,ifname=tap1,script=no,downscript=no,br=bridge0 \
  -device e1000,netdev=nd0,mac=02:72:69:67:68:74 \
  -name \"right\"
```

インストールが完了すると、"left" と "right" のマシンは相互に、またホストとも通信できるようになります。
ホスト上に厳しいファイアウォールルールが設定されている場合は、bridge デバイスと tap デバイスが相互に通信できるようルールを追加または修正することを検討してください。

<a id="qemu-usage-tips"></a>
### 利用のヒント

ここでは、QEMU を利用するうえでの実用的なヒントを紹介します。

<a id="qemu-setting-up-x-windows"></a>
#### X Window System の使用

`X Window` システムの設定方法は [Xorg のインストール](05-x11.md#x-install)で説明されています。
初期の `X Window` 設定についてはそのガイドを参照し、完全なデスクトップ環境の構築方法については[デスクトップ環境](07-desktop.md#desktop)を参照してください。

この節では XFCE デスクトップの使用例を示します。

インストールが完了したら、一般ユーザーとしてログインし、次のように入力します。

```shell
% startx
```

XFCE4 ウィンドウマネージャが起動し、[図 4](#qemu-two-qemu) のように動作するグラフィカルデスクトップが表示されます。
初回起動時はデスクトップが表示されるまで最大 1 分ほどかかる場合があります。
使い方の詳細は [XFCE Web サイト](https://www.xfce.org)のドキュメントを参照してください。

<a id="qemu-two-qemu"></a>
**図 4. 両方の QEMU 仮想マシン**

![両方の QEMU 仮想マシン](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd04.png)

> **ヒント**: ゲストシステムに割り当てるメモリを増やすと、グラフィカルユーザーインターフェースの動作が速くなる場合があります。

この例では、"left" 仮想マシンには `X Window` システムがインストールされており、"right" 仮想マシンはまだテキストモードのままです。

<a id="qemu-using-qemu-window"></a>
#### QEMU ウィンドウの使い方

QEMU ウィンドウは完全な FreeBSD コンソールとして機能し、ベアメタルシステムと同じように複数の仮想端末を実行できます。

別の仮想コンソールへ切り替えるには、QEMU ウィンドウ内をクリックして `Alt+F2` または `Alt+F3` を押します。
すると FreeBSD が別の仮想コンソールへ切り替わります。
[図 5](#qemu-console-ttyv3) は、`ttyv3` 上の仮想コンソールを表示している "left" 仮想マシンを示しています。

<a id="qemu-console-ttyv3"></a>
**図 5. QEMU ウィンドウでの別の仮想コンソールへの切り替え**

![QEMU ウィンドウでの別の仮想コンソールへの切り替え](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd05.png)

> **ヒント**: ホスト側の現在のデスクトップマネージャやウィンドウマネージャが、`Alt+F1` や `Alt+F2` のキーシーケンスを別の機能に割り当てている場合があります。
> その場合は、`Ctl+Alt+F1`、`Ctl+Alt+F2`、または類似のキーの組み合わせを試してください。
> 詳細はウィンドウマネージャまたはデスクトップマネージャのドキュメントを確認してください。

<a id="qemu-using-qemu-window-menus"></a>
#### QEMU ウィンドウメニューの使い方

QEMU ウィンドウのもう 1 つの機能として、`View` メニューとズーム制御があります。
最も便利なのは `Zoom to Fit` です。
このメニュー項目をクリックすると、ウィンドウの角のコントロールをドラッグして QEMU ウィンドウのサイズを変更できるようになります。
[図 6](#qemu-zoom-to-fit) は、グラフィックスモード中に "left" ウィンドウのサイズを変更した様子を示しています。

<a id="qemu-zoom-to-fit"></a>
**図 6. View メニューの `Zoom to Fit` オプションの使用**

![View メニューの Zoom to Fit オプションの使用](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd06.png)

<a id="qemu-other-qemu-window-menu-options"></a>
#### その他の QEMU ウィンドウメニューオプション

`View` メニューには次の項目も表示されます。

* `cirrus-vga`、`serial0`、`parallel0` オプション。
  これらにより、選択したデバイスへ入出力を切り替えることができます。

QEMU ウィンドウの `Machine` メニューでは、ゲスト仮想マシンに対して 4 種類の制御を行えます。

* `Pause` は QEMU 仮想マシンを一時停止します。
  高速にスクロールする画面を止めて確認したい場合に便利です。
* `Reset` は仮想マシンを即座にコールドな「電源投入」状態へリセットします。
  実機と同様、どうしても必要な場合を除き推奨されません。
* `Power Down` は ACPI シャットダウン信号をシミュレートし、オペレーティングシステムを正常にシャットダウンさせます。
* `Quit` は仮想マシンの電源を即座に切ります。これも必要な場合を除き推奨されません。

<a id="qemu-adding-serial-port-to-guest-vm"></a>
### ゲスト仮想マシンへのシリアルポートインターフェースの追加

シリアルコンソールを実装するには、FreeBSD を実行しているゲスト仮想マシンの `/boot/loader.conf` に

```
console="comconsole"
```

を挿入し、FreeBSD シリアルコンソールを使用できるようにする必要があります。

以下の更新された設定例は、ゲスト仮想マシンでシリアルコンソールを実装する方法を示しています。
スクリプトを実行して仮想マシンを起動します。

```
# left+serial.sh
echo
echo "NOTE: telnet startup server running on guest VM!"
echo "To start QEMU, start another session and telnet to localhost port 4410"
echo

/usr/local/bin/qemu-system-x86_64  -monitor none \
  -serial telnet:localhost:4410,server=on,wait=on\
  -cpu qemu64 \
  -vga std \
  -m 4096 \
  -smp 4   \
  -cdrom ../ISO/fbsd.iso \
  -boot order=cd,menu=on \
  -blockdev driver=file,aio=threads,node-name=imgleft,filename=../VM/left.img \
  -blockdev driver=raw,node-name=drive0,file=imgleft \
  -device virtio-blk-pci,drive=drive0,bootindex=1  \
  -netdev tap,id=nd0,ifname=tap0,script=no,downscript=no,br=bridge0 \
  -device e1000,netdev=nd0,mac=02:20:6c:65:66:74 \
  -name \"left\"
```

<a id="qemu-left-serial-port"></a>
**図 7. TCP 経由でのシリアルポートの有効化**

![TCP 経由でのシリアルポートの有効化](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd07.png)

[図 7](#qemu-notes-on-serial-console) では、仮想マシンの起動時にシリアルポートがホストシステム上の TCP ポートへリダイレクトされ、QEMU モニタは指定された localhost ポートへ `telnet(1)` 接続が行われるまでゲスト仮想マシンの起動を待機（`wait=on`）します。
別セッションからの接続を受け取ると、FreeBSD システムが起動を開始し、`/boot/loader.conf` 内のコンソール指定を参照します。
`"console=comconsole"` の指定により、FreeBSD はシリアルポート上でコンソールセッションを開始します。
QEMU モニタはこれを検知し、そのシリアルポート上の必要な文字 I/O をホスト上の telnet セッションへ振り向けます。
システムが起動を完了すると、シリアルポート（`ttyu0`）とコンソール（`ttyv0`）の両方でログインプロンプトが有効になります。

この TCP 経由のシリアルリダイレクトは仮想マシンの外側で行われる点に注意してください。
仮想マシン上のどのネットワークともやり取りしないため、ファイアウォールルールの影響を受けません。
実機の RS-232 ポートや USB ポートに接続されたダム端末のようなものだと考えてください。

<a id="qemu-notes-on-serial-console"></a>
#### シリアルコンソールの使用に関する注意

シリアルコンソールでウィンドウサイズを変更した場合は、`resizewin(1)` を実行して端末サイズを更新してください。

syslog メッセージがコンソール（QEMU コンソールとシリアルポートの両方）へ送られないようにすることが望ましい（あるいは必要な）場合があります。
コンソールメッセージのリダイレクト方法の詳細は `syslog.conf(5)` を参照してください。

> **注記**: `/boot/loader.conf`（原文表記 `/boot.loader.conf`）を更新してシリアルコンソールを許可すると、それ以降ゲスト仮想マシンは毎回シリアルポートからの起動を試みるようになります。
> 上記の例のようにシリアルポートを有効にしておくか、シリアルコンソールを要求しないように `/boot/loader.conf` ファイルを更新してください。

<a id="qemu-user-mode-emulation"></a>
### QEMU ユーザーモードエミュレーション

QEMU は、ホスト CPU とは異なるアーキテクチャ向けにコンパイル済みのアプリケーションの実行もサポートしています。
たとえば、x86_64 ホスト上で Sparc64 アーキテクチャのオペレーティングシステムを実行することが可能です。
次の節でその手順を示します。

<a id="qemu-sparc64-user-mode-emulation"></a>
#### x86_64 ホスト上への SPARC64 ゲスト仮想マシンの構築

ホストとは異なるアーキテクチャの新しい仮想マシンを構築するには、いくつかの手順が必要です。

* ゲスト仮想マシン上で実行するソフトウェアの入手
* ゲスト仮想マシン用の新しいディスクイメージの作成
* 新しいアーキテクチャ向けの QEMU スクリプトの作成
* インストールの実行

以下の手順では、この QEMU ユーザーモードエミュレーションの演習として OpenBSD 6.8 SPARC64 版のソフトウェアを使用します。

> **注記**: OpenBSD Sparc64 のすべてのバージョンが QEMU 上で動作するわけではありません。
> OpenBSD バージョン 6.8 は動作が確認されているため、この節の例として採用しています。

1. OpenBSD アーカイブから OpenBSD 6.8 Sparc64 をダウンロードします。

   OpenBSD のダウンロードサイトでは最新バージョンのみが維持されています。
   過去のリリースを入手するにはアーカイブを検索する必要があります。

   ```shell
   % cd ~/QEMU/ISO
   % fetch https://mirror.planetunix.net/pub/OpenBSD-archive/6.8/sparc64/install68.iso
   ```

2. Sparc64 仮想マシン用の新しいディスクイメージの作成は、前述の "right" 仮想マシンと同様です。
   この例ではディスクに QEMU の qcow2 形式を使用します。

   ```shell
   % cd ~/QEMU/VM
   qemu-img create -f qcow2 -o preallocation=full,lazy_refcounts=on sparc64.qcow2 16G
   ```

3. 新しい Sparc64 アーキテクチャ向けに以下のスクリプトを使用します。
   前述の例と同様にスクリプトを実行し、別のセッションを開いて指定されたポートで localhost に `telnet` 接続します。

   ```
   echo
   echo "NOTE: telnet startup server running on guest VM!"
   echo "To start QEMU, start another session and telnet to localhost port 4410"
   echo

   /usr/local/bin/qemu-system-sparc64 \
     -serial telnet:localhost:4410,server=on,wait=on \
     -machine sun4u,usb=off \
     -smp 1,sockets=1,cores=1,threads=1 \
     -rtc base=utc \
     -m 1024 \
     -boot d \
     -drive file=../VM/sparc64.qcow2,if=none,id=drive-ide0-0-1,format=qcow2,cache=none \
     -cdrom ../ISO/install68.iso \
     -device ide-hd,bus=ide.0,unit=0,drive=drive-ide0-0-1,id=ide0-0-1 \
     -msg timestamp=on \
     -net nic,model=sunhme -net user \
     -nographic \
     -name \"sparc64\"
   ```

次の点に注意してください。

* `-boot d` オプションは、`-cdrom ../ISO/install68.iso` として指定された QEMU CDROM デバイスから起動します。
* 先ほどと同様に、`telnet` サーバオプションはポート 4410 での別接続を待機するよう設定されています。
  別のセッションを起動し、`telnet(1)` を使って localhost のポート 4410 に接続してください。
* スクリプトは `-nographic` オプションを指定しているため、シリアルポート I/O のみが使用されます。
  グラフィカルインターフェースはありません。
* ネットワークは `tap(4)` / `if_bridge(4)` の組み合わせでは設定されません。
  この例では、「Serial Line Internet Protocol」（SLIRP）として知られる別の QEMU ネットワーク方式（「User Mode Networking」とも呼ばれます）を使用しています。
  この方式およびその他の QEMU ネットワーク方式に関するドキュメントは、[QEMU Networking Documentation](https://wiki.qemu.org/Documentation/Networking) にあります。

すべて正しく設定されていれば、[図 8](#qemu-sparc64-boot-cdrom-installation) のようにシステムが起動します。

<a id="qemu-sparc64-boot-cdrom-installation"></a>
**図 8. ユーザーモードエミュレーション中に CDROM から OpenBSD 6.8 Sparc64 を起動する QEMU**

![ユーザーモードエミュレーション中に CDROM から OpenBSD 6.8 Sparc64 を起動する QEMU](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd08.png)

システムのインストールが完了したら、スクリプトを修正してブートパラメータを `-boot c` に変更します。
これにより QEMU は CDROM ではなく指定されたハードディスクから起動するようになります。

インストールされたシステムは、他のゲスト仮想マシンとまったく同じように使用できます。
ただし、ゲストの基盤となるアーキテクチャは x86_64 ではなく Sparc64 です。

> **ヒント**: OpenBios コンソールプロンプト `0 >` でシステムが停止した場合は、`power-off` と入力してシステムを終了してください。

[図 9](#qemu-sparc64-login-to-installed-system) は、インストール済みシステムへ root ログインして `uname(1)` を実行した様子を示しています。

<a id="qemu-sparc64-login-to-installed-system"></a>
**図 9. ユーザーモードエミュレーション中に CDROM から起動する QEMU**

![ユーザーモードエミュレーション中に CDROM から起動する QEMU](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd09.png)

<a id="qemu-using-qemu-monitor"></a>
### QEMU モニタの使用

[QEMU モニタ](https://www.qemu.org/docs/master/system/monitor.html)は、実行中の QEMU エミュレータ（ゲスト仮想マシン）を制御します。

モニタを使うと、次の操作などが可能です。

* ディスク、ネットワークインターフェース、CD-ROM、フロッピーなどのデバイスを動的に取り外し、または挿入する
* ゲスト仮想マシンの凍結（freeze）／凍結解除（unfreeze）、およびディスクファイルへの状態の保存・復元を行う
* 仮想マシンおよびデバイスの状態に関する情報を収集する
* 実行中にデバイスの設定を変更する

モニタの最も一般的な用途は、仮想マシンの状態を調べること、およびデバイスの追加・削除・変更を行うことです。
マイグレーションなどの一部の操作は KVM や Xen などのハイパーバイザアクセラレータ下でのみ利用可能であり、FreeBSD ホストではサポートされていません。

グラフィカルデスクトップ環境を使用している場合、QEMU モニタを使う最も簡単な方法は、端末セッションから QEMU を起動する際に `-monitor stdio` オプションを指定することです。

```
# /usr/local/bin/qemu-system-x86_64  -monitor stdio \
  -cpu qemu64 \
  -vga cirrus \
  -m 4096  -smp 4   \
  ...
```

これにより、[図 10](#qemu-monitor-operation) のように端末ウィンドウに新しいプロンプト `(qemu)` が表示されます。

<a id="qemu-monitor-operation"></a>
**図 10. QEMU モニタプロンプトと "stop" コマンド**

![QEMU モニタプロンプトと stop コマンド](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd13.png)

この図には、FreeBSD のブートシーケンス中に `stop` コマンドでシステムを凍結した様子も示されています。
モニタで `cont` コマンドを入力するまで、システムは凍結されたままになります。

<a id="qemu-adding-new-disk"></a>
#### 仮想マシンへの新しいディスクの追加

実行中の仮想マシンに新しいディスクを追加するには、前述と同じようにディスクを準備する必要があります。

```shell
% cd ~/QEMU/VM
% qemu-img create -f raw  new10G.img  10G
```

[図 11](#qemu-add-new-disk-figure) は、仮想マシンに新しいディスクを追加するために必要なモニタコマンドの手順を示しています。
モニタで `device_add` コマンドを使ってデバイスを追加すると、図の下部に示されている FreeBSD システムコンソール上にデバイスが現れます。
あとは必要に応じてディスクを設定できます。

仮想マシンの再起動後も新しいディスクを使用したい場合は、起動スクリプトにそのディスクを追加する必要がある点に注意してください。

<a id="qemu-add-new-disk-figure"></a>
**図 11. 新しいディスクを追加するための QEMU モニタコマンド**

![新しいディスクを追加するための QEMU モニタコマンド](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd14.png)

<a id="qemu-using-monitor-manage-snapshots"></a>
#### QEMU モニタを使ったスナップショットの管理

QEMU のドキュメントでは、**スナップショット（snapshot）** という用語でいくつかの似た概念が説明されています。
コマンドラインの `-snapshot` オプションは、ドライブまたはドライブの一部を使ってデバイスのコピーを保持することを指します。
また、モニタコマンドの `snapshot_blkdev` と `snapshot_blkdev_internal` は、blockdev デバイスを実際にコピーする操作を指します。
最後に、モニタコマンドの `savevm`、`loadvm`、`delvm` は、仮想マシン全体のコピーを作成して保存・読み込み・削除する操作を指します。
これと合わせて、モニタの `info snapshots` コマンドは最近のスナップショットの詳細を一覧表示します。

この節では仮想マシン全体のイメージの作成・保存・読み込みに焦点を当て、この意味で **スナップショット** という用語を使用します。

まず、今回は `qcow2` 形式を使って "left" 仮想マシンを最初から作り直します。

```shell
% cd ~/QEMU/VM
% rm left.img
% qemu-img create -f qcow2 left.qcow2 16G  # Clean file for a new FreeBSD installation.
% cd ../SCRIPTS
# /bin/sh left.sh                     # See the below program listing.
```

インストールが完了したら、今度はモニタを使用できるように `-monitor stdio` オプションを指定して再起動します。

```
# left VM script.
/usr/local/bin/qemu-system-x86_64  -monitor stdio \
  -cpu qemu64 \
  -vga std \
  -m 4096 \
  -smp 4   \
  -cdrom ../ISO/fbsd.iso \
  -boot order=cd,menu=on \
  -blockdev driver=file,aio=threads,node-name=imgleft,filename=../VM/left.qcow2 \
  -blockdev driver=qcow2,node-name=drive0,file=imgleft \
  -device virtio-blk-pci,drive=drive0,bootindex=1  \
  -netdev tap,id=nd0,ifname=tap0,script=no,downscript=no,br=bridge0 \
  -device e1000,netdev=nd0,mac=02:20:6c:65:66:74 \
  -name \"left\"
```

スナップショットの動作を確認するため、次の手順を実行できます。

1. FreeBSD を最初からインストールする
2. 環境を準備し、`savevm` モニタコマンドでスナップショットを取得する
3. いくつかのパッケージをインストールする
4. システムをシャットダウンする
5. 素の QEMU インスタンスを再起動し、モニタコマンド `loadvm` を使って仮想マシンを復元する
6. 復元された仮想マシンにパッケージが一切入っていないことを確認する

「環境を準備する」ステップでは、ユーザー操作を模擬するため、別の仮想コンソール（ttyv1）で `vi(1)` による編集セッションを開始しています。
必要に応じて他のプログラムを起動しても構いません。
スナップショットには、取得時点で実行中のすべてのアプリケーションの状態が記録されます。

[図 12](#qemu-using-monitor-snapshots) は、パッケージがまだ入っていない新規インストール直後の FreeBSD システムと、それとは別の ttyv1 上での編集セッションを示しています。
`vi(1)` エディタは現在 `insert` モードになっており、入力者が「broadcast」という単語を入力している状態です。

<a id="qemu-using-monitor-snapshots"></a>
**図 12. 最初のスナップショット取得前の QEMU 仮想マシン**

![最初のスナップショット取得前の QEMU 仮想マシン](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd15.png)

スナップショットを生成するには、モニタで `savevm` を入力します。
その際、必ずタグ（たとえば `original_install`）を指定してください。

```shell
QEMU 9.0.1 monitor - type 'help' for more information
(qemu)
(qemu) savevm original_install
```

次に、メインのコンソールウィンドウで、依存関係のない `zip(1)` などのパッケージをインストールします。
インストールが完了したら、再びモニタに戻って別のスナップショット（`snap1_pkg+zip`）を作成します。

[図 13](#qemu-after-monitor-snapshots) は、上記コマンドの結果と `info snapshots` コマンドの出力を示しています。

<a id="qemu-after-monitor-snapshots"></a>
**図 13. スナップショット用の QEMU モニタコマンドの使用**

![スナップショット用の QEMU モニタコマンドの使用](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd16.png)

システムを再起動し、FreeBSD が起動する前にモニタへ切り替えて `stop` を入力します。
すると仮想マシンが停止します。

先ほど使用したタグ（ここでは `original_install`）を指定して `loadvm` を入力します。

```shell
QEMU 9.0.1 monitor - type 'help' for more information
(qemu) stop
(qemu) loadvm original_install
(qemu) cont
```

すると即座に、仮想マシンの画面が先ほど `savevm` コマンドを入力したまさにその瞬間へ切り替わります。
この時点ではまだ仮想マシンが停止している点に注意してください。

`cont` を入力して仮想マシンを再開し、`ttyv1` の編集セッションへ切り替えてキーボードで 1 文字入力してみてください。
挿入モードのままになっていたエディタが、そのまま入力に反応するはずです。
スナップショット取得時に実行中だった他のプログラムも影響を受けずに動作します。

以上の手順により、スナップショットを取得し、システムを変更した後、以前のスナップショットを復元して「ロールバック」する方法がわかります。

既定では、QEMU はスナップショットデータをイメージと同じファイルに保存します。
[図 14](#qemu-examine-monitor-snapshots) に示すように、`qemu-img(1)` でスナップショットの一覧を確認できます。

<a id="qemu-examine-monitor-snapshots"></a>
**図 14. `qemu-img(1)` を使ったスナップショットの確認**

![qemu-img を使ったスナップショットの確認](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd17.png)

<a id="qemu-using-qemu-usb-devices"></a>
### QEMU USB デバイスの使用

QEMU はイメージファイルをバックエンドとする仮想 USB デバイスの作成に対応しています。
これらは実際の USB デバイスとまったく同じように、パーティション分割、フォーマット、マウント、利用が可能な仮想 USB デバイスです。

```
/usr/local/bin/qemu-system-x86_64  -monitor stdio \
  -cpu qemu64 \
  -vga cirrus \
  -m 4096  -smp 4   \
  -cdrom ../ISO/fbsd.iso \
  -boot order=cd,menu=on \
  -drive if=none,id=usbstick,format=raw,file=../VM/foo.img \
  -usb \
  -device usb-ehci,id=ehci \
  -device usb-storage,bus=ehci.0,drive=usbstick \
  -device usb-mouse \
  -blockdev driver=file,node-name=img1,filename=../VM/right.qcow2 \
  -blockdev driver=qcow2,node-name=drive0,file=img1 \
  -device virtio-blk-pci,drive=drive0,bootindex=1  \
  -netdev tap,id=nd0,ifname=tap1,script=no,downscript=no,br=bridge0 \
  -device e1000,netdev=nd0,mac=02:72:69:67:68:74 \
  -name \"right\"
```

この設定には、`id=usbstick`、raw 形式、イメージファイル（`qemu-img(1)` で事前に作成しておく必要があります）を指定した `-drive` 指定が含まれています。
次の行には、`id=ehci` を持つ USB EHCI コントローラ用の `-device usb-ehci` 指定があります。
最後に、`-device usb-storage` 指定によって上記のドライブを EHCI USB バスに結び付けています。

システムが起動すると、[図 15](#qemu-usb-internal-storage) に示すように FreeBSD が USB ハブを認識し、接続された USB デバイスを追加して `da0` として割り当てます。

<a id="qemu-usb-internal-storage"></a>
**図 15. QEMU が作成した USB ハブとマスストレージデバイス**

![QEMU が作成した USB ハブとマスストレージデバイス](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd12.png)

このデバイスは `gpart(8)` でパーティション分割し、`newfs(8)` でフォーマットできる状態になっています。
USB デバイスは `qemu-img(1)` で作成したファイルをバックエンドとしているため、デバイスに書き込まれたデータは再起動後も永続的に保持されます。

<a id="qemu-using-host-usb-devices"></a>
### パススルーによるホスト USB デバイスの使用

QEMU の USB パススルーサポートは、バージョン 9.0.1（2024 年夏）では実験的（experimental）とされています。
とはいえ、以下の手順ではホストにマウントされた USB メモリをゲスト仮想マシンから使用する方法を示します。

詳細や例については次を参照してください。

* [https://www.qemu.org/docs/master/system/devices/usb.html](https://www.qemu.org/docs/master/system/devices/usb.html)

[図 16](#qemu-usb-passthrough) の上部は QEMU モニタコマンドを示しています。

* `info usbhost` はホストシステム上のすべての USB デバイスに関する情報を表示します。
  ホストシステム上で目的の USB デバイスを探し、その行にある 2 つの 16 進数値を控えます。
  （以下の例では、ホストの USB デバイスは Memorex Mini で、vendorid は 0718、productid は 0619 です。）
  `info usbhost` コマンドで表示された 2 つの値を、以下の `device_add` の手順で使用します。
* `device_add` はゲスト仮想マシンに USB デバイスを追加します。

<a id="qemu-usb-passthrough"></a>
**図 16. ホスト上の USB デバイスへアクセスするための QEMU モニタコマンド**

![ホスト上の USB デバイスへアクセスするための QEMU モニタコマンド](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd18.png)

先ほどと同様に、`device_add` が完了すると、図の下半分に示されているように FreeBSD カーネルが新しい USB デバイスを認識します。

新しいデバイスの使用例を[図 17](#qemu-usb-passthrough2) に示します。

<a id="qemu-usb-passthrough2"></a>
**図 17. パススルー経由でのホスト USB デバイスの使用**

![パススルー経由でのホスト USB デバイスの使用](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/virtualization/qemu-freebsd19.png)

USB デバイスが FAT16 または FAT32 ファイルシステムでフォーマットされている場合は、例に示されているように `mount_msdosfs(8)` を使って MS-DOS™ ファイルシステムとしてマウントできます。
`/etc/hosts` ファイルが新しくマウントされたドライブへコピーされ、USB デバイス上のファイルの整合性を確認するためにチェックサムが計算されています。
その後、`umount(8)` でデバイスがアンマウントされます。

USB デバイスが NTFS でフォーマットされている場合は、`fusefs-ntfs` パッケージをインストールし、`ntfs-3g(8)` を使用してデバイスにアクセスする必要があります。

```shell
# pkg install fusefs-ntfs
# kldload fusefs
# gpart show da1
# ntfs-3g /dev/da1s1 /mnt

Access the drive as needed.  When finished:

# umount /mnt
```

上記のデバイス識別子は、接続されているハードウェアに合わせて変更してください。
NTFS ファイルシステムの扱いに関する追加情報は `ntfs-3g(8)` を参照してください。

<a id="qemu-summary"></a>
### FreeBSD 上の QEMU のまとめ

前述のとおり、QEMU はいくつかの異なるハイパーバイザアクセラレータと連携して動作します。

QEMU がサポートする [Virtualization Accelerators](https://www.qemu.org/docs/master/system/introduction.html#virtualisation-accelerators) の一覧には次のものが含まれます。

* Linux 上の `KVM`: 64 ビット Arm、MIPS、PPC、RISC-V、s390x、および x86 をサポート
* Linux 上の dom0 としての `Xen`: Arm、x86 をサポート
* MacOS 上の `Hypervisor Framework (hvf)`: x86 および Arm（いずれも 64 ビットのみ）をサポート
* Windows 上の `Windows Hypervisor Platform (whpx)`: x86 をサポート
* NetBSD 上の `NetBSD Virtual Machine Monitor (nvmm)`: x86 をサポート
* Linux およびその他の POSIX、Windows、MacOS 上の `Tiny Code Generator (tcg)`: Arm、x86、Loongarch64、MIPS、PPC、s390x、および Sparc64 をサポート

この節のすべての例では、現時点で FreeBSD 上でサポートされている唯一のアクセラレータである `Tiny Code Generator (tcg)` アクセラレータを使用しました。

<a id="virtualization-host-bhyve"></a>
## bhyve をホストとする FreeBSD

BSD ライセンスのハイパーバイザである bhyve は、FreeBSD 10.0-RELEASE からベースシステムの一部となりました。
このハイパーバイザは、FreeBSD、OpenBSD、多くの Linux® ディストリビューション、Microsoft Windows® など複数のゲストをサポートしています。
既定では、bhyve はシリアルコンソールへのアクセスを提供し、グラフィカルコンソールはエミュレートしません。
新しい CPU の仮想化オフロード機能を利用することで、命令の変換やメモリマッピングの手動管理といった従来の手法を回避しています。

bhyve の設計には次のいずれかが必要です。

* Intel Extended Page Tables（EPT）をサポートする Intel® プロセッサ
* AMD Rapid Virtualization Indexing（RVI）または Nested Page Tables（NPT）をサポートする AMD® プロセッサ
* ARM® aarch64 CPU

ARM では純粋な ARMv8.0 仮想化のみがサポートされており、Virtualization Host Extensions は現時点では使用されません。
Linux® ゲストや複数の vCPU を持つ FreeBSD ゲストをホストするには、VMX unrestricted mode（UG）のサポートが必要です。

Intel または AMD プロセッサが bhyve に対応しているかを確認する最も簡単な方法は、`dmesg` を実行するか `/var/run/dmesg.boot` を確認して、AMD® プロセッサなら `Features2` 行の `POPCNT` プロセッサ機能フラグ、Intel® プロセッサなら `VT-x` 行の `EPT` と `UG` があるかを見ることです。

<a id="virtualization-bhyve-prep"></a>
### ホストの準備

bhyve で仮想マシンを作成する最初の手順は、ホストシステムを設定することです。
まず、bhyve のカーネルモジュールを読み込みます。

```shell
# kldload vmm
```

仮想マシンゲストをホストのネットワークへ接続する方法はいくつかありますが、分かりやすい方法の 1 つは、仮想マシン内のネットワークデバイスが接続するための `tap` インターフェースを作成することです。
そのネットワークデバイスがネットワークに参加できるように、`tap` インターフェースと物理インターフェースをメンバーに含むブリッジインターフェースも作成します。
この例では、物理インターフェースは _igb0_ です。

```shell
# ifconfig tap0 create
# sysctl net.link.tap.up_on_open=1
net.link.tap.up_on_open: 0 -> 1
# ifconfig bridge0 create
# ifconfig bridge0 addm igb0 addm tap0
# ifconfig bridge0 up
```

<a id="virtualization-bhyve-freebsd"></a>
### FreeBSD ゲストの作成

ゲストマシン用の仮想ディスクとして使用するファイルを作成します。
仮想ディスクのサイズと名前を指定します。

```shell
# truncate -s 16G guest.img
```

インストールする FreeBSD のインストールイメージをダウンロードします。

```shell
# fetch https://download.freebsd.org/releases/ISO-IMAGES/14.0/FreeBSD-14.0-RELEASE-amd64-bootonly.iso
FreeBSD-14.0-RELEASE-amd64-bootonly.iso                426 MB   16 MBps    22s
```

FreeBSD には、bhyve で仮想マシンを実行するためのサンプルスクリプト `vmrun.sh` が付属しています。
このスクリプトは仮想マシンを起動してループ内で実行するため、クラッシュした場合でも自動的に再起動します。
`vmrun.sh` にはマシンの構成を制御するためのいくつかのオプションがあります。

* `-c`: 仮想 CPU 数を制御します
* `-m`: ゲストが利用できるメモリ量を制限します
* `-t`: 使用する `tap` デバイスを定義します
* `-d`: 使用するディスクイメージを指定します
* `-i`: ディスクではなく CD イメージから起動するよう bhyve に指示します
* `-I`: 使用する CD イメージを定義します

最後のパラメータは仮想マシンの名前で、実行中のマシンを追跡するために使われます。
次のコマンドで、利用可能なすべてのプログラム引数オプションを一覧表示できます。

```shell
# sh /usr/share/examples/bhyve/vmrun.sh -h
```

次の例では、仮想マシンをインストールモードで起動します。

```shell
# sh /usr/share/examples/bhyve/vmrun.sh -c 1 -m 1024M -t tap0 -d guest.img \
     -i -I FreeBSD-14.0-RELEASE-amd64-bootonly.iso guestname
```

仮想マシンが起動し、インストーラが開始されます。
仮想マシンへのシステムインストールが終わり、最後にシェルへ抜けるかどうか尋ねられたら **Yes** を選択します。

仮想マシンを再起動します。
仮想マシンを再起動すると bhyve は終了しますが、`vmrun.sh` スクリプトは `bhyve` をループ内で実行しているため自動的に再起動します。
再起動したら、ブートローダメニューから reboot オプションを選んでループから抜けてください。
これで、仮想ディスクからゲストを起動できるようになります。

```shell
# sh /usr/share/examples/bhyve/vmrun.sh -c 4 -m 1024M -t tap0 -d guest.img guestname
```

<a id="virtualization-bhyve-linux"></a>
### Linux® ゲストの作成

Linux ゲストは、他の通常の [UEFI ベースのゲスト](#virtualization-bhyve-uefi)仮想マシンと同様に起動することも、代わりに `sysutils/grub2-bhyve` port を使用して起動することもできます。

これを行うには、まずこの port がインストールされていることを確認し、次にゲストマシン用の仮想ディスクとして使うファイルを作成します。

```shell
# truncate -s 16G linux.img
```

`grub2-bhyve` を使って Linux 仮想マシンを起動するには、2 段階の手順を踏みます。

1. まずカーネルを読み込み、その後でゲストを起動します。
2. Linux® カーネルは `sysutils/grub2-bhyve` で読み込みます。

grub が仮想デバイスをホストシステム上のファイルへマッピングするために使用する `device.map` を作成します。

```
(hd0) ./linux.img
(cd0) ./somelinux.iso
```

`sysutils/grub2-bhyve` を使って、ISO イメージから Linux® カーネルを読み込みます。

```shell
# grub-bhyve -m device.map -r cd0 -M 1024M linuxguest
```

これにより grub が起動します。
インストール CD に `grub.cfg` が含まれている場合はメニューが表示されます。
含まれていない場合は、`vmlinuz` と `initrd` ファイルを探して手動で読み込む必要があります。

```shell
grub> ls
(hd0) (cd0) (cd0,msdos1) (host)
grub> ls (cd0)/isolinux
boot.cat boot.msg grub.conf initrd.img isolinux.bin isolinux.cfg memtest
splash.jpg TRANS.TBL vesamenu.c32 vmlinuz
grub> linux (cd0)/isolinux/vmlinuz
grub> initrd (cd0)/isolinux/initrd.img
grub> boot
```

Linux® カーネルが読み込まれたので、ゲストを起動できます。

```shell
# bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc -s 2:0,virtio-net,tap0 \
    -s 3:0,virtio-blk,./linux.img -s 4:0,ahci-cd,./somelinux.iso \
    -l com1,stdio -c 4 -m 1024M linuxguest
```

システムが起動し、インストーラが開始されます。
仮想マシンへのシステムインストールが終わったら、仮想マシンを再起動します。
これにより bhyve が終了します。
再び起動する前に、仮想マシンのインスタンスを破棄する必要があります。

```shell
# bhyvectl --destroy --vm=linuxguest
```

これで仮想ディスクから直接ゲストを起動できるようになります。
カーネルを読み込みます。

```shell
# grub-bhyve -m device.map -r hd0,msdos1 -M 1024M linuxguest
grub> ls
(hd0) (hd0,msdos2) (hd0,msdos1) (cd0) (cd0,msdos1) (host)
(lvm/VolGroup-lv_swap) (lvm/VolGroup-lv_root)
grub> ls (hd0,msdos1)/
lost+found/ grub/ efi/ System.map-2.6.32-431.el6.x86_64 config-2.6.32-431.el6.x
86_64 symvers-2.6.32-431.el6.x86_64.gz vmlinuz-2.6.32-431.el6.x86_64
initramfs-2.6.32-431.el6.x86_64.img
grub> linux (hd0,msdos1)/vmlinuz-2.6.32-431.el6.x86_64 root=/dev/mapper/VolGroup-lv_root
grub> initrd (hd0,msdos1)/initramfs-2.6.32-431.el6.x86_64.img
grub> boot
```

仮想マシンを起動します。

```shell
# bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc -s 2:0,virtio-net,tap0 \
    -s 3:0,virtio-blk,./linux.img -l com1,stdio -c 4 -m 1024M linuxguest
```

仮想マシン内で Linux® が起動し、やがてログインプロンプトが表示されます。
ログインして仮想マシンを使用してください。
作業が終わったら、仮想マシンを再起動して bhyve を終了します。
仮想マシンインスタンスを破棄します。

```shell
# bhyvectl --destroy --vm=linuxguest
```

<a id="virtualization-bhyve-uefi"></a>
### UEFI ファームウェアによる bhyve 仮想マシンの起動

bhyve ハイパーバイザは、`bhyveload` や `grub-bhyve` に加えて、UEFI ファームウェアを使って仮想マシンを起動することもできます。
このオプションにより、他のローダではサポートされていないゲストオペレーティングシステムを起動できる場合があります。

bhyve の UEFI サポートを利用するには、まず UEFI ファームウェアイメージを入手します。
これは `sysutils/bhyve-firmware` port またはパッケージをインストールすることで行えます。

ファームウェアを配置したら、bhyve のコマンドラインに `-l bootrom,_/path/to/firmware_` フラグを追加します。
実際の bhyve コマンドは次のようになります。

```shell
# bhyve -AHP -s 0:0,hostbridge -s 1:0,lpc \
  	-s 2:0,virtio-net,tap1 -s 3:0,virtio-blk,./disk.img \
	-s 4:0,ahci-cd,./install.iso -c 4 -m 1024M \
	-l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
	guest
```

ゲストが UEFI 変数を保存できるようにするには、`-l` フラグに変数ファイルを追加します。
bhyve はゲストによる変更を指定された変数ファイルに書き込む点に注意してください。
そのため、最初に変数テンプレートファイルのゲストごとのコピーを必ず作成してください。

```shell
# cp /usr/local/share/uefi-firmware/BHYVE_UEFI_VARS.fd /path/to/vm-image/BHYVE_UEFI_VARS.fd
```

次に、その変数ファイルを bhyve の引数に追加します。

```shell
# bhyve -AHP -s 0:0,hostbridge -s 1:0,lpc \
  	-s 2:0,virtio-net,tap1 -s 3:0,virtio-blk,./disk.img \
	-s 4:0,ahci-cd,./install.iso -c 4 -m 1024M \
	-l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd,/path/to/vm-image/BHYVE_UEFI_VARS.fd \
	guest
```

> **注記**: 一部の Linux ディストリビューションでは、UEFI ブートファイルのパス（たとえば `bootx64.efi` ではなく `linux64.efi` や `grubx64.efi`）を保存するために UEFI 変数を使用する必要があります。
> そのため、ブートパーティション内のファイルを手動で変更しなくて済むよう、Linux 仮想マシンでは変数ファイルを使用することが推奨されます。

変数ファイルの内容を表示または変更するには、ホストから `efivar(8)` を使用します。

`sysutils/bhyve-firmware` には、UEFI に対応していないゲストをレガシー BIOS モードで起動するための CSM 対応ファームウェアも含まれています。

```shell
# bhyve -AHP -s 0:0,hostbridge -s 1:0,lpc \
  	-s 2:0,virtio-net,tap1 -s 3:0,virtio-blk,./disk.img \
	-s 4:0,ahci-cd,./install.iso -c 4 -m 1024M \
	-l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI_CSM.fd \
	guest
```

<a id="virtualization-bhyve-framebuffer"></a>
### bhyve ゲスト用のグラフィカル UEFI フレームバッファ

UEFI ファームウェアのサポートは、Microsoft Windows® のような主にグラフィカルなゲストオペレーティングシステムで特に有用です。

`-s 29,fbuf,tcp=_0.0.0.0:5900_` フラグを指定すると、UEFI-GOP フレームバッファのサポートも有効にできます。
フレームバッファの解像度は `w=_800_` と `h=_600_` で設定でき、`wait` を追加するとゲストを起動する前に VNC 接続を待機させることができます。
フレームバッファには、ホストから、またはネットワーク経由で VNC プロトコルを使ってアクセスできます。
さらに、`-s 30,xhci,tablet` を追加すると、ホストとマウスカーソルを正確に同期させることができます。

結果として bhyve コマンドは次のようになります。

```shell
# bhyve -AHP -s 0:0,hostbridge -s 31:0,lpc \
  	-s 2:0,virtio-net,tap1 -s 3:0,virtio-blk,./disk.img \
	-s 4:0,ahci-cd,./install.iso -c 4 -m 1024M \
	-s 29,fbuf,tcp=0.0.0.0:5900,w=800,h=600,wait \
	-s 30,xhci,tablet \
	-l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
	guest
```

BIOS エミュレーションモードでは、ファームウェアからゲストオペレーティングシステムへ制御が移るとフレームバッファの更新が停止する点に注意してください。

<a id="virtualization-bhyve-windows"></a>
### Microsoft Windows® ゲストの作成

Windows 10 以前のバージョンのゲストの構築は、元のインストールメディアから直接行うことができ、比較的単純な手順です。
最小リソース要件に加えて、Windows をゲストとして実行するには次のことが必要です。

* 仮想マシンのメモリを固定（wire）すること（`-w` フラグ）
* UEFI bootrom で起動すること

Windows インストール ISO を使って仮想マシンゲストを起動する例を次に示します。

```shell
bhyve \
      -c 2 \
      -s 0,hostbridge \
      -s 3,nvme,windows2016.img \
      -s 4,ahci-cd,install.iso \
      -s 10,virtio-net,tap0 \
      -s 31,lpc \
      -s 30,xhci,tablet \
      -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
      -m 8G -H -w \
      windows2016
```

インストール中は 1 個または 2 個の VCPU のみを使用すべきですが、Windows のインストール後はこの数を増やすことができます。

定義した `virtio-net` ネットワークインターフェースを使用するには、[VirtIO ドライバ](https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md)をインストールする必要があります。
代わりに上記のコマンドラインで `virtio-net` を `e1000` に変更して E1000（Intel E82545）エミュレーションへ切り替えることもできますが、性能は低下します。

<a id="virtualization-bhyve-windows-win11"></a>
#### Windows 11 ゲストの作成

Windows 11 以降、Microsoft は TPM 2 モジュールのハードウェア要件を導入しました。
bhyve はハードウェア TPM をゲストへパススルーすることに対応しています。
関連するハードウェアチェックを無効にするためにインストールメディアを変更することもできます。
この手順の詳細は [FreeBSD Wiki](https://wiki.freebsd.org/bhyve/Windows#iso-remaster) に記載されています。

> **警告**: Windows インストールメディアの変更や、TPM モジュールなしでの Windows ゲストの実行はメーカーによってサポートされていません。
> このような手法を採用する前に、用途とユースケースをよく検討してください。

<a id="virtualization-bhyve-zfs"></a>
### bhyve ゲストでの ZFS の使用

ホストマシンで ZFS が利用できる場合、ディスクイメージファイルの代わりに ZFS ボリュームを使用すると、ゲスト仮想マシンの性能を大幅に向上させることができます。
ZFS ボリュームは次のように作成できます。

```shell
# zfs create -V16G -o volmode=dev zroot/linuxdisk0
```

仮想マシンを起動する際、ディスクドライブとしてその ZFS ボリュームを指定します。

```shell
# bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc -s 2:0,virtio-net,tap0 \
  	-s3:0,virtio-blk,/dev/zvol/zroot/linuxdisk0 \
	-l com1,stdio -c 4 -m 1024M linuxguest
```

ホストとゲスト内の両方で ZFS を使用する場合、両方のシステムが仮想マシンの内容をキャッシュすることによるメモリ圧迫の競合に注意してください。
これを緩和するため、ホスト側の ZFS ファイルシステムではメタデータのみのキャッシュを使用するよう設定することを検討してください。
これを行うには、`<name>` を仮想マシンの特定の zvol データセット名に置き換えて、ホスト上の ZFS ファイルシステムに次の設定を適用します。

```shell
# zfs set primarycache=metadata <name>
```

<a id="virtualiziation-bhyve-snapshot"></a>
### 仮想マシンスナップショットの作成

現代のハイパーバイザでは、状態の「スナップショット」を作成できます。
このようなスナップショットには、ゲストのディスク、CPU、メモリの内容が含まれます。
通常、スナップショットはゲストが実行中かシャットダウンされているかに関係なく取得できます。
その後、スナップショットを取得したまさにその時点の状態へ仮想マシンをリセットして戻すことができます。

<a id="virtualization-bhyve-snapshot-zfs"></a>
#### ZFS スナップショット

仮想マシンのバックエンドストレージとして ZFS ボリュームを使用すると、ゲストのディスクのスナップショットを取得できるようになります。たとえば次のように実行します。

```shell
zfs snapshot zroot/path/to/zvol@snapshot_name
```

このようにゲストの実行中に ZFS ボリュームのスナップショットを取得することも可能ですが、ゲストが動作している間は仮想ディスクの内容が不整合な状態になり得る点に注意してください。
そのため、このコマンドを実行する前にまずゲストをシャットダウンするか一時停止することが推奨されます。
ゲストの一時停止は既定ではサポートされておらず、事前に有効化する必要があります（[メモリと CPU のスナップショット](#virtualization-bhyve-snapshot-builtin)を参照）。

> **警告**: 仮想マシンが ZFS zvol を使用中にスナップショットへロールバックすると、ファイルシステムの内容が破損し、ゲストがクラッシュするおそれがあります。
> ゲスト内の未保存データはすべて失われ、前回のスナップショット以降の変更が破壊される可能性があります。
>
> ファイルシステムを使用可能な状態へ戻すために、仮想マシンをシャットダウンした後で 2 回目のロールバックが必要になる場合があります。
> その結果、スナップショット以降に行われた変更は最終的にすべて失われます。

<a id="virtualization-bhyve-snapshot-builtin"></a>
#### メモリと CPU のスナップショット（実験的機能）

FreeBSD 13 以降、bhyve にはゲストのメモリと CPU の状態をファイルへダンプして仮想マシンを停止する実験的な「スナップショット」機能があります。
その後、スナップショットファイルの内容からゲストを再開できます。

ただし、この機能は既定では有効になっておらず、システムをソースから再構築する必要があります。
カスタムオプション付きでカーネルをコンパイルする手順の詳細は、[ソースからの構築](27-cutting-edge.md#updating-src-building)を参照してください。

> **警告**: この機能は本番環境での利用には適しておらず、特定の仮想マシン構成でのみ動作するよう制限されています。
> 複数の制限事項があります。
>
> * `nvme` および `virtio-blk` ストレージバックエンドはまだ動作しません
> * スナップショットはゲストが各デバイスを 1 種類ずつ使用している場合にのみサポートされます。つまり、複数の `ahci-hd` ディスクが接続されている場合、スナップショットの作成は失敗します
> * さらに、この機能は Intel CPU ではある程度安定しているかもしれませんが、AMD CPU では動作しない可能性が高いです。

> **注記**: 以下の手順を実行する前に、`/usr/src` ディレクトリが最新であることを確認してください。詳しい手順は[ソースの更新](27-cutting-edge.md#updating-src-obtaining-src)を参照してください。

まず、`/etc/src.conf` に以下を追加します。

```
WITH_BHYVE_SNAPHOT=yes
BHYVE_SNAPSHOT=1
MK_BHYVE_SNAPSHOT=yes
```

> **訳注**: 原文では `WITH_BHYVE_SNAPHOT=yes`（`SNAPSHOT` の `S` が抜けた綴り）となっていますが、原文どおり保持しています。

> **注記**: システムを部分的または全面的に再構築したことがある場合は、先へ進む前に以下を実行することが推奨されます。

```shell
# cd /usr/src
# make cleanworld
```

> 実行後、次の手順へ進んでください。

その後、[ソースからの FreeBSD 更新のクイックスタート](27-cutting-edge.md#updating-src-quick-start)節の手順に従って world とカーネルを構築・インストールします。

スナップショット機能が正常に有効化されたことを確認するには、次を入力します。

```shell
# bhyvectl --usage
```

そして、出力に `--suspend` フラグが含まれているか確認します。
このフラグが見当たらない場合、機能は正しく有効化されていません。

次に、任意の実行中の仮想マシンをスナップショットして一時停止（suspend）します。

```shell
# bhyvectl --vm=vmname --suspend=/path/to/snapshot/filename
```

> **注記**: `--suspend` には絶対パスとファイル名を指定してください。
> そうしないと、bhyve は起動元のディレクトリにスナップショットデータを書き込みます。
>
> スナップショットデータは必ず安全なディレクトリに書き込んでください。
> 生成される出力にはゲストの完全なメモリダンプが含まれるため、機密データ（パスワードなど）が含まれている可能性があります。

これにより次の 3 つのファイルが作成されます。

* メモリスナップショット — `--suspend` に指定した入力と同じ名前
* カーネルファイル — `--suspend` に指定した入力に `.kern` の接尾辞を付けた名前
* メタデータ — システム状態に関するメタデータを含み、`.meta` の接尾辞を付けた名前

スナップショットからゲストを復元するには、`bhyve` に `-r` フラグを指定して使用します。

```shell
# bhyve -r /path/to/snapshot/filename
```

異なる CPU アーキテクチャ上でゲストスナップショットを復元することはできません。
一般に、スナップショットを作成したシステムと同一でないシステム上で復元を試みると失敗する可能性が高いです。

<a id="virtualization-bhyve-jailed"></a>
### bhyve の jail 化

セキュリティを強化し、仮想マシンをホストオペレーティングシステムから分離するため、bhyve を jail 内で実行することができます。
jail とそのセキュリティ上の利点についての詳しい説明は、[Jails](16-jails.md#jails) を参照してください。

<a id="virtualization-bhyve-jailed-creation"></a>
#### bhyve 用 jail の作成

まず、jail 環境を作成します。UFS ファイルシステムを使用している場合は、次のように実行するだけです。

```shell
# mkdir -p /jails/bhyve
```

[ZFS ファイルシステム](23-zfs.md#zfs)を使用している場合は、次のコマンドを実行します。

```shell
# zfs create zroot/jails
# zfs create zroot/jails/bhyve
```

次に、仮想マシン `bhyvevm0` 用の ZFS zvol を作成します。

```shell
# zfs create zroot/vms
# zfs create -V 20G -o volmode=dev zroot/vms/bhyvevm0
```

ZFS を使用しない場合は、次のコマンドで jail のディレクトリ構造内にディスクイメージファイルを直接作成します。

```shell
# mkdir /jails/bhyve/vms
# truncate -s 20G /jails/bhyve/vms/bhyvevm0
```

FreeBSD のイメージ（できればホストと同じかそれより古いバージョン）をダウンロードし、jail ディレクトリへ展開します。

```shell
# cd /jails
# fetch -o base.txz http://ftp.freebsd.org/pub/FreeBSD/releases/amd64/13.2-RELEASE/base.txz
# tar -C /jails/bhyve -xvf base.txz
```

> **注記**: ホストより新しいバージョンの FreeBSD を jail 内で実行することはサポートされていません（たとえば、13.2-RELEASE ホスト内の jail で 14.0-RELEASE を実行する場合）。

次に、`/etc/devfs.rules` に devfs ルールセットを追加します。

```
[devfsrules_jail_bhyve=100]
add include $devfsrules_hide_all
add include $devfsrules_unhide_login
add path 'urandom' unhide
add path 'random' unhide
add path 'crypto' unhide
add path 'shm' unhide
add path 'zero' unhide
add path 'null' unhide
add path 'mem' unhide
add path 'vmm' unhide
add path 'vmm/*' unhide
add path 'vmm.io' unhide
add path 'vmm.io/*' unhide
add path 'vmmctl' unhide
add path 'nmdmbhyve*' unhide
add path 'zvol' unhide
add path 'zvol/zroot' unhide
add path 'zvol/zroot/vms' unhide
add path 'zvol/zroot/vms/bhyvevm0' unhide
add path 'zvol/zroot/vms/bhyvevm1' unhide
add path 'tap10*' unhide
```

> **注記**: `/etc/devfs.rules` ファイル内に数値 ID `100` を持つ別の devfs ルールがすでにある場合は、上記リストの ID をまだ使われていない別の番号に置き換えてください。

> **注記**: ZFS ファイルシステムを使用しない場合は、`/etc/devfs.rules` の関連する zvol ルールを省略してください。

```
add path 'zvol' unhide
add path 'zvol/zroot' unhide
add path 'zvol/zroot/vms' unhide
add path 'zvol/zroot/vms/bhyvevm0' unhide
add path 'zvol/zroot/vms/bhyvevm1' unhide
```

これらのルールにより、bhyve は次の動作を行います。

* `bhyvevm0` と `bhyvevm1` というディスクボリュームを持つ仮想マシンを作成する
* `tap10` というプレフィックスを持つ `tap` ネットワークインターフェースを使用する。
  つまり、有効なインターフェース名は `tap10`、`tap100`、`tap101`、…、`tap109`、`tap1000` などのようになります。

  使用可能な `tap` インターフェース名の一部だけにアクセスを制限することで、jail（およびその中の bhyve）からホストや他の jail の `tap` インターフェースが見えないようにできます。
* 「bhyve」をプレフィックスに持つ `nmdm` デバイス（すなわち `/dev/nmdmbhyve0`）を使用する

これらのルールは、必要に応じて異なるゲスト名やインターフェース名に合わせて拡張・変更できます。

> **注記**: ホスト上と 1 つ以上の jail 内の両方で bhyve を使用する予定がある場合は、`tap` や `nmdm` のインターフェース名が共有環境で動作することを忘れないでください。
> たとえば、`/dev/nmdmbhyve0` はホスト上の bhyve か jail 内の bhyve のどちらか一方でのみ使用してください。

変更を読み込むために devfs を再起動します。

```shell
# service devfs restart
```

次に、`/etc/jail.conf` または `/etc/jail.conf.d` に新しい jail の定義を追加します。
インターフェース番号 `$if` と IP アドレスは環境に合わせて置き換えてください。

**例: ファイアウォールによる NAT またはルーティング通信の使用**

```
bhyve {
        $if = 0;
        exec.prestart = "/sbin/ifconfig epair${if} create up";
        exec.prestart += "/sbin/ifconfig epair${if}a up";
        exec.prestart += "/sbin/ifconfig epair${if}a name ${name}0";
        exec.prestart += "/sbin/ifconfig epair${if}b name jail${if}";
        exec.prestart += "/sbin/ifconfig ${name}0 inet 192.168.168.1/27";
        exec.prestart += "/sbin/sysctl net.inet.ip.forwarding=1";

        exec.clean;

        host.hostname = "the-hostname-here";
        vnet;
        vnet.interface = "jail${if}";
        path = "/jails/${name}";
        persist;
        securelevel = 3;
        devfs_ruleset = 100;
        mount.devfs;

        allow.vmm;

        exec.start += "/bin/sh /etc/rc";
        exec.stop = "/bin/sh /etc/rc.shutdown";

        exec.poststop += "/sbin/ifconfig ${name}0 destroy";
}
```

この例では、jail のトラフィックを NAT するために `pf` や `ipfw` などのファイアウォールを使用することを前提としています。
これを実装するための利用可能なオプションの詳細は、[Firewalls](https://docs.freebsd.org/en/books/handbook/firewalls/#firewalls) 章を参照してください。

**例: ブリッジネットワーク接続の使用**

```
bhyve {
        $if = 0;
        exec.prestart = "/sbin/ifconfig epair${if} create up";
        exec.prestart += "/sbin/ifconfig epair${if}a up";
        exec.prestart += "/sbin/ifconfig epair${if}a name ${name}0";
        exec.prestart += "/sbin/ifconfig epair${if}b name jail${if}";
        exec.prestart += "/sbin/ifconfig bridge0 addm ${name}0";
        exec.prestart += "/sbin/sysctl net.inet.ip.forwarding=1";

        exec.clean;

        host.hostname = "the-hostname-here";
        vnet;
        vnet.interface = "jail${if}";
        path = "/jails/${name}";
        persist;
        securelevel = 3;
        devfs_ruleset = 100;
        mount.devfs;

        allow.vmm;

        exec.start += "/bin/sh /etc/rc";
        exec.stop = "/bin/sh /etc/rc.shutdown";

        exec.poststop += "/sbin/ifconfig ${name}0 destroy";
}
```

> **注記**: 先ほど `/etc/devfs.rules` の devfs ルールセット ID `100` を固有の番号に置き換えた場合は、`jail.conf`（原文表記 `jails.conf`）側の数値 ID も忘れずに置き換えてください。

<a id="virtualization-bhyve-jailed-config"></a>
#### jail の設定

jail を初めて起動し、追加の設定作業を行うには次のように入力します。

```shell
# cp /etc/resolv.conf /jails/bhyve/etc
# service jail onestart bhyve
# jexec bhyve
# sysrc ifconfig_jail0="inet 192.168.168.2/27"
# sysrc defaultrouter="192.168.168.1"
# sysrc sendmail_enable=NONE
# sysrc cloned_interfaces="tap100"
# exit
```

jail を有効化して再起動します。

```shell
# sysrc jail_enable=YES
# service jail restart bhyve
```

その後、jail 内で仮想マシンを作成します。
FreeBSD ゲストの場合は、まずインストール ISO をダウンロードします。

```shell
# jexec bhyve
# cd /vms
# fetch -o freebsd.iso https://download.freebsd.org/releases/ISO-IMAGES/14.0/FreeBSD-14.0-RELEASE-amd64-bootonly.iso
```

<a id="virtualization-bhyve-jailed-createvm"></a>
#### jail 内での仮想マシンの作成

仮想マシンを作成するには、まず `bhyvectl` を使って初期化します。

```shell
# jexec bhyve
# bhyvectl --create --vm=bhyvevm0
```

> **注記**: jail から仮想マシンを起動する際には、`bhyvectl` で事前にゲストを作成しておく必要がある場合があります。
> この手順を省略すると、`bhyve` の起動時に次のエラーメッセージが出ることがあります。
>
> `vm_open: vm-name could not be opened. No such file or directory`

最後に、好みの方法でゲストを起動します。

**例: `vmrun.sh` と ZFS による起動**

ZFS ファイルシステム上で `vmrun.sh` を使用する例です。

```shell
# jexec bhyve
# sh /usr/share/examples/bhyve/vmrun.sh -c 1 -m 1024M \
     -t tap100 -d /dev/zvol/zroot/vms/bhyvevm0 -i -I /vms/FreeBSD-14.0-RELEASE-amd64-bootonly.iso bhyvevm0
```

**例: `vmrun.sh` と UFS による起動**

UFS ファイルシステム上で `vmrun.sh` を使用する例です。

```shell
# jexec bhyve
# sh /usr/share/examples/bhyve/vmrun.sh -c 1 -m 1024M \
     -t tap100 -d /vms/bhyvevm0 -i -I /vms/FreeBSD-14.0-RELEASE-amd64-bootonly.iso bhyvevm0
```

**例: ZFS を使った UEFI ゲスト向け bhyve の起動**

UEFI ゲストを使用したい場合は、先に jail 内に必要なファームウェアパッケージ `sysutils/bhyve-firmware` をインストールしておく必要があります。

```shell
# pkg -j bhyve install bhyve-firmware
```

その後、`bhyve` を直接実行します。

```shell
# bhyve -A -c 4 -D -H -m 2G \
        -s 0,hostbridge \
        -s 1,lpc \
        -s 2,virtio-net,tap100 \
        -s 3,virtio-blk,/dev/zvol/zroot/vms/bhyvevm0 \
	-s 4,ahci-cd,/vms/FreeBSD-14.0-RELEASE-amd64-bootonly.iso \
        -s 31,fbuf,tcp=127.0.0.1:5900,w=1024,h=800,tablet \
        -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd \
        -l com1,/dev/nmdbbhyve0A \
        bhyvevm0
```

これにより、VNC 経由に加えて `/dev/nmdbbhyve0B` のシリアルコンソールからも仮想マシン `bhyvevm0` に接続できるようになります。

> **訳注**: 原文のこの例では `/dev/nmdbbhyve0A`・`/dev/nmdbbhyve0B` と記載されていますが、前述の `devfs.rules` の例では `nmdmbhyve*` となっている点に注意してください（名称を揃える必要があります）。

<a id="virtualization-bhyve-nmdm"></a>
### 仮想マシンコンソール

コンソールの切り離し（detach）や再接続（reattach）ができるように、`sysutils/tmux` や `sysutils/screen` などのセッション管理ツールの中で bhyve コンソールを実行すると便利です。
また、bhyve のコンソールを `cu` でアクセス可能なヌルモデム（null modem）デバイスにすることもできます。
これを行うには、`nmdm` カーネルモジュールを読み込み、`-l com1,stdio` を `-l com1,/dev/nmdm0A` に置き換えます。
`/dev/nmdm` デバイスは必要に応じて自動的に作成され、それぞれがヌルモデムケーブルの両端に対応するペア（`/dev/nmdm0A` と `/dev/nmdm0B`）になっています。
詳細は `nmdm(4)` を参照してください。

```shell
# kldload nmdm
# bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc -s 2:0,virtio-net,tap0 -s 3:0,virtio-blk,./linux.img \
    -l com1,/dev/nmdm0A -c 4 -m 1024M linuxguest
# cu -l /dev/nmdm0B
Connected

Ubuntu 13.10 handbook ttyS0

handbook login:
```

コンソールから切断するには、改行（つまり `RETURN` を押す）に続けてチルダ（`~`）、最後にドット（`.`）を入力します。
切断されるのは接続だけであり、ログインセッション自体は有効なまま残る点に注意してください。
そのため、同じコンソールへ別のユーザーが接続すると、最初に認証することなく有効なセッションを利用できてしまう可能性があります。
セキュリティ上の理由から、切断する前にログアウトすることが推奨されます。

`nmdm` デバイスパス内の番号は仮想マシンごとに一意でなければならず、bhyve が起動する前に他のプロセスで使用されていてはなりません。
番号は任意に選ぶことができ、連続した連番から取る必要はありません。
デバイスノードのペア（つまり `/dev/nmdm0a` と `/dev/nmdm0b`）は bhyve がコンソールを接続する際に動的に作成され、シャットダウン時に破棄されます。
仮想マシンを起動するスクリプトを作成する際は、すべての仮想マシンに一意の `nmdm` デバイスが割り当てられるよう注意してください。

<a id="virtualization-bhyve-managing"></a>
### 仮想マシンの管理

仮想マシンごとに `/dev/vmm` にデバイスノードが作成されます。
これにより、管理者は実行中の仮想マシンの一覧を簡単に確認できます。

```shell
# ls -al /dev/vmm
total 1
dr-xr-xr-x   2 root  wheel    512 Mar 17 12:19 ./
dr-xr-xr-x  14 root  wheel    512 Mar 17 06:38 ../
crw-------   1 root  wheel  0x1a2 Mar 17 12:20 guestname
crw-------   1 root  wheel  0x19f Mar 17 12:19 linuxguest
crw-------   1 root  wheel  0x1a1 Mar 17 12:19 otherguest
```

指定した仮想マシンは `bhyvectl` を使って破棄できます。

```shell
# bhyvectl --destroy --vm=guestname
```

この方法で仮想マシンを破棄すると、即座に強制終了されます。未保存のデータはすべて失われ、開いているファイルやファイルシステムが破損するおそれがあります。
仮想マシンを正常にシャットダウンするには、代わりにその bhyve プロセスへ `TERM` シグナルを送ります。これによりゲストに対して ACPI シャットダウンイベントが発行されます。

```shell
# ps ax | grep bhyve
17424  -  SC      56:48.27 bhyve: guestvm (bhyve)
# kill 17424
```

<a id="virtualization-tools-utilities"></a>
### ツールとユーティリティ

bhyve 仮想マシンの構築や管理を簡単にするため、Ports には多数のユーティリティやアプリケーションが用意されています。

**bhyve マネージャ**

| 名前 | ライセンス | パッケージ | ドキュメント |
|---|---|---|---|
| vm-bhyve | BSD-2 | `sysutils/vm-bhyve` | [Documentation](https://github.com/freebsd/vm-bhyve) |
| CBSD | BSD-2 | `sysutils/cbsd` | [Documentation](https://github.com/cbsd/cbsd/tree/develop/share/docs) |
| Virt-Manager | LGPL-3 | `deskutils/virt-manager` | [Documentation](https://virt-manager.org/) |
| Bhyve RC Script | Unknown | `sysutils/bhyve-rc` | [Documentation](https://www.freshports.org/sysutils/bhyve-rc/) |
| bmd | BSD-2 | `sysutils/bmd` | [Documentation](https://github.com/yuichiro-naito/bmd) |
| vmstated | BSD-2 | `sysutils/vmstated` | [Documentation](https://github.com/christian-moerz/vmstated) |

<a id="virtualization-bhyve-onboot"></a>
### 永続的な設定

起動時に bhyve ゲストを自動起動するようにシステムを設定するには、いくつかの設定ファイルを変更する必要があります。

1. `/etc/sysctl.conf`

   ネットワークバックエンドとして `tap` インターフェースを使用する場合、使用する各 `tap` インターフェースを手動で UP にするか、単に次の sysctl を設定します。

   ```
   net.link.tap.up_on_open=1
   ```

2. `/etc/rc.conf`

   仮想マシンの `tap` デバイスを `bridge` 経由でネットワークに接続するには、デバイス設定を `/etc/rc.conf` に永続化する必要があります。
   さらに、`kld_list` 設定変数を通じて、bhyve に必要な `vmm` カーネルモジュールと `nmdm` デバイス用の `nmdm` カーネルモジュールを読み込みます。
   `ifconfig_bridge0` を設定する際は、`<ipaddr>/<netmask>` を物理インターフェース（この例では `igb0`）の実際の IP アドレスに置き換え、物理デバイスからは IP 設定を削除してください。

   ```shell
   # sysrc cloned_interfaces+="bridge0 tap0"
   # sysrc ifconfig_bridge0="inet <ipaddr>/<netmask> addm igb0 addm tap0"
   # sysrc kld_list+="nmdm vmm"
   # sysrc ifconfig_igb0="up"
   ```

<a id="virtualization-bhyve-onboot-bridgenet"></a>
**例: ブリッジデバイスへの IP 設定**

IP `10.10.10.1`、ネットマスク `255.255.255.0` でネットワークに接続された _igb0_ インターフェースを持つホストの場合は、次のコマンドを実行します。

```shell
# sysrc ifconfig_igb0="up"
# sysrc ifconfig_bridge0="inet 10.10.10.1/24 addm igb0 addm tap0"
# sysrc kld_list+="nmdm vmm"
# sysrc cloned_interfaces+="bridge0 tap0"
```

> **警告**: システムの IP アドレス設定を変更すると、現在のリモート接続（SSH など）が切断され、ロックアウトされる可能性があります。
> システムへのアクセスを維持する対策を講じるか、ローカルの端末セッションにログインした状態で変更を行ってください。

<a id="virtualization-host-xen"></a>
## Xen™ ホストとしての FreeBSD

Xen は、Intel® および ARM® アーキテクチャ向けの GPLv2 ライセンスによる [Type 1 ハイパーバイザ](https://en.wikipedia.org/wiki/Hypervisor#Classification)です。
FreeBSD は FreeBSD 8.0 から i386™ および AMD® 64 ビットでの [DomU](https://wiki.xenproject.org/wiki/DomU) および [Amazon EC2](https://en.wikipedia.org/wiki/Amazon_Elastic_Compute_Cloud) 非特権ドメイン（仮想マシン）のサポートを含んでおり、FreeBSD 11.0 からは Dom0 制御ドメイン（ホスト）のサポートも含んでいます。
より高い性能が得られるハードウェア仮想化（HVM）ドメインを優先するため、準仮想化（PV）ドメインのサポートは FreeBSD 11 で削除されました。

Xen™ はベアメタルハイパーバイザであり、BIOS の後に最初に読み込まれるプログラムです。
その後、Domain-0（略して `Dom0`）と呼ばれる特別な特権ゲストが起動されます。
Dom0 はその特別な権限を使って基盤となる物理ハードウェアに直接アクセスするため、高性能なソリューションとなります。
ディスクコントローラやネットワークアダプタにも直接アクセスできます。
Xen™ ハイパーバイザを管理・制御するための Xen™ 管理ツールも Dom0 上で使用され、仮想マシンの作成・一覧表示・破棄を行います。
Dom0 は、しばしば `DomU` と呼ばれる非特権ドメイン向けに仮想ディスクとネットワークを提供します。
Xen™ の Dom0 は他のハイパーバイザ製品におけるサービスコンソールに相当し、DomU は個々のゲスト仮想マシンが動作する場所にあたります。

Xen™ は異なる Xen™ サーバ間で仮想マシンをマイグレーションできます。
2 台の Xen ホストが同じ基盤ストレージを共有している場合、事前に仮想マシンをシャットダウンすることなくマイグレーションを実行できます。
その代わりに DomU を実行したままライブマイグレーションが行われるため、再起動やダウンタイムの計画は不要です。
これはメンテナンス時やアップグレード時間帯に、DomU が提供するサービスを止めずに維持するうえで有用です。
Xen™ のさらに多くの機能は [Xen Wiki Overview ページ](https://wiki.xenproject.org/wiki/Category:Overview)にまとめられています。
ただし、現時点ではすべての機能が FreeBSD でサポートされているわけではありません。

<a id="virtualization-host-xen-requirements"></a>
### Xen™ Dom0 のハードウェア要件

ホスト上で Xen™ ハイパーバイザを実行するには、特定のハードウェア機能が必要です。
FreeBSD を Xen ホスト（Dom0）として実行するには、ホストプロセッサが Intel Extended Page Tables（[EPT](https://en.wikipedia.org/wiki/Extended_Page_Table)）または AMD Nested Page Tables（[NPT](https://en.wikipedia.org/wiki/Rapid_Virtualization_Indexing)）、および Input/Output Memory Management Unit（[IOMMU](https://en.wikipedia.org/wiki/List_of_IOMMU-supporting_hardware)）をサポートしている必要があります。

> **注記**: FreeBSD 13 の Xen™ Dom0 を実行するには、マシンをレガシーブート（BIOS）で起動する必要があります。
> FreeBSD 14 以降では、BIOS モードと UEFI モードの両方で Xen™ Dom0 としての起動に対応しています。

<a id="virtualization-host-xen-dom0-setup"></a>
### Xen™ Dom0 制御ドメインのセットアップ

Xen™ 4.18 をベースとした `emulators/xen-kernel` および `sysutils/xen-tools` パッケージをインストールしてください。

Xen パッケージをインストールした後、Dom0 統合に向けてホストを準備するため設定ファイルを編集する必要があります。
`/etc/sysctl.conf` にエントリを追加して、固定（wired）できるメモリページ数の上限を無効化します。
これを行わないと、より多くのメモリを必要とする DomU 仮想マシンが起動しません。

```shell
# echo 'vm.max_wired=-1' >> /etc/sysctl.conf
```

もう 1 つのメモリ関連の設定として、`/etc/login.conf` を変更し、`memorylocked` オプションを `unlimited` に設定します。
そうしないと、DomU ドメインの作成が `Cannot allocate memory` エラーで失敗する場合があります。
`/etc/login.conf` を変更した後は、`cap_mkdb` を実行してケーパビリティデータベースを更新してください。
詳細は[リソース制限（Resource Limits）](https://docs.freebsd.org/en/books/handbook/security/#security-resourcelimits)を参照してください。

```shell
# sed -i '' -e 's/memorylocked=64K/memorylocked=unlimited/' /etc/login.conf
# cap_mkdb /etc/login.conf
```

`/etc/ttys` に Xen™ コンソール用のエントリを追加します。

```shell
# echo 'xc0     "/usr/libexec/getty Pc"         xterm   onifconsole  secure' >> /etc/ttys
```

`/boot/loader.conf` で Xen™ カーネルを選択することで Dom0 が有効になります。
Xen™ は自身および他の DomU ドメインのために、ホストマシンから CPU やメモリなどのリソースも必要とします。
必要な CPU とメモリの量は、個々の要件やハードウェア性能によって異なります。
この例では、8 GB のメモリと 4 個の仮想 CPU を Dom0 に割り当てています。
また、シリアルコンソールを有効化し、ログ記録オプションも定義しています。

Xen 4.7 パッケージの場合は次のコマンドを使用します。

```shell
# echo 'hw.pci.mcfg=0' >> /boot/loader.conf
# echo 'if_tap_load="YES"' >> /boot/loader.conf
# echo 'xen_kernel="/boot/xen"' >> /boot/loader.conf
# echo 'xen_cmdline="dom0_mem=8192M dom0_max_vcpus=4 dom0pvh=1 console=com1,vga com1=115200,8n1 guest_loglvl=all loglvl=all"' >> /boot/loader.conf
```

Xen バージョン 4.11 以降の場合は、代わりに次のコマンドを使用してください。

```shell
# echo 'if_tap_load="YES"' >> /boot/loader.conf
# echo 'xen_kernel="/boot/xen"' >> /boot/loader.conf
# echo 'xen_cmdline="dom0_mem=8192M dom0_max_vcpus=4 dom0=pvh console=com1,vga com1=115200,8n1 guest_loglvl=all loglvl=all"' >> /boot/loader.conf
```

> **ヒント**: Xen™ が DomU 仮想マシン用に作成するログファイルは `/var/log/xen` に保存されます。
> 問題が発生した場合は、必ずそのディレクトリの内容を確認してください。

システム起動時に `xencommons` サービスを有効化します。

```shell
# sysrc xencommons_enable=yes
```

ここまでの設定で Dom0 が有効なシステムを起動することはできますが、DomU マシン向けのネットワーク機能がありません。
これを解消するため、DomU 仮想マシンがネットワーク接続に使えるよう、システムのメイン NIC を含むブリッジインターフェースを定義します。
_em0_ はホストのネットワークインターフェース名に置き換えてください。

```shell
# sysrc cloned_interfaces="bridge0"
# sysrc ifconfig_bridge0="addm em0 SYNCDHCP"
# sysrc ifconfig_em0="up"
```

Xen™ カーネルを読み込んで Dom0 を起動するため、ホストを再起動します。

```shell
# shutdown -r now
```

Xen™ カーネルの起動に成功して再びシステムへログインしたら、Xen™ 管理ツール `xl` を使ってドメインに関する情報を表示します。

```shell
# xl list
Name                                        ID   Mem VCPUs      State   Time(s)
Domain-0                                     0  8192     4     r-----     962.0
```

この出力から、Dom0（`Domain-0`）が ID `0` で実行中であることが確認できます。
また、先ほど `/boot/loader.conf` で定義したメモリと仮想 CPU が割り当てられていることもわかります。
詳細は [Xen™ Documentation](https://www.xenproject.org/help/documentation.html) を参照してください。
これで DomU ゲスト仮想マシンを作成できるようになりました。

<a id="virtualization-host-xen-domu-setup"></a>
### Xen™ DomU ゲスト仮想マシンの設定

非特権ドメインは、設定ファイルと仮想または物理ハードディスクで構成されます。
DomU 用の仮想ディスクストレージには、`truncate(1)` で作成したファイルか、[ボリュームの作成と破棄](23-zfs.md#zfs-zfs-volume)で説明している ZFS ボリュームを使用できます。
この例では 20 GB のボリュームを使用します。
ZFS ボリューム、FreeBSD ISO イメージ、1 GB の RAM、2 個の仮想 CPU を使って仮想マシンを作成します。
ISO インストールファイルは `fetch(1)` で取得し、`freebsd.iso` というファイル名でローカルに保存します。

```shell
# fetch https://download.freebsd.org/releases/ISO-IMAGES/14.0/FreeBSD-14.0-RELEASE-amd64-bootonly.iso -o freebsd.iso
```

仮想マシンのディスク領域として使用する `xendisk0` という 20 GB の ZFS ボリュームを作成します。

```shell
# zfs create -V20G -o volmode=dev zroot/xendisk0
```

新しい DomU ゲスト仮想マシンはファイルで定義します。
名前、キーマップ、VNC 接続の詳細などの具体的な定義もここに記述します。
次の `freebsd.cfg` には、この例における最小限の DomU 設定が含まれています。

```shell
# cat freebsd.cfg
builder = "hvm"
name = "freebsd"
memory = 1024
vcpus = 2
vif = [ 'mac=00:16:3E:74:34:32,bridge=bridge0' ]
disk = [
'/dev/zvol/tank/xendisk0,raw,hda,rw',
'/root/freebsd.iso,raw,hdc:cdrom,r'
  ]
vnc = 1
vnclisten = "0.0.0.0"
serial = "pty"
usbdevice = "tablet"
```

> **訳注**: 原文の `freebsd.cfg` ではディスクパスが `/dev/zvol/tank/xendisk0` となっていますが、直前の手順で作成したプール名は `zroot`（`/dev/zvol/zroot/xendisk0`）です。環境に合わせてプール名を揃えてください。

各行の詳細は次のとおりです。

1. `builder = "hvm"`: 使用する仮想化の種類を定義します。`hvm` はハードウェア支援仮想化（Hardware Virtual Machine）を指します。仮想化拡張機能を備えた CPU 上でゲストオペレーティングシステムを無変更のまま実行でき、物理ハードウェア上で実行する場合とほぼ同等の性能を発揮します。`generic` が既定値であり、PV ドメインを作成します。
2. `name = "freebsd"`: 同じ Dom0 上で動作する他の仮想マシンと区別するための仮想マシン名です。必須項目です。
3. `memory = 1024`: 仮想マシンに割り当てる RAM 容量（メガバイト単位）です。この量は Dom0 のメモリではなく、ハイパーバイザが利用できる総メモリから差し引かれます。
4. `vcpus = 2`: ゲスト仮想マシンが利用できる仮想 CPU 数です。最高の性能を得るためには、ホストの物理 CPU 数を超える仮想 CPU をゲストに割り当てないでください。
5. `vif = [ 'mac=00:16:3E:74:34:32,bridge=bridge0' ]`: 仮想ネットワークアダプタです。ホストのネットワークインターフェースに接続されたブリッジを指定します。`mac` パラメータは仮想ネットワークインターフェースに設定する MAC アドレスです。このパラメータは省略可能で、MAC を指定しない場合は Xen™ がランダムに生成します。
6. `'/dev/zvol/tank/xendisk0,raw,hda,rw'`: この仮想マシン用のディスクストレージとなるディスク、ファイル、または ZFS ボリュームのフルパスです。オプションや複数のディスク定義はカンマで区切ります。
7. `'/root/freebsd.iso,raw,hdc:cdrom,r'`: 最初のオペレーティングシステムをインストールするためのブートメディアを定義します。この例では、先ほどダウンロードした ISO イメージです。その他の種類のデバイスや設定可能なオプションについては Xen™ のドキュメントを参照してください。
8. `vnc = 1` 以下: DomU のシリアルコンソールへの VNC 接続を制御するオプションです。順に、VNC サポートの有効化、待ち受ける IP アドレスの定義、シリアルコンソール用のデバイスノード、マウスなどの入力デバイスを正確に位置合わせするための入力方式を指定します。`keymap` は使用するキーマップを定義し、既定値は `english` です。

必要なオプションをすべて含めてファイルを作成したら、`xl create` に引数として渡して DomU を作成します。

```shell
# xl create freebsd.cfg
```

> **注記**: Dom0 を再起動するたびに、DomU を再作成するには設定ファイルを再び `xl create` に渡す必要があります。
> 既定では、再起動後に作成されるのは Dom0 のみであり、個々の仮想マシンは自動作成されません。
> 仮想マシンは仮想ディスク上にオペレーティングシステムを保存しているため、中断した状態から続行できます。
> 仮想マシンの構成は時間とともに変化することがあります（たとえばメモリを増設する場合など）。
> 必要なときにゲスト仮想マシンを再作成できるよう、仮想マシンの設定ファイルは適切にバックアップして保管しておいてください。

`xl list` の出力により、DomU が作成されたことを確認できます。

```shell
# xl list
Name                                        ID   Mem VCPUs      State   Time(s)
Domain-0                                     0  8192     4     r-----  1653.4
freebsd                                      1  1024     1     -b----   663.9
```

ベースオペレーティングシステムのインストールを開始するには、VNC クライアントを起動し、ホストのメインネットワークアドレスまたは `freebsd.cfg` の `vnclisten` 行で定義した IP アドレスへ接続します。
オペレーティングシステムのインストールが完了したら、DomU をシャットダウンし、VNC ビューアを切断します。
`freebsd.cfg` を編集し、`cdrom` 定義の行を削除するか、行頭に `#` 文字を挿入してコメントアウトします。
この新しい設定を読み込むには、`xl destroy` に名前または ID を引数として渡して古い DomU を削除する必要があります。
その後、修正した **freebsd.cfg** を使って再作成します。

```shell
# xl destroy freebsd
# xl create freebsd.cfg
```

すると、VNC ビューアを使って再びマシンへアクセスできるようになります。
今回はオペレーティングシステムがインストールされた仮想ディスクから起動し、仮想マシンとして使用できます。

<a id="virtualization-host-xen-troubleshooting"></a>
### トラブルシューティング

この節には、FreeBSD を Xen™ ホストまたはゲストとして使用する際に見つかった問題を切り分けるための基本的な情報が含まれています。

<a id="virtualization-host-xen-troubleshooting-host"></a>
#### ホスト起動のトラブルシューティング

以下のトラブルシューティングのヒントは Xen™ 4.11 以降を対象としている点に注意してください。
引き続き Xen™ 4.7 を使用していて問題が発生している場合は、より新しいバージョンの Xen™ への移行を検討してください。

ホスト起動時の問題を切り分けるには、シリアルケーブルまたはデバッグ用 USB ケーブルが必要です。
`loader.conf` にある `xen_cmdline` オプションに引数を追加することで、Xen™ の詳細な起動出力を得ることができます。
関連するデバッグオプションの例を挙げます。

* `iommu=debug`: iommu に関する追加の診断情報を出力するために使用できます。
* `dom0=verbose`: dom0 の構築プロセスに関する追加の診断情報を出力するために使用できます。
* `sync_console`: 同期コンソール出力を強制するフラグです。レート制限によってメッセージが失われるのを防ぐためデバッグ時に有用です。ただし、悪意あるゲストがコンソールを使って Xen™ に対する DoS 攻撃を行えるようになるため、本番環境では決してこのオプションを使用しないでください。

問題を特定するため、FreeBSD も verbose モードで起動する必要があります。
verbose 起動を有効にするには次のコマンドを実行します。

```shell
# echo 'boot_verbose="YES"' >> /boot/loader.conf
```

これらのオプションのいずれも問題の解決に役立たない場合は、シリアル起動ログを [freebsd-xen@FreeBSD.org](mailto:freebsd-xen@FreeBSD.org) および [xen-devel@lists.xenproject.org](mailto:xen-devel@lists.xenproject.org) へ送付して詳細な解析を依頼してください。

<a id="virtualization-host-xen-troubleshooting-guest"></a>
#### ゲスト作成のトラブルシューティング

ゲストを作成する際にも問題が発生することがあります。以下では、ゲスト作成の問題を診断しようとする際に役立つ情報を紹介します。

ゲスト作成が失敗する最も一般的な原因は、`xl` コマンドが何らかのエラーを出力して 0 以外の終了コードで終了することです。
表示されたエラーだけでは問題を特定するのに不十分な場合は、`v` オプションを繰り返し指定することで `xl` からより詳細な出力を得ることができます。

```shell
# xl -vvv create freebsd.cfg
Parsing config from freebsd.cfg
libxl: debug: libxl_create.c:1693:do_domain_create: Domain 0:ao 0x800d750a0: create: how=0x0 callback=0x0 poller=0x800d6f0f0
libxl: debug: libxl_device.c:397:libxl__device_disk_set_backend: Disk vdev=xvda spec.backend=unknown
libxl: debug: libxl_device.c:432:libxl__device_disk_set_backend: Disk vdev=xvda, using backend phy
libxl: debug: libxl_create.c:1018:initiate_domain_create: Domain 1:running bootloader
libxl: debug: libxl_bootloader.c:328:libxl__bootloader_run: Domain 1:not a PV/PVH domain, skipping bootloader
libxl: debug: libxl_event.c:689:libxl__ev_xswatch_deregister: watch w=0x800d96b98: deregister unregistered
domainbuilder: detail: xc_dom_allocate: cmdline="", features=""
domainbuilder: detail: xc_dom_kernel_file: filename="/usr/local/lib/xen/boot/hvmloader"
domainbuilder: detail: xc_dom_malloc_filemap    : 326 kB
libxl: debug: libxl_dom.c:988:libxl__load_hvm_firmware_module: Loading BIOS: /usr/local/share/seabios/bios.bin
...
```

詳細な出力を見ても問題の診断に役立たない場合は、`/var/log/xen` に QEMU および Xen™ ツールスタックのログもあります。
ログ名にはドメイン名が付加されるため、ドメイン名が `freebsd` であれば `/var/log/xen/xl-freebsd.log` や、多くの場合 `/var/log/xen/qemu-dm-freebsd.log` が見つかります。
どちらのログファイルにもデバッグに有用な情報が含まれている場合があります。
これらすべてを試しても問題が解決しない場合は、問題の説明とできる限り多くの情報を [freebsd-xen@FreeBSD.org](mailto:freebsd-xen@FreeBSD.org) および [xen-devel@lists.xenproject.org](mailto:xen-devel@lists.xenproject.org) へ送付して助けを求めてください。
