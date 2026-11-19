<a id="network-servers"></a>
# 第33章 ネットワークサーバ（Network Servers）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/network-servers/)の「Chapter 33. Network Servers」を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/network-servers/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。コマンド例・設定例・出力例は原文のまま保持しています（FreeBSD 実機での動作確認および第三者による専門校閲は未実施）。

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

<a id="network-nfs"></a>
## Network File System（NFS）

FreeBSD は Network File System（NFS）に対応しており、サーバがディレクトリやファイルをネットワーク越しにクライアントと共有できます。NFS を使うと、ユーザーやプログラムはリモートシステム上のファイルを、あたかもローカルに保存されているかのようにアクセスできます。

NFS には多くの実用的な用途があり、代表的なものとして次が挙げられます。

* 各クライアントに重複して置く必要のあったデータを 1 か所にまとめて保持し、ネットワーク上のクライアントから参照する。
* 複数のクライアントが `/usr/ports/distfiles` ディレクトリを参照する必要がある場合に、そのディレクトリを共有して各クライアントへのダウンロードを省き、ソースファイルへ素早くアクセスする。
* 大規模なネットワークで、全ユーザーのホームディレクトリを中央の NFS サーバに集約して管理する。ユーザーはネットワーク上のどのクライアントにログインしても自分のホームディレクトリを利用できる。
* NFS エクスポートの管理を簡素化する。たとえば、セキュリティ設定やバックアップ方針を設定すべきファイルシステムが 1 つだけで済む。
* リムーバブルメディアの記憶装置をネットワーク上の他のマシンからも利用できるようにする。ネットワーク全体のデバイス数を減らし、セキュリティ管理を 1 か所に集約できるほか、集約されたインストールメディアから複数マシンへソフトウェアをインストールする際にも便利である。

NFS は 1 台のサーバと 1 台以上のクライアントで構成され、クライアントはサーバ上に保存されたデータへリモートからアクセスします。正しく機能させるには、いくつかのプロセスを設定して起動しておく必要があります。

サーバ側では、次のデーモンが動作している必要があります。

| デーモン | 説明 |
|---|---|
| `nfsd` | NFS クライアントからの要求を処理する NFS デーモン。 |
| `mountd` | `nfsd` が受け取ったマウント要求を実行する NFS マウントデーモン。 |
| `rpcbind` | NFS サーバが使用しているポートを NFS クライアントが発見できるようにするデーモン。 |

クライアント側で `nfsiod(8)` を動かすと性能を向上できますが、必須ではありません。

<a id="network-configuring-nfs"></a>
### サーバの設定（Configuring the Server）

NFS サーバが共有するファイルシステムは `/etc/exports` に記述します。このファイルの各行では、エクスポートするファイルシステム、アクセスを許可するクライアント、および各種アクセスオプションを指定します。エントリを追加する際は、エクスポート対象のファイルシステム・その属性・許可するホストを 1 行にまとめて記述する必要があります。エントリにクライアントを 1 つも記載しない場合は、ネットワーク上のどのクライアントからでもそのファイルシステムをマウントできるようになります。

以下に、ファイルシステムをエクスポートする `/etc/exports` の記述例を示します。ファイルシステム名やクライアント名は、各自のネットワーク環境に合わせて書き換えてください。このファイルでは多くのオプションを指定できますが、ここでは一部のみを紹介します。全オプションの一覧は `exports(5)` を参照してください。

次の例では、`/media` を *alpha*、*bravo*、*charlie* という 3 台のホストへエクスポートしています。

```
/media -ro alpha bravo charlie
```

`-ro` フラグを付けるとファイルシステムが読み取り専用（read-only）になり、クライアントがエクスポートされたファイルシステムに変更を加えられなくなります。この例では、ホスト名が DNS または `/etc/hosts` で名前解決できることを前提としています。ネットワークに DNS サーバがない場合は `hosts(5)` を参照してください。

次の例では、`/home` を IP アドレス指定で 3 台のクライアントへエクスポートしています。DNS や `/etc/hosts` のエントリがないネットワークで有用です。`-alldirs` フラグは、サブディレクトリをマウントポイントとして指定できるようにするものです。つまり、サブディレクトリを自動的にすべてマウントするのではなく、必要に応じてクライアントが配下のディレクトリをマウントできるようにします。

```
/usr/home  -alldirs  10.0.0.2 10.0.0.3 10.0.0.4
```

次の例では、異なるドメインに属する 2 台のクライアントがアクセスできるよう `/a` をエクスポートしています。`-maproot=root` を指定すると、リモートシステム上の `root` が、エクスポートされたファイルシステム上でも `root` としてデータを書き込めるようになります。`-maproot=root` を指定しない場合、クライアント側の `root` ユーザーはサーバ側の `nobody` アカウントにマッピングされ、`nobody` に設定されたアクセス制限を受けます。

```
/a  -maproot=root  host.example.com box.example.org
```

1 つのファイルシステムに対して同じクライアントを複数回指定することはできません。たとえば、`/usr` が 1 つのファイルシステムである場合、同じホストを 2 行に書くと無効になります。

```
# Invalid when /usr is one file system
/usr/src   client
/usr/ports client
```

この場合は、次のように 1 つのエントリにまとめるのが正しい書式です。

```
/usr/src /usr/ports  client
```

次に、`/usr` と `/exports` がローカルファイルシステムである場合の有効なエクスポート一覧の例を示します。

```
# Export src and ports to client01 and client02, but only
# client01 has root privileges on it
/usr/src /usr/ports -maproot=root    client01
/usr/src /usr/ports               client02
# The client machines have root and can mount anywhere
# on /exports. Anyone in the world can mount /exports/obj read-only
/exports -alldirs -maproot=root      client01 client02
/exports/obj -ro
```

システム起動時に NFS サーバに必要なプロセスを有効にするため、`/etc/rc.conf` に次の設定を追加します。

```
rpcbind_enable="YES"
nfs_server_enable="YES"
mountd_enable="YES"
```

次のコマンドを実行すると、今すぐサーバを起動できます。

```shell
# service nfsd start
```

NFS サーバを起動すると、`mountd` も自動的に起動します。ただし、`mountd` は起動時にしか `/etc/exports` を読み込みません。あとから `/etc/exports` を編集した内容を即座に反映させるには、`mountd` に再読み込みを指示してください。

```shell
# service mountd reload
```

`exports(5)` ファイルの代わりに ZFS の `sharenfs` プロパティを使って ZFS データセットを NFS でエクスポートする方法については、`zfs-share(8)` を参照してください。

NFS Version 4 の構成方法については、`nfsv4(4)` を参照してください。

<a id="chapter-33-heading-09"></a>
### クライアントの設定（Configuring the Client）

NFS クライアント機能を有効にするには、各クライアントの `/etc/rc.conf` に次の設定を追加します。

```
nfs_client_enable="YES"
```

続いて、各 NFS クライアントで次のコマンドを実行します。

```shell
# service nfsclient start
```

これで、クライアント側からリモートファイルシステムをマウントする準備が整いました。以下の例では、サーバ名を `server`、クライアント名を `client` としています。`server` 上の `/home` を `client` 上の `/mnt` マウントポイントへマウントするには、次のように実行します。

```shell
# mount server:/home /mnt
```

これにより、`/home` 内のファイルとディレクトリが `client` の `/mnt` ディレクトリから利用できるようになります。

クライアントの起動時に毎回リモートファイルシステムを自動マウントするには、`/etc/fstab` に追記します。

```
server:/home	/mnt	nfs	rw	0	0
```

指定可能なすべてのオプションについては、`fstab(5)` を参照してください。

<a id="chapter-33-heading-10"></a>
### ロック機能（Locking）

アプリケーションによっては、正常に動作するためにファイルロックが必要になる場合があります。ロック機能を有効にするには、クライアント側とサーバ側の両方で次のコマンドを実行します。

```shell
# sysrc rpc_lockd_enable="YES"
```

その後、`rpc.lockd(8)` サービスを起動します。

```shell
# service lockd start
```

サーバ側でのロックが不要な場合は、`mount` 実行時に `-L` を指定することで、NFS クライアント側でローカルロックを行うように構成できます。詳細は `mount_nfs(8)` を参照してください。

<a id="network-autofs"></a>
### `autofs(5)` による自動マウント（Automating Mounts with `autofs(5)`）

> **注記（NOTE）**: `autofs(5)` 自動マウント機能は FreeBSD 10.1-RELEASE 以降でサポートされています。それ以前のバージョンの FreeBSD で自動マウント機能を使う場合は、代わりに `amd(8)` を使用してください。本章では `autofs(5)` による自動マウントのみを解説します。

`autofs(5)` 機能は、リモートおよびローカルのファイルシステム内のファイルやディレクトリへアクセスしたタイミングで自動的にマウントを行う、複数のコンポーネントの総称です。カーネル側コンポーネントである `autofs(5)` と、ユーザー空間の複数のアプリケーション（`automount(8)`、`automountd(8)`、`autounmountd(8)`）で構成されています。これは従来の FreeBSD リリースで使われていた `amd(8)` の代替となる仕組みです。両者はマップ形式が異なるため、後方互換性のために `amd` も引き続き提供されています。`autofs` が採用しているマップ形式は、Solaris、MacOS X、Linux などの他の SVR4 系オートマウンタと同じものです。

`autofs(5)` 仮想ファイルシステムは、通常は起動時に実行される `automount(8)` によって指定のマウントポイントへマウントされます。

プロセスが `autofs(5)` マウントポイント内のファイルへアクセスしようとすると、カーネルは `automountd(8)` デーモンへ通知し、アクセス元プロセスを一時停止させます。`automountd(8)` デーモンは適切なマップを検索して指示どおりにファイルシステムをマウントすることでカーネルからの要求を処理し、その後カーネルへ通知して待機中のプロセスを再開させます。`autounmountd(8)` デーモンは、自動マウントされたファイルシステムが引き続き使用中でない限り、一定時間経過後に自動でアンマウントします。

`autofs` の主要な設定ファイルは `/etc/auto_master` です。このファイルでトップレベルのマウントに個別のマップを割り当てます。`auto_master` およびマップ構文の解説については、`auto_master(5)` を参照してください。

特別なオートマウンタマップとして、`/net` にマウントされるものがあります。このディレクトリ配下のファイルにアクセスすると、`autofs(5)` は対応するリモートマウントを検索して自動的にマウントします。たとえば、`/net/foobar/usr` 内のファイルへアクセスしようとすると、`automountd(8)` に対してホスト `foobar` の `/usr` エクスポートをマウントするよう指示が出ます。

**例: `autofs(5)` によるエクスポートのマウント**

次の例では、`showmount -e` を使って NFS サーバ `foobar` からマウント可能なエクスポート済みファイルシステムを表示しています。

```shell
% showmount -e foobar
Exports list on foobar:
/usr                               10.10.10.0
/a                                 10.10.10.0
% cd /net/foobar/usr
```

`showmount` の出力には、エクスポートの 1 つとして `/usr` が表示されています。`/host/foobar/usr` へディレクトリ移動すると、`automountd(8)` がその要求を捕捉し、ホスト名 `foobar` の名前解決を試みます。名前解決に成功すると、`automountd(8)` は元のエクスポートを自動的にマウントします。

> **訳注**: 原文の解説文では `/host/foobar/usr` と記載されていますが、直前の実行例や FreeBSD の既定の `/etc/auto_master` における `-hosts` マップのマウント先は `/net`（`/net/foobar/usr`）です。

起動時に `autofs(5)` を有効にするには、`/etc/rc.conf` に次の行を追加します。

```
autofs_enable="YES"
```

その後、次のコマンドを実行して `autofs(5)` を起動します。

```shell
# service automount start
# service automountd start
# service autounmountd start
```

