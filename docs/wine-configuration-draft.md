# 第12章 WINE：設定・管理節の作業稿

全章への統合前の作業稿です。第12章の翻訳完了を示すものではありません。

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

