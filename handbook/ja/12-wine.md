<a id="wine"></a>
# 第12章 WINE

本章では、Windows向けアプリケーションをFreeBSDで動かすためのWINEと、その設定・管理方法を説明します。

<a id="wine-synopsis"></a>
## 概要

[WINE](https://www.winehq.org/)は **Wine Is Not an Emulator** の略です。Windowsアプリケーションからの要求をFreeBSDなどのホストOSで扱える形へ変換し、必要に応じて応答も変換する互換層です。アプリケーションが期待するWindowsのインターフェースや資源を提供します。

コンピュータ全体を再現して別のOSを起動する方式とは異なり、通常はWindows本体をゲストOSとして起動しません。QEMUなどを使う仮想マシンでは、完全なゲストOSをインストールでき、アプリケーションから見た環境も実機に近くなります。一方、ゲスト用のメモリやCPUなどが必要です。原文はハードウェアのソフトウェアエミュレーションによる遅さも説明していますが、ハードウェア支援を利用する仮想化を含め、速度や資源の扱いは方式によって異なります。

WINEは要求をその場で変換するため、比較的少ない資源で動かせる可能性があります。ただし、Windowsの機能や更新を追い続ける必要があり、正しく動かない、起動しない、そもそもインストールできないアプリケーションもあります。速度も一律には保証されません。FreeBSDで特定のWindowsアプリケーションを使いたいときに、試す価値のある選択肢です。

本章で扱う内容は次のとおりです。

- WINEのインストールと、仮想化などとの仕組みの違い。
- アプリケーションに合わせた環境の調整。
- インストールを助けるGUIツール。
- よくある問題と対処の手掛かり。
- 複数ユーザーが使うFreeBSD環境での注意点。

読む前に、[UNIXとFreeBSDの基本](03-basics.md)、[FreeBSDのインストール](02-bsdinstall.md)、[ネットワーク接続](https://docs.freebsd.org/en/books/handbook/advanced-networking/)、[追加ソフトウェアの導入](04-ports.md)を理解しておくと役立ちます。

**訳注：** 原文には旧来の32ビット版パッケージ構成や開発状況の説明が残っています。以下のパッケージ名・画面・将来計画は固定原文に基づく例として読み、利用するFreeBSDとWINEの版に合わせて確認してください。

<a id="wine-overview-concepts"></a>
## WINEの仕組みと基本概念

WINEは多くの部品からなるシステムです。導入前に、何を提供し、どこでFreeBSDと結び付いているかを押さえておきましょう。

<a id="what-is-wine"></a>
### WINEとは

[概要](#wine-synopsis)で述べたように、WINEはWindowsアプリケーションをほかのOSで動かす互換層です。原文ではFreeBSD、macOS、Androidなどを例に挙げていますが、対応範囲はOS・CPU・版によって異なります。

Windowsの実行ファイルを起動すると、WINEは大きく次の二つの役割を果たします。

1. アプリケーションからWindowsのように見えるインターフェースを用意します。たとえばメモリを要求するとき、アプリケーションはWindowsと同じような操作を行えます。
2. その要求をホストOSの操作へ変換します。メモリの確保や、保存したデータの取り出しをFreeBSD側で行い、Windowsアプリケーションが期待する形で返します。

<a id="wine-and-the-os-system"></a>
### FreeBSD上のWINEの構成

WINEを導入すると、主に次の部品が配置されます。以下のファイル名は原文の例であり、実際の配置や形式は版によって変わります。

- Windows実行ファイルの起動、WINE環境の設定、WINE対応プログラムのコンパイルなどを行うFreeBSD用のプログラム。
- Windowsの基本機能を実装した多数のライブラリ。たとえば `/lib/wine/api-ms-core-memory-l1-1-1.dll.so` は、原文でメモリ関連の例として挙げられています。
- よく使われるWindowsの道具に相当する実行ファイル。例として `/lib/wine/notepad.exe.so` はメモ帳相当の機能を提供します。
- フォントなどの補助データ。Tahomaはインストール先の `share/wine/fonts/tahoma.ttf` に置かれる例が示されています。

<a id="graphical-versus-text-modeterminal-programs-in-wine"></a>
### GUIプログラムと端末プログラム

FreeBSDでは端末用プログラムも日常的に使いますが、Windowsの主要なアプリケーションはGUIを前提としています。WINEの道具も通常はGUIプログラムの起動を中心に設計されています。

文字ベースのCUI（Console User Interface）プログラムを動かす方法もあります。**Bare Streams**では出力を直接標準出力へ流します。`wineconsole` を使う場合は、**user**バックエンドと**curses**バックエンドを選べます。合わせて三つの方式です。詳細は[Wine User’s GuideのCUIの説明](https://wiki.winehq.org/Wine_User%27s_Guide#Text_mode_programs_.28CUI:_Console_User_Interface.29)を参照してください。

<a id="wine-derivative-projects"></a>
### WINEから派生したプロジェクト

WINEは成熟したオープンソースプロジェクトであり、それを土台に導入や互換性調整を付け加えた製品・ツールも作られています。

<a id="commercial-wine-implementations"></a>
#### 商用製品などでの利用

WINEのLGPLライセンスの下で、独自製品の中核としてWINEを利用する企業もあります。原文では次の二つを紹介しています。

**CodeWeavers CrossOver**は、導入を簡単にし、よく使われるアプリケーションの互換性を改善する製品です。CodeWeaversは多くの改良をWINE本体にも還元しています。かつてFreeBSD向けの版もありましたが、原文では長らく開発が止まっていると説明されています。[FreeBSD専用フォーラム](https://www.codeweavers.com/compatibility/crossover/forum/freebsd)への参照も、現行製品のサポートを保証するものではありません。

**Steam Proton**は、ValveのSteamでWindowsゲームをほかのOS上で動かすためにWINEを利用する取り組みです。原文はLinuxを主対象とし、macOSにも言及していますが、その記述を現在のmacOS対応の保証として扱わないでください。FreeBSDネイティブのSteamクライアントではなく、Linux版クライアントを[Linux互換機能](11-linuxemu.md)で利用する取り組みが紹介されています。

<a id="wine-companion-programs"></a>
#### WINEを補助するプログラム

標準のWINEと組み合わせ、環境の準備やアプリケーションの導入を簡単にするツールもあります。本章後半の[管理用GUI](#wine-management-guis)では、WinetricksとMizutamariを紹介します。

<a id="alternatives-to-wine"></a>
### WINE以外の選択肢

目的に応じて、次の方法も検討できます。

- **デュアルブート**：Windowsを直接起動してアプリケーションを使います。FreeBSDを終了して切り替えるため、両方のOSのプログラムを同時に使いたい用途には向きません。
- **仮想マシン**：QEMU、bhyve、VirtualBoxなどでゲストOSとしてWindowsを動かします。管理ツールで作成・運用しやすくなっていますが、CPU・メモリなどの資源をゲストにも割り当てる必要があります。詳細は[仮想化の章](https://docs.freebsd.org/en/books/handbook/virtualization/)を参照してください。
- **リモート接続**：別のWindowsコンピュータへRDPなどで接続し、その画面を通してプログラムやデータを利用します。VNCも、接続先に対応するサーバがあれば選択肢になります。原文はxrdpをクライアントの例として挙げていますが、[xrdpはRDPサーバ](https://www.xrdp.org/)です。接続する側ではRDPクライアントを使います。

<a id="installing-wine-on-freebsd"></a>
## FreeBSDへWINEをインストールする

WINEは `pkg` でバイナリパッケージを導入するか、Portsから構築できます。

<a id="wine-prerequistes"></a>
### 事前に用意するもの

**GUI環境**

多くのWindowsアプリケーションはグラフィカルな画面を必要とします。まず自分の使うデスクトップやウィンドウシステムを導入し、正常に動くことを確認すると、後の切り分けが容易です。原文はWINEの依存関係としてWaylandコンポジタが導入される構成に触れていますが、これは版やパッケージの選択によって異なります。

**wine-gecko**

一部のWindowsアプリケーションは、Internet Explorerなどのウェブ表示部品が存在することを前提にしています。WINEではMozillaのGeckoエンジンを使う部品でこの機能を補います。必要なときにダウンロードを促される場合もありますが、事前に導入することもできます。

```shell
# pkg install wine-gecko
```

Portsから構築する場合は次のとおりです。

```shell
# cd /usr/ports/emulators/wine-gecko
# make install
```

**wine-mono**

Microsoftの.NETに対応するオープンソース実装であるMonoを導入します。.NETを利用するアプリケーションの動作に必要となる場合がありますが、すべての.NETアプリケーションの互換性を保証するものではありません。

```shell
# pkg install wine-mono
```

Portsを使う場合は次のとおりです。

```shell
# cd /usr/ports/emulators/wine-mono
# make install
```

<a id="installing-wine"></a>
### WINE本体を導入する

前提となる環境を整えたら、パッケージを導入します。

```shell
# pkg install wine
```

Portsから構築する場合は次の操作です。

```shell
# cd /usr/ports/emulators/wine
# make install
```

<a id="thirtytwo-vs-sixtyfour-bit-wine"></a>
### 32ビットと64ビットを考慮する

Windowsアプリケーションには32ビット版と64ビット版があります。古いゲームなどを使いたい場合には、アプリケーションだけでなく、FreeBSD・WINE・prefixの対応するアーキテクチャを確認する必要があります。FreeBSDの64ビット対応は5.x系列からありますが、それだけで任意の32ビットWindowsアプリケーションを実行できるとは限りません。

原文が挙げる構成例は次の二つです。

- 64ビットのコンピュータで64ビットのWindowsソフトウェアを動かす場合は、前節のPortsを導入し、ホストに対応する64ビット版を使います。
- 古い32ビット機を使う場合は、i386版FreeBSDと対応するPortsを使う構成が挙げられています。利用するリリースでその機種・アーキテクチャがサポートされるか確認が必要です。

原文は「三つの構成」と述べますが、列挙は二つです。32ビット版と64ビット版の共存に関する旧来の説明は[FAQ](#how-to-install-32-bit-and-64-bit-wine-on-the-same-system)も参照してください。

<a id="running-first-wine-program"></a>
## 最初のプログラムを動かす

WINEを導入したら、まず単純なアプリケーションで試します。複雑なインストールを必要とせず、展開してすぐ動くportable版や、一つの実行ファイルで動作するプログラムが試用に向いています。

<a id="running-a-program-from-the-command-line"></a>
### 端末から起動する

実行ファイルのあるディレクトリへ移動し、次のように起動します。

```shell
% wine program.exe
```

コマンドライン引数を受け取るプログラムでは、通常どおり実行ファイル名の後へ引数を追加します。

```shell
% wine program2.exe -file file.txt
```

スクリプトなどでは、実行ファイルの絶対パスを指定することもできます。

```shell
% wine /home/user/bin/program.exe
```

<a id="running-a-program-from-a-gui"></a>
### GUIから起動する

WINEの導入後、Windows実行ファイル（`.EXE`）との関連付けが設定されていれば、ファイルマネージャからほかのプログラムと同様に起動できます。クリック回数はデスクトップの設定によります。

関連付けを確認するには、ファイルを右クリックし、開くためのメニューで **Wine Windows Program Loader** を探します。

![GUIから起動する：wine-run-np++-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-run-np++-1.png)

期待どおり動かなければ端末から起動し、表示されるメッセージを調べます。WINEが既定の起動プログラムになっていない場合は、デスクトップやファイルマネージャのMIME形式・拡張子の関連付けを確認してください。

<a id="configuring-wine-installation"></a>
## WINE環境を設定する

WINEを使いこなすには、Windowsアプリケーションの実行環境をどこに保存し、どの単位で設定するかを理解することが大切です。本節では、その基本となるprefixと設定ツールを説明します。

<a id="wine-prefixes"></a>
### WINEのprefix

**prefix**は、Windowsアプリケーションの実行に必要な設定や補助ファイルをまとめたディレクトリです。既定の場所は `$HOME/.wine` ですが、別の場所も指定できます。初回起動時には、おおむね次の構成が作られます。

- `.update-timestamp`：WINEの初期設定ファイル `wine.inf` の更新時刻を記録し、prefixの更新が必要か判断するために使います。原文の `/usr/share/wine/wine.inf` というパスは配置例であり、インストール先によって異なります。
- `dosdevices/`：Windows形式のドライブ名などとFreeBSD側の資源との対応を保持します。通常、`c:` は下記の `drive_c`、`z:` はホストのルートディレクトリ `/` へのシンボリックリンクです。
- `drive_c/`：WindowsのCドライブに相当します。`Users`、`Windows` などのディレクトリが入り、アプリケーションはアーキテクチャに応じて `Program Files` や `Program Files (x86)` にインストールされます。これはWINEが用意する互換環境であり、Windows本体をインストールするわけではありません。
- `system.reg`：prefix内のWindows環境全体に関するレジストリ情報です。
- `user.reg`：アプリケーションやレジストリエディタで変更した、利用者固有の設定です。
- `userdef.reg`：新しく作成する利用者向けの既定設定です。

<a id="creating-and-using-wine-prefixes"></a>
### prefixを作成して使い分ける

既定の `$HOME/.wine/` だけでなく、複数のprefixを用意できます。アプリケーションが要求するWindowsのバージョンを変えたい場合や、特別なDLL・設定変更をほかのアプリケーションから切り離したい場合に便利です。普段使うprefixを複製し、互換性を試すための環境にする方法もあります。

端末から新しいprefixを作るには、`WINEPREFIX` に保存先を指定して `winecfg` を実行します。`username` は自分の利用者名に置き換えます。

```shell
% WINEPREFIX="/home/username/.wine-new" winecfg
```

指定先にprefixがなければ作成し、そのprefixの設定画面を開きます。アプリケーションを起動するときも同じ環境変数を指定すると、使うprefixを選べます。

```shell
% WINEPREFIX="/home/username/.wine-new" wine program.exe
```

<a id="configuring-wine-prefixes-with-winecfg"></a>
### winecfgでprefixを設定する

`winecfg` はprefixをGUIで設定するツールです。対象を確実に指定するには、前節のように `WINEPREFIX` を設定して起動します。

**Applications**タブで選んだアプリケーションによって、**Libraries**と**Graphics**タブの変更が適用される範囲も変わります。全体の既定設定を変更するのか、特定のアプリケーションだけを調整するのかを確認してください。詳細は[Wine User’s GuideのUsing Winecfg](https://wiki.winehq.org/Wine_User%27s_Guide#Using_Winecfg)を参照してください。

<a id="applications"></a>
#### Applications：アプリケーションごとの互換設定

![Applications：アプリケーションごとの互換設定：wine-config-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-1.png)

このタブでは、アプリケーションに対してどのWindowsバージョンとして振る舞うかを設定します。最初からある **Default Settings** はprefix全体の既定設定で、削除できません。

個別設定を追加するには、**Add application**を押し、実行ファイルを選び、そのアプリケーションで使うWindowsバージョンを選択します。

<a id="libraries"></a>
#### Libraries：DLLの優先順位

![Libraries：DLLの優先順位：wine-config-2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-2.png)

WINEにはWindowsのライブラリと同じ機能を提供する実装が含まれます。ただし、新しいWindowsアプリケーションが必要とする機能に対応していない場合もあります。そこで、ライブラリごとにWINE内蔵実装とWindows由来の実装のどちらを優先するかを指定できます。同じコンピュータ上のWindows環境にあるライブラリを利用する場合などに使います。

**New override for library**で対象を選んで**Add**を押すと、**Existing overrides**に追加され、たとえば `native, builtin` という順序が表示されます。項目を選んで**Edit**を押し、読み込み順序を調整します。この操作はDLLそのものを選択・コピーするファイルダイアログではありません。Windows由来のDLLを使うなら、対象に対応した版を適切な場所へ用意する必要があります。互換性のないファイルへの置き換えは、予期しない動作の原因になります。

<a id="graphics"></a>
#### Graphics：ウィンドウと表示

![Graphics：ウィンドウと表示：wine-config-3.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-3.png)

WindowsアプリケーションのウィンドウとFreeBSDのデスクトップとの関係を調整します。

- 全画面時にマウスを自動的に捕捉するか。
- FreeBSD側のウィンドウマネージャにタイトルバーなどの装飾を任せるか。
- ウィンドウの移動やサイズ変更などをウィンドウマネージャに任せるか。
- 仮想デスクトップを作り、その内側でWINEのアプリケーションを実行するか。有効にすると、**Desktop size**で寸法を指定できます。
- WINEで動かすアプリケーションの画面解像度・表示の大きさをどう設定するか。

<a id="desktop-integration"></a>
#### Desktop Integration：デスクトップとの統合

![Desktop Integration：デスクトップとの統合：wine-config-4.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-4.png)

テーマや見た目、WINE側でMIME形式とアプリケーションの関連付けを扱うかどうか、Windows環境内の既知のフォルダとFreeBSD側ディレクトリの対応を設定します。フォルダの対応を変更するには、対象を選んで**Browse**を押し、使用するディレクトリを選びます。

<a id="drives"></a>
#### Drives：ドライブとディレクトリの対応

![Drives：ドライブとディレクトリの対応：wine-config-5.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-5.png)

FreeBSD側のディレクトリをWindows形式のドライブ文字に対応付けます。表示内容はprefix内の `dosdevices/` と対応しており、GUIの変更はそのディレクトリに反映されます。逆に、適切な形式のシンボリックリンクを作ると、このタブにも表示されます。

たとえば `/mnt/cdrom` にマウントしたCD-ROMを追加するには、**Add**を押し、未使用のドライブ文字を選んで**OK**を押します。続いて**Path**にパスを入力するか、**Browse**で選びます。

ドライブの種類は通常自動判定されますが、手動指定も可能です。詳しくは[Wine User’s GuideのDrive Settings](https://wiki.winehq.org/Wine_User%27s_Guide#Drive_Settings)を参照してください。

<a id="audio"></a>
#### Audio：音声出力

![Audio：音声出力：wine-config-6.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-6.png)

Windowsアプリケーションの音声をFreeBSDのサウンドシステムへ渡すための設定です。ドライバや既定デバイスを選び、テスト音で出力を確認できます。

<a id="about"></a>
#### About：WINEの情報

![About：WINEの情報：wine-config-7.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/wine-config-7.png)

WINEプロジェクトの情報とウェブサイトへのリンクを表示します。任意で利用者情報も入力できます。原文では、この画面へ入力した情報を外部へ送信しないと説明しています。

<a id="wine-management-guis"></a>
## WINEの管理用GUI

`winecfg` は主に既存prefixの設定を変更するための道具です。アプリケーションの導入や、それに適した環境の構築を助ける、さらに高機能なツールもあります。ここではWinetricksとMizutamariを紹介します。

<a id="winetricks"></a>
### Winetricks

[Winetricks](https://github.com/Winetricks/winetricks)は複数のOSで使えるWINEの補助ツールです。WINE本体とは別の貢献者グループが開発しています。よく使われるアプリケーションを動かすために、設定の調整や必要なDLLの取得などを自動化したレシピを提供します。

<a id="installing-winetricks"></a>
#### Winetricksのインストール

原文では、32ビット版WINEを別のパッケージとして導入する構成を前提に、次の例を示しています。このパッケージ構成や依存関係は版によって変わるため、利用中のリポジトリで提供される構成を確認してください。

```shell
# pkg install i386-wine winetricks
```

Portsから構築する場合の原文の例は次のとおりです。

```shell
# cd /usr/ports/emulators/i386-wine
# make install
# cd /usr/ports/emulators/winetricks
# make install
```

手動導入が必要な場合は、[Winetricksのリポジトリ](https://github.com/Winetricks/winetricks)にある手順を確認します。

<a id="using-winetricks"></a>
#### Winetricksを使う

次のコマンドで起動します。原文の操作例は32ビットprefixを前提にしています。

```shell
% winetricks
```

起動画面には複数の操作が表示されます。

![Winetricksを使う：winetricks-run-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-run-1.png)

**Install an application**、**Install a benchmark**、**Install a game**を選ぶと、対応するソフトウェアの一覧が表示されます。以下はアプリケーションの例です。

![Winetricksを使う：winetricks-run-2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-run-2.png)

導入する項目を選んで**OK**を押すと処理が始まります。互換性の問題を回避する設定の途中で、警告のような通知が出ることもあります。原文の例では情報通知ですが、すべてのエラーを無視してよいという意味ではありません。

![Winetricksを使う：winetricks-app-install-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-app-install-1.png)

必要な調整の後、アプリケーション本来のインストーラが起動します。

![Winetricksを使う：winetricks-app-install-2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-app-install-2.png)

導入が完了すると、対応するデスクトップ環境では通常のアプリケーションメニューから起動できます。次はLXQtの例です。

![Winetricksを使う：winetricks-menu-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-menu-1.png)

削除するときはWinetricksを再び起動し、**Run an uninstaller**を選びます。

![Winetricksを使う：winetricks-uninstall-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-uninstall-1.png)

Windows形式のプログラム一覧で対象を選び、**Modify/Remove**を押します。

![Winetricksを使う：winetricks-uninstall-2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-uninstall-2.png)

アプリケーションに付属するインストーラが起動するので、その削除機能を使います。

![Winetricksを使う：winetricks-uninstall-3.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/winetricks-uninstall-3.png)

<a id="homura"></a>
### Mizutamari

[Mizutamari](https://codeberg.org/Alexander88207/Mizutamari)はWinetricksと同様の補助ツールで、Linux向けの[Lutris](https://lutris.net/)から着想を得ています。主な対象はゲームですが、ゲーム以外のアプリケーションも扱います。原文のアンカーと画像名には旧称のHomuraが残っています。

<a id="installing-homura"></a>
#### Mizutamariのインストール

バイナリパッケージから導入する原文の例です。

```shell
# pkg install mizuma
```

Portsでは `emulators` ではなく `games` カテゴリにあります。

```shell
# cd /usr/ports/games/mizuma
# make install
```

<a id="using-homura"></a>
#### Mizutamariを使う

初回は端末、またはデスクトップ環境のコマンド実行欄から起動します。

```shell
% Mizuma
```

歓迎メッセージが表示されたら**OK**を押します。

![Mizutamariを使う：homura-launch-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-launch-1.png)

対応する環境では、アプリケーションメニューに起動項目を追加するか尋ねられます。

![Mizutamariを使う：homura-run-2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-run-2.png)

環境によっては、FreeBSD用のグラフィックスドライバを導入するよう通知が表示されます。

![Mizutamariを使う：homura-run-3.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-run-3.png)

続いてメインメニューが開きます。Winetricksと共通する操作に加え、**Open Mizutamari Folder**でデータフォルダを開いたり、**Run a executable in prefix**でprefix内のプログラムを指定して実行したりできます。

![Mizutamariを使う：homura-install-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-1.png)

対応アプリケーションを導入するには、**Installation**を選んで**OK**を押し、一覧から対象を選んでもう一度**OK**を押します。

![Mizutamariを使う：homura-install-2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-2.png)

最初にプログラムをダウンロードします。対応するデスクトップ環境では通知も表示されます。

![Mizutamariを使う：homura-install-3.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-3.png)

そのアプリケーション用のprefixが作られ、WINEのダイアログが表示されます。

![Mizutamariを使う：homura-install-4.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-4.png)

必要な前提ソフトウェアも導入されます。多数のファイルを取得・展開する場合があり、進行状況はダイアログで確認できます。

![Mizutamariを使う：homura-install-5.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-5.png)

取得したパッケージは必要に応じて開かれ、インストーラが実行されます。

![Mizutamariを使う：homura-install-6.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-6.png)

完了の通知方法は起動方法によって異なりますが、処理が終わるとメイン画面に戻ります。**Launcher**を選んで**OK**を押し、導入結果を確認します。

![Mizutamariを使う：homura-install-7.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-7.png)

インストール済みのアプリケーション一覧が表示されます。

![Mizutamariを使う：homura-install-8.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-install-8.png)

起動する項目を選んで**OK**を押します。削除するときはメイン画面の**Uninstallation**から同様の一覧を開き、削除対象を選んで**OK**を押します。

![Mizutamariを使う：homura-uninstall-1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/wine/homura-uninstall-1.png)

<a id="running-multiple-management-guis"></a>
### 管理ツールを併用するときの注意

WinetricksとMizutamariは対応するアプリケーションが異なるため、両方をインストールして使い分けられます。ただし、**同じprefixを両方のツールで管理しないようにします**。それぞれが互換性確保のためにDLLやレジストリなどを調整するため、もう一方の変更を上書きすると、一部またはすべてのアプリケーションが期待どおり動かなくなるおそれがあります。

<a id="wine-in-multi-user-os-installations"></a>
## 複数ユーザーが使うFreeBSDでのWINE

利用者ごとにprefixを分けるのが基本ですが、大きなアプリケーションを共有して保存容量や保守の手間を減らしたい場合もあります。本節では原文の二つの方法と、その制約を説明します。

<a id="issues-with-using-a-common-wine-prefix"></a>
### 共通prefixを使う際の問題

FreeBSDでは、複数の利用者が同時にログインして作業できます。一方、Windowsアプリケーションやその設定は、一つのデスクトップ環境を一人で使う状況を前提としていることがあります。これはWindows全般で複数ユーザーが利用できないという意味ではなく、共有するアプリケーションとprefixの設計上の問題です。

各利用者が独立した設定を持つことには利点があります。しかし、大容量のオフィスソフトやゲームを一度だけ導入できれば、同じファイルを重複して保存せずに済み、更新も一度で済みます。原文では、インストール先だけを共有する方法と、専用ユーザーのWINE環境を共有する方法を挙げています。

<a id="installing-applications-to-a-common-drivesettings"></a>
### 共通ドライブへアプリケーションを導入する

各利用者は自分のprefixを保持し、アプリケーションの実体だけを共通ディレクトリへ置く方法です。共有するプログラムが少なく、prefix固有の調整をあまり必要としない場合に向きます。個人設定を分離できるかどうかはアプリケーションにもよります。

1. `/mnt/windows-drive_d/` など、共有先のディレクトリを作ります。作成方法は `mkdir(1)` を参照してください。
2. 利用を認めるユーザーだけがアクセスできるようにします。たとえば `windows` グループを作って対象ユーザーを所属させ、ディレクトリのグループ所有者を合わせ、アクセス権を `770` にします。[ユーザーとグループ](03-basics.md#users-groups)および[アクセス権](03-basics.md#permissions)も参照してください。
3. 各利用者の `winecfg` で、そのディレクトリをドライブとして追加します。

以後、そこへ導入したアプリケーションをドライブ文字、またはUNIX形式のパスで指定できます。ただし、インストール先のファイルを書き換えるプログラムなどでは競合するため、原文は同時利用を避け、一人ずつ使うよう注意しています。ディレクトリ全体にグループの読み書き・実行権があっても、ファイル所有者と異なるユーザーで起動すると予期しない動作をするアプリケーションもあります。

<a id="using-a-common-installation-of-wine"></a>
### 専用ユーザーのWINE環境を共有する

共有するアプリケーションが多い場合や、同じ調整を一か所で保守したい場合は、専用ユーザーにprefixとプログラムを持たせる方法もあります。利用者は `sudo(8)` を使ってそのユーザーとして起動します。アプリケーションから見ると、専用ユーザーの設定を使うことになります。

以下は**原文の構成例**です。まず `root` でユーザーを作成します。

```shell
# adduser
```

原文ではユーザー名を `windows`、フルネームを `Microsoft Windows` とし、残りの質問には既定値で答える例を示しています。続いて `sudo` を導入します。

```shell
# pkg install sudo
```

原文のsudoers例は次のとおりです。`user1` と `user2` は実際の利用者名へ置き換える必要があります。

```shell
# User alias specification

# define which users can run the wine/windows programs
User_Alias WINDOWS_USERS = user1,user2

# define which users can administrate (become root)
User_Alias ADMIN = user1

# Cmnd alias specification

# define which commands the WINDOWS_USERS may run
Cmnd_Alias WINDOWS = /usr/bin/wine,/usr/bin/winecfg

# Defaults
Defaults:WINDOWS_USERS env_reset
Defaults:WINDOWS_USERS env_keep += DISPLAY
Defaults:WINDOWS_USERS env_keep += XAUTHORITY
Defaults    !lecture,tty_tickets,!fqdn

# User privilege specification
root    ALL=(ALL) ALL

# Members of the admin user_alias, defined above, may gain root privileges
ADMIN ALL=(ALL) ALL

# The WINDOWS_USERS may run WINDOWS programs as user windows without a password
WINDOWS_USERS ALL = (windows) NOPASSWD: WINDOWS
```

`WINDOWS_USERS` の利用者に、`WINDOWS` に列挙したコマンドを `windows` ユーザーとして実行する権限を与え、`DISPLAY` と `XAUTHORITY` を引き継ぐ構成です。`NOPASSWD` は、この許可に一致する実行でパスワード認証を要求しない指定です。

**訳注：** 原文はsudoersを `/etc/sudoers`、WINEを `/usr/bin/wine` としていますが、FreeBSDのPorts/pkgで導入するソフトウェアは通常 `/usr/local` 以下に配置されます。実際のsudoersの場所と `command -v wine`、`command -v winecfg` の結果を確認し、`visudo` を用いて設定します。また、`ADMIN ALL=(ALL) ALL` はWINE共有とは別に、`user1` へ任意のコマンドをrootとして実行できる権限を与えています。WINEを共有するだけならこの権限は不要です。既存のsudoersをこの例で丸ごと置き換えないでください。

次に、専用ユーザーからGUIへ接続するため、原文は次のX11用の例を挙げ、ログイン時やデスクトップ起動時の実行を提案しています。

```shell
% xhost +local:windows
```

**この指定は `windows` ユーザーだけへの許可として使わないでください。** [X.Orgのxhostマニュアル](https://xorg.freedesktop.org/archive/X11R7.5/doc/man/man1/xhost.1.html)では、`local` ファミリの名前は空文字列だけとされています。ユーザー名を後ろに書いても、ユーザー限定の認証にはなりません。利用中のXサーバの認証方式とユーザー単位の許可を確認する必要があります。Wayland環境でも、このX11向けの操作をそのまま一般化できません。

必要な権限と表示環境が整った利用者は、次のように専用ユーザーとして起動します。

```shell
% sudo -u windows wine program.exe
```

共通prefixへの同時アクセスには、なお競合の危険があります。専用ユーザーの下でもアプリケーションごとにprefixを分け、動作確認済みの環境を管理すれば、異なるprefixのゲームとオフィスソフトを別々の利用者が使う構成も考えられます。ただし、同じprefixを複数人で同時に使ってよいという意味ではありません。

<a id="wine-on-os-faq"></a>
## FreeBSDでWINEを使う際のFAQ

導入、表示、アプリケーションの互換性について、よくある疑問と調査の手掛かりをまとめます。

<a id="basic-installation-and-usage"></a>
### 基本的な導入と使い方

パッケージ構成に関する説明は、固定原文の時点のものです。利用する版で提供されているパッケージと、その説明を確認してください。

<a id="how-to-install-32-bit-and-64-bit-wine-on-the-same-system"></a>
#### 32ビット版と64ビット版を同じシステムで使えるか

原文では `wine` と `i386-wine` パッケージが競合する構成を説明しています。この場合、通常の方法では同時導入できず、chrootやjailで環境を分離するか、WINE本体のソースから独自に構築する方法が挙げられています。後者はPortsからビルドするという意味ではありません。これは旧来のパッケージ構成の説明であり、現在のすべての版に同じ制約があると決め付けず、使用するパッケージの32ビット対応方法を確認してください。

<a id="can-dos-programs-be-run-on-wine"></a>
#### DOSプログラムも動かせるか

原文は、前述のCUIプログラムとして実行を試す方法を紹介しています。ただし、DOSソフトウェアを動かす目的には `emulators/dosbox` のDOSBoxも適しています。試すなら普段使う環境と分けた新しいprefixを作り、動かない場合には試験用prefixを削除して片付けます。DOSプログラム全般の動作を保証するものではありません。

<a id="should-the-wine-devel-packageport-be-installed-to-use-the-development-version-of-wine-instead-of-stable"></a>
#### 開発版はwine-develで導入するのか

`emulators/wine-devel` はWINEの開発版を導入するためのPortsです。原文では安定版と競合するため、共存には環境分離などの追加措置が必要と説明しています。また、追加の変更を含むStaging版にも触れ、かつて存在したFreeBSDのPortが削除され、ソースから直接構築する方法があるとしています。これらの提供状況は固定原文の説明なので、使用するPortsツリーの現状を確認してください。

<a id="install-optimization"></a>
### 環境を調整する

表示やライブラリの調整は、ホスト側とWINE側のどちらを変更するのかを区別して行います。

<a id="how-should-windows-hardware-graphics-drivers-be-handled"></a>
#### Windows用のグラフィックスドライバを入れるべきか

WINEはホストOSのドライバを通じてハードウェアを利用します。グラフィックスカードに専用ドライバが必要なら、FreeBSDの通常の手順でFreeBSD用ドライバを導入します。Windows用ドライバのインストーラをWINEで実行してホストのドライバにする方法は想定されていません。

<a id="is-there-a-way-to-make-windows-fonts-look-better"></a>
#### フォントを読みやすくする方法はあるか

原文は、文字の輪郭が粗く見える場合の調整例として、[FreeBSD Forumsへの投稿](https://forums.freebsd.org/threads/make-wine-ui-fonts-look-good.68273/)を紹介しています。`.config/fontconfig/fonts.conf` でアンチエイリアスやヒンティングを指定するものです。

**訳注：以下は構文誤りを含む原文の例です。そのまま貼り付けないでください。** DOCTYPE宣言は `<!DOCTYPE fontconfig SYSTEM "fonts.dtd">` の形にする必要があり、各 `</edit>>` の末尾にある余分な `>` も除く必要があります。既存のfontconfig設定との整合性や、ディスプレイに合う描画方式も確認してください。

```text
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd>"

<fontconfig>

  <!-- antialias all fonts -->
  <match target="font">
    <edit name="antialias" mode="assign"><bool>true</bool></edit>>
    <edit name="hinting" mode="assign"><bool>true</bool></edit>>
    <edit name="hintstyle" mode="assign"><const>hintslight</const></edit>>
    <edit name="rgba" mode="assign"><const>rgb</const></edit>>
  </match>
</fontconfig>
```

<a id="does-having-windows-installed-elsewhere-on-a-system-help-wine-operate"></a>
#### 別パーティションのWindowsを利用すると改善するか

アプリケーションによっては改善する可能性があります。[Librariesタブ](#libraries)で説明したように、WINE内蔵のDLLに代えてWindows由来のライブラリを使える場合があります。WindowsのパーティションやドライブをFreeBSDでマウントし、対象ファイルへアクセスできることが前提です。対応するライブラリを適切に用意して読み込み順序を設定しますが、置き換えれば必ず改善するわけではありません。

<a id="application-specific"></a>
### アプリケーションごとの情報を調べる

同じWINEでもアプリケーションの版やホスト環境によって結果は異なります。動作報告の条件を自分の環境と照らし合わせてください。

<a id="where-is-the-best-place-to-see-if-application-x-works-on-wine"></a>
#### 動作するかどうかはどこで調べるか

最初の手掛かりは[WINE AppDB](https://appdb.winehq.org/)です。対応する各プラットフォームでの動作・不動作の報告が集められています。他のOSでの回避策がFreeBSDでも役立つ場合がありますが、OS・WINE・アプリケーションの版が違えば同じ結果になるとは限りません。

<a id="is-there-anything-that-will-help-games-run-better"></a>
#### ゲームの動作を改善する方法はあるか

多くのWindowsゲームはMicrosoftのDirectXを利用します。オープンソースの互換実装を使うことで改善する場合がありますが、ゲームやGPUによって結果は異なります。

原文はDXVKを紹介しています。DirectXの処理をVulkanへ対応付けるプロジェクトで、主対象はLinux上のWINEですが、[FreeBSDで構築・利用したという報告](https://forums.freebsd.org/threads/what-about-gaming-on-freebsd.723/page-9)も挙げています。

また原文では、Valveのゲーム向けWINE派生環境ProtonをFreeBSDへ持ち込む [wine-protonのPort](https://www.freshports.org/emulators/wine-proton/)を開発中と説明しています。これは原文時点の状況であり、現在の提供状態や各ゲームの対応を保証する説明ではありません。

<a id="is-there-anywhere-freebsd-wine-users-gather-to-exchange-tips-and-tricks"></a>
#### FreeBSDのWINE利用者はどこで情報交換しているか

原文は次の場を挙げています。チャンネルや招待先の状態は変わるため、利用時に確認してください。

- [FreeBSD Forums](https://forums.freebsd.org/)の **Installation and Maintenance of Ports or Packages**、**Emulation and virtualization** など。
- [FreeBSDのIRCチャンネル](https://wiki.freebsd.org/IRC/Channels)。一般的な支援の `#freebsd`、ゲーム関連の `#freebsd-games` など。
- [BSD World Discord](https://discord.gg/2CCuhCt)の `bsd-desktop`、`bsd-gaming`、`bsd-wine` など。

<a id="other-os-resources"></a>
### ほかのOS向けの資料も活用する

[WINE Wiki](https://wiki.winehq.org/)には、複数のOSに共通する豊富な情報があります。[Arch Linux WikiのWINEページ](https://wiki.archlinux.org/title/wine)も参考になりますが、Linux固有の手順や、FreeBSDでは利用できない補助アプリケーションを区別してください。

商用版の開発元CodeWeaversはWINE本体にも貢献しており、[同社のサポートフォーラム](https://www.codeweavers.com/support/forums)の回答が、オープンソース版の問題を調べる手掛かりになる場合もあります。
