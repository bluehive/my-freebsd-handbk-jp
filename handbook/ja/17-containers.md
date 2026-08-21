# 第17章 OCI コンテナ（Containers / Podman）

> **翻訳状態**: 初訳ドラフト（機械支援・要校正）  
> **上流**: https://docs.freebsd.org/en/books/handbook/containers/  
> **ソース参照**: `handbook/en/17-containers.adoc.txt`  
> **著作権**: 原文 © The FreeBSD Documentation Project。本日本語訳は BSD-2-Clause（リポジトリ LICENSE）。

**Part III. System Administration**

---



## OCI コンテナイメージの命名とタグ付け

### はじめに

FreeBSD 公式コンテナイメージはベースシステムパッケージから構築されており、これらは FreeBSD リリースプロセス中にビルドされ、公開レジストリに公開されます。
このガイドでは、イメージの命名方法とタグ付け方法を説明し、ニーズに合ったイメージの選択を支援するとともに、新しいイメージが公開されたり、場合によっては可変タグが修正されたりする際に、それぞれの選択が持つ意味を理解できるようにします。
この命名規則は、新しいベースシステムパッケージの命名スキームに沿ったものであり、コンテナイメージと対応する FreeBSD リリースとの間に明確な由来関係をもたらします。

[[containers-image-types]]
### 利用可能なイメージタイプ

FreeBSD コンテナイメージには、`+amd64+` および `+aarch64+` アーキテクチャ向けに、5 種類のタイプがあります。

[[containers-freebsd-static]]
#### `+freebsd-static+`

静的イメージは、完全に静的リンクされたワークロードのためのベースイメージとして意図されています。ライブラリもバイナリも含まず、この種のほとんどのアプリケーションが必要とする補助ファイルのみを含みます。

* 公開 TLS 証明書
* 最小限のパスワードファイル
* 最小限の termcap
* タイムゾーンデータベース

設計上、フットプリントが小さいため、コンテナがセキュリティ侵害された場合に攻撃者にとっての有用性が低くなります。UNIX シェルも、コマンドラインツールも、動的ライブラリも、パッケージマネージャもありません。
FreeBSD プロジェクトが提供する最小のイメージです。

[[containers-freebsd-dynamic]]
#### `+freebsd-dynamic+`

動的イメージは静的イメージを親レイヤーとして使用し、`+libc+` を含む共有ライブラリの使用をサポートします。
ほとんどの FreeBSD ソフトウェアは、若干の変更を加えるだけで、このイメージで問題なく動作するはずです。
シェル、rc システム、パッケージマネージャはありません。
これらの制限は追加のセキュリティとなり、侵害されたコンテナ内の攻撃者が水平移動したり、インストールされたことのないツールを利用したりすることを困難にします。

[[containers-freebsd-runtime]]
#### `+freebsd-runtime+`

ランタイムも、前述の動的レイヤーを基盤として構築され、ユーザーが期待する最低限のもの、つまり UNIX シェル、rc システム、パッケージマネージャを最終的に追加します。
既存のアプリケーションを最小限の変更で移植するための理想的なベースイメージです。
ユーザーは、Ports ツリーからの追加パッケージに加えて、追加の FreeBSD ベースシステムライブラリを含める必要があります。
これは典型的な FreeBSD システムに最も近く、man:pkg[8] ツールも含まれており、ユーザーは非コンテナ化システムと同様に、ほぼすべてのことをインストールしたり実行したりできます。

[[containers-freebsd-notoolchain]]
#### `+freebsd-notoolchain+`

このベースイメージには、典型的な FreeBSD システムで期待されるほとんどすべてのツールが含まれていますが、ハードウェアに直接関連するもの（コンテナ内では一般的に有用ではないもの）と、かなり大きいためコンパイラおよび関連ツールチェーンは除外されています。

[[containers-freebsd-toolchain]]
#### `+freebsd-toolchain+`

ツールチェーンベースイメージは、完全なコンパイラとツールチェーンを含む、前述のすべてのイメージの合計です。
通常の非 jail FreeBSD システムと同じ方法で、ほぼすべてのソフトウェアを FreeBSD 用にコンパイルすることが一般的に可能です。
すべてのイメージは、基盤となる FreeBSD リリースから派生した一貫した命名パターンに従います。

