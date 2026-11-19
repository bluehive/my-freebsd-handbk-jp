<a id="mail"></a>
# 第32章 電子メール（Electronic Mail）【ドラフト】

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/mail/)の「Chapter 32. Electronic Mail」（既存 TOC ID 31）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/mail/_index.adoc`）に基づいて日本語へ意訳したものです（現在ドラフト作成中）。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` は一般ユーザーのプロンプトを示します。

<a id="mail-synopsis"></a>
## 概要

「電子メール」（一般にはメール／email と呼ばれます）は、今日もっとも広く使われている通信手段の 1 つです。本章では、FreeBSD 上でメールサーバーを運用するための基礎と、FreeBSD を使ってメールを送受信する基本的な方法を紹介します。この分野を網羅的に学びたい場合は、[参考文献（Bibliography）](https://docs.freebsd.org/en/books/handbook/bibliography/#bibliography)に挙げられている書籍を参照してください。

本章では、次の内容を扱います。

* 電子メールの送受信に関わるソフトウェアコンポーネント
* DragonFly Mail Agent の設定方法
* FreeBSD における基本的な Sendmail 設定ファイルの配置場所
* リモートメールボックスとローカルメールボックスの違い
* DragonFly Mail Agent や Sendmail に代わる別のメール転送エージェント（MTA）をインストール・設定する方法
* メールサーバーでよくある問題のトラブルシューティング方法
* Sendmail を送信専用として設定する方法
* Sendmail のセキュリティを高めるための SMTP 認証の設定方法
* `mutt` などのメールユーザーエージェント（MUA）をインストールしてメールを送受信する方法
* リモートの POP または IMAP サーバーからメールをダウンロードする方法
* 受信メールに対してフィルタやルールを自動的に適用する方法

<a id="mail-using"></a>
## メールの構成要素

メールのやり取りには、メールユーザーエージェント（MUA）、メール転送エージェント（MTA）、メールホスト、リモートまたはローカルのメールボックス、そして DNS という 5 つの主要な要素が関わります。この節では、これらの構成要素の概要を説明します。

**メールユーザーエージェント（Mail User Agent: MUA）**
: メールユーザーエージェント（MUA）は、メールの作成・送信・受信を行うアプリケーションです。FreeBSD に組み込まれている `mail` ユーティリティや、Ports Collection（ポート集）から導入できる `alpine`・`elm`・`mutt` のようなコマンドラインプログラムもあれば、Claws Mail・Evolution・Thunderbird をはじめとする多数のグラフィカルなメールクライアントも Ports Collection に用意されています。また、Web ブラウザから利用できる Web メールを提供している組織もあります。FreeBSD での MUA のインストールと使い方については、[メールユーザーエージェント（MUA）](#mail-agents)を参照してください。

**メール転送エージェント（Mail Transfer Agent: MTA）**
: メール転送エージェント（MTA）は、外部からのメールの受信と送信メールの配送を担います。FreeBSD 14.0 以降のデフォルト MTA は DragonFly Mail Agent（`dma(8)`）であり、それ以前のバージョンでは `sendmail(8)` です。Exim、Postfix、qmail などの他の MTA をインストールして、デフォルトの MTA と置き換えることもできます。

**メールホストとメールボックス（Mail Host and Mailboxes）**
: メールホストは、あるホストやネットワーク宛てのメールの配送と受信を担当するサーバーです。メールホストはそのドメイン宛てに送られたメールをすべて受け取り、設定に応じてデフォルトの `mbox` 形式、または別の Maildir 形式で保存します。保存されたメールは、ローカル環境で MUA を使って直接読むことも、POP や IMAP などのプロトコル経由でリモートからアクセスして取得することもできます。メールをローカルで読む場合は、POP や IMAP のサーバーをインストールする必要はありません。

**ドメインネームシステム（Domain Name System: DNS）**
: ドメインネームシステム（DNS）とそのデーモンである `named(8)` は、メール配送において大きな役割を果たします。あるサイトから別のサイトへメールを配送する際、MTA は宛先サイトを DNS で問い合わせ、その宛先のメールを受け取るホストを特定します。リモートホストからこちらの MTA へメールが送られてくる際にも、同じ仕組みが働きます。

<a id="dragonFly-mail-agent"></a>
## DragonFly Mail Agent（DMA）

DragonFly Mail Agent（DMA）は、FreeBSD 14.0 以降のデフォルト MTA です。`dma(8)` は家庭やオフィスでの利用を想定して設計された小型のメール転送エージェント（Mail Transport Agent: MTA）です。ローカルにインストールされたメールユーザーエージェント（MUA）からメールを受け取り、ローカルまたはリモート宛先へ配送します。リモート配送では、TLS/SSL サポートや SMTP 認証などの機能も備えています。

`dma(8)` は、`sendmail(8)` や `postfix(1)` のような本格的な大型 MTA の代替を意図したものではありません。そのため、`dma(8)` は受信接続のためにポート 25 で待ち受けを行いません。

<a id="configuring-dragonfly-mail-agent"></a>
### DragonFly Mail Agent（DMA）の設定

DMA には多くの環境でそのまま使えるデフォルト設定が用意されています。独自の設定は `/etc/dma/dma.conf` に記述し、SMTP 認証は `/etc/dma/auth.conf` で設定します。

<a id="configuring-gmail-dma"></a>
#### DMA を使って Gmail 経由で送信メールを中継する（STARTTLS:SMTP の例）

次の `/etc/dma/dma.conf` の例を使うと、Google の SMTP サーバー経由でメールを送信できます。

```
SMARTHOST smtp.gmail.com
PORT 587
AUTHPATH /etc/dma/auth.conf
SECURETRANSFER
STARTTLS
MASQUERADE username@gmail.com
```

認証情報は、`/etc/dma/auth.conf` に 1 行記述することで設定できます。

```
username@gmail.com|smtp.gmail.com:password
```

> **注**: 2 要素認証が有効になっている場合は、通常のログインパスワードでは拒否されるため、生成したアプリ固有のパスワードを使用する必要があります。詳細は Google の[アプリパスワード（app-specific passwords）](https://myaccount.google.com/apppasswords)のドキュメントを参照してください。

次のコマンドを実行して設定をテストします。

```shell
% echo this is a test | mail -v -s testing-email username@gmail.com
```

<a id="configuring-fastmail-dma"></a>
#### DMA を使って Fastmail 経由で送信メールを中継する（SSL/TLS の例）

次の `/etc/dma/dma.conf` の例を使うと、Fastmail の SMTP サーバー経由でメールを送信できます。

```
SMARTHOST smtp.fastmail.com
PORT 465
AUTHPATH /etc/dma/auth.conf
SECURETRANSFER
MAILNAME example.server.com
```

認証情報は、`/etc/dma/auth.conf` に 1 行記述することで設定できます。

```
username@fastmail.com|smtp.fastmail.com:password
```

次のコマンドを実行して設定をテストします。

```shell
% echo this is a test | mail -v -s testing-email username@fastmail.com
```

<a id="configuring-custom-dma"></a>
#### DMA を使って独自のメールホスト経由で送信メールを中継する

次の `/etc/dma/dma.conf` の例を使うと、独自のメールホスト経由でメールを送信できます。

```
SMARTHOST mail.example.org
PORT 587
AUTHPATH /etc/dma/auth.conf
SECURETRANSFER
STARTTLS
```

認証情報は、`/etc/dma/auth.conf` に 1 行記述することで設定できます。

```
username@example.org|mail.example.org:password
```

次のコマンドを実行して設定をテストします。

```shell
% echo this is a test | mail -v -s testing-email username@example.org
```

<a id="sendmail"></a>
## Sendmail

Sendmail は、UNIX® および UNIX 系システムで長い歴史を持つ、実績豊富で多機能なメール転送エージェント（MTA）です。FreeBSD 13 までは FreeBSD ベースシステムの一部として提供されており、堅牢なメール転送機能、高度なカスタマイズ性、複雑なルーティングやフィルタリングのサポートを備えています。

<a id="configuring-sendmail"></a>
### 設定ファイル

Sendmail の設定ファイルは `/etc/mail/` に配置されています。

**`/etc/mail/access`**

このアクセスデータベースファイルは、ローカルのメールサーバーに対してどのホストや IP アドレスからのアクセスを許可し、どのようなアクセスを認めるかを定義します。デフォルトの動作である `OK` が指定されたホストは、メールの最終宛先がローカルマシンである場合に限り、このホストへメールを送信できます。`REJECT` が指定されたホストは、すべてのメール接続が拒否されます。`RELAY` が指定されたホストは、このメールサーバーを使って任意の宛先へメールを送信できます。`ERROR` が指定されたホストには、指定されたメールエラーを伴ってメールが返送されます。`SKIP` が指定されたホストについては、Sendmail はメールの受理も拒否もせずに、そのエントリに対する現在の検索を中止します。`QUARANTINE` が指定されたホストからのメッセージは保留され、保留理由として指定されたテキストが返されます。

これらのオプションを IPv4 アドレスと IPv6 アドレスの双方で使用する例は、FreeBSD のサンプル設定ファイル `/etc/mail/access.sample` にあります。

アクセスデータベースを設定するには、サンプルに示されている書式で `/etc/mail/access` にエントリを記述しますが、エントリの先頭にコメント記号（`#`）を付けないでください。アクセスを制御したいホストやネットワークごとにエントリを作成します。表の左側に一致するメール送信者に対して、表の右側のアクションが適用されます。

このファイルを更新したときは、その都度データベースを更新して Sendmail を再起動してください。

```shell
# makemap hash /etc/mail/access < /etc/mail/access
# service sendmail restart
```

**`/etc/mail/aliases`**

このデータベースファイルには、ユーザー、ファイル、プログラム、または別のエイリアスへ展開される仮想メールボックスの一覧が含まれます。ファイルの書式を示す例をいくつか挙げます。

```
root: localuser
ftp-bugs: joe,eric,paul
bit.bucket:  /dev/null
procmail: "|/usr/local/bin/procmail"
```

コロンの左側にあるメールボックス名が、右側にある展開先へ展開されます。1 行目のエントリでは、`root` メールボックスが `localuser` メールボックスへ展開され、さらに `localuser` が `/etc/mail/aliases` データベース内で検索されます。一致するエントリがなければ、メッセージは `localuser` へ配送されます。2 行目のエントリはメーリングリストの例で、`ftp-bugs` 宛てのメールは `joe`、`eric`、`paul` という 3 つのローカルメールボックスへ展開されます。リモートのメールボックスは *user@example.com* のように指定できます。3 行目のエントリはメールをファイル（この例では `/dev/null`）へ書き出す方法です。最後のエントリは、UNIX® のパイプ経由でプログラム `/usr/local/bin/procmail` へメールを渡す方法を示しています。このファイルの書式の詳細は `aliases(5)` を参照してください。

このファイルを更新したときは、その都度 `newaliases` を実行してエイリアスデータベースを更新・初期化してください。

**`/etc/mail/sendmail.cf`**

これは Sendmail のマスター設定ファイルです。メールアドレスの書き換えからリモートメールサーバーへ返す拒否メッセージの出力に至るまで、Sendmail 全体の動作を制御します。そのためこの設定ファイルは非常に複雑ですが、幸い、標準的なメールサーバーでは変更が必要になることはほとんどありません。

マスター設定ファイルは、Sendmail の機能や動作を定義する `m4(1)` マクロから構築できます。詳細の一部については `/usr/src/contrib/sendmail/cf/README` を参照してください。

このファイルを変更したときは、変更を反映するために Sendmail を再起動する必要があります。

**`/etc/mail/virtusertable`**

このデータベースファイルは、仮想ドメインや仮想ユーザーのメールアドレスを実際のメールボックスに対応付けます。対応先には、ローカルメールボックス、リモートメールボックス、`/etc/mail/aliases` で定義されたエイリアス、またはファイルを指定できます。これにより、1 台のマシン上で複数の仮想ドメインをホストできます。

FreeBSD では、書式の例としてサンプル設定ファイル `/etc/mail/virtusertable.sample` が用意されています。次の例は、その書式を使って独自のエントリを作成する方法を示しています。

```
root@example.com                root
postmaster@example.com          postmaster@noc.example.net
@example.com                    joe
```

このファイルは先頭から順に最初に一致した規則（first match）で処理されます。メールアドレスが左側のアドレスに一致すると、右側に記載されたメールボックスへ対応付けられます。この例の 1 行目は特定のメールアドレスをローカルメールボックスへ対応付ける書式、2 行目は特定のメールアドレスをリモートメールボックスへ対応付ける書式です。最後に、それまでのエントリのいずれにも一致しなかった `example.com` のメールアドレスはすべて最後の対応付けに一致し、ローカルメールボックス `joe` へ送られます。独自のエントリを作成するときは、この書式で `/etc/mail/virtusertable` に追加してください。このファイルを編集したときは、その都度データベースを更新して Sendmail を再起動します。

```shell
# makemap hash /etc/mail/virtusertable < /etc/mail/virtusertable
# service sendmail restart
```

**`/etc/mail/relay-domains`**

デフォルトの FreeBSD インストールでは、Sendmail は自身が稼働しているホストからのメールのみを送信するように設定されています。たとえば POP サーバーが利用可能な場合、ユーザーはリモート環境からメールを確認できても、外部から送信メールを送ることはできません。通常、送信を試みてから少し経つと、`MAILER-DAEMON` から `5.7 Relaying Denied` というメッセージが返送されます。

もっとも簡単な解決策は、ISP の FQDN を `/etc/mail/relay-domains` に追加することです。複数のアドレスが必要な場合は、1 行に 1 つずつ追加します。

```
your.isp.example.com
other.isp.example.net
users-isp.example.org
www.example.org
```

このファイルを作成または編集したら、`service sendmail restart` で Sendmail を再起動してください。

これにより、ユーザーがこのシステム上にアカウントを持っている限り、このリストに含まれるいずれのホストからこのシステム経由で送信されたメールも成功するようになります。こうして、インターネットからのスパム中継（リレー）を許してしまうことなく、ユーザーがリモートからこのシステム経由でメールを送信できるようになります。
