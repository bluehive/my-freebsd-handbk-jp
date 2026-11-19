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

<a id="wireless-ad-hoc-mode"></a>
## 無線アドホックモード（Wireless Ad-hoc Mode）

IBSS モード（アドホックモードとも呼ばれます）は、ピアツーピア（1 対 1）の接続向けに設計されています。
たとえば、マシン `A` と `B` の間でアドホックネットワークを確立するには、2 つの IP アドレスと 1 つの SSID を決めます。

マシン `A` 側で次のように設定します。

```shell
# ifconfig wlan0 create wlandev ath0 wlanmode adhoc
# ifconfig wlan0 inet 192.168.0.1 netmask 255.255.255.0 ssid freebsdap
# ifconfig wlan0
  wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
	  ether 00:11:95:c3:0d:ac
	  inet 192.168.0.1 netmask 0xffffff00 broadcast 192.168.0.255
	  media: IEEE 802.11 Wireless Ethernet autoselect mode 11g <adhoc>
	  status: running
	  ssid freebsdap channel 2 (2417 Mhz 11g) bssid 02:11:95:c3:0d:ac
	  country US ecm authmode OPEN privacy OFF txpower 21.5 scanvalid 60
	  protmode CTS wme burst
```

`adhoc` パラメータは、このインタフェースが IBSS モードで動作していることを示しています。

これでマシン `B` から `A` を検出できるはずです。

```shell
# ifconfig wlan0 create wlandev ath0 wlanmode adhoc
# ifconfig wlan0 up scan
  SSID/MESH ID    BSSID              CHAN RATE   S:N     INT CAPS
  freebsdap       02:11:95:c3:0d:ac    2   54M -64:-96  100 IS   WME
```

出力内の `I` は、`A` がアドホックモードで動作していることを示しています。
続いて、マシン `B` に別の IP アドレスを設定します。

```shell
# ifconfig wlan0 inet 192.168.0.2 netmask 255.255.255.0 ssid freebsdap
# ifconfig wlan0
  wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
	  ether 00:11:95:d5:43:62
	  inet 192.168.0.2 netmask 0xffffff00 broadcast 192.168.0.255
	  media: IEEE 802.11 Wireless Ethernet autoselect mode 11g <adhoc>
	  status: running
	  ssid freebsdap channel 2 (2417 Mhz 11g) bssid 02:11:95:c3:0d:ac
	  country US ecm authmode OPEN privacy OFF txpower 21.5 scanvalid 60
	  protmode CTS wme burst
```

これで `A` と `B` の双方が情報をやり取りできる状態になりました。

<a id="network-wireless-ap"></a>
### FreeBSD ホストアクセスポイント（FreeBSD Host Access Points）

FreeBSD はアクセスポイント（AP）として動作させることができるため、ハードウェア AP を別途購入したりアドホックネットワークを運用したりする必要がなくなります。
これは特に、FreeBSD マシンをインターネットなど別ネットワークへのゲートウェイとして動作させている場合に便利です。

<a id="network-wireless-ap-basic"></a>
#### 基本設定（Basic Settings）