`autofs(5)` のマップ形式は他の OS と共通であるため、[Mac OS X のドキュメント（アーカイブ）](http://web.archive.org/web/20160813071113/http://images.apple.com/business/docs/Autofs.pdf)といった他システムの資料も参考になります。

詳細は `automount(8)`、`automountd(8)`、`autounmountd(8)`、および `auto_master(5)` の各マニュアルページを参照してください。

<a id="network-nis"></a>
## Network Information System（NIS）

Network Information System（NIS）は、Solaris™、HP-UX、AIX®、Linux、NetBSD、OpenBSD、FreeBSD といった UNIX® 系システムの管理を一元化するために設計されました。NIS はもともと Yellow Pages と呼ばれていましたが、商標上の問題から名称が変更されました。NIS のコマンド名が `yp` で始まるのはそのためです。

NIS は Remote Procedure Call（RPC）ベースのクライアント／サーバシステムであり、1 つの NIS ドメインに属する複数のマシンが共通の設定ファイル群を共有できるようにします。これにより、システム管理者は最小限の設定データだけで NIS クライアントをセットアップし、1 か所から設定データの追加・削除・変更を行えるようになります。

FreeBSD では NIS プロトコルのバージョン 2 を使用します。

<a id="chapter-33-heading-13"></a>
### NIS の用語とプロセス（NIS Terms and Processes）

表 28.1 に、NIS で使われる用語と重要なプロセスをまとめます。

**表: NIS の用語**

| 用語 | 説明 |
|---|---|
| NIS ドメイン名 | NIS サーバとクライアントが共有する NIS ドメイン名。通常、この名前は DNS とは無関係である。 |
| `rpcbind(8)` | RPC を有効にするサービス。NIS サーバとして動作させる場合も、NIS クライアントとして動作させる場合も起動しておく必要がある。 |
| `ypbind(8)` | NIS クライアントを NIS サーバへバインドするサービス。NIS ドメイン名を受け取り、RPC を使ってサーバへ接続する。NIS 環境におけるクライアント／サーバ間通信の中核であり、クライアントマシン上でこのサービスが動いていないと NIS サーバへアクセスできない。 |
| `ypserv(8)` | NIS サーバ側のプロセス。このサービスが停止するとサーバは NIS 要求に応答できなくなるため、引き継げるスレーブサーバを用意しておくことが望ましい。FreeBSD 以外のクライアントの一部はスレーブサーバへの再接続を試みないため、その場合はクライアント上で `ypbind` プロセスを再起動する必要がある。 |
| `rpc.yppasswdd(8)` | NIS マスターサーバ上でのみ動作するプロセス。このデーモンにより、NIS クライアントから NIS パスワードを変更できるようになる。動いていない場合、ユーザーは NIS マスターサーバへログインしてパスワードを変更しなければならない。 |

> **訳注**: 原文の表番号（表 28.1 および後述の表 28.2・28.3）は、上流ソースに残っている旧章番号に基づく表記です。

<a id="chapter-33-heading-14"></a>
### マシンの種類（Machine Types）

NIS 環境には 3 種類のホストが存在します。

* **NIS マスターサーバ**

  ホスト設定情報の中央リポジトリとして機能し、すべての NIS クライアントが利用する設定ファイルの正本（authoritative copy）を保持します。NIS クライアントが参照する `passwd`、`group` などの各種ファイルはマスターサーバ上に保存されます。1 台のマシンを複数の NIS ドメインの NIS マスターサーバにすることも可能ですが、本章では比較的小規模な NIS 環境を想定しているため、そうした構成は扱いません。

* **NIS スレーブサーバ**

  NIS スレーブサーバは、冗長性を確保するために NIS マスターのデータファイルの複製を保持します。また、NIS クライアントは最初に応答した NIS サーバへ接続するため、スレーブサーバはマスターサーバの負荷分散にも役立ちます。

* **NIS クライアント**

  NIS クライアントは、ログイン時に NIS サーバに対して認証を行います。

NIS を使えば多くのファイルの情報を共有できます。一般的に共有されるのは `master.passwd`、`group`、`hosts` ファイルです。クライアント上のプロセスが本来ローカルのこれらのファイルから取得する情報を必要とすると、代わりにバインド先の NIS サーバへ問い合わせを行います。

<a id="chapter-33-heading-15"></a>
### 設計上の考慮事項（Planning Considerations）

この節では、一元管理の仕組みを持たない 15 台の FreeBSD マシンで構成されたサンプル NIS 環境を想定して説明します。各マシンはそれぞれ独自の `/etc/passwd` と `/etc/master.passwd` を持っており、これらのファイルは手動作業によってのみ同期が保たれています。現状では、ラボにユーザーを 1 人追加するたびに、15 台すべてのマシンで同じ作業を繰り返さなければなりません。

ラボの構成は次のとおりです。

| マシン名 | IP アドレス | マシンの役割 |
|---|---|---|
| `ellington` | `10.0.0.2` | NIS マスター |
| `coltrane` | `10.0.0.3` | NIS スレーブ |
| `basie` | `10.0.0.4` | 教員用ワークステーション |
| `bird` | `10.0.0.5` | クライアントマシン |
| `cli[1-11]` | `10.0.0.[6-17]` | その他のクライアントマシン |

初めて NIS の仕組みを導入する場合は、事前に十分な設計を行っておく必要があります。ネットワークの規模にかかわらず、計画段階でいくつかの事項を決めておかなければなりません。

<a id="chapter-33-heading-16"></a>
#### NIS ドメイン名の決定（Choosing a NIS Domain Name）

クライアントが情報要求をブロードキャストする際、自身が属する NIS ドメインの名前を含めます。これにより、同一ネットワーク上の複数のサーバが、どのサーバがどの要求に応答すべきかを判断できます。NIS ドメイン名は「ホストのグループに付ける名前」と考えるとわかりやすいでしょう。

組織によってはインターネットドメイン名をそのまま NIS ドメイン名に使うことがありますが、ネットワーク障害のデバッグ時に混乱を招くため推奨されません。NIS ドメイン名はネットワーク内で一意であるべきで、それが表すマシン群を連想しやすい名前であると便利です。たとえば Acme Inc. の美術部門なら `"acme-art"` のような NIS ドメイン名が考えられます。この例ではドメイン名として `test-domain` を使用します。

ただし、FreeBSD 以外の OS の中には、NIS ドメイン名がインターネットドメイン名と一致していることを要求するものもあります。ネットワーク上の 1 台以上のマシンにそのような制約がある場合は、インターネットドメイン名を NIS ドメイン名として*必ず*使用しなければなりません。

<a id="chapter-33-heading-17"></a>
#### 物理サーバの要件（Physical Server Requirements）

NIS サーバとして使うマシンを選ぶ際には、いくつか留意すべき点があります。NIS クライアントはサーバの可用性に依存するため、頻繁に再起動されないマシンを選んでください。NIS サーバは、理想的には NIS サーバ専用として稼働するスタンドアロンマシンであるべきです。ネットワークの負荷が高くない場合は、他のサービスを動かすマシンに NIS サーバを同居させても構いません。ただし、NIS サーバが利用できなくなると、すべての NIS クライアントに悪影響が及びます。

<a id="chapter-33-heading-18"></a>
### NIS マスターサーバの設定（Configuring the NIS Master Server）

すべての NIS ファイルの正本はマスターサーバ上に保存されます。情報の保存に使われるデータベースは「NIS マップ」と呼ばれます。FreeBSD では、これらのマップは `/var/yp/[domainname]`（`[domainname]` は NIS ドメイン名）に保存されます。複数ドメインに対応しているため、ドメインごとに複数のディレクトリを持つこともでき、各ドメインは独立したマップ一式を保持します。

NIS マスターサーバおよびスレーブサーバは、すべての NIS 要求を `ypserv(8)` を通じて処理します。このデーモンは、NIS クライアントからの要求を受け取り、要求されたドメイン名とマップ名を対応するデータベースファイルのパスへ変換し、データベースからクライアントへデータを送信する役割を担います。

マスター NIS サーバの構築は、環境要件にもよりますが比較的簡単です。FreeBSD には NIS サポートが組み込まれているため、`/etc/rc.conf` に次の行を追加するだけで有効にできます。

```
nisdomainname="test-domain"
nis_server_enable="YES"
nis_yppasswdd_enable="YES"
```

1. 1 行目で NIS ドメイン名を `test-domain` に設定します。
2. 2 行目でシステム起動時に NIS サーバプロセスを自動起動します。
3. 3 行目で `rpc.yppasswdd(8)` デーモンを有効にし、ユーザーがクライアントマシンから自分の NIS パスワードを変更できるようにします。

サーバマシン自身も NIS クライアントとなるマルチサーバドメインでは注意が必要です。サーバがブロードキャストでバインド要求を出して互い（別のサーバ）にバインドしてしまうのを許すのではなく、自分自身にバインドするよう強制するのが一般的によい方法です。あるサーバが停止し、他のサーバがそれに依存している状態だと、不可解な障害パターンを引き起こすことがあります。最終的にはすべてのクライアントがタイムアウトして別のサーバへバインドしようとしますが、それまでにかなりの遅延が発生するうえ、サーバ同士が再び互いにバインドしてしまうと障害状態が再発します。

クライアントも兼ねるサーバを特定のサーバへ強制的にバインドさせるには、`/etc/rc.conf` に次の行を追加します。

```
nis_client_enable="YES"
nis_client_flags="-S test-domain,server"
```

1. クライアント関連のプロセスもあわせて動作するよう有効化します。
2. NIS ドメイン名を `test-domain` に設定し、自分自身へバインドするよう指定します。

編集を保存したら、`/etc/netstart` を実行してネットワークを再起動し、`/etc/rc.conf` に定義した値を反映させます。NIS マップを初期化する前に、`ypserv(8)` を起動してください。

```shell
# service ypserv start
```

<a id="chapter-33-heading-19"></a>
#### NIS マップの初期化（Initializing the NIS Maps）

NIS マップは NIS マスター上の `/etc` 配下の設定ファイルから生成されますが、1 つだけ例外があり、それが `/etc/master.passwd` です。これは、NIS ドメイン内のすべてのサーバへパスワードがそのまま伝播するのを防ぐためです。そのため、NIS マップを初期化する前に、元となるパスワードファイルを準備します。

```shell
# cp /etc/master.passwd /var/yp/master.passwd
# cd /var/yp
# vi master.passwd
```

システムアカウントのエントリや、`root` その他の管理用アカウントなど、NIS クライアントへ配布する必要のないユーザーアカウントはすべて削除しておくことを推奨します。

> **注記（NOTE）**: `/var/yp/master.passwd` のパーミッションを `600` に設定し、グループやその他のユーザーから読み取れないように必ず確認してください。

この作業が終わったら、NIS マップを初期化します。FreeBSD にはこのための `ypinit(8)` スクリプトが用意されています。マスターサーバ用のマップを生成する場合は、`-m` を付けて NIS ドメイン名を指定します。

```shell
ellington# ypinit -m test-domain
Server Type: MASTER Domain: test-domain
Creating an YP server will require that you answer a few questions.
Questions will all be asked at the beginning of the procedure.
Do you want this procedure to quit on non-fatal errors? [y/n: n] n
Ok, please remember to go back and redo manually whatever fails.
If not, something might not work.
At this point, we have to construct a list of this domains YP servers.
rod.darktech.org is already known as master server.
Please continue to add any slave servers, one per line. When you are
done with the list, type a <control D>.
master server   :  ellington
next host to add:  coltrane
next host to add:  ^D
The current list of NIS servers looks like this:
ellington
coltrane
Is this correct?  [y/n: y] y

[..output from map generation..]

NIS Map update completed.
ellington has been setup as an YP master server without any errors.
```

これにより、`/var/yp/Makefile.dist` から `/var/yp/Makefile` が作成されます。既定では、このファイルは FreeBSD クライアントのみが存在する単一 NIS サーバ環境を想定しています。`test-domain` にはスレーブサーバがあるため、`/var/yp/Makefile` 内の次の行の先頭にコメント（`#`）を付けて無効化します。

```
NOPUSH = "True"
```

<a id="chapter-33-heading-20"></a>
#### 新しいユーザーの追加（Adding New Users）

新しいユーザーを作成するたびに、マスター NIS サーバへユーザーアカウントを追加し、NIS マップを再構築する必要があります。これを行うまでは、新しいユーザーは NIS マスター以外のどのマシンにもログインできません。たとえば、`test-domain` ドメインに新しいユーザー `jsmith` を追加するには、マスターサーバ上で次のコマンドを実行します。

```shell
# pw useradd jsmith
# cd /var/yp
# make test-domain
```

`pw useradd smith`（訳注: 直前の例の `jsmith`）の代わりに `adduser jsmith` を使ってユーザーを追加することもできます。

<a id="chapter-33-heading-21"></a>
### NIS スレーブサーバの構築（Setting up a NIS Slave Server）

NIS スレーブサーバを構築するには、スレーブサーバにログインし、マスターサーバのときと同様に `/etc/rc.conf` を編集します。すでにマスターサーバ上に存在するため、NIS マップを新規生成する必要はありません。スレーブサーバ上で `ypinit` を実行する際は、`-m`（master）ではなく `-s`（slave）を指定します。このオプションでは、次の例のようにドメイン名に加えて NIS マスターの名前も指定する必要があります。

```shell
coltrane# ypinit -s ellington test-domain

Server Type: SLAVE Domain: test-domain Master: ellington

Creating an YP server will require that you answer a few questions.
Questions will all be asked at the beginning of the procedure.

Do you want this procedure to quit on non-fatal errors? [y/n: n]  n

Ok, please remember to go back and redo manually whatever fails.
If not, something might not work.
There will be no further questions. The remainder of the procedure
should take a few minutes, to copy the databases from ellington.
Transferring netgroup...
ypxfr: Exiting: Map successfully transferred
Transferring netgroup.byuser...
ypxfr: Exiting: Map successfully transferred
Transferring netgroup.byhost...
ypxfr: Exiting: Map successfully transferred
Transferring master.passwd.byuid...
ypxfr: Exiting: Map successfully transferred
Transferring passwd.byuid...
ypxfr: Exiting: Map successfully transferred
Transferring passwd.byname...
ypxfr: Exiting: Map successfully transferred
Transferring group.bygid...
ypxfr: Exiting: Map successfully transferred
Transferring group.byname...
ypxfr: Exiting: Map successfully transferred
Transferring services.byname...
ypxfr: Exiting: Map successfully transferred
Transferring rpc.bynumber...
ypxfr: Exiting: Map successfully transferred
Transferring rpc.byname...
ypxfr: Exiting: Map successfully transferred
Transferring protocols.byname...
ypxfr: Exiting: Map successfully transferred
Transferring master.passwd.byname...
ypxfr: Exiting: Map successfully transferred
Transferring networks.byname...
ypxfr: Exiting: Map successfully transferred
Transferring networks.byaddr...
ypxfr: Exiting: Map successfully transferred
Transferring netid.byname...
ypxfr: Exiting: Map successfully transferred
Transferring hosts.byaddr...
ypxfr: Exiting: Map successfully transferred
Transferring protocols.bynumber...
ypxfr: Exiting: Map successfully transferred
Transferring ypservers...
ypxfr: Exiting: Map successfully transferred
Transferring hosts.byname...
ypxfr: Exiting: Map successfully transferred

coltrane has been setup as an YP slave server without any errors.
Remember to update map ypservers on ellington.
```

これにより、スレーブサーバ上に `/var/yp/test-domain` というディレクトリが作成され、NIS マスターサーバのマップの複製が格納されます。各スレーブサーバの `/etc/crontab` に次のエントリを追加しておくと、スレーブ側でマスターサーバのマップと定期的に同期させることができます。

```
20      *       *       *       *       root   /usr/libexec/ypxfr passwd.byname
21      *       *       *       *       root   /usr/libexec/ypxfr passwd.byuid
```

マスターサーバはマップ変更時にスレーブへ自動的にプッシュを試みるため、これらのエントリは必須ではありません。しかし、クライアントが正しいパスワード情報の取得をスレーブサーバに依存している場合があるため、パスワードマップの更新を頻繁に強制しておくことが推奨されます。マップ更新が毎回完了するとは限らない高負荷なネットワークでは、特に重要です。

設定を完了するには、スレーブサーバ上で `/etc/netstart` を実行して NIS サービスを起動します。

<a id="chapter-33-heading-22"></a>
### NIS クライアントの構築（Setting Up an NIS Client）

NIS クライアントは `ypbind(8)` を使って NIS サーバへバインドします。このデーモンはローカルネットワーク上に RPC 要求をブロードキャストします。要求にはクライアントに設定されたドメイン名が含まれます。同じドメインに属する NIS サーバがそのブロードキャストを受信すると `ypbind` へ応答し、`ypbind` はそのサーバのアドレスを記録します。利用可能なサーバが複数ある場合、クライアントは最初に応答したサーバのアドレスを使用し、以後のすべての NIS 要求をそのサーバへ送ります。クライアントは定期的にサーバへ ping を送って生存確認を行います。一定時間内に応答が得られない場合、`ypbind` はそのドメインを未バインド状態としてマークし、別のサーバを見つけるために再びブロードキャストを開始します。

FreeBSD マシンを NIS クライアントとして構成する手順は次のとおりです。

1. `/etc/rc.conf` を編集し、NIS ドメイン名を設定してネットワーク起動時に `ypbind(8)` を起動するため、次の行を追加します。

```
nisdomainname="test-domain"
nis_client_enable="YES"
```

2. NIS サーバから利用可能なすべてのパスワードエントリを取り込むため、`vipw` を使って `/etc/master.passwd` から 1 つを除いてすべてのユーザーアカウントを削除します。アカウントを削除する際は、少なくとも 1 つのローカルアカウントを残し、そのアカウントが `wheel` グループに所属しているようにしてください。NIS に問題が発生した場合でも、このローカルアカウントを使ってリモートログインし、スーパーユーザーになって問題を修復できます。編集を保存する前に、ファイルの末尾へ次の行を追加します。

```
+:::::::::
```

   この行により、NIS サーバのパスワードマップに有効なアカウントを持つすべてのユーザーに対して、クライアント上でもアカウントが提供されるようになります。この行を書き換えることで NIS クライアントの挙動をさまざまに制御できます。その 1 つの方法が [ネットグループの利用（Using Netgroups）](#network-netgroups) で説明されています。さらに詳しくは、O'Reilly Media 刊の書籍『`Managing NFS and NIS`』を参照してください。

3. NIS サーバから利用可能なすべてのグループエントリを取り込むため、`/etc/group` に次の行を追加します。

```
+:*::
```

すぐに NIS クライアントを起動するには、スーパーユーザーとして次のコマンドを実行します。

```shell
# /etc/netstart
# service ypbind start
```

これらの手順を完了したあと、クライアント上で `ypcat passwd` を実行すると、サーバ側の `passwd` マップが表示されるはずです。

<a id="chapter-33-heading-23"></a>
### NIS のセキュリティ（NIS Security）

RPC はブロードキャストベースのサービスであるため、同一ドメイン内で `ypbind` を動かしているシステムであれば誰でも NIS マップの内容を取得できてしまいます。不正なやり取りを防ぐため、`ypserv(8)` は「securenets」と呼ばれる機能に対応しており、アクセスを許可するホスト群を制限できます。既定では、`-p` で別パスを指定して `ypserv(8)` を起動しない限り、この情報は `/var/yp/securenets` に保存されます。このファイルには、空白で区切ったネットワーク指定とネットワークマスクの組を記述します。`"#"` で始まる行はコメントとみなされます。`securenets` の記述例は次のとおりです。

```
# allow connections from local host -- mandatory
127.0.0.1     255.255.255.255
# allow connections from any host
# on the 192.168.128.0 network
192.168.128.0 255.255.255.0
# allow connections from any host
# between 10.0.0.0 to 10.0.15.255
# this includes the machines in the testlab
10.0.0.0      255.255.240.0
```

`ypserv(8)` がこれらのルールのいずれかに一致するアドレスから要求を受け取ると、通常どおり要求を処理します。どのルールにも一致しないアドレスからの要求は無視され、警告メッセージがログに記録されます。`securenets` ファイルが存在しない場合、`ypserv` はあらゆるホストからの接続を許可します。

`securenets` の代わりに [TCP Wrapper](https://docs.freebsd.org/en/books/handbook/security/#tcpwrappers) を使ってアクセス制御を行うこともできます。いずれのアクセス制御機構も一定のセキュリティ向上にはなりますが、どちらも「IP スプーフィング」攻撃に対しては脆弱です。NIS 関連のトラフィックはすべてファイアウォールで遮断しておくべきです。

`securenets` を使用しているサーバは、古い TCP/IP 実装を持つ正規の NIS クライアントに対して応答できなくなる場合があります。そうした実装の中には、ブロードキャスト時にホストビットをすべて 0 にしたり、ブロードキャストアドレスの計算時にサブネットマスクを無視したりするものがあります。クライアント設定の変更で解決できる場合もありますが、そうでない場合はそのクライアントシステムを退役させるか、`securenets` の使用を断念せざるを得なくなります。

TCP Wrapper を使用すると NIS サーバの遅延（レイテンシ）が増加します。特に低速な NIS サーバと高負荷なネットワーク環境では、この追加遅延によってクライアントプログラムがタイムアウトするおそれがあります。1 台以上のクライアントで遅延が問題になる場合は、それらのクライアントを NIS スレーブサーバへ変更し、自分自身へバインドするように構成してください。

<a id="chapter-33-heading-24"></a>
#### 一部ユーザーのログイン禁止（Barring Some Users）

次の例では、`basie` システムが NIS ドメイン内の教員用ワークステーションであるとします。マスター NIS サーバの `passwd` マップには教員と学生の両方のアカウントが含まれています。この節では、このシステムで教員のログインを許可しつつ、学生のログインを拒否する方法を示します。

NIS データベースに登録されているユーザーであっても、特定のユーザーがシステムへログインできないようにするには、クライアント上の `/etc/master.passwd` の末尾付近に `vipw` を使って `-username`（`username` はログインを禁止するユーザー名）に適切な数のコロンを付けた行を追加します。ブロック対象ユーザーの行は、NIS ユーザーを許可する `+` 行よりも*前*に配置する必要があります。次の例では、`basie` への `bill` のログインを禁止しています。

```shell
basie# cat /etc/master.passwd
root:[password]:0:0::0:0:The super-user:/root:/bin/csh
toor:[password]:0:0::0:0:The other super-user:/root:/bin/sh
daemon:*:1:1::0:0:Owner of many system processes:/root:/usr/sbin/nologin
operator:*:2:5::0:0:System &:/:/usr/sbin/nologin
bin:*:3:7::0:0:Binaries Commands and Source,,,:/:/usr/sbin/nologin
tty:*:4:65533::0:0:Tty Sandbox:/:/usr/sbin/nologin
kmem:*:5:65533::0:0:KMem Sandbox:/:/usr/sbin/nologin
games:*:7:13::0:0:Games pseudo-user:/usr/games:/usr/sbin/nologin
news:*:8:8::0:0:News Subsystem:/:/usr/sbin/nologin
man:*:9:9::0:0:Mister Man Pages:/usr/share/man:/usr/sbin/nologin
bind:*:53:53::0:0:Bind Sandbox:/:/usr/sbin/nologin
uucp:*:66:66::0:0:UUCP pseudo-user:/var/spool/uucppublic:/usr/libexec/uucp/uucico
xten:*:67:67::0:0:X-10 daemon:/usr/local/xten:/usr/sbin/nologin
pop:*:68:6::0:0:Post Office Owner:/nonexistent:/usr/sbin/nologin
nobody:*:65534:65534::0:0:Unprivileged user:/nonexistent:/usr/sbin/nologin
-bill:::::::::
+:::::::::

basie#
```

<a id="network-netgroups"></a>
### ネットグループの利用（Using Netgroups）

システムごとに特定ユーザーのログインを個別に禁止する方法は、大規模ネットワークでは拡張性がなく、NIS 最大の利点である*一元*管理の恩恵をすぐに失ってしまいます。

ネットグループ（Netgroups）は、数百人ものユーザーと数百台ものマシンを抱える大規模で複雑なネットワークを扱うために開発されました。使い方は UNIX® のグループに似ていますが、数値 ID がない点と、ユーザーアカウントだけでなく他のネットグループも含めてネットグループを定義できる点が主な違いです。

本章の例を拡張し、表 28.2 と表 28.3 に示すユーザーとシステムを NIS ドメインへ追加してみます。

**表: 追加ユーザー**

| ユーザー名 | 説明 |
|---|---|
| `alpha`, `beta` | IT 部門の社員 |
| `charlie`, `delta` | IT 部門の研修生 |
| `echo`, `foxtrott`, `golf`, ... | 一般社員 |
| `able`, `baker`, ... | インターン |

**表: 追加システム**

| マシン名 | 説明 |
|---|---|
| `war`, `death`, `famine`, `pollution` | IT 部門の社員のみログインが許可されるサーバ。 |
| `pride`, `greed`, `envy`, `wrath`, `lust`, `sloth` | IT 部門のすべてのメンバーにログインが許可されるサーバ。 |
| `one`, `two`, `three`, `four`, ... | 一般社員が使用する通常のワークステーション。 |
| `trashcan` | 重要なデータが入っていない非常に古いマシン。インターンも利用可能。 |

ネットグループを使ってこの構成を設定する場合、各ユーザーを 1 つ以上のネットグループに割り当て、ネットグループのメンバー単位でログインを許可または禁止します。新しいマシンを追加するときはすべてのネットグループに対してログイン制限を定義し、新しいユーザーを追加するときは 1 つ以上のネットグループへアカウントを追加します。NIS の構成を慎重に設計しておけば、マシンへのアクセス許可や拒否を切り替える際に変更が必要なのは中央の設定ファイル 1 つだけになります。

最初の手順は、NIS の `netgroup` マップの初期化です。FreeBSD ではこのマップは既定で作成されません。NIS マスターサーバ上でエディタを使い、`/var/yp/netgroup` という名前のマップを作成します。

次の例では、IT 部門の社員、IT 部門の研修生、一般社員、インターンを表す 4 つのネットグループを作成しています。

```
IT_EMP  (,alpha,test-domain)    (,beta,test-domain)
IT_APP  (,charlie,test-domain)  (,delta,test-domain)
USERS   (,echo,test-domain)     (,foxtrott,test-domain) \
        (,golf,test-domain)
INTERNS (,able,test-domain)     (,baker,test-domain)
```

各エントリが 1 つのネットグループを定義します。エントリの 1 列目がネットグループ名です。各丸括弧の組は、1 人以上のユーザーの組または別のネットグループの名前を表します。ユーザーを指定する場合、括弧内のカンマで区切られた 3 つのフィールドは次の意味を持ちます。

1. 他のフィールドで表されるユーザーが有効となるホスト名。ホスト名を指定しない場合、そのエントリはすべてのホストで有効になります。
2. このネットグループに所属するアカウント名。
3. そのアカウントが属する NIS ドメイン。他の NIS ドメインからネットグループへアカウントを取り込むこともできます。

1 つのネットグループに複数のユーザーを含める場合は、各ユーザーを空白文字で区切ります。また、各フィールドにはワイルドカードも使用できます。詳細は `netgroup(5)` を参照してください。

ネットグループ名には 8 文字を超える名前を使わないでください。名前は大文字・小文字を区別するため、ネットグループ名にすべて大文字を使うと、ユーザー名・マシン名・ネットグループ名を容易に見分けられます。

FreeBSD 以外の NIS クライアントの一部は、16 件以上のエントリを含むネットグループを処理できません。この制限は、15 ユーザー以下のサブネットグループを複数作成し、それらをまとめた本来のネットグループを次のように定義することで回避できます。

```
BIGGRP1  (,joe1,domain)  (,joe2,domain)  (,joe3,domain) [...]
BIGGRP2  (,joe16,domain)  (,joe17,domain) [...]
BIGGRP3  (,joe31,domain)  (,joe32,domain)
BIGGROUP  BIGGRP1 BIGGRP2 BIGGRP3
```

1 つのネットグループに 225（15 × 15）人を超えるユーザーがいる場合は、この階層化を繰り返してください。

新しい NIS マップを有効化して配布するには、次のコマンドを実行します。

```shell
ellington# cd /var/yp
ellington# make
```

これにより、`netgroup`、`netgroup.byhost`、`netgroup.byuser` の 3 つの NIS マップが生成されます。新しい NIS マップが利用可能かどうかを確認するには、`ypcat(1)` のマップキー表示オプションを使います。

```shell
ellington% ypcat -k netgroup
ellington% ypcat -k netgroup.byhost
ellington% ypcat -k netgroup.byuser
```

1 つ目のコマンドの出力は `/var/yp/netgroup` の内容と似たものになります。2 つ目のコマンドはホスト指定付きのネットグループを作成した場合にのみ出力を返します。3 つ目のコマンドは特定ユーザーが属するネットグループの一覧を取得する際に使います。

クライアントを設定するには、`vipw(8)` を使ってネットグループ名を指定します。たとえば `war` という名前のサーバでは、次の行を

```
+:::::::::
```

次のように置き換えます。

```
+@IT_EMP:::::::::
```

これにより、ネットグループ `IT_EMP` で定義されたユーザーのみがこのシステムのパスワードデータベースへ取り込まれ、それらのユーザーだけがこのシステムへログインできるようになります。

ただし、この設定はシェルの `~` 展開や、ユーザー名と数値ユーザー ID を相互変換するすべてのルーチンにも影響します。つまり、`cd ~user` が動かなくなり、`ls -l` はユーザー名の代わりに数値 ID を表示し、`find . -user joe -print` は `No such user` というメッセージで失敗します。これを防ぐには、サーバへのログインは許可しないまま、すべてのユーザーエントリだけを取り込むようにします。それには次の行を追加します。

```
+:::::::::/usr/sbin/nologin
```

この行により、クライアントはすべてのエントリを取り込みつつ、それらのエントリのログインシェルを `/usr/sbin/nologin` に置き換えるようになります。

この追加行は必ず `+@IT_EMP:::::::::` の*後ろ*に配置してください。さもないと、NIS から取り込まれたすべてのユーザーアカウントのログインシェルが `/usr/sbin/nologin` になり、誰もシステムへログインできなくなってしまいます。

重要度の低いサーバを設定する場合は、従来の `+:::::::::` を次の行に置き換えます。

```
+@IT_EMP:::::::::
+@IT_APP:::::::::
+:::::::::/usr/sbin/nologin
```

ワークステーションに対応する記述は次のようになります。

```
+@IT_EMP:::::::::
+@USERS:::::::::
+:::::::::/usr/sbin/nologin
```

NIS は他のネットグループから新しいネットグループを作成することにも対応しており、ユーザーアクセスに関するポリシーを変更する際に便利です。1 つの方法として、役割ベースのネットグループを作るやり方があります。たとえば、重要なサーバのログイン制限を定義する `BIGSRV`、重要度の低いサーバ向けの `SMALLSRV`、ワークステーション向けの `USERBOX` というネットグループを作成します。それぞれのネットグループには、それらのマシンへログインを許可するネットグループを含めます。NIS の `netgroup` マップに追加する新しいエントリは次のようになります。

```
BIGSRV    IT_EMP  IT_APP
SMALLSRV  IT_EMP  IT_APP  ITINTERN
USERBOX   IT_EMP  ITINTERN USERS
```

このログイン制限の定義方法は、まったく同じ制限を持つマシングループを定義できる場合にはうまく機能します。しかし残念ながら、それは例外的なケースであり一般的ではありません。多くの場合、マシン単位でログイン制限を定義できる必要があります。

ポリシー変更に対応するもう 1 つの方法が、マシン固有のネットグループ定義です。この方法では、各システムの `/etc/master.passwd` に `+` で始まる行を 2 行記述します。1 行目でそのマシンへのログインを許可するアカウントを含むネットグループを追加し、2 行目でそれ以外のすべてのアカウントをシェル `/usr/sbin/nologin` として追加します。ネットグループ名にはホスト名を「すべて大文字（ALL-CAPS）」にしたものを使うことを推奨します。

```
+@BOXNAME:::::::::
+:::::::::/usr/sbin/nologin
```

すべてのマシンでこの設定を完了すれば、ローカルの `/etc/master.passwd` を二度と編集する必要はなくなります。以降の変更はすべて NIS マップの編集だけで処理できます。この構成における `netgroup` マップの例を次に示します。

```
# Define groups of users first
IT_EMP    (,alpha,test-domain)    (,beta,test-domain)
IT_APP    (,charlie,test-domain)  (,delta,test-domain)
DEPT1     (,echo,test-domain)     (,foxtrott,test-domain)
DEPT2     (,golf,test-domain)     (,hotel,test-domain)
DEPT3     (,india,test-domain)    (,juliet,test-domain)
ITINTERN  (,kilo,test-domain)     (,lima,test-domain)
D_INTERNS (,able,test-domain)     (,baker,test-domain)
#
# Now, define some groups based on roles
USERS     DEPT1   DEPT2     DEPT3
BIGSRV    IT_EMP  IT_APP
SMALLSRV  IT_EMP  IT_APP    ITINTERN
USERBOX   IT_EMP  ITINTERN  USERS
#
# And a groups for a special tasks
# Allow echo and golf to access our anti-virus-machine
SECURITY  IT_EMP  (,echo,test-domain)  (,golf,test-domain)
#
# machine-based netgroups
# Our main servers
WAR       BIGSRV
FAMINE    BIGSRV
# User india needs access to this server
POLLUTION  BIGSRV  (,india,test-domain)
#
# This one is really important and needs more access restrictions
DEATH     IT_EMP
#
# The anti-virus-machine mentioned above
ONE       SECURITY
#
# Restrict a machine to a single user
TWO       (,hotel,test-domain)
# [...more groups to follow]
```

マシンベースのネットグループを使うのが常に得策とは限りません。数十台から数百台のシステムを展開する場合は、NIS マップのサイズを妥当な範囲に収めるため、マシンベースではなく役割ベースのネットグループを使うほうがよい場合もあります。

<a id="chapter-33-heading-26"></a>
### パスワード形式（Password Formats）

NIS では、NIS ドメイン内のすべてのホストがパスワード暗号化に同じ形式を使用している必要があります。NIS クライアント上で認証に問題が生じる場合、パスワード形式が異なっていることが原因かもしれません。異なる OS が混在するネットワークでは、すべての OS が対応している形式にする必要があり、最小公倍数の標準は DES となります。

サーバやクライアントがどの形式を使っているかを確認するには、`/etc/login.conf` の次の箇所を参照します。

```
default:\
	:passwd_format=des:\
	[Further entries elided]
```

この例では、システムはパスワードハッシュに DES 形式を使用しています。他に指定できる値には、Blowfish の `blf`、MD5 の `md5`、SHA-256 と SHA-512 の `sha256` および `sha512` があります。詳細やそのシステムで利用可能な最新の形式一覧については、`crypt(3)` のマニュアルページを参照してください。

> **訳注**: 上記の `passwd_format=des` は固定原文に含まれる過去の例です。現在の FreeBSD では、より強固なハッシュ形式（`sha512` 等）が既定として用いられます。利用可能な形式は対象版の `crypt(3)` および `login.conf(5)` を確認してください。

NIS ドメインで使用している形式に合わせるためホスト側の形式を変更した場合は、変更を保存したあとにログイン機能データベース（login capability database）を再構築する必要があります。

```shell
# cap_mkdb /etc/login.conf
```

> **注記（NOTE）**: 既存のユーザーアカウントのパスワード形式は、ログイン機能データベースを再構築した*あと*で各ユーザーがパスワードを変更するまで更新されません。

<a id="network-ldap"></a>
## Lightweight Directory Access Protocol（LDAP）

Lightweight Directory Access Protocol（LDAP）は、分散ディレクトリ情報サービスを使ってオブジェクトの参照、変更、認証を行うためのアプリケーション層プロトコルです。複数階層の均質な情報を格納する電話帳や台帳のようなものだと考えるとわかりやすいでしょう。Active Directory や OpenLDAP のネットワークで利用されており、ユーザーは 1 つのアカウントを使って複数階層の社内情報へアクセスできます。たとえば、メール認証、社員連絡先の取得、社内 Web サイトの認証をすべて LDAP サーバのデータベース上の単一ユーザーアカウントで賄うことができます。

この節では、FreeBSD システム上で LDAP サーバを構成するためのクイックスタートガイドを提供します。管理者がすでに設計計画（格納する情報の種類、その情報の用途、どのユーザーにアクセス権を与えるか、不正アクセスからどう保護するか）を策定済みであることを前提としています。

<a id="chapter-33-heading-28"></a>
### LDAP の用語と構造（LDAP Terminology and Structure）

LDAP では、設定を始める前に理解しておくべきいくつかの用語があります。すべてのディレクトリエントリは*属性（attributes）*の集まりで構成されます。これらの属性セットにはそれぞれ、*識別名（Distinguished Name: DN）*と呼ばれる一意の識別子が含まれます。DN は通常、コモンネームや*相対識別名（Relative Distinguished Name: RDN）*など、他のいくつかの属性を組み合わせて作られます。ディレクトリに絶対パスと相対パスがあるのと同様に、DN を絶対パス、RDN を相対パスとみなすことができます。

LDAP エントリの例を次に示します。この例では、指定したユーザーアカウント（`uid`）、組織単位（`ou`）、組織（`o`）に一致するエントリを検索しています。

```shell
% ldapsearch -xb "uid=trhodes,ou=users,o=example.com"
# extended LDIF
#
# LDAPv3
# base <uid=trhodes,ou=users,o=example.com> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# trhodes, users, example.com
dn: uid=trhodes,ou=users,o=example.com
mail: trhodes@example.com
cn: Tom Rhodes
uid: trhodes
telephoneNumber: (123) 456-7890

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

このエントリ例では、`dn`、`mail`、`cn`、`uid`、`telephoneNumber` の各属性の値が示されています。ここでは `cn` 属性が RDN になります。

LDAP とその用語についての詳細は、[OpenLDAP Admin Guide](http://www.openldap.org/doc/admin24/intro.html) を参照してください。

<a id="ldap-config"></a>
### LDAP サーバの設定（Configuring an LDAP Server）

FreeBSD には組み込みの LDAP サーバは含まれていません。まず、`net/openldap-server` のパッケージまたは Port をインストールして設定を始めます。

```shell
# pkg install openldap-server
```

[パッケージ](https://docs.freebsd.org/en/articles/linux-users/#software)では、あらかじめ多くの既定オプションが有効になっています。有効なオプションは `pkg info openldap-server` で確認してください。たとえば SQL サポートが必要など既定オプションで不十分な場合は、適切な [Ports の利用方法](04-ports.md#ports-using) に従って Port から再コンパイルすることを検討してください。

インストールすると、データを格納するための `/var/db/openldap-data` ディレクトリが作成されます。証明書を格納するディレクトリは手動で作成する必要があります。

```shell
# mkdir /usr/local/etc/openldap/private
```

次の段階では認証局（Certificate Authority）を設定します。以下のコマンドは `/usr/local/etc/openldap/private` ディレクトリ内で実行する必要があります。ファイルのパーミッションを厳しく制限し、一般ユーザーがこれらのファイルへアクセスできないようにするため、この点は重要です。証明書やパラメータの詳細は [OpenSSL](https://docs.freebsd.org/en/books/handbook/security/#openssl) を参照してください。認証局を作成するには、次のコマンドを実行してプロンプトに従って入力します。

```shell
# openssl req -days 365 -nodes -new -x509 -keyout ca.key -out ../ca.crt
```

プロンプトへの入力内容は、`Common Name` を*除き*一般的な値で構いません。`Common Name` はシステムのホスト名とは*異なる*値にする必要があります。自己署名証明書にする場合は、ホスト名の先頭に認証局（Certificate Authority）を表す `CA` を付けてください。

次の作業は、証明書署名要求（CSR）と秘密鍵の作成です。次のコマンドを実行してプロンプトに入力します。

```shell
# openssl req -days 365 -nodes -new -keyout server.key -out server.csr
```

証明書生成の過程では、`Common Name` 属性を正しく設定してください。有効な証明書として使用するには、証明書署名要求に認証局で署名する必要があります。

```shell
# openssl x509 -req -days 365 -in server.csr -out ../server.crt -CA ../ca.crt -CAkey ca.key -CAcreateserial
```

証明書生成の最後の工程は、クライアント証明書の生成と署名です。

```shell
# openssl req -days 365 -nodes -new -keyout client.key -out client.csr
# openssl x509 -req -days 3650 -in client.csr -out ../client.crt -CA ../ca.crt -CAkey ca.key
```

プロンプトが表示された際は、先ほどと同じ `Common Name` 属性を使用してください。完了したら、ここまでのコマンドによって合計 8 個の新しいファイルが生成されていることを確認します。

OpenLDAP サーバを動かすデーモンは `slapd` です。設定は `slapd.ldif` を通じて行います（古い `slapd.conf` は OpenLDAP によって非推奨となりました）。

`slapd.ldif` の[設定例](http://www.openldap.org/doc/admin24/slapdconf2.html)はオンラインで公開されているほか、`/usr/local/etc/openldap/slapd.ldif.sample` にもあります。各オプションは `slapd-config(5)` に記載されています。`slapd.ldif` の各セクションは、他の LDAP 属性セットと同様に DN によって一意に識別されます。`dn:` 行から目的のセクション末尾までの間に空行を入れないよう注意してください。次の例では、安全な通信路を実装するために TLS を使用します。最初のセクションはグローバル設定を表します。

```
#
# See slapd-config(5) for details on configuration options.
# This file should NOT be world readable.
#
dn: cn=config
objectClass: olcGlobal
cn: config
#
#
# Define global ACLs to disable default read access.
#
olcArgsFile: /var/run/openldap/slapd.args
olcPidFile: /var/run/openldap/slapd.pid
olcTLSCertificateFile: /usr/local/etc/openldap/server.crt
olcTLSCertificateKeyFile: /usr/local/etc/openldap/private/server.key
olcTLSCACertificateFile: /usr/local/etc/openldap/ca.crt
#olcTLSCipherSuite: HIGH
olcTLSProtocolMin: 3.1
olcTLSVerifyClient: never
```

ここには認証局証明書、サーバ証明書、サーバ秘密鍵ファイルを指定する必要があります。暗号スイートの選択はクライアント側に任せ、`olcTLSCipherSuite` オプションは省略することが推奨されます（`openssl` 以外の TLS クライアントと非互換になるため）。`olcTLSProtocolMin` オプションはサーバが要求する最小セキュリティレベルを指定するもので、設定が推奨されます。サーバ側の検証は必須ですが、クライアント証明書検証は必須ではないため `olcTLSVerifyClient: never` としています。

2 つ目のセクションはバックエンドモジュールに関する設定で、次のように構成できます。

```
#
# Load dynamic backend modules:
#
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulepath:	/usr/local/libexec/openldap
olcModuleload:	back_mdb.la
#olcModuleload:	back_bdb.la
#olcModuleload:	back_hdb.la
#olcModuleload:	back_ldap.la
#olcModuleload:	back_passwd.la
#olcModuleload:	back_shell.la
```

3 つ目のセクションは、データベースが使用する必須の `ldif` スキーマを読み込むためのもので、これらは不可欠です。

```
dn: cn=schema,cn=config
objectClass: olcSchemaConfig
cn: schema

include: file:///usr/local/etc/openldap/schema/core.ldif
include: file:///usr/local/etc/openldap/schema/cosine.ldif
include: file:///usr/local/etc/openldap/schema/inetorgperson.ldif
include: file:///usr/local/etc/openldap/schema/nis.ldif
```

続いて、フロントエンドの設定セクションです。

```
# Frontend settings
#
dn: olcDatabase={-1}frontend,cn=config
objectClass: olcDatabaseConfig
objectClass: olcFrontendConfig
olcDatabase: {-1}frontend
olcAccess: to * by * read
#
# Sample global access control policy:
#	Root DSE: allow anyone to read it
#	Subschema (sub)entry DSE: allow anyone to read it
#	Other DSEs:
#		Allow self write access
#		Allow authenticated users read access
#		Allow anonymous users to authenticate
#
#olcAccess: to dn.base="" by * read
#olcAccess: to dn.base="cn=Subschema" by * read
#olcAccess: to *
#	by self write
#	by users read
#	by anonymous auth
#
# if no access controls are present, the default policy
# allows anyone and everyone to read anything but restricts
# updates to rootdn.  (e.g., "access to * by * read")
#
# rootdn can always read and write EVERYTHING!
#
olcPasswordHash: {SSHA}
# {SSHA} is already the default for olcPasswordHash
```

もう 1 つのセクションは*設定バックエンド（configuration backend）*用であり、あとからグローバルなスーパーユーザーとして OpenLDAP サーバ設定へアクセスするための唯一の手掛かりになります。

```
dn: olcDatabase={0}config,cn=config
objectClass: olcDatabaseConfig
olcDatabase: {0}config
olcAccess: to * by * none
olcRootPW: {SSHA}iae+lrQZILpiUdf16Z9KmDmSwT77Dj4U
```

既定の管理者ユーザー名は `cn=config` です。シェルで `slappasswd` を実行してパスワードを決め、そのハッシュ値を `olcRootPW` に指定してください。`slapd.ldif` をインポートする前にこのオプションを指定しておかないと、あとから誰も*グローバル設定*セクションを変更できなくなります。

最後のセクションはデータベースバックエンドに関する設定です。

```
#######################################################################
# LMDB database definitions
#######################################################################
#
dn: olcDatabase=mdb,cn=config
objectClass: olcDatabaseConfig
objectClass: olcMdbConfig
olcDatabase: mdb
olcDbMaxSize: 1073741824
olcSuffix: dc=domain,dc=example
olcRootDN: cn=mdbadmin,dc=domain,dc=example
# Cleartext passwords, especially for the rootdn, should
# be avoided.  See slappasswd(8) and slapd-config(5) for details.
# Use of strong authentication encouraged.
olcRootPW: {SSHA}X2wHvIWDk6G76CQyCMS1vDCvtICWgn0+
# The database directory MUST exist prior to running slapd AND
# should only be accessible by the slapd and slap tools.
# Mode 700 recommended.
olcDbDirectory:	/var/db/openldap-data
# Indices to maintain
olcDbIndex: objectClass eq
```

このデータベースが LDAP ディレクトリの*実際の内容*を保持します。`mdb` 以外の種類も利用できます。ここでは（グローバル管理者とは別の）このデータベース専用のスーパーユーザーを、`olcRootDN` に（任意の）ユーザー名、`olcRootPW` にパスワードハッシュを指定して設定します。先ほどと同様に `slappasswd` を使用できます。

[このリポジトリ](http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=tree;f=tests/data/regressions/its8444;h=8a5e808e63b0de3d2bdaf2cf34fecca8577ca7fd;hb=HEAD) には `slapd.ldif` の 4 つの例が収録されています。既存の `slapd.conf` を `slapd.ldif` へ変換するには、[こちらのページ](http://www.openldap.org/doc/admin24/slapdconf2.html)を参照してください（ただし、不要なオプションが混入する場合がある点に注意してください）。

設定が完了したら、`slapd.ldif` を空のディレクトリに配置する必要があります。次のようにディレクトリを作成することを推奨します。

```shell
# mkdir /usr/local/etc/openldap/slapd.d/
```

設定データベースをインポートします。

```shell
# /usr/local/sbin/slapadd -n0 -F /usr/local/etc/openldap/slapd.d/ -l /usr/local/etc/openldap/slapd.ldif
```

`slapd` デーモンを起動します。

```shell
# /usr/local/libexec/slapd -F /usr/local/etc/openldap/slapd.d/
```

`slapd(8)` に記載されているとおり、デバッグには `-d` オプションを使用できます。サーバが起動して動作していることを確認するには、次のように実行します。

```shell
# ldapsearch -x -b '' -s base '(objectclass=*)' namingContexts
# extended LDIF
#
# LDAPv3
# base <> with scope baseObject
# filter: (objectclass=*)
# requesting: namingContexts
#

#
dn:
namingContexts: dc=domain,dc=example

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

まだサーバ証明書が信頼された状態になっていません。これまでに信頼設定を行っていない場合は、次の手順に従ってください。OpenSSL パッケージまたは Port をインストールします。

```shell
# pkg install openssl
```

`ca.crt` が保存されているディレクトリ（この例では `/usr/local/etc/openldap`）で次を実行します。

```shell
# c_rehash .
```

これで、CA 証明書とサーバ証明書の双方がそれぞれの役割として正しく認識されるようになります。これを確認するには、`server.crt` があるディレクトリから次のコマンドを実行します。

```shell
# openssl verify -verbose -CApath . server.crt
```

すでに `slapd` が動作していた場合は再起動してください。`/usr/local/etc/rc.d/slapd` に記載されているとおり、起動時に `slapd` を正しく動作させるには `/etc/rc.conf` に次の行を追加する必要があります。

```
slapd_enable="YES"
slapd_flags='-h "ldapi://%2fvar%2frun%2fopenldap%2fldapi/ ldap://0.0.0.0/"'
slapd_sockets="/var/run/openldap/ldapi"
slapd_cn_config="YES"
```

`slapd` は起動時のデバッグ出力を行いません。問題調査には `/var/log/debug.log`、`dmesg -a`、`/var/log/messages` を確認してください。

次の例では、まだ空の状態の `domain.example` LDAP データベースに、グループ `team` とユーザー `john` を追加します。まず `domain.ldif` ファイルを作成します。

```shell
# cat domain.ldif
dn: dc=domain,dc=example
objectClass: dcObject
objectClass: organization
o: domain.example
dc: domain

dn: ou=groups,dc=domain,dc=example
objectClass: top
objectClass: organizationalunit
ou: groups

dn: ou=users,dc=domain,dc=example
objectClass: top
objectClass: organizationalunit
ou: users

dn: cn=team,ou=groups,dc=domain,dc=example
objectClass: top
objectClass: posixGroup
cn: team
gidNumber: 10001

dn: uid=john,ou=users,dc=domain,dc=example
objectClass: top
objectClass: account
objectClass: posixAccount
objectClass: shadowAccount
cn: John McUser
uid: john
uidNumber: 10001
gidNumber: 10001
homeDirectory: /home/john/
loginShell: /usr/bin/bash
userPassword: secret
```

詳細は OpenLDAP のドキュメントを参照してください。`userPassword` 内の平文パスワード `secret` は、`slappasswd` を使ってハッシュ値に置き換えてください。`loginShell` に指定したパスは、`john` にログインを許可するすべてのシステム上に存在している必要があります。最後に、`mdb` 管理者を使ってデータベースを更新します。

```shell
# ldapadd -W -D "cn=mdbadmin,dc=domain,dc=example" -f domain.ldif
```

*グローバル設定*セクションへの変更は、グローバルスーパーユーザーのみが実行できます。たとえば、最初に `olcTLSCipherSuite: HIGH:MEDIUM:SSLv3` オプションを指定していて、いま削除したいとします。まず、次の内容を含むファイルを作成します。

```shell
# cat global_mod
dn: cn=config
changetype: modify
delete: olcTLSCipherSuite
```

続いて、変更を適用します。

```shell
# ldapmodify -f global_mod -x -D "cn=config" -W
```

パスワードの入力を求められたら、*設定バックエンド*の節で決めたパスワードを入力します。ユーザー名は不要です。ここでの `cn=config` は、変更対象データベースセクションの DN を表しています。あるいは、データベースの 1 行だけを削除するには `ldapmodify` を、エントリ全体を削除するには `ldapdelete` を使用できます。

何か問題が起きた場合や、グローバルスーパーユーザーが設定バックエンドへアクセスできなくなった場合は、設定全体を削除して書き直すことも可能です。

```shell
# rm -rf /usr/local/etc/openldap/slapd.d/
```

そのあとで `slapd.ldif` を編集し、再度インポートできます。ただし、この手順は他に解決策がない場合にのみ行ってください。

以上はサーバ側のみの設定です。同じマシン上に、これとは独立した設定を持つ LDAP クライアントを同居させることもできます。

<a id="network-dhcp"></a>
## Dynamic Host Configuration Protocol（DHCP）

Dynamic Host Configuration Protocol（DHCP）は、システムがネットワークへ接続する際に、そのネットワークで通信するために必要なアドレス情報を自動割り当てするためのプロトコルです。FreeBSD には OpenBSD 版の `dhclient` が含まれており、クライアント側でアドレス情報を取得する際に使用されます。FreeBSD 標準では DHCP サーバはインストールされませんが、FreeBSD Ports Collection にはいくつかの DHCP サーバが収録されています。DHCP プロトコルの詳細な仕様は [RFC 2131](http://www.freesoft.org/CIE/RFC/2131/) に記載されています。また、[isc.org/downloads/dhcp/](http://www.isc.org/downloads/dhcp/) にも関連資料があります。

この節では、組み込みの DHCP クライアントの使い方を説明したあと、DHCP サーバのインストールと設定方法を解説します。

> **注記（NOTE）**: FreeBSD では、DHCP サーバと DHCP クライアントの両方で `bpf(4)` デバイスが必要です。このデバイスは FreeBSD に標準で含まれる `GENERIC` カーネルに組み込まれています。カスタムカーネルを構築する場合は、DHCP を利用するならこのデバイスを残しておく必要があります。
>
> なお、`bpf` を有効にすると、特権ユーザーがそのシステム上でネットワークパケットスニファを実行できるようになる点にも留意してください。

<a id="chapter-33-heading-31"></a>
### DHCP クライアントの設定（Configuring a DHCP Client）

DHCP クライアントのサポートは FreeBSD インストーラに組み込まれているため、新規インストールしたシステムが既存の DHCP サーバからネットワークのアドレス情報を自動取得するように設定するのは簡単です。ネットワーク設定の例については、[アカウント、タイムゾーン、サービス、ハードニング](02-bsdinstall.md#bsdinstall-post)を参照してください。

クライアントマシン上で `dhclient` が実行されると、設定情報を求める要求のブロードキャストを開始します。既定では、この要求には UDP ポート 68 が使われます。サーバは UDP ポート 67 で応答し、IP アドレスに加えてサブネットマスク、デフォルトゲートウェイ、DNS サーバアドレスなどの関連ネットワーク情報をクライアントへ渡します。この情報は DHCP「リース（lease）」の形で提供され、設定可能な有効期限を持ちます。これにより、ネットワークから切り離されたクライアントの古い IP アドレスを自動的に再利用できるようになります。DHCP クライアントはサーバから非常に多くの種類の情報を取得できます。網羅的な一覧は `dhcp-options(5)` を参照してください。

既定では、FreeBSD システムの起動時に DHCP クライアントはバックグラウンド、すなわち*非同期（asynchronously）*で動作します。DHCP の処理が完了するのを待たずに他の起動スクリプトが実行されるため、システム起動が高速になります。

バックグラウンドの DHCP は、DHCP サーバがクライアントの要求へ素早く応答する環境ではうまく機能します。しかし、環境によっては DHCP の完了に長い時間がかかる場合があります。DHCP によるネットワークアドレス情報の割り当てが終わる前にネットワークサービスが起動しようとすると、それらのサービスは失敗してしまいます。DHCP を*同期（synchronous）*モードで使うと、DHCP の設定が完了するまで起動処理を一時停止するため、この問題を防げます。

バックグラウンド（非同期）モードを設定するには、`/etc/rc.conf` に次の行を記述します。

```
ifconfig_fxp0="DHCP"
```

インストール時に DHCP を使うよう設定した場合は、この行がすでに存在していることがあります。これらの例における *fxp0* は、[ネットワークインターフェイスカードの設定](https://docs.freebsd.org/en/books/handbook/network/#config-network-setup)で説明されているとおり、動的設定を行いたいインターフェイス名に置き換えてください（訳注: 原文の相互参照先は `config` 章になっていますが、上流で独立した `network` 章へ移設されており、本リポジトリでは未翻訳のため公式英語版へリンクしています）。

代わりに同期モードを使い、DHCP が完了するまで起動時に待機させるには、`"SYNCDHCP"` を指定します。

```
ifconfig_fxp0="SYNCDHCP"
```

このほかにもクライアント用オプションがあります。詳細は `rc.conf(5)` で `dhclient` を検索してください。

DHCP クライアントは次のファイルを使用します。

* `/etc/dhclient.conf`

  `dhclient` が使用する設定ファイルです。通常はほとんどのクライアントにとって既定値が適切なため、コメントのみが書かれています。この設定ファイルについては `dhclient.conf(5)` で解説されています。

* `/sbin/dhclient`

  コマンド自体の詳細は `dhclient(8)` を参照してください。

* `/sbin/dhclient-script`

  FreeBSD 固有の DHCP クライアント設定スクリプトです。`dhclient-script(8)` で解説されていますが、通常はユーザーが変更しなくても正しく動作します。

* `/var/db/dhclient.leases.interface`

  DHCP クライアントは有効なリースのデータベースをこのファイルにログ形式で保持します。詳細は `dhclient.leases(5)` を参照してください。

<a id="network-dhcp-server"></a>
### DHCP サーバのインストールと設定（Installing and Configuring a DHCP Server）

この節では、Internet Systems Consortium（ISC）による DHCP サーバ実装を使って FreeBSD システムを DHCP サーバとして構成する方法を説明します。この実装とドキュメントは、`net/isc-dhcp44-server` のパッケージまたは Port を使ってインストールできます。

`net/isc-dhcp44-server` をインストールすると、サンプル設定ファイルが配置されます。`/usr/local/etc/dhcpd.conf.example` を `/usr/local/etc/dhcpd.conf` へコピーし、コピーした新しいファイルを編集してください。

設定ファイルは、DHCP クライアントへ提供する情報を定義するサブネット宣言およびホスト宣言で構成されます。たとえば、次の記述では各項目を設定しています。

```
option domain-name "example.org";
option domain-name-servers ns1.example.org;
option subnet-mask 255.255.255.0;

default-lease-time 600;
max-lease-time 72400;
ddns-update-style none;

subnet 10.254.239.0 netmask 255.255.255.224 {
  range 10.254.239.10 10.254.239.20;
  option routers rtr-239-0-1.example.org, rtr-239-0-2.example.org;
}

host fantasia {
  hardware ethernet 08:00:07:26:c0:a5;
  fixed-address fantasia.fugue.com;
}
```

1. `option domain-name`: クライアントへ提供する既定の検索ドメインを指定します。詳細は `resolv.conf(5)` を参照してください。
2. `option domain-name-servers`: クライアントが使用すべき DNS サーバをカンマ区切りで指定します。例のように完全修飾ドメイン名（FQDN）で指定することも、IP アドレスで指定することもできます。
3. `option subnet-mask`: クライアントへ提供するサブネットマスクです。
4. `default-lease-time`: 既定のリース有効期限（秒単位）です。クライアント側の設定でこの値を上書きすることもできます。
5. `max-lease-time`: リースに許可される最大期間（秒単位）です。クライアントがこれより長いリースを要求した場合でもリース自体は発行されますが、有効期限は `max-lease-time` までに制限されます。
6. `ddns-update-style`: 既定値の `none` は動的 DNS 更新を無効にします。これを `interim` に変更すると、DHCP サーバがリースを払い出すたびに DNS サーバを更新し、ネットワーク内のどのコンピュータにどの IP アドレスが割り当てられているかを DNS サーバ側が把握できるようになります。DNS サーバ側で動的 DNS に対応した設定を行っていない限り、既定値から変更しないでください。
7. `range`: DHCP クライアントへの割り当て用に予約された利用可能 IP アドレスのプールを作成します。アドレス範囲は、前の行で指定したネットワークまたはサブネットに対して有効な範囲でなければなりません。
8. `option routers`: 開き括弧 `{` の前で指定したネットワークまたはサブネットに対して有効なデフォルトゲートウェイを宣言します。
9. `hardware ethernet`: クライアントが要求を送ってきた際に DHCP サーバが識別できるよう、クライアントのハードウェア MAC アドレスを指定します。
10. `fixed-address`: このホストに常に同じ IP アドレスを割り当てるよう指定します。DHCP サーバはリース情報を返す前にホスト名を名前解決するため、ホスト名での指定が正しい書き方です。

この設定ファイルは他にも多くのオプションに対応しています。詳細や設定例は、サーバとともにインストールされる `dhcpd.conf(5)` を参照してください。

`dhcpd.conf` の設定が終わったら、`/etc/rc.conf` で DHCP サーバを有効にします。

```
dhcpd_enable="YES"
dhcpd_ifaces="dc0"
```

`dc0` の部分は、DHCP サーバがクライアントからの要求を待ち受けるインターフェイス名（複数の場合は空白区切り）に置き換えてください。

次のコマンドを実行してサーバを起動します。

```shell
# service isc-dhcpd start
```

今後サーバの設定を変更した際は、その都度 `service(8)` を使って `dhcpd` サービスを停止してから再起動する必要があります。

DHCP サーバは次のファイルを使用します。マニュアルページはサーバソフトウェアと一緒にインストールされます。

* `/usr/local/sbin/dhcpd`

  `dhcpd` サーバの詳細は `dhcpd(8)` を参照してください。

* `/usr/local/etc/dhcpd.conf`

  サーバ設定ファイルであり、クライアントへ提供するすべての情報と、サーバ自身の動作に関する情報を記述します。この設定ファイルについては `dhcpd.conf(5)` で解説されています。

* `/var/db/dhcpd.leases`

  DHCP サーバは発行済みリースのデータベースをこのファイルにログ形式で保持します。より詳しい説明は `dhcpd.leases(5)` を参照してください。

* `/usr/local/sbin/dhcrelay`

  このデーモンは、1 つの DHCP サーバがクライアントからの要求を別ネットワーク上の別の DHCP サーバへ転送する高度な環境で使用します。この機能が必要な場合は、`net/isc-dhcp44-relay` のパッケージまたは Port をインストールしてください。インストールされる `dhcrelay(8)` に詳細が記載されています。

<a id="network-dns"></a>
## Domain Name System（DNS）

Domain Name System（DNS）は、ドメイン名と IP アドレスを相互に対応付ける（名前解決する）ためのプロトコルです。DNS はインターネット全体において、権威ルートネームサーバ、トップレベルドメイン（TLD）ネームサーバ、および個別のドメイン情報をホスト・キャッシュする小規模なネームサーバ群からなる、やや複雑な階層構造によって連携して運用されています。なお、システム上で DNS 参照を行うためにネームサーバを自前で稼働させる必要はありません。

次の表に、DNS に関連する主な用語をまとめます。

**表: DNS の用語**

| 用語 | 定義 |
|---|---|
| 正引き DNS（Forward DNS） | ホスト名から IP アドレスへの対応付け。 |
| オリジン（Origin） | 特定のゾーンファイルが対象としているドメインを指す。 |
| リゾルバ（Resolver） | マシンがゾーン情報を得るためにネームサーバへ問い合わせを行うシステムプロセス。 |
| 逆引き DNS（Reverse DNS） | IP アドレスからホスト名への対応付け。 |
| ルートゾーン（Root zone） | インターネットのゾーン階層の最上位。ファイルシステムですべてのファイルがルートディレクトリ配下にあるのと同様、すべてのゾーンはルートゾーン配下に位置する。 |
| ゾーン（Zone） | 同一の管理権限によって管理される個別のドメイン、サブドメイン、または DNS の一部領域。 |

ゾーンの例は次のとおりです。

* `.` は、ドキュメント上でルートゾーンを指す際によく使われる表記です。
* `org.` はルートゾーン配下のトップレベルドメイン（TLD）です。
* `example.org.` は `org.` TLD 配下のゾーンです。
* `1.168.192.in-addr.arpa` は、`192.168.1.*` の IP アドレス空間に属するすべての IP アドレスを参照する逆引きゾーンです。

見てわかるとおり、ホスト名ではより具体的な部分が左側に現れます。たとえば `example.org.` は `org.` より具体的であり、`org.` はルートゾーンより具体的です。ホスト名の各部分の配置はファイルシステムによく似ており、`/dev` ディレクトリがルート配下にあるのと同じ構造です。

<a id="chapter-33-heading-34"></a>
### ネームサーバを運用する理由（Reasons to Run a Name Server）

ネームサーバには大きく分けて 2 つの形態があります。権威ネームサーバ（authoritative name server）と、キャッシュ（またはリゾルバ）ネームサーバ（caching / resolving name server）です。

権威ネームサーバが必要になるのは、次のような場合です。

* 外部へ向けて DNS 情報を配信し、問い合わせに対して権威ある応答を返したい場合。
* `example.org` のようなドメインを登録し、その配下のホスト名に IP アドレスを割り当てる必要がある場合。
* IP アドレスブロックに対して逆引き DNS エントリ（IP アドレスからホスト名への変換）が必要な場合。
* バックアップまたは 2 台目のネームサーバ（スレーブ）を用意して問い合わせに応答させたい場合。

キャッシュネームサーバが必要になるのは、次のような場合です。

* ローカルの DNS サーバで結果をキャッシュし、外部のネームサーバへ問い合わせるよりも高速に応答させたい場合。

`www.FreeBSD.org` を問い合わせると、通常はリゾルバが上位 ISP のネームサーバへ問い合わせて応答を取得します。ローカルにキャッシュ DNS サーバがあれば、外部への問い合わせはキャッシュ DNS サーバが行う最初の 1 回だけで済みます。情報がローカルにキャッシュされるため、以降の問い合わせではローカルネットワークの外へ出る必要がなくなります。

<a id="chapter-33-heading-35"></a>
### DNS サーバの設定（DNS Server Configuration）

FreeBSD のベースシステムには Unbound が含まれています。既定では、ローカルマシンに対してのみ DNS 名前解決を提供します。ベースシステムの Unbound をローカルマシン以外にも名前解決を提供するように設定することも可能ですが、そのような用途には FreeBSD Ports Collection から Unbound をインストールして対応することが推奨されます。

Unbound を有効にするには、`/etc/rc.conf` に次の行を追加します。

```
local_unbound_enable="YES"
```

`/etc/resolv.conf` にすでに記載されているネームサーバは、新しい Unbound の設定内でフォワーダ（forwarder）として構成されます。

> **注記（NOTE）**: 記載されているネームサーバの中に DNSSEC に対応していないものがあると、ローカルの DNS 名前解決は失敗します。各ネームサーバを必ずテストし、テストに失敗するものは取り除いてください。次のコマンドを実行すると、`192.168.1.1` で稼働しているネームサーバの信頼ツリー（trust tree）または失敗結果が表示されます。

```shell
% drill -S FreeBSD.org @192.168.1.1
```

すべてのネームサーバが DNSSEC に対応していることを確認したら、Unbound を起動します。

```shell
# service local_unbound onestart
```

これにより `/etc/resolv.conf` が自動的に更新され、DNSSEC で保護されたドメインへの問い合わせが機能するようになります。たとえば、次のように実行して `FreeBSD.org` の DNSSEC 信頼ツリーを検証できます。

```shell
% drill -S FreeBSD.org
;; Number of trusted keys: 1
;; Chasing: freebsd.org. A

DNSSEC Trust tree:
freebsd.org. (A)
|---freebsd.org. (DNSKEY keytag: 36786 alg: 8 flags: 256)
    |---freebsd.org. (DNSKEY keytag: 32659 alg: 8 flags: 257)
    |---freebsd.org. (DS keytag: 32659 digest type: 2)
        |---org. (DNSKEY keytag: 49587 alg: 7 flags: 256)
            |---org. (DNSKEY keytag: 9795 alg: 7 flags: 257)
            |---org. (DNSKEY keytag: 21366 alg: 7 flags: 257)
            |---org. (DS keytag: 21366 digest type: 1)
            |   |---. (DNSKEY keytag: 40926 alg: 8 flags: 256)
            |       |---. (DNSKEY keytag: 19036 alg: 8 flags: 257)
            |---org. (DS keytag: 21366 digest type: 2)
                |---. (DNSKEY keytag: 40926 alg: 8 flags: 256)
                    |---. (DNSKEY keytag: 19036 alg: 8 flags: 257)
;; Chase successful
```

<a id="chapter-33-heading-36"></a>
### 権威ネームサーバの設定（Authoritative Name Server Configuration）

FreeBSD のベースシステムには権威ネームサーバ用のソフトウェアは含まれていません。権威ネームサーバを運用する場合は、`dns/nsd` や `dns/bind918` などのサードパーティ製アプリケーションをパッケージまたは Port からインストールしてください。

<a id="network-zeroconf"></a>
## ゼロコンフィギュレーションネットワーキング（mDNS/DNS-SD）

[ゼロコンフィギュレーションネットワーキング](https://en.wikipedia.org/wiki/Zero-configuration_networking)（*Zeroconf* とも呼ばれます）は、ネットワーク設定を簡素化する一連の技術です。Zeroconf の主な構成要素は次のとおりです。

* Link-Local Addressing: 数値のネットワークアドレス（IP アドレス）を自動的に割り当てる仕組み。
* Multicast DNS（*mDNS*）: ホスト名の配信と名前解決を自動的に行う仕組み。
* DNS-Based Service Discovery（*DNS-SD*）: サービスインスタンスを自動的に発見する仕組み。

<a id="chapter-33-heading-38"></a>
### Avahi の設定と起動（Configuring and Starting Avahi）

Zeroconf の代表的な実装の 1 つが [Avahi](https://avahi.org/) です。Avahi は次のコマンドでインストールおよび設定できます。

```shell
# pkg install avahi-app nss_mdns
# grep -q '^hosts:.*\<mdns\>' /etc/nsswitch.conf || sed -i "" 's/^hosts: .*/& mdns/' /etc/nsswitch.conf
# service dbus enable
# service avahi-daemon enable
# service dbus start
# service avahi-daemon start
```

<a id="network-apache"></a>
## Apache HTTP Server

オープンソースの Apache HTTP Server は、最も広く使われている Web サーバです。FreeBSD では既定ではインストールされませんが、`www/apache24` のパッケージまたは Port からインストールできます。

この節では、FreeBSD 上で Apache HTTP Server バージョン 2.*x* を設定・起動する方法を概説します。Apache 2.X および設定ディレクティブの詳細は、[httpd.apache.org](http://httpd.apache.org/) を参照してください。

<a id="chapter-33-heading-40"></a>
### Apache の設定と起動（Configuring and Starting Apache）

FreeBSD では、Apache HTTP Server のメイン設定ファイルは `/usr/local/etc/apache2x/httpd.conf`（*x* はバージョン番号）としてインストールされます。この ASCII テキストファイルでは、`#` で始まる行がコメントになります。最も頻繁に変更されるディレクティブは次のとおりです。

* `ServerRoot "/usr/local"`

  Apache インストールの既定のディレクトリ階層を指定します。バイナリは ServerRoot 配下の `bin` および `sbin` サブディレクトリに、設定ファイルは `etc/apache2x` サブディレクトリに格納されます。

* `ServerAdmin \you@example.com`

  サーバの問題に関する通知を受け取るメールアドレスに変更してください。このアドレスは、エラーページなどサーバが自動生成する一部のページにも表示されます。

* `ServerName www.example.com:80`

  サーバからクライアントへ返すホスト名を設定します。たとえば実際のホスト名の代わりに `www` を使うことができます。システムに登録済みの DNS 名がない場合は、代わりに IP アドレスを入力してください。別のポートで待ち受ける場合は、`80` をそのポート番号に変更します。

* `DocumentRoot "/usr/local/www/apache2x/data"`

  ドキュメントを配信する元のディレクトリです。既定ではすべてのリクエストがこのディレクトリから処理されますが、シンボリックリンクやエイリアスを使って別の場所を指すこともできます。

変更を加える前に、既定の Apache 設定ファイルのバックアップコピーを取っておくことを常にお勧めします。Apache の設定が終わったらファイルを保存し、`apachectl` を使って設定を検証します。`apachectl configtest` を実行して `Syntax OK` が返れば構文に問題はありません。

システム起動時に Apache を自動起動するには、`/etc/rc.conf` に次の行を追加します。

```
apache24_enable="YES"
```

既定以外のオプション付きで Apache を起動したい場合は、`/etc/rc.conf` に次の行を追加して必要なフラグを指定できます。

```
apache24_flags=""
```

`apachectl` で設定エラーが報告されなければ、今すぐ `httpd` を起動します。

```shell
# service apache24 start
```

Web ブラウザで `http://localhost`（`localhost` は `httpd` が動作しているマシンの完全修飾ドメイン名に置き換えます）へアクセスすると、`httpd` サービスの動作を確認できます。既定で表示される Web ページは `/usr/local/www/apache24/data/index.html` です。

`httpd` の稼働中に設定を変更したあと、次のコマンドで設定エラーがないかテストできます。

```shell
# service apache24 configtest
```

> **注記（NOTE）**: `configtest` は `rc(8)` の標準コマンドではないため、すべての起動スクリプトで使えるとは限らない点に注意してください。

<a id="chapter-33-heading-41"></a>
### バーチャルホスト（Virtual Hosting）

バーチャルホスト（Virtual hosting）を使うと、1 台の Apache サーバ上で複数の Web サイトを運用できます。バーチャルホストには *IP ベース* と *名前ベース* があります。IP ベースでは Web サイトごとに異なる IP アドレスを使います。名前ベースではクライアントの HTTP/1.1 ヘッダからホスト名を判別するため、複数の Web サイトで同じ IP アドレスを共有できます。

Apache で名前ベースのバーチャルホストを設定するには、Web サイトごとに `VirtualHost` ブロックを追加します。たとえば、Web サーバ `www.domain.tld` に仮想ドメイン `www.someotherdomain.tld` を同居させる場合は、`httpd.conf` に次のエントリを追加します。

```
<VirtualHost *>
    ServerName www.domain.tld
    DocumentRoot /www/domain.tld
</VirtualHost>

<VirtualHost *>
    ServerName www.someotherdomain.tld
    DocumentRoot /www/someotherdomain.tld
</VirtualHost>
```

各バーチャルホストについて、`ServerName` と `DocumentRoot` の値を使用する環境に合わせて書き換えてください。

バーチャルホスト設定の詳細は、Apache 公式ドキュメント（[http://httpd.apache.org/docs/vhosts/](http://httpd.apache.org/docs/vhosts/)）を参照してください。

<a id="chapter-33-heading-42"></a>
### Apache モジュール（Apache Modules）

Apache ではモジュールを使って基本サーバの機能を拡張します。利用可能なモジュールの一覧や設定の詳細は、[http://httpd.apache.org/docs/current/mod/](http://httpd.apache.org/docs/current/mod/) を参照してください。

FreeBSD では、一部のモジュールは `www/apache24` Port と一緒にコンパイルできます。`/usr/ports/www/apache24` で `make config` を実行すると、どのモジュールが利用可能で、どれが既定で有効になっているかを確認できます。Port に組み込まれていないモジュールでも、FreeBSD Ports Collection を使えば多くのモジュールを簡単にインストールできます。この節では、よく使われる 3 つのモジュールを紹介します。

<a id="chapter-33-heading-43"></a>
#### SSL サポート（SSL support）

以前は Apache で SSL を利用するために `mod_ssl` という追加モジュールが必要でした。現在は状況が変わり、Apache の標準インストールに SSL サポートが組み込まれています。SSL 対応 Web サイトを有効にする設定例は、`/usr/local/etc/apache24/extra` ディレクトリ内にインストールされる `httpd-ssl.conf` にあります。同じディレクトリには `ssl.conf-sample` というサンプルファイルも置かれています。Apache Web サーバで安全な Web サイトを適切に構築するため、両方のファイルを確認しておくことを推奨します。

SSL の設定が完了したら、次回の Apache 再起動またはリロード時に変更が有効になるよう、メインの `httpd.conf`（原文表記: `http.conf`）で次の行のコメントを解除する必要があります。

```
#Include etc/apache24/extra/httpd-ssl.conf
```

> **警告（WARNING）**: SSL バージョン 2 およびバージョン 3 には既知の脆弱性があります。古い SSL オプションの代わりに TLS バージョン 1.2 および 1.3 を有効にすることを強く推奨します。これは `ssl.conf` に次のオプションを設定することで実現できます。

```
SSLProtocol all -SSLv3 -SSLv2 +TLSv1.2 +TLSv1.3
SSLProxyProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
```

Web サーバでの SSL 設定を完了するため、次の行のコメントを解除して、Apache の再起動またはリロード時に設定が読み込まれるようにします。

```
# Secure (SSL/TLS) connections
Include etc/apache24/extra/httpd-ssl.conf
```

また、Apache で SSL を完全に機能させるため、`httpd.conf` の次の行のコメントも解除する必要があります。

```
LoadModule authn_socache_module libexec/apache24/mod_authn_socache.so
LoadModule socache_shmcb_module libexec/apache24/mod_socache_shmcb.so
LoadModule ssl_module libexec/apache24/mod_ssl.so
```

次のステップとして、認証局（CA）から適切な証明書を取得してシステムにインストールします。これによりサイトに信頼の連鎖（chain of trust）が確立され、自己署名証明書による警告が表示されなくなります。

<a id="chapter-33-heading-44"></a>
#### `mod_perl`

`mod_perl` モジュールを使うと、Perl で Apache モジュールを書けるようになります。さらに、サーバ内に常駐インタプリタが組み込まれるため、外部インタプリタを起動するオーバーヘッドや Perl の起動時間のペナルティを回避できます。

`mod_perl` は `www/mod_perl2` のパッケージまたは Port からインストールできます。このモジュールの利用ドキュメントは [http://perl.apache.org/docs/2.0/index.html](http://perl.apache.org/docs/2.0/index.html) にあります。

<a id="chapter-33-heading-45"></a>
#### `mod_php`

*PHP: Hypertext Preprocessor*（PHP）は、特に Web 開発に適した汎用スクリプト言語です。HTML 内に埋め込むことができ、C、Java™、Perl の影響を受けた構文により、Web 開発者が動的に生成される Web ページを素早く記述できるよう設計されています。

Apache 向けの PHP サポートや PHP で書かれた各種機能は、対応する Port をインストールすることで追加できます。

サポートされているすべてのバージョンを探すには、`pkg` でパッケージデータベースを検索します。

```shell
# pkg search php
```

利用可能なバージョンと追加機能の一覧が表示されます。各コンポーネントは完全にモジュール化されているため、必要な Port をインストールすることで機能が有効になります。Apache 向けに PHP バージョン 7.4 をインストールするには、次のコマンドを実行します。

```shell
# pkg install mod_php74
```

依存パッケージのインストールが必要な場合は、あわせてインストールされます。

> **訳注**: `mod_php74` や `php74-*` は固定原文当時のバージョン例です。現在利用可能な PHP バージョンは `pkg search php` で確認してください。

既定では PHP は有効になっていません。有効にするには、`/usr/local/etc/apache24` にある Apache 設定ファイルに次の行を追加する必要があります。

```
<FilesMatch "\.php$">
    SetHandler application/x-httpd-php
</FilesMatch>
<FilesMatch "\.phps$">
    SetHandler application/x-httpd-php-source
</FilesMatch>
```

あわせて、設定ファイル内の `DirectoryIndex` も更新し、変更を反映するために Apache を再起動またはリロードする必要があります。

PHP の多くの拡張機能も `pkg` を使ってインストールできます。たとえば XML や SSL のサポートを追加するには、それぞれの Port をインストールします。

```shell
# pkg install php74-xml php74-openssl
```

先ほどと同様、単にモジュールをインストールしただけでも、変更を反映させるには Apache の設定をリロードする必要があります。

設定を再読み込みするグレースフルリスタート（graceful restart）を行うには、次のコマンドを実行します。

```shell
# apachectl graceful
```

インストールが完了したあと、導入済みの PHP サポートモジュールやビルド時の環境情報を確認する方法は 2 つあります。1 つ目は、PHP 本体のバイナリをインストールして情報を表示するコマンドを実行する方法です。

```shell
# pkg install php74
```

```shell
# php -i | less
```

出力量が多いため、`more` や `less` などのページャへ出力を渡して確認する必要があります。

最後に、PHP 全体のグローバル設定を変更したい場合、丁寧なコメント付きのファイルが `/usr/local/etc/php.ini` として使えるよう用意されています。インストール直後の時点ではこのファイルは存在せず、開発環境向けの `php.ini-development` と本番環境向けの `php.ini-production` の 2 種類が用意されているため、導入環境に合わせてひな形として選択してください。

<a id="chapter-33-heading-46"></a>
#### HTTP2 サポート（HTTP2 Support）

`pkg` で Port をインストールした場合、Apache の HTTP2 プロトコルサポートは既定で含まれています。HTTP の新しいバージョンでは、Web サイトへの接続を単一コネクションにまとめて TCP コネクションの往復回数を減らすなど、従来版から多くの改善が行われています。また、パケットヘッダデータは圧縮され、HTTP2 では既定で暗号化が要求されます。

Apache を HTTP2 のみ使うよう構成すると、Web ブラウザは暗号化された安全な HTTPS 接続を要求します。Apache を両バージョン併用で構成した場合は、接続時に問題が起きた際のフォールバック先として HTTP1.1 が使われます。

この変更には管理者による設定作業が必要ですが、前向きな変更であり、すべての人にとってより安全なインターネットにつながります。なお、この設定変更が必要になるのは、現時点で SSL/TLS を導入していないサイトのみです。

> **注記（NOTE）**: この設定は、TLS サポートを含む前の節の内容を前提としています。この設定へ進む前に、前の節の手順を完了しておくことを推奨します。

まず、`/usr/local/etc/apache24/httpd.conf` で http2 モジュールの行のコメントを外して有効化し、`mpm_prefork` モジュールを `mpm_event` に置き換えます（`mpm_prefork` は HTTP2 に対応していないためです）。

```
LoadModule http2_module libexec/apache24/mod_http2.so
LoadModule mpm_event_module libexec/apache24/mod_mpm_event.so
```

> **注記（NOTE）**: 独立した `mod_http2` Port も利用可能です。これは `apache24` Port に同梱されているモジュールよりも迅速にセキュリティ修正やバグ修正を届けるために用意されています。HTTP2 サポートに必須ではありませんが利用できます。こちらをインストールした場合は、Apache 設定内で `mod_http2.so` の代わりに `mod_h2.so` を指定する必要があります。

Apache で HTTP2 を実装する方法は 2 通りあります。1 つはシステム上のすべてのサイトにグローバルに適用する方法、もう 1 つは各 `VirtualHost` ごとに設定する方法です。HTTP2 をグローバルに有効にするには、`ServerName` ディレクティブの下に次の行を追加します。

```
Protocols h2 http/1.1
```

> **注記（NOTE）**: 平文上で HTTP2 を有効にする場合は、`httpd.conf` で `h2 h2c http/1.1`（原文表記: `h2h2chttp/1.1`）を指定します。

ここに `h2c` を含めると平文の HTTP2 データを通過させられるようになりますが、推奨されません。また、ここに `http/1.1` を含めておくことで、システム上で必要になった場合に HTTP1.1 プロトコルへフォールバックできるようになります。

個別の `VirtualHost` で HTTP2 を有効にするには、`httpd.conf` または `httpd-ssl.conf` の `VirtualHost` ディレクティブ内に同じ行を追加します。

`apachectl reload` コマンドで設定を再読み込みし、ホストしているページのいずれかへアクセスしたあと、次のいずれかの方法で設定をテストします。

```shell
# grep "HTTP/2.0" /var/log/httpd-access.log
```

すると、次のような出力が得られるはずです。

```
192.168.1.205 - - [18/Oct/2020:18:34:36 -0400] "GET / HTTP/2.0" 304 -
192.0.2.205 - - [18/Oct/2020:19:19:57 -0400] "GET / HTTP/2.0" 304 -
192.0.0.205 - - [18/Oct/2020:19:20:52 -0400] "GET / HTTP/2.0" 304 -
192.0.2.205 - - [18/Oct/2020:19:23:10 -0400] "GET / HTTP/2.0" 304 -
```

もう 1 つの方法は Web ブラウザ組み込みのサイトデバッガや `tcpdump` を使うやり方ですが、これらの使い方は本文書の範囲外です。

HTTP2 リバースプロキシ接続は `mod_proxy_http2.so` モジュールを使ってサポートされます。`ProxyPass` や `RewriteRules [P]` 文を設定する際は、接続先に `h2://` を指定してください。

<a id="chapter-33-heading-47"></a>
### 動的 Web サイト（Dynamic Websites）

`mod_perl` や `mod_php` に加え、動的 Web コンテンツを作成するための他の言語やフレームワークも利用できます。その代表例が Django と Ruby on Rails です。

<a id="chapter-33-heading-48"></a>
#### Django

Django は BSD ライセンスで提供されているフレームワークで、開発者が高性能で洗練された Web アプリケーションを素早く書けるように設計されています。オブジェクト関係マッパー（ORM）を備えており、データ型を Python オブジェクトとして開発できます。開発者が SQL を一切書かずに済むよう、それらのオブジェクトに対する豊富な動的データベースアクセス API が用意されています。また、アプリケーションのロジックと HTML の表現を分離できる拡張可能なテンプレートシステムも備えています。

Django は `mod_python` と SQL データベースエンジンに依存します。FreeBSD では、`www/py-django` Port をインストールすると `mod_python` が自動的に導入され、PostgreSQL、MySQL、または SQLite データベースに対応します（既定は SQLite）。データベースエンジンを変更するには、`/usr/ports/www/py-django` で `make config` を実行してから Port をインストールしてください。

> **訳注**: `mod_python` に関する記述および以下の `<Location>` 設定例は、固定原文に残っている過去の構成例です。

Django をインストールしたら、組み込み Python インタプリタを使うためにプロジェクトディレクトリと Apache の設定が必要になります。このインタプリタは、サイト上の特定の URL に対してアプリケーションを呼び出すために使われます。

特定の URL へのリクエストを Web アプリケーションへ渡すよう Apache を設定するには、プロジェクトディレクトリへのフルパスを指定して次の内容を `httpd.conf` に追加します。

```
<Location "/">
    SetHandler python-program
    PythonPath "['/dir/to/the/django/packages/'] + sys.path"
    PythonHandler django.core.handlers.modpython
    SetEnv DJANGO_SETTINGS_MODULE mysite.settings
    PythonAutoReload On
    PythonDebug On
</Location>
```

Django の使い方の詳細は [https://docs.djangoproject.com](https://docs.djangoproject.com) を参照してください。

<a id="chapter-33-heading-49"></a>
#### Ruby on Rails

Ruby on Rails もフルスタックの開発環境を提供するオープンソースの Web フレームワークです。Web 開発者の生産性を高め、強力なアプリケーションを素早く開発できるよう最適化されています。FreeBSD では、`www/rubygem-rails` のパッケージまたは Port を使ってインストールできます。

Ruby on Rails の使い方の詳細は [http://guides.rubyonrails.org](http://guides.rubyonrails.org) を参照してください。

<a id="network-ftp"></a>
## File Transfer Protocol（FTP）

File Transfer Protocol（FTP）は、FTP サーバとの間でファイルを送受信するためのシンプルな手段をユーザーに提供します。FreeBSD のベースシステムには FTP サーバソフトウェア `ftpd` が含まれています。

FreeBSD には、FTP サーバへのアクセスを制御するための設定ファイルがいくつか用意されています。この節ではそれらの概要を説明します。組み込み FTP サーバの詳細は `ftpd(8)` を参照してください。

<a id="chapter-33-heading-51"></a>
### 設定（Configuration）

設定の中で最も重要なのは、どのアカウントに FTP サーバへのアクセスを許可するかを決めることです。FreeBSD システムには、FTP アクセスを許可すべきではないシステムアカウントが多数存在します。FTP アクセスを一切禁止するユーザーの一覧は `/etc/ftpusers` に記載されており、既定ではシステムアカウントが含まれています。これ以外にも FTP アクセスを許可しないユーザーを追加できます。

場合によっては、FTP の利用を完全に禁止するのではなく、一部ユーザーのアクセス範囲だけを制限したいことがあります。その場合は、`ftpchroot(5)` に記載されているとおり `/etc/ftpchroot` を作成します。このファイルには、FTP アクセス制限の対象となるユーザーとグループを列挙します。

サーバへの匿名（anonymous）FTP アクセスを有効にするには、FreeBSD システム上に `ftp` という名前のユーザーを作成します。これにより、ユーザーは `ftp` または `anonymous` というユーザー名で FTP サーバへログインできるようになります。パスワードの入力を求められた際はどのような入力でも受け付けられますが、慣例としてパスワードにはメールアドレスを入力します。匿名ユーザーがログインすると、FTP サーバは `chroot(2)` を呼び出し、アクセス範囲を `ftp` ユーザーのホームディレクトリ内だけに制限します。

FTP クライアントへ表示するウェルカムメッセージを指定するために作成できるテキストファイルが 2 つあります。`/etc/ftpwelcome` の内容は、ログインプロンプトに到達する前にユーザーへ表示されます。ログインが成功したあとは、`/etc/ftpmotd` の内容が表示されます。このファイルのパスはログイン環境に相対的であるため、匿名ユーザーに対しては `~ftp/etc/ftpmotd` の内容が表示される点に注意してください。

FTP サーバの設定が完了したら、システム起動時にサービスを開始するよう `/etc/rc.conf` に適切な変数を設定します。

```
ftpd_enable="YES"
```

今すぐサービスを起動するには、次のように実行します。

```shell
# service ftpd start
```

次のコマンドを入力して FTP サーバへの接続をテストします。

```shell
% ftp localhost
```

`ftpd` デーモンはメッセージの記録に `syslog(3)` を使用します。既定では、システムログデーモンは FTP 関連のメッセージを `/var/log/xferlog` に書き込みます。FTP ログの出力先は、`/etc/syslog.conf` の次の行を変更することで変更できます。

```
ftp.info      /var/log/xferlog
```

> **注記（NOTE）**: 匿名 FTP サーバの運用に伴う潜在的な問題に注意してください。特に、匿名ユーザーによるファイルのアップロードを許可するかどうかは慎重に検討する必要があります。無許可の商用ソフトウェアやさらに悪質なデータのやり取りの場として FTP サイトが悪用されるおそれがあるためです。匿名 FTP でのアップロードが必要な場合は、管理者が確認するまで他の匿名ユーザーがそのファイルを読み取れないようパーミッションを設定してください。

<a id="network-samba"></a>
## Microsoft® Windows® クライアント向けファイル／プリントサービス（Samba）

Samba は、SMB/CIFS プロトコルを使ってファイルサービスとプリントサービスを提供する人気のオープンソースソフトウェアパッケージです。このプロトコルは Microsoft® Windows® システムに標準で組み込まれています。Microsoft® Windows® 以外のシステムでも、Samba クライアントライブラリをインストールすることで利用できるようになります。このプロトコルにより、クライアントは共有されたデータやプリンタへアクセスできます。これらの共有リソースはローカルのディスクドライブとして割り当てたり、共有プリンタをローカルプリンタであるかのように使ったりできます。

FreeBSD では、`net/samba416` の Port またはパッケージを使って Samba クライアントライブラリをインストールできます。クライアントを導入すると、FreeBSD システムから Microsoft® Windows® ネットワーク上の SMB/CIFS 共有へアクセスできるようになります。

同じ `net/samba416` の Port またはパッケージをインストールすることで、FreeBSD システムを Samba サーバとして構成することもできます。これにより、管理者は FreeBSD システム上に SMB/CIFS 共有を作成し、Microsoft® Windows® や Samba クライアントライブラリを実行しているクライアントからアクセスさせることが可能になります。

<a id="chapter-33-heading-53"></a>
### サーバの設定（Server Configuration）

Samba の設定は `/usr/local/etc/smb4.conf` で行います。Samba を使う前にこのファイルを作成しておく必要があります。

ワークグループ内の Windows® クライアントとディレクトリやプリンタを共有するためのシンプルな `smb4.conf` の例を次に示します。LDAP や Active Directory を含むより複雑な構成では、`samba-tool(8)` を使って初期の `smb4.conf` を生成するほうが簡単です。

```
[global]
workgroup = WORKGROUP
server string = Samba Server Version %v
netbios name = ExampleMachine
wins support = Yes
security = user
passdb backend = tdbsam

# Example: share /usr/src accessible only to 'developer' user
[src]
path = /usr/src
valid users = developer
writable  = yes
browsable = yes
read only = no
guest ok = no
public = no
create mask = 0666
directory mask = 0755
```

<a id="chapter-33-heading-54"></a>
#### グローバル設定（Global Settings）

ネットワーク全体に関する設定は `/usr/local/etc/smb4.conf` に記述します。

* `workgroup`

  サービスを提供するワークグループの名前です。

* `netbios name`

  Samba サーバを識別するための NetBIOS 名です。既定では、ホストの DNS 名の先頭要素と同じになります。

* `server string`

  `net view` の出力など、サーバの説明テキストを表示しようとする各種ネットワークツールで表示される文字列です。

* `wins support`

  Samba を WINS サーバとして動作させるかどうかを指定します。同じネットワーク上の 2 台以上のサーバで WINS サポートを有効にしないでください。

<a id="chapter-33-heading-55"></a>
#### セキュリティ設定（Security Settings）

`/usr/local/etc/smb4.conf` において最も重要な設定は、セキュリティモデルとバックエンドのパスワード形式です。これらの設定は次のディレクティブで制御します。

* `security`

  クライアントが FreeBSD マシン上のユーザー名と同じユーザー名を使う場合は、ユーザーレベルのセキュリティを使用する必要があります。`security = user` が既定のセキュリティポリシーであり、共有リソースへアクセスする前にクライアントへログインを要求します。

  `security` オプションで指定できるその他の設定については、`smb.conf(5)` を参照してください。

* `passdb backend`

  Samba には複数のバックエンド認証モデルがあります。クライアントは LDAP、NIS+、SQL データベース、または専用のパスワードファイルなどで認証できます。推奨される認証方式である `tdbsam` は小規模・単純なネットワークに最適であり、ここではこの方式を扱います。より大規模または複雑なネットワークでは `ldapsam` が推奨されます。かつての既定値であった `smbpasswd` は現在では時代遅れ（obsolete）となっています。

<a id="chapter-33-heading-56"></a>
#### Samba ユーザー（Samba Users）

Windows® クライアントが共有にアクセスできるようにするには、FreeBSD のユーザーアカウントを `SambaSAMAccount` データベースへ登録（マッピング）する必要があります。既存の FreeBSD ユーザーアカウントを登録するには、`pdbedit(8)` を使用します。

```shell
# pdbedit -a -u username
```

この節では最もよく使われる設定項目のみを取り上げました。利用可能な設定オプションの詳細は、[Official Samba Wiki](https://wiki.samba.org) を参照してください。

<a id="chapter-33-heading-57"></a>
### Samba の起動（Starting Samba）

起動時に Samba を有効にするには、`/etc/rc.conf` に次の行を追加します。

```
samba_server_enable="YES"
```

今すぐ Samba を起動するには、次のように実行します。

```shell
# service samba_server start
Performing sanity check on Samba configuration: OK
Starting nmbd.
Starting smbd.
```

Samba は 3 つの独立したデーモンで構成されています。`nmbd` と `smbd` の両デーモンは `samba_enable` によって起動されます（訳注: 直前の `/etc/rc.conf` の設定例にあるとおり、Samba 4 系ポートの `rc.d` 変数名は `samba_server_enable` です）。`winbind` による名前解決も必要な場合は、次を設定します。

```
winbindd_enable="YES"
```

Samba はいつでも次のコマンドで停止できます。

```shell
# service samba_server stop
```

Samba は、Microsoft® Windows® ネットワークと幅広く統合できる機能を備えた多機能なソフトウェアスイートです。ここで説明した基本設定を超える機能の詳細については、[https://www.samba.org](https://www.samba.org) を参照してください。

<a id="network-ntp"></a>
## NTP による時刻同期（Clock Synchronization with NTP）

コンピュータの時計は時間の経過とともにずれていく傾向があります。ネットワーク上の多くのサービスでは、ネットワーク内のコンピュータが同じ正確な時刻を共有している必要があるため、時刻のずれは問題になります。また、ファイルのタイムスタンプの一貫性を保つためにも正確な時刻が必要です。Network Time Protocol（NTP）は、ネットワーク上で時刻の正確さを維持する手段の 1 つです。

FreeBSD には `ntpd(8)` が含まれており、他の NTP サーバへ問い合わせてそのマシン自身の時計を同期させたり、ネットワーク上の他のコンピュータへ時刻サービスを提供したりするように設定できます。

この節では、FreeBSD で `ntpd` を設定する方法を説明します。さらに詳しいドキュメントは、HTML 形式で `/usr/share/doc/ntp/` に収録されています。

<a id="chapter-33-heading-59"></a>
### NTP の設定（NTP Configuration）

FreeBSD では、組み込みの `ntpd` を使ってシステムの時計を同期できます。`ntpd` の設定は、以下の節で詳しく説明するように `rc.conf(5)` の変数と `/etc/ntp.conf` を使って行います。

`ntpd` はネットワーク上のピア（peer）と UDP パケットで通信します。マシンと NTP ピアの間にあるすべてのファイアウォールでは、ポート 123 の UDP パケットの送受信を許可するよう設定しておく必要があります。

<a id="chapter-33-heading-60"></a>
#### `/etc/ntp.conf` ファイル（The `/etc/ntp.conf` file）

`ntpd` は `/etc/ntp.conf` を読み込んで、どの NTP サーバへ問い合わせるかを決定します。いずれかのサーバに到達できなくなったり、そのサーバの時計が信頼できなくなったりした場合に備え、複数の NTP サーバを指定しておくことが推奨されます。`ntpd` は応答を受け取るにつれて、信頼性の低いサーバよりも信頼性の高いサーバを優先して使うようになります。問い合わせ先のサーバには、ローカルネットワーク内のサーバ、ISP が提供するサーバ、あるいは [公開 NTP サーバのオンライン一覧](http://support.ntp.org/bin/view/Servers/WebHome) から選んだサーバを指定できます。公開 NTP サーバを選ぶ際は、地理的に近いものを選び、利用ポリシーを確認してください。`pool` 設定キーワードを使うと、サーバプールから 1 台以上のサーバを自動選択します。地域別に整理された [公開 NTP プールのオンライン一覧](http://support.ntp.org/bin/view/Servers/NTPPoolServers) も利用できます。さらに FreeBSD は、プロジェクトが提供するプール `0.freebsd.pool.ntp.org` を用意しています。

**例: `/etc/ntp.conf` のサンプル**

以下は `ntp.conf` ファイルのシンプルな例です。公開ネットワーク接続上で運用する際に推奨される `restrict` オプションが含まれているため、このまま安全に使用できます。

```

# Disallow ntpq control/query access.  Allow peers to be added only
# based on pool and server statements in this file.
restrict default limited kod nomodify notrap noquery nopeer
restrict source  limited kod nomodify notrap noquery

# Allow unrestricted access from localhost for queries and control.
restrict 127.0.0.1
restrict ::1

# Add a specific server.
server ntplocal.example.com iburst

# Add FreeBSD pool servers until 3-6 good servers are available.
tos minclock 3 maxclock 6
pool 0.freebsd.pool.ntp.org iburst

# Use a local leap-seconds file.
leapfile "/var/db/ntpd.leap-seconds.list"
```

このファイルの書式は `ntp.conf(5)` に記載されています。以下では、上記のサンプルファイルで使われているキーワードだけを簡単に説明します。

既定では、NTP サーバはネットワーク上のどのホストからもアクセス可能です。`restrict` キーワードは、どのシステムがサーバへアクセスできるかを制御します。複数の `restrict` エントリを記述でき、それぞれが前の文で指定された制限をさらに絞り込みます。上記の例では、ローカルシステムに対しては問い合わせと制御のフルアクセスを許可しつつ、リモートシステムに対しては時刻の問い合わせのみを許可しています。詳細は `ntp.conf(5)` の `Access Control Support` サブセクションを参照してください。

`server` キーワードは、問い合わせ先の単一サーバを指定します。ファイルには複数の `server` キーワードを記述でき、1 行に 1 台のサーバを記載します。`pool` キーワードはサーバのプールを指定します。`ntpd` は `tos minclock` で指定されたピア数に達するまで、必要に応じてこのプールから 1 台以上のサーバを追加します。`iburst` キーワードは、最初に接続を確立した際に 8 回の高速なパケット交換バーストを実行してシステム時刻を素早く同期するよう `ntpd` に指示します。

`leapfile` キーワードは、うるう秒（leap seconds）に関する情報を含むファイルの場所を指定します。このファイルは `periodic(8)` によって自動的に更新されます。このキーワードで指定するファイルの場所は、`/etc/rc.conf` の `ntp_db_leapfile` 変数で設定する場所と一致していなければなりません。

<a id="chapter-33-heading-61"></a>
#### `/etc/rc.conf` の NTP エントリ（NTP entries in `/etc/rc.conf`）

起動時に `ntpd` を開始するには `ntpd_enable=YES` を設定します。`/etc/rc.conf` に `ntpd_enable=YES` を追加したら、システムを再起動しなくても次のように入力すれば今すぐ `ntpd` を起動できます。

```shell
# service ntpd start
```

`ntpd` を使うために必須の設定は `ntpd_enable` だけです。必要に応じて、以下に挙げる `rc.conf` 変数も設定できます。

`ntpd_sync_on_start=YES` を設定すると、起動時に 1 回だけ、ずれの大きさにかかわらず時計を一気に合わせる（step する）ことを `ntpd` に許可します。通常、`ntpd` は時計が 1000 秒以上ずれているとエラーメッセージをログに出力して終了します。このオプションは、バッテリーバックアップ付きのリアルタイムクロック（RTC）を持たないシステムで特に有用です。

`ntpd_oomprotect=YES` を設定すると、システムがメモリ不足（Out Of Memory: OOM）状態から回復しようとする際に `ntpd` デーモンが強制終了（kill）されないよう保護します。

`ntpd_config=` には、別の場所にある `ntp.conf` ファイルのパスを指定します。

`ntpd_flags=` には必要に応じてその他の `ntpd` フラグを指定できますが、`/etc/rc.d/ntpd` が内部で管理する次のフラグは指定しないでください。

* `-p`（PID ファイルの場所）
* `-c`（代わりに `ntpd_config=` を設定してください）

<a id="chapter-33-heading-62"></a>
#### `ntpd` と非特権 `ntpd` ユーザー（`ntpd` and the unprivileged `ntpd` user）

FreeBSD 上の `ntpd` は、非特権ユーザーとして起動・実行することができます。これを行うには `mac_ntpd(4)` ポリシーモジュールが必要です。`/etc/rc.d/ntpd` 起動スクリプトは最初に NTP の設定を確認します。可能であれば `mac_ntpd` モジュールをロードし、非特権ユーザー `ntpd`（ユーザー ID 123）として `ntpd` を起動します。ファイルやディレクトリへのアクセス権の問題を避けるため、設定にファイル関連のオプションが含まれている場合は、起動スクリプトは自動的に `ntpd` ユーザーとして起動することはありません。

`ntpd_flags` に次のいずれかが含まれている場合は、`ntpd` ユーザーとして実行するために後述の手動設定が必要になります。

* `-f` または `--driftfile`
* `-i` または `--jaildir`
* `-k` または `--keyfile`
* `-l` または `--logfile`
* `-s` または `--statsdir`

`ntp.conf` に次のキーワードのいずれかが含まれている場合も、`ntpd` ユーザーとして実行するために後述の手動設定が必要になります。

* `crypto`
* `driftfile`
* `key`
* `logdir`
* `statsdir`

`ntpd` ユーザーとして実行するよう手動設定するには、次の手順を行います。

* 設定で指定したすべてのファイルとディレクトリに対して、`ntpd` ユーザーがアクセス権を持っていることを確認します。
* `mac_ntpd` モジュールをロードするか、カーネルへ組み込むように設定します。詳細は `mac_ntpd(4)` を参照してください。
* `/etc/rc.conf` に `ntpd_user="ntpd"` を設定します。

<a id="chapter-33-heading-63"></a>
### PPP 接続での NTP の利用（Using NTP with a PPP Connection）

`ntpd` が正常に動作するために、インターネットへの常時接続は必須ではありません。ただし、オンデマンドでダイヤルアウトするよう設定された PPP 接続環境では、NTP トラフィックがきっかけでダイヤルアウトが始まったり、接続が維持されたりしないようにする必要があります。これは `/etc/ppp/ppp.conf` の `filter` ディレクティブで設定できます。たとえば次のように記述します。

```
set filter dial 0 deny udp src eq 123
# Prevent NTP traffic from initiating dial out
set filter dial 1 permit 0 0
set filter alive 0 deny udp src eq 123
# Prevent incoming NTP traffic from keeping the connection open
set filter alive 1 deny udp dst eq 123
# Prevent outgoing NTP traffic from keeping the connection open
set filter alive 2 permit 0/0 0/0
```

詳細は `ppp(8)` の `PACKET FILTERING` セクションおよび `/usr/share/examples/ppp/` 内の設定例を参照してください。

> **注記（NOTE）**: インターネットアクセスプロバイダによっては番号の小さいポートを遮断している場合があり、応答がマシンに届かないため NTP が機能しないことがあります。

<a id="network-iscsi"></a>
## iSCSI イニシエータとターゲットの設定（iSCSI Initiator and Target Configuration）

iSCSI は、ネットワーク越しにストレージを共有するための仕組みです。ファイルシステムレベルで動作する NFS とは異なり、iSCSI はブロックデバイスレベルで動作します。

iSCSI の用語では、ストレージを提供する側のシステムを*ターゲット（target）*と呼びます。提供するストレージには、物理ディスク全体、複数のディスクにまたがる領域、あるいは物理ディスクの一部を使用できます。たとえば、ディスクが ZFS でフォーマットされている場合は、zvol を作成して iSCSI ストレージとして利用できます。

iSCSI ストレージへアクセスするクライアント側は*イニシエータ（initiator）*と呼ばれます。イニシエータから見ると、iSCSI 経由で利用可能になったストレージは LUN（Logical Unit Number）と呼ばれる未フォーマットの生のディスクとして見えます。ディスクのデバイスノードは `/dev/` 配下に現れ、個別にフォーマットとマウントを行う必要があります。

FreeBSD には、カーネルベースのネイティブな iSCSI ターゲットとイニシエータが組み込まれています。この節では、FreeBSD システムをターゲットまたはイニシエータとして設定する方法を説明します。

<a id="network-iscsi-target"></a>
### iSCSI ターゲットの設定（Configuring an iSCSI Target）

iSCSI ターゲットを設定するには、`/etc/ctl.conf` 設定ファイルを作成し、起動時に `ctld(8)` デーモンが自動起動するよう `/etc/rc.conf` に行を追加したうえで、デーモンを起動します。

シンプルな `/etc/ctl.conf` 設定ファイルの例を次に示します。このファイルで指定できるオプションの完全な解説は `ctl.conf(5)` を参照してください。

```
portal-group pg0 {
	discovery-auth-group no-authentication
	listen 0.0.0.0
	listen [::]
}

target iqn.2012-06.com.example:target0 {
	auth-group no-authentication
	portal-group pg0

	lun 0 {
		path /data/target0-0
		size 4G
	}
}
```

最初のエントリは `pg0` ポータルグループを定義しています。ポータルグループは、`ctld(8)` デーモンが待ち受けるネットワークアドレスを定義します。`discovery-auth-group no-authentication` という記述は、すべてのイニシエータが認証なしで iSCSI ターゲットディスカバリを実行できることを意味します。3 行目と 4 行目は、既定のポート 3260 上ですべての IPv4 アドレス（`listen 0.0.0.0`）および IPv6 アドレス（`listen [::]`）で待ち受けるよう `ctld(8)` を設定しています。

`default` と呼ばれる組み込みのポータルグループがあるため、ポータルグループを独自に定義することは必須ではありません。この場合、`default` と `pg0` の違いは、`default` ではターゲットディスカバリが常に拒否されるのに対し、`pg0` では常に許可される点です。

2 つ目のエントリは単一のターゲットを定義しています。「ターゲット」には iSCSI を提供するマシンを指す場合と、LUN に名前を付けたグループを指す場合の 2 通りの意味があります。この例では後者の意味で使っており、`iqn.2012-06.com.example:target0` がターゲット名になります。このターゲット名はテスト目的のものです。実際の運用では、`com.example` の部分を実際のドメイン名を逆順にしたものに書き換えてください。`2012-06` はそのドメイン名の管理権を取得した年月を表し、`target0` には任意の値を指定できます。この設定ファイルには任意の数のターゲットを定義できます。

`auth-group no-authentication` 行はすべてのイニシエータが指定のターゲットへ接続できるようにし、`portal-group pg0` は `pg0` ポータルグループ経由でそのターゲットへ到達できるようにします。

次のセクションでは LUN を定義しています。イニシエータからは、各 LUN が個別のディスクデバイスとして見えます。ターゲットごとに複数の LUN を定義できます。各 LUN は番号で識別され、LUN 0 は必須です。`path /data/target0-0` 行は LUN の実体となるファイルまたは zvol のフルパスを定義します。このパスは `ctld(8)` を起動する前に存在していなければなりません。2 行目は任意であり、LUN のサイズを指定します。

次に、起動時に `ctld(8)` デーモンが開始されるよう `/etc/rc.conf` に次の行を追加します。

```
ctld_enable="YES"
```

今すぐ `ctld(8)` を起動するには、次のコマンドを実行します。

```shell
# service ctld start
```

`ctld(8)` デーモンは起動時に `/etc/ctl.conf` を読み込みます。デーモンの起動後にこのファイルを編集した場合は、次のコマンドを実行して変更を即座に反映させてください。

```shell
# service ctld reload
```

<a id="chapter-33-heading-66"></a>
#### 認証（Authentication）

前の例では認証を行っていないため、誰にでもすべてのターゲットへのフルアクセスを許可してしまい、本質的に安全ではありません。ターゲットへのアクセスにユーザー名とパスワードを要求するには、設定を次のように変更します。

```
auth-group ag0 {
	chap username1 secretsecret
	chap username2 anothersecret
}

portal-group pg0 {
	discovery-auth-group no-authentication
	listen 0.0.0.0
	listen [::]
}

target iqn.2012-06.com.example:target0 {
	auth-group ag0
	portal-group pg0
	lun 0 {
		path /data/target0-0
		size 4G
	}
}
```

`auth-group` セクションでは、ユーザー名とパスワードの組を定義します。`iqn.2012-06.com.example:target0` へ接続しようとするイニシエータは、定義されたユーザー名とシークレットを先に指定する必要があります。ただし、この設定のままでは認証なしでのターゲットディスカバリは引き続き許可されています。ターゲットディスカバリにも認証を要求するには、`discovery-auth-group` に `no-authentication` ではなく定義済みの `auth-group` 名を指定してください。

イニシエータごとに 1 つの公開ターゲットを定義する運用も一般的です。上記構文の省略記法として、ターゲットエントリ内にユーザー名とパスワードを直接記述することもできます。

```
target iqn.2012-06.com.example:target0 {
	portal-group pg0
	chap username1 secretsecret

	lun 0 {
		path /data/target0-0
		size 4G
	}
}
```

<a id="network-iscsi-initiator"></a>
### iSCSI イニシエータの設定（Configuring an iSCSI Initiator）

> **注記（NOTE）**: この節で説明する iSCSI イニシエータは FreeBSD 10.0-RELEASE 以降でサポートされています。それ以前のバージョンで利用可能な iSCSI イニシエータを使う場合は、`iscontrol(8)` を参照してください。

iSCSI イニシエータを利用するには、`iscsid(8)` デーモンが動作している必要があります。このデーモンは設定ファイルを使用しません。起動時に自動的に開始するには、`/etc/rc.conf` に次の行を追加します。

```
iscsid_enable="YES"
```

今すぐ `iscsid(8)` を起動するには、次のコマンドを実行します。

```shell
# service iscsid start
```

ターゲットへの接続は、`/etc/iscsi.conf` 設定ファイルを使う方法と使わない方法のどちらでも行えます。この節では両方の接続方法を紹介します。

<a id="chapter-33-heading-68"></a>
#### 設定ファイルを使わずにターゲットへ接続する（Connecting to a Target Without a Configuration File）

イニシエータを単一のターゲットへ接続するには、ポータルの IP アドレスとターゲット名を指定します。

```shell
# iscsictl -A -p 10.10.10.10 -t iqn.2012-06.com.example:target0
```

接続に成功したかを確認するには、引数なしで `iscsictl` を実行します。次のような出力が表示されるはずです。

```
Target name                                     Target portal   State
iqn.2012-06.com.example:target0                 10.10.10.10     Connected: da0
```

この例では iSCSI セッションが正常に確立され、接続された LUN が `/dev/da0` として認識されています。`iqn.2012-06.com.example:target0` ターゲットが複数の LUN を公開している場合は、出力の該当箇所に複数のデバイスノードが表示されます。

```shell
Connected: da0 da1 da2.
```

エラーが発生した場合は、出力およびシステムログに報告されます。たとえば、次のメッセージは通常 `iscsid(8)` デーモンが動作していないことを意味します。

```
Target name                                     Target portal   State
iqn.2012-06.com.example:target0                 10.10.10.10     Waiting for iscsid(8)
```

次のメッセージは、IP アドレスやポート番号の誤りなどネットワーク上の問題を示唆しています。

```
Target name                                     Target portal   State
iqn.2012-06.com.example:target0                 10.10.10.11     Connection refused
```

このメッセージは、指定したターゲット名が誤っていることを意味します。

```
Target name                                     Target portal   State
iqn.2012-06.com.example:target0                 10.10.10.10     Not found
```

このメッセージは、ターゲット側で認証が要求されていることを意味します。

```
Target name                                     Target portal   State
iqn.2012-06.com.example:target0                 10.10.10.10     Authentication failed
```

CHAP のユーザー名とシークレットを指定するには、次の構文を使います。

```shell
# iscsictl -A -p 10.10.10.10 -t iqn.2012-06.com.example:target0 -u user -s secretsecret
```

<a id="chapter-33-heading-69"></a>
#### 設定ファイルを使ってターゲットへ接続する（Connecting to a Target with a Configuration File）

設定ファイルを使って接続するには、次のような内容で `/etc/iscsi.conf` を作成します。

```
t0 {
	TargetAddress   = 10.10.10.10
	TargetName      = iqn.2012-06.com.example:target0
	AuthMethod      = CHAP
	chapIName       = user
	chapSecret      = secretsecret
}
```

`t0` は設定ファイル内のセクションに対するニックネームを指定しています。イニシエータがどの設定を使うかを指定する際にこの名前を用います。残りの行では接続時に使用するパラメータを指定します。`TargetAddress` と `TargetName` は必須で、それ以外のオプションは任意です。この例では CHAP のユーザー名とシークレットも記載しています。

定義したターゲットへ接続するには、ニックネームを指定します。

```shell
# iscsictl -An t0
```

あるいは、設定ファイル内に定義されたすべてのターゲットへ接続するには、次のように実行します。

```shell
# iscsictl -Aa
```

システム起動時に `/etc/iscsi.conf` 内のすべてのターゲットへイニシエータが自動接続するようにするには、`/etc/rc.conf` に次を追加します。

```
iscsictl_enable="YES"
iscsictl_flags="-Aa"
```
