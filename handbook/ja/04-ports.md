<a id="ports"></a>
# 第4章 アプリケーションの導入：PackagesとPorts

> **状態:** 意訳ドラフト。固定原文の全節とコード・出力例を照合しています。実機での導入・更新は未検証です。
> **原文:** [Installing Applications: Packages and Ports](https://docs.freebsd.org/en/books/handbook/ports/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/04-ports.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

コードと出力は原文の例を保持しています。古いパッケージの版、2023年のブランチ、13.1-RELEASEなどは操作を説明するための例で、現在の推奨対象ではありません。利用するOS・Portsブランチ・パッケージ名・パスに合わせて置き換えてください。`#` はrootのプロンプトで、入力するコマンドの一部ではありません。

<a id="ports-synopsis"></a>
## この章で学ぶこと

FreeBSDにはベースシステムの豊富なツールに加え、サードパーティーのソフトウェアを入れる2つの仕組みがあります。**Packages**はビルド済みバイナリ、**Ports Collection**はソースからのビルドを使います。いずれもネットワークやローカルメディアから導入できます。

この章では、両者の使い分け、必要なソフトウェアの探し方、pkgによるパッケージ管理、Portsからのビルド、導入後の設定ファイルの見つけ方、インストール失敗時の対処を説明します。

<a id="ports-overview"></a>
## PackagesとPortsの使い分け

FreeBSDの「port」は、ソースの取得、展開、パッチ適用、コンパイル、インストールを自動化するファイル一式です。FreeBSDへ未対応のソフトウェアには修正が必要になる場合がありますが、[Ports Portal](https://ports.freebsd.org/)には既に移植された多数のアプリケーションがあります。配布が可能なものはビルド済みパッケージも提供されます。

パッケージは実行ファイル・設定・文書を含み、`pkg install` などの `pkg(8)` で操作します。Ports・Packagesとも依存関係を扱い、必要なライブラリが未導入なら先に導入します。

**パッケージが向く場合**

- 圧縮済みバイナリは通常ソースより小さく、転送量を抑えられます。
- コンパイル時間が不要です。特に遅い機種でFirefox、KDE Plasma、GNOMEなどを入れる場合に有利です。
- FreeBSD上でのビルド手順を理解しなくても利用できます。

**Portsが向く場合**

- 多くのシステムで動く保守的な既定設定ではなく、自分に合うコンパイルオプションを選べます。
- ビルド時に必要な機能だけを選べます。たとえばNGINXには多数の組み込み機能があります。`nginx` と `nginx-lite` のように複数のパッケージもありますが、機能の多い版は依存先が増え、容量と攻撃面が広がります。間接依存でXライブラリなどまで入る場合もあり、Portsなら必要な機能に絞れます。
- バイナリ再配布を禁じるライセンスのソフトウェアでは、利用者によるソースからのビルドが必要です。
- バイナリ配布を信頼せずソースを確認したい場合や、独自のパッチを当てたい場合に利用できます。

Portsの更新を追うには、[FreeBSDメーリングリスト](https://lists.freebsd.org/)の `freebsd-ports` と `freebsd-ports-bugs` を参照します。

> **注意:** 導入前に [VuXML](https://vuxml.freebsd.org/)で対象の脆弱性を確認します。導入済みパッケージは `pkg audit -F` で既知の脆弱性に照合できます。

<a id="ports-finding-applications"></a>
## 必要なソフトウェアを探す

利用可能なアプリケーションは増え続けています。次の方法で探せます。

- [Ports Portal](https://ports.freebsd.org/)はFreeBSD公式の検索可能な一覧です。名前やカテゴリで検索できます。
- [FreshPorts](https://www.freshports.org/)は検索と変更履歴を提供します。登録するとウォッチリストを作り、対象portの更新をメールで受け取れます。Dan Langilleが運営しています。
- 目的のものが見つからなければ、[SourceForge](https://sourceforge.net/)や[GitHub](https://github.com/)でプロジェクトを見つけ、その後Ports Portalで移植済みか調べます。
- `pkg(8)` でバイナリパッケージのリポジトリを検索します。

<a id="pkgng-intro"></a>
## pkgでバイナリパッケージを管理する

`pkg(8)` はパッケージの登録・追加・削除・更新を行います。公式ミラーのビルド済みパッケージだけで運用する場合、通常はpkgで管理できます。

ソースからビルドする運用には、別途[Ports管理ツール](#ports-upgrading-tools)が必要です。これらのツールはソースとバイナリを扱えますが、pkgの導入対象はバイナリパッケージであり、Portsのビルド管理そのものを置き換えるものではありません。

<a id="pkgng-initial-setup"></a>
### pkgを使い始める

対応中のFreeBSDには `/usr/sbin/pkg`、すなわち `pkg(7)` が入っています。これは本体の `pkg(8)` を導入するための小さな入口です。初回のブートストラップにはインターネット接続が必要です。

次を実行します。

```shell
# pkg
```

未導入なら確認が表示されます。

```text
The package management tool is not yet installed on your system.
Do you want to fetch and install it now? [y/N]
```

承認するとpkg本体を取得・展開し、ローカルのデータベースを初期化して、最初に要求した操作へ進みます。

`pkg -N` は導入を始めずに本体の有無を調べます。`pkg bootstrap` は他の操作をせず本体だけを導入し、`-f` を付けると再導入を強制できます。

一般的な使い方は `pkg(8)` または引数なしの `pkg`、設定は `pkg.conf(5)` を参照します。サブコマンドごとにマニュアルがあり、たとえばinstallは次で読めます。

```shell
# pkg help install
```

以下はよく使う操作です。各コマンドには追加のスイッチがあるため、詳細と他の例はhelpやmanページを確認します。

<a id="quarterly-latest-branch"></a>
### QuarterlyとLatestを選ぶ

**Quarterly**は四半期ごとにHEADから分岐し、通常は新機能を増やさず、セキュリティ修正・バグ修正・Ports基盤への対応を取り込みます。セキュリティ修正にはバージョン更新やバックポートを含むことがあります。予測しやすい更新を重視するブランチです。

分岐は1・4・7・10月の初めで、`2023Q1` のように年と四半期で名付けます。**Latest**は新しい版を継続して提供します。

pkgのQuarterlyからLatestへ切り替える原文例です。

```shell
# mkdir -p /usr/local/etc/pkg/repos
# echo 'FreeBSD-ports: { url: "pkg+https://pkg.FreeBSD.org/${ABI}/latest" }' > /usr/local/etc/pkg/repos/FreeBSD.conf
```

その後、カタログを取得し直します。

```shell
# pkg update -f
```

> **訳注:** この例のリポジトリ識別子は `FreeBSD-ports` です。後述の古い設定例では `FreeBSD` という識別子も出てきます。設定を上書き・無効化する際は、実際のリポジトリ名に合わせます。

<a id="kmod-repository"></a>
### カーネルモジュール用リポジトリ

グラフィックスドライバーなどのカーネルモジュールにも、ビルド済みのリポジトリがあります。FreeBSD 14.3以降、プロジェクトは対応する各バージョン向けのモジュールを提供しています。設定がない場合は `/usr/local/etc/pkg/repos/kmods.conf` に次を記述します。

```text
FreeBSD-kmods: {
        url: "pkg+https://pkg.FreeBSD.org/${ABI}/KMODSFLAVOR",
        mirror_type: "srv",
        signature_type: "fingerprints",
        fingerprints: "/usr/share/keys/pkg",
        enabled: yes
}
```

`KMODSFLAVOR` は `kmods_PORTBRANCH_MINORRELEASE` 形式の値へ置き換えます。原文の対応表は次のとおりです。

| FreeBSDの版 | ports main | ports quarterly |
|---|---|---|
| 14.2-RELEASE | `kmods_latest_2` | `kmods_quarterly_2` |
| 14.3-RELEASE | `kmods_latest_3` | `kmods_quarterly_3` |
| 14.3-STABLE | `kmods_latest` | `kmods_quarterly` |
| 15.0-CURRENT | `kmods_latest` | — |

> **訳注:** 表は原文の例です。`KMODSFLAVOR` をそのまま残したり、別リリースの行をそのまま適用したりせず、対象カーネルとPortsブランチに合う値を選びます。

<a id="pkg-configuration"></a>
### pkgの設定ファイル

システム全体の設定は通常 `/usr/local/etc/pkg.conf` に置きます。ただし必須ではなく、ファイルがない状態やコメントだけの空の設定で動く環境も多くあります。

`#` から始まる行はコメントです。書式はUCLで、真偽値・文字列・リスト型のオプションを扱います。真偽値を有効にする値は `YES`、`TRUE`、`ON` などです。詳しくは `pkg.conf(5)` と [UCLの公式リポジトリ](https://github.com/vstakhov/libucl)を参照してください。

<a id="pkg-search"></a>
### パッケージを検索する

`pkg-search(8)` で名前などを検索します。NGINXの例です。

```shell
# pkg search nginx
```

出力例です。各種NGINXパッケージに加え、関連モジュールなども見つかります。版番号は原文の表示例です。

```text
modsecurity3-nginx-1.0.3       Instruction detection and prevention engine / nginx Wrapper
nginx-1.22.1_2,3               Robust and small WWW server
nginx-devel-1.23.2_4           Robust and small WWW server
nginx-full-1.22.1_1,3          Robust and small WWW server (full package)
nginx-lite-1.22.1,3            Robust and small WWW server (lite package)
nginx-naxsi-1.22.1,3           Robust and small WWW server (plus NAXSI)
nginx-prometheus-exporter-0.10.0_7 Prometheus exporter for NGINX and NGINX Plus stats
nginx-ultimate-bad-bot-blocker-4.2020.03.2005_1 Nginx bad bot and other things blocker
nginx-vts-exporter-0.10.7_7    Server that scraps NGINX vts stats and export them via HTTP
p5-Nginx-ReadBody-0.07_1       Nginx embeded perl module to read and evaluate a request body
p5-Nginx-Simple-0.07_1         Perl 5 module for easy to use interface for Nginx Perl Module
p5-Test-Nginx-0.30             Testing modules for Nginx C module development
py39-certbot-nginx-2.0.0       NGINX plugin for Certbot
rubygem-passenger-nginx-6.0.15 Modules for running Ruby on Rails and Rack applications
```

<a id="pkg-installing-fetching"></a>
### パッケージの導入と事前取得

`pkg-install(8)` はリポジトリの情報を使い、導入する版と不足する依存先を判断します。curlを入れる例です。

```shell
# pkg install curl
```

追加されるパッケージ、必要な容量、転送量が表示されます。内容を確認して進めます。

```text
Updating FreeBSD repository catalogue...
FreeBSD repository is up to date.
All repositories are up to date.
The following 9 package(s) will be affected (of 0 checked):

New packages to be INSTALLED:
        ca_root_nss: 3.83
        curl: 7.86.0
        gettext-runtime: 0.21
        indexinfo: 0.3.1
        libidn2: 2.3.3
        libnghttp2: 1.48.0
        libpsl: 0.21.1_4
        libssh2: 1.10.0.3
        libunistring: 1.0

Number of packages to be installed: 9

The process will require 11 MiB more space.
3 MiB to be downloaded

Proceed with this action? [y/N]
```

導入したものと依存先は一覧で確認できます。

```shell
# pkg info
```

出力例です。

```text
ca_root_nss-3.83               Root certificate bundle from the Mozilla Project
curl-7.86.0                    Command line tool and library for transferring data with URLs
gettext-runtime-0.21.1         GNU gettext runtime libraries and programs
indexinfo-0.3.1                Utility to regenerate the GNU info page index
libidn2-2.3.3                  Implementation of IDNA2008 internationalized domain names
libnghttp2-1.48.0              HTTP/2.0 C Library
libpsl-0.21.1_6                C library to handle the Public Suffix List
libssh2-1.10.0.3               Library implementing the SSH2 protocol
libunistring-1.0               Unicode string library
pkg-1.18.4                     Package manager
```

後から、または別の場所で導入するために取得だけを行うには `pkg-fetch(8)` を使います。

```shell
# pkg fetch -d -o /usr/home/user/packages/ nginx-lite
```

`-d` は依存先も取得し、`-o` は保存先を指定します。

```text
Updating FreeBSD repository catalogue...
FreeBSD repository is up to date.
All repositories are up to date.
The following packages will be fetched:

New packages to be FETCHED:
        nginx-lite: 1.22.1,3 (342 KiB: 22.20% of the 2 MiB to download)
        pcre: 8.45_3 (1 MiB: 77.80% of the 2 MiB to download)

Number of packages to be fetched: 2

The process will require 2 MiB more space.
2 MiB to be downloaded.

Proceed with fetching packages? [y/N]:
```

取得先へ移動し、ダウンロードしたファイルを指定して導入します。

```shell
# cd /usr/home/user/packages/
```

```shell
# pkg install nginx-lite-1.22.1,3.pkg
```

ファイル名の版番号は、実際に取得したものへ置き換えてください。

<a id="pkgng-pkg-info"></a>
### 導入済みパッケージの情報を見る

`pkg-info(8)` は、全パッケージまたは指定したパッケージの版などを表示します。pkg本体を調べる例です。

```shell
# pkg info pkg
```

出力例には名前、版、導入日時、Ports内のorigin、アーキテクチャ、導入先、ライセンス、保守担当、ビルドオプション、共有ライブラリ、容量などが含まれます。

```text
pkg-1.19.0
Name           : pkg
Version        : 1.19.0
Installed on   : Sat Dec 17 11:05:28 2022 CET
Origin         : ports-mgmt/pkg
Architecture   : FreeBSD:13:amd64
Prefix         : /usr/local
Categories     : ports-mgmt
Licenses       : BSD2CLAUSE
Maintainer     : pkg@FreeBSD.org
WWW            : https://github.com/freebsd/pkg
Comment        : Package manager
Options        :
        DOCS           : on
Shared Libs provided:
        libpkg.so.4
Annotations    :
        FreeBSD_version: 1301000
        repo_type      : binary
        repository     : FreeBSD
Flat size      : 33.2MiB
Description    :
Package management tool

WWW: https://github.com/freebsd/pkg
```

<a id="pkgng-upgrading"></a>
### 導入済みパッケージを更新する

`pkg-upgrade(8)` で、導入済みの版とリポジトリのカタログを比較し、新しい版へ更新します。

```shell
# pkg upgrade
```

<a id="pkgng-auditing"></a>
### 既知の脆弱性を検査する

サードパーティーのソフトウェアでは継続的に脆弱性が見つかります。pkgの監査機能で、導入済みのソフトウェアを既知の情報に照合できます。

```shell
# pkg audit -F
```

脆弱性が見つかった場合の原文例です。CVE番号と詳しい情報へのリンクが表示されます。

```text
Fetching vuln.xml.xz: 100%  976 KiB 499.5kB/s    00:02
chromium-108.0.5359.98 is vulnerable:
  chromium -- multiple vulnerabilities
  CVE: CVE-2022-4440
  CVE: CVE-2022-4439
  CVE: CVE-2022-4438
  CVE: CVE-2022-4437
  CVE: CVE-2022-4436
  WWW: https://vuxml.FreeBSD.org/freebsd/83eb9374-7b97-11ed-be8f-3065ec8fd3ec.html
```

<a id="pkg-delete"></a>
### 不要なパッケージを削除する

`pkg-delete(8)` で不要なパッケージを削除します。curlの例です。

```shell
# pkg delete curl
```

削除対象と解放される容量を確認して進めます。

```text
Checking integrity... done (0 conflicting)
Deinstallation has been requested for the following 1 packages (of 0 packages in the universe):

Installed packages to be REMOVED:
        curl :7.86.0

Number of packages to be removed: 1

The operation will free 4 MiB.

Proceed with deinstallation packages? [y/N]: y
[1/1] Deinstalling curl-7.86.0...
[1/1] Deleting files for curl-7.86.0: 100%
```

<a id="pkgng-autoremove"></a>
### 使われなくなった依存パッケージを整理する

ソフトウェアを削除しても、不要になった依存パッケージが残ることがあります。依存先として自動導入され、現在は必要とされていないものを `pkg-autoremove(8)` で検出・削除できます。

```shell
# pkg autoremove
```

候補を確認してから削除します。

```text
Checking integrity... done (0 conflicting)
Deinstallation has been requested for the following 1 packages:

Installed packages to be REMOVED:
        ca_root_nss-3.83

Number of packages to be removed: 1

The operation will free 723 KiB.

Proceed with deinstalling packages? [y/N]:
```

依存先として入ったものは **automatic** パッケージです。それ以外、つまり利用者が明示的に導入したものは次で一覧できます。

```shell
# pkg prime-list
```

出力例です。

```text
nginx
openvpn
sudo
```

`prime-list` はpkg.confに定義されるエイリアスの1つです。ほかにもデータベースを問い合わせるエイリアスがあり、`prime-origins` は同じ一覧をPortsのorigin形式で表示します。

```shell
# pkg prime-origins
```

```text
www/nginx
security/openvpn
security/sudo
```

このorigin一覧は `ports-mgmt/poudriere` や `ports-mgmt/synth` でシステムのパッケージを再ビルドする際に使えます。

既存パッケージをautomaticへ変更する例です。

```shell
# pkg set -A 1 devel/cmake
```

automaticで、どのパッケージからも必要とされなくなればautoremoveの候補になります。明示的に残す非automaticへ変更するには次を使います。

```shell
# pkg set -A 0 devel/cmake
```

<a id="pkgng-clean"></a>
### 取得済みパッケージのキャッシュを掃除する

pkgは `pkg.conf(5)` の `PKG_CACHEDIR` が指す場所へ取得したバイナリを保存します。原文は、新しいpkgでは最新の導入済みパッケージを残し、古い版のpkgでは過去のものも蓄積したと説明しています。古くなったキャッシュを整理するには次を実行します。

```shell
# pkg clean
```

全キャッシュを消す場合は `-a` を使います。

```shell
# pkg clean -a
```

<a id="pkg-locking-unlocking"></a>
### パッケージをロック・解除する

`pkg-lock(8)` は再導入・変更・削除を防ぐロックをかけ、`pkg-unlock(8)` は解除します。対象は **既に導入されたパッケージ** です。新しいパッケージの導入自体を禁じる仕組みではありませんが、その導入がロック中のパッケージの更新を必要とする場合は影響します。

nginx-liteをロックします。

```shell
# pkg lock nginx-lite
```

解除します。

```shell
# pkg unlock nginx-lite
```

<a id="pkgng-set"></a>
### パッケージのメタデータを変更する

Ports内の名前や主要バージョンが変わった場合、pkgはoriginの変更を扱えます。原文では `lang/python3` を `lang/python311` へ変更してPython 3.11を指すようにする例を示しています。

```shell
# pkg set -o lang/python3:lang/python311
```

Ruby 3.1から3.2へのorigin変更例です。

```shell
# pkg set -o lang/ruby31:lang/ruby32
```

> **注意:** originを変更したら、そのパッケージへ依存するパッケージも再導入する必要があります。強制再導入の原文例は次のとおりです。

```shell
# pkg install -Rf lang/ruby32
```

これらの版と名前は説明用の例です。実際の変更は、対象Portsの更新案内と一致させます。

<a id="ports-using"></a>
## Ports Collectionを使う

Ports Collectionは `Makefile`、パッチ、説明などの集合です。個々のアプリケーションに対応するファイル一式をportと呼び、通常は `/usr/ports` に置きます。カテゴリの下に各アプリケーションのディレクトリがあり、ビルド・導入の手順を記述した **ports skeleton** が入っています。

> **注意:** 公式バイナリとPortsからの導入を無計画に混在させることは勧められません。pkgの既定はQuarterlyで、HEADのPortsとは依存関係が異なり、衝突する場合があります。併用するなら、両方のPortsブランチを揃えます。

| ファイル／ディレクトリ | 役割 |
|---|---|
| `Makefile` | ビルド方法と導入先を指定します。 |
| `distinfo` | 取得するファイル名とチェックサム。 |
| `files/` | FreeBSD上で動かすためのパッチやビルド補助ファイル。 |
| `pkg-descr` | ソフトウェアの詳しい説明。 |
| `pkg-plist` | 導入ファイルの一覧と、削除時に取り除くファイル。 |

portによっては `pkg-message` などの追加ファイルもあります。詳しくは [Porter's Handbook](https://docs.freebsd.org/en/books/porters-handbook/)を参照してください。

port自体にソースコード（distfile）は入りません。ビルドの取得・展開処理でダウンロードされ、通常 `/usr/ports/distfiles` に保存されます。

<a id="ports-using-installation-methods"></a>
### Ports Collectionを取得・更新する

<a id="ports-using-git-method"></a>

ソースからビルドする前にPortsツリーを用意します。OSの導入時に入れなかった場合もGitで取得できます。ローカル変更の管理やFreeBSD-CURRENTの利用にもGitが適しています。詳しい操作は [Git Primer](https://docs.freebsd.org/en/articles/committers-guide/#git-primer)を参照してください。

例の `--depth 1` は履歴を取得しない浅いcloneで、通常の利用では転送量と時間を節約できます。独自変更を保守したり履歴を使ったりする場合は省略します。

1. Gitを用意します。既にPortsがあるなら次のようにビルドできます。

```shell
# cd /usr/ports/devel/git
# make install clean
```

Portsがまだない場合やpkg運用なら、パッケージで入れます。

```shell
# pkg install git
```

2. HEADのPortsを取得する例です。

```shell
# git clone --depth 1 https://git.FreeBSD.org/ports.git /usr/ports
```

Quarterlyを取得する場合の原文例です。

```shell
# git clone --depth 1 https://git.FreeBSD.org/ports.git -b 2023Q1 /usr/ports
```

3. 取得後は必要に応じて更新します。

```shell
# git -C /usr/ports pull
```

4. 別のQuarterlyブランチへ切り替える原文例です。

```shell
# git -C /usr/ports fetch --depth 1 origin 2023Q2:2023Q2
# git -C /usr/ports switch 2023Q2
```

`2023Q1`・`2023Q2` は原文の例です。現在利用するブランチへ置き換え、pkgと併用するときはそちらとも揃えます。

<a id="chapter-04-heading-22"></a>
### Portsからビルド・導入する

Portsの各ターゲットや環境変数の詳細は `ports(7)` にあります。ここでは基本の導入・削除を扱います。

> **注意:** ビルド前にPorts Collectionを更新し、[VuXML](https://vuxml.freebsd.org/)で対象の既知の脆弱性を確認します。`pkg audit -F` も利用できます。毎日のセキュリティ検査で脆弱性データベースの更新・監査を行う設定は `pkg-audit(8)` と `periodic(8)` を参照してください。

通常は動作するインターネット接続とroot権限が必要です。対象portのディレクトリへ移動して `make install` を実行します。次はlsofの取得・展開・パッチ・ビルド・導入が進む原文例です。

```shell
# cd /usr/ports/sysutils/lsof
# make install
>> lsof_4.88D.freebsd.tar.gz doesn't seem to exist in /usr/ports/distfiles/.
>> Attempting to fetch from ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/.
===>  Extracting for lsof-4.88
...
[extraction output snipped]
...
>> Checksum OK for lsof_4.88D.freebsd.tar.gz.
===>  Patching for lsof-4.88.d,8
===>  Applying FreeBSD patches for lsof-4.88.d,8
===>  Configuring for lsof-4.88.d,8
...
[configure output snipped]
...
===>  Building for lsof-4.88.d,8
...
[compilation output snipped]
...

===>  Installing for lsof-4.88.d,8
...
[installation output snipped]
...
===>   Generating temporary packing list
===>   Compressing manual pages for lsof-4.88.d,8
===>   Registering installation for lsof-4.88.d,8
===>  SECURITY NOTE:
      This port has installed the following binaries which execute with
      increased privileges.
/usr/local/sbin/lsof
#
```

lsofは高い権限で実行されるプログラムなので、その旨の警告が表示されます。終了するとプロンプトへ戻ります。

シェルがPATH内のコマンドをキャッシュしている場合は更新します。tcshでは `rehash`、shでは `hash -r` を使うと、新しいコマンドを絶対パスなしで呼び出せます。詳細はシェルの文書を確認してください。

ビルドで作られた作業ディレクトリを消すと、容量を節約でき、次回更新時に残骸が問題になる可能性も減ります。

```shell
# make clean
===>  Cleaning for lsof-88.d,8
#
```

最初から `make install clean` とすれば、導入後の掃除までまとめて行えます。

<a id="chapter-04-heading-23"></a>
#### Portsのビルド設定を変える

FirefoxやGPGMEなどのportには、機能・セキュリティなどのビルドオプションがあります。依存先にも選択肢があると、ビルドの途中で何度も確認画面が出ます。先に `make config-recursive` でまとめて設定し、その後 `make install`、または掃除もする `make install clean` を実行できます。

`config-recursive` は `all-depends-list` で依存先を列挙します。選択内容で依存関係が変わるため、選択画面が出なくなるまで繰り返し、必要な依存先すべての設定を終えておくことを勧めています。

後から設定を確認・変更するには対象portで次を使います。

- `make config`: 選択画面を開きます。
- `make showconfig`: 設定を表示します。
- `make rmconfig`: 保存した選択を削除し、やり直せるようにします。

詳しくは `ports(7)` を参照してください。

ソース取得には `fetch(1)` を使います。ファイアウォールやFTP／HTTPプロキシの背後では、`FTP_PASSIVE_MODE`、`FTP_PROXY`、`FTP_PASSWORD` などを設定する場合があります。対応変数の一覧は `fetch(3)` にあります。

常時接続できない環境では、接続できる間に `make fetch` でdistfileを取得できます。`/usr/ports` 全体、`/usr/ports/net` などのカテゴリ、個別portのいずれでも実行できます。ただしカテゴリや個別portで実行した場合、別カテゴリの依存先までは取得しません。依存先も必要なら `make fetch-recursive` を使います。

組織内のdistfileサーバーなど、取得元を上書きする場合の原文例です。本文は `MASTER_SITES` に言及し、コマンド例は `MASTER_SITE_OVERRIDE` を使っています。

```shell
# cd /usr/ports/directory
# make MASTER_SITE_OVERRIDE= \
ftp://ftp.organization.org/pub/FreeBSD/ports/distfiles/ fetch
```

`WRKDIRPREFIX` は作業先、`PREFIX` は導入先を変更します。次は `/usr/home/example/ports` でビルドし、通常の `/usr/local` へ導入します。

```shell
# make WRKDIRPREFIX=/usr/home/example/ports install
```

次はPortsツリー側でビルドし、`/usr/home/example/local` へ導入します。

```shell
# make PREFIX=/usr/home/example/local install
```

両方を組み合わせる例です。

```shell
# make WRKDIRPREFIX=../ports PREFIX=../local install
```

これらは環境変数として設定することもできます。設定方法は使っているシェルのマニュアルを参照してください。

<a id="ports-removing"></a>
### Portsから入れたものを削除する

Portsで入れたソフトウェアも `pkg delete` で削除できます。使い方は `pkg-delete(8)` を参照してください。対象portのディレクトリで `make deinstall` を使う方法もあります。

```shell
# cd /usr/ports/sysutils/lsof
# make deinstall
===>  Deinstalling for sysutils/lsof
===>   Deinstalling
Deinstallation has been requested for the following 1 packages:

	lsof-4.88.d,8

The deinstallation will free 229 kB
[1/1] Deleting lsof-4.88.d,8... done
```

削除中のメッセージは確認してください。他のアプリケーションが依存している場合は情報が表示されても削除が進みます。その場合は依存関係を壊したままにせず、必要なソフトウェアの再導入を検討します。

<a id="ports-upgrading"></a>
### Portsを更新する

新しいソフトウェアはPorts Collectionへ取り込まれます。まず[Gitの手順](#ports-using-git-method)でツリーを更新し、次で古くなった導入済みportを一覧にします。

```shell
# pkg version -l "<"
```

> **重要:** 更新前に `/usr/ports/UPDATING` を先頭から読み、前回の更新日または導入日まで遡って、対象portの案内を確認します。ファイル形式、設定場所、旧版との互換性など、追加手順が必要になる変更が書かれています。該当する指示を記録し、更新時に従ってください。

<a id="ports-upgrading-tools"></a>
#### 更新・管理ツールを選ぶ

実際の更新を行うツールはいくつかあり、それぞれ得意・不得意があります。従来はPortmasterとPortupgradeがよく使われ、Synthはより新しい選択肢として紹介されています。どれを使うかは管理者が判断し、実行前にデータをバックアップします。

<a id="portmaster"></a>
#### Portmasterで更新する

`ports-mgmt/portmaster` は小さな更新ツールです。他のportや独自データベースへ依存せず、ベースシステムのツールを使うように設計されています。

```shell
# cd /usr/ports/ports-mgmt/portmaster
# make install clean
```

Portmasterはportを次の4種類に分けます。

| 種類 | 関係 |
|---|---|
| Root | 依存先がなく、他からも依存されません。 |
| Trunk | 依存先はありませんが、他から依存されます。 |
| Branch | 依存先があり、他からも依存されます。 |
| Leaf | 依存先はありますが、他からは依存されません。 |

分類と更新候補を表示します。

```shell
# portmaster -L
===>>> Root ports (No dependencies, not depended on)
===>>> ispell-3.2.06_18
===>>> screen-4.0.3
        ===>>> New version available: screen-4.0.3_1
===>>> tcpflow-0.21_1
===>>> 7 root ports
...
===>>> Branch ports (Have dependencies, are depended on)
===>>> apache22-2.2.3
        ===>>> New version available: apache22-2.2.8
...
===>>> Leaf ports (Have dependencies, not depended on)
===>>> automake-1.9.6_2
===>>> bash-3.1.17
        ===>>> New version available: bash-3.2.33
...
===>>> 32 leaf ports

===>>> 137 total installed ports
        ===>>> 83 have new versions available
```

古いものをすべて更新します。

```shell
# portmaster -a
```

既定では既存portを消す前にバックアップパッケージを作り、新版の導入に成功すると消します。`-b` ならバックアップを残し、`-i` なら個別の更新前に確認します。ほかのオプションは `portmaster(8)` を参照してください。

更新中に問題があった場合、原文は `-f` を加えた全体の再ビルドを紹介しています。

```shell
# portmaster -af
```

新しいportを指定すると、その導入前に依存先を更新できます。

```shell
# portmaster shells/bash
```

詳しい説明はportの `pkg-descr` にもあります。

<a id="portupgrade"></a>
#### Portupgradeで更新する

> **原文の警告:** Portupgradeは非推奨で、将来削除される予定です。以下は原文の手順を残したものです。

`ports-mgmt/portupgrade` はPorts管理用のツール一式を導入し、Rubyへ依存します。

```shell
# cd /usr/ports/ports-mgmt/portupgrade
# make install clean
```

更新前に `pkgdb -F` で導入済みportを検査し、報告された不整合を直すことを勧めています。

全更新は `portupgrade -a`、毎回確認するなら `-i` も付けます。

```shell
# portupgrade -ai
```

単体の更新は `portupgrade パッケージ名` です。先に必要な依存先を更新するため、`-R` を付けることが重要です。

```shell
# portupgrade -R firefox
```

`-P` は `PKG_PATH` にあるローカルパッケージを探し、なければ遠隔から取得し、それもなければPortsからビルドします。`-PP` はパッケージがなければ中止し、Portsを使いません。

```shell
# portupgrade -PP gnome3
```

`-F` は取得だけを行い、ビルド・導入はしません。`-P` と組み合わせればパッケージ、そうでなければdistfileの取得です。詳細はportupgradeのマニュアルと `pkg-descr` を参照してください。

<a id="ports-disk-space"></a>
### ビルドで使ったディスク容量を整理する

Portsを使い続けると作業ファイルやdistfileが溜まります。個別portでは `make clean` で `work` を消せます。Portmasterは `-K` を指定しなければ自動的に消します。

Portupgradeがある場合、Portsツリー全体の `work` を消すには次を使います。

```shell
# portsclean -C
```

`/usr/ports/distfiles` のうち、どのportからも参照されないファイルを削除します。

```shell
# portsclean -D
```

現在導入しているportが参照しないdistfileまで削除する場合は次です。

```shell
# portsclean -DD
```

Portmasterでは次を使います。

```shell
# portmaster --clean-distfiles
```

既定では削除ごとに確認します。さらに `ports-mgmt/pkg_cutleaves` は、不要になった導入済みportを取り除く作業を自動化します。

<a id="ports-poudriere"></a>
## poudriereでパッケージを作る

poudriereはBSDライセンスのパッケージ作成・試験ツールです。FreeBSD jailでビルド環境を分離し、ホストと異なるFreeBSDの版向けや、amd64ホストでi386向けのパッケージも作れます。完成したものは公式ミラーと同じ形式で配置され、pkgなどから利用できます。

`ports-mgmt/poudriere` をパッケージまたはportで導入し、`/usr/local/etc/poudriere.conf.sample` を `/usr/local/etc/poudriere.conf` へコピーして環境に合わせます。

ZFSは必須ではありませんが便利です。使う場合は `ZPOOL` を指定し、`FREEBSD_HOST` は近いミラーへ設定します。`CCACHE_DIR` を定義すると `devel/ccache` でコンパイル結果を再利用でき、繰り返しビルドを短縮できます。poudriereのデータセットを `/poudriere` の独立したツリーにまとめる方法もあります。その他の設定は通常既定値で足ります。

並列ビルド数は検出したCPUコア数から決まります。RAMとswapを十分に用意してください。仮想メモリが不足するとビルド用jailが停止・撤去され、原因が分かりにくいエラーが出る場合があります。

<a id="poudriere-initialization"></a>
### ビルド用jailとPortsツリーを初期化する

設定後、対象FreeBSDのユーザーランドを持つjailとPortsツリーを用意します。`-j` はjail名、`-v` はFreeBSDの版です。amd64ホストでは `-a` で `i386`／`amd64` を選べ、省略時はunameが示すアーキテクチャです。

次は原文の13.1-RELEASEの例です。現在ビルドする対象リリースに置き換えます。

```shell
# poudriere jail -c -j 13amd64 -v 13.1-RELEASE
[00:00:00] Creating 13amd64 fs at /poudriere/jails/13amd64... done
[00:00:00] Using pre-distributed MANIFEST for FreeBSD 13.1-RELEASE amd64
[00:00:00] Fetching base for FreeBSD 13.1-RELEASE amd64
/poudriere/jails/13amd64/fromftp/base.txz              125 MB 4110 kBps    31s
[00:00:33] Extracting base... done
[00:00:54] Fetching src for FreeBSD 13.1-RELEASE amd64
/poudriere/jails/13amd64/fromftp/src.txz               154 MB 4178 kBps    38s
[00:01:33] Extracting src... done
[00:02:31] Fetching lib32 for FreeBSD 13.1-RELEASE amd64
/poudriere/jails/13amd64/fromftp/lib32.txz              24 MB 3969 kBps    06s
[00:02:38] Extracting lib32... done
[00:02:42] Cleaning up... done
[00:02:42] Recording filesystem state for clean... done
[00:02:42] Upgrading using ftp
/etc/resolv.conf -> /poudriere/jails/13amd64/etc/resolv.conf
Looking up update.FreeBSD.org mirrors... 3 mirrors found.
Fetching public key from update4.freebsd.org... done.
Fetching metadata signature for 13.1-RELEASE from update4.freebsd.org... done.
Fetching metadata index... done.
Fetching 2 metadata files... done.
Inspecting system... done.
Preparing to download files... done.
Fetching 124 patches.....10....20....30....40....50....60....70....80....90....100....110....120.. done.
Applying patches... done.
Fetching 6 files... done.
The following files will be added as part of updating to
13.1-RELEASE-p1:
/usr/src/contrib/unbound/.github
/usr/src/contrib/unbound/.github/FUNDING.yml
/usr/src/contrib/unbound/contrib/drop2rpz
/usr/src/contrib/unbound/contrib/unbound_portable.service.in
/usr/src/contrib/unbound/services/rpz.c
/usr/src/contrib/unbound/services/rpz.h
/usr/src/lib/libc/tests/gen/spawnp_enoexec.sh
The following files will be updated as part of updating to
13.1-RELEASE-p1:
[…]
Installing updates...Scanning //usr/share/certs/blacklisted for certificates...
Scanning //usr/share/certs/trusted for certificates...
 done.
13.1-RELEASE-p1
[00:04:06] Recording filesystem state for clean... done
[00:04:07] Jail 13amd64 13.1-RELEASE-p1 amd64 is ready to be used
```

Portsツリーを作ります。

```shell
# poudriere ports -c -p local -m git+https
[00:00:00] Creating local fs at /poudriere/ports/local... done
[00:00:00] Checking out the ports tree... done
```

1台で、複数jail・Portsツリー・設定の組み合わせを扱えます。この設定の組み合わせを **set** と呼びます。詳細はpoudriereまたはpoudriere-devel導入後の `poudriere(8)` のCUSTOMIZATIONを参照してください。

ここでは `/usr/local/etc/poudriere.d` に、jail名・Portsツリー名・set名を組み合わせた `13amd64-local-workstation-make.conf` を置きます。ビルド時にシステムのmake.confと組み合わせ、jail内の設定を作ります。

作るパッケージは `13amd64-local-workstation-pkglist` に記述します。Portsの[FLAVORS](https://docs.freebsd.org/en/books/porters-handbook/flavors/)は `@FLAVOR` で指定できます。

```text
editors/emacs
devel/git
devel/php-composer2@php82
ports-mgmt/pkg
...
```

選択したportと依存先のオプションを設定します。

```shell
# poudriere options -j 13amd64 -p local -z workstation -f 13amd64-local-workstation-pkglist
```

最後にビルドし、パッケージリポジトリを作成します。

```shell
# poudriere bulk -j 13amd64 -p local -z workstation -f 13amd64-local-workstation-pkglist
```

実行中の `Ctrl+t` は進行状況を表示します。`/poudriere/logs/bulk/jailname` のログはWebサーバー経由で見ることもできます。完了後は作ったリポジトリから導入できます。詳細は `poudriere(8)` と [公式Wiki](https://github.com/freebsd/poudriere/wiki)を参照してください。

<a id="chapter-04-heading-32"></a>
### クライアントから独自リポジトリを使う

公式と独自のリポジトリを併用できますが、公式を無効にする場合もあります。原文は `/usr/local/etc/pkg/repos/FreeBSD.conf` で公式の設定を上書きする例を示しています。

```text
FreeBSD: {
	enabled: no
}
```

> **訳注:** `FreeBSD` はこの例のリポジトリ識別子です。前の節の `FreeBSD-ports` など、実際に利用している識別子と合わせないと目的のリポジトリを無効化できません。

一般に、パッケージのディレクトリをHTTPで公開するとクライアントへ配布しやすくなります。原文の公開元の例は `/usr/local/poudriere/data/packages/13amd64` で、`13amd64` はビルド名です。

公開URLが `https://pkg.example.com/13amd64` なら、クライアントの `/usr/local/etc/pkg/repos/custom.conf` は次のようになります。

```text
custom: {
	url: "https://pkg.example.com/13amd64",
	enabled: yes,
}
```

インターネットへ公開しない場合は、ローカルのリポジトリを `file://` で指す方法もあります。

```text
custom: {
	url: "file:///usr/local/poudriere/data/packages/11amd64",
	enabled: yes,
}
```

最後の原文例は `11amd64` という別のビルド名を使っています。パスは実際の配置・ビルド名に合わせてください。

<a id="ports-nextsteps"></a>
## 導入後に行うこと

Packages・Portsのどちらで入れても、多くのアプリケーションには追加設定が必要です。次を確認します。

- **設定ファイル:** 通常は `/usr/local/etc`、数が多ければその下の専用ディレクトリにあります。`.sample` などのサンプルは、その拡張子を除いた名前へコピーしてから用途に合わせて編集します。
- **文書:** `/usr/local/share/doc` とmanページを読み、設定を始める前に必要な手順を確認します。
- **サービス:** 起動スクリプトは通常 `/usr/local/etc/rc.d` にあります。`/etc/rc.conf` で有効化してから起動します。[サービスの起動](https://docs.freebsd.org/en/books/handbook/config/#configtuning-starting-services)も参照してください。
- **シェルのキャッシュ:** csh系なら `rehash` でPATH内のコマンド一覧を更新します。
- **導入ファイルの調査:** `pkg info` で、設定・文書・実行ファイルとして何が入ったか調べます。

> **注:** アプリケーションは、導入時に自動でサービスを開始したり、削除・更新時に停止スクリプトを動かしたりしない設計です。開始・停止の判断は管理者が行います。

<a id="ports-broken"></a>
## ビルド・導入できないportに対処する

失敗した場合は、次の順で調べます。

1. [FreeBSDの問題報告](https://www.freebsd.org/support/)を検索し、対象portの修正が既に提案されていないか確認します。適用できる修正なら解決する場合があります。
2. 保守担当に相談します。対象portで `make maintainer` を実行するかMakefileを読み、連絡先を調べます。相談にはエラー直前からの出力も添えます。
3. 返事がなければ、[問題報告の書き方](https://docs.freebsd.org/en/articles/problem-reports/)に従ってBugzillaへ報告します。
4. 自分で直す場合は [Porter's Handbook](https://docs.freebsd.org/en/books/porters-handbook/)のPorts基盤の説明を利用できます。ビルドを避けられる場合は、[pkgによるバイナリ導入](#pkgng-intro)へ切り替える方法もあります。

保守担当が個人でなくメーリングリストの場合もあります。多くは `freebsd-listname@FreeBSD.org` のような名前ですが、例外もあります。特に `ports@FreeBSD.org` は特定の個人ではなく、コミュニティ全体で対応する窓口です。この違いを踏まえて連絡します。協力者も常に必要とされています。
