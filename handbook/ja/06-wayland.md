<a id="wayland"></a>
# 第6章 FreeBSDでWaylandを使う

> **状態:** 意訳ドラフト。固定原文の全節・設定・出力例を照合しています。各コンポジターの実機検証は未実施です。
> **原文:** [Wayland on FreeBSD](https://docs.freebsd.org/en/books/handbook/wayland/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/06-wayland.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

原文には2021年時点のPlasmaや、当時のログインマネージャーに関する記述が残っています。これらを現在の対応状況として扱わず、日付や制約を示して訳します。コードは原文を保持し、抜粋・書式上の不足は訳注で説明します。`#` はroot、`%` は一般ユーザーのプロンプトです。

<a id="wayland-synopsis"></a>
## この章で行うこと

bsdinstallだけではGUIは入りません。この章ではWaylandのコンポジターを選び、導入・設定してグラフィックス環境を作ります。

先に[追加ソフトウェアの導入](04-ports.md)と、[GPUの特定・ドライバー設定](05-x11.md#x-graphic-card-drivers)を確認してください。ここではFreeBSD側の準備、コンポジターの導入、旧来のXアプリの実行、遠隔デスクトップを扱います。

<a id="wayland-overview"></a>
## Waylandの仕組みと共通の準備

Waylandは、クライアントとコンポジターを結ぶ通信プロトコルです。XorgのようにX11プロトコルとXサーバーを一体で提供するものではありません。表示サーバーの役割はコンポジターや対応するウィンドウマネージャーが担い、従来のXサーバーへの依存を外します。

遠隔接続もXの画面接続と同じ方式ではなく、VNCやRDPなどを使います。Waylandの合成・表示処理自体はXプロトコルに対応する必要がありません。

ネイティブWaylandへ未対応のアプリはXwaylandを使います。原文は、Wayland非対応のX11ウィンドウマネージャーを使う場合に、Xwaylandを `-rootless` なしで起動する方法も説明しています。通常のWayland上でXアプリを動かす用途とは区別します。

原文時点では、多くのソフトウェア、たとえばFirefoxが利用でき、Compiz Fusionに似たWayfireや、i3に代わるSwayが紹介されています。NVIDIAのドライバーは多くのwlroots系で使える一方、不安定さや未対応機能がある場合があり、開発協力も求められているとしています。

> **過去の記述:** 原文には「2021年5月時点でplasma5-kwinが対応し、`dbus-launch --exit-with-x11 ck-launch-session startplasma-wayland` で起動できる」とあります。現在のPlasmaの版やセッション起動方法を示す手順ではなく、当時の案内です。

キーバインドには `evdev(4)` のあるカーネルが必要です。GENERICには既定で入っていますが、独自カーネルで外した場合はモジュールを読み込みます。また、利用者を `video` グループへ追加します。次はrootで実行し、`user` を実際の名前へ置き換えます。

```text
pw groupmod video -m user
```

Wayland自体の設定は少なく、多くはコンポジター側で行います。非rootユーザーへGPUなどのデバイスアクセスを仲介するseatdも先に導入します。

```shell
# pkg install wayland seatd
```

原文の各例は `graphics/drm-kmod` のオープンソースドライバーでの利用を想定し、NVIDIAのプロプライエタリードライバーでは問題がある場合があるとしています。

各コンポジターには実行時ディレクトリが必要です。FreeBSD 14.1以降は自動作成・設定されると説明されています。それ以前の版でBourneシェルから指定する原文例です。

```shell
% export XDG_RUNTIME_DIR=/var/run/user/`id -u`
```

> **訳注:** 環境変数を設定するだけで、ディレクトリの作成や権限設定まで行うわけではありません。[XDG Base Directory仕様](https://specifications.freedesktop.org/basedir/latest/)は、実行時ディレクトリをその利用者が所有し、権限を0700にし、ログインの存続期間に結び付けることを求めています。

原文は設定ファイルの探索先にもXDG_RUNTIME_DIRを挙げていますが、以下の例では一時ファイルと設定を分け、`~/.config` のファイルを起動オプションで明示します。必要ならそのコマンドをエイリアスにできます。

> **訳注:** XDG仕様上のユーザー設定の基準は `XDG_CONFIG_HOME`（既定は `~/.config`）で、`XDG_RUNTIME_DIR` はソケットなどの実行時オブジェクトの場所です。両者を混同しないでください。

> **原文の回避策:** ZFS上の実行時ディレクトリで `posix_fallocate()` が必要なクライアントに問題が出たという報告があり、著者の環境では再現できなかったとしています。回避策として `/var/run` をtmpfsにし、`mount -t tmpfs tmpfs /var/run` とfstabで設定する方法を挙げています。これは問題が起きた構成向けの説明で、稼働中のシステムへ一律に実行する通常の準備手順ではありません。既存の実行時ファイルやサービスへの影響を考慮して構成します。

seatdは、ここで扱うWaylandコンポジターを起動する前に有効化・起動します。従来のX11セッションのためだけには不要です。

```shell
# sysrc seatd_enable="YES"
# service seatd start
```

次にコンポジターを導入します。以下は3種類の基本設定、画面ロック、追加資料の案内です。

<a id="wayland-wayfire"></a>
## Wayfireを使う

Wayfireは軽さとカスタマイズを重視し、Compiz Fusionを思わせる表示効果も持つコンポジターです。原文の構成では次を導入します。

```shell
# pkg install wayfire wf-shell alacritty swaylock-effects swayidle wlogout kanshi mako wlsunset
```

Alacrittyは端末エミュレーターです。必須ではなく、原文ではkittyやXfceのTerminalも動作例に挙げています。設定サンプルをコピーして編集します。

```shell
% mkdir ~/.config/wayfire
% cp /usr/local/share/examples/wayfire/wayfire.ini ~/.config/wayfire
```

多くの既定値はそのまま使えます。cubeなどの効果も設定され、コメントに案内があります。出力設定の例です。

```text
[output]
mode = 1920x1080@60000
position = 0,0
transform = normal
scale = 1.000000
```

`mode` は幅×高さとリフレッシュレート、`position` は画面位置、`transform` は変換、`scale` は拡大率を表します。数値・単位の扱いは利用する版の文書で確認してください。

原文は当時SDDMからのWaylandコンポジター起動に問題があるとし、画面のアイドル・ロックにはswayidleとswaylockを使う構成を紹介しています。ログインマネージャーと画面ロックは別の役割です。

アイドル時の動作を指定します。

```text
idle = swaylock
```

タイムアウトなどの例です。

```text
[idle]
toggle = <super> KEY_Z
screensaver_timeout = 300
dpms_timeout = 600
```

原文の説明では300秒でロックし、さらに300秒後にDPMSで画面を消します。

`<super>` は通常Windowsロゴキーです。ないキーボードなら設定内で別のキーへ割り当てます。既定のマッピングなら `Super+Shift+Escape` でswaylockが起動します。通常は灰色の画面ですが、swaylock-effectsならぼかしなどを使えます。

```shell
% swaylock --effect-blur 7x5
```

`--clock` は日時を表示します。パッケージには既定のPAM設定が入り、追加の調整はPAMの文書を参照します。

Wayfireを試します。

```shell
% wayfire -c ~/.config/wayfire/wayfire.ini
```

起動すると背景と上部メニューが出ます。対応する導入済みアプリ、たとえばXfceのファイルマネージャーがメニューへ載ることがあります。アプリのキーバインドはwayfire.iniで定義できます。

Wayfire Config Managerはメニュー、または端末から開けます。

```shell
% wcm
```

表示効果などをGUIで調整できます。背景・パネル・ドックを使う原文の設定例です。

```text
panel = wf-panel
dock = wf-dock
background = wf-background
```

> **警告:** wcmによる変更は、wayfire.iniの手動変更を上書きします。重要な設定を戻せるよう、先にファイルをバックアップしてください。

原文の既定ランチャーは `x11/wf-shell` で、好みに応じて別のパネルへ置き換えることもできます。

<a id="wayland-hikari"></a>
## Hikariを使う

Hikariは、view・sheet・group・workspaceという概念でウィンドウを整理し、生産性を重視するコンポジターです。viewが個々のウィンドウで、sheetやgroupがそれらをまとめ、操作対象をworkspaceとして扱います。この説明では1つのworkspaceとsheetを使うものとして進めます。細かな機能はmanページを確認してください。

Hikariと端末Alacrittyを導入します。

```shell
# pkg install hikari alacritty
```

kittyやPlasmaの端末など、ほかの好みの端末でも互換性を試せます。設定ファイルは `hikari.conf` です。原文はXDG_RUNTIME_DIRへの配置にも言及していますが、ここでは設定を `~/.config` に置き、`-c` で明示します。自動起動ファイルは必須ではないものの、移行時に便利です。

```shell
% mkdir ~/.config/hikari
% cp /usr/local/etc/hikari/hikari.conf ~/.config/hikari
```

設定はui・outputs・layoutsなどに分かれます。既定で使える項目も多い一方、通常は環境にない `$TERMINAL` などの設定を見直します。環境変数を用意するか、設定で端末を直接指定します。

```text
terminal = "/usr/local/bin/alacritty"
```

キー名の大文字は修飾キーを表します。端末起動の `L+Return` の `L` は、文字LではなくSuper／Windowsロゴキーです。つまり `Super+Enter` で指定端末を開きます。

別のアプリを割り当てるには、actionsへ動作を定義します。

```text
actions {
  terminal = "/usr/local/bin/alacritty"
  browser = "/usr/local/bin/firefox"
}
```

その後、bindingsのkeyboardへ割り当てます。

```text
bindings {
  keyboard {
SNIP
    "L+Return" = action-terminal
    "L+b" = action-browser
SNIP
```

> **訳注:** `SNIP` を含む抜粋で、ファイル全体ではありません。既存設定の対応箇所へ組み込み、必要な閉じ括弧は元の構造に従って保持します。

再起動後に `Super+b` でブラウザーが開きます。Hikariにはメニューバーがないため、移行前に少なくとも端末を開けるキーを設定します。manページを読んでから移行してください。PlasmaやGNOMEの中から起動して試す方法もあります。

画面ロック用のPAM設定と解除ツールはパッケージに入ります。既定のキーは `Super+Shift+Backspace` です。publicでないviewは隠れ、ロック中は入力を受け付けませんが、公開されたviewに機密情報が見えていないか注意します。必要ならswaylock-effectsなど別のロックツールも検討できます。

設定を指定して起動します。

```shell
% hikari -c ~/.config/hikari/hikari.conf
```

<a id="wayland-sway"></a>
## Swayを使う

Swayはi3に代わるタイル型コンポジターで、既存i3設定を使えるように設計されています。ただし新機能には追加設定が必要な場合があります。GPUとドライバーを[前章](05-x11.md#x-graphic-card-drivers)に沿って準備することが、正常動作の前提です。

ここでは既存i3設定を移さず、新しく構成します。rootで次を導入します。

```shell
# pkg install sway swayidle swaylock-effects alacritty dmenu-wayland dmenu
```

基本設定をコピーして編集します。

```shell
% mkdir ~/.config/sway
% cp /usr/local/etc/sway/config ~/.config/sway
```

主な設定の原文例です。

```shell
# Logo key. Use Mod1 for Alt.
input * xkb_rules evdev
set $mod Mod4
# The preferred terminal emulator
set $term alacritty
set $lock swaylock -f -c 000000
output "My Workstation" mode 1366x768@60Hz position 1366 0
output * bg ~/wallpapers/mywallpaper.png stretch
### Idle configuration
exec swayidle -w \
          timeout 300 'swaylock -f -c 000000' \
          timeout 600 'swaymsg "output * dpms off"' resume 'swaymsg "output * dpms on"' \
          before-sleep 'swaylock -f -c 000000'
```

evdevのキーボード規則を読み込み、`$mod` はWindowsロゴキー、端末はAlacrittyにしています。出力名・モード・位置・壁紙は実際の環境へ置き換えます。`stretch` は画像を画面に合わせて拡大します。

swayidleは300秒後に黒（`000000`）のロック画面、600秒後に画面の省電力化、復帰時に表示を戻す動作、スリープ前のロックを定義します。swaylock-effectsでは `--clock` で時計を表示することもできます。出力設定の詳細は `sway-output(5)` を確認してください。

アプリメニューは `Super+d` で開き、矢印キーで選びます。バーの配置やトレイは `sway-bar(5)` と設定のBar節を参照します。既定では右上に日時が出ます。

上のタイマー例だけでなく、手動ロックのキーも用意します。Key bindingsへ次を追加します。

```shell
# Lock the screen manually
bindsym $mod+Shift+Return exec $lock
```

これで `Super+Shift+Enter` がロックになります。パッケージ・Portsのどちらで導入しても既定のPAM設定が入り、詳しい調整はPAMの文書を参照します。

終了は `Super+Shift+e` で確認画面を出し、終了を選びます。完全移行前にPlasmaなどのX11デスクトップの端末から試すと、キーや設定を確認しやすくなります。

```shell
% sway -c ~/.config/sway/config
```

<a id="wayland-xwayland"></a>
## XwaylandでXアプリを動かす

Wayland環境の導入時にX11対応を外していなければ、Xwaylandが既に入っている場合があります。`/usr/local/bin/Xwayland` がなければ導入します。

```shell
# pkg install xwayland
```

原文は開発版を勧め、Waylandパッケージに入っている可能性にも言及していますが、実際の構成と必要な版を確認してください。有効化の方法はコンポジターごとに違います。

Wayfireではwayfire.iniへ次を記述します。

```text
xwayland = true
```

Swayは既定で有効と説明されていますが、原文は明示設定も案内しています。

```text
xwayland enable
```

Hikariは既定で組み込まれ、変更不要です。無効にするにはPortsから再ビルドしてXwayland対応を外す方法を示しています。

コンポジターを起動して端末を開き、環境変数を確認します。

```shell
% env | grep DISPLAY
```

正常な例では、Wayland用とX11用の表示先が分かれています。

```text
WAYLAND_DISPLAY=wayland-1
DISPLAY=:0
```

小さなXアプリであるxeyesを導入して試す方法もあります。目がポインターを追えばXwaylandで動作しています。原文はこのアプリのPorts表記を崩れた形で記載していますが、ここでは実行名をxeyesとして説明します。

次のようなエラーは、初期化や表示先の設定に問題があることを示し、原文は再導入が必要な場合にも言及しています。

```text
Error: Cannot open display wayland-0
```

> **原文の注意と訳注:** Xサーバーを追加すると、そのクライアント接続の仕組みも増えます。ただし、以下で確認しているのはUNIXドメインソケットです。Xwaylandを有効にしただけで必ず外部ネットワーク向けTCPポートが開く、という意味には読み替えないでください。

Wayfireなどで、XwaylandがあるのにXアプリを起動できない場合、次のようにDISPLAYが誤ってWaylandのソケット名になっていることがあります。

```shell
% env | grep DISPLAY
```

```text
DISPLAY=wayland-1
WAYLAND_DISPLAY=wayland-1
```

まずXwaylandが既にUNIXソケットを使って動いているか確認します。

```shell
% sockstat | grep x11
```

出力例です。

```text
trhodes  Xwayland   2734  8  stream /tmp/.X11-unix/X0
trhodes  Xwayland   2734  9  stream /tmp/.X11-unix/X0
trhodes  Xwayland   2734  10 stream /tmp/.X11-unix/X0
trhodes  Xwayland   2734  27 stream /tmp/.X11-unix/X0_
trhodes  Xwayland   2734  28 stream /tmp/.X11-unix/X0
```

さらにコンポジター内の端末からXwaylandを直接起動すると、既存サーバーの有無を調べられます。

```shell
% Xwayland
```

既にdisplay 0が動いている場合の出力例です。

```text
(EE)
Fatal server error:
(EE) Server is already active for display 0
	If this server is no longer running, remove /tmp/.X0-lock
	and start again.
(EE)
```

これはdisplay 0のサーバーが存在することを示すため、ロックファイルをむやみに消すのではなく、表示先の誤設定を直します。そのサーバーを使う場合の例です。

```text
export DISPLAY=:0
```

原文では `mail/claws-mail` を再実行する例を挙げています。`:0` は実際に確認できた表示番号に合わせてください。

<a id="wayland-remotedesktop"></a>
## VNCで遠隔デスクトップを使う

WaylandはXorgと同じ画面接続を提供しないため、RDPやVNCなどを選びます。ここではwlroots系コンポジターに対応するwayvncを導入します。

```shell
# pkg install wayvnc
```

原文時点では設定ファイルが付属しないため、manページを参照して作ります。基本例です。

```text
address=0.0.0.0
enable_auth=true
username=username
password=password
private_key_file=/path/to/key.pem
certificate_file=/path/to/cert.pem
```

ユーザー名・パスワード・鍵と証明書のパスを実際の値へ置き換えます。鍵と証明書は別途用意し、接続保護のため利用することを原文は強く勧めています。`address=0.0.0.0` はすべてのIPv4インターフェースで待ち受ける例なので、公開したい範囲に合わせて設定します。

既定の設定先は `~/.config/wayvnc/config`、`-C` で別ファイルを指定できます。

```shell
% wayvnc -C ~/.config/wayvnc/config
```

原文の執筆時点では、システム起動時のrc.dスクリプトは付属せず、必要ならローカルで開始処理を用意すると説明されています。

<a id="wayland-ly"></a>
## Waylandセッションのログインマネージャー

ログインマネージャーの選択肢として、テキストUIの `x11/ly` が紹介されています。比較的少ない設定でSway・Wayfireなどのログイン画面を起動時に出せます。

```shell
# pkg install ly
```

導入時に表示される案内も確認します。原文は `/etc/gettytab` へ次を追加する方式を示しています。

```text
Ly:\
  :lo=/usr/local/bin/ly:\
  :al=root:
```

次に `/etc/ttys` のttyv1行を変更します。

```text
ttyv1 "/usr/libexec/getty Ly" xterm onifexists secure
```

再起動するとログイン画面が出ます。言語などは `/usr/local/etc/ly/config.ini` で設定し、少なくともttysと同じttyを指定します。ttyv0を使った場合は、表示のため `Alt+F1` が必要になることがあります。

ログイン画面では左右キーで対応するセッションを切り替えます。以上は原文のgetty連携の手順なので、実際の導入版が示す案内とも照合します。

<a id="wayland-utilities"></a>
## 便利な補助ツール

WaybarはWayland対応のタスクバーで、コンポジターのランチャーに加えて使えます。音量調整用のpavucontrolと導入する例です。

```shell
# pkg install pavucontrol waybar
```

設定ディレクトリを作り、基本設定をコピーして調整します。

```shell
% mkdir ~/.config/waybar
% cp /usr/local/etc/xdg/waybar/config ~/.config/waybar
```

lavalauncherはアプリの起動バーです。原文は設定サンプルが付属しないとし、まずディレクトリを作る手順を示しています。

```text
mkdir ~/.config/lavalauncher
```

原文の設定例は、画面下の右側へアプリのボタンを置くものです。

```text
global-settings {
	watch-config-file = true;
}

bar {
	output            = eDP-1;
	position          = bottom;
	background-colour = "#202020";

	# Condition for the default configuration set.
	condition-resolution = wider-than-high;

	config {
		position = right;
	}

	button {
		image-path          =     /usr/local/lib/firefox/browser/chrome/icons/default/default48.png;
		command[mouse-left] =     /usr/local/bin/firefox;
	}
	button {
	  image-path           =   /usr/local/share/pixmaps/thunderbird.png;
	  command[mouse-left]  =   /usr/local/bin/thunderbird;
}
```

> **訳注:** 本文は「Firefoxだけ」と説明していますが、例にはThunderbirdのボタンもあります。また末尾は2つ目のbuttonを閉じたところで終わり、外側のbarを閉じる `}` が不足しています。これは原文の例を保持したものです。実際の設定では外側も閉じ、出力名 `eDP-1`、画像・実行ファイルのパス、必要なアプリに合わせて調整します。
