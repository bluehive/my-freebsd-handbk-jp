<a id="appendix-A-heading-01"></a>
# 付録A FreeBSDの入手（Obtaining FreeBSD）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/mirrors/)の「Appendix A. Obtaining FreeBSD」（既存 TOC ID A）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/mirrors/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::`（`shared/authors.adoc`、`shared/mirrors.adoc`、`shared/releases.adoc`、`attributes`、`teams.adoc`、`mailing-lists.adoc`、`urls.adoc`、`asciidoctor.adoc`）は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンド例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザーのプロンプトを示します。

<a id="mirrors"></a>
## ミラー（Mirrors）

FreeBSD プロジェクトの公式ミラーは、プロジェクトのクラスター管理者が運用する多数のマシンで構成されており、GeoDNS によって利用者を最も近い利用可能なミラーへ案内します。
現在の拠点は、オーストラリア、ブラジル、フランス、日本（2 拠点）、マレーシア、南アフリカ、スウェーデン、台湾、アメリカ合衆国（カリフォルニア州 2 拠点、イリノイ州 2 拠点、ニュージャージー州、ワシントン州）です。

公式ミラーサービスは次のとおりです。

| サービス名 | プロトコル | 詳細情報 |
|---|---|---|
| **cgit.FreeBSD.org** | [https](https://cgit.FreeBSD.org/) | FreeBSD Git リポジトリの Web インターフェース。 |
| **docs.FreeBSD.org** | [https](https://docs.FreeBSD.org/) | FreeBSD ドキュメンテーションポータル。 |
| **download.FreeBSD.org** | [https](https://download.FreeBSD.org/) [ftp](ftp://download.FreeBSD.org/pub/FreeBSD/) | `ftp.FreeBSD.org` と同じ内容です。`ftp` は旧名称であり、`download.FreeBSD.org` の利用を推奨します。 |
| **git.FreeBSD.org** | `https` および `ssh` 経由の git | 詳細は [Git の利用](#git)節を参照してください。 |
| **pkg.FreeBSD.org** | `http` および `https` 経由の `pkg(8)` | `pkg(8)` プログラムが使用する FreeBSD 公式パッケージリポジトリ。 |
| **vuxml.FreeBSD.org** / **www.VuXML.org** | [https](https://www.vuxml.org/) | FreeBSD プロジェクトの VuXML Web ページ。`pkg audit` はこのサービスから脆弱性一覧を取得します。 |
| **www.FreeBSD.org** | [https](https://www.FreeBSD.org/) | FreeBSD Web サイト。 |

すべての公式ミラーは IPv4 と IPv6 に対応しています。

http://ftp-archive.FreeBSD.org は GeoDNS インフラストラクチャには含まれておらず、1 拠点（米国）のみでホストされています。

プロジェクトでは新たな拠点を募集しています。スポンサーを希望される場合は、詳細についてクラスター管理者チーム（Cluster Administrators team）までお問い合わせください。

**download.FreeBSD.org** と **pkg.FreeBSD.org** の配信には [Fastly](https://www.fastly.com) CDN が利用されており、FreeBSD のイメージやパッケージの高速化、キャッシュ、およびグローバルな帯域分散を提供しています。

コミュニティや他社によって維持されているミラーの一覧は次のとおりです。

| 国 | ホスト名 | プロトコル |
|---|---|---|
| オーストラリア（[連絡先](mailto:hostmaster@au.FreeBSD.org)） | ftp.au.FreeBSD.org | [http](http://ftp.au.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.au.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.au.FreeBSD.org) [rsync_v6](rsync://ftp.au.FreeBSD.org) |
| | ftp3.au.FreeBSD.org | [http](http://ftp3.au.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp3.au.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp3.au.FreeBSD.org) |
| アゼルバイジャン（[連絡先](mailto:orkhan@our.az)） | ftp1.az.FreeBSD.org | [http](http://ftp1.az.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp1.az.FreeBSD.org) |
| ブラジル（[連絡先](mailto:hostmaster@br.FreeBSD.org)） | ftp2.br.FreeBSD.org | [http](http://ftp2.br.FreeBSD.org/FreeBSD) [rsync](rsync://ftp2.br.FreeBSD.org) [rsync_v6](rsync://ftp2.br.FreeBSD.org) |
| | ftp3.br.FreeBSD.org | [http](http://ftp3.br.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp3.br.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp3.br.FreeBSD.org) |
| ブルガリア（[連絡先](mailto:mirror@telepoint.bg)） | ftp.bg.FreeBSD.org | [ftp](ftp://ftp.bg.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.bg.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.bg.FreeBSD.org) [rsync_v6](rsync://ftp.bg.FreeBSD.org) |
| チェコ（[連絡先](mailto:hostmaster@cz.FreeBSD.org)） | ftp.cz.FreeBSD.org | [http](http://ftp.cz.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.cz.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.cz.FreeBSD.org) [rsync_v6](rsync://ftp.cz.FreeBSD.org) |
| デンマーク（[連絡先](mailto:staff@dotsrc.org)） | ftp.dk.FreeBSD.org | [http](http://ftp.dk.FreeBSD.org/FreeBSD/) [http_v6](http://ftp.dk.FreeBSD.org/FreeBSD/) [ftp](ftp://ftp.dk.FreeBSD.org/FreeBSD/) [ftp_v6](ftp://ftp.dk.FreeBSD.org/FreeBSD/) [rsync](rsync://ftp.dk.FreeBSD.org/FreeBSD/) [rsync_v6](rsync://ftp.dk.FreeBSD.org/FreeBSD/) |
| フィンランド（[連絡先](mailto:hostmaster@fi.FreeBSD.org)） | ftp.fi.FreeBSD.org | [ftp](ftp://ftp.fi.FreeBSD.org/pub/FreeBSD) |
| フランス（[連絡先](mailto:hostmaster@fr.FreeBSD.org)） | ftp.fr.FreeBSD.org | [http](http://ftp.fr.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.fr.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.fr.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.fr.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.fr.FreeBSD.org) [rsync_v6](rsync://ftp.fr.FreeBSD.org) |
| | ftp3.fr.FreeBSD.org | [ftp](ftp://ftp3.fr.FreeBSD.org/pub/FreeBSD) |
| | ftp6.fr.FreeBSD.org | [http](http://ftp6.fr.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp6.fr.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp6.fr.FreeBSD.org) |
| ドイツ（[連絡先](mailto:de-bsd-hubs@de.FreeBSD.org)） | ftp.de.FreeBSD.org | [http](http://ftp.de.FreeBSD.org/FreeBSD) [http_v6](http://ftp.de.FreeBSD.org/FreeBSD) [https](https://ftp.de.FreeBSD.org/FreeBSD) [https_v6](https://ftp.de.FreeBSD.org/FreeBSD) [ftp](ftp://ftp.de.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.de.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.de.FreeBSD.org/FreeBSD) [rsync_v6](rsync://ftp.de.FreeBSD.org/FreeBSD) |
| | ftp1.de.FreeBSD.org | [http](http://ftp1.de.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp1.de.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp1.de.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp1.de.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp1.de.FreeBSD.org) [rsync_v6](rsync://ftp1.de.FreeBSD.org) |
| | ftp2.de.FreeBSD.org | [http](http://ftp2.de.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp2.de.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp2.de.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp2.de.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp2.de.FreeBSD.org) [rsync_v6](rsync://ftp2.de.FreeBSD.org) |
| | ftp5.de.FreeBSD.org | [ftp](ftp://ftp5.de.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp5.de.FreeBSD.org/pub/FreeBSD) |
| | ftp7.de.FreeBSD.org | [http](http://ftp7.de.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp7.de.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp7.de.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp7.de.FreeBSD.org/pub/FreeBSD) |
| ギリシャ（[連絡先](mailto:hostmaster@gr.FreeBSD.org)） | ftp.gr.FreeBSD.org | [http](http://ftp.gr.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.gr.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.gr.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.gr.FreeBSD.org/pub/FreeBSD) |
| | ftp2.gr.FreeBSD.org | [http](http://ftp2.gr.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp2.gr.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp2.gr.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp2.gr.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp2.gr.FreeBSD.org) |
| 日本（[連絡先](mailto:hostmaster@jp.FreeBSD.org)） | ftp.jp.FreeBSD.org | [http](http://ftp.jp.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.jp.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.jp.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.jp.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.jp.FreeBSD.org) [rsync_v6](rsync://ftp.jp.FreeBSD.org) |
| | ftp2.jp.FreeBSD.org | [ftp](ftp://ftp2.jp.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp2.jp.FreeBSD.org) [rsync_v6](rsync://ftp2.jp.FreeBSD.org) |
| | ftp3.jp.FreeBSD.org | [http](http://ftp3.jp.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp3.jp.FreeBSD.org) |
| | ftp4.jp.FreeBSD.org | [ftp](ftp://ftp4.jp.FreeBSD.org/pub/FreeBSD) |
| | ftp6.jp.FreeBSD.org | [http](http://ftp6.jp.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp6.jp.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp6.jp.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp6.jp.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp6.jp.FreeBSD.org) [rsync_v6](rsync://ftp6.jp.FreeBSD.org) |
| カザフスタン（[連絡先](mailto:support@ps.kz)） | mirror.ps.kz | [http](http://mirror.ps.kz/freebsd) [ftp](ftp://mirror.ps.kz/freebsd) |
| | mirror.neolabs.kz | [http](http://mirror.neolabs.kz/freebsd) [ftp](ftp://mirror.neolabs.kz/freebsd) |
| 韓国（[連絡先](mailto:hostmaster@kr.FreeBSD.org)） | ftp.kr.FreeBSD.org | [http](http://ftp.kr.FreeBSD.org/pub/FreeBSD) [https](https://ftp.kr.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.kr.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.kr.FreeBSD.org) |
| | ftp2.kr.FreeBSD.org | [rsync](rsync://ftp2.kr.FreeBSD.org) |
| ラトビア（[連絡先](mailto:hostmaster@lv.FreeBSD.org)） | ftp.lv.FreeBSD.org | [http](http://ftp.lv.FreeBSD.org/freebsd) [ftp](ftp://ftp.lv.FreeBSD.org/freebsd) |
| オランダ（[連絡先](mailto:hostmaster@nl.FreeBSD.org)） | ftp.nl.FreeBSD.org | [http](http://ftp.nl.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.nl.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.nl.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.nl.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.nl.FreeBSD.org) [rsync_v6](rsync://ftp.nl.FreeBSD.org) |
| | ftp2.nl.FreeBSD.org | [http](http://ftp2.nl.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp2.nl.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp2.nl.FreeBSD.org) |
| | mirror.nl.altushost.com | [https](https://mirror.nl.altushost.com/FreeBSD) |
| ニュージーランド（[連絡先](mailto:hostmaster@nz.FreeBSD.org)） | ftp.nz.FreeBSD.org | [http](http://ftp.nz.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.nz.FreeBSD.org/pub/FreeBSD) |
| ノルウェー（[連絡先](mailto:hostmaster@no.FreeBSD.org)） | ftp.no.FreeBSD.org | [ftp](ftp://ftp.no.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.no.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.no.FreeBSD.org) [rsync_v6](rsync://ftp.no.FreeBSD.org) |
| ポーランド（[連絡先](mailto:hostmaster@pl.FreeBSD.org)） | ftp.pl.FreeBSD.org | [http](http://ftp.pl.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.pl.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.pl.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.pl.FreeBSD.org) [rsync_v6](rsync://ftp.pl.FreeBSD.org) |
| ロシア（[連絡先](mailto:hostmaster@ru.FreeBSD.org)） | ftp.ru.FreeBSD.org | [http](http://ftp.ru.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.ru.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.ru.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.ru.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.ru.FreeBSD.org) [rsync_v6](rsync://ftp.ru.FreeBSD.org) |
| | ftp2.ru.FreeBSD.org | [https](https://ftp2.ru.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp2.ru.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp2.ru.FreeBSD.org) |
| スロベニア（[連絡先](mailto:hostmaster@si.FreeBSD.org)） | ftp.si.FreeBSD.org | [http](http://ftp.si.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.si.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.si.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.si.FreeBSD.org/pub/FreeBSD) |
| 南アフリカ（[連絡先](mailto:hostmaster@za.FreeBSD.org)） | ftp2.za.FreeBSD.org | [http](http://ftp2.za.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp2.za.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp2.za.FreeBSD.org/pub/FreeBSD) |
| | ftp4.za.FreeBSD.org | [http](http://ftp4.za.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp4.za.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp4.za.FreeBSD.org) |
| スウェーデン（[連絡先](mailto:hostmaster@se.FreeBSD.org)） | ftp.se.FreeBSD.org | [http](http://ftp.se.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.se.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.se.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.se.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.se.FreeBSD.org) [rsync_v6](rsync://ftp.se.FreeBSD.org) |
| | mirror.se.altushost.com | [https](https://mirror.se.altushost.com/FreeBSD) |
| 台湾（[連絡先](mailto:hostmaster@tw.FreeBSD.org)） | ftp4.tw.FreeBSD.org | [https](https://ftp4.tw.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp4.tw.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp4.tw.FreeBSD.org) |
| | ftp5.tw.FreeBSD.org | [http](http://ftp5.tw.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp5.tw.FreeBSD.org/pub/FreeBSD) |
| ウクライナ（[連絡先](mailto:hostmaster@ua.FreeBSD.org)） | ftp.ua.FreeBSD.org | [http](http://ftp.ua.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.ua.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.ua.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.ua.FreeBSD.org) [rsync_v6](rsync://ftp.ua.FreeBSD.org) |
| 英国（[連絡先](mailto:hostmaster@uk.FreeBSD.org)） | ftp.uk.FreeBSD.org | [http](http://ftp.uk.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp.uk.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp.uk.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp.uk.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp.uk.FreeBSD.org) [rsync_v6](rsync://ftp.uk.FreeBSD.org) |
| | ftp2.uk.FreeBSD.org | [http](http://ftp2.uk.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp2.uk.FreeBSD.org/pub/FreeBSD) [https](https://ftp2.uk.FreeBSD.org/pub/FreeBSD) [https_v6](https://ftp2.uk.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp2.uk.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp2.uk.FreeBSD.org/pub/FreeBSD) |
| アメリカ合衆国（[連絡先](mailto:hostmaster@us.FreeBSD.org)） | ftp11.FreeBSD.org | [http](http://ftp11.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp11.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp11.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp11.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp11.FreeBSD.org) [rsync_v6](rsync://ftp11.FreeBSD.org) |
| | ftp14.FreeBSD.org | [ftp](ftp://ftp14.FreeBSD.org/pub/FreeBSD) [rsync](rsync://ftp14.FreeBSD.org)（旧公式 Tier 1） |
| | ftp5.FreeBSD.org | [http](http://ftp5.FreeBSD.org/pub/FreeBSD) [http_v6](http://ftp5.FreeBSD.org/pub/FreeBSD) [ftp](ftp://ftp5.FreeBSD.org/pub/FreeBSD) [ftp_v6](ftp://ftp5.FreeBSD.org/pub/FreeBSD) |

> **訳注**: 上記の表における各国の連絡先メールアドレスは、同じ固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28` の `shared/mirrors.adoc` の定義（`{mirrors-*-email}` 属性）を解決したものです。

コミュニティミラーが対応するプロトコルの現行一覧は 2022-01-31 が最終更新日であり、現在の状況は保証されていません。

<a id="git"></a>
## Git の利用

> **訳注**: 原文ではこの見出しの下に本文がなく、内容は以下の小節にあります。

<a id="git-intro"></a>
### はじめに

2020 年 12 月以降、FreeBSD はベースシステムのソースコードとドキュメントすべてを格納する主要なバージョン管理システムとして Git を使用しています。
2021 年 4 月以降、FreeBSD は Ports Collection すべてを格納する唯一のバージョン管理システムとして Git を使用しています。

> **注**: Git は一般に開発者向けのツールです。FreeBSD ベースシステムの更新には、`freebsd-update`（[FreeBSD Update](27-cutting-edge.md#updating-upgrading-freebsdupdate)）の利用を好むユーザーも多いでしょう。

この節では、FreeBSD システムに Git をインストールし、FreeBSD のソースコードリポジトリのローカルコピーを作成する方法を説明します。

<a id="git-install"></a>
### インストール

Git は Ports Collection から、またはパッケージとしてインストールできます。

```shell
# pkg install git
```

<a id="git-usage"></a>
### Git の実行

ソースのクリーンなコピーをローカルディレクトリへ取得するには、`git clone` を使用します。
このファイル群を格納するディレクトリを*作業ツリー（working tree）*と呼びます。

Git はリポジトリの指定に URL を用います。
リポジトリは 3 種類あり、FreeBSD システムのソースコード用の `src`、ドキュメント用の `doc`、FreeBSD Ports Collection 用の `ports` です。
いずれも HTTPS と SSH の 2 種類のプロトコルで利用できます。
たとえば、`https://git.FreeBSD.org/src.git` という URL は、`https` プロトコルを使って `src` リポジトリの `main` ブランチを指定します。

<a id="git-url-table"></a>
**表: FreeBSD Git リポジトリ URL 一覧**

| 項目 | Git URL |
|---|---|
| HTTPS 経由の読み取り専用 src リポジトリ | `https://git.FreeBSD.org/src.git` |
| 匿名 SSH（anon-ssh）経由の読み取り専用 src リポジトリ | `ssh://anongit@git.FreeBSD.org/src.git` |
| HTTPS 経由の読み取り専用 doc リポジトリ | `https://git.FreeBSD.org/doc.git` |
| 匿名 SSH（anon-ssh）経由の読み取り専用 doc リポジトリ | `ssh://anongit@git.FreeBSD.org/doc.git` |
| HTTPS 経由の読み取り専用 ports リポジトリ | `https://git.FreeBSD.org/ports.git` |
| 匿名 SSH（anon-ssh）経由の読み取り専用 ports リポジトリ | `ssh://anongit@git.FreeBSD.org/ports.git` |

プロジェクトメンバーが維持している外部ミラーも利用できます。[外部ミラー](#external-mirrors)節を参照してください。

FreeBSD システムのソースコードリポジトリのコピーをクローンするには、次のように実行します。

```shell
# git clone -o freebsd https://git.FreeBSD.org/src.git /usr/src
```

`-o freebsd` オプションはオリジン（リモート名）を指定するもので、FreeBSD ドキュメントの慣例ではオリジンを `freebsd` と想定しています。
初回のチェックアウトではリモートリポジトリのブランチ全体をダウンロードする必要があるため、時間がかかることがあります。
しばらくお待ちください。

初期状態では、作業ツリーには CURRENT に対応する `main` ブランチのソースコードが含まれています。
代わりに 13-STABLE へ切り替えるには、次のように実行します。

```shell
# cd /usr/src
# git checkout stable/13
```

作業ツリーは `git pull` で更新できます。
上記の例で作成した `/usr/src` を更新するには、次のように実行します。

```shell
# cd /usr/src
# git pull --rebase
```

更新は変更されたファイルのみを転送するため、初回のチェックアウトよりもはるかに高速です。

<a id="appendix-A-heading-07"></a>
### Web ベースのリポジトリブラウザ

FreeBSD プロジェクトでは、Web ベースのリポジトリブラウザとして cgit を使用しています（[https://cgit.FreeBSD.org/](https://cgit.FreeBSD.org/)）。

<a id="appendix-A-heading-08"></a>
### 開発者向け情報

リポジトリへの書き込みアクセスについては、[Committer's Guide](https://docs.freebsd.org/en/articles/committers-guide/#git-mini-primer) を参照してください。

<a id="external-mirrors"></a>
### 外部ミラー

以下のミラーは FreeBSD.org 上ではホストされていませんが、プロジェクトメンバーによって維持されています。
ユーザーや開発者は、これらのミラーからリポジトリを pull したり閲覧したりすることができます。
GitHub の `doc` および `src` リポジトリではプルリクエストを受け付けていますが、それ以外のミラーにおけるプロジェクトのワークフローは引き続き議論中です。

**Codeberg**

* doc: https://codeberg.org/FreeBSD/freebsd-doc
* ports: https://codeberg.org/FreeBSD/freebsd-ports
* src: https://codeberg.org/FreeBSD/freebsd-src

**GitHub**

* doc: https://github.com/freebsd/freebsd-doc
* ports: https://github.com/freebsd/freebsd-ports
* src: https://github.com/freebsd/freebsd-src

**GitLab**

* doc: https://gitlab.com/FreeBSD/freebsd-doc
* ports: https://gitlab.com/FreeBSD/freebsd-ports
* src: https://gitlab.com/FreeBSD/freebsd-src

<a id="appendix-A-heading-10"></a>
### メーリングリスト

FreeBSD プロジェクトにおける Git の一般的な利用方法や質問に関する主要なメーリングリストは [freebsd-git](https://lists.freebsd.org/subscription/freebsd-git) です。
コミットメッセージ用メーリングリストなどの詳細については、[メーリングリスト（Mailing Lists）](https://docs.freebsd.org/en/books/handbook/eresources/#eresources-mail)の章を参照してください。

<a id="appendix-A-heading-11"></a>
### SSH ホスト鍵

* `gitrepo.FreeBSD.org` のホスト鍵フィンガープリント:
  * ECDSA 鍵のフィンガープリント: `SHA256:seWO5D27ySURcx4bknTNKlC1mgai0whP443PAKEvvZA`
  * ED25519 鍵のフィンガープリント: `SHA256:lNR6i4BEOaaUhmDHBA1WJsO7H3KtvjE2r5q4sOxtIWo`
  * RSA 鍵のフィンガープリント: `SHA256:f453CUEFXEJAXlKeEHV+ajJfeEfx9MdKQUD7lIscnQI`

* `git.FreeBSD.org` のホスト鍵フィンガープリント:
  * ECDSA 鍵のフィンガープリント: `SHA256:/UlirUAsGiitupxmtsn7f9b7zCWd0vCs4Yo/tpVWP9w`
  * ED25519 鍵のフィンガープリント: `SHA256:y1ljKrKMD3lDObRUG3xJ9gXwEIuqnh306tSyFd1tuZE`
  * RSA 鍵のフィンガープリント: `SHA256:jBe6FQGoH4HjvrIVM23dcnLZk9kmpdezR/CvQzm7rJM`

これらは DNS の SSHFP レコードとしても公開されています。
