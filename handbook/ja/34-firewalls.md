<a id="firewalls"></a>
# 第34章 ファイアウォール（Firewalls）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/firewalls/)の「Chapter 34. Firewalls」を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/firewalls/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。本リポジトリの未翻訳章への相互参照は公式 FreeBSD Handbook（英語版）へリンクしています。また、掲載されているコマンド・設定例・ルールセットの FreeBSD 実機での動作確認および第三者による専門校閲は未実施です。

<a id="firewalls-intro"></a>
## 概要

ファイアウォールを使うと、システムを通過する送受信トラフィックをフィルタリングできます。
ネットワーク接続を出入りするパケットを1組または複数の「ルール（規則）」で検査し、通信を許可するか遮断するかを決めます。
ファイアウォールのルールでは、プロトコルの種類、送信元や宛先のホストアドレス、送信元や宛先のポート番号など、パケットのさまざまな属性を検査できます。

ファイアウォールはホストやネットワークのセキュリティを高めます。たとえば、次のような目的で利用します。

* 内部ネットワーク上のアプリケーション、サービス、マシンを、パブリックインターネットからの不要なトラフィックから保護し隔離する。
* 内部ネットワークのホストからパブリックインターネット上のサービスへのアクセスを制限または無効化する。
* ネットワークアドレス変換（NAT）を提供する。これにより、内部ネットワークでプライベート IP アドレスを使いながら、単一の IP アドレスまたは自動割り当てされたパブリックアドレスの共有プールを使って、パブリックインターネットへの1本の接続を共有できる。

FreeBSD のベースシステムには、PF、IPFW、IPFILTER（IPF とも呼ばれます）の3種類のファイアウォールが組み込まれています。
さらに FreeBSD は、帯域幅の使用量を制御する2種類のトラフィックシェーパー（`altq(4)` と `dummynet(4)`）も備えています。
従来、ALTQ は PF と、dummynet は IPFW と密接に結びついています。
いずれのファイアウォールもルールを使って FreeBSD システムに出入りするパケットのアクセスを制御しますが、仕組みやルールの構文はそれぞれ異なります。

FreeBSD が複数のファイアウォールを用意しているのは、利用者の多様な要件や好みに応えるためです。
どのファイアウォールが自分の用途に最も合うかは、利用者ごとに検討して選ぶとよいでしょう。

本章で学ぶ内容は次のとおりです。

* パケットフィルタリングルールの定義方法
* FreeBSD に組み込まれている各ファイアウォールの違い
* PF ファイアウォールの設定方法と使い方
* IPFW ファイアウォールの設定方法と使い方
* IPFILTER ファイアウォールの設定方法と使い方

本章を読む前に、次の知識があると理解しやすくなります。

* FreeBSD とインターネットの基本的な概念を理解していること