[[containers-tag-structure]]
### イメージタグの構造

[[containers-immutable-tags]]
#### 不変タグ（Immutable Tags）

不変タグは決して変更されず、安定性と予測可能性を必要とする本番システムに最適です。
これらはリリースプロセスで使用される最も一般的なタグです。
FreeBSD のセキュリティパッチやエラータ通知後も変更されません。
高い再現性が期待されるソフトウェアデプロイメント用のベースイメージに最適ですが、より積極的なセキュリティパッチ適用とのトレードオフになります。

* `+major.minor+`（例：`+14.4+`）：特定の FreeBSD RELEASE バージョンを指します
* `+major.minor.pX+`（例：`+14.4p1+`）：RELEASE の特定のパッチレベルを指します
* `+major.snapYYYYMMDDHHMMSS+`（例：`+16.snap20260325035941+`）：タイムスタンプ付きのスナップショットビルド

[[containers-mutable-tags]]
#### 可変タグ（Mutable Tags）

可変タグは時間の経過とともに更新され、常に最新の更新を取得したいが、FreeBSD の ABI 互換性に沿っていたい本番環境や CI/CD システムに最適です。

* `+major+`（例：`+15+`）は、常に 15.x 安定 ABI に沿った最新のサポート対象 RELEASE バージョンになります
* `+major.snap+`（例：`+15.snap+`）は、15.x 安定 ABI トレインに沿った最新の開発者スナップショットに追従し、多くの場合公式リリースより先んじており、破損のリスクを伴います。

非互換性や、その他の予期しない問題が発生する可能性があります。これは最も可変性の高いタグであり、注意して使用すべきです。FreeBSD の STABLE または CURRENT スナップショットをそのまま使うのとまったく同じで、それらのイメージをソースとしています。

### タグタイプの使い分け

#### 本番環境向け

イミュータブル（不変）タグを使用して、環境を常に一貫した状態に保ちます。

* `freebsd-runtime:15.0` - FreeBSD 15.0-RELEASE に固定

セキュリティパッチがリリースされた場合は、新しいイメージタグを指定して明示的に再ビルドまたは更新する必要があります。

#### 継続的インテグレーションおよび開発向け

ミュータブル（可変）タグを使用すると、最新の更新を自動的に取得できます。

* `freebsd-runtime:15` - 常に 15.x シリーズの最新の公式 RELEASE を指します

以下の追加のミュータブルタグは、FreeBSD STABLE および CURRENT の定期的に公開されるスナップショットに追従します。将来の FreeBSD リリースに含まれる可能性のある内容に対してテストしたい場合に使用し、その際には偶発的な破損や予期しない変更を受け入れる必要があります。

* `freebsd-runtime:14.snap` - 常に 14-STABLE ブランチの最新ビルドを指します
* `freebsd-runtime:15.snap` - 常に 15-STABLE ブランチの最新ビルドを指します
* `freebsd-runtime:16.snap` - 常に 16-CURRENT ブランチの最新ビルドを指します

[[containers-registries]]

## 公式レジストリの場所

