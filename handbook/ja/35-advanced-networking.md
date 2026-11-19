<a id="advanced-networking"></a>
# 高度なネットワーク設定（Advanced Networking）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/)の Chapter 35「Advanced Networking」（本リポジトリ既存目次では ID 34）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/advanced-networking/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。コマンド例・設定例・出力例は原文の記載どおりに保持しており、プロンプトの `#` は `root` 権限、`%` は一般ユーザー権限を示します。本リポジトリで未翻訳の章（`network` など）への相互参照は、公式 FreeBSD Handbook（英語版）の該当ページへリンクしています。

<a id="advanced-networking-synopsis"></a>
## 概要（Synopsis）

この章では、高度なネットワーク設定に関するさまざまなトピックを取り上げます。

この章を読むことで、次の内容を学べます。

* ゲートウェイと経路制御（ルーティング）の基本
* USB テザリングの設定方法
* IEEE® 802.11 無線 LAN デバイスおよび Bluetooth® デバイスの設定方法
* FreeBSD をブリッジとして動作させる方法
* ネットワーク経由の PXE ブートの設定方法
* FreeBSD における Common Address Redundancy Protocol（CARP）の有効化と活用方法
* FreeBSD で複数の VLAN を設定する方法
* Bluetooth ヘッドセットの設定方法

この章を読む前の前提知識は次のとおりです。

