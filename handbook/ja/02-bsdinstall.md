<a id="bsdinstall"></a>
# 第2章 FreeBSDのインストール

> **状態:** 意訳ドラフト。原文の全節・手順・注意点を照合し、コマンドと画面例を保持しています。実機インストールは未検証です。
> **原文:** [FreeBSD Handbook: Installing FreeBSD](https://docs.freebsd.org/en/books/handbook/bsdinstall/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/02-bsdinstall.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

画面の項目名は操作時に対応を付けやすいよう英語を併記します。原文のコード中の `{rel-latest}` はリリース番号を表す属性です。固定した原文の定義では `15.1` ですが、実行時は取得する配布物の番号に置き換えてください。`#` はroot、`%` は一般ユーザーのプロンプトで、コマンドの一部ではありません。画面と動作は使用するリリースや機種によって異なります。

<a id="bsdinstall-synopsis"></a>
## この章で行うこと

FreeBSDはamd64、ARM、RISC-V、PowerPCなどのアーキテクチャに対応します。[ダウンロードページ](https://www.freebsd.org/where/)で、自分の機種と用途に合うイメージを選びます。主な種類は次の3つです。

- **仮想マシン用ディスクイメージ:** `qcow2`、`vmdk`、`vhd`、rawなど。インストーラーではなく、OSが導入済みのディスクです。起動後に設定を行います。クラウドでも使われます。
- **SDカード用イメージ:** Raspberry Piなどの組み込み機器向けです。展開してSDカードへイメージとして書き込み、そのカードから起動します。
- **インストール用イメージ:** ISOやUSBメモリから起動し、デスクトップ・ノートPC・サーバーのディスクへFreeBSDを導入します。

この章は3番目の方法を扱います。テキスト形式のインストーラー `bsdinstall` を使い、メディアの作成、起動、各質問の意味と選び方、失敗時の対処までを説明します。導入前にLive CDとして試す方法も紹介します。画面を一字一句なぞる手順書ではなく、判断に必要な案内として読んでください。

<a id="bsdinstall-hardware"></a>
## 必要なハードウェアを確認する

最低要件はアーキテクチャとリリースによって異なります。一律の数値で判断せず、対象リリースの[リリース情報](https://www.freebsd.org/releases/)にある対応アーキテクチャ・デバイス一覧を確認します。[ダウンロードページ](https://www.freebsd.org/where/)には、機種ごとのイメージ選択の案内もあります。

<a id="bsdinstall-pre"></a>
## インストール前の準備


対応ハードウェアであることを確認したら、イメージを取得して起動メディアを作ります。既存OSを使い続けたい場合は、先に[仮想化](https://docs.freebsd.org/en/books/handbook/virtualization/)も検討できます。

作業を始める前に、次の4項目を確認します。

1. **重要なデータをバックアップする。** 保存先は導入対象ディスクの外です。USBドライブ、別のコンピューター、オンラインバックアップなどに保存し、必要なファイルが含まれ、実際に読めることも確認します。フォーマットしたディスク上のデータは失われます。
2. **導入先を決める。** FreeBSDだけを入れるならディスク全体を使えます。他のOSと共存させるなら、FreeBSDに使うディスクまたはパーティションを事前に決めます。
3. **ネットワーク情報を用意する。** ネットワーク経由で配布物を取得する方式では必須です。どの方式でも導入後にネットワーク設定を行えます。
4. **対象リリースのErrataを読む。** 安定性に配慮されていても、インストールへ影響する不具合が判明することがあります。[リリース情報](https://www.freebsd.org/releases/)から既知の問題と修正を確認します。

ディスク分割方式にはMBRとGPTがあります。i386・amd64で従来使われてきたMBRは、最大4つの基本パーティションを定義します。FreeBSDでは歴史的にこれを「スライス」と呼びます。1つを拡張パーティションにして、その中に論理パーティションを置く方式もあります。より新しいGPTは一般的な実装で128個まで扱え、論理パーティションを必要としません。

FreeBSDのブートローダーには基本パーティションまたはGPTパーティションが必要です。既に埋まっている場合は空きを作ります。データを残したまま縮小するには、既存パーティションを対応ツールで縮め、できた空きに新しく作成します。[GParted Live](https://gparted.org/livecd.php)などのツールや、[ディスク分割ソフトウェアの一覧](https://en.wikipedia.org/wiki/List_of_disk_partitioning_software)を参照できます。パーティションを変更せず複数OSを同時に動かす方法が仮想化です。

> **警告:** 縮小ツールでも対象を選び間違えることがあります。操作前にバックアップを取り、復元に使えることを確認してください。

<a id="bsdinstall-collect-network-information"></a>

DHCPサーバーがあるネットワークでは設定を自動取得できます。ない場合は管理者またはISPに、次の情報を確認します。

- このコンピューターのIPアドレス。
- サブネットマスク。
- デフォルトゲートウェイのIPアドレス。
- ネットワークのドメイン名。
- DNSサーバーのIPアドレス。

<a id="bsdinstall-installation-media"></a>
### インストールメディアを用意する

インストーラーは別のOS上で起動するアプリケーションではありません。イメージを、その形式と大きさに合うCD・DVD・USBメモリへ書き込み、そこからコンピューターを起動します。

[公式ダウンロードページ](https://www.freebsd.org/where/)から取得できます。ファイル名にはリリース、アーキテクチャ、用途が含まれます。`xz(1)`で圧縮したものと非圧縮のものがあり、提供形式はアーキテクチャと媒体によって異なります。

| ファイル名の種類 | 入っているものと用途 |
|---|---|
| `*-bootonly.iso` | 最小の光学メディア用イメージ。インストーラーのみを含み、配布物はネットワーク取得するため、導入中にインターネット接続が必要です。 |
| `*-disc1.iso` | FreeBSD本体、ソース、Ports Collectionの導入に必要なファイル。光学メディアへ書き込みます。 |
| `*-dvd1.iso` | disc1の内容に加え、ウィンドウマネージャーやアプリケーションなどの代表的なバイナリパッケージを含みます。ネット接続なしでシステムを組み立てる用途です。 |
| `*-memstick.img` | 本体、ソース、Ports Collectionの導入に必要なファイルを含むUSBメモリ用イメージ。次節の方法で書き込みます。 |
| `*-mini-memstick.img` | bootonlyと同様に配布物をネットワーク取得するUSB版。導入中にインターネット接続が必要です。 |

イメージと同じディレクトリから、少なくとも1種類のチェックサムファイルも取得します。例は `CHECKSUM.SHA256-FreeBSD-{rel-latest}-RELEASE-amd64` と `CHECKSUM.SHA512-FreeBSD-{rel-latest}-RELEASE-amd64` です。

取得したイメージのハッシュを計算して、対応するアルゴリズムのチェックサムと照合します。SHA256とSHA512は別物なので、比較するファイルを取り違えないでください。FreeBSDでは `sha256(1)`・`sha512(1)` を使え、他のOSにも同様のツールがあります。FreeBSDの `sha256sum(1)`・`sha512sum(1)` なら自動検査できます。

```shell
% sha256sum -c CHECKSUM.SHA256-FreeBSD-{rel-latest}-RELEASE-amd64 --ignore-missing
FreeBSD-{rel-latest}-RELEASE-amd64-dvd1.iso: OK
```

値は完全に一致する必要があります。不一致ならイメージが破損しているため、再ダウンロードします。

<a id="bsdinstall-usb"></a>
#### イメージをUSBメモリへ書き込む


`*memstick.img` はUSBメモリ全体の内容を表すディスクイメージです。通常のファイルとしてUSBメモリへコピーするだけでは起動できません。イメージ書き込みツールを使います。

> **重要:** 書き込み先の既存データは消えます。先にUSBメモリ内の重要データをバックアップしてください。

<a id="bsdinstall-usb-dd"></a>

**BSD・Linux・macOSなどでddを使う場合**

USBメモリを挿し、デバイス名を調べてから、取得したファイル名と書き込み先を指定します。次はFreeBSD上でamd64用イメージを最初のUSBデバイスへ書く原文例です。

> **警告:** `/dev/da0` は例です。必ず実際のUSBメモリを特定してください。指定した対象の内容は破壊されます。

```shell
# dd if=FreeBSD-{rel-latest}-RELEASE-amd64-memstick.img of=/dev/da0 bs=1M conv=sync
```

失敗した場合はUSBメモリがマウントされていないこと、デバイス名がパーティションではなくディスク全体を指すことを確認します。OSによっては `sudo(8)` が必要です。`dd(1)` の書式も少し異なり、macOSでは `bs=1m` と小文字で指定します。Linuxなど書き込みをバッファーするシステムでは、`sync(8)` で書き込み完了を確認します。

**WindowsでImage Writerを使う場合**

[Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/)を取得してフォルダーへ展開します。Win32DiskImagerを起動し、`Device` のドライブ文字が目的のUSBメモリであることを確認します。フォルダーのアイコンからイメージを選び、ファイル名を確定します。内容と書き込み先を再確認し、USBメモリ内のフォルダーを別ウィンドウで開いていないことも確かめてから、`Write` を押します。

> **警告:** Windowsでもドライブ文字を選び間違えると、そのドライブの既存データを失います。

<a id="bsdinstall-start"></a>
## インストールを開始する

標準のインストール手順では、次の確認メッセージが出るまでディスクへ変更を書き込みません。

```text
Your changes will now be written to disk. If you
have chosen to overwrite existing data, it will
be PERMANENTLY ERASED. Are you sure you want to
commit your changes?
```

これは「変更をディスクに書き込みます。上書きを選んだデータは完全に消去されます。確定しますか」という意味です。この段階より前なら中止でき、設定に不安があれば電源を切ってもインストーラーはディスクを変更していません。

> **訳注:** ここでの保証は標準のメニュー操作に対するものです。`Shell` から手動でディスクを書き換えた操作には当てはまりません。

[準備したメディア](#bsdinstall-installation-media)から起動します。USBメモリは電源を入れる前に挿します。CD・DVDでは電源投入後、できるだけ早く挿入します。メディアから起動するための設定方法は、機種とアーキテクチャによって異なります。

<a id="bsdinstall-view-probe"></a>
### ブートローダーのメニュー


インストールメディアから起動すると、次のようなメニューが表示されます。

<a id="bsdinstall-newboot-loader-menu"></a>

![ブートローダーのメニュー：bsdinstall-newboot-loader-menu.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-newboot-loader-menu.png)

通常は10秒間入力を待ち、そのままインストーラーへ進みます。導入済みシステムならFreeBSDを起動します。`Space` でタイマーを止め、強調表示された数字・文字・キーで項目を選びます。

| 項目 | 意味 |
|---|---|
| `Boot Multi User` | 通常の起動を続けます。タイマー停止後は `1`、`B`／`b`、`Enter` で進めます。 |
| `Boot Single User` | 既存システムの修復に使う[シングルユーザーモード](https://docs.freebsd.org/en/books/handbook/boot/#boot-singleuser)。`2` または `S`／`s` で選択します。 |
| `Escape to loader prompt` | 低レベルの修復コマンドを使う[ローダープロンプト](https://docs.freebsd.org/en/books/handbook/boot/#boot-loader)。`3` または `Esc` で入ります。 |
| `Reboot` | 再起動します。 |
| `Cons` | 画面、シリアル、両方（シリアル優先／画面優先）のコンソール方式を選びます。 |
| `Kernel` | 別のカーネルを読み込みます。 |
| `Boot Options` | 起動オプションのメニューを開きます。 |

<a id="bsdinstall-boot-options-menu"></a>

![ブートローダーのメニュー：bsdinstall-boot-options-menu.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-boot-options-menu.png)

起動オプション画面の前半ではメインメニューへ戻ったり設定をデフォルトへ戻したりできます。後半の設定は強調された数字・文字で `On`／`Off` を切り替え、変更するまでこの設定で起動します。

- `ACPI`: 起動中に固まる場合は `Off` を試します。ACPIが利用でき、かつ必須でない機種にだけ出ます。
- `Safe Mode`: ACPIを切っても固まる場合は `On` を試します。
- `Single User`: 既存環境を修復するときに `On` にし、問題解消後は `Off` に戻します。
- `Verbose`: 起動メッセージを詳しくし、ハードウェアの問題を調べやすくします。

`1` または `Backspace` で戻り、`Enter` で起動します。ハードウェア検出とインストーラー読み込みのメッセージが流れた後、Welcome Menuが出ます。

<a id="bsdinstall-choose-mode"></a>

![ブートローダーのメニュー：bsdinstall-choose-mode.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-choose-mode.png)

既定の `Install` を `Enter` で選ぶとインストーラーへ入ります。左右の矢印や色付きの文字でも項目を選べます。`Shell` はディスク準備などに使うコマンドライン、`Live CD` はインストール前の試用環境です。[Live CD](#using-live-cd)は章末で説明します。

起動時のハードウェア検出ログを読みたい場合は `S`／`s` と `Enter` でシェルに入り、`more /var/run/dmesg.boot` を実行します。`Space` で先へ進み、終わったら `exit` でWelcome Menuに戻ります。

<a id="using-bsdinstall"></a>
## bsdinstallの基本操作

以降はメニューの順番に沿って設定します。矢印キーで項目を移動し、`Space` で選択・解除、`Enter` で確定して次へ進みます。画面によっては後続の設定を先に求められることもあります。

<a id="bsdinstall-keymap"></a>
### キーボード配列を選ぶ


最初にキーマップのファイルが読み込まれます。

<a id="bsdinstall-keymap-loading"></a>

![キーボード配列を選ぶ：bsdinstall-keymap-loading.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-keymap-loading.png)

一覧が出たら、接続したキーボードに近い配列を上下キーで選び、`Enter` で確定します。

<a id="bsdinstall-keymap-10"></a>

![キーボード配列を選ぶ：bsdinstall-keymap-10.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-keymap-10.png)

`Esc` でこの画面を抜けると既定のキーマップになります。判断できない場合は `United States of America ISO-8859-1` も無難な選択肢です。

既定以外を選んだときは、先へ進む前にテスト画面で実際の入力を確認できます。

<a id="bsdinstall-keymap-testing"></a>

![キーボード配列を選ぶ：bsdinstall-keymap-testing.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-keymap-testing.png)

<a id="bsdinstall-hostname"></a>
### ホスト名を設定する


新しいシステムのホスト名を入力します。

<a id="bsdinstall-config-hostname"></a>

![ホスト名を設定する：bsdinstall-config-hostname.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-config-hostname.png)

ネットワーク内で重複しない名前にします。原文では `machine3.example.com` のような完全修飾ホスト名を使うことを勧めています。

<a id="bsdinstall-installation-type"></a>
### ベースシステムの導入方式を選ぶ


FreeBSD 15.0以降のインストーラーは、従来の配布セットとパッケージ方式を選べます。

<a id="bsdinstall-choose-type"></a>

![ベースシステムの導入方式を選ぶ：bsdinstall-distributions-sets-pkgbase.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-distributions-sets-pkgbase.png)

入るカーネルとユーザーランドは同じですが、配布とその後の保守方法が異なります。

- **`Distribution Sets`:** 圧縮tarアーカイブからベースを展開する従来方式です。更新には `freebsd-update(8)` を使います。安定した正式サポートの方法で、15.xの多くのインストールメディアでは既定です。
- **`Packages (Tech Preview)`:** `FreeBSD-base` リポジトリからベースを個別パッケージとして導入する `pkgbase` 方式です。導入後はベースとサードパーティーのソフトウェアを `pkg upgrade` で更新でき、管理を `pkg(8)` に統一します。

> **原文時点の位置づけ:** `Packages (Tech Preview)` は試験・先行利用向けです。16.0で既定になることが想定されていますが、15.xの本番用途で実績を重視する場合は `Distribution Sets` を選ぶよう案内されています。

<a id="bsdinstall-components"></a>
### 追加コンポーネントを選ぶ


用途とディスク容量に合わせて、追加のコンポーネントを選びます。

<a id="bsdinstall-config-components"></a>

![追加コンポーネントを選ぶ：bsdinstall-config-components.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-config-components.png)

カーネルとユーザーランドからなる「ベースシステム」は必ずインストールされます。以下の項目はアーキテクチャによって表示されないことがあります。

| 項目 | 内容 |
|---|---|
| `base-dbg` | `cat`、`ls`などのベースツールのデバッグシンボル。 |
| `kernel-dbg` | カーネルとモジュールのデバッグシンボル。 |
| `lib32-dbg` | 64ビット環境で32ビットアプリを動かす互換ライブラリのデバッグシンボル。 |
| `lib32` | 64ビット環境用の32ビット互換ライブラリ。 |
| `ports` | サードパーティーのソフトウェアの取得・ビルド・導入を自動化するPorts Collection。[PackagesとPorts](https://docs.freebsd.org/en/books/handbook/ports/)で説明します。 |
| `src` | カーネルとユーザーランドの全ソース。通常のアプリ実行には不要ですが、ドライバー・カーネルモジュール・一部PortsのビルドやFreeBSD開発に使います。原文の目安はソースに1GB、システム全体の再ビルドに追加5GBです。 |
| `tests` | FreeBSD Test Suite。 |

> **注意:** インストーラーはPorts用の十分な空き容量を確認しません。固定した原文の属性値ではPorts Collectionに約3GBを見込んでいます。空きがあることを確かめて選択してください。

<a id="bsdinstall-netinstall"></a>
### ネットワークから配布物を取得する


`-bootonly.iso` や `-mini-memstick.img` には配布物が含まれないため、ネットワーク取得の案内が出ます。

<a id="bsdinstall-netinstall-notify"></a>

![ネットワークから配布物を取得する：bsdinstall-netinstall-files.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-netinstall-files.png)

この画面が途中で現れたら、先に[ネットワークインターフェースの設定](#bsdinstall-config-network-dev)を行ってください。

<a id="bsdinstall-partitioning"></a>
## ディスク領域を割り当てる


続いてディスクの使い方を選びます。

<a id="bsdinstall-zfs-partmenu"></a>

![ディスク領域を割り当てる：bsdinstall-zfs-partmenu.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-partmenu.png)

- **`Auto (ZFS)`:** ルートをZFSに置きます。GELI暗号化やブート環境を利用できます。
- **`Auto (UFS)`:** UFS用のパーティションを自動作成します。
- **`Manual`:** メニューから自分でパーティションを作ります。
- **`Shell`:** `gpart(8)`、`fdisk(8)`、`bsdlabel(8)` などを使ってコマンドラインで構成します。

まず配置を考える際の注意点を説明し、その後で各方法を見ていきます。

<a id="configtuning-initial"></a>
### パーティションの配置を考える

既定の構成はシステム全体で1つのファイルシステムを使います。UFSで十分な容量や複数ディスクがある場合は、複数のファイルシステムに分ける方法もあります。

原文は回転式ハードディスクの特性を踏まえ、小さくアクセスの多い領域を転送速度が高い外周側へ、大きな `/usr` などを内周側へ配置する方法を説明しています。作成順の例は `/`、swap、`/var`、`/usr` です。書き込みの多い小さな領域で生じる断片化を、読み取り中心の領域から分けられます。大きな `/usr` を外側へ移すより、頻繁に書き込む `/var` を外側へ置く方が効果的だとしています。

`/var` にはメールボックス、ログ、印刷スプールなどを置きます。利用者数や保存期間によって大きく増えるため、用途から容量を決めます。原文の一般的な目安は1GB程度の空きですが、固定値として扱わないでください。`/var/tmp` はパッケージ展開の一時領域にもなるため、FirefoxやLibreOfficeなどの大きなパッケージを扱うなら余裕が必要です。

`/usr` はシステムを支えるファイル、Ports Collection、ソースを置く場所で、原文は最低2GBを勧めています。また、ここではホームディレクトリの既定位置を `/usr/home`、`/home` をそのシンボリックリンクとして説明しています。ホームを別パーティションへ置くこともできます。片方が空いているのに別の領域が満杯にならないよう、実際の用途を考えます。

swapの概算として原文はRAMの約2倍を挙げています。RAMが少ない構成では多めのswapが有利な場合があり、極端に少ないとVMのページ走査が非効率になったり、後のRAM増設で問題になったりします。必要量はRAM容量と負荷に依存し、RAMが大きい構成では比率を小さくできます。

複数のSCSIディスクや、別々のコントローラーにつながるIDEディスクがある大規模構成では、最大4台に同程度のswapを分散することを勧めています。カーネルは異なるサイズも扱えますが、内部データ構造は最大のswapパーティションの4倍に比例するため、サイズを揃えると効率よくストライピングできます。大きなswapで警告が出た場合は、その案内に従って割り当て追跡用メモリの上限を調整します。十分なswapは、暴走プログラムに対処する猶予を作る場合もあります。

> **訳注:** この節には回転式ディスクや従来構成に関する目安が含まれます。SSDや大容量RAMの環境へ、そのままの配置・容量を一律に適用する説明ではありません。

<a id="bsdinstall-part-guided"></a>
### UFSの自動分割を使う


利用可能なディスクが表示されます。複数ある場合は、FreeBSDを入れるディスクを選びます。

<a id="bsdinstall-part-guided-disk"></a>

![UFSの自動分割を使う：bsdinstall-part-guided-disk.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-guided-disk.png)

`Entire Disk` はディスク全体を使う構成を作り、`Partition` は未使用領域内に構成を作ります。

<a id="bsdinstall-part-entire-part"></a>

![UFSの自動分割を使う：bsdinstall-part-entire-part.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-entire-part.png)

次にパーティション方式を選びます。amd64では通常GPTが適しています。GPT非対応の古い機種はMBRを使い、それ以外の方式は主に特殊・旧式の機種向けです。[方式の一覧](#partition-schemes)も参照してください。

<a id="bsdinstall-ufs-scheme"></a>

![UFSの自動分割を使う：bsdinstall-part-manual-partscheme.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-manual-partscheme.png)

作成された構成を確認します。`Revert` は元の状態に戻し、`Auto` は自動構成を作り直します。パーティションの手動作成・変更・削除も可能です。内容が適切なら `Finish` で進みます。

<a id="bsdinstall-part-review"></a>

![UFSの自動分割を使う：bsdinstall-part-review.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-review.png)

次の確認が、フォーマット前に戻れる最後の機会です。`Back` は分割メニューへ戻り、`Revert & Exit` はディスクへ変更を書き込まずに終了します。`Commit` を選ぶと実際の書き込みを開始します。

<a id="bsdinstall-ufs-final-confirmation"></a>

![UFSの自動分割を使う：bsdinstall-final-confirmation.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-final-confirmation.png)

確定後は[配布ファイルの取得・展開](#bsdinstall-fetching-distribution)へ進みます。

<a id="bsdinstall-part-manual"></a>
### 手動で分割する


`Manual` を選ぶとパーティションエディターが開きます。

<a id="bsdinstall-part-manual-create"></a>

![手動で分割する：bsdinstall-part-manual-create.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-manual-create.png)

対象ディスク（画面例では `ada0`）を選び、`Create` で方式のメニューを開きます。

<a id="bsdinstall-part-manual-partscheme"></a>

![手動で分割する：bsdinstall-part-manual-partscheme.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-manual-partscheme.png)

amd64は通常GPT、GPT非対応の古い機種はMBRを選びます。代表的な方式は次のとおりです。

<a id="partition-schemes"></a>

| 方式 | 説明 |
|---|---|
| APM | Apple Partition Map。PowerPCで使われます。 |
| BSD | MBRなしのBSDラベル。他OSのツールが認識できない場合があり、「dangerously dedicated mode」と呼ばれることもあります。 |
| GPT | [GUID Partition Table](https://en.wikipedia.org/wiki/GUID_Partition_Table)。 |
| MBR | [Master Boot Record](https://en.wikipedia.org/wiki/Master_boot_record)。 |

方式を作成したら、再び `Create` でパーティションを追加します。`Tab` でOK・Options・Cancelなどを巡回し、入力欄へ移動します。

<a id="bsdinstall-part-manual-addpart"></a>

![手動で分割する：bsdinstall-part-manual-addpart.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-part-manual-addpart.png)

標準的なGPT構成は、起動領域・UFSまたはZFSの領域・swapを組み合わせます。

- `freebsd-boot` または `efi`: FreeBSDの起動コード。
- `freebsd-ufs`: UFSファイルシステム。
- `freebsd-zfs`: ZFSファイルシステム。[ZFS章](https://docs.freebsd.org/en/books/handbook/zfs/)を参照。
- `freebsd-swap`: swap領域。

利用できるGPTタイプの詳細は `gpart(8)` にあります。`/`、`/var`、`/tmp`、`/usr` を分ける従来型構成も作れます。RAMに余裕があれば、`/tmp` を後から `tmpfs(5)` として置く方法もあります。

`Size` は `K`・`M`・`G` で指定できます。512バイト／4KBセクターのどちらでも整列しやすいよう、4KBの倍数にします。通常は1MBや1GBの倍数にすると揃えやすくなります。ただしBIOS起動の `freebsd-boot` は古い起動コードの制約で **512KB以下** にします。この制約はUEFI起動にはありません。

ファイルシステムを作る場合は `Mountpoint` を指定します。UFSを1つだけ作るなら `/` です。

`Label` はパーティションを識別する名前です。接続先やポートが変わるとデバイス番号が変わることがありますが、ラベルは変わりません。`/etc/fstab` でディスク名・番号の代わりにラベルを使うと、ハードウェア変更に強くなります。GPTラベルは `/dev/gpt/` に現れます。他方式ではラベルの機能と `/dev/` 内の場所が異なります。

ラベルはすべて一意にします。機種名・用途・場所などを含めると衝突を避けやすく、たとえばホスト名 `lab` のルート領域なら `labroot` や `rootfslab` とできます。

<a id="bsdinstall-part-manual-splitfs"></a>

**20GBディスクでの従来型構成の原文例**

先にGPTを作り、以下のように分割します。余裕があればswapや `/var` を広げられます。`ex` はexampleの略なので、実際には固有のラベルへ変更してください。既定の `gptboot` は最初のUFSパーティションを `/` と想定します。

| タイプ | サイズ | マウント先 | ラベル |
|---|---|---|---|
| `freebsd-boot` | `512K` | — | — |
| `freebsd-ufs` | `2G` | `/` | `exrootfs` |
| `freebsd-swap` | `4G` | — | `exswap` |
| `freebsd-ufs` | `2G` | `/var` | `exvarfs` |
| `freebsd-ufs` | `1G` | `/tmp` | `extmpfs` |
| `freebsd-ufs` | 残り全部（既定値） | `/usr` | `exusrfs` |

作成できたら `Finish` で[配布ファイルの取得](#bsdinstall-fetching-distribution)へ進みます。

<a id="bsdinstall-part-zfs"></a>
### ルートをZFSに置く自動分割


この方式はディスク全体を使い、**選択したディスクの全内容を消去します**。ZFSプールの作成方法をメニューで設定します。

<a id="bsdinstall-zfs-menu"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-menu.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-menu.png)

| 項目 | 意味 |
|---|---|
| `Install` | 選択した設定で導入を進めます。 |
| `Pool Type/Disks` | プールの構成と使用ディスクを選びます。自動作成はstripeを除き単一の最上位vdevに限られ、複雑な構成には[Shell方式](#bsdinstall-part-shell)を使います。 |
| `Rescan Devices` | ディスク一覧を再検出します。 |
| `Disk Info` | パーティション、機種名、取得できればシリアル番号などを確認します。 |
| `Pool Name` | プール名。既定は `zroot` です。 |
| `Force 4K Sectors?` | 4KB境界に整列し、ZFSに4KBセクターを使わせます。既定で有効です。512バイトセクターのディスクでも使え、将来4KBディスクを追加・交換しやすくなります。`Enter` で切り替えます。 |
| `Encrypt Disks?` | GELI暗号化を使います。`Enter` で切り替え、詳細は[GELIによる暗号化](https://docs.freebsd.org/en/books/handbook/disks/#disks-encrypting-geli)を参照します。 |
| `Partition Scheme` | GPTなどの分割方式。通常はGPTが推奨され、`Enter` で選びます。 |
| `Swap Size` | swap容量。 |
| `Mirror Swap?` | swapもミラー化するかを指定します。有効にするとクラッシュダンプが利用できなくなる点に注意します。 |
| `Encrypt Swap?` | 起動ごとの一時鍵でswapを暗号化し、再起動時に鍵を破棄します。[swap暗号化](https://docs.freebsd.org/en/books/handbook/disks/#swap-encrypting)も参照します。 |
| `ZFS Pool Options` | プール作成時の追加プロパティ。`zpool-create(8)`・`zpoolprops(7)`を参照します。 |

`T` でプールのタイプとディスクを選びます。

<a id="bsdinstall-zfs-vdev_type"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-vdev_type.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-vdev_type.png)

| タイプ | 特徴と原文の最小ディスク数 |
|---|---|
| `stripe` | 全ディスクの容量を使えますが冗長性はなく、1台の故障でプール全体を失います。 |
| `mirror` | 各ディスクに完全なコピーを保持。並列読み取りができ、書き込みはすべてへ行います。最低2台で、1台残ればデータを維持できます。 |
| `raid10` | ミラーをストライピング。高性能ですが利用可能容量は少なく、偶数台・最低4台が必要です。 |
| `raidz1` | 同時1台の故障に耐え、最低3台。 |
| `raidz2` | 同時2台の故障に耐え、最低4台。 |
| `raidz3` | 同時3台の故障に耐え、最低5台。 |

タイプの選択後、ディスクを選びます。

<a id="bsdinstall-zfs-disk_select"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-disk_select.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-disk_select.png)

台数などが検査され、不足するとエラー画面になります。

<a id="bsdinstall-zfs-vdev_invalid"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-vdev_invalid.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-vdev_invalid.png)

`Change Selection` でディスクを選び直すか、`Back` でタイプを変更します。追加したディスクが見えない場合は `Rescan Devices` を使います。

<a id="bsdinstall-zfs-rescan-devices"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-rescan-devices.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-rescan-devices.png)

誤消去を避けるため、`Disk Info` でディスクの情報を確認できます。

<a id="bsdinstall-zfs-disk_info"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-disk_info.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-disk_info.png)

`N` でプール名を入力し、`OK` で確定します。`Cancel` なら既定の名前を残して戻ります。

<a id="bsdinstall-zfs-pool-name"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-pool-name.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-pool-name.png)

`S` でswap容量を入力し、同様に確定または取り消しを選びます。

<a id="bsdinstall-zfs-swap-amount"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-swap-amount.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-swap-amount.png)

設定が整ったら先頭の `>>> Install` を選びます。ディスクを消去する前の、最後の確認が出ます。

<a id="bsdinstall-zfs-warning"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-warning.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-warning.png)

GELI暗号化を有効にした場合は、パスフレーズを2回入力します。

<a id="bsdinstall-zfs-geli_password"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-geli_password.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-geli_password.png)

暗号化の初期化が始まります。

<a id="bsdinstall-zfs-init-encription"></a>

![ルートをZFSに置く自動分割：bsdinstall-zfs-init-encription.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-zfs-init-encription.png)

その後は通常どおり[配布ファイルの取得・展開](#bsdinstall-fetching-distribution)へ進みます。

<a id="bsdinstall-part-shell"></a>
### Shellからディスクを構成する

メニューでは表せない高度な構成には `Shell` を使います。自分でパーティションとファイルシステムを作成し、`/tmp/bsdinstall_etc/fstab` を設定して、各ファイルシステムを `/mnt` 配下へマウントします。準備が済んだら `exit` でbsdinstallに戻り、導入を続けます。

<a id="bsdinstall-fetching-distribution"></a>
## 配布ファイルを取得・検証・展開する


所要時間は選択した配布物、メディア、コンピューターの性能によって異なります。進行状況は画面に表示されます。

まず選択ディスクのフォーマットとパーティション初期化を行います。bootonlyやmini-memstickでは、次に必要な配布物をダウンロードします。

<a id="bsdinstall-distfile-fetching"></a>

![配布ファイルを取得・検証・展開する：bsdinstall-distfile-fetching.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-distfile-fetching.png)

取得中の破損やメディアの読み取り誤りがないか、配布ファイルを検証します。

<a id="bsdinstall-distfile-verify"></a>

![配布ファイルを取得・検証・展開する：bsdinstall-distfile-verifying.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-distfile-verifying.png)

検証できたファイルをディスクへ展開します。

<a id="bsdinstall-distfile-extract"></a>

![配布ファイルを取得・検証・展開する：bsdinstall-distfile-extracting.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-distfile-extracting.png)

すべての展開が終わると、次節の導入後設定へ進みます。

<a id="bsdinstall-post"></a>
## ネットワーク・アカウント・時刻・サービスを設定する

配布物の展開後は、rootのパスワード、ネットワーク、タイムゾーン、自動起動するサービス、セキュリティ、一般ユーザーを順に設定します。

<a id="bsdinstall-post-root"></a>
### rootのパスワードを設定する


管理者である `root` のパスワードを設定します。入力文字は画面に表示されません。タイプミスを避けるため、同じものを2回入力します。

<a id="bsdinstall-post-set-root-passwd"></a>

![rootのパスワードを設定する：bsdinstall-post-root-passwd.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-post-root-passwd.png)

<a id="bsdinstall-config-network-dev"></a>
### ネットワークインターフェースを設定する


検出されたネットワークインターフェースから、設定するものを選びます。

<a id="bsdinstall-configure-net-interface"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface.png)

有線EthernetならIPv4の設定へ進みます。無線なら、まずアクセスポイントを検索します。

<a id="bsdinstall-wireless-scan"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-wireless-scan.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-wireless-scan.png)

無線ネットワークはSSIDという名前で識別されます。一覧にはSSIDと対応する暗号化方式が出ます。見つからなければ `Rescan` で再検索します。それでも出ないときはアンテナ接続を確認したり、アクセスポイントへ近づけたりして、その都度検索し直します。

<a id="bsdinstall-wireless-accesspoints"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-wireless-accesspoints.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-wireless-accesspoints.png)

接続先を選んだら暗号化の情報を入力します。原文は、安全性の低いWEPなどよりWPA2を強く推奨しています。WPA2ではPSK（事前共有鍵）、つまり無線ネットワークのパスワードを入力します。入力はアスタリスクで隠されます。

<a id="bsdinstall-wireless-wpa2"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-wireless-wpa2setup.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-wireless-wpa2setup.png)

次にIPv4を使うかを選びます。

<a id="bsdinstall-configure-net-ipv4"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface-ipv4.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface-ipv4.png)

DHCPサーバーがあるネットワークでは自動設定を使えます。ない場合は手動で静的に設定します。

> **注意:** 推測した値を適当に入力しても接続できません。[事前に用意する情報](#bsdinstall-collect-network-information)を管理者やISPに確認してください。

DHCPがある場合は `Yes` を選びます。サーバーの検出と情報取得で1分ほど止まって見える場合があります。

<a id="bsdinstall-net-ipv4-dhcp"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface-ipv4-dhcp.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface-ipv4-dhcp.png)

ない場合は `No` を選び、次を入力します。

<a id="bsdinstall-net-ipv4-static"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface-ipv4-static.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface-ipv4-static.png)

- `IP Address`: このコンピューター固有のIPv4アドレス。他の機器と重複させません。
- `Subnet Mask`: ネットワークのサブネットマスク。
- `Default Router`: デフォルトゲートウェイのIPv4アドレス。

続いてIPv6を使うなら `Yes` を選びます。

<a id="bsdinstall-net-ipv6"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface-ipv6.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface-ipv6.png)

IPv6も自動・手動を選べます。SLAACはローカルのルーターから情報を得て自動構成する方式です。詳細は [RFC 4862](https://www.rfc-editor.org/rfc/rfc4862)を参照してください。対応ルーターがある場合は次の画面で `Yes` を選び、取得を待ちます。

<a id="bsdinstall-net-ipv6-slaac"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface-slaac.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface-slaac.png)

ルーターが利用できなければ `No` を選び、静的な情報を入力します。

<a id="bsdinstall-net-ipv6-static"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-interface-ipv6-static.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-interface-ipv6-static.png)

- `IPv6 Address`: このコンピューター固有のIPv6アドレス。
- `Default Router`: デフォルトゲートウェイのIPv6アドレス。

最後に、ホスト名とネットワークアドレスを対応させるDNSリゾルバーを設定します。DHCPやSLAACを使った場合は、既に値が入っていることもあります。必要なら `Search` に検索用ドメインを入力し、`DNS #1`・`DNS #2` にDNSサーバーのIPv4／IPv6アドレスを設定します。少なくとも1台のDNSサーバーが必要です。

<a id="bsdinstall-net-dns-config"></a>

![ネットワークインターフェースを設定する：bsdinstall-configure-network-ipv4-dns.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-configure-network-ipv4-dns.png)

ネットワーク設定後はミラーを選びます。近い地域のミラーほど、一般に取得が速くなります。`https://download.freebsd.org Main Site (GeoDNS, HTTPS)` または `ftp://download.freebsd.org Main Site (GeoDNS, FTP)` は近いミラーへ自動的に振り分けます。

<a id="bsdinstall-netinstall-mirror"></a>

![ネットワークインターフェースを設定する：bsdinstall-netinstall-mirrorselect.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-netinstall-mirrorselect.png)

<a id="bsdinstall-timezone"></a>
### タイムゾーンと日時を設定する


地域・国・タイムゾーンを選び、現地時間を正しく扱えるようにします。夏時間などの地域別の時刻変更にも関係します。原文の画面例はヨーロッパのスペイン本土で、利用者の所在地に合わせて選び直します。

矢印キーと `Enter` で地域を選びます。

<a id="bsdinstall-timezone-region"></a>

![タイムゾーンと日時を設定する：bsdinstall-timezone-region.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-timezone-region.png)

同様に国を選びます。

<a id="bsdinstall-timezone-country"></a>

![タイムゾーンと日時を設定する：bsdinstall-timezone-country.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-timezone-country.png)

該当するタイムゾーンを選びます。

<a id="bsdinstall-timezone-zone"></a>

![タイムゾーンと日時を設定する：bsdinstall-timezone-zone.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-timezone-zone.png)

表示されたタイムゾーンの略称が正しいことを確認します。

<a id="bsdinstall-timezone-confirmation"></a>

![タイムゾーンと日時を設定する：bsdinstall-timezone-confirm.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-timezone-confirm.png)

日付は矢印キーで合わせて `Set Date`、変更しない場合は `Skip` を選びます。

<a id="bsdinstall-timezone-date"></a>

![タイムゾーンと日時を設定する：bsdinstall-timezone-date.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-timezone-date.png)

時刻も `Set Time` で確定するか `Skip` で飛ばします。

<a id="bsdinstall-timezone-time"></a>

![タイムゾーンと日時を設定する：bsdinstall-timezone-time.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-timezone-time.png)

<a id="bsdinstall-sysconf"></a>
### 自動起動するサービスを選ぶ


システム起動時に開始するサービスを選びます。すべて任意なので、必要なものだけを有効にします。

<a id="bsdinstall-config-serv"></a>

![自動起動するサービスを選ぶ：bsdinstall-config-services.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-config-services.png)

| サービス | 用途 |
|---|---|
| `sshd` | 暗号化したSSH接続による遠隔ログイン。遠隔から入る必要がある場合に有効にします。 |
| `ntpd` | 外部の時刻サーバーやプールと時計を自動同期します。 |
| `ntpd_sync_on_start` | 起動時のntpdに `-g` を付け、一度だけ大きな時刻補正を許可して同期します。 |
| `local_unbound` | このコンピューター用のキャッシュ・転送DNSリゾルバー。ネットワーク全体へ提供するDNSを作る場合は、別途 `dns/unbound` を導入します。 |
| `powerd` | 電力制御・省電力。 |
| `moused` | コマンドラインのシステムコンソールでマウスを使います。 |
| `dumpdev` | 障害解析用のクラッシュダンプ。問題調査に役立つため、原文は有効化を勧めています。 |

<a id="bsdinstall-hardening"></a>
### セキュリティ強化の設定を選ぶ


必要なセキュリティ強化を選びます。すべて任意ですが、原文は活用を勧めています。制限により使えなくなる機能も確認してください。

<a id="bsdinstall-hardening-options"></a>

![セキュリティ強化の設定を選ぶ：bsdinstall-hardening.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-hardening.png)

| 項目 | 効果 |
|---|---|
| `hide_uids` | 非特権ユーザーから、別UIDのプロセスを隠します。 |
| `hide_gids` | 非特権ユーザーから、別GIDのプロセスを隠します。 |
| `hide_jail` | 非特権ユーザーから、jail内のプロセスを隠します。 |
| `read_msgbuf` | 非特権ユーザーによるカーネルメッセージバッファの読み取りを禁止し、`dmesg(8)` などを制限します。 |
| `proc_debug` | 非特権ユーザーのプロセスデバッグを制限します。一部procfs機能、`ptrace()`、`ktrace()`などに加え、`lldb(1)`・`truss(1)`・`procstat(1)`やPHPなどの一部デバッグ機能にも影響します。 |
| `random_pid` | プロセスIDをランダム化します。 |
| `clear_tmp` | 起動時に `/tmp` を掃除します。 |
| `disable_syslogd` | syslogdを既定の `-s` より厳しい `-ss` で動かし、ネットワークソケットを開かせません。`-s` はUDP 514での受信を止めますが、`-ss` はポート自体を開きません。 |
| `secure_console` | シングルユーザーモードに入るとき、rootのパスワードを求めます。 |
| `disable_ddtrace` | カーネルへ影響するDTraceの破壊的操作を制限します。破壊的操作には明示的な許可が必要で、利用時の `-w` との関係は `dtrace(1)` を確認します。 |

syslogdの詳細は `syslogd(8)`、DTraceの詳細は `dtrace(1)` を参照してください。

<a id="bsdinstall-addusers"></a>
### 一般ユーザーを作成する


日常のログインにはrootではなく一般ユーザーを使います。rootには実質的な操作制限がなく、誤操作への保護も弱いためです。`Yes` を選び、少なくとも1人の一般ユーザーを作成します。

<a id="bsdinstall-add-user1"></a>

![一般ユーザーを作成する：bsdinstall-adduser1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-adduser1.png)

案内に従って情報を入力します。画面例では `asample` を作っています。

<a id="bsdinstall-add-user2"></a>

![一般ユーザーを作成する：bsdinstall-adduser2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-adduser2.png)

| 入力項目 | 内容と通常の選び方 |
|---|---|
| `Username` | ログイン名。システム内で一意にし、空白を含めません。大文字・小文字は区別されます。名前の頭文字と姓を組み合わせるなどの慣例があります。 |
| `Full name` | 説明用の氏名。空白を使えます。 |
| `Uid` | ユーザーID。通常は空欄で自動割り当てにします。 |
| `Login group` | 主グループ。通常は空欄で既定値を使います。 |
| `Invite user into other groups?` | 追加するグループ。管理者権限を使うユーザーなら `wheel` を指定します。 |
| `Login class` | 通常は既定のままにします。 |
| `Shell` | 一覧から対話シェルを選びます。[シェル](https://docs.freebsd.org/en/books/handbook/basics/#shells)も参照してください。 |
| `Home directory` | ホームディレクトリ。通常は既定で構いません。 |
| `Home directory permissions` | ホームのアクセス権。通常は既定で構いません。 |
| `Use password-based authentication?` | 通常は `yes` とし、ログイン時にパスワードを求めます。 |
| `Use an empty password?` | 通常は `no`。空のパスワードは安全ではありません。 |
| `Use a random password?` | 自分で次の欄へ設定するなら `no`。 |
| `Enter password` | パスワードを入力します。文字は表示されません。 |
| `Enter password again` | 確認のため再入力します。 |
| `Lock out the account after creation?` | 通常は `no` としてログイン可能にします。 |

最後に要約が表示されます。間違いがあれば `no` で修正し、正しければ `yes` で作成します。

<a id="bsdinstall-add-user3"></a>

![一般ユーザーを作成する：bsdinstall-adduser3.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-adduser3.png)

続けて作る場合は `Add another user?` に `yes`、終える場合は `no` を選びます。詳しくは[ユーザーとアカウント管理](https://docs.freebsd.org/en/books/handbook/basics/#users-synopsis)を参照してください。

<a id="bsdinstall-final-conf"></a>
### 最終確認と初回起動


インストールと設定が終わると、最後に変更できるメニューが出ます。

<a id="bsdinstall-final-config"></a>

![最終確認と初回起動：bsdinstall-finalconfiguration.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-finalconfiguration.png)

`Add User`、`Root Password`、`Hostname`、`Network`、`Services`、`System Hardening`、`Time Zone` から、前述の各設定へ戻れます。このほか `Firmware` はWi-Fiやグラフィックスなどに必要なファームウェアを取得・導入し、`Handbook` はハンドブックを取得・導入します。

完了したら `Exit` を選びます。

<a id="bsdinstall-final-modification-shell"></a>

![最終確認と初回起動：bsdinstall-final-modification-shell.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-final-modification-shell.png)

再起動前に追加の手動設定をするか聞かれます。`Yes` は新システム内のシェル、`No` は最後の画面へ進みます。

<a id="bsdinstall-final-main"></a>

![最終確認と初回起動：bsdinstall-mainexit.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/bsdinstall/bsdinstall-mainexit.png)

さらに特殊な設定が必要なら `Live CD` でメディア側の環境へ入ります。完了していれば `Reboot` で新システムを起動します。インストールメディアを外さないと、再びメディアから起動することがあります。

起動メッセージの後に `login:` が出たら、作成した一般ユーザーでログインします。rootでの常用は避け、管理操作が必要なときだけ[スーパーユーザー](https://docs.freebsd.org/en/books/handbook/basics/#users-superuser)になります。

コンソールで起動メッセージを遡るには `Scroll-Lock` を押し、`PgUp`・`PgDn`・矢印キーを使います。もう一度 `Scroll-Lock` で通常表示へ戻ります。起動後でも `less /var/run/dmesg.boot` で読め、`q` で終了できます。

sshdを有効にした場合、初回はSSHホスト鍵を生成するため少し長くかかり、次回から速くなります。原文には次のような鍵の指紋の表示例があります。

```text
Generating public/private rsa1 key pair.
Your identification has been saved in /etc/ssh/ssh_host_key.
Your public key has been saved in /etc/ssh/ssh_host_key.pub.
The key fingerprint is:
10:a0:f5:af:93:ae:a3:1a:b2:bb:3c:35:d9:5a:b3:f3 root@machine3.example.com
The key's randomart image is:
+--[RSA1 1024]----+
|    o..          |
|   o . .         |
|  .   o          |
|       o         |
|    o   S        |
|   + + o         |
|o . + *          |
|o+ ..+ .         |
|==o..o+E         |
+-----------------+
Generating public/private dsa key pair.
Your identification has been saved in /etc/ssh/ssh_host_dsa_key.
Your public key has been saved in /etc/ssh/ssh_host_dsa_key.pub.
The key fingerprint is:
7e:1c:ce:dc:8a:3a:18:13:5b:34:b5:cf:d9:d1:47:b2 root@machine3.example.com
The key's randomart image is:
+--[ DSA 1024]----+
|       ..     . .|
|      o  .   . + |
|     . ..   . E .|
|    . .  o o . . |
|     +  S = .    |
|    +  . = o     |
|     +  . * .    |
|    . .  o .     |
|      .o. .      |
+-----------------+
Starting sshd.
```

> **訳注:** この出力例にはRSA1・DSAなどの古い形式が含まれます。原文の表示例として保持したもので、現在の鍵形式・強度を指定する設定例ではありません。

鍵の指紋とSSHは [OpenSSH](https://docs.freebsd.org/en/books/handbook/security/#openssh)を参照してください。グラフィカル環境は標準では入りません。[X Window System](https://docs.freebsd.org/en/books/handbook/x11/)で追加方法を説明します。

終了するときは、いきなり電源を切らず正しくシャットダウンします。`wheel` のユーザーなら `su` を実行してrootのパスワードを入力し、`shutdown -p now` を実行します。安全に終了し、対応ハードウェアなら電源も切れます。

<a id="bsdinstall-install-trouble"></a>
## インストール時のトラブルに対処する

まず対象リリースの[Hardware Notes](https://www.freebsd.org/releases/)で、ハードウェアが対応しているかを確認します。

マザーボードなどのファームウェアを更新すると、導入時の問題が解消する場合もあります。マザーボードのファームウェアはBIOSと呼ばれることが多く、製造元が更新版と案内を提供します。ただし更新に失敗すると起動不能になるおそれがあります。原文も、重要な修正などの理由なしに更新しないというメーカーの一般的な案内を紹介しています。

ハードウェア検出中に固まる、導入中の動作がおかしい、といった場合はACPIが原因のことがあります。i386・amd64のFreeBSDは検出できたACPIを広く利用しますが、ドライバーやマザーボード・BIOS双方の不具合が影響する場合があります。第3段階のブートローダーで、次を設定して無効化できます。

```text
set hint.acpi.0.disabled="1"
```

この設定は起動ごとにリセットされます。継続して使う場合は `/boot/loader.conf` に `hint.acpi.0.disabled="1"` を追加します。詳しくは[起動の仕組み](https://docs.freebsd.org/en/books/handbook/boot/#boot-synopsis)を参照してください。

<a id="using-live-cd"></a>
## Live CDで試す

Welcome Menuの `Live CD` は、ディスクへ導入する前にFreeBSDを試したいときに使えます。

- ログイン名は `root`、パスワードは空欄です。
- インストールメディアから直接動くため、ディスクへ導入した環境よりかなり遅くなります。
- 利用できるのはコマンドプロンプトで、グラフィカル環境ではありません。