アーキテクチャに依存しないイメージは、[公式 FreeBSD リリース](https://download.freebsd.org/releases) サイトからダウンロードして、ご自分のレジストリに直接インポートできます。あるいは、FreeBSD プロジェクトの [Docker Hub](https://hub.docker.com/u/freebsd) または [GitHub Container Registry](https://github.com/orgs/freebsd/packages) からプルすることもできます。

[Alpine Linux](https://hub.docker.com/_/alpine/) と [Debian](https://hub.docker.com/_/debian/) プロジェクトはどちらも、同様の方法でタグ付きのミュータブル（変更可能な）イメージを公開しています。

## Podman の紹介

Podman スイートは、3 つの主要ツールといくつかの補助ツールで構成されています:

* [podman](https://podman.io/) は、docker 互換コマンドを使用するデーモンレスのコンテナエンジンです
* [buildah](https://buildah.io/) は、OCI 形式のコンテナイメージを生成します
* [skopeo](https://github.com/containers/skopeo) は、リモートの OCI イメージレジストリを操作します

## Podman コンテナ用にシステムを準備する

> **警告:**
> SSH または同様のリモートセッションでコマンドを実行する場合は、`man screen(1)`、`man tmux(1)` などを使用して、ファイアウォールの再起動中に接続が失われないようにしてください。

ZFS が利用できない場合は、UFS ストレージに切り替えて、以下の ZFS コマンドをスキップしてください:

```shell
    /usr/local/etc/containers/storage.conf
```

それ以外の場合は、コンテナストレージ用の dataset を作成します:

```shell
# zfs create -o mountpoint=/var/db/containers zroot/containers
# zfs snapshot zroot/containers@empty
```

ファイルディスクリプタファイルシステム (fdescfs) が必要です:

```shell
# mount -t fdescfs fdesc /dev/fd
```

Podman は FreeBSD のパケットフィルタ (pf) を使用して、コンテナポートをホストネットワークに転送します:

```shell
# test -c /dev/pf || kldload pf
# sysctl net.pf.filter_local=1
```

これらの変更を永続的にするには、`/etc/sysctl.conf` と `/etc/fstab` を適宜修正してください。

## Podman のインストール

必要なのは `sysutils/podman-suite` メタパッケージのみですが、追加で `emulators/qemu-user-static` パッケージをインストールすると、`amd64` ホスト上で `arm64` などの他のアーキテクチャ用のイメージをビルドまたはテストできるようになります。

```shell
# pkg install -r FreeBSD -y podman-suite emulators/qemu-user-static
```

`/usr/local/etc/containers/pf.conf.sample` の変更を `/etc/pf.conf` に統合し、egress マクロを適切に設定してから、ファイアウォールを再起動します:

```shell
# service pf restart
```

パッケージはいくつかのテンプレート設定ファイルをインストールしますが、すぐに編集する必要があるものはありません。必要に応じてこれらを確認し、修正してください:

```shell
# pkg list buildah podman conmon \
    ocijail containers-common \
    containernetworking-plugins \
    | grep /etc/
/usr/local/etc/containers/containers.conf.sample
/usr/local/etc/containers/policy.json.sample
/usr/local/etc/containers/registries.conf.sample
/usr/local/etc/containers/storage.conf.sample
/usr/local/etc/containers/pf.conf.sample
```



パブリックレジストリから `podman pull` で取得できます：

```shell
# podman pull ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
Trying to pull ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}...
Getting image source signatures
Copying blob 711cf0d3c0ef done   |
Copying config 086572f35c done   |
Writing manifest to image destination
086572f35cc90b1a1d2b7904b63e8a849071b4ba89b15492f6da47a802372aa2
```

### Running a Container

`podman run` を使ってコンテナを起動します。  
`-it` フラグは対話型ターミナルを割り当て、`--rm` フラグはコンテナが終了したときにコンテナを削除します。  
コマンドが指定されない場合、イメージの既定のエントリポイントが使用されます：

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
# exit
```

特定のコマンドを指定することもできます：

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest} uname -a
FreeBSD c0038de70651 {rel-latest}-RELEASE FreeBSD {rel-latest}-RELEASE releng/{rel-latest}-n283562-96841ea08dcf GENERIC amd64
```

コンテナイメージにはカーネルが含まれていないため、`man freebsd-version(1)` は実行中のカーネルとインストールされているユーザーランドで異なる結果を表示します。  
この例では、{rel-latest-previous}-RELEASE のコンテナが {rel-latest}-RELEASE のホスト上で実行されています：

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest-previous} /bin/sh
# freebsd-version -ru
{rel-latest}-RELEASE
{rel-latest-previous}-RELEASE
# exit
```

## 便利なバリエーションとヒント

`podman run ...` のパラメータはほぼすべて `podman build` にも適用されます。  
詳細は、`man podman-run(1)` および `man podman-build(1)` のマニュアルページを参照してください。

一時的なコンテナは、`--rm` フラグを使うと終了後に自動的に削除されます。

ダウンロード済みのすべてのイメージを表示するには、`podman images -a` を使用します:

```shell
# podman images -a
REPOSITORY                       TAG            IMAGE ID      CREATED      SIZE
ghcr.io/freebsd/freebsd-runtime  {rel-latest}   90c493675429  2 weeks ago  34.1 MB
```

実行中のコンテナを確認するには、`podman ps -a` を使用します:

```shell
# podman ps -a
CONTAINER ID  IMAGE                                          COMMAND  CREATED        STATUS        NAMES
3123623bef9b  ghcr.io/freebsd/freebsd-runtime:{rel-latest}   /bin/sh  4 minutes ago  Up 4 minutes  admiring_brattain
```

### 環境変数

Podman は各コンテナ内に多数のデフォルト環境変数を設定します:

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest} /usr/bin/env
container=podman
TERM=xterm
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOME=/root
HOSTNAME=60bae3343e6b
```

`HOSTNAME` はデフォルトでコンテナ ID に設定されます。  
コンテナ内のアプリケーションが安定した、または意味のあるホスト名を必要とする場合には、`--hostname` で上書きできます。

任意の環境変数は、`--env` で渡すことができます:

```shell
# podman run --env FOO=BAR -it --rm ghcr.io/freebsd/freebsd-runtime:{rel-latest}
# echo $FOO
BAR
```

### ファイルとボリュームのマウント

ファイルとボリュームの両方を `--volume` を使ってコンテナに渡すことができます。  
たとえば、`runtime` イメージには `man which(1)` が含まれていません:

```shell
# podman run -it --rm ghcr.io/freebsd/freebsd-runtime:{rel-latest}
# which
/bin/sh: which: not found
```

これはホストからコンテナにマウントできます:

```shell
# podman run -it --rm --volume /usr/bin/which:/usr/bin/which \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest}
# which which
/usr/bin/which
```

`freebsd-static` のような軽量イメージでは、ホストにある `man pkg-static(8)` をマウントして、コンテナ内で `man pkg(8)` をブートストラップします。  
ホストのパッケージキャッシュを `--volume /var/cache/pkg` で共有すると、すでに取得済みのパッケージを再ダウンロードせずに済みます。これは、複数のコンテナを構築するときに特に便利です。  
`--no-hosts` フラグは、`/etc/hosts` のマウントを防ぎます。そうしないと、パッケージのアップグレードに干渉します。

> **注:** パッケージはバージョン固有であるため、パッケージキャッシュの共有は、ホストとコンテナが同じ FreeBSD メジャーバージョンで動作している場合にのみ機能します。

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

ホストのファイルやディレクトリもコンテナにマウントできます:

```shell
# podman run -it --rm \
    --volume /etc/fstab:/etc/fstab \
    --volume /tmp:/var/tmp \
    --volume /tmp \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest}
```

### イメージ内容の確認

シェルやツールのない最小限のイメージを含む、任意のイメージ内のすべてのファイルを一覧表示するには、コンテナのファイルシステムをエクスポートして、その内容を一覧表示します:

```shell
# podman export $(podman create --rm ghcr.io/freebsd/freebsd-static:{rel-latest} /) | tar tf -
```

コンテナイメージには `man pkg(8)` 自体は含まれていませんが、ホストから `man pkg-static(8)` をマウントして、インストールされているベースシステムのパッケージを問い合わせることができます。  
パッケージ名を一覧表示するには `pkg info -q` を、パッケージが所有するすべてのファイルを表示するには `pkg info -ql` を使用します:

```shell
# podman run --rm \
    -v /usr/local/sbin/pkg-static:/pkg \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest} /pkg info -q
FreeBSD-audit-lib-{rel-latest}
FreeBSD-bzip2-lib-{rel-latest}
FreeBSD-certctl-{rel-
```

ホストとコンテナが異なる FreeBSD メジャーバージョンで動作している場合、`man pkg(8)` はコンテナ内の `/bin/sh` を検査して ABI を検出し、不一致について警告します:

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

`/bin/sh` を含まないイメージ (`freebsd-dynamic` など) では、`man pkg-static(8)` はシステム ABI をまったく検出できません。

<a id="containers-networking"></a>

## ネットワークと名前解決

デフォルトでは、Podman ツール群は `man mount_nullfs(8)` を使用して、jail ホストから `/etc/resolv.conf` と変更された `/etc/hosts`、さらに `/var/run` 内の `.containerenv` ファイルをマウントします。

この hosts ファイルはベースシステムのパッケージアップグレードと競合するため、`podman build` 実行時にはこれをスキップし、本番デプロイ時には有効のままにしておくことをお勧めします:

```shell
# podman run --dns 1.2.3.4 ...
# podman build --no-hosts ...
```

`--dns` フラグは、ホストから `/etc/resolv.conf` をマウントする代わりに、カスタム DNS サーバーを指定します。
`--no-hosts` フラグは、ホストから `/etc/hosts` をマウントしないようにします。

<a id="containers-building"></a>

## カスタムイメージの構築

カスタムイメージは、tarball（たとえば `man poudriere(8)` が生成したものや、公式リリースの tarball）から直接、既存のタグ付きイメージから、または `man pkg(8)` からブートストラップして構築できます。

### Tarball からの構築

`man podman-import(1)` を使用すると、任意の FreeBSD ルートファイルシステム tarball からカスタムイメージを作成できます。tarball には、公式リリースの `base.txz`、`man poudriere-image(8)` が生成したもの、または独自のカスタム tarball を使用できます。最終的なタグ付きイメージは、レジストリにプッシュしたり、変更したり、さらなるイメージ作成に使用したりできます。

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

### Containerfile からの構築

イメージは、Dockerfile と同様の `Containerfile` を使用して構築できます。ほとんどの場合、`freebsd-notoolchain` イメージには標準的なシステムツールがほぼすべて含まれているため、最も便利なベースとなります。より軽量なコンテナの場合は、`freebsd-static`、`freebsd-dynamic`、`freebsd-runtime` のいずれかを適宜ベースにして、必要なものだけを追加してください:

```dockerfile
# Containerfile
FROM ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}
RUN env ASSUME_ALWAYS_YES=yes IGNORE_OS_VERSION=yes pkg bootstrap -r FreeBSD
RUN pkg update
RUN pkg upgrade -y
RUN pkg clean -y
ENTRYPOINT /bin/sh
```

`man podman-build(1)` でイメージを構築します:

```shell
# podman build --no-hosts --squash \
    -t localhost/freebsd-base:{rel-latest} \
    -f ./Containerfile
```

さらに、その上にイメージを重ねることができます:

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

`--detach` で Web サーバーをバックグラウンドで実行し、`-p` でホストのポートをコンテナのポートにマッピングします。この例では、コンテナはデフォルトのポート 8000 で待ち受けし、ホストのポート 8888 にマッピングされています:

```shell
# c=$(podman run --detach --rm -p 8888:8000 localhost/python-www:{rel-latest})
```

ポートマッピングには `man pf(4)` のリダイレクトルールを使用します。これらのルールはネットワークを介して到着するトラフィックをリダイレクトするため、マッピングされたポートには別のホストから、またはホストのネットワーク側 IP アドレス経由でアクセスする必要があります:

```shell
$ fetch -v http://172.16.2.10:8888/
resolving server address: 172.16.2.10:8888
requesting http://172.16.2.10:8888/
remote size / mtime: 784 / 0
fetch.out                                              784  B 3791 kBps    00s
```

ホストからコンテナに直接アクセスするには、コンテナの待受ポートでコンテナ自身の IP を使用します:

```shell
# podman inspect -f '{{.NetworkSettings.IPAddress}}' $c
10.88.0.91
# fetch -v http://10.88.0.91:8000/
resolving server address: 10.88.0.91:8000
requesting http://10.88.0.91:8000/
remote size / mtime: 784 / 0
fetch.out                                              784  B   25 MBps    00s
```

> **注:**
> 
> `-p` によるポートマッピングは `man pf(4)` のリダイレクトルールによって処理され、ネットワークを介して到着するトラフィックにのみ適用されます。jail ホスト自体から `localhost` または `127.0.0.1` へのトラフィックはリダイレクトされません。ホストからは、代わりにコンテナの IP アドレスを直接使用してください。

---

## 高度な使い方

### Podman のデーモン化

FreeBSD の Podman 実装には、2 つの `man rc(8)` サービスがあります。

* `podman` サービスは起動時に実行され、`restart-policy=always` でマークされたすべてのコンテナが起動されるようにします。
* `podman_service` サービスは、[Podman API サービス](https://docs.podman.io/en/latest/_static/api.html) を実行し、REST API を提供し、デフォルトでは `/var/run/podman/podman.sock` で待ち受けます。

以下のようにして有効にします。

```shell
# sysrc podman_enable=YES
# sysrc podman_service_enable=YES
# sysrc podman_service_flags='--time 0'
# service podman start
# service podman_service start
```

ホストの再起動後に自動的に再起動する必要があるコンテナは、`--restart=always` オプションを付けて実行しなければなりません。

```shell
# podman run --detach --restart=always my-image
```

### Linux コンテナの実行

FreeBSD の Linux エミュレーションを使用して、多くの Linux コンテナイメージを実行できます。

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

> **注:** systemd に依存する Linux コンテナ、PID 1 であることを期待するコンテナ、または Linux 固有のカーネルインターフェイスに依存するコンテナは、FreeBSD の Linux エミュレーションでは正しく動作しない可能性があります。

### ローカルレジストリの実行

レジストリは、OCI イメージを保存および共有するための Web サーバーです。  
[sysutils/docker-registry](https://freshports.org/sysutils/docker-registry) ポートは、ローカル開発や小規模な組織に適したシンプルなレジストリを提供します。  
[Zot Registry](https://zotregistry.dev/) は、より包括的な現代的な代替案です。

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

`/usr/local/etc/docker-registry/config.yml` の設定例:

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

レジストリを起動し、動作していることを確認します。

```shell
# service registry start
# curl -u admin:passwd http://localhost:5000/v2/
```

> **ヒント:** レジストリは、nginx や haproxy などのリバースプロキシの背後で TLS 経由で提供することをお勧めします。

### レジストリの同期

`skopeo` を使用して、公式の FreeBSD イメージをローカルレジストリに同期することができます。  
次の例では、[Docker Hub](https://hub.docker.com/u/freebsd) からすべての FreeBSD 関連イメージをローカルレジストリに複製します。

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

`/root/.config/containers/auth.json` 内の認証情報が最新である限り、イメージの同期に root 権限は必要ありません。

### コンテナレジストリの操作

レジストリは通常、プッシュ操作に認証を必要とし、プル操作にもオプションで認証を必要とします。  
認証情報は、ログイン後、デフォルトで `/root/.config/containers/auth.json` に保存されます。

```shell
# podman login ghcr.io -u username
Password:
Login Succeeded!
```

イメージはその後、レジストリにプッシュできます。

公開イメージは認証なしでプルできます。

```shell
# podman pull ghcr.io/freebsd/freebsd-runtime:{rel-latest}
```

[[containers-building-sources]]

## ソースからのコンテナイメージの構築

FreeBSD のリリース用ツール群には `+oci-release+` ターゲットがあり、`podman load` で使用するために必要なイメージを構築できます。
このターゲットは、最初に world、kernel、ベースシステムのパッケージを構築する必要があるため、時間がかかることがあります。

次の例では、`arm64` イメージを構築します:

```shell
# cd /usr/src \
    && make TARGET_ARCH=aarch64 TARGET=arm64 -s -j32 buildworld \
    && make TARGET_ARCH=aarch64 TARGET=arm64 KERNCONF=GENERIC -s -j32 buildkernel \
    && make TARGET_ARCH=aarch64 TARGET=arm64 KERNCONF=GENERIC -s -j32 packages \
    && cd ./release \
    && make TARGET_ARCH=aarch64 TARGET=arm64 -j32 -s clean \
    && make KERNCONF=GENERIC TARGET_ARCH=aarch64 TARGET=arm64 WITH_OCIIMAGES=yes \
      -s oci-release
```

同様に、`amd64` の場合:

```shell
# cd /usr/src \
    && make TARGET_ARCH=amd64 TARGET=amd64 -s -j32 buildworld \
    && make TARGET_ARCH=amd64 TARGET=amd64 KERNCONF=GENERIC -s -j32 buildkernel \
    && make TARGET_ARCH=amd64 TARGET=amd64 KERNCONF=GENERIC -s -j32 packages \
    && cd ./release \
    && make TARGET_ARCH=amd64 TARGET=amd64 -s -j32 clean \
    && make KERNCONF=GENERIC TARGET_ARCH=amd64 TARGET=amd64 \
      WITH_OCIIMAGES=yes -s oci-release
```

[[containers-cross-arch]]
## クロスアーキテクチャテスト

`emulators/qemu-user-static` パッケージを使用すると、他のアーキテクチャ用に構築されたコンテナイメージをテストできます。
パッケージをインストールした後、サービスを有効化して開始し、エミュレートされるすべてのアーキテクチャのイメージアクティベータを登録します:

```shell
# pkg install emulators/qemu-user-static
# service qemu_user_static enable
# service qemu_user_static start
```

次に、適切な QEMU バイナリをマウントして、`amd64` ホスト上で `arm64` イメージを実行します:

```shell
# podman run -it --rm --arch=arm64 \
    -v /usr/local/bin/qemu-aarch64-static:/usr/local/bin/qemu-aarch64-static \
    ghcr.io/freebsd/freebsd-runtime:14.snap uname -a
FreeBSD 73d4049d10b2 14.2-RELEASE-p1 FreeBSD 14.2-RELEASE-p1 GENERIC arm64
```

[[containers-troubleshooting]]

## トラブルシューティング

### パッケージのアップグレードとマウントされたファイル

Podman は `man mount_nullfs(8)` を使って `/etc/resolv.conf` と `/etc/hosts` をコンテナにマウントします。  
このマウントが原因で、`man pkg(8)` による操作中に `Cross-device link` のようなエラーが発生する場合があります:

```
pkg: Fail to rename /etc/.pkgtemp.hosts.VeIDrHM0sKN5 -> /etc/hosts:Cross-device link
```

これを回避するには、`--no-hosts` フラグと `--dns` フラグを使用してください:

```shell
# podman run --no-hosts --dns 1.1.1.1 -it --rm \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest} /bin/sh
```

### ネットワークの確認

最初に、`/usr/local/etc/containers/pf.conf.sample` のファイアウォールルールを使用します。  
コンテナ内から段階的に接続をテストします:

```shell
# podman run --no-hosts --dns 1.1.1.1 \
    --env ASSUME_ALWAYS_YES=1 \
    -it --rm \
    ghcr.io/freebsd/freebsd-runtime:{rel-latest} \
    /bin/sh

# route show 1.1.1.1
   route to: 1.1.1.1
destination: default
    gateway: 10.88.0.1
  interface: eth0

# ping -c 3 10.88.0.1
PING 10.88.0.1 (10.88.0.1): 56 data bytes
64 bytes from 10.88.0.1: icmp_seq=0 ttl=64 time=0.083 ms
...

# ping -c 3 1.1.1.1
PING 1.1.1.1 (1.1.1.1): 56 data bytes
64 bytes from 1.1.1.1: icmp_seq=0 ttl=60 time=0.920 ms
...

# fetch -v http://1.1.1.1/
...

# pkg -dd bootstrap -r FreeBSD
```

`man ping(8)` が失敗する場合は、ICMP がブロックされているかどうかファイアウォールルールを確認してください。  
`man fetch(1)` が失敗する場合は、TCP ポート 80 と 443 がブロックされていないかファイアウォールルールを確認してください。  
`man pkg(8)` が失敗するものの ICMP と TCP が動作する場合は、断片化または MTU の問題の可能性があります。  
`/etc/pf.conf` に `set reassemble yes no-df` を追加し、ファイアウォールを再起動してください。

ブロックされたパケットをデバッグするには、`/etc/pf.conf` 内のすべてのブロックルールで `log` を有効にし、`man pflog(4)` デバイス上で `man tcpdump(1)` を使用します:

```shell
# service pflog onerestart
# tcpdump -vvveni pflog0 icmp or net 10.88.0.0/16
```

### MTU の一貫性

プライマリネットワークインターフェイス、コンテナブリッジ、コンテナ自体の間で、MTU 値が一貫していることを確認してください。  
MTU 値が一致していないと、パケットの断片化や接続障害が発生する可能性があります。

次の例では、`vtnet0` の MTU は 9000 ですが、ブリッジとコンテナの MTU は 1500 です。  
一般に、内部レイアウトを外部ネットワークに合わせて調整してください:

```shell
# ifconfig vtnet0 mtu 9000
# ifconfig cni-podman0 mtu 9000
```

コンテナ内:

```shell
# ifconfig eth0 mtu 9000
```

Podman が使用するブリッジと epair は一時的なものであり、ブリッジの作成ごと、コンテナごとに設定が必要です。  
一部のクラウド環境では、`/etc/pf.conf` に `set reassemble yes no-df` を追加することも必要な場合があります。

---

## 翻訳メモ

- 機械支援初訳。コマンド例は原文照合推奨。
- 用語は `handbook/ja/glossary.md` と揃える。