> **注記**: すべてのファイアウォールは、指定されたパケット制御フィールドの値を検査することで動作します。そのため、ファイアウォールのルールセットを作成する人は、TCP/IP がどのように動くのか、パケット制御フィールドにどのような値が入るのか、そして通常のセッション通信でそれらの値がどう使われるのかを理解している必要があります。入門資料としては [Daryl's TCP/IP Primer](https://www.ipprimer.com) が参考になります。

<a id="firewalls-concepts"></a>
## ファイアウォールの基本概念

ルールセットとは、パケットに含まれる値に基づいてパケットを通過（pass）させたり遮断（block）したりするルールの集まりです。
ホスト間で双方向にパケットをやり取りすることで、1つのセッション通信が成り立ちます。
ファイアウォールのルールセットは、パブリックインターネットから届くパケットだけでなく、それに対する応答としてシステムが生成するパケットも処理します。
各 TCP/IP サービスは、プロトコルと待ち受けポート（listening port）によってあらかじめ定義されています。
特定のサービス宛てのパケットは、送信元アドレスの非特権ポートから発信され、宛先アドレスの特定のサービスポートを標的にします。
これらのパラメータはすべて、サービスを通過または遮断するルールを作る際の選択条件として使えます。

不明なポート番号を調べたい場合は、`/etc/services` を参照してください。
あるいは [Wikipedia の TCP および UDP ポート番号一覧](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers) を訪れてポート番号を検索し、特定のポートの用途を調べることもできます。

トロイの木馬が使われるポート番号については、[port numbers used by Trojans（Web Archive）](https://web.archive.org/web/20150803024617/http://www.sans.org/security-resources/idfaq/oddports.php) を参照してください。

FTP にはアクティブモード（active mode）とパッシブモード（passive mode）の2つの動作モードがあります。
両者の違いは、データチャネルをどのように確立するかにあります。
パッシブモードでは通常の FTP セッションを要求する側がデータチャネルを開くため、より安全です。
FTP と各モードの詳しい解説については、[http://www.slacksite.com/other/ftp.html](http://www.slacksite.com/other/ftp.html) を参照してください。

ファイアウォールのルールセットには、「排他的（exclusive）」と「包含的（inclusive）」の2種類があります。
排他的なファイアウォールは、ルールセットに一致するトラフィックだけを除いて、すべての通信を通過させます。
一方、包含的なファイアウォールはその逆で、ルールに一致するトラフィックだけを通過させ、それ以外はすべて遮断します。

包含的なファイアウォールは、外向きトラフィックをより細かく制御できるため、パブリックインターネットへサービスを提供するシステムに適しています。
また、パブリックインターネットから発信されてプライベートネットワークへ入ってくるトラフィックの種類も制御できます。
ルールに一致しないトラフィックはすべて遮断され、ログに記録されます。
包含的なファイアウォールは不要な通信を誤って許可する危険を大幅に減らせるため、一般に排他的なファイアウォールより安全です。

> **注記**: 特に断りがない限り、本章で示す設定例とルールセットの例はすべて包含的なファイアウォールルールセットを作成します。

「ステートフルファイアウォール（stateful firewall）」を使うと、セキュリティをさらに高められます。
この種のファイアウォールは、開いている接続（コネクション）の状態を追跡し、既存の接続に一致するトラフィックか、新しく許可された接続を開くトラフィックだけを許可します。

ステートフルフィルタリングでは、トラフィックを1つのセッションを構成する双方向のパケット交換として扱います。
一致ルールにステート（状態保持）を指定すると、ファイアウォールはそのセッション中にやり取りされると見込まれる各パケット用の内部ルールを動的に生成します。
そして、あるパケットがそのセッションに対して正当なものかを判定できるだけの十分な照合機能を備えています。
セッションのひな型に正しく当てはまらないパケットは、自動的に拒否されます。

セッションが完了すると、その情報は動的なステートテーブル（状態表）から削除されます。

ステートフルフィルタリングを使うと、新しいセッションを遮断するか通過させるかだけに集中してルールを書けます。
新しいセッションが許可されれば、その後に続くパケットはすべて自動的に許可され、なりすましパケットは自動的に拒否されます。
逆に新しいセッションが遮断されれば、後続のパケットは一切許可されません。
ステートフルフィルタリングは高度な照合機能を備えており、攻撃者が仕掛けるさまざまな攻撃手法の洪水からシステムを守ることができます。

NAT は *Network Address Translation*（ネットワークアドレス変換）の略です。
NAT 機能を使うと、ファイアウォールの背後にあるプライベート LAN 内の複数台で、ISP から割り当てられた1つの IP アドレスを共有できます（動的割り当ての場合でも利用可能です）。
そのため、LAN 上の各コンピュータがインターネットにアクセスするために、ISP と複数のインターネットアカウントや複数の IP アドレスを契約する必要がなくなります。

NAT は、LAN 内の各システムからパブリックインターネットへ向けてパケットがファイアウォールを出る際、プライベート LAN の IP アドレスを単一のパブリック IP アドレスへ自動的に変換します。
また、戻ってくるパケットに対してはその逆変換を行います。

RFC 1918 により、パブリックインターネットへ直接ルーティングされることのないプライベートネットワーク向けアドレス範囲として次のものが予約されており、NAT で利用できます。

* `10.0.0.0/8`
* `172.16.0.0/12`
* `192.168.0.0/16`

> **警告**: ファイアウォールのルールを操作するときは、**十分に注意してください**。設定によっては、**管理者自身がサーバーから締め出される（ロックアウトされる）** ことがあります。安全のため、初期のファイアウォール設定は SSH 越しのリモート作業ではなく、ローカルコンソールから行うことを検討してください。

<a id="firewalls-pf"></a>
## PF

FreeBSD 5.3 以降、OpenBSD の PF ファイアウォールを移植したものがベースシステムの一部として組み込まれています。
PF は高機能で完成度の高いファイアウォールであり、QoS（Quality of Service）を提供する ALTQ（Alternate Queuing）にもオプションで対応しています。

OpenBSD プロジェクトは [PF FAQ](https://www.openbsd.org/faq/pf/) で PF の公式リファレンスを公開しています。
また、Peter Hansteen 氏は [https://home.nuug.no/~peter/pf/](https://home.nuug.no/~peter/pf/) で網羅的な PF チュートリアルを公開しています。

> **警告**: [PF FAQ](https://www.openbsd.org/faq/pf/) を読む際は、FreeBSD 版の PF が長年にわたり上流の OpenBSD 版から大きく分岐している点に注意してください。すべての機能が OpenBSD と同じように FreeBSD で動くわけではなく、その逆も同様です。

PF ファイアウォールの設定や運用について質問したい場合は、FreeBSD PF メーリングリスト（`freebsd-pf`）が役立ちます。
すでに回答済みのこともあるため、質問する前にメーリングリストのアーカイブを確認してください。

本節では、FreeBSD における PF に焦点を当て、PF と ALTQ を有効にする方法を示します。
あわせて、FreeBSD システムでルールセットを作成するための実例もいくつか紹介します。

<a id="chapter-34-heading-05"></a>
### PF を有効にする

PF を使うには、まずカーネルモジュールを読み込む必要があります。
ここでは、PF を有効にするために `/etc/rc.conf` へ追加できる設定項目を説明します。

まず、`/etc/rc.conf` に `pf_enable=yes` を追加します。

```shell
# sysrc pf_enable=yes
```

PF の起動時には、`pfctl(8)` に記載されている追加オプションを渡すこともできます。
`/etc/rc.conf` に次の行を追加または変更し、二重引用符（`""`）の間に必要なフラグを指定してください。

```
pf_flags=""                     # additional flags for pfctl startup
```

PF はルールセット設定ファイルが見つからないと起動しません。
既定では FreeBSD にルールセットは同梱されておらず、`/etc/pf.conf` も存在しません。
ルールセットの例は `/usr/share/examples/pf/` にあります。
独自に作成したルールセットを別の場所に保存した場合は、そのファイルへのフルパスを `/etc/rc.conf` に追記してください。

```
pf_rules="/path/to/pf.conf"
```

PF のログ記録機能は `pflog(4)` が提供します。
ログ記録を有効にするには、`/etc/rc.conf` に `pflog_enable=yes` を追加します。

```shell
# sysrc pflog_enable=yes
```

ログファイルの既定の保存先を変更したり、起動時に `pflog(4)` へ渡す追加フラグを指定したりするには、次の行も追加できます。

```
pflog_logfile="/var/log/pflog"  # where pflogd should store the logfile
pflog_flags=""                  # additional flags for pflogd startup
```

最後に、ファイアウォールの背後に LAN があり、LAN 上のコンピュータのためにパケットを転送する必要がある場合や NAT が必要な場合は、次のオプションを有効にします。

```
gateway_enable="YES"            # Enable as LAN gateway
```

必要な編集を保存したら、次のコマンドを実行してログ機能付きで PF を起動できます。

```shell
# service pf start
# service pflog start
```

既定では、PF は `/etc/pf.conf` から設定ルールを読み込み、そのファイルに指定されたルールや定義に従ってパケットを書き換え、破棄し、あるいは通過させます。
FreeBSD をインストールすると、`/usr/share/examples/pf/` に複数のサンプルファイルが配置されます。
PF ルールセットの網羅的な解説については、[PF FAQ](https://www.openbsd.org/faq/pf/) を参照してください。

PF の制御には `pfctl` を使います。
[pfctl の便利なオプション](#pfctl) に、このコマンドのよく使うオプションをまとめます。
利用可能なすべてのオプションについては `pfctl(8)` を参照してください。

<a id="pfctl"></a>
| コマンド | 目的 |
|---|---|
| `pfctl -e` | PF を有効にする。 |
| `pfctl -d` | PF を無効にする。 |
| `pfctl -F all -f /etc/pf.conf` | すべての NAT、フィルタ、ステート、テーブルのルールを消去（flush）し、`/etc/pf.conf` を再読み込みする。 |
| `pfctl -s [ rules \| nat \| states ]` | フィルタールール、NAT ルール、またはステートテーブルの状態を表示する。 |
| `pfctl -vnf /etc/pf.conf` | `/etc/pf.conf` の構文エラーを検査するが、ルールセットは読み込まない。 |

> **ヒント**: `pfctl` のように特権が必要なコマンドを実行する際は、`security/sudo` パッケージが便利です。Ports Collection からインストールできます。

PF ファイアウォールを通過するトラフィックを監視したい場合は、`sysutils/pftop` のパッケージまたは port のインストールを検討してください。
インストールすると、`pftop` を実行して `top(1)` に似た形式で通信状況のリアルタイムスナップショットを確認できます。

<a id="pf-tutorial"></a>
### PF ルールセット

ここでは、目的に合わせたルールセットの作り方を説明します。
最も単純なルールセットから始め、PF の多彩な機能の実用的な使い方を示すいくつかの例を通じて概念を広げていきます。

最も単純なルールセットは、サービスを一切動かさず、インターネットなどの1つのネットワークへアクセスできればよい単体マシン向けのものです。
この最小限のルールセットを作るには、`/etc/pf.conf` を次のように編集します。

```
block in all
pass out all keep state
```

1行目のルールは、既定ですべての着信トラフィックを拒否します。
2行目のルールは、このシステムが開始した接続が外へ出ていくのを許可しつつ、その接続のステート情報を保持します。
このステート情報によってそれらの接続に対する戻りトラフィックの通過が許可されるため、信頼できるマシンでのみ使用してください。
ルールセットは次のコマンドで読み込めます。

```shell
# pfctl -e ; pfctl -f /etc/pf.conf
```

PF ではステートの保持に加えて、ルール作成時に使える**リスト（list）**や**マクロ（macro）**を定義できます。
マクロにはリストを含めることができ、使用する前に定義しておく必要があります。
例として、ルールセットのいちばん先頭に次の行を挿入します。

```
tcp_services = "{ ssh, smtp, domain, www, pop3, auth, pop3s }"
udp_services = "{ domain }"
```

PF は、`/etc/services` に記載されている名前であればポート番号だけでなくポート名も理解します。
この例では2つのマクロを作成しています。
1つ目は7つの TCP ポート名のリスト、2つ目は1つの UDP ポート名です。
定義したマクロはルールの中で使えます。
次の例では、このシステムから開始された指定の7つの TCP サービスと1つの UDP サービスへの接続を除き、すべてのトラフィックを遮断します。

```
tcp_services = "{ ssh, smtp, domain, www, pop3, auth, pop3s }"
udp_services = "{ domain }"
block all
pass out proto tcp to any port $tcp_services keep state
pass proto udp to any port $udp_services keep state
```

UDP はステートレスなプロトコルとみなされますが、PF は一部のステート情報を追跡できます。
たとえば、ネームサーバーにドメイン名を問い合わせる UDP リクエストが通過すると、PF はその応答を待ち受けて通過させます。

ルールセットを編集したら、そのたびに新しいルールを読み込んで反映させる必要があります。

```shell
# pfctl -f /etc/pf.conf
```

構文エラーがなければ、`pfctl` はルール読み込み中に何もメッセージを出力しません。
また、実際に読み込む前にルールをテストすることもできます。

```shell
# pfctl -nf /etc/pf.conf
```

`-n` を付けると、ルールの解釈だけが行われ、実際には読み込まれません。
これにより、エラーを事前に見つけて修正できます。
PF が無効化されるか新しいルールセットが読み込まれるまでは、常に最後に正常に読み込まれたルールセットが適用され続けます。

> **ヒント**: `pfctl` でルールセットの検証や読み込みを行う際に `-v` を追加すると、実際に読み込まれる形へ完全に展開・解析されたルールが表示されます。ルールのデバッグ時に非常に役立ちます。

<a id="pftut-gateway"></a>
#### NAT を使ったシンプルなゲートウェイ

ここでは、PF を動かす FreeBSD システムを、少なくとも1台の別マシンのためのゲートウェイとして構成する方法を説明します。
ゲートウェイには、それぞれ異なるネットワークに接続された少なくとも2つのネットワークインタフェースが必要です。
この例では、`xl0` がインターネットに、`xl1` が内部ネットワークに接続されているものとします。

まず、あるインタフェースで受信したネットワークトラフィックを別のインタフェースへ転送できるよう、ゲートウェイ機能を有効にします。
次の sysctl 設定で IPv4 パケットを転送します。

```shell
# sysctl net.inet.ip.forwarding=1
```

IPv6 トラフィックを転送するには次のようにします。

```shell
# sysctl net.inet6.ip6.forwarding=1
```

システム起動時にこれらの設定を有効にするには、`sysrc(8)` を使って `/etc/rc.conf` に追記します。

```shell
# sysrc gateway_enable=yes
# sysrc ipv6_gateway_enable=yes
```

両方のインタフェースが有効（up）で稼働していることを `ifconfig` で確認してください。

次に、ゲートウェイがトラフィックを通過させられるように PF ルールを作成します。
以下のルールは、内部ネットワークのホストからゲートウェイへ向かうステートフルなトラフィックを通過させますが、`to` キーワードだけでは送信元から宛先までの全経路の通過を保証しません。

```
pass in on xl1 from xl1:network to xl0:network port $ports keep state
```

このルールは、内部インタフェースからゲートウェイへ入ってくるトラフィックだけを許可します。
パケットをさらに先へ通すには、対になるルールが必要です。

```
pass out on xl0 from xl1:network to xl0:network port $ports keep state
```

これら2つのルールでも動作しますが、ここまで細かく指定したルールが必要になることはめったにありません。
忙しいネットワーク管理者にとっては、読みやすいルールセットほど安全なルールセットになります。
この節の残りの部分では、読みやすさを保つためにルールをできる限り簡潔に書く方法を示します。
たとえば、上の2つのルールは次の1つのルールに置き換えられます。

```
pass from xl1:network to any port $ports keep state
```

`interface:network` 表記をマクロに置き換えると、ルールセットをさらに読みやすくできます。
たとえば、`$localnet` マクロを内部インタフェースに直接接続されたネットワーク（`$xl1:network`）として定義できます。
あるいは、`$localnet` の定義を *IPアドレス/ネットマスク* 表記に変更し、プライベートアドレスのサブネットとして `192.168.100.1/24` のようにネットワークを表すこともできます。

必要であれば、`$localnet` をネットワークのリストとして定義することさえ可能です。
具体的な要件が何であれ、適切な `$localnet` 定義は次のように一般的な pass ルールで使えます。

```
pass from $localnet to any port $ports keep state
```

次のサンプルルールセットは、内部ネットワーク上のマシンから開始されたすべてのトラフィックを許可します。
最初に、ゲートウェイの外部および内部の 3COM インタフェースを表す2つのマクロを定義しています。

> **注記**: ダイヤルアップ接続の利用者の場合、外部インタフェースには `tun0` を使います。ADSL 接続、特に PPP over Ethernet（PPPoE）を使う接続でも、正しい外部インタフェースは物理イーサネットインタフェースではなく `tun0` です。

```
ext_if = "xl0"	# macro for external interface - use tun0 for PPPoE
int_if = "xl1"	# macro for internal interface
localnet = $int_if:network
# ext_if IP address could be dynamic, hence ($ext_if)
nat on $ext_if from $localnet to any -> ($ext_if)
block all
pass from { lo0, $localnet } to any keep state
```

このルールセットでは、`nat` ルールを導入しています。これにより、内部ネットワーク内のルーティング不能なアドレスから外部インタフェースに割り当てられた IP アドレスへのネットワークアドレス変換を行います。
`nat` ルールの末尾にある `($ext_if)` の丸括弧は、外部インタフェースの IP アドレスが動的に割り当てられる場合に付けます。
これにより、外部 IP アドレスが変わってもネットワークトラフィックが大きく途切れることなく動き続けます。

なお、このルールセットはおそらく必要以上に多くのトラフィックをネットワーク外へ通過させてしまいます。
妥当な設定の一例として、次のようなマクロを作成し、

```
client_out = "{ ftp-data, ftp, ssh, domain, pop3, auth, nntp, http, \
    https, cvspserver, 2628, 5999, 8000, 8080 }"
```

主要な pass ルールで使うことができます。

```
pass inet proto tcp from $localnet to any port $client_out \
    flags S/SA keep state
```

ほかにもいくつか pass ルールが必要になる場合があります。
次は外部インタフェースで SSH を有効にするルールです。

```
pass in inet proto tcp to $ext_if port ssh
```

次のマクロ定義とルールは、内部クライアント向けに DNS と NTP を許可します。

```
udp_services = "{ domain, ntp }"
pass quick inet proto { tcp, udp } to any port $udp_services keep state
```

このルールにある `quick` キーワードに注目してください。
ルールセットは複数のルールから構成されるため、ルール間の関係を理解しておくことが重要です。
ルールは記述された順に上から下へと評価されます。
PF が評価する各パケットや接続に対しては、ルールセットの中で**最後に一致したルール**が適用されます。
ただし、`quick` キーワードを含むルールにパケットが一致すると、その時点でルールの評価が打ち切られ、パケットはそのルールに従って処理されます。
一般的なルールに対する例外を作りたいときに非常に便利です。

<a id="pftut-ftp"></a>
#### FTP プロキシの作成

FTP プロトコルの性質上、正常に動作する FTP ルールを設定するのは厄介な場合があります。
FTP はファイアウォールより何十年も前に作られており、設計上安全ではありません。
FTP の使用を避けるべき主な理由には次の点があります。

* パスワードが平文で転送される。
* プロトコル上、別々のポートで少なくとも2本の TCP 接続（制御用とデータ用）が必要になる。
* セッション確立後、ランダムに選ばれたポートを使ってデータが通信される。

クライアントやサーバーソフトウェアに潜む脆弱性を考慮する以前の問題として、これらはいずれもセキュリティ上の課題になります。
ファイル転送には、認証とデータ転送の両方を暗号化された接続上で行う `sftp(1)` や `scp(1)` のような、より安全な代替手段があります。

どうしても FTP が必要な状況のために、PF では FreeBSD のベースシステムに含まれる `ftp-proxy(8)` という小さなプロキシプログラムへ FTP トラフィックをリダイレクトする機能が用意されています。
このプロキシの役割は、FTP トラフィックを正しく処理するために、アンカー（anchor）の仕組みを使ってルールセット内のルールを動的に追加・削除することです。

FTP プロキシを有効にするには、`/etc/rc.conf` に次の行を追加します。

```
ftpproxy_enable="YES"
```

次に、プロキシを起動します。

```bash
# service ftp-proxy start
```

基本的な構成では、`/etc/pf.conf` に3つの要素を追加する必要があります。
1つ目は、FTP セッション用に生成したルールをプロキシが挿入するためのアンカーです。

```
nat-anchor "ftp-proxy/*"
rdr-anchor "ftp-proxy/*"
```

2つ目は、プロキシへの FTP トラフィックの流入を許可する pass ルールです。

3つ目に、リダイレクトルールと NAT ルールをフィルタリングルールより前に定義する必要があります。
次の `rdr` ルールを `nat` ルールの直後に挿入してください。

```
rdr pass on $int_if proto tcp from any to any port ftp -> 127.0.0.1 port 8021
```

最後に、リダイレクトされたトラフィックが外へ出ていくのを許可します。

```
pass out proto tcp from $proxy to any port ftp
```

ここで `$proxy` はプロキシデーモンがバインドしているアドレスに展開されます。

`/etc/pf.conf` を保存して新しいルールを読み込み、クライアントから FTP 接続が動作することを確認します。

```shell
# pfctl -f /etc/pf.conf
```

この例では、ローカルネットワーク内のクライアントが外部の FTP サーバーへ接続する必要がある基本的な構成を扱っています。
この基本設定は、ほとんどの FTP クライアントとサーバーの組み合わせで問題なく動作するはずです。
`ftp-proxy(8)` に記載されているとおり、`ftpproxy_flags=` 行にオプションを追加することでプロキシの挙動をさまざまに変更できます。
クライアントやサーバー固有のクセを設定で補う必要がある場合や、FTP トラフィックを特定のキューに割り当てるなど特殊な連携が必要な場合もあります。

PF と `ftp-proxy(8)` で保護された FTP サーバーを運用する方法については、別の `ftp-proxy` を `-R` によるリバースモードで、別のポートと専用のリダイレクト用 pass ルールを伴って設定してください。

<a id="pftut-icmp"></a>
#### ICMP の管理

TCP/IP ネットワークのデバッグやトラブルシューティングに使うツールの多くは、まさにデバッグを念頭に設計された Internet Control Message Protocol（ICMP）に依存しています。

ICMP プロトコルはホストとゲートウェイの間で**制御メッセージ**を送受信し、主に宛先ホストへの経路上で発生した異常や困難な状況について送信元へフィードバックを返します。
ルーターは ICMP を使ってパケットサイズやその他の伝送パラメータを調整します。この処理は一般に**パス MTU 探索（path MTU discovery）**と呼ばれます。

ファイアウォールの観点からは、一部の ICMP 制御メッセージが既知の攻撃手法に悪用されるおそれがあります。
また、診断用トラフィックを無条件にすべて通すとデバッグは楽になりますが、第三者がネットワークに関する情報を収集するのも容易になってしまいます。
そのため、次のようなルールは最適とは言えません。

```
pass inet proto icmp from any to any
```

1つの解決策は、ローカルネットワークからの ICMP トラフィックはすべて通し、ネットワーク外部からの探索（probe）はすべて止めることです。

```
pass inet proto icmp from $localnet to any keep state
pass inet proto icmp from any to $ext_if keep state
```

PF の柔軟性を示すオプションはほかにもあります。
たとえば、すべての ICMP メッセージを許可するのではなく、`ping(8)` や `traceroute(8)` が使うメッセージだけを指定できます。
まず、その種類のメッセージを表すマクロを定義します。

```
icmp_types = "echoreq"
```

そして、そのマクロを使うルールを記述します。

```
pass inet proto icmp all icmp-type $icmp_types keep state
```

ほかの種類の ICMP パケットも必要な場合は、`icmp_types` をそれらのパケット種別のリストへ拡張してください。
PF が対応している ICMP メッセージ種別の一覧は、`more /usr/src/sbin/pfctl/pfctl_parser.c` で確認できます。
各メッセージ種別の解説については、[https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml](https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml) を参照してください。

Unix の `traceroute` は既定で UDP を使うため、Unix の `traceroute` を許可するには別のルールが必要です。

```
# allow out the default range for traceroute(8):
pass out on $ext_if inet proto udp from any to any port 33433 >< 33626 keep state
```

Microsoft Windows システムの `TRACERT.EXE` は ICMP エコー要求（echo request）メッセージを使うため、それらのシステムからの経路追跡を許可するには最初のルールだけで足ります。
Unix の `traceroute` も別のプロトコルを使うように指定でき、`-I` を付けると ICMP エコー要求メッセージを使用します。
詳しくは `traceroute(8)` のマニュアルページを確認してください。

<a id="pftut-pathmtudisc"></a>
##### パス MTU 探索（Path MTU Discovery）

インターネットプロトコルはデバイスに依存しないように設計されており、その結果として、ある接続にとって最適なパケットサイズを常に確実に予測できるわけではありません。
パケットサイズに対する主な制約は、インタフェースにおけるパケットサイズの上限を決める **Maximum Transmission Unit（MTU）** です。
システムのネットワークインタフェースの MTU を確認するには `ifconfig` を実行します。

TCP/IP は、接続に適したパケットサイズを求めるためにパス MTU 探索と呼ばれる処理を行います。
この処理では、「フラグメント禁止（Do not fragment）」フラグを立てたさまざまなサイズのパケットを送信し、上限に達したときに返される「type 3, code 4」の ICMP 応答パケットを待ちます。
type 3 は「宛先到達不能（destination unreachable）」、code 4 は「フラグメンテーションが必要だが、フラグメント禁止フラグが設定されている」という意味です。
異なる MTU を持つ相手との接続に対応できるようパス MTU 探索を許可するには、`icmp_types` マクロに `destination unreachable`（`unreach`）種別を追加します。

```
icmp_types = "{ echoreq, unreach }"
```

pass ルールはすでにそのマクロを使っているため、新しい ICMP 種別に対応するためにルール側を変更する必要はありません。

```
pass inet proto icmp all icmp-type $icmp_types keep state
```

PF では、あらゆる組み合わせの ICMP type と code に基づいてフィルタリングできます。
指定可能な type と code の一覧は `icmp(4)` と `icmp6(4)` に記載されています。

<a id="pftut-tables"></a>
#### テーブル（Tables）の利用

フィルタリングやリダイレクトにおいて特定の時点で参照したいデータの中には、定義が長すぎてルールセットファイルへ直接書き込めないものがあります。
PF はテーブル（table）をサポートしており、ルールセット全体を再読み込みせずに操作でき、高速な検索が可能なリストを定義できます。
テーブル名は次のように必ず `< >` で囲みます。

```
table <clients> { 192.168.2.0/24, !192.168.2.5 }
```

この例では、`192.168.2.0/24` ネットワークがテーブルに含まれますが、`!` 演算子によって `192.168.2.5` のアドレスだけは除外されています。
次の `/etc/clients` の例のように、各項目を1行ずつ書いたファイルからテーブルを読み込むことも可能です。

```
192.168.2.0/24
!192.168.2.5
```

ファイルを参照するには、次のようにテーブルを定義します。

```
table <clients> persist file "/etc/clients"
```

テーブルを定義すれば、ルールから参照できます。

```
pass inet proto tcp from <clients> to any port $client_out flags S/SA keep state
```

テーブルの内容は `pfctl` を使って稼働中に動的に操作できます。
次の例では、テーブルに別のネットワークを追加しています。

```shell
# pfctl -t clients -T add 192.168.1.0/16
```

この方法で行った変更は即座に反映されるためテストには最適ですが、電源断や再起動をまたいでは残りません。
変更を永続化するには、ルールセット内のテーブル定義を修正するか、テーブルが参照しているファイルを編集してください。
`pfctl -t clients -T show >/etc/clients` のようなコマンドを `cron(8)` ジョブで定期実行し、テーブルの内容をディスク上のコピーへ書き出して維持することもできます。
また、次のようにしてメモリ上のテーブル内容を `/etc/clients` の内容で更新することもできます。

```shell
# pfctl -t clients -T replace -f /etc/clients
```

<a id="pftut-overload"></a>
#### 過負荷（Overload）テーブルを使った SSH の保護

外部インタフェースで SSH を動かしていると、認証ログに次のような記録を見たことがあるかもしれません。

```
Sep 26 03:12:34 skapet sshd[25771]: Failed password for root from 200.72.41.31 port 40992 ssh2
Sep 26 03:12:34 skapet sshd[5279]: Failed password for root from 200.72.41.31 port 40992 ssh2
Sep 26 03:12:35 skapet sshd[5279]: Received disconnect from 200.72.41.31: 11: Bye Bye
Sep 26 03:12:44 skapet sshd[29635]: Invalid user admin from 200.72.41.31
Sep 26 03:12:44 skapet sshd[24703]: input_userauth_request: invalid user admin
Sep 26 03:12:44 skapet sshd[24703]: Failed password for invalid user admin from 200.72.41.31 port 41484 ssh2
```

これは、何者かまたはプログラムがシステムへ侵入するためのユーザー名とパスワードを探り出そうとしているブルートフォース攻撃の兆候です。

正当な利用者のために外部からの SSH アクセスが必要な場合、SSH が使う既定のポート番号を変更することである程度の防御になります。
しかし、PF にはより洗練された解決策があります。
pass ルールに接続元ホストの振る舞いに対する上限を設定でき、上限を超えた違反者を、一部またはすべてのアクセスを拒否するアドレスのテーブルへ追放できます。
上限を超えたマシンからの既存の接続をすべて切断することさえ可能です。

これを設定するには、まずルールセットのテーブル定義部分に次のテーブルを作成します。

```
table <bruteforce> persist
```

次に、ルールセットの前半あたりに、正当なアクセスを許可しつつブルートフォース攻撃を遮断するルールを追加します。

```
block quick from <bruteforce>
pass inet proto tcp from any to $localnet port $tcp_services \
    flags S/SA keep state \
    (max-src-conn 100, max-src-conn-rate 15/5, \
    overload <bruteforce> flush global)
```

括弧内の部分は制限内容を定義しており、数値はローカル環境の要件に合わせて変更してください。
各指定の意味は次のとおりです。

`max-src-conn` は、1台のホストから許可される同時接続数の上限です。

`max-src-conn-rate` は、単一のホストから許可される新規接続の頻度（*5* 秒あたり *15* 回）です。

`overload <bruteforce>` は、これらの上限を超えたホストのアドレスを `bruteforce` テーブルに追加することを意味します。
上のルールセットでは、`bruteforce` テーブル内のアドレスからのすべてのトラフィックを遮断します。

最後の `flush global` は、ホストが上限に達した際、そのホストのすべての（`global`）接続を強制終了（`flush`）することを指示します。

> **注記**: これらのルールは、[https://home.nuug.no/~peter/hailmary2013/](https://home.nuug.no/~peter/hailmary2013/) で解説されているような低速なブルートフォース攻撃（slow bruteforcer）は**遮断しません**。

このルールセットの例は主に仕組みを示すためのものです。
たとえば、一般的な接続数は多めに許可したいが、ssh に関してはより厳しく制限したい場合は、上のルールに加えてルールセットの前半に次のようなルールを補います。

```
pass quick proto { tcp, udp } from any to any port ssh \
    flags S/SA keep state \
    (max-src-conn 15, max-src-conn-rate 5/3, \
    overload <bruteforce> flush global)
```

> **注記**: **上限超過者をすべて遮断する必要はない場合もあります**:
>
> 過負荷（overload）の仕組みは SSH 専用ではなく汎用的な手法であり、違反者からのすべてのトラフィックを完全に遮断するのが常に最適とは限りません。
>
> たとえば、メールサービスや Web サービスを保護するために overload ルールを使い、overload テーブルを参照するルールによって、違反者を最小帯域幅しか割り当てないキューへ振り分けたり、特定の Web ページへリダイレクトしたりすることもできます。

時間が経つにつれて、テーブルは overload ルールによってエントリが追加され続け、徐々に大きくなってメモリを消費します。
また、遮断された IP アドレスが動的割り当てのもので、その後、ローカルネットワーク内のホストと通信する正当な理由のある別のホストへ割り当て直されることもあります。

このような状況のために、`pfctl` にはテーブルエントリを期限切れにして削除する機能があります。
たとえば、次のコマンドは `86400` 秒間参照されていない `<bruteforce>` テーブルのエントリを削除します。

```shell
# pfctl -t bruteforce -T expire 86400
```

同様の機能は `security/expiretable` でも提供されており、指定した期間アクセスされていないテーブルエントリを削除します。

インストール後、`expiretable` を実行して指定した経過時間より古い `<bruteforce>` テーブルのエントリを削除できます。
次の例では、24時間より古いすべてのエントリを削除します。

```
/usr/local/sbin/expiretable -v -d -t 24h bruteforce
```

<a id="pftut-spamd"></a>
#### SPAM 対策

SpamAssassin に同梱されている `spamd` デーモンと混同しないよう注意が必要ですが、`mail/spamd` を PF と組み合わせて設定すると、SPAM に対する外郭防御を構築できます。
この `spamd` はリダイレクト設定を使って PF の構成に組み込みます。

スパマーは大量のメッセージを送信する傾向があり、SPAM は主に少数のスパマーに友好的なネットワークや多数の乗っ取られたマシンから送られます。これらはいずれも比較的早く**ブロックリスト（blocklist）**に報告されます。

ブロックリストに載っているアドレスから SMTP 接続を受けると、`spamd` はバナーを返した直後に、SMTP トラフィックに対して1バイトずつ応答を返すモードへ切り替わります。
送信側のスパマーにできるだけ多くの時間を浪費させることを狙ったこの手法は**ターピッティング（tarpitting）**と呼ばれます。
1バイトずつ SMTP 応答を返す具体的な実装は、よく **スタッタリング（stuttering）** と呼ばれます。

この例では、自動更新されるブロックリストとともに `spamd` を設定する基本手順を示します。
詳しくは、`mail/spamd` とともにインストールされるマニュアルページを参照してください。

**手順: spamd の設定**

1. `mail/spamd` のパッケージまたは port をインストールします。`spamd` のグレイリスティング機能を使うには、`/dev/fd` に `fdescfs(5)` がマウントされている必要があります。`/etc/fstab` に次の行を追加してください。

   ```
    fdescfs /dev/fd fdescfs rw 0 0
   ```

   その後、ファイルシステムをマウントします。

   ```
   #  mount fdescfs
   ```

2. 次に、PF ルールセットを編集して以下を含めます。

   ```
   table <spamd> persist
   table <spamd-white> persist
   rdr pass on $ext_if inet proto tcp from <spamd> to \
       { $ext_if, $localnet } port smtp -> 127.0.0.1 port 8025
   rdr pass on $ext_if inet proto tcp from !<spamd-white> to \
       { $ext_if, $localnet } port smtp -> 127.0.0.1 port 8025
   ```

   `<spamd>` と `<spamd-white>` の2つのテーブルが不可欠です。
   `<spamd>` に含まれており、かつ `<spamd-white>` に含まれていないアドレスからの SMTP トラフィックは、ポート 8025 で待ち受けている `spamd` デーモンへリダイレクトされます。

3. 続いて、`/usr/local/etc/spamd.conf` で `spamd` を設定し、`/etc/rc.conf` にいくつかのパラメータを追加します。

   `mail/spamd` をインストールすると、サンプル設定ファイル（`/usr/local/etc/spamd.conf.sample`）と `spamd.conf` のマニュアルページが導入されます。
   この例で示す項目以外の設定オプションについては、これらを参照してください。

   設定ファイルの先頭付近にある、`#` コメント記号で始まらない最初の行の1つに、使用するリストを指定する `all` リストの定義ブロックがあります。

   ```
   all:\
       :traplist:allowlist:
   ```

   この項目には、使いたいブロックリストをコロン（`:`）で区切って並べます。許可リスト（allowlist）を使ってブロックリストから特定のアドレスを除外したい場合は、そのブロックリスト名の**直後**に許可リストの名前を付けます（例: `:blocklist:allowlist:`）。

   その後に、指定したブロックリストの定義が続きます。

   ```
   traplist:\
       :black:\
       :msg="SPAM. Your address %A has sent spam within the last 24 hours":\
       :method=http:\
       :file=www.openbsd.org/spamd/traplist.gz
   ```

   1行目がブロックリストの名前、2行目がリストの種類を指定しています。
   `msg` フィールドには、ブロックリストに載っている送信者へ SMTP 対話中に表示するメッセージを指定します。
   `method` フィールドには、`spamd-setup` がリストデータを取得する方法を指定します。対応している方法は `http`、`ftp`、マウントされたファイルシステム上の `file`、および外部プログラムの `exec` です。
   最後の `file` フィールドには、`spamd` が受け取るファイル名を指定します。

   指定した許可リストの定義も同様ですが、メッセージは不要なため `msg` フィールドは省略します。

   ```
   allowlist:\
       :white:\
       :method=file:\
       :file=/var/mail/allowlist.txt
   ```

   > **ヒント**: **データソースは慎重に選ぶ**:
   >
   > サンプルの `spamd.conf` にあるブロックリストをすべて使うと、インターネットの広大な範囲を遮断してしまいます。管理者はファイルを編集し、適切なデータソースを使い、必要に応じて独自リストも組み込んだ最適な構成を作成する必要があります。

   次に、この項目を `/etc/rc.conf` に追加します。追加のフラグについてはコメントに書かれたマニュアルページを参照してください。

   ```
   spamd_flags="-v" # use "" and see spamd-setup(8) for flags
   ```

   設定が終わったらルールセットを再読み込みし、`service obspamd start` を実行して `spamd` を起動し、`spamd-setup` で設定を完了させます。
   最後に、適切な間隔で `spamd-setup` を呼び出してテーブルを更新する `cron(8)` ジョブを作成します。

メールサーバーの手前にある一般的なゲートウェイでは、数秒から数分以内にホストが捕捉され始めるでしょう。

PF は**グレイリスティング（greylisting）**もサポートしており、未知のホストからのメッセージを一時的に *45n* コードで拒否します。
グレイリストに登録されたホストからのメッセージは、妥当な時間内に再試行された場合に通過が許可されます。
RFC 1123 および RFC 2821 の規定に沿った振る舞いをする送信元からのトラフィックは、ただちに通過します。

グレイリスティングという手法の詳しい情報は、[greylisting.org](http://www.greylisting.org/) の Web サイトにあります。
グレイリスティングの最も驚くべき点は、その単純さもさることながら、現在でも有効に機能していることです。
スパマーやマルウェア作成者は、この手法を回避するための対応が非常に遅れています。

グレイリスティングを設定する基本手順は次のとおりです。

**手順: グレイリスティングの設定**

1. 前の手順のステップ 1 で説明したとおり、`fdescfs(5)` がマウントされていることを確認します。
2. `spamd` をグレイリスティングモードで動かすため、`/etc/rc.conf` に次の行を追加します。

   ```
   spamd_grey="YES"  # use spamd greylisting if YES
   ```

   関連するその他のパラメータについては、`spamd` のマニュアルページを参照してください。

3. 次のコマンドでグレイリスティングの設定を完了します。

   ```
   #  service obspamd restart
   #  service obspamlogd start
   ```

舞台裏では、`spamdb` データベースツールと `spamlogd` ホワイトリスト更新デーモンが、グレイリスティング機能に不可欠な役割を担っています。
`spamdb` は、`/var/db/spamdb` データベースの内容を通じてブロックリスト・グレイリスト・許可リストを管理するための管理者向け主要インタフェースです。

<a id="pftut-hygiene"></a>
#### ネットワークの健全性（Network Hygiene）

ここでは、`block-policy`、`scrub`、`antispoof` を使ってルールセットを健全に動作させる方法を説明します。

`block-policy` は、ルールセット内のリダイレクトルールやフィルタリングルールより前に置かれる `options` セクションで設定できるオプションです。
このオプションは、ルールによって遮断されたホストに対して PF が何らかの応答を返すかどうかを決めます。
指定できる値は2つあり、`drop` は遮断したパケットを何も応答せず破棄し、`return` は `Connection refused` などのステータスコードを返します。

設定しない場合、既定のポリシーは `drop` です。
`block-policy` を変更するには、希望する値を指定します。

```
set block-policy return
```

PF の `scrub` は、ネットワークパケットの正規化（normalization）を有効にするキーワードです。
この処理では、フラグメント化されたパケットを再構成し、不正なフラグの組み合わせを持つ TCP パケットを破棄します。
`scrub` を有効にすることで、パケットフラグメントの誤った処理につけ込む特定の種類の攻撃に対する一定の防御が得られます。
多数のオプションが利用できますが、ほとんどの構成では最も単純な書式で十分です。

```
scrub in all
```

NFS などの一部のサービスでは、特定のフラグメント処理オプションが必要になります。
詳しくは [https://home.nuug.no/~peter/pf/en/scrub.html](https://home.nuug.no/~peter/pf/en/scrub.html) を参照してください。

次の例では、フラグメントを再構成し、「do not fragment」ビットをクリアして、最大セグメントサイズ（MSS）を 1440 バイトに設定します。

```
scrub in all fragment reassemble no-df max-mss 1440
```

`antispoof` 機構は、論理的にあり得ないインタフェースや方向から現れるパケットを主に遮断することで、なりすまし（spoofed）または偽造された IP アドレスからの通信を防ぎます。

次のルールは、外部世界から入ってくるなりすましトラフィックだけでなく、ローカルネットワーク内で発生したなりすましパケットも排除します。

```
antispoof for $ext_if
antispoof for $int_if
```

<a id="pftut-unrouteables"></a>
#### ルーティング不能アドレスの扱い

ネットワークアドレス変換を処理するゲートウェイを適切に設定していても、他者の設定ミスへの対処が必要になることがあります。
よくある設定ミスの一つが、ルーティング不能なアドレスを持つトラフィックをインターネットへ流してしまうことです。
ルーティング不能アドレスからのトラフィックは複数の DoS 攻撃手法に関与し得るため、外部インタフェースを通ってネットワークへ侵入するルーティング不能アドレスからの通信を明示的に遮断することを検討してください。

この例では、ルーティング不能アドレスを含むマクロを定義し、それを遮断ルールで使用しています。
ゲートウェイの外部インタフェースにおいて、これらのアドレス発着のトラフィックは黙って破棄されます。

```
martians = "{ 127.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12, \
	      10.0.0.0/8, 169.254.0.0/16, 192.0.2.0/24, \
	      0.0.0.0/8, 240.0.0.0/4 }"

block drop in quick on $ext_if from $martians to any
block drop out quick on $ext_if from any to $martians
```

<a id="chapter-34-heading-16"></a>
### ALTQ を有効にする

FreeBSD では、PF とともに ALTQ を使って QoS（Quality of Service）を提供できます。
ALTQ を有効にすると、ルールセット内にキュー（queue）を定義して送信パケットの処理優先度を決められるようになります。

ALTQ を有効にする前に、`altq(4)` を参照してシステムに搭載されているネットワークカードのドライバが ALTQ に対応しているか確認してください。

ALTQ は動的に読み込み可能なカーネルモジュールとしては提供されていません。
システムのインタフェースが ALTQ に対応している場合は、[FreeBSD カーネルの設定](09-kernelconfig.md#kernelconfig) の手順に従ってカスタムカーネルを作成してください。
次のカーネルオプションが利用できます。
最初のオプションは ALTQ を有効にするために必須です。
さらに、キューイングのスケジューリングアルゴリズムを指定するために、残りのオプションのうち少なくとも1つが必要です。

```
options         ALTQ
options         ALTQ_CBQ        # Class Based Queuing (CBQ)
options         ALTQ_RED        # Random Early Detection (RED)
options         ALTQ_RIO        # RED In/Out
options         ALTQ_HFSC       # Hierarchical Packet Scheduler (HFSC)
options         ALTQ_PRIQ       # Priority Queuing (PRIQ)
```

次のスケジューラアルゴリズムが利用できます。

* **CBQ**: Class Based Queuing（CBQ）は、接続の帯域幅を複数のクラスまたはキューに分割し、フィルタールールに基づいてトラフィックに優先順位を付けるために使います。
* **RED**: Random Early Detection（RED）は、キューの長さを計測してキューの最小閾値および最大閾値と比較することで、ネットワークの輻輳を回避するために使います。キューが最大値を超えると、新しいパケットはすべてランダムに破棄されます。
* **RIO**: Random Early Detection In and Out（RIO）モードでは、RED が QoS レベルごとに複数の平均キュー長と複数の閾値を管理します。
* **HFSC**: Hierarchical Fair Service Curve Packet Scheduler（HFSC）については、[https://www-2.cs.cmu.edu/~hzhang/HFSC/main.html](https://www-2.cs.cmu.edu/~hzhang/HFSC/main.html) で解説されています。
* **PRIQ**: Priority Queuing（PRIQ）は、より優先度の高いキューにあるトラフィックを常に先に通過させます。

スケジューリングアルゴリズムやルールセットの例に関する詳しい情報は、[OpenBSD の Web アーカイブ](https://web.archive.org/web/20151109213426/http://www.openbsd.org/faq/pf/queueing.html) で入手できます。

<a id="firewalls-ipfw"></a>
## IPFW

IPFW は FreeBSD 向けに開発されたステートフルファイアウォールで、IPv4 と IPv6 の両方に対応しています。
カーネル内のファイアウォールフィルタリングルール処理部とそれに統合されたパケット課金（アカウンティング）機能、ログ記録機能、NAT、`dummynet(4)` トラフィックシェーパー、転送（forward）機能、ブリッジ機能、ipstealth 機能など、複数のコンポーネントで構成されています。

FreeBSD は `/etc/rc.firewall` にサンプルのルールセットを用意しており、初心者が適切なルールセットを簡単に生成できるよう、よくある用途向けのファイアウォールタイプをいくつか定義しています。
また、IPFW は高度な構文を備えており、上級者は環境ごとのセキュリティ要件に合わせた独自のルールセットを作成できます。

本節では、IPFW を有効にする方法、ルール構文の概要、および一般的な構成シナリオ向けのルールセット例を紹介します。

<a id="firewalls-ipfw-enable"></a>
### IPFW を有効にする

IPFW は FreeBSD の基本インストールに動的読み込み可能なカーネルモジュールとして含まれているため、IPFW を有効にするためにカスタムカーネルをビルドする必要はありません。

カスタムカーネルへ IPFW サポートを静的に組み込みたい場合は、[IPFW カーネルオプション](#firewalls-ipfw-kernelconfig) を参照してください。

システム起動時に IPFW を有効にするには、`/etc/rc.conf` に `firewall_enable="YES"` を追加します。

```shell
# sysrc firewall_enable="YES"
```

FreeBSD が提供する既定のファイアウォールタイプのいずれかを使うには、そのタイプを指定する行を追加します。

```shell
# sysrc firewall_type="open"
```

指定できるタイプは次のとおりです。

* `open`: すべてのトラフィックを通過させる。
* `client`: このマシンだけを保護する。
* `simple`: ネットワーク全体を保護する。
* `closed`: ループバックインタフェースを除き、IP トラフィックを完全に無効化する。
* `workstation`: ステートフルルールを使ってこのマシンだけを保護する。
* `UNKNOWN`: ファイアウォールルールの読み込みを無効化する。
* `filename`: ファイアウォールルールセットを記述したファイルのフルパス。

`firewall_type` を `client` または `simple` に設定した場合は、`/etc/rc.firewall` にある既定のルールをシステムの構成に合わせて修正してください。

`filename` タイプは、独自のルールセットを読み込む際に使います。

独自ルールセットを読み込む別の方法として、IPFW コマンド群を記述した**実行可能スクリプト**の絶対パスを `firewall_script` 変数に設定する方法もあります。
本節の例では、`firewall_script` が `/etc/ipfw.rules` に設定されていることを前提としています。

```shell
# sysrc firewall_script="/etc/ipfw.rules"
```

`syslogd(8)` 経由でのログ記録を有効にするには、次の行を含めます。

```shell
# sysrc firewall_logging="YES"
```

> **警告**: `log` オプションが付いたファイアウォールルールだけがログに記録されます。既定のルールにはこのオプションが含まれていないため、手動で追加する必要があります。したがって、ログを取得するには既定のルールセットを編集しておくことを勧めます。さらに、ログを別ファイルへ保存する場合は、ログローテーションの設定も検討してください。

ログ記録の回数制限を設定するための `/etc/rc.conf` 変数はありません。
接続試行あたりに1つのルールがログへ記録される回数を制限するには、`/etc/sysctl.conf` に次の行を書いて回数を指定します。

```shell
# echo "net.inet.ip.fw.verbose_limit=5" >> /etc/sysctl.conf
```

代わりに `ipfw0` という専用インタフェース経由でログを記録するには、`/etc/rc.conf` に次の行を追加します。

```shell
# sysrc firewall_logif="YES"
```

その後、`tcpdump` を使って何が記録されているかを確認します。

```shell
# tcpdump -t -n -i ipfw0
```

> **ヒント**: `tcpdump` を接続していない限り、このログ機能によるオーバーヘッドは発生しません。

必要な編集を保存したら、ファイアウォールを起動します。
ログ回数制限を即座に有効にするため、上で指定した `sysctl` 値も同時に設定します。

```shell
# service ipfw start
# sysctl net.inet.ip.fw.verbose_limit=5
```

<a id="firewalls-ipfw-rules"></a>
### IPFW ルール構文

パケットが IPFW ファイアウォールに入ると、ルールセットの先頭ルールと比較され、上から下へ順番に1ルールずつ評価されます。
パケットがルールの選択条件に一致すると、そのルールのアクションが実行され、そのパケットに対するルールセットの検索はそこで終了します。
これを「最初の一致が勝つ（first match wins）」方式と呼びます。
どのルールにも一致しなかったパケットは、IPFW の必須の既定ルールである番号 65535 に捕捉され、すべて拒否されて黙って破棄されます。
ただし、`count`、`skipto`、`tee` の各キーワードを含むルールに一致した場合は検索が続行されます。
これらのキーワードがルール処理にどう影響するかの詳細は `ipfw(8)` を参照してください。

IPFW ルールを作成するときは、キーワードを次の順序で記述する必要があります。
必須のキーワードと省略可能なキーワードがあります。
大文字で示された語は変数（値）を表し、小文字で示された語は直後に続く変数の前に必ず置く必要があります。
`#` 記号はコメントの開始を示し、ルールの末尾にも独立した行にも置けます。
空行は無視されます。

`*CMD RULE_NUMBER* set *SET_NUMBER ACTION* log *LOG_AMOUNT PROTO* from *SRC SRC_PORT* to *DST DST_PORT OPTIONS*`

ここでは、これらのキーワードとオプションの概要を説明します。
利用可能なすべてのオプションを網羅したものではありません。
IPFW ルールを作成する際に使える構文の完全な解説は `ipfw(8)` を参照してください。

* **CMD**: すべてのルールは `ipfw add` で始める必要があります。

* **RULE_NUMBER**: 各ルールには `1` から `65534` までの番号を割り当てます。この番号はルール処理の順序を示すために使われます。複数のルールに同じ番号を付けることもでき、その場合は追加された順に適用されます。

* **SET_NUMBER**: 各ルールには `0` から `31` までのセット番号を割り当てます。セット単位で有効化・無効化できるため、一群のルールを素早く追加したり削除したりできます。`SET_NUMBER` を指定しない場合、ルールはセット `0` に追加されます。

* **ACTION**: ルールには次のいずれかのアクションを関連付けられます。パケットがルールの選択条件に一致したとき、指定されたアクションが実行されます。

  `allow | accept | pass | permit`: これらのキーワードは同等で、ルールに一致したパケットを許可します。

  `check-state`: 動的ステートテーブルとパケットを照合します。一致が見つかった場合、その動的ルールを生成したルールに関連付けられたアクションを実行し、見つからなければ次のルールへ進みます。`check-state` ルールには選択条件がありません。ルールセット内に `check-state` ルールが存在しない場合、最初の `keep-state` または `limit` ルールの位置で動的ルールテーブルが検査されます。

  `count`: ルールに一致したすべてのパケットについてカウンタを更新します。検索は次のルールへ続行されます。

  `deny | drop`: どちらの語も、このルールに一致したパケットを黙って破棄します。

  このほかにもアクションが用意されています。詳細は `ipfw(8)` を参照してください。

* **LOG_AMOUNT**: パケットが `log` キーワード付きのルールに一致すると、ファシリティ名 `SECURITY` で `syslogd(8)` にメッセージが記録されます。ログ記録は、その特定ルールで記録されたパケット数が指定された `LOG_AMOUNT` を超えていない場合にのみ行われます。`LOG_AMOUNT` を指定しない場合、上限は `net.inet.ip.fw.verbose_limit` の値から取得されます。値を 0 にするとログ回数制限が解除されます。上限に達した後は、`ipfw resetlog` を使ってそのルールのログカウンタまたはパケットカウンタをクリアすることでログ記録を再開できます。

  > **注記**: ログ記録は、パケットの他の一致条件がすべて満たされた後、パケットに対する最終アクションを実行する直前に行われます。どのルールでログを有効にするかは管理者が決めます。

* **PROTO**: この省略可能な値では、`/etc/protocols` に記載されている任意のプロトコル名またはプロトコル番号を指定できます。

* **SRC**: `from` キーワードの後には、送信元アドレスまたは送信元アドレスを表すキーワードを置く必要があります。アドレスには、`any`、`me`（このシステムのいずれかのインタフェースに設定されている任意のアドレス）、`me6`（このシステムのいずれかのインタフェースに設定されている任意の IPv6 アドレス）、あるいはアドレス一覧を含むルックアップテーブルの番号を続けた `table` を指定できます。IP アドレスを指定する場合、任意で CIDR マスクまたはサブネットマスクを後ろに付けられます。たとえば `1.2.3.4/25` や `1.2.3.4:255.255.255.128` のように書きます。

* **SRC_PORT**: 送信元ポートは省略可能で、`/etc/services` のポート番号またはポート名を使って指定できます。

* **DST**: `to` キーワードの後には、宛先アドレスまたは宛先アドレスを表すキーワードを置く必要があります。宛先の指定には、SRC の項目で説明したものと同じキーワードとアドレスが使えます。

* **DST_PORT**: 宛先ポートは省略可能で、`/etc/services` のポート番号またはポート名を使って指定できます。

* **OPTIONS**: 送信元と宛先の後ろにはいくつかのキーワードを続けられます。名前のとおり、`OPTIONS` は省略可能です。よく使われるオプションには、パケットの流れの方向を指定する `in` や `out`、ICMP メッセージの種別を続ける `icmptypes`、および `keep-state` があります。

  `keep-state` ルールに一致すると、ファイアウォールは同じプロトコルを使う送信元・宛先のアドレスおよびポート間の双方向トラフィックに一致する動的ルールを作成します。

  動的ルール機能は、大量の動的ルールを開かせる SYN フラッド攻撃によるリソース枯渇に対して脆弱です。IPFW でこの種の攻撃に対抗するには `limit` を使います。このオプションは、開いている動的ルールを検査してこのルールと IP アドレスの組み合わせが何回発生したかを数えることで、同時セッション数を制限します。この回数が `limit` で指定した値を超えると、パケットは破棄されます。

  数十種類の `OPTIONS` が用意されています。利用可能な各オプションの解説は `ipfw(8)` を参照してください。

<a id="chapter-34-heading-20"></a>
### ルールセットの例

ここでは、`/etc/ipfw.rules` という名前のステートフルファイアウォール用ルールセットスクリプトの例を作成する方法を示します。
この例では、方向を明確にするためすべての接続ルールで `in` または `out` を使っています。
また、パケットが通過するインタフェースを指定するために `via` *インタフェース名* を使っています。

> **注記**: ファイアウォールルールセットを最初に作成またはテストするときは、一時的に次のチューナブルを設定することを検討してください。
>
> ```
> net.inet.ip.fw.default_to_accept="1"
> ```
>
> これにより `ipfw(8)` の既定ポリシーが標準の `deny ip from any to any` よりも緩やかになり、再起動直後にシステムからロックアウトされにくくなります。

ファイアウォールスクリプトは、POSIX® シェルスクリプトであることを示す行から始まり、既存のルールをすべて消去（flush）します。
次に、すべてのルールの先頭に `ipfw add` と書かなくて済むように `cmd` 変数を作成します。
また、インターネットに接続されたインタフェース名を表す `pif` 変数も定義します。

```
#!/bin/sh
# Flush out the list before we begin.
ipfw -q -f flush

# Set rules command prefix
cmd="ipfw -q add"
pif="dc0"     # interface name of NIC attached to Internet
```

最初の2つのルールは、信頼された内部インタフェースとループバックインタフェース上のすべてのトラフィックを許可します。

```
# Change xl0 to LAN NIC interface name
$cmd 00005 allow all from any to any via xl0

# No restrictions on Loopback Interface
$cmd 00010 allow all from any to any via lo0
```

次のルールは、動的ルールテーブルの既存エントリに一致したパケットを通過させます。

```
$cmd 00101 check-state
```

続くルール群は、内部システムからインターネット上のホストに対して作成できるステートフル接続を定義します。

```
# Allow access to public DNS
# Replace x.x.x.x with the IP address of a public DNS server
# and repeat for each DNS server in /etc/resolv.conf
$cmd 00110 allow tcp from any to x.x.x.x 53 out via $pif setup keep-state
$cmd 00111 allow udp from any to x.x.x.x 53 out via $pif keep-state

# Allow access to ISP's DHCP server for cable/DSL configurations.
# Use the first rule and check log for IP address.
# Then, uncomment the second rule, input the IP address, and delete the first rule
$cmd 00120 allow log udp from any to any 67 out via $pif keep-state
#$cmd 00120 allow udp from any to x.x.x.x 67 out via $pif keep-state

# Allow outbound HTTP and HTTPS connections
$cmd 00200 allow tcp from any to any 80 out via $pif setup keep-state
$cmd 00220 allow tcp from any to any 443 out via $pif setup keep-state

# Allow outbound email connections
$cmd 00230 allow tcp from any to any 25 out via $pif setup keep-state
$cmd 00231 allow tcp from any to any 110 out via $pif setup keep-state

# Allow outbound ping
$cmd 00250 allow icmp from any to any out via $pif keep-state

# Allow outbound NTP
$cmd 00260 allow udp from any to any 123 out via $pif keep-state

# Allow outbound SSH
$cmd 00280 allow tcp from any to any 22 out via $pif setup keep-state

# deny and log all other outbound connections
$cmd 00299 deny log all from any to any out via $pif
```

次のルール群は、インターネット上のホストから内部ネットワークへの接続を制御します。
まず攻撃に典型的に使われるパケットを拒否し、続いて特定の種類の接続だけを明示的に許可します。
インターネットから発信される許可済みサービスは、フラッドを防ぐためにすべて `limit` を使っています。

```
# Deny all inbound traffic from non-routable reserved address spaces
$cmd 00300 deny all from 192.168.0.0/16 to any in via $pif     #RFC 1918 private IP
$cmd 00301 deny all from 172.16.0.0/12 to any in via $pif      #RFC 1918 private IP
$cmd 00302 deny all from 10.0.0.0/8 to any in via $pif         #RFC 1918 private IP
$cmd 00303 deny all from 127.0.0.0/8 to any in via $pif        #loopback
$cmd 00304 deny all from 0.0.0.0/8 to any in via $pif          #loopback
$cmd 00305 deny all from 169.254.0.0/16 to any in via $pif     #DHCP auto-config
$cmd 00306 deny all from 192.0.2.0/24 to any in via $pif       #reserved for docs
$cmd 00307 deny all from 204.152.64.0/23 to any in via $pif    #Sun cluster interconnect
$cmd 00308 deny all from 224.0.0.0/3 to any in via $pif        #Class D & E multicast

# Deny public pings
$cmd 00310 deny icmp from any to any in via $pif

# Deny ident
$cmd 00315 deny tcp from any to any 113 in via $pif

# Deny all Netbios services.
$cmd 00320 deny tcp from any to any 137 in via $pif
$cmd 00321 deny tcp from any to any 138 in via $pif
$cmd 00322 deny tcp from any to any 139 in via $pif
$cmd 00323 deny tcp from any to any 81 in via $pif

# Deny fragments
$cmd 00330 deny all from any to any frag in via $pif

# Deny ACK packets that did not match the dynamic rule table
$cmd 00332 deny tcp from any to any established in via $pif

# Allow traffic from ISP's DHCP server.
# Replace x.x.x.x with the same IP address used in rule 00120.
#$cmd 00360 allow udp from any to x.x.x.x 67 in via $pif keep-state

# Allow HTTP connections to internal web server
$cmd 00400 allow tcp from any to me 80 in via $pif setup limit src-addr 2

# Allow inbound SSH connections
$cmd 00410 allow tcp from any to me 22 in via $pif setup limit src-addr 2

# Reject and log all other incoming connections
$cmd 00499 deny log all from any to any in via $pif
```

最後のルールは、ルールセットのどのルールにも一致しなかったすべてのパケットをログに記録します。

```
# Everything else is denied and logged
$cmd 00999 deny log all from any to any
```

<a id="in-kernel-nat"></a>
### カーネル内 NAT（In-kernel NAT）

FreeBSD の IPFW ファイアウォールには 2 種類の NAT 実装があります。ユーザーランド実装の `natd(8)` と、より新しいカーネル内 NAT（in-kernel NAT）実装です。
どちらも IPFW と連携してネットワークアドレス変換を提供します。
これを使うと、インターネット接続共有の仕組みを構築し、複数の内部コンピュータが単一のパブリック IP アドレスを使ってインターネットへ接続できるようになります。

これを行うには、インターネットに接続された FreeBSD マシンがゲートウェイとして動作する必要があります。
このシステムには 2 つの NIC が必要で、1つはインターネットに、もう1つは内部 LAN に接続します。
LAN に接続された各マシンには、[RFC 1918](https://www.ietf.org/rfc/rfc1918.txt) で定義されたプライベートネットワーク空間の IP アドレスを割り当てる必要があります。

IPFW のカーネル内 NAT 機能を有効にするには、いくつか追加の設定が必要です。
起動時にカーネル内 NAT サポートを有効にするには、`/etc/rc.conf` に次を設定します。

```
gateway_enable="YES"
firewall_enable="YES"
firewall_nat_enable="YES"
```

> **注記**: `firewall_nat_enable` を設定しても `firewall_enable` が設定されていなければ、何の効果もなく何も行われません。カーネル内 NAT 実装は IPFW 専用だからです。

ルールセットにステートフルルールが含まれる場合、NAT ルールの配置位置が重要になり、`skipto` アクションが使われます。
`skipto` アクションには、どのルールへジャンプするかを示すルール番号が必要です。
以下の例は、前の節で示したファイアウォールルールセットをベースにしています。
ファイアウォールでカーネル内 NAT を使うために、いくつか新しい項目を追加し、既存のルールを一部変更しています。
最初に、ジャンプ先のルール番号、`keep-state` オプション、そしてルール数を減らすために使う TCP ポートのリストを表す変数を追加しています。

```
#!/bin/sh
ipfw -q -f flush
cmd="ipfw -q add"
skip="skipto 1000"
pif=dc0
ks="keep-state"
good_tcpo="22,25,37,53,80,443,110"
```

カーネル内 NAT では、`libalias(3)` の構造上の理由から TCP セグメンテーションオフロード（TSO）を無効にする必要があります。`libalias(3)` は、IPFW のカーネル内 NAT 機能を提供するためにカーネルモジュールとして実装されているライブラリです。
TSO は、`ifconfig(8)` を使ってネットワークインタフェース単位で無効にすることも、`sysctl(8)` を使ってシステム全体で無効にすることもできます。
システム全体で TSO を無効にするには、`/etc/sysctl.conf` に次のように設定します。

```
net.inet.tcp.tso="0"
```

あわせて NAT インスタンスも構成します。
それぞれ独自の設定を持つ複数の NAT インスタンスを作成することも可能です。
この例では 1 つの NAT インスタンス（NAT インスタンス番号 1）だけが必要です。
設定ではいくつかのオプションを指定できます。たとえば、`if` はパブリックインタフェースを示し、`same_ports` はエイリアスされたポートとローカルポート番号が同じ番号に対応付けられるようにし、`unreg_only` は未登録の（プライベート）アドレス空間のみを NAT インスタンスで処理させ、`reset` は IPFW マシンのパブリック IP アドレスが変わった場合でも NAT インスタンスが機能し続けるようにします。
単一の NAT インスタンス設定に渡せるすべてのオプションについては `ipfw(8)` を参照してください。
ステートフルな NAT ファイアウォールを構成する場合、変換されたパケットをさらに処理するためにファイアウォールへ再投入できるようにする必要があります。
これは、ファイアウォールスクリプトの先頭で `one_pass` の挙動を無効にすることで実現できます。

```
ipfw disable one_pass
ipfw -q nat 1 config if $pif same_ports unreg_only reset
```

インバウンド NAT ルールは、信頼されたインタフェースとループバックインタフェース上の全トラフィックを許可する2つのルールおよび再構成（reassemble）ルールの**後**、かつ `check-state` ルールの**前**に挿入します。
この NAT ルールに選ぶルール番号（この例では `100`）は、最初の3つのルールより大きく、`check-state` ルールより小さいことが重要です。
さらに、カーネル内 NAT の動作仕様上、最初の NAT ルールの直前かつ信頼インタフェース上のトラフィックを許可するルールの後ろに、再構成（reassemble）ルールを置くことが推奨されます。
通常 IP フラグメンテーションは起きないはずですが、IPSEC/ESP/GRE トンネリングのトラフィックを扱う場合には発生し得るため、完成したパケットをカーネル内 NAT 機能へ渡す前にフラグメントの再構成が必要になります。

> **注記**: ユーザーランドの `natd(8)` では再構成ルールは不要でした。`ipfw(8)` にも記載されているとおり、IPFW の `divert` アクションの内部処理がソケットへ渡す前にパケットの再構成を自動的に行ってくれるためです。
>
> この例で使う NAT インスタンス番号とルール番号は、FreeBSD に標準で用意されている既定のファイアウォールルール設定スクリプト `rc.firewall` が作成する既定の NAT インスタンス番号やルール番号とは一致しません。

```
$cmd 005 allow all from any to any via xl0  # exclude LAN traffic
$cmd 010 allow all from any to any via lo0  # exclude loopback traffic
$cmd 099 reass all from any to any in       # reassemble inbound packets
$cmd 100 nat 1 ip from any to any in via $pif # NAT any inbound packets
# Allow the packet through if it has an existing entry in the dynamic rules table
$cmd 101 check-state
```

アウトバウンドルールは、`allow` アクションを `$skip` 変数に置き換えて修正し、ルール `1000` でルール処理が続くようにします。
7つあった `tcp` ルールは、許可された7つのアウトバウンドポートを含む `$good_tcpo` 変数を使ってルール `125` にまとめられています。

> **注記**: IPFW の性能は、ルールセット内に存在するルール数によって大きく左右されることを覚えておいてください。

```
# Authorized outbound packets
$cmd 120 $skip udp from any to x.x.x.x 53 out via $pif $ks
$cmd 121 $skip udp from any to x.x.x.x 67 out via $pif $ks
$cmd 125 $skip tcp from any to any $good_tcpo out via $pif setup $ks
$cmd 130 $skip icmp from any to any out via $pif $ks
```

インバウンドルールは同じままですが、最後のルールだけはインバウンドとアウトバウンドの両方のルールを捕捉するため `via $pif` を取り除きます。
NAT ルールはこの最後のアウトバウンドルールより後ろに置き、そのルールより大きい番号を付け、`skipto` アクションからそのルール番号を参照する必要があります。
このルールセットでは、ルール番号 `1000` がすべてのパケットを構成済みインスタンスへ渡して NAT 処理を行います。
次のルールは、NAT 処理を受けたあらゆるパケットの通過を許可します。

```
$cmd 999 deny log all from any to any
$cmd 1000 nat 1 ip from any to any out via $pif # skipto location for outbound stateful rules
$cmd 1001 allow ip from any to any
```

この例では、動的ステートテーブルのエントリに常にプライベート LAN の IP アドレスが登録されるよう、ルール `100`、`101`、`125`、`1000`、`1001` が送受信パケットのアドレス変換を制御しています。

内部の Web ブラウザがポート 80 で新しいアウトバウンド HTTP セッションを開始する場合を考えてみましょう。
最初のアウトバウンドパケットがファイアウォールに入ると、インバウンドではなくアウトバウンドなのでルール `100` には一致しません。
これは最初のパケットであり、まだ動的ステートテーブルに登録されていないためルール `101` を通過します。
最後にこのパケットは、許可されたポートへのアウトバウンド通信であり内部 LAN の送信元 IP アドレスを持っているため、ルール `125` に一致します。
このルールに一致すると、2つの動作が行われます。
まず `keep-state` アクションが動的ステートテーブルにエントリを追加し、続いて指定されたアクション `skipto rule 1000` が実行されます。
次に、パケットは NAT を受けてインターネットへ送り出されます。
このパケットは宛先の Web サーバーへ届き、そこで応答パケットが生成されて返送されます。
この新しいパケットはルールセットの先頭に入ります。
ルール `100` に一致して、宛先 IP アドレスが元の内部アドレスへ戻されます。
続いて `check-state` ルールで処理され、既存セッションとしてテーブル内に見つかり、LAN へ送り出されます。

インバウンド側では、ルールセットは不正なパケットを拒否し、許可されたサービスだけを通す必要があります。
インバウンドルールに一致したパケットは動的ステートテーブルに登録され、LAN へ送り出されます。
応答として生成されたパケットは、`check-state` ルールによって既存セッションに属すると認識されます。
その後、アウトバウンドインタフェースへ送り出される前に NAT を行うためルール `1000` へ送られます。

> **注記**: ユーザーランドの `natd(8)` からカーネル内 NAT への移行は一見シームレスに見えますが、小さな注意点があります。GENERIC カーネルを使っていて `/etc/rc.conf` で `firewall_nat_enable` を有効にすると、IPFW は `libalias.ko` カーネルモジュールを読み込みます。`libalias.ko` カーネルモジュールが提供するのは基本的な NAT 機能だけであり、ユーザーランド実装の `natd(8)` が追加設定なしでユーザーランドライブラリ内の全 NAT 機能を備えているのとは異なります。全機能を利用するには、標準の `libalias.ko` カーネルモジュールに加えて、必要に応じて `/etc/rc.conf` の `kld_list` 指定を使って次のカーネルモジュールを追加読み込みできます：`alias_ftp.ko`、`alias_bbt.ko`、`skinny.ko`、`irc.ko`、`alias_pptp.ko`、`alias_smedia.ko`。カスタムカーネルを使う場合は、`options LIBALIAS` を指定することでユーザーランドライブラリの全機能をカーネルへ組み込めます。

<a id="chapter-34-heading-22"></a>
#### ポートリダイレクト（Port Redirection）

一般的な NAT の欠点は、インターネットから LAN クライアントへアクセスできないことです。
LAN 上のクライアントは外部へ接続できますが、外部からの着信接続を受けられません。
これは、LAN クライアントマシンの1つでインターネットサービスを動かそうとする場合に問題になります。
簡単な回避策は、NAT を提供しているマシン上の特定のインターネット向けポートを LAN クライアントへリダイレクト（転送）することです。

たとえば、クライアント `A` で IRC サーバーが動き、クライアント `B` で Web サーバーが動いているとします。
これを正しく動かすには、ポート 6667（IRC）とポート 80（HTTP）で受信した接続をそれぞれのマシンへリダイレクトする必要があります。

カーネル内 NAT では、設定はすべて NAT インスタンス設定の中で行います。
カーネル内 NAT インスタンスで使えるオプションの全一覧は `ipfw(8)` を参照してください。
IPFW の構文は `natd` の構文を踏襲しています。`redirect_port` の構文は次のとおりです。

```
redirect_port proto targetIP:targetPORT[-targetPORT]
  [aliasIP:]aliasPORT[-aliasPORT]
  [remoteIP[:remotePORT[-remotePORT]]]
```

上記の例の構成を設定するには、引数を次のようにします。

```
redirect_port tcp 192.168.0.2:6667 6667
redirect_port tcp 192.168.0.3:80 80
```

先ほどのルールセット内の NAT インスタンス 1 の設定にこれらの引数を追加すると、IRC と HTTP サービスを動かしている LAN クライアントマシンへ各 TCP ポートがポートフォワードされます。

```
ipfw -q nat 1 config if $pif same_ports unreg_only reset \
  redirect_port tcp 192.168.0.2:6667 6667 \
  redirect_port tcp 192.168.0.3:80 80
```

`redirect_port` では個別のポートではなくポート範囲も指定できます。
たとえば *tcp 192.168.0.2:2000-3000 2000-3000* とすると、ポート 2000 から 3000 で受信したすべての接続がクライアント `A` のポート 2000 から 3000 へリダイレクトされます。

<a id="chapter-34-heading-23"></a>
#### アドレスリダイレクト（Address Redirection）

複数の IP アドレスが利用できる場合は、アドレスリダイレクトが便利です。
`ipfw(8)` によって各 LAN クライアントに専用の外部 IP アドレスを割り当てることができ、LAN クライアントから出ていくパケットを適切な外部 IP アドレスへ書き換え、その特定の IP アドレスに届いたすべてのトラフィックを特定の LAN クライアントへ転送し返します。
これは静的 NAT（static NAT）とも呼ばれます。
たとえば、`128.1.1.1`、`128.1.1.2`、`128.1.1.3` の IP アドレスが使える場合、`128.1.1.1` を `ipfw(8)` マシンの外部 IP アドレスとして使い、`128.1.1.2` と `128.1.1.3` は LAN クライアント `A` と `B` へ転送できます。

`redirect_addr` の構文は次のとおりで、`localIP` が LAN クライアントの内部 IP アドレス、`publicIP` がその LAN クライアントに対応する外部 IP アドレスです。

```
redirect_addr localIP publicIP
```

この例では、引数は次のようになります。

```
redirect_addr 192.168.0.2 128.1.1.2
redirect_addr 192.168.0.3 128.1.1.3
```

`redirect_port` と同様に、これらの引数は NAT インスタンスの設定に記述します。
アドレスリダイレクトを使う場合、特定の IP アドレスで受信したすべてのデータがリダイレクトされるため、ポートリダイレクトは不要になります。

`ipfw(8)` マシン上の外部 IP アドレスは有効化され、外部インタフェースにエイリアスとして設定されている必要があります。
詳しくは `rc.conf(5)` を参照してください。

<a id="chapter-34-heading-24"></a>
#### ユーザー空間 NAT（Userspace NAT）

まず明確にしておくと、ユーザー空間 NAT 実装である `natd(8)` は、カーネル内 NAT よりもオーバーヘッドが大きくなります。
`natd(8)` がパケットを変換するには、パケットをカーネルからユーザー空間へコピーし、再びカーネルへ戻す必要があるため、カーネル内 NAT にはない余分なオーバーヘッドが生じます。

起動時にユーザー空間 NAT デーモン `natd(8)` を有効にするための `/etc/rc.conf` の最小構成は次のとおりです。
ここで `natd_interface` にはインターネットに接続された NIC の名前を設定します。
`natd(8)` の `rc(8)` スクリプトは動的 IP アドレスが使われているかどうかを自動で確認し、それに対応できるように自身を設定します。

```
gateway_enable="YES"
natd_enable="YES"
natd_interface="rl0"
```

おおむね、カーネル内 NAT で説明した先ほどのルールセットは `natd(8)` と組み合わせてそのまま使えます。
例外は、カーネル内 NAT インスタンスの設定 `(ipfw -q nat 1 config ...)` と再構成ルール 99 で、その機能は `divert` アクションに含まれているため不要になります。
ルール番号 100 と 1000 は、次のように少し書き換える必要があります。

```
$cmd 100 divert natd ip from any to any in via $pif
$cmd 1000 divert natd ip from any to any out via $pif
```

ポートリダイレクトやアドレスリダイレクトを設定するには、カーネル内 NAT と同様の構文を使います。
ただし、カーネル内 NAT のようにルールセットスクリプト内に設定を書くのではなく、`natd(8)` の設定は設定ファイルに書くのが最適です。
そのためには、`/etc/rc.conf` 経由で設定ファイルのパスを指定する追加フラグを渡す必要があります。

```
natd_flags="-f /etc/natd.conf"
```

> **注記**: 指定するファイルには、1行に1つずつ設定オプションを記述する必要があります。設定ファイルと利用可能な変数について詳しくは `natd(8)` を参照してください。以下は1行に1つずつ記述した2つの設定例です。
>
> ```
> redirect_port tcp 192.168.0.2:6667 6667
> redirect_addr 192.168.0.3 128.1.1.3
> ```

<a id="firewalls-ipfw-cmd"></a>
### ipfw コマンド

稼働中のファイアウォールに対して、`ipfw` を使って手動で単一のルールを追加したり削除したりできます。
この方法の問題点は、システムを再起動すると変更がすべて失われることです。
代わりに、すべてのルールをファイルに記述しておき、起動時にそのファイルからルールを読み込み、ファイルを変更したときもそれで現在稼働中のファイアウォールルールを置き換えることを推奨します。

`ipfw` は、稼働中のファイアウォールルールをコンソール画面に表示する便利な手段でもあります。
IPFW のアカウンティング機能は各ルールに対してカウンタを動的に作成し、そのルールに一致したパケット数を数えます。
ルールのテスト中にルールをカウンタ付きで一覧表示することは、ルールが期待どおりに動いているかを確かめる方法の一つです。

稼働中のすべてのルールを順番に表示するには次のようにします。

```shell
# ipfw list
```

最後にルールが一致した時刻のタイムスタンプ付きで稼働中の全ルールを表示するには次のようにします。

```shell
# ipfw -t list
```

次の例では、ルール自体とあわせてアカウンティング情報と一致したルールごとのパケット数を表示します。
最初の列がルール番号、続いて一致したパケット数とバイト数、その後にルール本体が表示されます。

```shell
# ipfw -a list
```

静的ルールに加えて動的ルールも表示するには次のようにします。

```shell
# ipfw -d list
```

期限切れの動的ルールもあわせて表示するには次のようにします。

```shell
# ipfw -d -e list
```

カウンタをゼロにリセットするには次のようにします。

```shell
# ipfw zero
```

番号 *NUM* のルールについてのみカウンタをゼロにするには次のようにします。

```shell
# ipfw zero NUM
```

<a id="chapter-34-heading-26"></a>
#### ファイアウォールメッセージのログ記録

ログ機能を有効にしていても、IPFW は自動的にルールのログを生成することはありません。
ルールセット内のどのルールをログに記録するかはファイアウォール管理者が決め、それらのルールに `log` キーワードを追加します。
通常は拒否（deny）ルールのみをログに記録します。
ルールセットの最後のルールとして、`log` キーワード付きの「ipfw 既定ですべて拒否」ルールを重複して配置するのが慣例です。
こうすることで、ルールセットのどのルールにも一致しなかったすべてのパケットを確認できます。

ログ記録は諸刃の剣です。
注意しないと、過剰なログデータや DoS 攻撃によってログファイルがディスクを埋め尽くすことがあります。
ログメッセージは `syslogd` に書き込まれるだけでなく root コンソール画面にも表示されるため、すぐに煩わしくなります。

カーネルオプション `IPFIREWALL_VERBOSE_LIMIT=5` は、特定のルールのパケット一致に関して `syslogd(8)` へ連続して送られるメッセージ数を制限します。
カーネルでこのオプションを有効にすると、特定のルールに関する連続メッセージ数は指定された数までに抑えられます。
同じログメッセージが 200 件並んでも意味はありません。
このオプションを 5 に設定すると、特定のルールに関する連続メッセージは 5 件まで `syslogd` に記録され、残りの同一の連続メッセージは集計されて次のような文言で `syslogd` へ送られます。

```
last message repeated 45 times
```

ログに記録されたパケットメッセージはすべて、既定で `/etc/syslog.conf` に定義されている `/var/log/security` へ書き込まれます。

<a id="firewalls-ipfw-rules-script"></a>
#### ルールスクリプトの作成

経験豊富な IPFW 利用者の多くは、ルールを収めたファイルを作成し、スクリプトとして実行できる形式で記述します。
この方法の最大の利点は、システムを再起動して有効化しなくても、ファイアウォールルールを一括で再読み込みできる点にあります。
手順を何度でも実行できるため、新しいルールのテストにも便利です。
スクリプトであるため、よく使う値に変数置換（symbolic substitution）を使って複数のルールへ埋め込むこともできます。

次の例のスクリプトは、`sh(1)`、`csh(1)`、`tcsh(1)` シェルで使われる構文と互換性があります（訳注: 原文では `sh(1)`・`csh(1)`・`tcsh(1)` と書かれていますが、下記の `VAR="value"` 形式の代入は `#!/bin/sh` による `sh(1)` 互換構文です）。
変数置換を行う箇所には先頭にドル記号（`$`）を付けます。
変数の定義側には `$` を付けません。
変数に設定する値は二重引用符（`""`）で囲む必要があります。

ルールファイルは次のように書き始めます。

```
############### start of example ipfw rules script #############
#
ipfw -q -f flush       # Delete all rules
# Set defaults
oif="tun0"             # out interface
odns="192.0.2.11"      # ISP's DNS server IP address
cmd="ipfw -q add "     # build rule prefix
ks="keep-state"        # just too lazy to key this each time
$cmd 00500 check-state
$cmd 00502 deny all from any to any frag
$cmd 00501 deny tcp from any to any established
$cmd 00600 allow tcp from any to any 80 out via $oif setup $ks
$cmd 00610 allow tcp from any to $odns 53 out via $oif setup $ks
$cmd 00611 allow udp from any to $odns 53 out via $oif $ks
################### End of example ipfw rules script ############
```

この例では変数置換のフィールドにどう値が入るかに焦点を当てているため、ルール自体の内容は重要ではありません。

上記の例が `/etc/ipfw.rules` にある場合、次のコマンドでルールを再読み込みできます。

```shell
# sh /etc/ipfw.rules
```

`/etc/ipfw.rules` はどこに置いてもよく、ファイル名も任意です。

同じことは、次のコマンドを手動で実行することでも実現できます。

```shell
# ipfw -q -f flush
# ipfw -q add check-state
# ipfw -q add deny all from any to any frag
# ipfw -q add deny tcp from any to any established
# ipfw -q add allow tcp from any to any 80 out via tun0 setup keep-state
# ipfw -q add allow tcp from any to 192.0.2.11 53 out via tun0 setup keep-state
# ipfw -q add 00611 allow udp from any to 192.0.2.11 53 out via tun0 keep-state
```

<a id="firewalls-ipfw-kernelconfig"></a>
### IPFW カーネルオプション

カスタムカーネルへ IPFW サポートを静的にコンパイルして組み込むには、[FreeBSD カーネルの設定](09-kernelconfig.md#kernelconfig) の手順を参照してください。
カスタムカーネル設定ファイルでは次のオプションが利用できます。

```
options    IPFIREWALL			# enables IPFW
options    IPFIREWALL_VERBOSE		# enables logging for rules with log keyword to syslogd(8)
options    IPFIREWALL_VERBOSE_LIMIT=5	# limits number of logged packets per-entry
options    IPFIREWALL_DEFAULT_TO_ACCEPT # sets default policy to pass what is not explicitly denied
options    IPFIREWALL_NAT		# enables basic in-kernel NAT support
options    LIBALIAS			# enables full in-kernel NAT support
options    IPFIREWALL_NAT64		# enables in-kernel NAT64 support
options    IPFIREWALL_NPTV6		# enables in-kernel IPv6 NPT support
options    IPFIREWALL_PMOD		# enables protocols modification module support
options    IPDIVERT			# enables NAT through natd(8)
```

> **注記**: IPFW はカーネルモジュールとして読み込むことができます。上記のオプションは既定でモジュールとしてビルドされるか、実行時にチューナブルを使って設定できます。

<a id="firewalls-ipf"></a>
## IPFILTER (IPF)

IPFILTER（IPF とも呼ばれます）は、FreeBSD、NetBSD、OpenBSD、Solaris™ など複数のオペレーティングシステムに移植されているクロスプラットフォームのオープンソースファイアウォールです。

IPFILTER はカーネル側のファイアウォールおよび NAT 機構であり、ユーザーランドのプログラムから制御・監視できます。
`ipf` を使ってファイアウォールルールを設定・削除し、`ipnat` を使って NAT ルールを設定・削除し、`ipfstat` を使って IPFILTER のカーネル部分の実行時統計情報を表示し、`ipmon` を使って IPFILTER の動作をシステムログファイルへ記録できます。

IPF はもともと「最後に一致したルールが勝つ（the last matching rule wins）」というルール処理ロジックとステートレスルールだけを使って書かれていました。
その後、`quick` オプションや `keep state` オプションが追加され、機能が強化されています。

IPF FAQ は [https://www.phildev.net/ipf/index.html](https://www.phildev.net/ipf/index.html) にあります。
IPFilter メーリングリストの検索可能なアーカイブは [https://marc.info/?l=ipfilter](https://marc.info/?l=ipfilter) で利用できます。

本節では、FreeBSD における IPF に焦点を当て、`quick` と `keep state` オプションを含むルールの例を紹介します。

<a id="chapter-34-heading-30"></a>
### IPF を有効にする

IPF は FreeBSD の基本インストールに動的読み込み可能なカーネルモジュールとして含まれているため、IPF を有効にするためにカスタムカーネルをビルドする必要はありません。

IPF サポートをカスタムカーネルへ静的に組み込みたい場合は、[FreeBSD カーネルの設定](09-kernelconfig.md#kernelconfig) の手順を参照してください。
次のカーネルオプションが利用できます。

```
options IPFILTER
options IPFILTER_LOG
options IPFILTER_LOOKUP
options IPFILTER_DEFAULT_BLOCK
```

ここで、`options IPFILTER` は IPFILTER のサポートを有効にし、`options IPFILTER_LOG` は `log` キーワードを持つすべてのルールについて `ipl` パケットログ用擬似デバイスを使った IPF のログ記録を有効にし、`IPFILTER_LOOKUP` は IP 検索を高速化するための IP プールを有効にし、`options IPFILTER_DEFAULT_BLOCK` はファイアウォールの `pass` ルールに一致しないパケットをすべて遮断するように既定の挙動を変更します。

システム起動時に IPF を有効にするには、`/etc/rc.conf` に次の項目を追加します。
これらの設定により、ログ記録と `default pass all`（既定ですべて通過）も有効になります。
カスタムカーネルをコンパイルせずに既定のポリシーを `block all`（すべて遮断）へ変更するには、ルールセットの最後に `block all` ルールを追加するのを忘れないでください。

```
ipfilter_enable="YES"             # Start ipf firewall
ipfilter_rules="/etc/ipf.rules"   # loads rules definition text file
ipv6_ipfilter_rules="/etc/ipf6.rules" # loads rules definition text file for IPv6
ipmon_enable="YES"                # Start IP monitor log
ipmon_flags="-Ds"                 # D = start as daemon
                                  # s = log to syslog
                                  # v = log tcp window, ack, seq
                                  # n = map IP & port to names
```

NAT 機能が必要な場合は、次の行も追加します。

```
gateway_enable="YES"              # Enable as LAN gateway
ipnat_enable="YES"                # Start ipnat function
ipnat_rules="/etc/ipnat.rules"    # rules definition file for ipnat
```

その後、今すぐ IPF を起動するには次のように実行します。

```
#  service ipfilter start
```

ファイアウォールルールを読み込むには、`ipf` を使ってルールセットファイル名を指定します。
現在稼働中のファイアウォールルールを置き換えるには、次のコマンドを使用します。

```shell
# ipf -Fa -f /etc/ipf.rules
```

ここで `-Fa` は内部のルールテーブルをすべて消去（flush）し、`-f` は読み込むルールを記述したファイルを指定します。

これにより、システムを再起動することなく独自のルールセットを変更し、稼働中のファイアウォールを最新のルールで更新できます。
手順を何度でも実行できるため、新しいルールのテストにも便利です。

このコマンドで使えるその他のフラグの詳細は `ipf(8)` を参照してください。

<a id="chapter-34-heading-31"></a>
### IPF ルール構文

ここでは、ステートフルルールを作成するための IPF ルール構文を説明します。
ルールを作成するときは、ルールに `quick` キーワードが含まれていない限り、すべてのルールが順番に読み込まれ、**最後に一致したルール**が適用される点に注意してください。
つまり、パケットに最初に一致したルールが `pass` であっても、その後ろに一致する `block` ルールがあれば、そのパケットは破棄されます。
サンプルのルールセットは `/usr/share/examples/ipfilter` にあります。

ルールを書く際、`#` 文字はコメントの開始を示し、そのルールの機能を説明するためにルール末尾に置くことも、単独の行に置くこともできます。
空行はすべて無視されます。

ルール内で使うキーワードは、左から右へ決まった順序で記述する必要があります。
必須のキーワードと省略可能なキーワードがあります。
一部のキーワードにはサブオプションがあり、それら自体がキーワードとなってさらにサブオプションを持つこともあります。
キーワードの順序は次のとおりです。大文字で示された語は変数（値）を表し、小文字で示された語は直後に続く変数の前に必ず置く必要があります。

`*ACTION DIRECTION OPTIONS* proto *PROTO_TYPE* from *SRC_ADDR SRC_PORT* to *DST_ADDR DST_PORT TCP_FLAG|ICMP_TYPE* keep state *STATE*`

ここでは、これらのキーワードとオプションをそれぞれ説明します。
利用可能なすべてのオプションを網羅したものではありません。
IPF ルールを作成する際に使える構文の完全な解説と各キーワードの使用例は `ipf(5)` を参照してください。

* **ACTION**: アクションキーワードは、パケットがそのルールに一致したときに何をするかを指定します。すべてのルールにはアクションが**必須**です。次のアクションが認識されます。

  `block`: パケットを破棄する。

  `pass`: パケットを許可する。

  `log`: ログレコードを生成する。

  `count`: パケット数とバイト数を数える。ルールがどの程度の頻度で使われているかの目安になる。

  `auth`: 別のプログラムによる追加処理のためにパケットをキューに入れる。

  `call`: IPF に組み込まれた関数を呼び出し、より複雑なアクションを実行する。

  `decapsulate`: パケットの内容を処理するためにヘッダを取り除く。

* **DIRECTION**: 次に、各ルールでは次のいずれかのキーワードを使ってトラフィックの方向を明示する必要があります。

  `in`: インバウンド（受信）パケットに対してルールを適用する。

  `out`: アウトバウンド（送信）パケットに対してルールを適用する。

  `all`: どちらの方向にもルールを適用する。

  システムに複数のインタフェースがある場合は、方向とあわせてインタフェースを指定できます。たとえば `in on fxp0` のように書きます。

* **OPTIONS**: オプションは省略可能です。ただし、複数のオプションを指定する場合は、ここに示す順序で記述する必要があります。

  `log`: 指定された `ACTION` を実行する際、パケットのヘッダ内容を `ipl(4)` パケットログ用擬似デバイスへ書き出す。

  `quick`: パケットがこのルールに一致した場合、ルールで指定された `ACTION` が実行され、このパケットに対する後続ルールの処理は一切行われない。

  `on`: 後ろに `ifconfig(8)` で表示されるインタフェース名を続ける必要がある。パケットが指定されたインタフェースを指定された方向に通過する場合にのみルールに一致する。

  `log` キーワードを使う場合、次の修飾子をこの順序で使用できます。

  `body`: ヘッダに続いてパケット内容の先頭 128 バイトもログに記録することを指定する。

  `first`: `log` キーワードを `keep state` オプションと併用する場合に推奨されるオプションで、ステートフル接続に一致するすべてのパケットではなく、きっかけとなった最初のパケットだけがログに記録されるようにする。

  エラー応答メッセージを指定するためのオプションも追加で用意されています。詳細は `ipf(5)` を参照してください。

* **PROTO_TYPE**: プロトコル種別は省略可能です。ただし、プロトコルの種類を定義するため、ルールで `SRC_PORT` または `DST_PORT` を指定する必要がある場合は必須になります。プロトコル種別を指定するときは、`proto` キーワードの後ろに `/etc/protocols` のプロトコル番号またはプロトコル名を続けます。プロトコル名の例としては `tcp`、`udp`、`icmp` などがあります。`PROTO_TYPE` を指定して `SRC_PORT` や `DST_PORT` を指定しない場合、そのプロトコルのすべてのポート番号がそのルールに一致します。

* **SRC_ADDR**: `from` キーワードは必須であり、後ろにパケットの送信元を表すキーワードを続けます。送信元には、ホスト名、後ろに CIDR マスクを付けた IP アドレス、アドレスプール、または `all` キーワードを指定できます。例については `ipf(5)` を参照してください。

  ドット区切りの数値表記 / マスク長表記で簡単に表せない IP アドレス範囲を一致させる方法はありません。CIDR マスクの計算を簡単にするには、`net-mgmt/ipcalc` のパッケージまたは port を使えます。詳しい情報はユーティリティの Web ページ（[https://jodies.de/ipcalc](https://jodies.de/ipcalc)）にあります。

* **SRC_PORT**: 送信元のポート番号は省略可能です。ただし、使用する場合はルール内で先に `PROTO_TYPE` が定義されている必要があります。また、ポート番号の前には `proto` キーワードが必要です。

  次の各種比較演算子がサポートされています：`=`（等しい）、`!=`（等しくない）、`<`（より小さい）、`>`（より大きい）、`<=`（以下）、`>=`（以上）。

  ポート範囲を指定するには、2つのポート番号を `<>`（より小さい、またはより大きい＝範囲外）、`><`（より大きく、かつより小さい＝範囲内）、または `:`（以上、かつ以下＝両端を含む範囲内）で挟みます。

* **DST_ADDR**: `to` キーワードは必須であり、後ろにパケットの宛先を表すキーワードを続けます。`SRC_ADDR` と同様に、ホスト名、後ろに CIDR マスクを付けた IP アドレス、アドレスプール、または `all` キーワードを指定できます。

* **DST_PORT**: `SRC_PORT` と同様に、宛先のポート番号は省略可能です。ただし、使用する場合はルール内で先に `PROTO_TYPE` が定義されている必要があります。また、ポート番号の前には `proto` キーワードが必要です。

* **TCP_FLAG|ICMP_TYPE**: `PROTO_TYPE` として `tcp` を指定した場合、接続状態を判定するために使われる TCP フラグを表す文字を指定できます。指定できる値は `S`（SYN）、`A`（ACK）、`P`（PSH）、`F`（FIN）、`U`（URG）、`R`（RST）、`C`（CWN）、`E`（ECN）です。

  `PROTO_TYPE` として `icmp` を指定した場合、一致させる ICMP 種別を指定できます。指定可能な種別については `ipf(5)` を参照してください。

* **STATE**: `pass` ルールに `keep state` が含まれていると、IPF は動的ステートテーブルにエントリを追加し、その接続に一致する後続のパケットを許可します。IPF は TCP、UDP、ICMP の各セッションの状態を追跡できます。別のプロトコルであっても、アクティブなセッションの一部であると IPF が確実に判断できるパケットはすべて許可されます。

  IPF では、パブリックインターネットに接続されたインタフェースから出ていくパケットは、まず動的ステートテーブルと照合されます。アクティブなセッション通信を構成する次の期待パケットに一致した場合、そのパケットはファイアウォールを通過し、動的ステートテーブル内のセッション通信フローの状態が更新されます。すでにアクティブなセッションに属していないパケットは、アウトバウンドルールセットと照合されます。パブリックインターネットに接続されたインタフェースから入ってくるパケットも、まず動的ステートテーブルと照合されます。アクティブなセッションを構成する次の期待パケットに一致した場合、そのパケットはファイアウォールを通過し、動的ステートテーブル内のセッション通信フローの状態が更新されます。すでにアクティブなセッションに属していないパケットは、インバウンドルールセットと照合されます。

  `keep state` の後ろにはいくつかのキーワードを追加できます。これらを使うと、接続数上限や接続の生存期間の設定など、ステートフルフィルタリングを制御するさまざまなオプションを設定できます。利用可能なオプションの一覧と解説は `ipf(5)` を参照してください。

<a id="chapter-34-heading-32"></a>
### ルールセットの例

ここでは、`pass` ルールに一致するサービスだけを許可し、それ以外をすべて遮断するルールセットの例を作成する方法を示します。

FreeBSD は内部通信にループバックインタフェース（`lo0`）と IP アドレス `127.0.0.1` を使います。
ファイアウォールルールセットには、これらの内部用パケットの自由なやり取りを許可するルールを含める必要があります。

```
# no restrictions on loopback interface
pass in quick on lo0 all
pass out quick on lo0 all
```

インターネットに接続されたパブリックインタフェースは、すべてのアウトバウンド接続およびインバウンド接続のアクセスを認可・制御するために使われます。
1つ以上のインタフェースがプライベートネットワークに接続されている場合、LAN から発信されたパケットが内部ネットワーク間やインターネット接続インタフェースへ流れるように、それらの内部インタフェースにもルールが必要になることがあります。
ルールセットは大きく分けて、信頼された内部インタフェース、パブリックインタフェース経由のアウトバウンド接続、パブリックインタフェース経由のインバウンド接続の3つのセクションに整理するとよいでしょう。

次の2つのルールは、`xl0` という名前の信頼された LAN インタフェースを通過するすべてのトラフィックを許可します。

```
# no restrictions on inside LAN interface for private network
pass out quick on xl0 all
pass in quick on xl0 all
```

パブリックインタフェースのアウトバウンドおよびインバウンドセクションのルールでは、頻繁に一致するルールをあまり一致しないルールより前に配置し、セクションの最後のルールでそのインタフェースと方向のすべてのパケットを遮断してログに記録するようにします。

次のルール群は、`dc0` という名前のパブリックインタフェースのアウトバウンドセクションを定義します。
これらのルールはステートを保持し、内部システムがパブリックインターネットへのアクセスを許可されている特定のサービスを識別します。
すべてのルールで `quick` を使い、適切なポート番号と、該当する場合は宛先アドレスを指定しています。

```
# interface facing Internet (outbound)
# Matches session start requests originating from or behind the
# firewall, destined for the Internet.

# Allow outbound access to public DNS servers.
# Replace x.x.x.x with address listed in /etc/resolv.conf.
# Repeat for each DNS server.
pass out quick on dc0 proto tcp from any to x.x.x.x port = 53 flags S keep state
pass out quick on dc0 proto udp from any to x.x.x.x port = 53 keep state

# Allow access to ISP's specified DHCP server for cable or DSL networks.
# Use the first rule, then check log for the IP address of DHCP server.
# Then, uncomment the second rule, replace z.z.z.z with the IP address,
# and comment out the first rule
pass out log quick on dc0 proto udp from any to any port = 67 keep state
#pass out quick on dc0 proto udp from any to z.z.z.z port = 67 keep state

# Allow HTTP and HTTPS
pass out quick on dc0 proto tcp from any to any port = 80 flags S keep state
pass out quick on dc0 proto tcp from any to any port = 443 flags S keep state

# Allow email
pass out quick on dc0 proto tcp from any to any port = 110 flags S keep state
pass out quick on dc0 proto tcp from any to any port = 25 flags S keep state

# Allow NTP
pass out quick on dc0 proto tcp from any to any port = 37 flags S keep state

# Allow FTP
pass out quick on dc0 proto tcp from any to any port = 21 flags S keep state

# Allow SSH
pass out quick on dc0 proto tcp from any to any port = 22 flags S keep state

# Allow ping
pass out quick on dc0 proto icmp from any to any icmp-type 8 keep state

# Block and log everything else
block out log first quick on dc0 all
```

次のパブリックインタフェースのインバウンドセクションのルール例では、望ましくないパケットを最初にすべて遮断します。
これにより、最後のルールでログに記録されるパケットの数を減らせます。

```
# interface facing Internet (inbound)
# Block all inbound traffic from non-routable or reserved address spaces
block in quick on dc0 from 192.168.0.0/16 to any    #RFC 1918 private IP
block in quick on dc0 from 172.16.0.0/12 to any     #RFC 1918 private IP
block in quick on dc0 from 10.0.0.0/8 to any        #RFC 1918 private IP
block in quick on dc0 from 127.0.0.0/8 to any       #loopback
block in quick on dc0 from 0.0.0.0/8 to any         #loopback
block in quick on dc0 from 169.254.0.0/16 to any    #DHCP auto-config
block in quick on dc0 from 192.0.2.0/24 to any      #reserved for docs
block in quick on dc0 from 204.152.64.0/23 to any   #Sun cluster interconnect
block in quick on dc0 from 224.0.0.0/3 to any       #Class D & E multicast

# Block fragments and too short tcp packets
block in quick on dc0 all with frags
block in quick on dc0 proto tcp all with short

# block source routed packets
block in quick on dc0 all with opt lsrr
block in quick on dc0 all with opt ssrr

# Block OS fingerprint attempts and log first occurrence
block in log first quick on dc0 proto tcp from any to any flags FUP

# Block anything with special options
block in quick on dc0 all with ipopts

# Block public pings and ident
block in quick on dc0 proto icmp all icmp-type 8
block in quick on dc0 proto tcp from any to any port = 113

# Block incoming Netbios services
block in log first quick on dc0 proto tcp/udp from any to any port = 137
block in log first quick on dc0 proto tcp/udp from any to any port = 138
block in log first quick on dc0 proto tcp/udp from any to any port = 139
block in log first quick on dc0 proto tcp/udp from any to any port = 81
```

`log first` オプション付きのルールでメッセージが記録されたときは、`ipfstat -hio` を実行してそのルールが何回一致したかを確認してください。
一致回数が非常に多い場合は、システムが攻撃を受けている可能性があります。

インバウンドセクションの残りのルールでは、インターネットから開始することが許可される接続を定義します。
最後のルールは、このセクションの前のルールで明示的に許可されなかったすべての接続を拒否します。

```
# Allow traffic in from ISP's DHCP server. Replace z.z.z.z with
# the same IP address used in the outbound section.
pass in quick on dc0 proto udp from z.z.z.z to any port = 68 keep state

# Allow public connections to specified internal web server
pass in quick on dc0 proto tcp from any to x.x.x.x port = 80 flags S keep state

# Block and log only first occurrence of all remaining traffic.
block in log first quick on dc0 all
```

<a id="chapter-34-heading-33"></a>
### NAT の設定

NAT を有効にするには、`/etc/rc.conf` に次の記述を追加し、NAT ルールを収めたファイル名を指定します。

```
gateway_enable="YES"
ipnat_enable="YES"
ipnat_rules="/etc/ipnat.rules"
```

NAT ルールは柔軟で、企業ユーザーと家庭ユーザーのどちらのニーズにも合わせて多様な処理を実現できます。
ここで紹介するルール構文は、一般的な使い方を示すために簡略化したものです。
ルール構文の完全な解説は `ipnat(5)` を参照してください。

NAT ルールの基本構文は次のとおりです。ルールは `map` で始まり、*IF* は外部インタフェース名に置き換えます。

```
map IF LAN_IP_RANGE -> PUBLIC_ADDRESS
```

*LAN_IP_RANGE* は内部クライアントが使う IP アドレスの範囲です。
通常は `192.168.1.0/24` のようなプライベートアドレス範囲を指定します。
*PUBLIC_ADDRESS* には、静的な外部 IP アドレス、または *IF* に割り当てられた IP アドレスを表すキーワード `0/32` のいずれかを指定できます。

IPF では、パブリック宛先のパケットが LAN からファイアウォールに到着すると、まずファイアウォールルールセットのアウトバウンドルールを通過します。
次に、パケットは NAT ルールセットへ渡されます。NAT ルールセットは上から下へ読み込まれ、最初に一致したルールが適用されます。
IPF は各 NAT ルールをパケットのインタフェース名および送信元 IP アドレスと照合します。
パケットのインタフェース名が NAT ルールに一致すると、プライベート LAN 内の送信元 IP アドレスが *LAN_IP_RANGE* で指定された IP アドレス範囲に含まれるかどうかが調べられます。
一致した場合、パケットの送信元 IP アドレスは *PUBLIC_ADDRESS* で指定されたパブリック IP アドレスに書き換えられます。
IPF は内部の NAT テーブルにエントリを登録し、インターネットからパケットが戻ってきたときに、ファイアウォールルールへ渡してさらに処理する前に元のプライベート IP アドレスへ戻せるようにします。

多数の内部システムや複数のサブネットを持つネットワークでは、すべてのプライベート IP アドレスを単一のパブリック IP アドレスへ集約する処理がリソース上の問題になることがあります。
この問題を緩和するには2つの方法があります。

1つ目の方法は、送信元ポートとして使うポート範囲を割り当てることです。
`portmap` キーワードを追加すると、指定した範囲内の送信元ポートだけを使うように NAT に指示できます。

```
map dc0 192.168.1.0/24 -> 0/32 portmap tcp/udp 20000:60000
```

あるいは、`auto` キーワードを使うと、利用可能なポートを NAT に自動決定させられます。

```
map dc0 192.168.1.0/24 -> 0/32 portmap tcp/udp auto
```

2つ目の方法は、パブリックアドレスのプールを使うことです。
これは、単一のパブリックアドレスに収まりきらないほど多くの LAN アドレスがあり、かつパブリック IP アドレスのブロックが利用できる場合に便利です。
パケットのアドレスが外向きに変換される際、NAT が IP アドレスを選ぶためのプールとしてこれらのパブリックアドレスを使えます。

パブリック IP アドレスの範囲はネットマスクまたは CIDR 表記で指定できます。
次の2つのルールは同等です。

```
map dc0 192.168.1.0/24 -> 204.134.75.0/255.255.255.0
map dc0 192.168.1.0/24 -> 204.134.75.0/24
```

よく行われる構成として、外部からアクセス可能な Web サーバーやメールサーバーを内部ネットワークセグメントに隔離して配置する方法があります。
これらのサーバーからのトラフィックも NAT を受ける必要がありますが、インバウンドトラフィックを正しいサーバーへ導くにはポートリダイレクトが必要です。
たとえば、内部アドレス `10.0.10.25` を使う Web サーバーをパブリック IP アドレス `20.20.20.5` に対応付けるには、次のルールを使います。

```
rdr dc0 20.20.20.5/32 port 80 -> 10.0.10.25 port 80
```

それが唯一の Web サーバーである場合は、外部からのすべての HTTP リクエストを `10.0.10.25` へリダイレクトする次のルールでも動作します。

```
rdr dc0 0.0.0.0/0 port 80 -> 10.0.10.25 port 80
```

IPF には NAT と組み合わせて使える組み込みの FTP プロキシがあります。
これは、アクティブまたはパッシブ FTP 接続要求のアウトバウンドトラフィックをすべて監視し、FTP データチャネルで使われるポート番号を含む一時的なフィルタールールを動的に作成します。
これにより、FTP 接続のために高位ポートの広い範囲を開けておく必要がなくなります。

次の例では、最初のルールが内部 LAN からのアウトバウンド FTP トラフィックに対してプロキシを呼び出します。
2つ目のルールはファイアウォールからインターネットへの FTP トラフィックを通過させ、3つ目のルールは内部 LAN からの FTP 以外のすべてのトラフィックを処理します。

```
map dc0 10.0.10.0/29 -> 0/32 proxy port 21 ftp/tcp
map dc0 0.0.0.0/0 -> 0/32 proxy port 21 ftp/tcp
map dc0 10.0.10.0/29 -> 0/32
```

FTP の `map` ルールは NAT ルールより前に置きます。そうすることで、パケットが FTP ルールに一致したとき、FTP プロキシが一時的なフィルタールールを作成し、FTP セッションのパケットを通過させて NAT を行えるようになります。
FTP ではないすべての LAN パケットは FTP ルールには一致しませんが、3つ目のルールに一致して NAT を受けます。

FTP プロキシを使わない場合は、代わりに次のようなファイアウォールルールが必要になります。
プロキシを使わない場合は `1024` より大きいすべてのポートを許可する必要がある点に注意してください。

```
# Allow out LAN PC client FTP to public Internet
# Active and passive modes
pass out quick on rl0 proto tcp from any to any port = 21 flags S keep state

# Allow out passive mode data channel high order port numbers
pass out quick on rl0 proto tcp from any to any port > 1024 flags S keep state

# Active mode let data channel in from FTP server
pass in quick on rl0 proto tcp from any to any port = 20 flags S keep state
```

NAT ルールを含むファイルを編集したときは、必ず `-CF` を付けて `ipnat` を実行し、現在の NAT ルールを削除して動的変換テーブルの内容を消去（flush）してください。
あわせて `-f` を付け、読み込む NAT ルールセットの名前を指定します。

```shell
# ipnat -CF -f /etc/ipnat.rules
```

NAT の統計情報を表示するには次のようにします。

```shell
# ipnat -s
```

NAT テーブルの現在のマッピング一覧を表示するには次のようにします。

```shell
# ipnat -l
```

詳細モード（verbose mode）を有効にして、ルール処理やアクティブなルール、テーブルエントリに関する情報を表示するには次のようにします。

```shell
# ipnat -v
```

<a id="chapter-34-heading-34"></a>
### IPF 統計情報の表示

IPF には `ipfstat(8)` が含まれており、パケットがファイアウォールを通過してルールに一致する際に収集された統計情報を取得・表示できます。
統計情報は、最後にファイアウォールを起動した時点、または最後に `ipf -Z` でゼロリセットした時点から累積されます。

`ipfstat` の既定の出力は次のようになります。

```shell
input packets: blocked 99286 passed 1255609 nomatch 14686 counted 0
 output packets: blocked 4200 passed 1284345 nomatch 14687 counted 0
 input packets logged: blocked 99286 passed 0
 output packets logged: blocked 0 passed 0
 packets logged: input 0 output 0
 log failures: input 3898 output 0
 fragment state(in): kept 0 lost 0
 fragment state(out): kept 0 lost 0
 packet state(in): kept 169364 lost 0
 packet state(out): kept 431395 lost 0
 ICMP replies: 0 TCP RSTs sent: 0
 Result cache hits(in): 1215208 (out): 1098963
 IN Pullups succeeded: 2 failed: 0
 OUT Pullups succeeded: 0 failed: 0
 Fastroute successes: 0 failures: 0
 TCP cksum fails(in): 0 (out): 0
 Packet log flags set: (0)
```

いくつかのオプションが用意されています。
インバウンド用の `-i` またはアウトバウンド用の `-o` を指定すると、現在カーネルに組み込まれて使用されている該当方向のフィルタールール一覧を取得して表示します。
ルール番号もあわせて表示するには `-n` を付けます。
たとえば、`ipfstat -on` はアウトバウンドのルールテーブルをルール番号付きで表示します。

```shell
@1 pass out on xl0 from any to any
@2 block out on dc0 from any to any
@3 pass out quick on dc0 proto tcp/udp from any to any keep state
```

各ルールの先頭に一致回数を表示するには `-h` を付けます。
たとえば、`ipfstat -oh` はアウトバウンドの内部ルールテーブルを、各ルールの先頭に利用回数を付けて表示します。

```shell
2451423 pass out on xl0 from any to any
354727 block out on dc0 from any to any
430918 pass out quick on dc0 proto tcp/udp from any to any keep state
```

ステートテーブルを `top(1)` に似た形式で表示するには、`ipfstat -t` を使います。
ファイアウォールが攻撃を受けているとき、このオプションを使うと攻撃元のパケットを特定して確認できます。
追加のサブフラグを使うと、リアルタイムで監視する宛先・送信元の IP、ポート、プロトコルを選択できます。
詳しくは `ipfstat(8)` を参照してください。

<a id="chapter-34-heading-35"></a>
### IPF のログ記録

IPF には `ipmon` が用意されており、ファイアウォールのログ情報を人間が読める形式で書き出すことができます。
これを使うには、あらかじめ [FreeBSD カーネルの設定](09-kernelconfig.md#kernelconfig) の手順に従ってカスタムカーネルへ `options IPFILTER_LOG` を追加しておく必要があります。

過去のイベントのログを後から確認できるよう継続的なシステムログファイルを提供するため、このコマンドは通常デーモンモードで実行します。
FreeBSD にはシステムログを自動的にローテーションする `syslogd(8)` 機能が組み込まれているため、`/etc/rc.conf` の既定の `ipmon_flags` 指定では `-Ds` を使います。

```
ipmon_flags="-Ds" # D = start as daemon
                  # s = log to syslog
                  # v = log tcp window, ack, seq
                  # n = map IP & port to names
```

ログを記録しておくと、どのパケットが破棄されたのか、どのアドレスから来たのか、どこへ向かっていたのかといった情報を事後に確認できます。
この情報は攻撃者の追跡に役立ちます。

`/etc/rc.conf` でログ機能を有効にして `service ipmon start` で起動した後は、IPF は `log` キーワードを含むルールだけを記録します。
ルールセット内のどのルールを記録すべきかはファイアウォール管理者が決め、通常は拒否ルールのみを記録します。
ルールセットの最後のルールに `log` キーワードを含めるのが慣例です。
これにより、ルールセットのどのルールにも一致しなかったすべてのパケットを確認できます。

既定では、`ipmon -Ds` モードはログファシリティとして `local0` を使います。
記録データをさらに分類するために、次のログレベルが使えます。

```shell
LOG_INFO - packets logged using the "log" keyword as the action rather than pass or block.
LOG_NOTICE - packets logged which are also passed
LOG_WARNING - packets logged which are also blocked
LOG_ERR - packets which have been logged and which can be considered short due to an incomplete header
```

IPF のすべてのデータを `/var/log/ipfilter.log` へ記録するよう設定するには、まず空ファイルを作成します。

```shell
# touch /var/log/ipfilter.log
```

次に、ログに記録されたすべてのメッセージを指定ファイルへ書き出すため、`/etc/syslog.conf` に次の行を追加します。

```
local0.* /var/log/ipfilter.log
```

変更を有効にし、修正された `/etc/syslog.conf` を `syslogd(8)` に読み込ませるには、`service syslogd reload` を実行します。

新しいログファイルをローテーションするよう `/etc/newsyslog.conf` を編集するのも忘れないでください。

`ipmon` が生成するメッセージは、空白文字で区切られたデータフィールドで構成されます。
すべてのメッセージに共通するフィールドは次のとおりです。

1. パケットを受信した日付。
2. パケットを受信した時刻。時・分・秒・秒の端数を表す `HH:MM:SS.F` 形式。
3. パケットを処理したインタフェースの名前。
4. `@0:17` 形式でのルールのグループ番号とルール番号。
5. アクション：`p` は通過（passed）、`b` は遮断（blocked）、`S` は短いパケット（short packet）、`n` はどのルールにも一致せず、`L` はログ（log）ルール。
6. 3つのフィールドとして書かれたアドレス：コンマで区切った送信元アドレスとポート、`->` 記号、および宛先アドレスとポート（例：`209.53.17.22,80 -> 198.73.220.17,1722`）。
7. `PR` に続けてプロトコル名または番号（例：`PR tcp`）。
8. `len` に続けてパケットのヘッダ長と全長（例：`len 20 40`）。

パケットが TCP パケットの場合は、さらにハイフンで始まり、設定されている各フラグに対応する文字を並べたフィールドが追加されます。
文字とフラグの一覧については `ipf(5)` を参照してください。

パケットが ICMP パケットの場合は、末尾に2つのフィールドが付きます。1つ目は常に `icmp`、2つ目は ICMP メッセージとサブメッセージ種別をスラッシュで区切ったものです。
たとえば、ポート到達不能（port unreachable）メッセージの場合は `icmp 3/3` となります。