FreeBSD マシンを AP として設定する前に、使用する無線カードおよびセキュリティプロトコルに対応した適切なネットワークサポートをカーネルに組み込んでおく必要があります。
詳細は [基本設定（Basic Settings）](#network-wireless-ap-basic) を参照してください。

> **注記**: Windows® ドライバ用の NDIS ドライバラッパーは現在 AP 動作に対応していません。AP モードに対応しているのは FreeBSD ネイティブの無線ドライバのみです。

無線ネットワークサポートを読み込んだら、その無線デバイスがホストベースアクセスポイントモード（hostap モードとも呼ばれます）に対応しているか確認します。

```shell
# ifconfig wlan0 create wlandev ath0
# ifconfig wlan0 list caps
drivercaps=6f85edc1<STA,FF,TURBOP,IBSS,HOSTAP,AHDEMO,TXPMGT,SHSLOT,SHPREAMBLE,MONITOR,MBSS,WPA1,WPA2,BURST,WME,WDS,BGSCAN,TXFRAG>
cryptocaps=1f<WEP,TKIP,AES,AES_CCM,TKIPMIC>
```

この出力にはカードの機能（capabilities）が表示されます。
`HOSTAP` という語があれば、この無線カードが AP として動作できることが確認できます。
また、WEP、TKIP、AES といった対応暗号方式も一覧表示されており、AP で使用できるセキュリティプロトコルを把握できます。

無線デバイスを hostap モードに設定できるのはネットワーク擬似デバイスの作成時のみであるため、すでに作成済みのデバイスがある場合は先に破棄する必要があります。

```shell
# ifconfig wlan0 destroy
```

その後、他のパラメータを設定する前に適切なオプションを付けて再作成します。

```shell
# ifconfig wlan0 create wlandev ath0 wlanmode hostap
# ifconfig wlan0 inet 192.168.0.1 netmask 255.255.255.0 ssid freebsdap mode 11g channel 1
```

`ifconfig(8)` を再度実行して `wlan0` インタフェースの状態を確認します。

```shell
# ifconfig wlan0
  wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
	  ether 00:11:95:c3:0d:ac
	  inet 192.168.0.1 netmask 0xffffff00 broadcast 192.168.0.255
	  media: IEEE 802.11 Wireless Ethernet autoselect mode 11g <hostap>
	  status: running
	  ssid freebsdap channel 1 (2412 Mhz 11g) bssid 00:11:95:c3:0d:ac
	  country US ecm authmode OPEN privacy OFF txpower 21.5 scanvalid 60
	  protmode CTS wme burst dtimperiod 1 -dfs
```

`hostap` パラメータは、インタフェースがホストベースアクセスポイントモードで動作していることを示しています。

起動時にこのインタフェース設定を自動的に行うには、`/etc/rc.conf` に次の行を追加します。

```
wlans_ath0="wlan0"
create_args_wlan0="wlanmode hostap"
ifconfig_wlan0="inet 192.168.0.1 netmask 255.255.255.0 ssid freebsdap mode 11g channel 1"
```

<a id="chapter-35-heading-16"></a>
#### 認証・暗号化なしのホストベースアクセスポイント（Host-based Access Point Without Authentication or Encryption）

認証や暗号化なしで AP を運用することは推奨されませんが、AP が正しく動作しているかを確かめる手軽な方法になります。
この構成は、クライアント側の問題をデバッグする際にも重要です。

AP の設定が終わったら、別の無線マシンからスキャンを実行して AP を検索します。

```shell
# ifconfig wlan0 create wlandev ath0
# ifconfig wlan0 up scan
SSID/MESH ID    BSSID              CHAN RATE   S:N     INT CAPS
freebsdap       00:11:95:c3:0d:ac    1   54M -66:-96  100 ES   WME
```

クライアントマシンが AP を検出したら、その AP へ接続（associate）できます。

```shell
# ifconfig wlan0 inet 192.168.0.2 netmask 255.255.255.0 ssid freebsdap
# ifconfig wlan0
  wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
	  ether 00:11:95:d5:43:62
	  inet 192.168.0.2 netmask 0xffffff00 broadcast 192.168.0.255
	  media: IEEE 802.11 Wireless Ethernet OFDM/54Mbps mode 11g
	  status: associated
	  ssid freebsdap channel 1 (2412 Mhz 11g) bssid 00:11:95:c3:0d:ac
	  country US ecm authmode OPEN privacy OFF txpower 21.5 bmiss 7
	  scanvalid 60 bgscan bgscanintvl 300 bgscanidle 250 roam:rssi 7
	  roam:rate 5 protmode CTS wme burst
```

<a id="network-wireless-ap-wpa"></a>
#### WPA2 ホストベースアクセスポイント（WPA2 Host-based Access Point）

この節では、WPA2 セキュリティプロトコルを用いて FreeBSD アクセスポイントを構築する方法を取り上げます。
WPA の詳細や WPA ベースの無線クライアントの設定については、[EAP-TLS を用いた WPA（WPA with EAP-TLS）](#network-wireless-wpa-eap-tls) を参照してください。

WPA2 を有効にした AP でのクライアント認証と鍵管理には、`hostapd(8)` デーモンを使用します。

以下の設定作業は、AP として動作する FreeBSD マシン上で行います。
AP が正しく動作することを確認したら、`/etc/rc.conf` に次の行を追加して起動時に `hostapd(8)` を自動起動できます。

```
hostapd_enable="YES"
```

`hostapd(8)` を設定する前に、まず [基本設定（Basic Settings）](#network-wireless-ap-basic) で紹介した基本設定を済ませておいてください。

<a id="chapter-35-heading-18"></a>
##### WPA2-PSK

WPA2-PSK は、バックエンド認証サーバを利用できない、あるいは利用する必要がない小規模ネットワーク向けの方式です。

設定は `/etc/hostapd.conf` で行います。

```
interface=wlan0
debug=1
ctrl_interface=/var/run/hostapd
ctrl_interface_group=wheel
ssid=freebsdap
wpa=2
wpa_passphrase=freebsdmall
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
```

1. アクセスポイントに使用する無線インタフェースです。
2. `hostapd(8)` 実行時の出力詳細度（verbosity）レベルです。値 `1` は最小限のレベルを表します。
3. `hostapd_cli(8)` などの外部プログラムと通信するためのドメインソケットファイルを `hostapd(8)` が格納するディレクトリのパス名です。この例では既定値を使用しています。
4. 制御インタフェースファイルへのアクセスを許可するグループです。
5. 無線スキャン時に表示される無線ネットワーク名（SSID）です。
6. WPA を有効化し、必須とする WPA 認証プロトコルを指定します。値 `2` は AP を WPA2 用に設定するもので、これが推奨されます。旧式の WPA が必要な場合にのみ `1` を指定してください。
7. WPA 認証用の ASCII パスフレーズです。
8. 使用する鍵管理プロトコルです。この例では WPA-PSK を設定しています。
9. アクセスポイントが受け入れる暗号化アルゴリズムです。この例では CCMP（AES）暗号のみを受け入れます。CCMP は TKIP の後継であり、可能な限り CCMP の使用が強く推奨されます。TKIP は CCMP に対応していない端末が存在する場合にのみ許可してください。

次の手順として、`hostapd(8)` を起動します。

```shell
# service hostapd forcestart
```

```shell
# ifconfig wlan0
wlan0: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500
	ether 04:f0:21:16:8e:10
	inet6 fe80::6f0:21ff:fe16:8e10%wlan0 prefixlen 64 scopeid 0x9
	nd6 options=21<PERFORMNUD,AUTO_LINKLOCAL>
	media: IEEE 802.11 Wireless Ethernet autoselect mode 11na <hostap>
	status: running
	ssid No5ignal channel 36 (5180 MHz 11a ht/40+) bssid 04:f0:21:16:8e:10
	country US ecm authmode WPA2/802.11i privacy MIXED deftxkey 2
	AES-CCM 2:128-bit AES-CCM 3:128-bit txpower 17 mcastrate 6 mgmtrate 6
	scanvalid 60 ampdulimit 64k ampdudensity 8 shortgi wme burst
	dtimperiod 1 -dfs
	groups: wlan
```

AP が稼働したら、クライアントはその AP へ接続できます。
詳細は [基本設定（Basic Settings）](#network-wireless-ap-basic) を参照してください。
AP に接続している端末の一覧は `ifconfig wlan0 list sta`（`wlan0` の部分は実際のインタフェース名に置き換えてください）で確認できます。

<a id="network-usb-tethering"></a>
## USB テザリング（USB Tethering）

多くの携帯電話には、USB 経由でデータ通信接続を共有する機能（一般に「テザリング」と呼ばれます）が備わっています。
この機能では、RNDIS、CDC、または Apple® iPhone®/iPad® 独自プロトコルのいずれかが使用されます。

* Android™ デバイスでは通常 `urndis(4)` ドライバを使用します。
* Apple® デバイスでは `ipheth(4)` ドライバを使用します。
* 古いデバイスでは `cdce(4)` ドライバがよく使われます。

デバイスを接続する前に、適切なドライバをカーネルへ読み込みます。

```shell
# kldload if_urndis
# kldload if_cdce
# kldload if_ipheth
```

デバイスを接続すると、`ue0` が通常のネットワークデバイスと同様に利用できるようになります。
デバイス側で「USB テザリング」オプションが有効になっていることを確認してください。

この変更を永続化して起動時にドライバをモジュールとして読み込むには、`/boot/loader.conf` に次の行のうち適切なものを記述します。

```shell
if_urndis_load="YES"
if_cdce_load="YES"
if_ipheth_load="YES"
```

<a id="network-bluetooth"></a>
## Bluetooth

Bluetooth は、2.4 GHz の免許不要帯域で動作し、通信範囲が約 10 メートルのパーソナルネットワークを構築するための無線技術です。
通常、携帯電話や携帯端末、ノートパソコンなどのポータブルデバイス間でアドホックにネットワークを形成します。
Wi-Fi 無線技術とは異なり、Bluetooth には FTP のようなファイルサーバ、ファイル送信（プッシュ）、音声伝送、シリアル回線エミュレーションといった上位のサービスプロファイルが用意されています。

この節では、FreeBSD システムで USB Bluetooth ドングルを使用する方法を説明し、続けて各種 Bluetooth プロトコルとユーティリティを紹介します。

<a id="chapter-35-heading-21"></a>
### Bluetooth サポートの読み込み（Loading Bluetooth Support）

FreeBSD の Bluetooth スタックは `netgraph(4)` フレームワークを用いて実装されています。
幅広い種類の Bluetooth USB ドングルが `ng_ubt(4)` でサポートされています。
Broadcom BCM2033 ベースの Bluetooth デバイスは `ubtbcmfw(4)` および `ng_ubt(4)` ドライバでサポートされています。
3Com Bluetooth PC Card 3CRWB60-A は `ng_bt3c(4)` ドライバでサポートされています。
シリアルおよび UART ベースの Bluetooth デバイスは `ng_h4(4)` および `hcseriald(8)` でサポートされています。

デバイスを接続する前に、上記のどのドライバを使用するかを特定し、そのドライバを読み込みます。
たとえば、`ng_ubt(4)` ドライバを使用するデバイスであれば次のようにします。

```shell
# kldload ng_ubt
```

システム起動時から Bluetooth デバイスを接続しておく場合は、`/boot/loader.conf` にドライバを追記することで起動時にモジュールを読み込めます。

```
ng_ubt_load="YES"
```

ドライバを読み込んだら、USB ドングルを差し込みます。
ドライバの読み込みに成功していれば、コンソールおよび `/var/log/messages` に次のような出力が表示されます。

```shell
ubt0: vendor 0x0a12 product 0x0001, rev 1.10/5.25, addr 2
ubt0: Interface 0 endpoints: interrupt=0x81, bulk-in=0x82, bulk-out=0x2
ubt0: Interface 1 (alt.config 5) endpoints: isoc-in=0x83, isoc-out=0x3,
      wMaxPacketSize=49, nframes=6, buffer size=294
```

Bluetooth スタックの起動と停止には起動スクリプトを使用します。デバイスを取り外す前にはスタックを停止しておくのが望ましいです。
Bluetooth スタックの起動には、`hcsecd(8)` の起動が必要になる場合があります。
スタックを起動すると、次のような出力が表示されます。

```shell
# service bluetooth start ubt0
BD_ADDR: 00:02:72:00:d4:1a
Features: 0xff 0xff 0xf 00 00 00 00 00
<3-Slot> <5-Slot> <Encryption> <Slot offset>
<Timing accuracy> <Switch> <Hold mode> <Sniff mode>
<Park mode> <RSSI> <Channel quality> <SCO link>
<HV2 packets> <HV3 packets> <u-law log> <A-law log> <CVSD>
<Paging scheme> <Power control> <Transparent SCO data>
Max. ACL packet size: 192 bytes
Number of ACL packets: 8
Max. SCO packet size: 64 bytes
Number of SCO packets: 8
```

<a id="chapter-35-heading-22"></a>
### 他の Bluetooth デバイスの検出（Finding Other Bluetooth Devices）

Host Controller Interface（HCI）は、Bluetooth ベースバンド機能へアクセスするための統一的な手段を提供します。
FreeBSD では、各 Bluetooth デバイスに対して netgraph HCI ノードが作成されます。
詳細は `ng_hci(4)` を参照してください。

最も一般的な作業の 1 つは、電波の届く範囲内にある Bluetooth デバイスの検出です。
この操作は **照会（inquiry）** と呼ばれます。
inquiry やその他の HCI 関連操作は `hccontrol(8)` を使って行います。
以下の例は、通信範囲内にある Bluetooth デバイスを探す方法を示しています。
数秒以内にデバイスの一覧が表示されるはずです。
なお、リモートデバイスは**検出可能（discoverable）**モードに設定されている場合にのみ inquiry に応答します。

```shell
% hccontrol -n ubt0hci inquiry
Inquiry result, num_responses=1
Inquiry result #0
       BD_ADDR: 00:80:37:29:19:a4
       Page Scan Rep. Mode: 0x1
       Page Scan Period Mode: 00
       Page Scan Mode: 00
       Class: 52:02:04
       Clock offset: 0x78ef
Inquiry complete. Status: No error [00]
```

`BD_ADDR` はネットワークカードの MAC アドレスに似た、Bluetooth デバイス固有のアドレスです。
このアドレスはデバイスとの今後の通信に必要であり、`BD_ADDR` に対して人間が読みやすい名前を割り当てることもできます。
既知の Bluetooth ホストに関する情報は `/etc/bluetooth/hosts` に記述されます。
次の例は、リモートデバイスに割り当てられている人間が読みやすい名前を取得する方法を示しています。

```shell
% hccontrol -n ubt0hci remote_name_request 00:80:37:29:19:a4
BD_ADDR: 00:80:37:29:19:a4
Name: Pav's T39
```

リモート側の Bluetooth デバイスから inquiry を実行すると、このコンピュータは `"your.host.name (ubt0)"` として検出されます。
ローカルデバイスに割り当てられた名前はいつでも変更できます。

リモートデバイスには `/etc/bluetooth/hosts` でエイリアスを割り当てることができます。
`/etc/bluetooth/hosts` ファイルの詳細は `bluetooth.hosts(5)` を参照してください。

Bluetooth システムは、2 台の Bluetooth 機器間のポイントツーポイント接続、または複数の Bluetooth デバイス間で共有されるポイントツーマルチポイント接続を提供します。
次の例は、リモートデバイスへの接続を作成する方法を示しています。

```shell
% hccontrol -n ubt0hci create_connection BT_ADDR
```

`create_connection` は `BT_ADDR` に加えて `/etc/bluetooth/hosts` に定義されたホストエイリアスも受け付けます。

次の例は、ローカルデバイスのアクティブなベースバンド接続の一覧を取得する方法を示しています。

```shell
% hccontrol -n ubt0hci read_connection_list
Remote BD_ADDR    Handle Type Mode Role Encrypt Pending Queue State
00:80:37:29:19:a4     41  ACL    0 MAST    NONE       0     0 OPEN
```

**接続ハンドル（connection handle）**はベースバンド接続を切断する必要があるときに使いますが、通常は手動で切断する必要はありません。
スタックが非アクティブなベースバンド接続を自動的に終了します。

```shell
# hccontrol -n ubt0hci disconnect 41
Connection handle: 41
Reason: Connection terminated by local host [0x16]
```

利用可能な HCI コマンドの完全な一覧を表示するには `hccontrol help` を実行してください。
ほとんどの HCI コマンドはスーパーユーザー権限を必要としません。

<a id="chapter-35-heading-23"></a>
### デバイスのペアリング（Device Pairing）

既定では、Bluetooth 通信は認証されておらず、どのデバイスも他のどのデバイスとも通信できます。
携帯電話などの Bluetooth デバイスは、特定のサービスを提供する際に認証を要求する場合があります。
Bluetooth 認証は通常、最大 16 文字の ASCII 文字列である **PIN コード**を使って行われます。
ユーザーは双方のデバイスに同じ PIN コードを入力する必要があります。
ユーザーが PIN コードを入力すると、双方のデバイスが**リンクキー（link key）**を生成します。
その後、リンクキーはデバイス内または永続ストレージに保存されます。
次回からは、双方のデバイスが前回生成したリンクキーを使用します。
この手順を**ペアリング（pairing）**と呼びます。
どちらかのデバイスでリンクキーが失われた場合は、ペアリングをやり直す必要がある点に注意してください。

Bluetooth の認証要求を処理するのは `hcsecd(8)` デーモンです。
既定の設定ファイルは `/etc/bluetooth/hcsecd.conf` です。
PIN コードを `1234` に設定した携帯電話向けのセクション例を次に示します。

```
device {
        bdaddr  00:80:37:29:19:a4;
        name    "Pav's T39";
        key     nokey;
        pin     "1234";
      }
```

PIN コードの唯一の制限は長さです。
Bluetooth ヘッドセットなどの一部のデバイスには、固定の PIN コードが内蔵されている場合があります。
`-d` スイッチを付けると `hcsecd(8)` がフォアグラウンドに留まるため、何が起きているかを簡単に確認できます。
リモートデバイスをペアリング待機状態に設定し、リモートデバイスへの Bluetooth 接続を開始してください。
リモートデバイス側でペアリングが受け入れられたことが表示され、PIN コードの入力が求められます。
`hcsecd.conf` に記述したのと同じ PIN コードを入力します。
これでコンピュータとリモートデバイスのペアリングが完了しました。
あるいは、リモートデバイス側からペアリングを開始することもできます。

システム起動時に `hcsecd(8)` を自動起動するよう設定するには、`/etc/rc.conf` に次の行を追加します。

```
hcsecd_enable="YES"
```

以下は `hcsecd(8)` デーモンの出力例です。

```
hcsecd[16484]: Got Link_Key_Request event from 'ubt0hci', remote bdaddr 0:80:37:29:19:a4
hcsecd[16484]: Found matching entry, remote bdaddr 0:80:37:29:19:a4, name 'Pav's T39', link key doesn't exist
hcsecd[16484]: Sending Link_Key_Negative_Reply to 'ubt0hci' for remote bdaddr 0:80:37:29:19:a4
hcsecd[16484]: Got PIN_Code_Request event from 'ubt0hci', remote bdaddr 0:80:37:29:19:a4
hcsecd[16484]: Found matching entry, remote bdaddr 0:80:37:29:19:a4, name 'Pav's T39', PIN code exists
hcsecd[16484]: Sending PIN_Code_Reply to 'ubt0hci' for remote bdaddr 0:80:37:29:19:a4
```

<a id="chapter-35-heading-24"></a>
### PPP プロファイルによるネットワークアクセス（Network Access with PPP Profiles）

Dial-Up Networking（DUN）プロファイルを使うと、携帯電話を無線モデムとして設定し、ダイヤルアップインターネットアクセスサーバへ接続できます。
また、コンピュータ側が携帯電話からのデータ着信を受け付けるように設定することもできます。

PPP プロファイルによるネットワークアクセスは、単一または複数の Bluetooth デバイスへ LAN アクセスを提供するために利用できます。
さらに、シリアルケーブルエミュレーション上の PPP ネットワークを用いて PC 間接続を提供することも可能です。

FreeBSD では、これらのプロファイルは `ppp(8)` と、Bluetooth 接続を PPP が利用できる形式へ変換するラッパー `rfcomm_pppd(8)` によって実装されています。
プロファイルを使用する前に、`/etc/ppp/ppp.conf` に新しい PPP ラベルを作成しておく必要があります。
設定例については `rfcomm_pppd(8)` を参照してください。

次の例では、`rfcomm_pppd(8)` を使って `BD_ADDR` が `00:80:37:29:19:a4` のリモートデバイスに対し、DUN RFCOMM チャネル上で接続を開きます。

```shell
# rfcomm_pppd -a 00:80:37:29:19:a4 -c -C dun -l rfcomm-dialup
```

実際のチャネル番号は、SDP プロトコルを使ってリモートデバイスから取得されます。
RFCOMM チャネルを手動で指定することもでき、その場合は `rfcomm_pppd(8)` による SDP 問い合わせは行われません。
リモートデバイス上の RFCOMM チャネルを調べるには `sdpcontrol(8)` を使用します。

PPP LAN サービスでネットワークアクセスを提供するには、`sdpd(8)` が起動していることと、LAN クライアント用の新しいエントリを `/etc/ppp/ppp.conf` に作成しておくことが必要です。
設定例については `rfcomm_pppd(8)` を参照してください。
最後に、有効な RFCOMM チャネル番号で RFCOMM PPP サーバを起動します。
RFCOMM PPP サーバは、ローカルの SDP デーモンへ Bluetooth LAN サービスを自動的に登録します。
以下の例は RFCOMM PPP サーバを起動する方法を示しています。

```shell
# rfcomm_pppd -s -C 7 -l rfcomm-server
```

<a id="chapter-35-heading-25"></a>
### Bluetooth プロトコル（Bluetooth Protocols）

この節では、各種 Bluetooth プロトコルとその機能、および関連するユーティリティの概要を説明します。

<a id="chapter-35-heading-26"></a>
#### Logical Link Control and Adaptation Protocol（L2CAP）

Logical Link Control and Adaptation Protocol（L2CAP）は、上位層プロトコルに対してコネクション型およびコネクションレス型のデータサービスを提供します。
L2CAP により、上位プロトコルやアプリケーションは最大 64 キロバイト長の L2CAP データパケットを送受信できます。

L2CAP は**チャネル（channel）**の概念に基づいています。
チャネルとはベースバンド接続上の論理的な接続であり、各チャネルは多対 1 の関係で単一のプロトコルに結び付けられます。
複数のチャネルを同じプロトコルに結び付けることはできますが、1 つのチャネルを複数のプロトコルに結び付けることはできません。
あるチャネルで受信された各 L2CAP パケットは、対応する上位プロトコルへ渡されます。
複数のチャネルで同じベースバンド接続を共有することも可能です。

FreeBSD では、Bluetooth デバイスごとに netgraph L2CAP ノードが作成されます。
このノードは通常、下流の Bluetooth HCI ノードと上流の Bluetooth ソケットノードに接続されます。
L2CAP ノードの既定の名前は `"devicel2cap"` です。
詳細は `ng_l2cap(4)` を参照してください。

便利なコマンドとして、他のデバイスへ ping を送れる `l2ping(8)` があります。
一部の Bluetooth 実装では送信したデータをすべて返さないことがあるため、次の例で `0 bytes` と表示されるのは正常です。

```shell
# l2ping -a 00:80:37:29:19:a4
0 bytes from 0:80:37:29:19:a4 seq_no=0 time=48.633 ms result=0
0 bytes from 0:80:37:29:19:a4 seq_no=1 time=37.551 ms result=0
0 bytes from 0:80:37:29:19:a4 seq_no=2 time=28.324 ms result=0
0 bytes from 0:80:37:29:19:a4 seq_no=3 time=46.150 ms result=0
```

`l2control(8)` ユーティリティは、L2CAP ノードに対するさまざまな操作を実行するために使用します。
次の例は、ローカルデバイスの論理接続（チャネル）一覧とベースバンド接続一覧を取得する方法を示しています。

```shell
% l2control -a 00:02:72:00:d4:1a read_channel_list
L2CAP channels:
Remote BD_ADDR     SCID/ DCID   PSM  IMTU/ OMTU State
00:07:e0:00:0b:ca    66/   64     3   132/  672 OPEN
% l2control -a 00:02:72:00:d4:1a read_connection_list
L2CAP connections:
Remote BD_ADDR    Handle Flags Pending State
00:07:e0:00:0b:ca     41 O           0 OPEN
```

もう 1 つの診断ツールが `btsockstat(1)` です。
これは `netstat(1)` に似ていますが、Bluetooth ネットワーク関連のデータ構造を対象としています。
以下の例では、上の `l2control(8)` と同じ論理接続が表示されています。

```shell
% btsockstat
Active L2CAP sockets
PCB      Recv-Q Send-Q Local address/PSM       Foreign address   CID   State
c2afe900      0      0 00:02:72:00:d4:1a/3     00:07:e0:00:0b:ca 66    OPEN
Active RFCOMM sessions
L2PCB    PCB      Flag MTU   Out-Q DLCs State
c2afe900 c2b53380 1    127   0     Yes  OPEN
Active RFCOMM sockets
PCB      Recv-Q Send-Q Local address     Foreign address   Chan DLCI State
c2e8bc80      0    250 00:02:72:00:d4:1a 00:07:e0:00:0b:ca 3    6    OPEN
```

<a id="chapter-35-heading-27"></a>
#### Radio Frequency Communication（RFCOMM）

RFCOMM プロトコルは、L2CAP プロトコル上でシリアルポートのエミュレーションを提供します。
RFCOMM はシンプルなトランスポートプロトコルであり、RS-232（EIA/TIA-232-E）シリアルポートの 9 本の回路をエミュレートするための仕組みを備えています。
2 台の Bluetooth デバイス間で最大 60 個の同時接続（RFCOMM チャネル）をサポートします。

RFCOMM における完全な通信経路は、通信の両端で動作する 2 つのアプリケーションと、その間を結ぶ通信セグメントで構成されます。
RFCOMM は、各アプリケーションが動作しているデバイス上のシリアルポートを利用するようなアプリケーションを想定しています。
通信セグメントは、あるデバイスから別のデバイスへの直接接続 Bluetooth リンクです。

RFCOMM が関与するのは、直接接続の場合はデバイス間の接続のみ、ネットワーク接続の場合はデバイスとモデム間の接続のみです。
RFCOMM は、片側で Bluetooth 無線技術を介して通信し、もう片側で有線インタフェースを提供するモジュールなど、他の構成もサポートできます。

FreeBSD では、RFCOMM は Bluetooth ソケット層で実装されています。

<a id="chapter-35-heading-28"></a>
#### Service Discovery Protocol（SDP）

Service Discovery Protocol（SDP）は、クライアントアプリケーションがサーバアプリケーションの提供するサービスの存在や、そのサービスの属性を検出するための手段を提供します。
サービスの属性には、提供されるサービスの種類やクラス、およびそのサービスを利用するために必要な機構やプロトコル情報が含まれます。

SDP では、SDP サーバと SDP クライアントの間で通信が行われます。
サーバは、自身に関連付けられたサービスの特性を記述したサービスレコードの一覧を保持します。
各サービスレコードには、単一のサービスに関する情報が含まれます。
クライアントは SDP リクエストを発行することで、SDP サーバが保持するサービスレコードから情報を取得できます。
クライアントまたはそれに関連するアプリケーションがサービスの利用を決定した場合、実際にサービスを使うためにはサービス提供元に対して別の接続を開く必要があります。
SDP はサービスとその属性を発見するための仕組みを提供しますが、それらのサービス自体を利用する仕組みは提供しません。

通常、SDP クライアントはサービスの望ましい特性を指定して検索を行います。
しかし、サービスに関する事前情報なしに、SDP サーバのサービスレコードにどのような種類のサービスが記述されているかを知りたい場合もあります。
提供されているサービスを総当たりで探すこの処理は、**ブラウジング（browsing）**と呼ばれます。

Bluetooth SDP サーバの `sdpd(8)` とコマンドラインクライアントの `sdpcontrol(8)` は、FreeBSD の標準インストールに含まれています。
次の例は、SDP ブラウズ問い合わせを実行する方法を示しています。

```shell
% sdpcontrol -a 00:01:03:fc:6e:ec browse
Record Handle: 00000000
Service Class ID List:
        Service Discovery Server (0x1000)
Protocol Descriptor List:
        L2CAP (0x0100)
                Protocol specific parameter #1: u/int/uuid16 1
                Protocol specific parameter #2: u/int/uuid16 1

Record Handle: 0x00000001
Service Class ID List:
        Browse Group Descriptor (0x1001)

Record Handle: 0x00000002
Service Class ID List:
        LAN Access Using PPP (0x1102)
Protocol Descriptor List:
        L2CAP (0x0100)
        RFCOMM (0x0003)
                Protocol specific parameter #1: u/int8/bool 1
Bluetooth Profile Descriptor List:
        LAN Access Using PPP (0x1102) ver. 1.0
```

各サービスには、RFCOMM チャネルなどの属性リストが含まれている点に注意してください。
サービスによっては、これらの属性の一部を控えておく必要があります。
一部の Bluetooth 実装はサービスブラウジングに対応しておらず、空の一覧を返すことがあります。
その場合は、特定のサービスを指定して検索することが可能です。
以下の例は、OBEX Object Push（OPUSH）サービスを検索する方法を示しています。

```shell
% sdpcontrol -a 00:01:03:fc:6e:ec search OPUSH
```

FreeBSD 上で Bluetooth クライアントに対してサービスを提供するには、`sdpd(8)` サーバを使用します。
`/etc/rc.conf` に次の行を追加できます。

```
sdpd_enable="YES"
```

その後、次のコマンドで `sdpd(8)` デーモンを起動できます。

```shell
# service sdpd start
```

リモートクライアントへ Bluetooth サービスを提供したいローカルサーバアプリケーションは、ローカルの SDP デーモンにそのサービスを登録します。
そのようなアプリケーションの一例が `rfcomm_pppd(8)` です。
起動すると、ローカルの SDP デーモンに Bluetooth LAN サービスを自動的に登録します。

ローカルの SDP サーバに登録されているサービスの一覧は、ローカル制御チャネル経由で SDP ブラウズ問い合わせを発行することで取得できます。

```shell
# sdpcontrol -l browse
```

<a id="chapter-35-heading-29"></a>
#### OBEX Object Push（OPUSH）

Object Exchange（OBEX）は、モバイルデバイス間で簡単なファイル転送を行うために広く使われているプロトコルです。
主な用途は赤外線通信であり、ノート PC や PDA 間での一般的なファイル転送や、携帯電話と Personal Information Manager（PIM）アプリケーションを備えた他のデバイス間での名刺・予定表エントリの送信に使われます。

OBEX サーバおよびクライアントは `obexapp` によって実装されており、`comms/obexapp` パッケージまたは port からインストールできます。

OBEX クライアントは、OBEX サーバへオブジェクトを送信（push）したり、サーバから取得（pull）したりするために使用します。
オブジェクトの例としては、名刺や予定などがあります。
OBEX クライアントは SDP 経由でリモートデバイスから RFCOMM チャネル番号を取得できます。
これは、RFCOMM チャネル番号の代わりにサービス名を指定することで行えます。
サポートされているサービス名は `IrMC`、`FTRN`、`OPUSH` です。
RFCOMM チャネルを数値として直接指定することもできます。
以下は、携帯電話からデバイス情報オブジェクトを取得（pull）し、新しいオブジェクトである名刺を電話のディレクトリへ送信（push）する OBEX セッションの例です。

```shell
% obexapp -a 00:80:37:29:19:a4 -C IrMC
obex> get telecom/devinfo.txt devinfo-t39.txt
Success, response: OK, Success (0x20)
obex> put new.vcf
Success, response: OK, Success (0x20)
obex> di
Success, response: OK, Success (0x20)
```

OPUSH サービスを提供するには、`sdpd(8)` が起動していることと、受信したすべてのオブジェクトを格納するルートフォルダを作成しておくことが必要です。
ルートフォルダの既定パスは `/var/spool/obex` です。
最後に、有効な RFCOMM チャネル番号で OBEX サーバを起動します。
OBEX サーバはローカルの SDP デーモンに OPUSH サービスを自動的に登録します。
以下の例は OBEX サーバを起動する方法を示しています。

```shell
# obexapp -s -C 10
```

<a id="chapter-35-heading-30"></a>
#### Serial Port Profile（SPP）

Serial Port Profile（SPP）を使用すると、Bluetooth デバイスでシリアルケーブルエミュレーションを実行できます。
このプロファイルにより、仮想シリアルポートの抽象化を通じて、従来のアプリケーションがケーブルの代わりに Bluetooth を利用できるようになります。

FreeBSD では `rfcomm_sppd(1)` が SPP を実装しており、仮想シリアルポートの抽象化として擬似端末（pseudo tty）が使用されます。
以下の例は、リモートデバイスのシリアルポートサービスへ接続する方法を示しています。
`rfcomm_sppd(1)` は SDP 経由でリモートデバイスから RFCOMM チャネルを取得できるため、必ずしもチャネルを指定する必要はありません。
これを上書きしたい場合は、コマンドラインで RFCOMM チャネルを指定してください。

```shell
# rfcomm_sppd -a 00:07:E0:00:0B:CA -t
rfcomm_sppd[94692]: Starting on /dev/pts/6...
/dev/pts/6
```

接続できたら、その擬似端末をシリアルポートとして使用できます。

```shell
# cu -l /dev/pts/6
```

擬似端末のパスは標準出力に出力されるため、ラッパースクリプトから読み取って利用することもできます。

```
PTS=`rfcomm_sppd -a 00:07:E0:00:0B:CA -t`
cu -l $PTS
```

<a id="chapter-35-heading-31"></a>
### トラブルシューティング（Troubleshooting）

既定では、FreeBSD は新しい接続を受け入れる際にロールスイッチ（role switch）を試みてマスター（master）になろうとします。
ロールスイッチに対応していない一部の古い Bluetooth デバイスでは、接続できなくなることがあります。
ロールスイッチは新しい接続が確立される際に行われるため、リモートデバイスがロールスイッチに対応しているかどうかを事前に問い合わせることはできません。
ただし、ローカル側でロールスイッチを無効化する HCI オプションが用意されています。

```shell
# hccontrol -n ubt0hci write_node_role_switch 0
```

Bluetooth パケットを表示するには、`comms/hcidump` パッケージまたは port からインストールできるサードパーティ製パッケージ `hcidump` を使用します。
このユーティリティは `tcpdump(1)` に似ており、Bluetooth パケットの内容を端末に表示したり、ファイルへダンプしたりするために使用できます。

<a id="network-bridging"></a>
## ブリッジ（Bridging）

IP サブネットを分けてルータで相互接続することなく、イーサネットセグメントなどのネットワークを複数のセグメントへ分割すると便利な場合があります。
このように 2 つのネットワークを相互に接続する装置を「ブリッジ（bridge）」と呼びます。

ブリッジは、各ネットワークインタフェースに接続されたデバイスの MAC アドレスを学習することで動作します。
送信元と宛先の MAC アドレスが異なるネットワーク側に存在する場合にのみ、ネットワーク間でトラフィックを転送します。
多くの点で、ブリッジはポート数の非常に少ないイーサネットスイッチのようなものです。
複数のネットワークインタフェースを備えた FreeBSD システムは、ブリッジとして動作するように構成できます。

ブリッジは次のような場面で役立ちます。

* **ネットワークの接続**: ブリッジの基本的な役割は、2 つ以上のネットワークセグメントを結合することです。配線の制約やファイアウォール設置など、専用ネットワーク機器の代わりにホストベースのブリッジを使う理由はさまざまです。また、hostap モードで動作する無線インタフェースと有線ネットワークをブリッジで接続し、アクセスポイントとして動作させることもできます。
* **フィルタリング／トラフィックシェーピング機能付きファイアウォール**: ルーティングやネットワークアドレス変換（NAT）を行わずにファイアウォール機能が必要な場合にブリッジを利用できます。
  たとえば、DSL や ISDN で ISP に接続している小規模企業を考えます。ISP から 13 個のグローバル IP アドレスが割り当てられており、ネットワーク上には 10 台のコンピュータがあるとします。このような状況では、サブネット分割の問題からルータ型のファイアウォールを使うのは困難です。ブリッジ型のファイアウォールであれば、IP アドレッシングの問題を起こさずに構成できます。
* **ネットワークタップ（Network Tap）**: ブリッジで 2 つのネットワークセグメントを接続し、ブリッジインタフェース上で `bpf(4)` と `tcpdump(1)` を用いて通過するすべてのイーサネットフレームを検査したり、スパンポート（span port）と呼ばれる追加のインタフェースへ全フレームのコピーを送出したりできます。
* **レイヤ 2 VPN**: 2 つのイーサネットネットワークを EtherIP トンネルや OpenVPN などの `tap(4)` ベースのソリューションへブリッジすることで、IP リンク越しに結合できます。
* **レイヤ 2 冗長化**: 複数のリンクでネットワークを接続し、Spanning Tree Protocol（STP）を用いて冗長経路をブロックできます。

この節では、`if_bridge(4)` を使用して FreeBSD システムをブリッジとして設定する方法を説明します。
netgraph ベースのブリッジドライバも用意されており、`ng_bridge(4)` で解説されています。

> **注記**: パケットフィルタリングは、`pfil(9)` フレームワークにフックする任意のファイアウォールパッケージと組み合わせて使用できます。また、`altq(4)` や `dummynet(4)` と組み合わせることで、ブリッジをトラフィックシェーパとして利用することもできます。

<a id="chapter-35-heading-33"></a>
### ブリッジの有効化（Enabling the Bridge）

FreeBSD では、`if_bridge(4)` はカーネルモジュールとして提供されており、`ifconfig(8)` でブリッジインタフェースを作成する際に自動的に読み込まれます。
カスタムカーネル設定ファイルに `device if_bridge` を追加して、ブリッジサポートをカスタムカーネルに組み込むこともできます。

ブリッジはインタフェースのクローニング（cloning）によって作成します。
ブリッジインタフェースを作成するには次のように実行します。

```shell
# ifconfig bridge create
bridge0
# ifconfig bridge0
bridge0: flags=8802<BROADCAST,SIMPLEX,MULTICAST> metric 0 mtu 1500
        ether 96:3d:4b:f1:79:7a
        id 00:00:00:00:00:00 priority 32768 hellotime 2 fwddelay 15
        maxage 20 holdcnt 6 proto rstp maxaddr 100 timeout 1200
        root id 00:00:00:00:00:00 priority 0 ifcost 0 port 0
```

ブリッジインタフェースを作成すると、ランダムに生成されたイーサネットアドレスが自動的に割り当てられます。
`maxaddr` と `timeout` パラメータは、ブリッジが転送テーブルに保持する MAC アドレスの最大数と、最後に観測されてから各エントリが削除されるまでの秒数を制御します。
その他のパラメータは STP の動作を制御します。

次に、ブリッジのメンバーとして追加するネットワークインタフェースを指定します。
ブリッジがパケットを転送するには、すべてのメンバーインタフェースとブリッジ自体が有効（up）になっている必要があります。

```shell
# ifconfig bridge0 addm fxp0 addm fxp1 up
# ifconfig fxp0 up
# ifconfig fxp1 up
```

これでブリッジは `fxp0` と `fxp1` の間でイーサネットフレームを転送できるようになりました。
起動時にブリッジが自動作成されるようにするには、`/etc/rc.conf` に次の行を追加します。

```
cloned_interfaces="bridge0"
ifconfig_bridge0="addm fxp0 addm fxp1 up"
ifconfig_fxp0="up"
ifconfig_fxp1="up"
```

ブリッジホスト自身に IP アドレスが必要な場合は、メンバーインタフェースではなくブリッジインタフェースに設定します。
アドレスは静的にも DHCP 経由でも設定できます。
次の例では静的な IP アドレスを設定しています。

```shell
# ifconfig bridge0 inet 192.168.0.1/24
```

ブリッジインタフェースに IPv6 アドレスを割り当てることも可能です。

設定を永続化するには、アドレス情報を `/etc/rc.conf` に追記します。

次の例では動的な IPv6 アドレスを使用しています。

```
ifconfig_bridge0_ipv6="inet6 auto_linklocal accept_rtadv"
```

> **注記**: パケットフィルタリングが有効になっている場合、ブリッジを通過するパケットは、着信元のメンバーインタフェース上のインバウンド、ブリッジインタフェース上、および適切なインタフェース上のアウトバウンドでそれぞれフィルタを通過します。どの段階も無効化することができます。パケットの流れる方向が重要になる場合は、ブリッジ自体ではなくメンバーインタフェース上でファイアウォールを適用するのが最善です。
>
> ブリッジには、非 IP パケットおよび IP パケットの通過や、`ipfw(8)` を用いたレイヤ 2 ファイアウォールに関する設定項目がいくつか用意されています。詳細は `if_bridge(4)` を参照してください。

<a id="chapter-35-heading-34"></a>
### スパニングツリーの有効化（Enabling Spanning Tree）

イーサネットネットワークが正常に機能するには、2 つのデバイス間に存在するアクティブな経路は 1 つだけでなければなりません。
STP プロトコルはループを検出し、冗長なリンクをブロック（blocked）状態にします。
アクティブなリンクのいずれかに障害が発生すると、STP は別のツリーを計算し、ブロックしていた経路の 1 つを有効化してネットワーク上のすべての地点への接続性を復旧させます。

Rapid Spanning Tree Protocol（RSTP、または 802.1w）は、従来の STP との後方互換性を備えています。
RSTP は収束がより高速であり、隣接スイッチと情報を交換することで、ループを発生させずに素早く転送（forwarding）モードへ移行します。
FreeBSD は動作モードとして RSTP と STP の両方をサポートしており、既定のモードは RSTP です。

STP は `ifconfig(8)` を使ってメンバーインタフェース上で有効にできます。
現在のインタフェースが `fxp0` と `fxp1` であるブリッジで STP を有効にするには、次のように実行します。

```shell
# ifconfig bridge0 stp fxp0 stp fxp1
bridge0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        ether d6:cf:d5:a0:94:6d
        id 00:01:02:4b:d4:50 priority 32768 hellotime 2 fwddelay 15
        maxage 20 holdcnt 6 proto rstp maxaddr 100 timeout 1200
        root id 00:01:02:4b:d4:50 priority 32768 ifcost 0 port 0
        member: fxp0 flags=1c7<LEARNING,DISCOVER,STP,AUTOEDGE,PTP,AUTOPTP>
                port 3 priority 128 path cost 200000 proto rstp
                role designated state forwarding
        member: fxp1 flags=1c7<LEARNING,DISCOVER,STP,AUTOEDGE,PTP,AUTOPTP>
                port 4 priority 128 path cost 200000 proto rstp
                role designated state forwarding
```

このブリッジのスパニングツリー ID は `00:01:02:4b:d4:50`、プライオリティは `32768` です。
`root id` が同じ値になっていることから、このブリッジがこのツリーのルートブリッジであることが分かります。

ネットワーク上の別のブリッジでも STP が有効になっています。

```shell
bridge0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        ether 96:3d:4b:f1:79:7a
        id 00:13:d4:9a:06:7a priority 32768 hellotime 2 fwddelay 15
        maxage 20 holdcnt 6 proto rstp maxaddr 100 timeout 1200
        root id 00:01:02:4b:d4:50 priority 32768 ifcost 400000 port 4
        member: fxp0 flags=1c7<LEARNING,DISCOVER,STP,AUTOEDGE,PTP,AUTOPTP>
                port 4 priority 128 path cost 200000 proto rstp
                role root state forwarding
        member: fxp1 flags=1c7<LEARNING,DISCOVER,STP,AUTOEDGE,PTP,AUTOPTP>
                port 5 priority 128 path cost 200000 proto rstp
                role designated state forwarding
```

`root id 00:01:02:4b:d4:50 priority 32768 ifcost 400000 port 4` の行は、ルートブリッジが `00:01:02:4b:d4:50` であり、このブリッジからのパスコストが `400000` であることを示しています。
ルートブリッジへの経路は `port 4`、すなわち `fxp0` を経由しています。

<a id="chapter-35-heading-35"></a>
### ブリッジインタフェースのパラメータ（Bridge Interface Parameters）

`ifconfig` には、ブリッジインタフェースに固有のパラメータがいくつか存在します。
この節では、それらのパラメータの一般的な用途をまとめます。
利用可能なパラメータの完全な一覧は `ifconfig(8)` を参照してください。

* **`private`**: プライベートインタフェースは、同じくプライベートインタフェースとして指定されている他のどのポートに対してもトラフィックを転送しません。トラフィックは無条件にブロックされるため、ARP パケットを含めイーサネットフレームは一切転送されません。トラフィックを選択的にブロックする必要がある場合は、代わりにファイアウォールを使用してください。
* **`span`**: スパンポート（span port）は、ブリッジが受信したすべてのイーサネットフレームのコピーを送出します。1 つのブリッジに設定できる span ポートの数に制限はありませんが、span ポートとして指定されたインタフェースは通常のブリッジポートとしては使用できません。これは、ブリッジの span ポートの 1 つに接続した別ホスト上で、ブリッジされたネットワークをパッシブに監視（スヌーピング）したい場合に最も有用です。たとえば、`fxp4` という名前のインタフェースへ全フレームのコピーを送出するには次のようにします。

```shell
# ifconfig bridge0 span fxp4
```

* **`sticky`**: ブリッジのメンバーインタフェースを sticky に設定すると、動的に学習されたアドレスエントリが転送キャッシュ内で静的エントリとして扱われます。sticky エントリは、別のインタフェースで同じアドレスが観測されたとしても、キャッシュからタイムアウトで消去されたり置き換えられたりしません。これにより、転送テーブルを事前登録することなく静的アドレスエントリの利点を得られます。ブリッジの特定のセグメントで学習されたクライアントは、別のセグメントへ移動（roam）できなくなります。
  sticky アドレスの活用例の 1 つに、ブリッジと VLAN を組み合わせて IP アドレス空間を無駄にせず顧客ネットワークを分離する構成があります。`CustomerA` が `vlan100`、`CustomerB` が `vlan101` にあり、ブリッジがアドレス `192.168.0.1` を持つ場合を考えます。

```shell
# ifconfig bridge0 addm vlan100 sticky vlan100 addm vlan101 sticky vlan101
# ifconfig bridge0 inet 192.168.0.1/24
```

  この例では、双方のクライアントが `192.168.0.1` をデフォルトゲートウェイとして認識します。ブリッジキャッシュが sticky であるため、一方のホストが他方の顧客の MAC アドレスを偽装してトラフィックを傍受することはできません。
  VLAN 間のあらゆる通信は、ファイアウォールを使うか、この例のようにプライベートインタフェースを用いてブロックできます。

```shell
# ifconfig bridge0 private vlan100 private vlan101
```

  これで顧客同士は完全に分離され、サブネット分割を行わずに `/24` のアドレス範囲全体を割り当てることができます。
  さらに、あるインタフェースの背後に置ける一意な送信元 MAC アドレスの数を制限することもできます。上限に達すると、既存のホストキャッシュエントリが期限切れになるか削除されるまで、未知の送信元アドレスを持つパケットは破棄されます。
  次の例では、`vlan100` 上の `CustomerA` に対するイーサネットデバイスの最大数を 10 に設定しています。

```shell
# ifconfig bridge0 ifmaxaddr vlan100 10
```

ブリッジインタフェースはモニターモード（monitor mode）にも対応しており、`bpf(4)` での処理後にパケットを破棄し、それ以上の処理や転送を行いません。
これは、2 つ以上のインタフェースからの入力を単一の `bpf(4)` ストリームへ多重化するために利用できます。
RX と TX の信号を 2 つの別々のインタフェースから出力するネットワークタップのトラフィックを再構成したい場合に便利です。
たとえば、4 つのネットワークインタフェースからの入力を 1 つのストリームとして読み取るには次のようにします。

```shell
# ifconfig bridge0 addm fxp0 addm fxp1 addm fxp2 addm fxp3 monitor up
# tcpdump -i bridge0
```

<a id="chapter-35-heading-36"></a>
### SNMP による監視（SNMP Monitoring）

ブリッジインタフェースと STP パラメータは、FreeBSD ベースシステムに含まれる `bsnmpd(1)` を介して監視できます。
エクスポートされるブリッジ MIB は IETF 標準に準拠しているため、任意の SNMP クライアントや監視パッケージを使ってデータを取得できます。

ブリッジの監視を有効にするには、`/etc/snmpd.config` 内の次の行の先頭にある `#` 記号を削除してコメントを解除します。

```
begemotSnmpdModulePath."bridge" = "/usr/lib/snmp_bridge.so"
```

このファイルでは、コミュニティ名やアクセスリストなど、その他の設定項目も変更が必要になる場合があります。
詳細は `bsnmpd(1)` および `snmp_bridge(3)` を参照してください。
これらの編集内容を保存したら、`/etc/rc.conf` に次の行を追加します。

```
bsnmpd_enable="YES"
```

その後、`bsnmpd(1)` を起動します。

```shell
# service bsnmpd start
```

以下の例では、クライアントシステムからブリッジへ問い合わせるために Net-SNMP ソフトウェア（`net-mgmt/net-snmp`）を使用しています。
`net-mgmt/bsnmptools` port を使用することもできます。
Net-SNMP が動作している SNMP クライアント側で、ブリッジ MIB 定義を読み込むために `$HOME/.snmp/snmp.conf` へ次の行を追加します。

```
mibdirs +/usr/share/snmp/mibs
mibs +BRIDGE-MIB:RSTP-MIB:BEGEMOT-MIB:BEGEMOT-BRIDGE-MIB
```

IETF BRIDGE-MIB（RFC4188）を使って単一のブリッジを監視するには次のようにします。

```shell
% snmpwalk -v 2c -c public bridge1.example.com mib-2.dot1dBridge
BRIDGE-MIB::dot1dBaseBridgeAddress.0 = STRING: 66:fb:9b:6e:5c:44
BRIDGE-MIB::dot1dBaseNumPorts.0 = INTEGER: 1 ports
BRIDGE-MIB::dot1dStpTimeSinceTopologyChange.0 = Timeticks: (189959) 0:31:39.59 centi-seconds
BRIDGE-MIB::dot1dStpTopChanges.0 = Counter32: 2
BRIDGE-MIB::dot1dStpDesignatedRoot.0 = Hex-STRING: 80 00 00 01 02 4B D4 50
...
BRIDGE-MIB::dot1dStpPortState.3 = INTEGER: forwarding(5)
BRIDGE-MIB::dot1dStpPortEnable.3 = INTEGER: enabled(1)
BRIDGE-MIB::dot1dStpPortPathCost.3 = INTEGER: 200000
BRIDGE-MIB::dot1dStpPortDesignatedRoot.3 = Hex-STRING: 80 00 00 01 02 4B D4 50
BRIDGE-MIB::dot1dStpPortDesignatedCost.3 = INTEGER: 0
BRIDGE-MIB::dot1dStpPortDesignatedBridge.3 = Hex-STRING: 80 00 00 01 02 4B D4 50
BRIDGE-MIB::dot1dStpPortDesignatedPort.3 = Hex-STRING: 03 80
BRIDGE-MIB::dot1dStpPortForwardTransitions.3 = Counter32: 1
RSTP-MIB::dot1dStpVersion.0 = INTEGER: rstp(2)
```

`dot1dStpTopChanges.0` の値が 2 になっており、STP ブリッジトポロジが 2 回変化したことを示しています。
トポロジ変化とは、ネットワーク内の 1 つ以上のリンクに変化または障害が発生し、新しいツリーが計算されたことを意味します。
`dot1dStpTimeSinceTopologyChange.0` の値は、それがいつ起きたかを示します。

複数のブリッジインタフェースを監視するには、プライベートな BEGEMOT-BRIDGE-MIB を使用できます。

```shell
% snmpwalk -v 2c -c public bridge1.example.com
enterprises.fokus.begemot.begemotBridge
BEGEMOT-BRIDGE-MIB::begemotBridgeBaseName."bridge0" = STRING: bridge0
BEGEMOT-BRIDGE-MIB::begemotBridgeBaseName."bridge2" = STRING: bridge2
BEGEMOT-BRIDGE-MIB::begemotBridgeBaseAddress."bridge0" = STRING: e:ce:3b:5a:9e:13
BEGEMOT-BRIDGE-MIB::begemotBridgeBaseAddress."bridge2" = STRING: 12:5e:4d:74:d:fc
BEGEMOT-BRIDGE-MIB::begemotBridgeBaseNumPorts."bridge0" = INTEGER: 1
BEGEMOT-BRIDGE-MIB::begemotBridgeBaseNumPorts."bridge2" = INTEGER: 1
...
BEGEMOT-BRIDGE-MIB::begemotBridgeStpTimeSinceTopologyChange."bridge0" = Timeticks: (116927) 0:19:29.27 centi-seconds
BEGEMOT-BRIDGE-MIB::begemotBridgeStpTimeSinceTopologyChange."bridge2" = Timeticks: (82773) 0:13:47.73 centi-seconds
BEGEMOT-BRIDGE-MIB::begemotBridgeStpTopChanges."bridge0" = Counter32: 1
BEGEMOT-BRIDGE-MIB::begemotBridgeStpTopChanges."bridge2" = Counter32: 1
BEGEMOT-BRIDGE-MIB::begemotBridgeStpDesignatedRoot."bridge0" = Hex-STRING: 80 00 00 40 95 30 5E 31
BEGEMOT-BRIDGE-MIB::begemotBridgeStpDesignatedRoot."bridge2" = Hex-STRING: 80 00 00 50 8B B8 C6 A9
```

`mib-2.dot1dBridge` サブツリー経由で監視対象となるブリッジインタフェースを切り替えるには次のようにします。

```shell
% snmpset -v 2c -c private bridge1.example.com
BEGEMOT-BRIDGE-MIB::begemotBridgeDefaultBridgeIf.0 s bridge2
```

<a id="network-aggregation"></a>
## リンクアグリゲーションとフェイルオーバー（Link Aggregation and Failover）

FreeBSD には `lagg(4)` インタフェースが用意されており、複数のネットワークインタフェースを 1 つの仮想インタフェースに束ねて、フェイルオーバーやリンクアグリゲーションを実現できます。
フェイルオーバーでは、束ねられたネットワークインタフェースのうち少なくとも 1 つでリンクが確立されている限り、トラフィックを流し続けることができます。
リンクアグリゲーションは LACP をサポートするスイッチで最も効果を発揮します。LACP は個々のリンク障害に対応しつつ、双方向にトラフィックを分散するためです。

`lagg` インタフェースがサポートするアグリゲーションプロトコルによって、送信トラフィックにどのポートを使うか、また特定のポートで受信トラフィックを受け入れるかどうかが決まります。
`lagg(4)` は次のプロトコルをサポートしています。

* **`failover`**: このモードでは、マスターポートのみを通じてトラフィックを送受信します。マスターポートが利用できなくなると、次のアクティブなポートが使用されます。仮想インタフェースに最初に追加されたインタフェースがマスターポートとなり、それ以降に追加されたインタフェースはすべてフェイルオーバー用デバイスとして使われます。非マスターポートへフェイルオーバーした場合でも、元のポートが再び利用可能になるとマスターに戻ります。
* **`loadbalance`**: 静的な設定を提供し、対向機器とのアグリゲーションネゴシエーションやリンク監視のためのフレーム交換を行いません。スイッチが LACP をサポートしている場合は、代わりに LACP を使用すべきです。
* **`lacp`**: IEEE® 802.3ad Link Aggregation Control Protocol（LACP）は、対向機器とネゴシエーションを行って、集約可能なリンク群を 1 つ以上の Link Aggregated Group（LAG）にまとめます。各 LAG は同じ速度で全二重動作に設定されたポートで構成され、合計速度が最大の LAG 内のポート間でトラフィックが分散されます。通常はすべてのポートを含む LAG が 1 つだけ存在します。物理的な接続状態が変化した場合、LACP は迅速に新しい構成へ収束します。
  LACP はプロトコルヘッダのハッシュ情報に基づいてアクティブなポート間で送信トラフィックを分散し、どのアクティブなポートからでも受信トラフィックを受け入れます。ハッシュにはイーサネットの送信元・宛先アドレスに加え、利用可能であれば VLAN タグ、および IPv4 または IPv6 の送信元・宛先アドレスが含まれます。
* **`roundrobin`**: このモードでは、ラウンドロビンスケジューラを使ってすべてのアクティブなポートへ送信トラフィックを分散し、どのアクティブなポートからでも受信トラフィックを受け入れます。このモードはイーサネットフレームの順序保証に違反するため、注意して使用する必要があります。
* **`broadcast`**: このモードでは、`lagg` インタフェースに設定されたすべてのポートへ送信トラフィックを送出し、どのポートでもフレームを受信します。

<a id="chapter-35-heading-38"></a>
### 設定例（Configuration Examples）

この節では、Cisco® スイッチと FreeBSD システムで LACP 負荷分散を設定する方法を示します。
続いて、2 つのイーサネットインタフェースをフェイルオーバーモードで設定する方法と、イーサネットと無線インタフェースの間でフェイルオーバーモードを設定する方法を説明します。

<a id="networking-lacp-aggregation-cisco"></a>
**例 1. Cisco® スイッチとの LACP アグリゲーション（LACP Aggregation with a Cisco® Switch）**

この例では、FreeBSD マシン上の 2 つの `fxp(4)` イーサネットインタフェースを Cisco® スイッチの最初の 2 つのイーサネットポートに接続し、負荷分散と耐障害性を備えた 1 本のリンクとして構成します。
さらにインタフェースを追加してスループットと耐障害性を高めることも可能です。
例に示されている Cisco® のポート名、イーサネットデバイス名、チャネルグループ番号、IP アドレスは、実際の環境に合わせて置き換えてください。

イーサネットリンクではフレーム順序の維持が必須であるため、2 台の端末間のトラフィックは常に同じ物理リンクを通過し、最大速度は 1 本のインタフェースの速度に制限されます。
送信アルゴリズムは、可能な限り多くの情報を用いて異なるトラフィックフローを識別し、利用可能なインタフェース全体へフローを分散しようとします。

Cisco® スイッチ側で、`FastEthernet0/1` と `FastEthernet0/2` インタフェースをチャネルグループ `1` に追加します。

```shell
interface FastEthernet0/1
 channel-group 1 mode active
 channel-protocol lacp
!
interface FastEthernet0/2
 channel-group 1 mode active
 channel-protocol lacp
```

FreeBSD システム側では、物理インタフェース `fxp0` と `fxp1` を使って `lagg(4)` インタフェースを作成し、IP アドレス `10.0.0.3/24` を設定して有効化します。

```shell
# ifconfig fxp0 up
# ifconfig fxp1 up
# ifconfig lagg0 create
# ifconfig lagg0 up laggproto lacp laggport fxp0 laggport fxp1 10.0.0.3/24
```

次に、仮想インタフェースの状態を確認します。

```shell
# ifconfig lagg0
lagg0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        options=8<VLAN_MTU>
        ether 00:05:5d:71:8d:b8
        inet 10.0.0.3 netmask 0xffffff00 broadcast 10.0.0.255
        media: Ethernet autoselect
        status: active
        laggproto lacp
        laggport: fxp1 flags=1c<ACTIVE,COLLECTING,DISTRIBUTING>
        laggport: fxp0 flags=1c<ACTIVE,COLLECTING,DISTRIBUTING>
```

`ACTIVE` と表示されているポートは、対向スイッチとのネゴシエーションが完了した LAG の一部です。
トラフィックはこれらのアクティブなポートを通じて送受信されます。
LAG 識別子を表示するには、上記のコマンドに `-v` を追加してください。

Cisco® スイッチ側でポートの状態を確認するには次のようにします。

```shell
switch# show lacp neighbor
Flags:  S - Device is requesting Slow LACPDUs
        F - Device is requesting Fast LACPDUs
        A - Device is in Active mode       P - Device is in Passive mode

Channel group 1 neighbors

Partner's information:

                  LACP port                        Oper    Port     Port
Port      Flags   Priority  Dev ID         Age     Key     Number   State
Fa0/1     SA      32768     0005.5d71.8db8  29s    0x146   0x3      0x3D
Fa0/2     SA      32768     0005.5d71.8db8  29s    0x146   0x4      0x3D
```

さらに詳しい情報を表示するには `show lacp neighbor detail` を実行します。

再起動後もこの設定を維持するには、FreeBSD システムの `/etc/rc.conf` に次のエントリを追加します。

```
ifconfig_fxp0="up"
ifconfig_fxp1="up"
cloned_interfaces="lagg0"
ifconfig_lagg0="laggproto lacp laggport fxp0 laggport fxp1 10.0.0.3/24"
```

<a id="networking-lagg-failover"></a>
**例 2. フェイルオーバーモード（Failover Mode）**

フェイルオーバーモードを使用すると、マスターインタフェースでリンクが失われた場合にセカンダリインタフェースへ切り替えることができます。
フェイルオーバーを設定するには、配下の物理インタフェースが有効（up）になっていることを確認したうえで、`lagg(4)` インタフェースを作成します。
この例では、`fxp0` をマスターインタフェース、`fxp1` をセカンダリインタフェースとし、仮想インタフェースに IP アドレス `10.0.0.15/24` を割り当てます。

```shell
# ifconfig fxp0 up
# ifconfig fxp1 up
# ifconfig lagg0 create
# ifconfig lagg0 up laggproto failover laggport fxp0 laggport fxp1 10.0.0.15/24
```

仮想インタフェースは次のように表示されるはずです。

```shell
# ifconfig lagg0
lagg0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        options=8<VLAN_MTU>
        ether 00:05:5d:71:8d:b8
        inet 10.0.0.15 netmask 0xffffff00 broadcast 10.0.0.255
        media: Ethernet autoselect
        status: active
        laggproto failover
        laggport: fxp1 flags=0<>
        laggport: fxp0 flags=5<MASTER,ACTIVE>
```

トラフィックは `fxp0` 上で送受信されます。
`fxp0` のリンクが失われると、`fxp1` がアクティブなリンクになります。
マスターインタフェースのリンクが復旧すると、再びマスターがアクティブなリンクに戻ります。

再起動後もこの設定を維持するには、`/etc/rc.conf` に次のエントリを追加します。

```
ifconfig_fxp0="up"
ifconfig_fxp1="up"
cloned_interfaces="lagg0"
ifconfig_lagg0="laggproto failover laggport fxp0 laggport fxp1 10.0.0.15/24"
```

<a id="networking-lagg-wired-and-wireless"></a>
**例 3. イーサネットと無線インタフェース間のフェイルオーバーモード（Failover Mode Between Ethernet and Wireless Interfaces）**

ノート PC のユーザーにとっては、通常、有線イーサネット接続が利用できないときにのみ使われるセカンダリとして無線デバイスを設定するのが望ましいでしょう。
`lagg(4)` を使えば、性能面とセキュリティ面の両方から有線イーサネット接続を優先しつつ、必要に応じて無線接続経由でデータ通信を継続できるフェイルオーバーを構成できます。

これは、有線イーサネットインタフェースの MAC アドレスを無線インタフェースの MAC アドレスで上書きすることによって実現します。

> **注記**: 理論上は、有線イーサネットと無線のどちらの MAC アドレスを変更してもう一方に合わせることも可能です。しかし、広く使われている無線インタフェースの中には MAC アドレスの上書きに対応していないものがあります。そのため、この目的では有線イーサネット側の MAC アドレスを上書きすることを推奨します。

> **注記**: 無線インタフェース用のドライバが `GENERIC` カーネルまたはカスタムカーネルに組み込まれておらず、コンピュータで FreeBSD 12.1 が動作している場合は、`/boot/loader.conf` に対応する `.ko` を読み込むための `*driver_load="YES"*` を追加して再起動してください。より良い別の方法として、`/etc/rc.conf` の `kld_list` にドライバを追加して再起動する方法もあります（詳細は `rc.conf(5)` を参照してください）。これを行わないと、`lagg(4)` インタフェースを設定する時点でまだドライバが読み込まれていない状態になるため、この手順が必要です。
>
> **訳注**: 原文では FreeBSD のバージョン属性 `{rel121-current}`（固定原文の `shared/releases.adoc` における値は `12.1`）が参照されています。より新しい FreeBSD リリースでも、`kld_list` によるカーネルモジュールの読み込みは同様に有効です。

この例では、有線イーサネットインタフェースの `re0` をマスターとし、無線インタフェースの `wlan0` をフェイルオーバー先とします。
`wlan0` インタフェースは物理無線インタフェース `ath0` から作成されており、有線イーサネットインタフェースには無線インタフェースの MAC アドレスを設定します。
まず、無線インタフェースを有効化します（`FR` はお住まいの地域の 2 文字の国コードに置き換えてください）が、この時点では IP アドレスを設定しません。
`wlan0` はシステム上の実際の無線インタフェース名に合わせて置き換えてください。

```shell
# ifconfig wlan0 create wlandev ath0 country FR ssid my_router up
```

次のようにして無線インタフェースの MAC アドレスを確認します。

```shell
# ifconfig wlan0
wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
	ether b8:ee:65:5b:32:59
	groups: wlan
	ssid Bbox-A3BD2403 channel 6 (2437 MHz 11g ht/20) bssid 00:37:b7:56:4b:60
	regdomain ETSI country FR indoor ecm authmode WPA2/802.11i privacy ON
	deftxkey UNDEF AES-CCM 2:128-bit txpower 30 bmiss 7 scanvalid 60
	protmode CTS ampdulimit 64k ampdudensity 8 shortgi -stbctx stbcrx
	-ldpc wme burst roaming MANUAL
	media: IEEE 802.11 Wireless Ethernet MCS mode 11ng
	status: associated
	nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
```

`ether` 行に、指定したインタフェースの MAC アドレスが表示されます。
次に、有線イーサネットインタフェースの MAC アドレスを同じ値へ変更します。

```shell
# ifconfig re0 ether b8:ee:65:5b:32:59
```

`re0` インタフェースが有効（up）になっていることを確認したうえで、`re0` をマスター、`wlan0` をフェイルオーバー先として `lagg(4)` インタフェースを作成します。

```shell
# ifconfig re0 up
# ifconfig lagg0 create
# ifconfig lagg0 up laggproto failover laggport re0 laggport wlan0
```

仮想インタフェースは次のように表示されるはずです。

```shell
# ifconfig lagg0
lagg0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        options=8<VLAN_MTU>
        ether b8:ee:65:5b:32:59
        laggproto failover lagghash l2,l3,l4
        laggport: re0 flags=5<MASTER,ACTIVE>
        laggport: wlan0 flags=0<>
        groups: lagg
        media: Ethernet autoselect
        status: active
```

その後、DHCP クライアントを起動して IP アドレスを取得します。

```shell
# dhclient lagg0
```

再起動後もこの設定を維持するには、`/etc/rc.conf` に次のエントリを追加します。

```
ifconfig_re0="ether b8:ee:65:5b:32:59"
wlans_ath0="wlan0"
ifconfig_wlan0="WPA"
create_args_wlan0="country FR"
cloned_interfaces="lagg0"
ifconfig_lagg0="up laggproto failover laggport re0 laggport wlan0 DHCP"
```