* `/etc/rc` スクリプトの基本的な仕組みを理解していること
* 基本的なネットワーク用語に馴染みがあること
* FreeBSD における基本的なネットワーク設定を理解していること（[FreeBSD network](https://docs.freebsd.org/en/books/handbook/network/#network)）
* 新しい FreeBSD カーネルの構成・インストール方法を知っていること（[カーネルの構築（Kernel Configuration）](09-kernelconfig.md#kernelconfig)）
* サードパーティ製ソフトウェアの追加インストール方法を知っていること（[パッケージとPorts（Packages and Ports）](04-ports.md#ports)）

<a id="network-routing"></a>
## ゲートウェイと経路制御（Gateways and Routes）

**ルーティング（routing）**とは、あるシステムから別のシステムへのネットワーク経路を見つけ出す仕組みです。
**ルート（route、経路）**は、「宛先（destination）」と「ゲートウェイ（gateway）」を表すアドレスの組として定義されます。
これは、指定された宛先へ通信するときに、指定されたゲートウェイ経由でパケットを送信することを意味します。
宛先には「個別ホスト」「サブネット」「デフォルト（`default`）」の 3 種類があり、他のどのルートにも一致しない場合は「デフォルトルート」が使われます。
ゲートウェイにも「個別ホスト」「インタフェース（リンクとも呼ばれます）」「イーサネットのハードウェア（MAC）アドレス」の 3 種類があります。
既知のルートは、ルーティングテーブル（経路表）に格納されます。

この節では、まずルーティングの基本を概観したうえで、FreeBSD システムをルータとして構成する方法とトラブルシューティングのヒントを説明します。

<a id="network-routing-default"></a>
### ルーティングの基本（Routing Basics）

FreeBSD システムのルーティングテーブルを表示するには、`netstat(1)` を使用します。

```shell
% netstat -r
Routing tables

Internet:
Destination      Gateway            Flags     Refs     Use     Netif Expire
default          outside-gw         UGS        37      418       em0
localhost        localhost          UH          0      181       lo0
test0            0:e0:b5:36:cf:4f   UHLW        5    63288       re0     77
10.20.30.255     link#1             UHLW        1     2421
example.com      link#1             UC          0        0
host1            0:e0:a8:37:8:1e    UHLW        3     4601       lo0
host2            0:e0:a8:37:8:1e    UHLW        0        5       lo0 =>
host2.example.com link#1            UC          0        0
224              link#1             UC          0        0
```

この例における各エントリの意味は次のとおりです。

* **`default`**: テーブルの最初のルートは `default` ルートを示しています。ローカルシステムはリモートホストへ接続する必要が生じたとき、まず既知の経路があるかルーティングテーブルを調べます。リモートホストがテーブル内のエントリに一致すれば、そのエントリで指定されたインタフェースを使って接続できるかを確認します。
  宛先がどのエントリにも一致しない場合、または既知の経路がすべて失敗した場合は、デフォルトルートのエントリが使われます。ローカルエリアネットワーク（LAN）上のホストでは、デフォルトルートの `Gateway` 欄にインターネットへ直接接続されているシステムが指定されます。このエントリを確認する際は、`Flags` 列にゲートウェイが利用可能であることを示す `UG` が含まれているかを確かめてください。
  マシン自身が外部へのゲートウェイとして機能している場合、そのデフォルトルートはインターネットサービスプロバイダ（ISP）側のゲートウェイマシンになります。
* **`localhost`**: 2 番目のルートは `localhost` ルートです。`localhost` の `Netif` 列に指定されているインタフェースは `lo0`（ループバックデバイス）であり、この宛先へのトラフィックはすべてネットワークへ送出せず内部で処理することを示します。
* **MAC アドレス**: `0:e0:` で始まるアドレスは MAC アドレスです。FreeBSD はローカルイーサネット上のホスト（この例では `test0`）を自動的に識別し、イーサネットインタフェース `re0` 経由でそのホストへのルートを追加します。この種類のルートには `Expire` 列に表示されるタイムアウトがあり、一定時間ホストから応答がない場合に自動的に削除されます。これらのホストは、最短経路の決定に基づいてローカルホストへのルートを計算する Routing Information Protocol（RIP）を用いて識別されます。
* **サブネット**: FreeBSD はローカルサブネット向けのサブネットルートも自動的に追加します。この例では、`10.20.30.255` がサブネット `10.20.30` のブロードキャストアドレス、`example.com` がそのサブネットに関連付けられたドメイン名です。`link#1` という表記は、マシン上の 1 番目のイーサネットカードを指します。
  ローカルネットワーク上のホストとローカルサブネットのルートは、`routed(8)` というデーモンによって自動的に設定されます。これが動作していない場合は、管理者が静的に定義したルートのみが存在します。
* **ホスト**: `host1` の行は、ホスト自身のイーサネットアドレスによって自分自身を指しています。送信元ホスト自身であるため、FreeBSD はイーサネットインタフェースではなくループバックインタフェース（`lo0`）を使うよう判断します。
  2 つの `host2` の行は、`ifconfig(8)` を使って作成されたエイリアスを表しています。`lo0` インタフェースの後ろにある `=>` 記号は、ループバックアドレスに加えてエイリアスが設定されていることを意味します。このようなルートはエイリアスを持つホスト上にのみ表示され、ローカルネットワーク上の他のすべてのホストには、この種のルートに対して `link#1` の行が表示されます。
* **`224`**: 最後の行（宛先サブネット `224`）はマルチキャストを扱います。

各ルートのさまざまな属性は `Flags` 列で確認できます。[よく見かけるルーティングテーブルのフラグ](#routeflags) に、主なフラグとその意味をまとめます。

<a id="routeflags"></a>
**表 1. よく見かけるルーティングテーブルのフラグ**

| フラグ | 意味 |
|---|---|
| U | ルートが有効（up）である。 |
| H | ルートの宛先が単一のホストである。 |
| G | この宛先へのパケットをすべてこのゲートウェイへ送り、そこから先の転送をゲートウェイに任せる。 |
| S | このルートは静的（static）に設定された。 |
| C | ローカルネットワーク向けに接続するための新しいルートを、このルートを基に複製（clone）する。通常はローカルネットワークで使われる。 |
| W | ローカルエリアネットワーク（クローン）ルートに基づいて自動設定されたルートである。 |
| L | イーサネット（リンク）ハードウェアへの参照を含むルートである。 |

FreeBSD システムでデフォルトルートを定義するには、`/etc/rc.conf` にデフォルトゲートウェイの IP アドレスを指定します。

```
defaultrouter="10.20.30.1"
```

`route` を使って手動でルートを追加することもできます。

```shell
# route add default 10.20.30.1
```

手動で追加したルートは再起動すると失われる点に注意してください。ルーティングテーブルを手動で操作する方法の詳細は、`route(8)` を参照してください。

<a id="network-static-routes"></a>
### 静的ルートを用いたルータの設定（Configuring a Router with Static Routes）

FreeBSD システムは、デュアルホームシステム（dual-homed system）であれば、ネットワークのデフォルトゲートウェイ（すなわちルータ）として構成できます。
デュアルホームシステムとは、少なくとも 2 つの異なるネットワークに属するホストのことです。
通常は各ネットワークを別々のネットワークインタフェースに接続しますが、IP エイリアシングを使って 1 つの物理インタフェースに異なるサブネット上の複数アドレスを割り当てることもできます。

インタフェース間でパケットを転送できるようにするには、FreeBSD をルータとして構成する必要があります。
インターネット標準および健全な設計慣行に従い、FreeBSD プロジェクトではこの機能を既定で無効にしていますが、`/etc/rc.conf` に次の行を追加することで起動時に有効化できます。

```
gateway_enable="YES"          # Set to YES if this host will be a gateway
```

再起動せずに今すぐルーティングを有効にするには、`sysctl(8)` 変数 `net.inet.ip.forwarding` を `1` に設定します。ルーティングを停止するには、この変数を `0` に戻します。

ルータのルーティングテーブルには、他のネットワークへ到達するための追加ルートが必要です。
ルートは静的ルートとして手動で追加することも、ルーティングプロトコルを使って自動的に学習させることもできます。
小規模なネットワークには静的ルートが適しており、この節では小規模ネットワーク向けに静的ルートエントリを追加する方法を説明します。

> **注記**: 大規模なネットワークでは、静的ルートはすぐにスケーラビリティの限界に達します。FreeBSD には標準の BSD ルーティングデーモンである `routed(8)` が付属しており、RIP（バージョン 1 および 2）と IRDP を提供します。BGP や OSPF ルーティングプロトコルへの対応は、`net/quagga` パッケージまたは port からインストールできます。

次のネットワーク構成を考えてみましょう。

![静的ルートのネットワーク構成図](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/advanced-networking/static-routes.png)

このシナリオでは、`RouterA` がインターネット全体へのルータとして機能する FreeBSD マシンです。
外部世界と接続できるように、デフォルトルートは `10.0.0.1` に設定されています。
`RouterB` はすでにデフォルトゲートウェイとして `192.168.1.1` を使うよう設定されています。

静的ルートを追加する前の `RouterA` のルーティングテーブルは次のようになっています。

```shell
% netstat -nr
Routing tables

Internet:
Destination        Gateway            Flags    Refs      Use  Netif  Expire
default            10.0.0.1           UGS         0    49378    xl0
127.0.0.1          127.0.0.1          UH          0        6    lo0
10.0.0.0/24        link#1             UC          0        0    xl0
192.168.1.0/24     link#2             UC          0        0    xl1
```

現在のルーティングテーブルでは、`RouterA` は `192.168.2.0/24` ネットワークへのルートを持っていません。
次のコマンドを実行すると、`192.168.1.2` をネクストホップとして `Internal Net 2` ネットワークを `RouterA` のルーティングテーブルに追加できます。

```shell
# route add -net 192.168.2.0/24 192.168.1.2
```

これで `RouterA` は `192.168.2.0/24` ネットワーク上の任意のホストへ到達できるようになりました。
ただし、このルート情報は FreeBSD システムを再起動すると保持されません。
静的ルートを永続化するには、`/etc/rc.conf` に追加します。

```
# Add Internal Net 2 as a persistent static route
static_routes="internalnet2"
route_internalnet2="-net 192.168.2.0/24 192.168.1.2"
```

設定変数 `static_routes` には、ルート名を表す文字列を空白区切りで並べます。
そして `route_internalnet2` 変数に、そのルート名に対応する静的ルートの内容を記述します。

`static_routes` に複数の文字列を指定すれば、複数の静的ルートを作成できます。
次の例は、`192.168.0.0/24` と `192.168.1.0/24` の両ネットワークに対する静的ルートを追加する設定です。

```
static_routes="net1 net2"
route_net1="-net 192.168.0.0/24 192.168.0.1"
route_net2="-net 192.168.1.0/24 192.168.1.1"
```

<a id="network-routing-troubleshooting"></a>
### トラブルシューティング（Troubleshooting）

ネットワークにアドレス空間が割り当てられると、サービスプロバイダはそのネットワーク宛てのすべてのトラフィックが拠点のリンクへ送られるよう、自社のルーティングテーブルを設定します。
では、外部のサイトはどのようにしてそのネットワークの ISP へパケットを送ればよいと知るのでしょうか。

割り当て済みのすべてのアドレス空間を追跡し、インターネットバックボーン（国内および世界各地へインターネットトラフィックを運ぶ基幹回線）への接続点を定義する仕組みが存在します。
各バックボーンマシンはマスターテーブル群のコピーを保持しており、特定のネットワーク宛てのトラフィックを特定のバックボーン事業者へ向け、そこからサービスプロバイダの連鎖をたどって該当ネットワークへ到達させます。

サイトへの接続点（すなわち内側への経路）が自社であることをバックボーン側の拠点へ広報（advertise）するのは、サービスプロバイダの役割です。
これは**ルート伝播（route propagation）**と呼ばれます。

ときおりルート伝播に問題が起き、一部のサイトへ接続できなくなることがあります。
ルーティングのどこで問題が起きているかを切り分けるうえで、おそらく最も役立つコマンドは `traceroute` です。
これは `ping` が失敗するときに有用です。

`traceroute` を使う際は、接続先となるリモートホストのアドレスを指定します。
出力には、到達を試みる経路上のゲートウェイホストが順に表示され、最終的に目的のホストへ到達するか、接続不能のため途中で終了します。
詳細は `traceroute(8)` を参照してください。

<a id="network-routing-multicast"></a>
### マルチキャストに関する考慮事項（Multicast Considerations）

FreeBSD は、マルチキャストアプリケーションとマルチキャストルーティングの両方をネイティブにサポートしています。
マルチキャストアプリケーションを FreeBSD 上で動かすだけなら、特別な設定は不要です。
一方、マルチキャストルーティングのサポートを有効にするには、次のオプションをカスタムカーネルに組み込んでコンパイルする必要があります。

```
options MROUTING
```

マルチキャストルーティングデーモン `mrouted` は、`net/mrouted` パッケージまたは port からインストールできます。
このデーモンは DVMRP マルチキャストルーティングプロトコルを実装しており、`/usr/local/etc/mrouted.conf` を編集してトンネルや DVMRP の設定を行います。
`mrouted` をインストールすると、`map-mbone` や `mrinfo` およびそれらの man ページもあわせてインストールされます。
設定例については、これらの man ページを参照してください。

> **注記**: 多くのマルチキャスト環境では、DVMRP はすでに PIM プロトコルへ置き換えられています。詳細は `pim(4)` を参照してください。

<a id="configtuning-virtual-hosts"></a>
## 仮想ホスト（Virtual Hosts）

FreeBSD の一般的な用途の 1 つに仮想サイトホスティング（virtual site hosting）があり、1 台のサーバをネットワーク上で複数のサーバに見せかけることができます。
これは、単一のインタフェースに複数のネットワークアドレスを割り当てることで実現します。

1 つのネットワークインタフェースには 1 つの「実（real）」アドレスがあり、それに加えて任意の数の「エイリアス（alias）」アドレスを持たせることができます。
通常、これらのエイリアスは次のように `/etc/rc.conf` にエイリアスエントリを記述して追加します。

```shell
# sysrc ifconfig_fxp0_alias0="inet xxx.xxx.xxx.xxx netmask xxx.xxx.xxx.xxx"
```

エイリアスエントリは `alias0`、`alias1` のように `alias0` から始まる連番で指定しなければなりません。
設定処理は、連番が途切れた最初の箇所で停止します。

エイリアスのネットマスクの計算は重要です。
あるインタフェースにおいて、そのネットワークのネットマスクを正しく表すアドレスが 1 つ存在する必要があります。
同じネットワーク内に属するそれ以外のアドレスは、すべてビットが `1` のネットマスク（`255.255.255.255` または `0xffffffff`）を指定しなければなりません。

たとえば、`fxp0` インタフェースがネットマスク `255.255.255.0` の `10.1.1.0` と、ネットマスク `255.255.255.240` の `202.0.75.16` という 2 つのネットワークに接続されている場合を考えます。
このシステムで `10.1.1.1` 〜 `10.1.1.5` および `202.0.75.17` 〜 `202.0.75.20` の範囲のアドレスを持たせたいとします。
それぞれのネットワーク範囲における最初のアドレスだけに本来のネットマスクを指定し、残りのすべて（`10.1.1.2` 〜 `10.1.1.5` および `202.0.75.18` 〜 `202.0.75.20`）にはネットマスク `255.255.255.255` を設定しなければなりません。

このシナリオに対してアダプタを正しく設定する `/etc/rc.conf` のエントリは次のとおりです。

```shell
# sysrc ifconfig_fxp0="inet 10.1.1.1 netmask 255.255.255.0"
# sysrc ifconfig_fxp0_alias0="inet 10.1.1.2 netmask 255.255.255.255"
# sysrc ifconfig_fxp0_alias1="inet 10.1.1.3 netmask 255.255.255.255"
# sysrc ifconfig_fxp0_alias2="inet 10.1.1.4 netmask 255.255.255.255"
# sysrc ifconfig_fxp0_alias3="inet 10.1.1.5 netmask 255.255.255.255"
# sysrc ifconfig_fxp0_alias4="inet 202.0.75.17 netmask 255.255.255.240"
# sysrc ifconfig_fxp0_alias5="inet 202.0.75.18 netmask 255.255.255.255"
# sysrc ifconfig_fxp0_alias6="inet 202.0.75.19 netmask 255.255.255.255"
# sysrc ifconfig_fxp0_alias7="inet 202.0.75.20 netmask 255.255.255.255"
```

これをより簡潔に記述する方法として、IP アドレス範囲を空白区切りのリストで指定する形式もあります。
この形式では、最初のアドレスに指定したサブネットマスクが割り当てられ、残りのアドレスにはサブネットマスク `255.255.255.255` が割り当てられます。

```shell
# sysrc ifconfig_fxp0_aliases="inet 10.1.1.1-5/24 inet 202.0.75.17-20/28"
```

<a id="network-advanced-wireless"></a>
## 無線ネットワークの高度な認証（Wireless Advanced Authentication）

FreeBSD は無線ネットワークへ接続するための複数の方式に対応しています。
この節では、無線ネットワークに対する高度な認証の設定方法を説明します。

無線ネットワークへの接続と基本的な認証については、Network 章の [Connection and Authentication to a Wireless Network](https://docs.freebsd.org/en/books/handbook/network/#wireless-authentication) を参照してください。

<a id="network-wireless-wpa-eap-tls"></a>
### EAP-TLS を用いた WPA（WPA with EAP-TLS）

WPA を利用する 2 つ目の方法は、802.1X バックエンド認証サーバと組み合わせる方式です。
この場合、セキュリティ強度の低い WPA Personal と区別して **WPA Enterprise** と呼ばれます。
WPA Enterprise における認証は、Extensible Authentication Protocol（EAP）に基づいています。

EAP 自体は暗号化方式を備えていません。
その代わり、EAP は暗号化されたトンネルの内部に埋め込まれてやり取りされます。
EAP の認証方式には多くの種類がありますが、最も一般的なのは EAP-TLS、EAP-TTLS、および EAP-PEAP です。

EAP with Transport Layer Security（EAP-TLS）は、[Wi-Fi Alliance](https://www.wi-fi.org/) によって最初に認定された EAP 方式であるため、広くサポートされている無線認証プロトコルです。
EAP-TLS を運用するには、すべてのマシンにインストールする認証局（CA）の証明書、認証サーバ用のサーバ証明書、そして各無線クライアント用のクライアント証明書の 3 種類の証明書が必要です。
この EAP 方式では、認証サーバと無線クライアントがそれぞれの証明書を提示して相互に認証し、それらの証明書が組織の CA によって署名されていることを検証します。

これまでと同様に、設定は `/etc/wpa_supplicant.conf` で行います。

```
network={
  ssid="freebsdap"
  proto=RSN
  key_mgmt=WPA-EAP
  eap=TLS
  identity="loader"
  ca_cert="/etc/certs/cacert.pem"
  client_cert="/etc/certs/clientcert.pem"
  private_key="/etc/certs/clientkey.pem"
  private_key_passwd="freebsdmallclient"
}
```

1. `ssid` はネットワーク名（SSID）を指定します。
2. `proto=RSN` は WPA2 とも呼ばれる RSN IEEE® 802.11i プロトコルを使用することを示します。
3. `key_mgmt` 行は使用する鍵管理プロトコルを指定します。この例では EAP 認証を用いる WPA です。
4. `eap` は接続に用いる EAP 方式を指定します。
5. `identity` には EAP 用の識別子文字列を指定します。
6. `ca_cert` は CA 証明書ファイルのパス名を指定します。このファイルはサーバ証明書の検証に必要です。
7. `client_cert` はクライアント証明書ファイルのパス名を指定します。この証明書はネットワーク上の各無線クライアントごとに固有です。
8. `private_key` はクライアント証明書の秘密鍵ファイルのパス名です。
9. `private_key_passwd` には秘密鍵のパスフレーズを指定します。

次に、`/etc/rc.conf` に次の行を追加します。

```
wlans_ath0="wlan0"
ifconfig_wlan0="WPA DHCP"
```

続いて、インタフェースを起動します。

```shell
# service netif start
Starting wpa_supplicant.
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 7
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 15
DHCPACK from 192.168.0.20
bound to 192.168.0.254 -- renewal in 300 seconds.
wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500
      ether 00:11:95:d5:43:62
      inet 192.168.0.254 netmask 0xffffff00 broadcast 192.168.0.255
      media: IEEE 802.11 Wireless Ethernet DS/11Mbps mode 11g
      status: associated
      ssid freebsdap channel 1 (2412 Mhz 11g) bssid 00:11:95:c3:0d:ac
      country US ecm authmode WPA2/802.11i privacy ON deftxkey UNDEF
      AES-CCM 3:128-bit txpower 21.5 bmiss 7 scanvalid 450 bgscan
      bgscanintvl 300 bgscanidle 250 roam:rssi 7 roam:rate 5 protmode CTS
      wme burst roaming MANUAL
```

`wpa_supplicant(8)` と `ifconfig(8)` を使って手動でインタフェースを起動することも可能です。

<a id="network-wireless-wpa-eap-ttls"></a>
### EAP-TTLS を用いた WPA（WPA with EAP-TTLS）

EAP-TLS では認証サーバとクライアントの双方に証明書が必要でしたが、EAP-TTLS ではクライアント証明書は任意です。
この方式は、訪問者がクライアント証明書を持っていなくても安全な SSL トンネルを構築する Web サーバの仕組みと似ています。
EAP-TTLS は暗号化された TLS トンネルを使って認証データを安全に転送します。

必要な設定は `/etc/wpa_supplicant.conf` に追加します。

```
network={
  ssid="freebsdap"
  proto=RSN
  key_mgmt=WPA-EAP
  eap=TTLS
  identity="test"
  password="test"
  ca_cert="/etc/certs/cacert.pem"
  phase2="auth=MD5"
}
```

1. `eap` は接続に用いる EAP 方式を指定します。
2. `identity` には、暗号化された TLS トンネル内での EAP 認証に使う識別子文字列を指定します。
3. `password` には EAP 認証のパスフレーズを指定します。
4. `ca_cert` は CA 証明書ファイルのパス名を指定します。このファイルはサーバ証明書の検証に必要です。
5. `phase2` は暗号化された TLS トンネル内で使われる認証方式を指定します。この例では MD5-Challenge を用いる EAP を使用しています。この「内側認証（inner authentication）」フェーズは、しばしば「phase2」と呼ばれます。

次に、`/etc/rc.conf` に次の行を追加します。

```
wlans_ath0="wlan0"
ifconfig_wlan0="WPA DHCP"
```

続いて、インタフェースを起動します。

```shell
# service netif start
Starting wpa_supplicant.
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 7
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 15
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 21
DHCPACK from 192.168.0.20
bound to 192.168.0.254 -- renewal in 300 seconds.
wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500
      ether 00:11:95:d5:43:62
      inet 192.168.0.254 netmask 0xffffff00 broadcast 192.168.0.255
      media: IEEE 802.11 Wireless Ethernet DS/11Mbps mode 11g
      status: associated
      ssid freebsdap channel 1 (2412 Mhz 11g) bssid 00:11:95:c3:0d:ac
      country US ecm authmode WPA2/802.11i privacy ON deftxkey UNDEF
      AES-CCM 3:128-bit txpower 21.5 bmiss 7 scanvalid 450 bgscan
      bgscanintvl 300 bgscanidle 250 roam:rssi 7 roam:rate 5 protmode CTS
      wme burst roaming MANUAL
```

<a id="network-wireless-wpa-eap-peap"></a>
### EAP-PEAP を用いた WPA（WPA with EAP-PEAP）

> **注記**: PEAPv0/EAP-MSCHAPv2 は最も一般的な PEAP 方式です。この章では、その方式を指して「PEAP」と呼びます。

Protected EAP（PEAP）は EAP-TTLS の代替として設計されており、EAP-TLS に次いで広く使われている EAP 標準です。
複数のオペレーティングシステムが混在するネットワークでは、EAP-TLS に次いで最も広くサポートされている標準となるはずです。

PEAP は、クライアントと認証サーバの間に暗号化された TLS トンネルを作成し、サーバ側証明書でクライアント側がサーバを認証したうえで後続の認証情報のやり取りを保護する点で、EAP-TTLS と似ています。
ただし PEAP 認証は、ユーザー名を平文で送信し、パスワードのみを暗号化された TLS トンネル内で送信する点が EAP-TTLS と異なります。
EAP-TTLS ではユーザー名とパスワードの両方に TLS トンネルを使用します。

EAP-PEAP 関連の設定を行うには、`/etc/wpa_supplicant.conf` に次の行を追加します。

```
network={
  ssid="freebsdap"
  proto=RSN
  key_mgmt=WPA-EAP
  eap=PEAP
  identity="test"
  password="test"
  ca_cert="/etc/certs/cacert.pem"
  phase1="peaplabel=0"
  phase2="auth=MSCHAPV2"
}
```

1. `eap` は接続に用いる EAP 方式を指定します。
2. `identity` には、暗号化された TLS トンネル内での EAP 認証に使う識別子文字列を指定します。
3. `password` には EAP 認証のパスフレーズを指定します。
4. `ca_cert` は CA 証明書ファイルのパス名を指定します。このファイルはサーバ証明書の検証に必要です。
5. `phase1` には認証の第 1 フェーズである TLS トンネル用のパラメータを指定します。使用する認証サーバに応じて、認証用の特定のラベルを指定してください。多くの場合、ラベルは `"client EAP encryption"` であり、これは `peaplabel=0` によって設定されます。詳細は `wpa_supplicant.conf(5)` を参照してください。
6. `phase2` は暗号化された TLS トンネル内で使用される認証プロトコルを指定します。PEAP の場合は `auth=MSCHAPV2` になります。

`/etc/rc.conf` に次の行を追加します。

```
wlans_ath0="wlan0"
ifconfig_wlan0="WPA DHCP"
```

その後、インタフェースを起動します。

```shell
# service netif start
Starting wpa_supplicant.
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 7
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 15
DHCPREQUEST on wlan0 to 255.255.255.255 port 67 interval 21
DHCPACK from 192.168.0.20
bound to 192.168.0.254 -- renewal in 300 seconds.
wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500
      ether 00:11:95:d5:43:62
      inet 192.168.0.254 netmask 0xffffff00 broadcast 192.168.0.255
      media: IEEE 802.11 Wireless Ethernet DS/11Mbps mode 11g
      status: associated
      ssid freebsdap channel 1 (2412 Mhz 11g) bssid 00:11:95:c3:0d:ac
      country US ecm authmode WPA2/802.11i privacy ON deftxkey UNDEF
      AES-CCM 3:128-bit txpower 21.5 bmiss 7 scanvalid 450 bgscan
      bgscanintvl 300 bgscanidle 250 roam:rssi 7 roam:rate 5 protmode CTS
      wme burst roaming MANUAL
```
