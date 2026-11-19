<a id="containers"></a>
# 第18章 OCI コンテナ（OCI Containers）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/containers/)の「Chapter 18. OCI Containers」（既存 TOC ID 17）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/containers/_index.adoc`）に基づいて日本語へ意訳したものです（現在ドラフト作業中）。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`$` は一般ユーザーのプロンプトを示します。また、コード例中の `{rel-latest}` と `{rel-latest-previous}` は原文のリリース属性をそのまま保持しており、固定コミットの `shared/releases.adoc` ではそれぞれ `15.1` と `15.0` に定義されています。実際にコマンドを利用する際は、対象とする FreeBSD のリリース番号へ置き換えてください。

<a id="containers-synopsis"></a>
## 概要

一般に `OCI` と呼ばれる [Open Container Initiative](https://opencontainers.org/) は、ベンダーや OS に依存しない形でコンテナを記述・配布・実行するための仕組みを提供しています。
OCI 仕様により、FreeBSD を含むさまざまなオペレーティングシステム上でこれらを利用できます。
基盤となる仮想化技術は引き続き FreeBSD jail であり機能セットも同じですが、OCI ツール群を使うことで、コンテナベースのワークロードを扱う・構築するための新たな手法が利用できるようになります。
[14.3-RELEASE](https://www.freebsd.org/releases/14.3R/announce/) 以降（[スナップショット](https://download.freebsd.org/snapshots/OCI-IMAGES/)を含む）では OCI 互換イメージが提供されており、FreeBSD 上の [Podman](https://podman.io/) ツールキットは amd64 と arm64 の両アーキテクチャでこれらのイメージを利用できます。

jail に慣れている FreeBSD ユーザー向けにおおまかな対応関係を示すと、次のようになります。

* FreeBSD の `base.txz` tarball はコンテナイメージの一例に相当します。
* `jail.conf` ファイルは、コンテナの望ましいプロパティを記述する点、すなわち `Containerfile` に相当します。
* ファイルシステムパスを指定してコンテナを実行する `jail ..` コマンドは、`podman` ツール群に相当します。

このコンテナスタックを取り入れることで、FreeBSD ユーザーは共通のツール群の恩恵を受けられるだけでなく、公開・非公開のコンテナレジストリやコンテナ向けツール・サービスの幅広いエコシステムも活用できます。
[aarch64](https://download.freebsd.org/releases/OCI-IMAGES/15.1-RELEASE/aarch64/Latest/) および [amd64](https://download.freebsd.org/releases/OCI-IMAGES/15.1-RELEASE/amd64/Latest/) のダウンロードディレクトリに、公式の OCI 形式イメージが置かれています。
命名規則は最初こそ少し紛らわしく感じるかもしれませんが、使い始めれば自然と理解できるはずです。

同じイメージは [Docker Hub](https://hub.docker.com/u/freebsd) や [GitHub Container Registry](https://github.com/orgs/freebsd/packages) といった一般的な公開コンテナレジストリでも入手できます。ただし、最も強固な信頼の連鎖（chain of trust）を確保したい場合は、[Official FreeBSD Releases](https://download.freebsd.org/releases) から直接イメージを取得し、ローカルシステムへインポートしてください。

各イメージは用途に応じて標準の FreeBSD `base.txz` リリース tarball の一部から構成されており、通常の FreeBSD `CHECKSUM.*` ファイルも併せて提供されるため、PGP 署名済みのリリースアナウンスと照合して検証できます。
これにより、FreeBSD リリースチームから直接検証可能な非常に強固な出所の連鎖（chain of provenance）が得られます。

```text
CHECKSUM.SHA256
CHECKSUM.SHA512
FreeBSD-{rel-latest}-RELEASE-amd64-container-image-static.txz
FreeBSD-{rel-latest}-RELEASE-amd64-container-image-dynamic.txz
FreeBSD-{rel-latest}-RELEASE-amd64-container-image-runtime.txz
FreeBSD-{rel-latest}-RELEASE-amd64-container-image-notoolchain.txz
FreeBSD-{rel-latest}-RELEASE-amd64-container-image-toolchain.txz
```

<a id="containers-naming-tagging"></a>
## コンテナイメージの命名とタグ付け

> **訳注**: 原文ではこの見出しの直下に本文がなく、内容は以下の小節で説明されています。

<a id="chapter-18-heading-04"></a>
### はじめに

FreeBSD の公式コンテナイメージは、FreeBSD のリリースプロセス中にビルドされるベースシステムパッケージから構築され、公開レジストリへ公開されます。
このガイドでは、イメージの命名方法とタグ付け方法を説明し、目的に合ったイメージを選ぶ手助けをするとともに、新しいイメージが公開されたときや可変タグが更新されたときに各選択がどのような意味を持つのかを理解できるようにします。
この命名規則は新しいベースシステムパッケージの命名方式に沿っており、コンテナイメージと対応する FreeBSD リリースとの間に明確な出所関係をもたらします。

<a id="containers-image-types"></a>
### 利用可能なイメージ種別

FreeBSD のコンテナイメージは、`amd64` および `aarch64` アーキテクチャ向けに 5 種類が用意されています。

<a id="containers-freebsd-static"></a>
#### `freebsd-static`

static イメージは、完全に静的リンクされたワークロード向けのベースイメージを想定しています。ライブラリもバイナリも含まず、この種のアプリケーションの大半が必要とする補助ファイルのみを含みます。

* 公開 TLS 証明書
* 最小限のパスワードファイル
* 最小限の termcap
* タイムゾーンデータベース

設計上フットプリントを小さく抑えているため、万一コンテナが侵害されても攻撃者にとって利用価値が低くなります。
UNIX シェルもコマンドラインツールも動的ライブラリもパッケージマネージャもありません。
FreeBSD プロジェクトが提供する中で最小のイメージです。

<a id="containers-freebsd-dynamic"></a>
#### `freebsd-dynamic`

dynamic イメージは static イメージを親レイヤーとして利用し、`libc` を含む共有ライブラリの使用に対応します。
ほとんどの FreeBSD ソフトウェアは、わずかな変更だけでこのイメージ上で問題なく動作するはずです。
シェル、rc システム、パッケージマネージャは含まれません。
こうした制限は追加のセキュリティ対策として機能し、侵害されたコンテナ内の攻撃者が横展開（ラテラルムーブメント）を行ったり、未インストールのツールを悪用したりするのを困難にします。

<a id="containers-freebsd-runtime"></a>
#### `freebsd-runtime`

runtime イメージは前述の dynamic レイヤーを土台として構築され、ユーザーが通常期待する最小限の要素、すなわち UNIX シェル、rc システム、パッケージマネージャを追加します。
既存のアプリケーションを最小限の変更で移植するための理想的なベースイメージです。
ユーザーは、追加の FreeBSD ベースシステムライブラリや Ports ツリーからの追加パッケージを含める必要があります。
これは典型的な FreeBSD システムに最も近い構成であり、`pkg(8)` ツールも含まれているため、非コンテナ環境と同様にほぼ何でもインストール・実行できます。

<a id="containers-freebsd-notoolchain"></a>
#### `freebsd-notoolchain`

このベースイメージには、典型的な FreeBSD システムで期待されるツールのほとんどすべてが含まれます。ただし、ハードウェアに直接関係するためコンテナ内では一般に役に立たないものと、サイズが非常に大きいコンパイラおよび関連ツールチェーンは除外されています。

<a id="containers-freebsd-toolchain"></a>
#### `freebsd-toolchain`

toolchain ベースイメージは、前述のすべてのイメージを合わせたものに完全なコンパイラとツールチェーンを加えた構成です。
通常の jail 外の FreeBSD システムと同じ方法で、ほぼあらゆる FreeBSD 向けソフトウェアをコンパイルできます。
すべてのイメージは、基盤となる FreeBSD リリースに由来する一貫した命名パターンに従います。

<a id="containers-tag-structure"></a>
### イメージタグの構造

> **訳注**: 原文ではこの見出しの直下に本文がなく、内容は以下の小節で説明されています。

<a id="containers-immutable-tags"></a>
#### 不変タグ（Immutable Tags）

不変タグは決して変更されないため、安定性と予測可能性が求められる本番システムに最適です。
リリースプロセスで最もよく使われるタグであり、FreeBSD のセキュリティパッチやエラッタ通知が出た後も変更されません。
積極的なセキュリティパッチ適用とのトレードオフにはなりますが、高い再現性が期待されるソフトウェアデプロイ向けのベースイメージに適しています。

* `major.minor`（例: `14.4`）: 特定の FreeBSD RELEASE バージョンを指します
* `major.minor.pX`（例: `14.4p1`）: RELEASE の特定のパッチレベルを指します
* `major.snapYYYYMMDDHHMMSS`（例: `16.snap20260325035941`）: タイムスタンプ付きのスナップショットビルド

<a id="containers-mutable-tags"></a>
#### 可変タグ（Mutable Tags）

可変タグは時間とともに更新されるため、常に最新の更新を取り込みつつ FreeBSD の ABI 互換性を保ちたい本番環境や CI/CD システムに最適です。

* `major`（例: `15`）は、15.x 安定 ABI に沿った最新のサポート対象 RELEASE バージョンを常に指します
* `major.snap`（例: `15.snap`）は、15.x 安定 ABI トレインに沿った最新の開発者スナップショットに追従します。公式リリースより先行していることが多く、動作不良や非互換性、その他の予期しない問題が発生するリスクを伴います。
これは最も変化の大きいタグであり、慎重に使用する必要があります。
FreeBSD の STABLE または CURRENT スナップショットそのものをベースにしているため、それらを直接使うのとまったく同じです。

<a id="chapter-18-heading-14"></a>
### 各タグ種別の使い分け

> **訳注**: 原文ではこの見出しの直下に本文がなく、内容は以下の小節で説明されています。

<a id="chapter-18-heading-15"></a>
#### 本番環境向け

環境を一貫した状態に保つため、不変タグを使用します。

* `freebsd-runtime:15.0` - FreeBSD 15.0-RELEASE に固定

セキュリティパッチがリリースされたときは、新しいイメージタグを使って明示的に再ビルドまたは更新する必要があります。

<a id="chapter-18-heading-16"></a>
#### 継続的インテグレーションおよび開発向け

最新の更新を自動的に取得するため、可変タグを使用します。

* `freebsd-runtime:15` - 15.x 系列の最新公式 RELEASE を常に指す

次の追加の可変タグは、定期的に公開される FreeBSD STABLE および CURRENT のスナップショットに追従します。
将来の FreeBSD リリースに含まれる内容を先行テストしたい場合で、時折の動作不良や予期しない変更を許容できるときに使用してください。

* `freebsd-runtime:14.snap` - 14-STABLE ブランチの最新ビルドを常に指す
* `freebsd-runtime:15.snap` - 15-STABLE ブランチの最新ビルドを常に指す
* `freebsd-runtime:16.snap` - 16-CURRENT ブランチの最新ビルドを常に指す

<a id="containers-registries"></a>
## 公式レジストリの場所

アーキテクチャに依存しないイメージは、[Official FreeBSD Releases](https://download.freebsd.org/releases) サイトからダウンロードして自身のレジストリへ直接インポートすることも、FreeBSD プロジェクトの [Docker Hub](https://hub.docker.com/u/freebsd) または [GitHub Container Registry](https://github.com/orgs/freebsd/packages) からプルすることもできます。

[Alpine Linux](https://hub.docker.com/_/alpine/) および [Debian](https://hub.docker.com/_/debian/) プロジェクトも、同様の手法でタグ付きイメージと可変イメージを公開しています。

<a id="containers-podman-intro"></a>
## Podman の紹介

Podman スイートは 3 つの主要ツールといくつかの補助ツールから構成されています。

* [podman](https://podman.io/): Docker 互換コマンドを備えたデーモンレスのコンテナエンジン
* [buildah](https://buildah.io/): OCI 形式のコンテナイメージを生成するツール
* [skopeo](https://github.com/containers/skopeo): リモートの OCI イメージレジストリを操作するツール

<a id="containers-preparing"></a>
## Podman コンテナ向けシステムの準備

> **警告**: SSH などのリモートセッション経由でコマンドを実行している場合は、ファイアウォール再起動時に接続が切断されないよう、`screen(1)` や `tmux(1)` などのツールを使用してください。

ZFS を利用できない場合は UFS ストレージに切り替え、後続の ZFS コマンドはスキップしてください。

```shell
# sed -I .bak -e 's/driver = "zfs"/driver = "vfs"/' \
    /usr/local/etc/containers/storage.conf
```

ZFS を利用できる場合は、コンテナストレージ用のデータセットを作成します。

```shell
# zfs create -o mountpoint=/var/db/containers zroot/containers
# zfs snapshot zroot/containers@empty
```

ファイル記述子ファイルシステム（fdescfs）が必要です。

```shell
# mount -t fdescfs fdesc /dev/fd
```

再起動後も有効にするため、`/etc/fstab` に次の行を追加してください。

```shell
fdescfs  /dev/fd  fdescfs  rw  0  0
```

<a id="containers-installing"></a>
## Podman のインストール

必須なのはメタパッケージ `sysutils/podman-suite` のみですが、追加で `emulators/qemu-user-static` パッケージをインストールすると、`amd64` ホスト上で `arm64` など他アーキテクチャ向けイメージをビルド・テストできるようになります。

```shell
# pkg install -r FreeBSD -y podman-suite emulators/qemu-user-static
```

<a id="containers-networking"></a>
## ネットワークの設定

コンテナのネットワーキングでは、VNET jail がホストのネットワークへアクセスできるようにするため、ネットワークアドレス変換（NAT）を使用します。これは `pf(4)` によって行われるため、パケットフィルタのカーネルモジュールを読み込んでおく必要があります。

`/usr/local/etc/containers/pf.conf.sample` の設定を `/etc/pf.conf` に統合し、egress インターフェースのマクロをデフォルトネットワークインターフェースに合わせて設定します。

```text
# Change these to your interface(s) with the default route
v4egress_if = "vtnet0"
v6egress_if = "vtnet0"

nat on $v4egress_if inet from <cni-nat> to any -> ($v4egress_if)
nat on $v6egress_if inet6 from <cni-nat> to !ff00::/8 -> ($v6egress_if)

rdr-anchor "cni-rdr/*"
nat-anchor "cni-rdr/*"
table <cni-nat>
```

`rdr-anchor` と `nat-anchor "cni-rdr/*"` の各行は、`cni-rdr` 配下にネストされたアンカーとしてポートリダイレクトを実装します。特に `nat-anchor "cni-rdr/*"` の行は、宛先が `localhost`（`127.0.0.1` または `::1`）の場合も含め、コンテナホストからコンテナ内で動作するサービスへの接続をリダイレクトするために必要です。

ファイアウォールを有効化して起動します。

```shell
# service pf enable
# service pf start
```

コンテナホスト自身からコンテナ内で動作するサービスへの接続をリダイレクトするには、ローカルリダイレクトのサポートも有効にする必要があります。

```shell
# sysctl net.pf.filter_local=1
```

再起動後も設定を維持するため、`/etc/sysctl.conf` に追記します。

```text
net.pf.filter_local=1
```

<a id="containers-config-files"></a>
## その他の設定ファイル

パッケージをインストールすると多数のテンプレート設定ファイルが配置されますが、直ちに編集する必要はありません。必要に応じて内容を確認・修正してください。

```shell
# pkg list | grep /etc/containers/
/usr/local/etc/containers/containers.conf.sample
/usr/local/etc/containers/policy.json.sample
/usr/local/etc/containers/registries.conf.sample
/usr/local/etc/containers/storage.conf.sample
/usr/local/etc/containers/pf.conf.sample
```

<a id="containers-first"></a>
## 最初のコンテナの実行

各種フラグの詳細は `podman-run(1)` に記載されています。次の実行例では新しいコンテナを作成して対話型端末を接続し、終了時にコンテナを自動削除します。

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
# top -b
last pid: 24414;  load averages:    0.47,    0.51,    0.53; battery: 23%  up 0+18:48:46    23:30:12
2 processes:   1 running, 1 sleeping
CPU:  6.9% user,  0.0% nice,  2.2% system,  0.7% interrupt, 90.2% idle
Mem: 2619M Active, 6587M Inact, 1813M Laundry, 4552M Wired, 56K Buf, 334M Free
ARC: 2526M Total, 802M MFU, 1219M MRU, 3586K Anon, 29M Header, 467M Other
     1625M Compressed, 4234M Uncompressed, 2.61:1 Ratio
Swap: 10G Total, 219M Used, 10G Free, 2% Inuse

  PID USERNAME    THR PRI NICE   SIZE    RES STATE    C   TIME    WCPU COMMAND
17963 root          1   1    0    14M  3120K wait     1   0:00   0.44% sh
24414 root          1   3    0    15M  2992K CPU0     0   0:00   0.00% top
# exit
```

<a id="containers-terminal-tour"></a>
## コンテナのインポートと実行

> **注**: 現時点では、FreeBSD jail の仕様上、FreeBSD 上のすべての Podman コンテナは root として実行する必要があります。

必要なツールとファイアウォールルールが整ったら、公式に公開されているイメージを [FreeBSD Releases](https://download.freebsd.org/releases/OCI-IMAGES/) から、環境に応じて [aarch64](https://download.freebsd.org/releases/OCI-IMAGES/15.1-RELEASE/aarch64/Latest/) または [amd64](https://download.freebsd.org/releases/OCI-IMAGES/15.1-RELEASE/amd64/Latest/) 向けに取得できます。

<a id="containers-importing"></a>
### FreeBSD OCI イメージのインポート

前述のとおり、公開コンテナレジストリから直接イメージをプルするのが最も手軽ですが、最も強固な信頼の連鎖を確保したい場合は、[FreeBSD.org](https://download.freebsd.org/releases) から直接ダウンロードし、PGP 署名済みのリリースアナウンスと照合してチェックサムを検証してください。

```shell
# export OCIBASE=https://download.freebsd.org/releases/OCI-IMAGES/{rel-latest}-RELEASE/amd64/Latest
# podman load -i=$OCIBASE/FreeBSD-{rel-latest}-RELEASE-amd64-container-image-static.txz
Getting image source signatures
Copying blob 44defc6cee2e done   |
Copying config 5921c62e76 done   |
Writing manifest to image destination
Loaded image: localhost/freebsd-static:{rel-latest}-RELEASE-amd64

# podman load -i=$OCIBASE/FreeBSD-{rel-latest}-RELEASE-amd64-container-image-dynamic.txz
Getting image source signatures
Copying blob 6054dffc3887 done   |
Copying config 33427d59f9 done   |
Writing manifest to image destination
Loaded image: localhost/freebsd-dynamic:{rel-latest}-RELEASE-amd64

# podman load -i=$OCIBASE/FreeBSD-{rel-latest}-RELEASE-amd64-container-image-runtime.txz
Getting image source signatures
Copying blob dcbbfcb598fe done   |
Copying config 90c4936754 done   |
Writing manifest to image destination
Loaded image: localhost/freebsd-runtime:{rel-latest}-RELEASE-amd64

# podman load -i=$OCIBASE/FreeBSD-{rel-latest}-RELEASE-amd64-container-image-notoolchain.txz
Getting image source signatures
Copying blob a16c94176cc3 done   |
Copying config 086572f35c done   |
Writing manifest to image destination
Loaded image: localhost/freebsd-notoolchain:{rel-latest}-RELEASE-amd64

# podman load -i=$OCIBASE/FreeBSD-{rel-latest}-RELEASE-amd64-container-image-toolchain.txz
Getting image source signatures
Copying blob b04531b7d93d done   |
Copying config b927c11b2e done   |
Writing manifest to image destination
Loaded image: localhost/freebsd-toolchain:{rel-latest}-RELEASE-amd64
```

<a id="containers-listing"></a>
### イメージの一覧表示

```shell
# podman images
REPOSITORY                    TAG                   IMAGE ID      CREATED       SIZE
localhost/freebsd-toolchain   {rel-latest}-RELEASE-amd64  b927c11b2e8d  13 days ago   660 MB
localhost/freebsd-notoolchain {rel-latest}-RELEASE-amd64  086572f35cc9  13 days ago   152 MB
localhost/freebsd-runtime     {rel-latest}-RELEASE-amd64  90c493675429  13 days ago   34.1 MB
localhost/freebsd-dynamic     {rel-latest}-RELEASE-amd64  33427d59f990  13 days ago   14.5 MB
localhost/freebsd-static      {rel-latest}-RELEASE-amd64  5921c62e76c1  13 days ago   2.92 MB
```

イメージ ID は毎回再現性があり、`IMAGE_ID` 列の値はイメージをインポートした際に表示されたハッシュと一致します。

<a id="containers-listing-layers"></a>
### レイヤーの一覧表示

イメージを構成するレイヤーを表示できます。次の例では、`runtime` イメージが 3 つの要素から成り、それぞれが独立したレイヤーになっていることがわかります。

```shell
# podman image tree ghcr.io/freebsd/freebsd-runtime:14.2
Image ID: c5f3e77557a9
Tags:     [ghcr.io/freebsd/freebsd-runtime:14.2]
Size:     35.07MB
Image Layers
├── ID: cd53fb07fb66 Size: 5.449MB Top Layer of: [ghcr.io/freebsd/freebsd-static:14.2]
├── ID: a01d37f7777b Size:  10.4MB Top Layer of: [ghcr.io/freebsd/freebsd-dynamic:14.2]
└── ID: 36b0c80ca1f7 Size: 19.21MB Top Layer of: [ghcr.io/freebsd/freebsd-runtime:14.2]
```

<a id="containers-public-registries"></a>
### 公開レジストリの利用

最も安全な出所確認方法は [Official FreeBSD Releases](https://download.freebsd.org/releases) からダウンロードすることですが、FreeBSD リリースチームおよびクラスタ管理チームが管理する 2 つの公開コンテナレジストリも用意されています。
どちらのレジストリにあるイメージも同一ですが、よりシンプルでコンテナ向けのワークフローを利用できます。

* [Docker Hub](https://hub.docker.com/u/freebsd)
* [GitHub Container Registry](https://github.com/orgs/freebsd/packages)

<a id="containers-fetching"></a>
### コンテナイメージの取得

公開レジストリからイメージを取得するには `podman pull` を使用します。

```shell
# podman pull ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
Trying to pull ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}...
Getting image source signatures
Copying blob 711cf0d3c0ef done   |
Copying config 086572f35c done   |
Writing manifest to image destination
086572f35cc90b1a1d2b7904b63e8a849071b4ba89b15492f6da47a802372aa2
```

<a id="containers-running"></a>
### コンテナの実行

コンテナを起動するには `podman run` を使用します。
`-it` フラグは対話型端末を割り当て、`--rm` は終了時にコンテナを削除します。
コマンドを指定しない場合は、イメージのデフォルトエントリポイントが実行されます。

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
# exit
```

特定のコマンドを指定して実行することもできます。

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest} uname -a
FreeBSD c0038de70651 {rel-latest}-RELEASE FreeBSD {rel-latest}-RELEASE releng/{rel-latest}-n283562-96841ea08dcf GENERIC amd64
```

コンテナイメージにはカーネルが含まれないため、`freebsd-version(1)` を実行すると、稼働中のカーネルとインストールされているユーザーランドで異なる結果が表示されます。
次の例では、15.1-RELEASE ホスト上で 15.0-RELEASE のコンテナを実行しています。

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest-previous} /bin/sh
# freebsd-version -ru
{rel-latest}-RELEASE
{rel-latest-previous}-RELEASE
# exit
```

<a id="containers-variations"></a>
## 便利な応用例とヒント

`podman run ...` のパラメータのほとんどは `podman build` でもそのまま利用できます。
詳細は `podman-run(1)` および `podman-build(1)` の man ページを参照してください。

短命（ephemeral）なコンテナを終了後に自動クリーンアップするには、`--rm` フラグを使用します。

ダウンロード済みのすべてのイメージを表示するには `podman images -a` を使用します。

```shell
# podman images -a
REPOSITORY                       TAG            IMAGE ID      CREATED      SIZE
ghcr.io/freebsd/freebsd-runtime  {rel-latest}   90c493675429  2 weeks ago  34.1 MB
```

実行中のコンテナを確認するには `podman ps -a` を使用します。

```shell
# podman ps -a
CONTAINER ID  IMAGE                                          COMMAND  CREATED        STATUS        NAMES
3123623bef9b  ghcr.io/freebsd/freebsd-runtime:{rel-latest}   /bin/sh  4 minutes ago  Up 4 minutes  admiring_brattain
```

<a id="containers-env-vars"></a>
### 環境変数

Podman は、各コンテナ内にいくつかのデフォルト環境変数を設定します。

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest} /usr/bin/env
container=podman
TERM=xterm
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOME=/root
HOSTNAME=60bae3343e6b
```

`HOSTNAME` にはデフォルトでコンテナ ID が設定されます。
コンテナ内のアプリケーションに安定したホスト名や意味のあるホスト名が必要な場合は、`--hostname` で上書きできます。

任意の環境変数は `--env` で渡すことができます。

```shell
# podman run --env FOO=BAR -it --rm ghcr.io/freebsd/freebsd-runtime:{rel-latest}
# echo $FOO
BAR
```

<a id="containers-volumes"></a>
### ファイルとボリュームのマウント

ファイルもボリュームも、`--volume` を使ってコンテナへ渡すことができます。
たとえば、`runtime` イメージには `which(1)` が含まれていません。

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-runtime:{rel-latest}
# which
/bin/sh: which: not found
```

ホストからコンテナ内へマウントして利用できます。

```shell
# podman run -it --rm --volume /usr/bin/which:/usr/bin/which \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest}
# which which
/usr/bin/which
```

`freebsd-static` のような軽量イメージでは、ホストに既存の `pkg-static(8)` をマウントすることでコンテナ内に `pkg(8)` をブートストラップできます。
`--volume /var/cache/pkg` でホストのパッケージキャッシュを共有すれば、取得済みパッケージの再ダウンロードを避けられるため、複数のコンテナをビルドする際に特に有用です。
`--no-hosts` フラグは `/etc/hosts` のマウントを抑止し、パッケージのアップグレードと競合するのを防ぎます。

> **注**: パッケージはバージョン固有であるため、パッケージキャッシュの共有はホストとコンテナが同じ FreeBSD メジャーバージョンで動作している場合にのみ機能します。

```shell
# podman run -it --rm \
    --env ASSUME_ALWAYS_YES=true \
    --no-hosts \
    --volume /usr/local/sbin/pkg-static:/bin/pkg-static \
    --volume /var/cache/pkg \
    ghcr.io/freebsd/freebsd-static:{rel-latest}
# pkg-static bootstrap -r FreeBSD
Bootstrapping pkg from pkg+https://pkg.FreeBSD.org/FreeBSD:14:amd64/latest, please wait...
Verifying signature with trusted certificate pkg.freebsd.org.2013102301... done
[fd343e182fa5] Installing pkg-2.1.2...
[fd343e182fa5] Extracting pkg-2.1.2: 100%
```

> **訳注**: 上記の出力例は固定原文のまま保持しています。コマンド行は `{rel-latest}`（15.1）を使用していますが、出力例は FreeBSD 14 環境で取得された内容になっています。

ホスト上のファイルやディレクトリもコンテナ内へマウントできます。

```shell
# podman run -it --rm \
    --volume /etc/fstab:/etc/fstab \
    --volume /tmp:/var/tmp \
    --volume /tmp \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest}
```

<a id="containers-inspecting"></a>
### イメージ内容の調査

シェルやツールを持たない最小イメージを含め、任意のイメージ内の全ファイルを一覧表示するには、コンテナのファイルシステムをエクスポートして内容を表示します。

```shell
# podman export $(podman create --rm ghcr.io/freebsd/freebsd-static:{rel-latest} /) | tar tf -
```

コンテナイメージ自体には `pkg(8)` が含まれていませんが、ホストから `pkg-static(8)` をマウントして、インストール済みのベースシステムパッケージを照会できます。
パッケージ名の一覧を表示するには `pkg info -q`、パッケージが所有するすべてのファイルを表示するには `pkg info -ql` を使用します。

```shell
# podman run --rm \
    -v /usr/local/sbin/pkg-static:/pkg \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest} /pkg info -q
FreeBSD-audit-lib-{rel-latest}
FreeBSD-bzip2-lib-{rel-latest}
FreeBSD-certctl-{rel-latest}
FreeBSD-clibs-{rel-latest}
FreeBSD-fetch-{rel-latest}
FreeBSD-kerberos-lib-{rel-latest}
FreeBSD-libarchive-{rel-latest}
FreeBSD-libcasper-{rel-latest}
FreeBSD-libexecinfo-{rel-latest}
FreeBSD-libucl-{rel-latest}
FreeBSD-mtree-{rel-latest}
FreeBSD-ncurses-lib-{rel-latest}
FreeBSD-openssl-{rel-latest}
FreeBSD-openssl-lib-{rel-latest}
FreeBSD-pam-lib-{rel-latest}
FreeBSD-pkg-bootstrap-{rel-latest}
FreeBSD-rc-{rel-latest}
FreeBSD-runtime-{rel-latest}
FreeBSD-xz-lib-{rel-latest}
FreeBSD-zlib-{rel-latest}
FreeBSD-zoneinfo-{rel-latest}
FreeBSD-zstd-lib-{rel-latest}
```

ホストとコンテナで異なる FreeBSD メジャーバージョンが動作している場合、`pkg(8)` はコンテナ内の `/bin/sh` を調べて ABI を検出し、不一致について警告を表示します。

```shell
# podman run -it --rm \
    --env ASSUME_ALWAYS_YES=true \
    --no-hosts \
    --volume /usr/local/sbin/pkg-static:/usr/sbin/pkg \
    --volume /var/cache/pkg \
    ghcr.io/freebsd/freebsd-runtime:14.4 /bin/sh
# pkg bootstrap
pkg: Warning: Major OS version upgrade detected.  Running "pkg bootstrap -f" recommended
```

`freebsd-dynamic` のように `/bin/sh` を持たないイメージでは、`pkg-static(8)` はシステムの ABI をまったく検出できません。

<a id="containers-name-resolution"></a>
## ネットワークと名前解決

デフォルトでは、Podman ツール群は `mount_nullfs(8)` を使用して、jail ホストから `/etc/resolv.conf` と加工済みの `/etc/hosts`、さらに `/var/run` 内に `.containerenv` ファイルをマウントします。

この hosts ファイルはベースシステムパッケージのアップグレードと競合するため、`podman build` の実行時はマウントをスキップし、本番デプロイ時のみ有効にしておくことが推奨されます。

```shell
# podman run --dns 1.2.3.4 ...
# podman build --no-hosts ...
```

`--dns` フラグは、ホストの `/etc/resolv.conf` をマウントする代わりに任意の DNS サーバを指定します。
`--no-hosts` フラグは、ホストからの `/etc/hosts` マウントを抑止します。

<a id="containers-building"></a>
## カスタムイメージの構築

カスタムイメージは、tarball（たとえば `poudriere(8)` で生成したものや公式リリース tarball）から直接構築する方法、既存のタグ付きイメージから構築する方法、`pkg(8)` からブートストラップする方法で作成できます。

<a id="containers-building-base"></a>
### tarball からの構築

任意の FreeBSD ルートファイルシステム tarball から、`podman-import(1)` を使ってカスタムイメージを作成できます。
使用する tarball は、公式リリースの `base.txz`、`poudriere-image(8)` で生成したもの、あるいは独自のカスタム tarball のいずれでもかまいません。
最終的にタグ付けされたイメージは、レジストリへのプッシュ、変更、さらなるイメージ作成のベースとして利用できます。

```shell
# podman import --os freebsd \
    --arch amd64 \
    --message 'Import FreeBSD {rel-latest}-RELEASE base.txz' \
    https://download.freebsd.org/releases/amd64/{rel-latest}-RELEASE/base.txz
Downloading from "https://download.freebsd.org/releases/amd64/{rel-latest}-RELEASE/base.txz"
Getting image source signatures
Copying blob 3768988b151c done   |
Copying config 332bec83a4 done   |
Writing manifest to image destination
sha256:332bec83a428efa6c9f7d1f8b3fbd589c5613d938dca7da5125240c89f4f3dcd

# podman image tag 332bec83a428 localhost/freebsd-base:{rel-latest}

# podman image ls
REPOSITORY              TAG   IMAGE ID      CREATED        SIZE
localhost/freebsd-base  {rel-latest}  332bec83a428  5 minutes ago  715 MB
```

<a id="containers-building-containerfile"></a>
### Containerfile からの構築

Dockerfile と同様の `Containerfile` を使ってイメージを構築できます。
ほとんどの場合、標準システムツールの大半を含む `freebsd-notoolchain` イメージをベースにするのが最も便利です。
より軽量なコンテナを作る場合は、用途に応じて `freebsd-static`、`freebsd-dynamic`、または `freebsd-runtime` を起点とし、必要なものだけを追加してください。

```dockerfile
# Containerfile
FROM ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
RUN env ASSUME_ALWAYS_YES=yes IGNORE_OS_VERSION=yes pkg bootstrap -r FreeBSD
RUN pkg update
RUN pkg upgrade -y
RUN pkg clean -y
ENTRYPOINT /bin/sh
```

`podman-build(1)` でイメージをビルドします。

```shell
# podman build --no-hosts --squash \
    -t localhost/freebsd-base:{rel-latest} \
    -f ./Containerfile
```

さらにその上に別のイメージを重ねて構築することもできます。

```dockerfile
# Containerfile.webserver
FROM localhost/freebsd-base:{rel-latest}
RUN pkg install -y lang/python3
RUN pkg clean -y
ENTRYPOINT /usr/local/bin/python3 -m http.server
```

```shell
# podman build --no-hosts \
    -t localhost/python-www:{rel-latest} \
    -f ./Containerfile.webserver
```

`--detach` を指定して Web サーバをバックグラウンドで起動し、`-p` でホストのポートをコンテナのポートへマッピングします。
この例では、コンテナが待ち受けるデフォルトのポート 8000 をホストのポート 8888 にマッピングしています。

```shell
# c=$(podman run --detach --rm -p 8888:8000 localhost/python-www:{rel-latest})
```

ポートマッピングには `pf(4)` のリダイレクトルールが使われます。
これらのルールはネットワーク経由で到着するトラフィックをリダイレクトするため、マッピングされたポートには別ホストからアクセスするか、ホストのネットワーク向け IP アドレス経由でアクセスする必要があります。

```shell
$ fetch -v http://172.16.2.10:8888/
resolving server address: 172.16.2.10:8888
requesting http://172.16.2.10:8888/
remote size / mtime: 784 / 0
fetch.out                                              784  B 3791 kBps    00s
```

ホストからコンテナへ直接アクセスするには、コンテナ自身の IP アドレスと待ち受けポートを使用します。

```shell
# podman inspect -f '{{.NetworkSettings.IPAddress}}' $c
10.88.0.91
# fetch -v http://10.88.0.91:8000/
resolving server address: 10.88.0.91:8000
requesting http://10.88.0.91:8000/
remote size / mtime: 784 / 0
fetch.out                                              784  B   25 MBps    00s
```

> **注**: `-p` によるポートマッピングは `pf(4)` のリダイレクトルールで処理され、ネットワーク経由で到着するトラフィックにのみ適用されます。jail ホスト自身から `localhost` や `127.0.0.1` 宛てに発信されたトラフィックはリダイレクトされません。ホストからは代わりにコンテナの IP アドレスを直接使用してください。

> **訳注**: 上記の注記は固定原文のまま訳出していますが、本章の[ネットワークの設定](#containers-networking)節では、`pf.conf` の `nat-anchor "cni-rdr/*"` と `sysctl net.pf.filter_local=1` によりホストから `localhost` 宛ての接続をコンテナ内サービスへリダイレクトできる旨が説明されています。

<a id="containers-advanced"></a>
## 応用的な利用方法

> **訳注**: 原文ではこの見出しの直下に本文がなく、内容は以下の小節で説明されています。

<a id="containers-daemonising"></a>
### Podman のデーモン化

FreeBSD 版の Podman 実装では、2 つの `rc(8)` サービスが提供されます。

* `podman` サービスは起動時に実行され、`restart-policy=always` が設定されたすべてのコンテナを確実に起動します。
* `podman_service` サービスは [Podman API サービス](https://docs.podman.io/en/latest/_static/api.html)を実行し、REST API を提供します。デフォルトでは `/var/run/podman/podman.sock` で待ち受けます。

次のように有効化して起動します。

```shell
# sysrc podman_enable=YES
# sysrc podman_service_enable=YES
# sysrc podman_service_flags='--time 0'
# service podman start
# service podman_service start
```

ホストの再起動後に自動で再起動させたいコンテナは、`--restart=always` オプションを付けて実行しておく必要があります。

```shell
# podman run --detach --restart=always my-image
```

<a id="containers-linux"></a>
### Linux コンテナの実行

FreeBSD の Linux エミュレーション機能を使うと、多くの Linux コンテナイメージを実行できます。

```shell
# service linux onestart
# podman run --rm --os=linux docker.io/alpine cat /etc/os-release | head -1
Trying to pull docker.io/library/alpine:latest...
Getting image source signatures
Copying blob 4abcf2066143 done   |
Copying config 05455a0888 done   |
Writing manifest to image destination
NAME="Alpine Linux"
```

> **注**: systemd に依存する Linux コンテナ、PID 1 として動作することを前提とする Linux コンテナ、あるいは Linux 固有のカーネルインターフェースに依存する Linux コンテナは、FreeBSD の Linux エミュレーション上では正しく動作しない場合があります。

<a id="containers-local-registry"></a>
### ローカルレジストリの運用

レジストリは、OCI イメージを保存・共有するための Web サーバです。
[sysutils/docker-registry](https://freshports.org/sysutils/docker-registry) port は、ローカル開発や小規模組織に適したシンプルなレジストリを提供します。
より包括的でモダンな代替としては [Zot Registry](https://zotregistry.dev/) があります。

```shell
# pkg install -r FreeBSD sysutils/docker-registry
# zfs create zroot/var/db/registry
# chown -R www:www /var/db/registry
# sysrc docker_registry_enable=YES
# sysrc docker_registry_user=www
# sed -i '' -E -e 's,rootdirectory:.+,rootdirectory: /var/db/registry,' \
    /usr/local/etc/docker-registry/config.yml
# touch /usr/local/etc/docker-registry/htpasswd
# chown -R root:www /usr/local/etc/docker-registry/config.yml \
    /usr/local/etc/docker-registry/htpasswd
# chmod 0640 /usr/local/etc/docker-registry/config.yml \
    /usr/local/etc/docker-registry/htpasswd
```

`/usr/local/etc/docker-registry/config.yml` の設定例です。

```yaml
version: 0.1
log:
  fields:
    service: registry
storage:
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /var/db/registry
http:
  addr: :5000
  secret: <random-secret>
  headers:
    X-Content-Type-Options: [nosniff]
auth:
  htpasswd:
    realm: basic-realm
    path: /usr/local/etc/docker-registry/htpasswd
health:
  storagedriver:
    enabled: true
    interval: 10s
    threshold: 3
```

レジストリを起動し、稼働していることを確認します。

```shell
# service registry start
# curl -u admin:passwd http://localhost:5000/v2/
```

> **ヒント**: レジストリは nginx や haproxy などのリバースプロキシの背後に置き、TLS 経由で公開することを推奨します。

<a id="containers-syncing"></a>
### レジストリの同期

`skopeo` を使うと、FreeBSD 公式イメージをローカルレジストリへ同期できます。
次の例では、[Docker Hub](https://hub.docker.com/u/freebsd) にある FreeBSD 関連イメージをすべてローカルレジストリへ複製します。

```yaml
# sync.yml
docker.io:
  images:
    freebsd/freebsd-static: []
    freebsd/freebsd-dynamic: []
    freebsd/freebsd-runtime: []
```

```shell
$ skopeo sync --src yaml --dest docker --all sync.yml cr.example.net/freebsd
INFO[0000] Processing repo                               repo=freebsd/freebsd-static
INFO[0000] Querying registry for image tags              repo=freebsd/freebsd-static
...
INFO[0771] Synced 42 images from 3 sources
```

`/root/.config/containers/auth.json` の認証情報が最新である限り、イメージの同期に root 権限は必要ありません。

<a id="containers-registries-auth"></a>
### コンテナレジストリの操作

一般にレジストリではプッシュ操作に認証が必要であり、プル操作でも認証を求められる場合があります。
ログイン後、認証情報はデフォルトで `/root/.config/containers/auth.json` に保存されます。

```shell
# podman login ghcr.io -u username
Password:
Login Succeeded!
```

その後、イメージをレジストリへプッシュできます。

```shell
# podman push localhost/freebsd-runtime:{rel-latest} \
    docker://ghcr.io/example/freebsd-runtime:{rel-latest}
Getting image source signatures
Copying blob bbacfdfbe140 done   |
Copying config 786f2592a8 done   |
Writing manifest to image destination
```

公開イメージは認証なしでプルできます。

```shell
# podman pull ghcr.io/freebsd/freebsd-runtime:{rel-latest}
```
