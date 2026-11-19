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
