<a id="network-servers"></a>
# 第33章 ネットワークサーバ（Network Servers）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/network-servers/)の「Chapter 33. Network Servers」を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/network-servers/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。本ファイルは章単位の作業中ドラフトであり、コマンド例・設定例は原文のまま保持しています（実機検証・第三者専門校閲は未実施）。

<a id="network-servers-synopsis"></a>
## 概要（Synopsis）

この章では、UNIX® システムでよく使われる代表的なネットワークサービスについて、インストール・設定・動作確認・運用の手順を解説します。本文中には、設定例となるファイルもあわせて掲載しています。

この章を読み終えると、次のことがわかるようになります。

* `inetd` デーモンの管理方法
* Network File System（NFS）の構築方法
* ユーザーアカウントを一元管理・共有するための Network Information Server（NIS）の構築方法
* FreeBSD を LDAP サーバまたはクライアントとして構成する方法
* DHCP を使ったネットワーク設定の自動割り当て方法
* Domain Name Server（DNS）の構築方法
* Apache HTTP Server の構築方法
* File Transfer Protocol（FTP）サーバの構築方法
* Samba を使った Windows® クライアント向けファイル／プリントサーバの構築方法
* Network Time Protocol（NTP）を使った日時同期とタイムサーバの構築方法
* iSCSI の構築方法

この章を読むにあたっては、次の基本的な知識を前提としています。

