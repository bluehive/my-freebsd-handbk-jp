<a id="usb-device-mode"></a>
# 第29章 USB デバイスモード / USB OTG（USB Device Mode / USB OTG）

> **ドラフト**: 本ファイルは現在翻訳作業中です。全節の翻訳および自己校正が完了するまでドラフト扱いです。

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/usb-device-mode/)の「Chapter 29. USB Device Mode / USB OTG」（既存 TOC ID 28）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/usb-device-mode/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザーのプロンプトを示します。

<a id="usb-device-mode-synopsis"></a>
## 概要

本章では、FreeBSD における USB デバイスモードおよび USB On The Go（USB OTG）の使い方を説明します。対象には、仮想シリアルコンソール、仮想ネットワークインターフェース、仮想 USB ドライブが含まれます。

多くの組み込みボードに搭載されているような USB デバイスモードまたは USB OTG 対応ハードウェアで動作している場合、FreeBSD の USB スタックは*デバイスモード*で動作できます。デバイスモードを使うと、コンピュータ自身をシリアルポート、ネットワークアダプタ、マスストレージ、またはそれらの組み合わせといったさまざまな USB デバイスクラスとして見せられます。ノート PC やデスクトップ PC などの USB ホストからは、物理的な USB デバイスと同じようにアクセスできます。デバイスモードは「USB ガジェットモード」と呼ばれることもあります。

ハードウェアがデバイスモード機能を提供する方法は、大きく分けて 2 つあります。1 つはデバイスモードのみに対応する専用の「クライアントポート」を使う方式、もう 1 つはデバイスモードとホストモードの両方を提供できる USB OTG ポートを使う方式です。USB OTG ポートの場合、ポートに接続された相手に応じて、USB スタックがホスト側とデバイス側を自動的に切り替えます。USB メモリのような USB デバイスを接続すると FreeBSD はホストモードに切り替わり、コンピュータのような USB ホストを接続するとデバイスモードに切り替わります。単一用途の「クライアントポート」は常にデバイスモードで動作します。

FreeBSD が USB ホストにどのデバイスを見せるかは、`hw.usb.template` sysctl で決まります。シリアル端末など単一のデバイスを提供するテンプレートもあれば、同時に利用できる複数のデバイスを提供するテンプレートもあります。たとえばテンプレート 10 は、マスストレージデバイス、シリアルコンソール、ネットワークインターフェースの 3 つを提供します。利用できる値の一覧は `usb_template(4)` を参照してください。

ハードウェアやホスト側のオペレーティングシステムによっては、設定変更をホストに認識させるために、ケーブルを物理的に抜き差しするか、システム固有の方法で USB バスを強制的に再スキャンする必要がある点に注意してください。ホスト側で FreeBSD が動作している場合は、`usbconfig(8)` の `reset` を使えます。USB ホストがすでに USB OTG ソケットに接続されている状態で `usb_template.ko` をロードした場合も、この操作が必要です。

本章を読むと、次の内容を学べます。

* FreeBSD で USB デバイスモード機能をセットアップする方法
* FreeBSD で仮想シリアルポートを設定する方法
* 各種オペレーティングシステムから仮想シリアルポートへ接続する方法
* 仮想 USB ネットワークインターフェースを提供するように FreeBSD を設定する方法
* 仮想 USB ストレージデバイスを提供するように FreeBSD を設定する方法

<a id="usb-device-mode-terminals"></a>
## USB 仮想シリアルポート

> **訳注**: 原文ではこの見出しの下に本文がなく、内容は以下の小節にあります。

<a id="chapter-29-heading-04"></a>
### USB デバイスモードのシリアルポート設定

仮想シリアルポート機能は、テンプレート番号 3、8、10 で提供されます。なお、テンプレート 3 は特別なドライバや INF ファイルなしで Microsoft Windows 10 でも動作します。その他のホスト OS では、3 つのテンプレートすべてが動作します。利用には `usb_template(4)` と `umodem(4)` の両方のカーネルモジュールがロードされている必要があります。

USB デバイスモードのシリアルポートを有効にするには、次の行を `/etc/ttys` に追加します。

```
ttyU0	"/usr/libexec/getty 3wire"	vt100	onifconsole secure
ttyU1	"/usr/libexec/getty 3wire"	vt100	onifconsole secure
```

次に、以下の行を `/etc/devd.conf` に追加します。

```
notify 100 {
	match "system"		"DEVFS";
	match "subsystem"	"CDEV";
	match "type"		"CREATE";
	match "cdev"		"ttyU[0-9]+";
	action "/sbin/init q";
};
```

`devd(8)` がすでに動作している場合は、設定を再読み込みします。

```shell
# service devd restart
```

起動時に必要なモジュールがロードされ、正しいテンプレートが設定されるように、次の行を `/boot/loader.conf` に追加します（ファイルが存在しない場合は作成します）。

```shell
umodem_load="YES"
hw.usb.template=3
```

再起動せずにモジュールをロードしてテンプレートを設定するには、次のように実行します。

```shell
# kldload umodem
# sysctl hw.usb.template=3
```

<a id="chapter-29-heading-05"></a>
### FreeBSD から USB デバイスモードのシリアルポートへ接続する

USB デバイスモードのシリアルポートを提供するように設定したボードへ接続するには、ノート PC などの USB ホストをボードの USB OTG ポートまたは USB クライアントポートに接続します。ホスト側で `pstat -t` を実行して端末ラインを一覧表示すると、一覧の末尾付近に「ttyU0」のような USB シリアルポートが表示されます。接続を開くには、次のように実行します。

```shell
# cu -l /dev/ttyU0
```

`Enter` キーを数回押すと、ログインプロンプトが表示されます。

<a id="chapter-29-heading-06"></a>
### macOS から USB デバイスモードのシリアルポートへ接続する

USB デバイスモードのシリアルポートを提供するように設定したボードへ接続するには、ノート PC などの USB ホストをボードの USB OTG ポートまたは USB クライアントポートに接続します。接続を開くには、次のように実行します。

```shell
# cu -l /dev/cu.usbmodemFreeBSD1
```

<a id="chapter-29-heading-07"></a>
### Linux から USB デバイスモードのシリアルポートへ接続する

USB デバイスモードのシリアルポートを提供するように設定したボードへ接続するには、ノート PC などの USB ホストをボードの USB OTG ポートまたは USB クライアントポートに接続します。接続を開くには、次のように実行します。

```shell
# minicom -D /dev/ttyACM0
```

<a id="chapter-29-heading-08"></a>
### Microsoft Windows 10 から USB デバイスモードのシリアルポートへ接続する

USB デバイスモードのシリアルポートを提供するように設定したボードへ接続するには、ノート PC などの USB ホストをボードの USB OTG ポートまたは USB クライアントポートに接続します。接続を開くには、PuTTY などのシリアル端末プログラムが必要です。Windows で使用されている COM ポート名を確認するには、デバイス マネージャー（Device Manager）を起動して「ポート (COM と LPT)」（Ports (COM & LPT)）を展開します。「USB シリアル デバイス (COM4)」（USB Serial Device (COM4)）のような名前が表示されます。PuTTY など好みのシリアル端末プログラムを起動し、PuTTY のダイアログで「Connection type」を「Serial」に設定し、「Serial line」入力欄にデバイス マネージャーで確認した `COMx` を入力して「Open」をクリックします。
