<a id="desktop"></a>
# 第7章 デスクトップ環境とアプリケーション

> **状態:** 意訳ドラフト。固定原文の全節・表・コマンドを照合しています。デスクトップの実機起動や各アプリの動作は未検証です。
> **原文:** [Desktop Environments](https://docs.freebsd.org/en/books/handbook/desktop/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/07-desktop.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **章番号:** 本リポジトリの既存TOCでは第7章、固定した上流では第8章です。
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

以下はデスクトップの選択肢を説明するもので、すべてのログインマネージャーを同時に有効化する手順ではありません。`#` はroot、`%` は一般ユーザーです。`echo ... > ~/.xinitrc` は既存ファイルを上書きするため、既存の設定があれば保存・内容確認をしてから適用します。パッケージ名・機能・ライセンスの表記は固定原文の一覧であり、将来の版でも同一であることを保証するものではありません。

<a id="desktop-synopsis"></a>
## この章で行うこと

FreeBSDは性能・安定性からサーバーでよく使われますが、日常のデスクトップ用途にも利用できます。多くのPortsを組み合わせ、用途に合わせた環境を作れます。この章ではデスクトップ環境、ブラウザー、開発ツール、オフィス、文書閲覧、個人の会計管理ソフトを紹介します。

先に[X Window System](05-x11.md)または[Wayland](06-wayland.md)を準備してください。ここでは公式パッケージを使います。独自のビルド設定が必要なら[Portsの使い方](04-ports.md#ports-using)を参照します。

<a id="desktop-environments"></a>
## デスクトップ環境を選ぶ

デスクトップ環境には、単純なウィンドウマネージャーからアプリ一式を揃えたものまであります。原文で紹介する環境は次のとおりです。

| 環境 | 原文のライセンス表記 | Portsのパス |
|---|---|---|
| Plasma | GPL 2.0以降 | `x11/kde` |
| GNOME | GPL 2.0以降 | `x11/gnome` |
| Xfce | GPL、LGPL、BSD | `x11-wm/xfce4` |
| MATE | GPL 2.0、LGPL 2.0 | `x11/mate` |
| Cinnamon | GPL 2.0以降 | `x11/cinnamon` |
| LXQt | GPL、LGPL | `x11-wm/lxqt` |

<a id="kde-environment"></a>
### Plasma

KDEコミュニティの使いやすいデスクトップです。見た目の揃ったアプリ、メニュー・ツールバー・キー操作・配色・国際化を備え、設定を中央のGUIへまとめています。[Plasma公式](https://kde.org/plasma-desktop)と[FreeBSD向けKDE情報](https://freebsd.kde.org/)も参照してください。

<a id="kde-meta-install"></a>
#### Plasmaと基本アプリを導入する

基本的なKDEアプリを含むメタパッケージを導入します。

```shell
# pkg install kde
```

追加アプリは `kde-applications` カテゴリで探せます。

```shell
% pkg search -S origin kde-applications
```

<a id="kde-minimal-install"></a>
#### Plasmaを最小構成で導入する

最小のPlasmaデスクトップを導入する例です。

```shell
# pkg install plasma6-plasma
```

非常に小さな構成なので、端末Konsoleも別途導入します。

```shell
# pkg install konsole
```

<a id="kde-configuration"></a>
#### Plasmaの共通設定

メッセージバスなどに使うD-Busは依存先として導入されます。起動時にサービスを開始する設定をrc.confへ追加します。

```shell
# sysrc dbus_enable="YES"
```

<a id="kde-start"></a>
#### Plasmaを起動する

原文はSDDMによる自動起動を推奨しています。

```shell
# pkg install sddm
```

起動時に有効にします。

```shell
# sysrc sddm_enable="YES"
```

SDDMの言語設定の原文例はスペイン語です。利用する言語へ合わせます。

```shell
# sysrc sddm_lang="es_ES"
```

Xorgで手動のstartxを使う場合は、一般ユーザーの `~/.xinitrc` を次の内容にします。

```shell
% echo "exec dbus-launch --exit-with-x11 ck-launch-session startplasma-x11" > ~/.xinitrc
```

原文はWaylandセッションの手動起動を実験的な方法として示しています。

```shell
% exec dbus-launch ck-launch-session startplasma-wayland
```

<a id="gnome-environment"></a>
### GNOME

アプリ起動・状態表示のパネル、デスクトップ、各種ツールとアプリを備えた環境です。アプリ間の連携や一貫した操作を重視しています。

<a id="gnome-meta-install"></a>
#### GNOME一式を導入する

デスクトップとアプリケーションを含むメタパッケージを導入します。

```shell
# pkg install gnome
```

<a id="gnome-minimal-install"></a>
#### GNOMEを最小構成で導入する

基本機能へ絞ったGNOME-liteを導入します。

```shell
# pkg install gnome-lite
```

<a id="gnome-configuration"></a>
#### GNOMEを設定する

原文の構成では `/proc` を必要とします。起動時にマウントするため、`/etc/fstab` へ次を追加します。

```shell
# Device                Mountpoint      FStype  Options         Dump    Pass#
proc                    /proc           procfs  rw              0       0
```

依存先として入るD-Busを、rc.confで有効化します。

```shell
# sysrc dbus_enable="YES"
```

<a id="gnome-start"></a>
#### GNOMEを起動する

GNOMEに含まれるGDMを使う方法が推奨されています。起動時のサービスを有効にします。

```shell
# sysrc gdm_enable="YES"
```

手動でstartxを使う場合は、`~/.xinitrc` を次のようにします。

```shell
% echo "exec gnome-session" > ~/.xinitrc
```

<a id="xfce-environment"></a>
### Xfce

GTK系の軽いデスクトップです。メニュー・アプレット・ランチャーを持つパネル、ファイル管理、音の設定、テーマなどを備え、柔軟に構成できます。メモリの少ない古い機種や低速な機種にも向くと紹介されています。

<a id="xfce-install"></a>
#### Xfceを導入する

メタパッケージを導入します。

```shell
# pkg install xfce
```

<a id="xfce-configuration"></a>
#### Xfceを設定する

D-Busは依存先として入り、起動時に使うようrc.confで有効化します。

```shell
# sysrc dbus_enable="YES"
```

<a id="xfce-start"></a>
#### Xfceを起動する

軽量で少ないメモリで使えるLightDMが選択肢です。GTKのgreeterと導入します。

```shell
# pkg install lightdm lightdm-gtk-greeter
```

起動時に有効化します。

```shell
# sysrc lightdm_enable="YES"
```

手動のstartxを使うなら、`~/.xinitrc` からXfceの初期化ファイルを読み込みます。

```shell
% echo '. /usr/local/etc/xdg/xfce4/xinitrc' > ~/.xinitrc
```

<a id="mate-environment"></a>
### MATE

GNOME 2を引き継ぐデスクトップ環境で、従来型の分かりやすい操作を提供します。

<a id="mate-meta-install"></a>
#### MATE一式を導入する

テキストエディターやアーカイブ管理なども含むメタパッケージです。

```shell
# pkg install mate
```

<a id="mate-minimal-install"></a>
#### MATEを最小構成で導入する

基本機能だけに絞る場合のパッケージです。

```shell
# pkg install mate-base
```

<a id="mate-configuration"></a>
#### MATEを設定する

原文の構成は `/proc` を必要とするため、`/etc/fstab` へ追加して起動時にマウントします。

```shell
# Device                Mountpoint      FStype  Options         Dump    Pass#
proc                    /proc           procfs  rw              0       0
```

依存先として入るD-Busも起動時に有効化します。

```shell
# sysrc dbus_enable="YES"
```

<a id="mate-start"></a>
#### MATEを起動する

軽量のLightDMとGTK greeterを使う例です。

```shell
# pkg install lightdm lightdm-gtk-greeter
```

起動時に有効化します。

```shell
# sysrc lightdm_enable="YES"
```

手動のstartxを使う場合の `~/.xinitrc` です。

```shell
% echo "exec dbus-launch --exit-with-x11 ck-launch-session mate-session" > ~/.xinitrc
```

<a id="cinnamon-environment"></a>
### Cinnamon

GNOME Shellから分岐した技術を使い、GNOME 2に似た従来型の配置へ新しい機能を組み合わせた環境です。慣れた操作感と使いやすさを重視しています。

<a id="cinnamon-install"></a>
#### Cinnamonを導入する

パッケージを導入します。

```shell
# pkg install cinnamon
```

<a id="cinnamon-configuration"></a>
#### Cinnamonを設定する

原文の構成は `/proc` を使うため、`/etc/fstab` に追加します。

```shell
# Device                Mountpoint      FStype  Options         Dump    Pass#
proc                    /proc           procfs  rw              0       0
```

依存先として導入されるD-Busを起動時に有効化します。

```shell
# sysrc dbus_enable="YES"
```

<a id="cinnamon-start"></a>
#### Cinnamonを起動する

LightDMとGTK greeterを導入する例です。

```shell
# pkg install lightdm lightdm-gtk-greeter
```

起動時に有効化します。

```shell
# sysrc lightdm_enable="YES"
```

手動のstartxでは、`~/.xinitrc` を次のようにします。

```shell
% echo "exec dbus-launch --exit-with-x11 ck-launch-session cinnamon-session" > ~/.xinitrc
```

<a id="lxqt-environment"></a>
### LXQt

Qtを使う、シンプルで速く直感的なデスクトップです。性能の低い機種でも動かしやすい環境として紹介されています。

<a id="lxqt-install"></a>
#### LXQtを導入する

メタパッケージを導入します。

```shell
# pkg install lxqt
```

<a id="lxqt-configuration"></a>
#### LXQtを設定する

原文の構成では `/proc` を使い、fstabへ次を追加します。

```shell
# Device                Mountpoint      FStype  Options         Dump    Pass#
proc                    /proc           procfs  rw              0       0
```

依存先のD-Busを起動時に有効化します。

```shell
# sysrc dbus_enable="YES"
```

<a id="lxqt-start"></a>
#### LXQtを起動する

原文はSDDMを推奨しています。

```shell
# pkg install sddm
```

起動時に有効化します。

```shell
# sysrc sddm_enable="YES"
```

言語の原文例はスペイン語です。実際に利用する言語へ合わせます。

```shell
# sysrc sddm_lang="es_ES"
```

手動のstartxを使う場合の `~/.xinitrc` は次のとおりです。

```shell
% echo "exec dbus-launch --exit-with-x11 ck-launch-session startlxqt" > ~/.xinitrc
```

<a id="desktop-browsers"></a>
## Webブラウザー

機能の多いブラウザーから、資源消費の少ないコマンドライン向けまであります。必要資源は原文の相対的な目安です。

| 名前 | 原文のライセンス | Portsのパス | 資源の目安 |
|---|---|---|---|
| Firefox | MPL 2.0 | `www/firefox` | 多 |
| Chromium | BSD-3ほか | `www/chromium` | 多 |
| Iridium | BSD-3ほか | `www/iridium-browser` | 多 |
| Falkon | MPL 2.0 | `www/falkon-qtonly` | 多 |
| Konqueror | GPL 2.0以降 | `x11-fm/konqueror` | 中 |
| GNOME Web | GPL 3.0以降 | `www/epiphany` | 中 |
| qutebrowser | GPL 3.0以降 | `www/qutebrowser` | 中 |
| Dillo | GPL 3.0以降 | `www/dillo2` | 少 |
| Links | GPL 2.0以降 | `www/links` | 少 |
| w3m | MIT | `www/w3m` | 少 |

<a id="firefox"></a>
### Firefox

Mozilla系のコードを基にしたオープンソースのブラウザーです。標準に沿ったHTML表示、タブ、ポップアップ抑制、拡張機能、セキュリティ機能などを備えます。

通常リリースを導入します。

```shell
# pkg install firefox
```

長期サポート版ESRを使う場合は次です。

```shell
# pkg install firefox-esr
```

<a id="chromium"></a>
### Chromium

安全性・速度・安定性を重視するオープンソースのブラウザープロジェクトで、Google Chromeの基盤でもあります。タブ、ポップアップ抑制、拡張機能などを備えます。

```shell
# pkg install chromium
```

実行ファイルは `/usr/local/bin/chrome` で、`/usr/local/bin/chromium` ではありません。原文は、使える検索エンジンに地域設定が影響すると説明しています。適切なロケールは[ローカライズ](https://docs.freebsd.org/en/books/handbook/l10n/#using-localization)を参照します。

<a id="iridium"></a>
### Iridium

Chromiumを基にプライバシーを重視したブラウザーです。入力途中の検索語・キーワード・利用統計などを中央のサービスへ自動送信する動作を抑え、同意がある場合に限る設計と説明されています。

導入します。

```shell
# pkg install iridium-browser
```

<a id="falkon"></a>
### Falkon

QtWebEngineを使い、各主要プラットフォームで軽く使えることを目指したブラウザーです。ブックマーク・履歴・タブを備えます。原文はAdBlock、Flashを止めるClick2Flash、ローカルCA証明書を扱うSSL Managerも紹介していますが、Flash関連などの記述は旧来の機能説明として読んでください。

導入します。

```shell
# pkg install falkon
```

<a id="konqueror"></a>
### Konqueror

Webブラウザーに加え、ファイル管理やマルチメディア閲覧も行うKDE系のアプリです。原文はWebKitと独自のKHTMLを挙げています。原文中のChromiumのエンジンに関する説明は古いため、現在の各ブラウザーの実装を示す記述としては扱いません。

導入します。

```shell
# pkg install konqueror
```

<a id="gnome-web-epiphany"></a>
### GNOME Web（Epiphany）

多機能なブラウザーの一部機能を省き、軽さ・速さ・簡潔さを目指すGNOMEのWebブラウザーです。

導入します。

```shell
# pkg install epiphany
```

<a id="qutebrowser"></a>
### qutebrowser

最小限のGUIとキーボード操作を重視したブラウザーです。GPLの自由ソフトウェアで、原文はPythonとPyQt5を基盤として紹介しています。

導入します。

```shell
# pkg install qutebrowser
```

<a id="dillo"></a>
### Dillo

小さく速く、安定性・使いやすさ・拡張性・開発しやすさを目指すクロスプラットフォームのブラウザーです。原文は、GTK1からFLTKへ大きく書き直された実験的な新版として説明しています。

導入します。

```shell
# pkg install dillo
```

<a id="links"></a>
### Links

Lynxに似たブラウザーで、テキストとグラフィックスのモードを持ち、表やメニューなども表示できます。

導入します。

```shell
# pkg install links
```

<a id="w3m"></a>
### w3m

ページャーとしても使えるテキストブラウザーです。Lynxに似ていますが、表やフレームの表示などの機能もあります。

導入します。

```shell
# pkg install w3m
```

<a id="desktop-development"></a>
## 開発ツール

FreeBSDで使える主な開発ツールを紹介します。資源の目安とライセンス名は原文の表記です。

| 名前 | ライセンス | Portsのパス | 資源の目安 |
|---|---|---|---|
| Visual Studio Code | MIT | `editors/vscode` | 多 |
| Qt Creator | QtGPL | `devel/qtcreator` | 多 |
| KDevelop | GPL 2.0以降、LGPL 2.0以降 | `devel/kdevelop` | 多 |
| Eclipse IDE | EPL | `java/eclipse` | 多 |
| Vim | VIM | `editors/vim` | 少 |
| Neovim | Apache 2.0 | `editors/neovim` | 少 |
| GNU Emacs | GPL 3.0以降 | `editors/emacs` | 少 |

<a id="vs-code"></a>
### Visual Studio Code

コードエディターの手軽さに、編集・ビルド・デバッグの作業をまとめたツールです。編集・デバッグの支援、拡張機能、既存ツールとの軽い連携を備えます。

導入します。

```shell
# pkg install vscode
```

<a id="qt-creator"></a>
### Qt Creator

Qt開発者向けのクロスプラットフォームIDEです。C++・QML・ECMAScriptの編集、素早いコード移動、入力中の静的検査とスタイルの助言、文脈に応じたヘルプ、視覚的デバッガー、GUIレイアウト・フォームのデザイナーを備えます。

導入します。

```shell
# pkg install qtcreator
```

<a id="kdevelop"></a>
### KDevelop

C/C++など複数言語向けの、オープンソースでプラグイン拡張可能なIDEです。KDevPlatform・KDE・Qtのライブラリを基にし、1998年から開発されています。

導入します。

```shell
# pkg install kdevelop
```

<a id="eclipse"></a>
### Eclipse IDE

拡張可能な統合開発基盤です。特定の用途だけに固定せず、開発ツールを作り、組み合わせて実行するための部品と基盤を提供します。別々の開発者が作ったツールも統合できる設計です。

導入します。

```shell
# pkg install eclipse
```

<a id="vim"></a>
### Vim

viを発展させた、細かく設定できるテキストエディターです。効率的な編集やプログラミングに使われますが、メールや設定ファイルなど一般の文章編集にも利用できます。人によってはIDE全体に相当するほどの機能を使いこなします。

導入します。

```shell
# pkg install vim
```

<a id="neovim"></a>
### Neovim

Vimのコードを大きく再構成したエディターです。扱いやすい既定値、組み込み端末、非同期プラグイン、速度と拡張性を重視したAPIなどを備え、ほとんどのVimプラグインやスクリプトとの互換性を保つよう設計されています。

導入します。

```shell
# pkg install neovim
```

<a id="gnu-emacs"></a>
### GNU Emacs

拡張・カスタマイズが可能な自由なテキストエディターです。中心には、テキスト編集向けの拡張を持つLisp方言であるEmacs Lispのインタープリターがあります。

導入します。

```shell
# pkg install emacs
```

<a id="desktop-productivity"></a>
## オフィス・文書作成

オフィス一式や使いやすいワープロが必要なら、デスクトップ環境とは独立して選べます。Plasma系にもオフィスがありますが、FreeBSD全体で決まった標準の業務ソフトがあるわけではありません。必要資源は原文の目安です。大きなものはPortsからのビルドにも時間がかかります。

| 名前 | 原文のライセンス | Portsのパス | 資源の目安 |
|---|---|---|---|
| LibreOffice | MPL 2.0 | `editors/libreoffice` | 多 |
| Calligra Suite | LGPL、GPL | `editors/calligra` | 中 |
| AbiWord | GPL 2.0以降 | `editors/abiword` | 中 |

<a id="libreoffice"></a>
### LibreOffice

[The Document Foundation](https://www.documentfoundation.org/)が開発する自由なオフィススイートです。主要な他製品の形式に対応し、複数プラットフォームで利用できます。OpenOffice系から分岐し、ワープロ、表計算、プレゼンテーション、図形描画、データベース、数式の作成・編集を備えます。UIだけでなくスペルチェックや辞書も多言語対応です。詳しくは[公式サイト](https://www.libreoffice.org/)を参照してください。

```shell
# pkg install libreoffice
```

基本パッケージは既定で英語のみと説明されています。利用する言語のパックを追加します。原文の例はスペイン語です。

```shell
# pkg install es-libreoffice
```

別の言語を使う場合は対応する言語パックを選びます。

<a id="calligra"></a>
### Calligra

KDE系のオフィススイートで、Plasma全体とは別に導入できます。原文では、Wordsがワープロ、Sheetsが表計算、Stageがプレゼンテーション、Karbonが図形文書の作成を担当すると紹介されています。

```shell
# pkg install calligra
```

<a id="abiword"></a>
### AbiWord

Microsoft Wordに似た操作感の自由なワープロです。高速で使いやすく、多くの機能を備えます。RTFなど、一部の独自形式を含む複数の文書形式を読み書きできます。

```shell
# pkg install abiword
```

<a id="desktop-viewers"></a>
## 文書ビューアー

ベースシステムだけでは閲覧できない新しい文書形式には、追加のビューアーを導入します。

| 名前 | 原文のライセンス | Portsのパス | 資源の目安 |
|---|---|---|---|
| Okular | GPL 2.0 | `graphics/okular` | 多 |
| Evince | GPL 2.0 | `graphics/evince` | 中 |
| ePDFView | GPL 2.0 | `graphics/epdfview` | 中 |
| Xpdf | GPL 2.0 | `graphics/xpdf` | 少 |
| Zathura | Zlib | `graphics/zathura` | 少 |

<a id="okular"></a>
### Okular

KDEプロジェクトの汎用文書ビューアーです。PDF、PostScript、DjVu、CHM、XPS、ePubなど多くの形式に対応し、機能の豊富さを重視しています。

導入します。

```shell
# pkg install okular
```

<a id="evince"></a>
### Evince

GNOMEの文書ビューアーで、PDF・PostScriptなど複数形式を扱います。ggvやgpdfなど用途別のビューアーを、簡単な1つのアプリへまとめることを目指しています。

導入します。

```shell
# pkg install evince
```

<a id="epdfview"></a>
### ePDFView

GTKとPopplerを使う軽いPDFビューアーです。GNOMEのライブラリには依存せず、Evinceのように簡単な閲覧を提供することを目指しています。

導入します。

```shell
# pkg install epdfview
```

<a id="xpdf"></a>
### Xpdf

少ない資源で使える軽いPDFビューアーです。原文は、標準Xフォントを使い追加のツールキットを要求しないものとして紹介しています。

導入します。

```shell
# pkg install xpdf
```

<a id="zathura"></a>
### Zathura

最小限の省スペースなUIとキーボード操作を重視し、細かくカスタマイズできるビューアーです。PDF対応と導入する例です。

```shell
# pkg install zathura zathura-pdf-mupdf
```

別のPDFエンジンには `graphics/zathura-pdf-poppler`、PostScriptには `graphics/zathura-ps`、DjVuには `graphics/zathura-djvu`、コミック形式には `graphics/zathura-cb` を追加できます。

<a id="desktop-finance"></a>
## 個人の会計・家計管理

FreeBSDのデスクトップには、個人の収支などを管理するソフトウェアもあります。QuickenやExcelなどの広く使われる形式と連携できるものもあります。以下は原文が紹介するアプリと資源の目安です。

| 名前 | 原文のライセンス | Portsのパス | 資源の目安 |
|---|---|---|---|
| KMyMoney | GPL 2.0 | `finance/kmymoney` | 多 |
| GnuCash | GPL 2.0、GPL 3.0 | `finance/gnucash` | 多 |

<a id="kmymoney"></a>
### KMyMoney

KDEコミュニティの個人向け会計管理アプリです。市販の個人向け金融管理ソフトで重要な機能を備えることを目指し、使いやすさと複式簿記を特徴とします。QuickenのQIF取り込み、投資の記録、複数通貨、各種レポートに対応します。

```shell
# pkg install kmymoney
```

<a id="gnucash"></a>
### GnuCash

収入・支出、銀行口座、株式などを記録するアプリです。使いやすさと本格的な機能の両立を目指します。入力しやすい取引記録、階層的な勘定科目、キーボードショートカット、自動補完、1つの取引を複数項目へ分ける機能を備えます。

QuickenのQIFを取り込み・統合でき、国際的な日付・通貨の多くの形式も扱います。

```shell
# pkg install gnucash
```
