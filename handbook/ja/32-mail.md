<a id="mail"></a>
# 第32章 電子メール（Electronic Mail）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/mail/)の「Chapter 32. Electronic Mail」（既存 TOC ID 31）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/mail/_index.adoc`）に基づいて日本語へ意訳したものです。

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

メールユーザーエージェント（MUA）は、メールの作成・送信・受信を行うアプリケーションです。FreeBSD に組み込まれている `mail` ユーティリティや、Ports Collection（ポート集）から導入できる `alpine`・`elm`・`mutt` のようなコマンドラインプログラムもあれば、Claws Mail・Evolution・Thunderbird をはじめとする多数のグラフィカルなメールクライアントも Ports Collection に用意されています。また、Web ブラウザから利用できる Web メールを提供している組織もあります。FreeBSD での MUA のインストールと使い方については、[メールユーザーエージェント（MUA）](#mail-agents)を参照してください。

**メール転送エージェント（Mail Transfer Agent: MTA）**

メール転送エージェント（MTA）は、外部からのメールの受信と送信メールの配送を担います。FreeBSD 14.0 以降のデフォルト MTA は DragonFly Mail Agent（`dma(8)`）であり、それ以前のバージョンでは `sendmail(8)` です。Exim、Postfix、qmail などの他の MTA をインストールして、デフォルトの MTA と置き換えることもできます。

**メールホストとメールボックス（Mail Host and Mailboxes）**

メールホストは、あるホストやネットワーク宛てのメールの配送と受信を担当するサーバーです。メールホストはそのドメイン宛てに送られたメールをすべて受け取り、設定に応じてデフォルトの `mbox` 形式、または別の Maildir 形式で保存します。保存されたメールは、ローカル環境で MUA を使って直接読むことも、POP や IMAP などのプロトコル経由でリモートからアクセスして取得することもできます。メールをローカルで読む場合は、POP や IMAP のサーバーをインストールする必要はありません。

**ドメインネームシステム（Domain Name System: DNS）**

ドメインネームシステム（DNS）とそのデーモンである `named(8)` は、メール配送において大きな役割を果たします。あるサイトから別のサイトへメールを配送する際、MTA は宛先サイトを DNS で問い合わせ、その宛先のメールを受け取るホストを特定します。リモートホストからこちらの MTA へメールが送られてくる際にも、同じ仕組みが働きます。

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

このファイルは先頭から順に最初に一致した規則（first match）で処理されます。メールアドレスが左側のアドレスに一致すると、右側に記載されたローカルメールボックスへ対応付けられます。この例の 1 行目は特定のメールアドレスをローカルメールボックスへ対応付ける書式、2 行目は特定のメールアドレスをリモートメールボックスへ対応付ける書式です。最後に、それまでのエントリのいずれにも一致しなかった `example.com` のメールアドレスはすべて最後の対応付けに一致し、ローカルメールボックス `joe` へ送られます。独自のエントリを作成するときは、この書式で `/etc/mail/virtusertable` に追加してください。このファイルを編集したときは、その都度データベースを更新して Sendmail を再起動します。

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

<a id="mail-changingmta"></a>
## メール転送エージェント（MTA）の変更

FreeBSD 14.0 以降は `dma(8)` がデフォルト MTA であり、14.0 より前は `sendmail(8)` がデフォルト MTA です。ただし、システム管理者はシステムの MTA を変更できます。FreeBSD の Ports Collection の `mail` カテゴリには、代替 MTA が数多く用意されています。

> **警告**: デフォルトの送信メールサービスを無効化する場合は、必ず別のメール配送システムへ置き換えてください。そうしないと、`periodic(8)` のようなシステム機能が実行結果をメールで配信できなくなります。システムの多くの箇所は、正常に動作する MTA の存在を前提としています。無効化後もアプリケーションがデフォルトのバイナリを使ってメール送信を試み続けると、メールが非アクティブなキューに入ったまま配送されなくなるおそれがあります。

<a id="replace-sendmail-dma"></a>
### Sendmail を他の MTA へ置き換える

`sendmail(8)` を完全に無効化するには、次のコマンドを実行します。

```shell
# sysrc sendmail_enable="NO"
# sysrc sendmail_submit_enable="NO"
# sysrc sendmail_outbound_enable="NO"
# sysrc sendmail_msp_queue_enable="NO"
```

`sendmail(8)` の受信メールサービスだけを無効化する場合は、次のコマンドを実行します。

```shell
# sysrc sendmail_enable="NO"
```

続いて、`sendmail(8)` サービスを停止します。

```shell
# service sendmail onestop
```

`sendmail(8)` は広く普及しているため、すでにインストール・設定済みであることを前提とするソフトウェアも存在し、追加の設定が必要です。`/etc/periodic.conf` を確認し、次の設定値が `NO` になっていることを確かめてください。ファイルが存在しない場合は、次の内容で作成します。

```
daily_clean_hoststat_enable="NO"
daily_status_mail_rejects_enable="NO"
daily_status_include_submit_mailq="NO"
daily_submit_queuerun="NO"
```

次の手順として別の MTA をインストールします。この例では `dma(8)` を使用します。前述のとおり、FreeBSD 14.0 以降では `dma(8)` がデフォルト MTA のため、Ports からインストールする必要があるのはそれ以前のバージョンを使っている場合のみです。

インストールするには、次のコマンドを実行します。

```shell
# pkg install dma
```

[DragonFly Mail Agent（DMA）の設定](#configuring-dragonfly-mail-agent)の手順に従って設定を行います。

その後、`/etc/mail/mailer.conf` 内のすべてのエントリを `dma(8)` に変更します。

```
# Execute the "real" sendmail program, named /usr/libexec/sendmail/sendmail
#
# If dma(8) is installed, an example mailer.conf that uses dma(8) instead can
# be found in /usr/share/examples/dma
#
sendmail        /usr/local/libexec/dma
mailq           /usr/local/libexec/dma
newaliases      /usr/local/libexec/dma
```

> **注**: ベースシステムに含まれる `dma(8)` を使用する場合は、パスが `/usr/libexec/dma` に変わります。

起動時またはシャットダウン前にキュー内のメールを確実にフラッシュ（送出）するため、次のコマンドを実行します。

```shell
# sysrc dma_flushq_enable="YES"
```

すべての設定が終わったら、システムを再起動することを推奨します。再起動することで、起動時に新しい MTA が自動的に開始されるよう正しく設定されているかを確認できます。

<a id="replace-dma"></a>
### DragonFly Mail Agent（DMA）を他の MTA へ置き換える

前述のとおり、FreeBSD 14.0 以降のデフォルト MTA は DMA です。この例では、代替 MTA として `mail/postfix` を使用します。

`mail/postfix` をインストールする前に、追加の設定が必要です。`/etc/periodic.conf` を確認し、次の設定値が `NO` になっていることを確かめてください。ファイルが存在しない場合は、次の内容で作成します。

```
daily_clean_hoststat_enable="NO"
daily_status_mail_rejects_enable="NO"
daily_status_include_submit_mailq="NO"
daily_submit_queuerun="NO"
```

続いて、`mail/postfix` をインストールします。

```shell
# pkg install postfix
```

システム起動時に `mail/postfix` を自動起動するには、次のコマンドを実行します。

```shell
# sysrc postfix_enable="YES"
```

> **ヒント**: アプリケーションをインストールした後は、インストールメッセージを読む習慣を付けるとよいでしょう。設定などに関する有用な情報が含まれています。

`/usr/local/etc/mail/mailer.conf` で Postfix が**まだ**有効化されていない場合は、次のコマンドを実行します。

```shell
mv /usr/local/etc/mail/mailer.conf /usr/local/etc/mail/mailer.conf.old
install -d /usr/local/etc/mail
install -m 0644 /usr/local/share/postfix/mailer.conf.postfix /usr/local/etc/mail/mailer.conf
```

SASL を使用する場合は、Postfix が sasldb ファイルを読み取れるようにしておく必要があります。これには、ユーザー `postfix` をグループ `mail` に追加し、`/usr/local/etc/sasldb*` ファイルをグループ `mail` から読み取り可能にします（新規インストールではこれがデフォルトになっているはずです）。

すべての設定が終わったら、システムを再起動することを推奨します。再起動することで、起動時に新しい MTA が自動的に開始されるよう正しく設定されているかを確認できます。

<a id="mail-agents"></a>
## メールユーザーエージェント（MUA）

MUA はメールの送受信に使用するアプリケーションです。メールが「進化」して複雑になるにつれて、MUA もますます高機能になり、ユーザーにより高い機能性と柔軟性を提供するようになっています。FreeBSD の Ports Collection の `mail` カテゴリには多数の MUA が用意されており、Evolution や Balsa のようなグラフィカルなメールクライアントから、`mutt` や `alpine` のようなコンソールベースのクライアントまで幅広く揃っています。

<a id="mail-command"></a>
### mail

`mail(1)` は FreeBSD に標準でインストールされているデフォルトの MUA です。コンソールベースの MUA であり、テキストベースのメールを送受信するための基本的な機能を備えています。添付ファイルのサポートは限定的で、アクセスできるのはローカルメールボックスのみです。

`mail(1)` 自体は POP や IMAP サーバーとのやり取りに対応していませんが、`fetchmail` や `getmail` のようなアプリケーションを使えば、リモートメールボックスのメールをローカルの `mbox` へダウンロードできます。

メールを送受信するには、`mail(1)` を実行します。

```shell
% mail
```

`mail(1)` は `/var/mail` にあるユーザーのメールボックスの内容を自動的に読み込みます。メールボックスが空であれば、メールが見つからない旨のメッセージを表示して終了します。メールが存在する場合は、アプリケーションのインターフェースが起動し、メッセージの一覧が表示されます。

次の例のように、メッセージには自動的に番号が振られます。

```
Mail version 8.1 6/6/93.  Type ? for help.
"/var/mail/username": 3 messages 3 new
>N  1 root@localhost        Mon Mar  8 14:05  14/510   "test"
 N  2 root@localhost        Mon Mar  8 14:05  14/509   "user account"
 N  3 root@localhost        Mon Mar  8 14:05  14/509   "sample"
```

メッセージを読むには、`t` に続けてメッセージ番号を入力します。

次の例では 1 番目のメールを読んでいます。

```
& t 1
Message 1:
From root@localhost  Mon Mar  8 14:05:52 2004
X-Original-To: username@localhost
Delivered-To: username@localhost
To: username@localhost
Subject: test
Date: Mon,  8 Mar 2004 14:05:52 +0200 (SAST)
From: root@localhost (Charlie Root)

This is a test message, please reply if you receive it.
```

この例のように、メッセージはすべてのヘッダ付きで表示されます。

メッセージ一覧をもう一度表示するには、`h` を押します。

メールに返信する必要がある場合は、`mail(1)` で `R` または `r` キーを押します。`R` はメールの送信者のみに返信するよう `mail(1)` に指示し、`r` は元のメッセージの他の受信者全員にも返信します。これらのコマンドの後ろに、返信対象となるメールの番号を付けることもできます。返信内容を入力し終えたら、1 行にピリオド（`.`）だけを単独で入力してメッセージの終わりを示します。

例を次に示します。

```
& R 1
To: root@localhost
Subject: Re: test

Thank you, I did get your email.
.
EOT
```

新しいメールを送信するには、`m` に続けて宛先メールアドレスを入力します。各アドレスをカンマ（`,`）で区切ることで複数の宛先を指定できます。続いてメッセージの件名を入力し、本文を入力します。メッセージの終わりには、1 行にピリオド（`.`）だけを単独で入力します。

```
& mail root@localhost
Subject: I mastered mail

Now I can send and receive email using mail ... :)
.
EOT
```

`mail(1)` の使用中は、いつでも `?` を押すとヘルプを表示できます。`mail(1)` の詳しい使い方については `mail(1)` を参照してください。

> **注**: `mail(1)` は添付ファイルを扱うようには設計されていないため、添付ファイルの処理は得意ではありません。より新しい MUA の方が、添付ファイルをより適切に扱えます。

<a id="mutt-command"></a>
### Mutt

Mutt は高機能な MUA であり、次のような多くの機能を備えています。

* メッセージのスレッド表示機能
* メールのデジタル署名および暗号化のための PGP サポート
* MIME サポート
* Maildir サポート
* 高いカスタマイズ性

Mutt の詳細については [http://www.mutt.org](http://www.mutt.org) を参照してください。

> **ヒント**: 追加機能を備えた NeoMutt という Mutt のフォークも知っておくとよいでしょう。詳細は [NeoMutt の Web サイト](https://neomutt.org/about.html)を参照してください。NeoMutt を選んだ場合は、以降のコマンド例の `mutt` を `neomutt` に読み替えてください。

Mutt は `mail/mutt` port を使ってインストールできます。インストールが完了したら、次のコマンドで Mutt を起動できます。

```shell
% mutt
```

Mutt は `/var/mail` にあるユーザーのメールボックスの内容を自動的に読み込み、表示します。メールが見つからない場合、Mutt はユーザーからのコマンド入力待ちになります。次の例は、Mutt がメッセージ一覧を表示している画面です。

![メッセージ一覧を表示している Mutt メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/mutt1.png)

メールを読むには、カーソルキーで選択して `Enter` を押します。Mutt でメールを表示した例を次に示します。

![メールを表示している Mutt メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/mutt2.png)

`mail(1)` と同様に、Mutt でも送信者のみへの返信と、受信者全員への返信を使い分けられます。送信者のみに返信するには `r` を押します。元の送信者とすべての受信者へグループ返信を送るには `g` を押します。

> **注**: デフォルトでは、Mutt はメールの作成や返信に `vi(1)` エディタを使用します。各ユーザーはホームディレクトリに `.muttrc` を作成または編集して `editor` 変数を設定するか、環境変数 `EDITOR` を設定することで、これをカスタマイズできます。Mutt の設定に関する詳細は [http://www.mutt.org/](http://www.mutt.org/) を参照してください。

新しいメールを作成するには `m` を押します。有効な件名を入力すると、メール本文を書けるように Mutt が `vi(1)` を起動します。本文を書き終えたら `vi` を保存して終了します。すると Mutt の画面に戻り、送信しようとしているメールの概要画面が表示されます。メールを送信するには `y` を押します。概要画面の例を次に示します。

![送信前の概要画面を表示している Mutt メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/mutt3.png)

Mutt には充実したヘルプが組み込まれており、ほとんどのメニューから `?` を押すことで参照できます。画面最上部にも、その場に応じたキーボードショートカットが表示されます。

<a id="alpine-command"></a>
### alpine

alpine は初心者ユーザーを主な対象としつつ、高度な機能もいくつか備えています。

> **警告**: alpine には過去に複数のリモート脆弱性が見つかっており、細工されたメールを送りつけることで、リモートの攻撃者がローカルシステム上のユーザー権限で任意のコードを実行できる問題がありました。*既知の*問題は修正されていますが、alpine のコードは安全性の低いスタイルで書かれており、FreeBSD Security Officer は他にも未発見の脆弱性が存在する可能性が高いと考えています。alpine のインストールはユーザー自身の責任で行ってください。

最新版の alpine は `mail/alpine` port を使ってインストールできます。インストールが完了したら、次のコマンドで alpine を起動できます。

```shell
% alpine
```

alpine を初めて起動すると、簡単な紹介と、クライアントの利用者数を把握するために匿名のメールメッセージを送信してほしいという alpine 開発チームからのお願いが書かれた挨拶ページが表示されます。この匿名メッセージを送信するには `Enter` を押します。匿名メッセージを送信せずに挨拶ページを終了するには `E` を押します。挨拶ページの例を次に示します。

![挨拶ページを表示している alpine メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/pine1.png)

続いてメインメニューが表示され、カーソルキーで移動できます。メインメニューには、新しいメールの作成、メールディレクトリの閲覧、アドレス帳エントリの管理といった操作へのショートカットが用意されています。メインメニューの下部には、現在の作業に応じた機能を実行するためのキーボードショートカットが表示されます。

alpine がデフォルトで開くディレクトリは `inbox` です。メッセージ一覧を表示するには、`I` を押すか、下の図にある `MESSAGE INDEX` 項目を選択します。

![デフォルトディレクトリを表示している alpine メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/pine2.png)

メッセージ一覧には現在のディレクトリ内のメッセージが表示され、カーソルキーで移動できます。強調表示されているメッセージは、`Enter` を押して読むことができます。

![メッセージ一覧を表示している alpine メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/pine3.png)

次のスクリーンショットは、alpine でサンプルメッセージを表示しているところです。画面下部には状況に応じたキーボードショートカットが表示されます。たとえば `r` は、現在表示中のメッセージに返信するよう MUA に指示するショートカットです。

![メールを表示している alpine メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/pine4.png)

alpine でのメールの返信には、alpine と一緒にデフォルトでインストールされる pico エディタが使用されます。pico はメッセージ内の移動が簡単で、初心者にとっては `vi(1)` や `mail(1)` よりも扱いやすいエディタです。返信を書き終えたら、`Ctrl+X` を押してメッセージを送信できます。alpine は送信前に確認を求めてきます。

![メッセージ作成画面を表示している alpine メールクライアント](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/mail/pine5.png)

alpine は、メインメニューの `SETUP` 項目からカスタマイズできます。


<a id="mail-advanced"></a>
## 高度なトピック

この節では、メールの詳細な設定やドメイン全体のメール構築といった、より高度なトピックを扱います。

<a id="mail-config"></a>
### 基本設定

`/etc/resolv.conf` が設定されているか、ネットワーク上から設定済みの DNS サーバーにアクセスできる環境であれば、初期状態のまま外部ホストへメールを送信できます。FreeBSD ホスト上の MTA でメールを受信するには、次のいずれかを行います。

* そのドメイン用の DNS サーバーを運用する。
* マシンの FQDN 宛てに直接メールを配送させる。

ホスト宛てに直接メールを配送させるには、動的 IP アドレスではなく固定の静的 IP アドレスが必要です。システムがファイアウォールの背後にある場合は、SMTP トラフィックを許可するよう設定しておく必要があります。ホストで直接メールを受信するには、次の 2 つのいずれかを設定します。

* DNS で最も番号の小さい MX レコードが、そのホストの静的 IP アドレスを指すようにする。
* DNS にそのホスト用の MX エントリを置かないようにする。

いずれかの設定を行えば、ホストで直接メールを受信できます。

次のコマンドを試してみてください。

```shell
# hostname
```

出力は次のようになります。

```
example.FreeBSD.org
```

```shell
# host example.FreeBSD.org
```

出力は次のようになります。

```
example.FreeBSD.org has address 204.216.27.XX
```

この例では、`example.FreeBSD.org` 上で本格的な MTA が正しく稼働していれば、[yourlogin@example.FreeBSD.org](mailto:yourlogin@example.FreeBSD.org) 宛てに直接送られたメールは問題なく届くはずです。なお、`dma(8)` は受信接続のためにポート 25 で待ち受けを行わないため、この構成では使用できません。

次に、以下の例を見てみます。

```shell
# host example.FreeBSD.org
```

出力は次のようになります。

```
example.FreeBSD.org has address 204.216.27.XX
example.FreeBSD.org mail is handled (pri=10) by nevdull.FreeBSD.org
```

この場合、`example.FreeBSD.org` 宛てのメールはすべて、ローカルホストへ直接送られる代わりに、`nevdull` 上の同じユーザー名で受け取られます。

上記の情報は DNS サーバーによって管理されています。メールの配送先情報を保持する DNS レコードは、[メールエクスチェンジャレコード（MX レコード）](https://en.wikipedia.org/wiki/MX_record)と呼ばれます。MX レコードが存在しない場合、メールはそのホストの IP アドレスを使って直接配送されます。

かつて `freefall.FreeBSD.org` の MX エントリは次のようになっていました。

```
freefall		MX	30	mail.crl.net
freefall		MX	40	agora.rdrop.com
freefall		MX	10	freefall.FreeBSD.org
freefall		MX	20	who.cdrom.com
```

`freefall` には多数の MX エントリがありました。最も番号の小さい MX が、到達可能であればメールを直接受信するホストです。何らかの理由でそのホストに到達できない場合は、次に番号の小さいホストが一時的にメッセージを受け取り、より番号の小さいホストが再び到達可能になった時点で転送します。

代替の MX サイトは、最大限の効果を発揮させるために別のインターネット回線を持つべきです。こうしたサービスは ISP が提供している場合があります。

<a id="mail-domain"></a>
### ドメイン宛てのメール

ネットワーク向けに MTA を設定する場合は、そのドメイン内の各ホスト宛てに送られたメールを MTA へ集約し、ユーザーがマスターメールサーバー上でメールを受け取れるようにします。

もっとも管理を簡単にするには、MTA 側と MUA を使うシステム側の両方に同じ*ユーザー名*のユーザーアカウントを用意します。ユーザーアカウントの作成には `adduser(8)` を使用します。

> **ヒント**: ホストにローカルユーザーを追加する以外にも、仮想ユーザー（virtual users）と呼ばれる代替手段があります。[Cyrus](https://www.cyrusimap.org/) や [Dovecot](https://www.dovecot.org/) などのプログラムを MTA と連携させると、ユーザー管理やメール保存に加え、POP3 や IMAP 経由でのアクセスも提供できます。

MTA は、ネットワーク上の各ワークステーションに対する指定メールエクスチェンジャとして設定する必要があります。これは DNS 設定で MX レコードを使って行います。

```
example.FreeBSD.org	A	204.216.27.XX		; Workstation
			MX	10 nevdull.FreeBSD.org	; Mailhost
```

これにより、A レコードがどこを指しているかにかかわらず、ワークステーション宛てのメールは MTA へ転送されます。メールは MX ホストへ送られます。

これは DNS サーバー上で設定する必要があります。ネットワーク内で独自の DNS サーバーを運用していない場合は、ISP または DNS プロバイダーに相談してください。

次に、仮想メールホスティングの例を示します。

ドメイン `customer1.org` を持つ顧客がいて、`customer1.org` 宛てのメールをすべて `mail.myhost.com` へ送りたいとします。

DNS エントリは次のようになります。

```
customer1.org		MX	10	mail.myhost.com
```

そのドメインのメールだけを扱うのであれば、`customer1.org` に `A` レコードは*不要*です。ただし、`A` レコードが存在しない場合、`customer1.org` に対して `ping` を実行しても応答は得られません。

続いて、どのドメインやホスト名宛てのメールを受理するかを MTA に指示します。Sendmail では次のいずれかの方法が使えます。

* `FEATURE(use_cw_file)` を使用している場合は、`/etc/mail/local-host-names` にホスト名を追加する。
* `/etc/sendmail.cf` に `Cwyour.host.com` の行を追加する。（訳注: 原文では `/etc/sendmail.cf` と記載されていますが、FreeBSD の Sendmail マスター設定ファイルは通常 `/etc/mail/sendmail.cf` に配置されます。）

<a id="outgoing-only"></a>
### 送信専用の設定

リレー経由でメールを送信するだけでよいケースは数多くあります。たとえば次のような場合です。

* デスクトップマシンであり、ISP のメールリレーを使って `mail(1)` などのプログラムを利用したい場合。
* ローカルではメールを処理しないサーバーであり、すべてのメールをリレーへ渡して処理させたい場合。

どの MTA でもこうした用途に対応できますが、メールを外部へ送り出すためだけに本格的な MTA を正しく設定するのは手間がかかります。この用途には Sendmail や Postfix のようなプログラムは大げさすぎます。

さらに、一般的なインターネット接続サービスの利用規約では、「メールサーバー」の運用が禁止されていることもあります。

こうした要件を満たすもっとも簡単な方法は、[ベースシステム](#configuring-dragonfly-mail-agent)に含まれる `dma(8)` MTA を使うことです。FreeBSD 13.2 までのシステムでは、Ports からインストールする必要があります。

`dma(8)` 以外にも、`mail/ssmtp` のようなサードパーティ製ソフトウェアを使って同じ目的を達成できます。

```shell
# cd /usr/ports/mail/ssmtp
# make install replace clean
```

インストールが完了したら、`/usr/local/etc/ssmtp/ssmtp.conf` で `mail/ssmtp` を設定します。

```
root=yourrealemail@example.com
mailhub=mail.example.com
rewriteDomain=example.com
hostname=_HOSTNAME_
```

`root` には実際のメールアドレスを指定します。`mail.example.com` の部分には ISP の送信メールリレーを入力します。ISP によっては、これを「送信メールサーバー（outgoing mail server）」や「SMTP サーバー」と呼ぶこともあります。

送信メールサービスを含め、Sendmail を必ず無効化しておいてください。

`mail/ssmtp` には他にもいくつかのオプションが用意されています。詳細は `/usr/local/etc/ssmtp` にある設定例や `ssmtp` の man ページを参照してください。

このように `ssmtp` を設定しておけば、ISP の利用規約に違反したり、スパム送信に悪用されたりすることなく、コンピュータ上でメール送信を必要とするソフトウェアを正常に動作させることができます。

<a id="SMTP-Auth"></a>
### Sendmail における SMTP 認証

MTA で SMTP 認証を設定すると、さまざまな利点があります。SMTP 認証は Sendmail にセキュリティの層を追加するだけでなく、接続元ホストを移動するモバイルユーザーが、毎回メールクライアントの設定を変更しなくても同じ MTA を使えるようにしてくれます。

Ports Collection から `security/cyrus-sasl2` をインストールします。この port には多数のコンパイル時オプションがあります。この例で示す SMTP 認証方式を使うには、`LOGIN` が無効化されていないことを確認してください。

`security/cyrus-sasl2` をインストールしたら、`/usr/local/lib/sasl2/Sendmail.conf` を編集（存在しない場合は新規作成）し、次の行を追加します。

```
pwcheck_method: saslauthd
```

次に、`security/cyrus-sasl2-saslauthd` をインストールし、次のコマンドを実行します。

```shell
# sysrc saslauthd_enable="YES"
```

最後に、`saslauthd` デーモンを起動します。

```shell
# service saslauthd start
```

このデーモンは、Sendmail が FreeBSD の `passwd(5)` データベースに対して認証を行う際の仲介役として機能します。これにより、SMTP 認証を使うユーザーごとに新しいユーザー名とパスワードの組を作り直す手間が省け、ログインパスワードとメールパスワードを同じに保つことができます。

次に、`/etc/make.conf` を編集し、以下の行を追加します。

```
SENDMAIL_CFLAGS=-I/usr/local/include/sasl -DSASL
SENDMAIL_LDADD=/usr/local/lib/libsasl2.so
```

これらの行は、Sendmail のコンパイル時に `cyrus-sasl2` とリンクするための適切な設定オプションを指定します。Sendmail を再コンパイルする前に、`cyrus-sasl2` がインストール済みであることを確認してください。

次のコマンドを実行して Sendmail を再コンパイルします。

```shell
# cd /usr/src/lib/libsmutil
# make cleandir && make obj && make
# cd /usr/src/lib/libsm
# make cleandir && make obj && make
# cd /usr/src/usr.sbin/sendmail
# make cleandir && make obj && make && make install
```

`/usr/src` に大幅な変更が加えられておらず、必要な共有ライブラリが揃っていれば、このコンパイルは問題なく完了するはずです。

Sendmail のコンパイルと再インストールが終わったら、`/etc/mail/freebsd.mc` またはローカルの `.mc` ファイルを編集します。一意性を保つため、`hostname(1)` の出力を `.mc` ファイル名として使う管理者も多くいます。

次の行を追加します。

```
dnl set SASL options
TRUST_AUTH_MECH(`GSSAPI DIGEST-MD5 CRAM-MD5 LOGIN')dnl
define(`confAUTH_MECHANISMS', `GSSAPI DIGEST-MD5 CRAM-MD5 LOGIN')dnl
```

これらのオプションは、Sendmail がユーザー認証に使用できる各種方式を設定します。`pwcheck` 以外の方式を使う場合は、Sendmail のドキュメントを参照してください。

最後に、`/etc/mail` ディレクトリ内で `make(1)` を実行します。これにより新しい `.mc` が処理され、`freebsd.cf` またはローカルの `.mc` で使用した名前の `.cf` ファイルが生成されます。

続いて `make install restart` を実行すると、そのファイルが `sendmail.cf` へコピーされ、Sendmail が適切に再起動されます。

この処理の詳細は `/etc/mail/Makefile` を参照してください。

設定をテストするには、MUA を使ってテストメッセージを送信します。さらに詳しく調査したい場合は、Sendmail の `LogLevel` を `13` に設定し、`/var/log/maillog` にエラーが出力されないか確認してください。

詳細については、[SMTP authentication](http://www.sendmail.org/~ca/email/auth.html) を参照してください。
