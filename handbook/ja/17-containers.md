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
