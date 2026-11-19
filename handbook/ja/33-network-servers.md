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