* `/etc/rc` スクリプトの仕組み
* ネットワークの基本用語
* サードパーティ製ソフトウェアの追加インストール方法（[アプリケーションの導入: Packages と Ports](04-ports.md#ports)）

<a id="network-inetd"></a>
## `inetd` スーパーサーバ（The inetd Super-Server）

`inetd(8)` デーモンは、多数のサービスの接続を一括して管理するため「スーパーサーバ（Super-Server）」と呼ばれることがあります。複数のアプリケーションを個別に起動しておく代わりに、`inetd` サービスだけを起動しておけば済みます。`inetd` が管理するサービス宛ての接続を受けると、`inetd` はその接続に対応するプログラムを判別し、プロセスを起動してソケットを引き渡します。利用頻度の低いサービスを `inetd` 経由で動かすことで、各デーモンをスタンドアロンモードで常時起動しておく場合と比べてシステム負荷を抑えることができます。

`inetd` の主な役割は他のデーモンを起動することですが、`chargen`、`auth`、`time`、`echo`、`discard`、`daytime` といった簡単なプロトコルは内部で直接処理します。

この節では、`inetd` の基本的な設定方法を解説します。

<a id="network-inetd-conf"></a>
### 設定ファイル（Configuration File）

`inetd` の設定は `/etc/inetd.conf` を編集して行います。この設定ファイルの各行が、`inetd` から起動できる 1 つのアプリケーションに対応しています。初期状態ではすべての行がコメント（`#`）で始まっており、`inetd` はどのアプリケーションの接続も待ち受けていません。特定のアプリケーションへの接続を待ち受けさせるには、該当行の先頭にある `#` を削除します。

編集を保存したら、システム起動時に `inetd` が自動起動するよう `/etc/rc.conf` に追記します。

```
inetd_enable="YES"
```

設定したサービスの待ち受けを今すぐ開始するには、次のように `inetd` を起動します。

```shell
# service inetd start
```

`inetd` の起動後に `/etc/inetd.conf` を変更した場合は、その都度 `inetd` へ再読み込みを通知する必要があります。

<a id="network-inetd-reread"></a>
**例: `inetd` 設定ファイルの再読み込み**

```shell
# service inetd reload
```

通常は、対象アプリケーションの既定エントリから `#` を外すだけで編集は済みます。ただし、状況によっては既定エントリ自体を調整したほうがよい場合もあります。

例として、IPv4 上の `ftpd(8)` に対する既定エントリを次に示します。

```
ftp     stream  tcp     nowait  root    /usr/libexec/ftpd       ftpd -l
```

エントリ内の 7 つの列（フィールド）は次の構成になっています。

```
service-name
socket-type
protocol
{wait|nowait}[/max-child[/max-connections-per-ip-per-minute[/max-child-per-ip]]]
user[:group][/login-class]
server-program
server-program-arguments
```

各列の意味は次のとおりです。

* `service-name`: 起動するデーモンのサービス名です。`/etc/services` に記載されたサービスと一致している必要があり、この値によって `inetd` が接続を待ち受けるポートが決まります。独自サービスを使う場合は、あらかじめ `/etc/services` に追加しておく必要があります。
* `socket-type`: `stream`、`dgram`、`raw`、`seqpacket` のいずれかを指定します。TCP 接続には `stream`、UDP サービスには `dgram` を使用します。
* `protocol`: 次のプロトコル名のいずれかを指定します。

  | プロトコル名 | 説明 |
  |---|---|
  | `tcp` または `tcp4` | TCP IPv4 |
  | `udp` または `udp4` | UDP IPv4 |
  | `tcp6` | TCP IPv6 |
  | `udp6` | UDP IPv6 |
  | `tcp46` | TCP IPv4 と IPv6 の両方 |
  | `udp46` | UDP IPv4 と IPv6 の両方 |

* `{wait|nowait}[/max-child[/max-connections-per-ip-per-minute[/max-child-per-ip]]]`: この列では `wait` または `nowait` の指定が必須です。`max-child`、`max-connections-per-ip-per-minute`、`max-child-per-ip` は省略可能です。

  `wait|nowait` は、そのサービス自身がソケットを処理できるかどうかを示します。`dgram` ソケット種別では `wait` を指定する必要があり、通常マルチスレッドで動作する `stream` デーモンでは `nowait` を指定します。一般的に `wait` は 1 つのデーモンに複数のソケットを処理させ、`nowait` は新しいソケットごとに子デーモンを起動します。

  `inetd` が起動できる子デーモンの最大数は `max-child` で設定します。たとえばデーモンの同時実行数を 10 個に制限するには、`nowait` の後ろに `/10` を付けます。`/0` を指定すると子プロセス数の上限がなくなります。

  `max-connections-per-ip-per-minute` は、特定の IP アドレスからの 1 分あたりの接続回数を制限します。上限に達すると、その IP アドレスからの以降の接続はその分が終わるまで破棄されます。たとえば `/10` を指定すると、任意の単一 IP アドレスからの接続試行は 1 分間に 10 回までに制限されます。`max-child-per-ip` は、任意の時点で 1 つの IP アドレスのために起動できる子プロセス数の上限を設定します。これらのオプションにより、過剰なリソース消費を抑え、サービス拒否（DoS）攻撃の緩和に役立てることができます。

  設定例は `fingerd(8)` の既定エントリで確認できます。

  ```
  finger stream  tcp     nowait/3/10 nobody /usr/libexec/fingerd fingerd -k -s
  ```

* `user`: デーモンを実行するユーザー名です。通常は `root`、`daemon`、`nobody` のいずれかで実行します。
* `server-program`: デーモンのフルパスです。`inetd` が内部で提供するサービスの場合は `internal` を指定します。
* `server-program-arguments`: デーモン起動時に渡すコマンド引数を指定します。内部サービスの場合は `internal` を指定します。

<a id="network-inetd-cmdline"></a>
### コマンドラインオプション（Command-Line Options）

多くのサーバデーモンと同様、`inetd` にも動作を変更するためのオプションが用意されています。既定では、`inetd` は `-wW -C 60` を指定して起動されます。この設定により、内部サービスを含むすべてのサービスで TCP ラッパー（TCP wrappers）が有効になり、同一 IP アドレスから 1 分間に 60 回を超えるサービス要求が拒否されます。

`inetd` に渡す既定のオプションを変更するには、`/etc/rc.conf` に `inetd_flags` のエントリを追加します。すでに `inetd` が動作している場合は、`service inetd restart` で再起動してください。

利用可能なレート制限オプションは次のとおりです。

* `-c maximum`: 各サービスを同時に起動できる既定の最大数を指定します（既定は無制限）。`/etc/inetd.conf` 内の `max-child` を使ってサービスごとに上書きできます。
* `-C rate`: 単一 IP アドレスから 1 分間に 1 つのサービスを起動できる既定の最大回数を指定します。`/etc/inetd.conf` 内の `max-connections-per-ip-per-minute` を使ってサービスごとに上書きできます。
* `-R rate`: 1 分間に 1 つのサービスを起動できる最大回数を指定します（既定は `256`）。`0` を指定すると無制限になります。
* `-s maximum`: 単一 IP アドレスから同時に 1 つのサービスを起動できる最大数を指定します（既定は無制限）。`/etc/inetd.conf` 内の `max-child-per-ip` を使ってサービスごとに上書きできます。

このほかにもオプションがあります。全一覧については `inetd(8)` を参照してください。

<a id="network-inetd-security"></a>
### セキュリティ上の考慮事項（Security Considerations）

`inetd` で管理できるデーモンの多くは、セキュリティを十分に意識して作られていません。たとえば `fingerd` のようなデーモンは、攻撃者に有用な情報を漏らしてしまうおそれがあります。必要なサービスだけを有効にし、過剰な接続試行がないかシステムを監視してください。そうした攻撃を制限するために、`max-connections-per-ip-per-minute`、`max-child`、`max-child-per-ip` を活用できます。

既定では TCP ラッパーが有効になっています。`inetd` から起動される各種デーモンに TCP の接続制限を設定する方法については、`hosts_access(5)` を参照してください。
