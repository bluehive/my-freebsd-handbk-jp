<a id="network"></a>
# 第7章 ネットワーク（Network）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/network/)の「Chapter 7. Network」（既存 TOC ID なし）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/network/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 本訳は作業中のドラフトです。原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` および `$` は一般ユーザーのプロンプトを示します。

<a id="network-synopsis"></a>
## 概要

本章では、FreeBSD におけるネットワークの設定とパフォーマンスについて解説し、FreeBSD オペレーティングシステムが備える堅牢なネットワーク機能を紹介します。有線ネットワークと無線ネットワークのどちらを使う場合でも、FreeBSD でネットワーク接続を設定・最適化するための包括的なガイドとして利用できます。

詳細に進む前に、プロトコル、ネットワークインターフェース、アドレッシングといったネットワークの基本概念を理解しておくと役立ちます。

本章では次の内容を扱います。

* ネットワークインターフェースの設定、アドレッシング、カスタマイズオプションを含む、FreeBSD での有線ネットワークの設定方法
* 無線ネットワークインターフェースの設定、セキュリティプロトコル、トラブルシューティング手法を含む、FreeBSD での無線ネットワークの設定スキル
* FreeBSD のネットワーク機能と、優れたネットワーク性能で知られる理由
* DNS や DHCP などの設定手順を含む、FreeBSD がサポートする各種ネットワークサービスとプロトコルの理解

高度なネットワーク設定の方法については、[高度なネットワーク（Advanced Networking）](35-advanced-networking.md#advanced-networking)に詳しい情報があります。

<a id="config-network-setup"></a>
## ネットワークの設定

有線または無線のネットワーク接続を設定することは、FreeBSD ユーザーにとって一般的な作業です。この節では、有線および無線のネットワークアダプタを特定し、設定する方法を説明します。

設定を始める前に、次のネットワーク情報を把握しておく必要があります。

* ネットワークに DHCP があるかどうか
* DHCP がない場合、使用する静的 IP アドレス
* ネットマスク
* デフォルトゲートウェイの IP アドレス

> **ヒント**: ネットワーク接続は、インストール時に `bsdinstall(8)` によってすでに設定されている場合があります。

<a id="config-identify-network-adapter"></a>
### ネットワークアダプタの特定

FreeBSD は、有線・無線ともに幅広いネットワークアダプタをサポートしています。お使いのネットワークアダプタが対応しているかどうかは、使用している [FreeBSD リリース](https://www.freebsd.org/releases/)のハードウェア互換性リスト（Hardware Compatibility List）を確認してください。

システムで使用されているネットワークアダプタを調べるには、次のコマンドを実行します。

```shell
% pciconf -lv | grep -A1 -B3 network
```

出力は次のようになります。

```text
em0@pci0:0:25:0:        class=0x020000 rev=0x03 hdr=0x00 vendor=0x8086 device=0x10f5 subvendor=0x17aa subdevice=0x20ee
    vendor     = 'Intel Corporation' <1>
    device     = '82567LM Gigabit Network Connection' <2>
    class      = network
    subclass   = ethernet
--
iwm0@pci0:3:0:0:        class=0x028000 rev=0x00 hdr=0x00 vendor=0x8086 device=0x4237 subvendor=0x8086 subdevice=0x1211
    vendor     = 'Intel Corporation' <1>
    device     = 'PRO/Wireless 5100 AGN [Shiloh] Network Connection' <2>
    class      = network
```

`@` 記号の前の文字列が、そのデバイスを制御するドライバの名前です。この例では `em(4)` と `iwn(4)` です。

> **訳注**: 原文の `pciconf` 出力例では 2 つ目のデバイス名が `iwm0` となっていますが、本文では `iwn(4)` と記載されています（原文どおり保持しています）。

1. `<1>`: ベンダー名を示します。
2. `<2>`: デバイス名を示します。

> **注**: ネットワークインターフェースカードのモジュールを手動で読み込む必要があるのは、FreeBSD がカードを正しく検出できなかった場合のみです。
>
> たとえば `alc(4)` モジュールを読み込むには、次のコマンドを実行します。

```shell
# kldload if_alc
```

> あるいは、起動時にドライバをモジュールとして読み込むには、`/boot/loader.conf` に次の行を追加します。

```text
if_alc_load="YES"
```

<a id="config-network-connection"></a>
## 有線ネットワーク

適切なドライバが読み込まれたら、ネットワークアダプタを設定する必要があります。FreeBSD では、ドライバ名の後ろにユニット番号を付けてネットワークインターフェースアダプタに名前を付けます。ユニット番号は、起動時に検出された順、または後から発見された順を表します。

たとえば、`em0` はシステム上で `em(4)` ドライバを使用する最初のネットワークインターフェースカード（NIC）です。

ネットワークインターフェースの設定を表示するには、次のコマンドを入力します。

```shell
% ifconfig
```

出力は次のようになります。

```text
em0: flags=8863<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        options=481249b<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,VLAN_HWCSUM,LRO,WOL_MAGIC,VLAN_HWFILTER,NOMAP>
        ether 00:1f:16:0f:27:5a
        inet6 fe80::21f:16ff:fe0f:275a%em0 prefixlen 64 scopeid 0x1
        inet 192.168.1.19 netmask 0xffffff00 broadcast 192.168.1.255
        media: Ethernet autoselect (1000baseT <full-duplex>)
        status: active
        nd6 options=23<PERFORMNUD,ACCEPT_RTADV,AUTO_LINKLOCAL>
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> metric 0 mtu 16384
        options=680003<RXCSUM,TXCSUM,LINKSTATE,RXCSUM_IPV6,TXCSUM_IPV6>
        inet6 ::1 prefixlen 128
        inet6 fe80::1%lo0 prefixlen 64 scopeid 0x2
        inet 127.0.0.1 netmask 0xff000000
        groups: lo
        nd6 options=21<PERFORMNUD,AUTO_LINKLOCAL>
```

この例では、次のデバイスが表示されています。

* `em0`: イーサネットインターフェース。
* `lo0`: ループバックインターフェース。性能分析、ソフトウェアのテスト、ローカル通信などに利用できるソフトウェアのループバック機構です。詳細は `lo(4)` を参照してください。

この例は、`em0` が起動して稼働していることを示しています。

主な確認点は次のとおりです。

1. `UP` は、インターフェースが設定済みで利用可能であることを意味します。
2. インターフェースには IPv4 インターネット（`inet`）アドレス `192.168.1.19` が設定されています。
3. インターフェースには IPv6 インターネット（`inet6`）アドレス `fe80::21f:16ff:fe0f:275a%em0` が設定されています。
4. 有効なサブネットマスク（`netmask`）が設定されており、`0xffffff00` は `255.255.255.0` と同じです。
5. 有効なブロードキャストアドレス `192.168.1.255` が設定されています。
6. インターフェースの MAC アドレス（`ether`）は `00:1f:16:0f:27:5a` です。
7. 物理メディアの選択は自動選択モード（`media: Ethernet autoselect (1000baseT <full-duplex>)`）になっています。
8. リンクの状態（`status`）は `active` であり、キャリア信号が検出されていることを示します。`em0` の場合、イーサネットケーブルがインターフェースに接続されていないときは `status: no carrier` と表示されるのが正常です。

`ifconfig(8)` の出力が次のような内容であった場合は、インターフェースがまだ設定されていないことを示します。

```text
em0: flags=8822<BROADCAST,SIMPLEX,MULTICAST> metric 0 mtu 1500
        options=481249b<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,VLAN_HWCSUM,LRO,WOL_MAGIC,VLAN_HWFILTER,NOMAP>
        ether 00:1f:16:0f:27:5a
        media: Ethernet autoselect
        status: no carrier
        nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
```

<a id="config-static-ip-v4"></a>
### 静的 IPv4 アドレスの設定

この節では、FreeBSD システムに静的 IPv4 アドレスを設定する手順を説明します。

ネットワークインターフェースカードの設定はコマンドラインから `ifconfig(8)` で行えますが、`/etc/rc.conf` にも設定を追加しておかなければ再起動後には保持されません。

> **注**: インストール時に `bsdinstall(8)` でネットワークを設定している場合、ネットワークインターフェースカード（NIC）用のエントリがすでに存在していることがあります。`sysrc(8)` を実行する前に `/etc/rc.conf` を再確認してください。

IP アドレスは次のコマンドで設定できます。

```shell
# ifconfig em0 inet 192.168.1.150/24
```

再起動後も変更を維持するには、次のコマンドを実行します。

```shell
# sysrc ifconfig_em0="inet 192.168.1.150 netmask 255.255.255.0"
```

デフォルトルータを追加するには、次のコマンドを実行します。

```shell
# sysrc defaultrouter="192.168.1.1"
```

`/etc/resolv.conf` に DNS レコードを追加します。

```text
nameserver 8.8.8.8
nameserver 8.8.4.4
```

次に、以下のコマンドを実行して `netif` と `routing` を再起動します。

```shell
# service netif restart && service routing restart
```

接続は `ping(8)` を使ってテストできます。

```shell
% ping -c2 www.FreeBSD.org
```

出力は次のようになります。

```text
PING web.geo.FreeBSD.org (147.28.184.45): 56 data bytes
64 bytes from 147.28.184.45: icmp_seq=0 ttl=51 time=55.173 ms
64 bytes from 147.28.184.45: icmp_seq=1 ttl=51 time=53.093 ms

--- web.geo.FreeBSD.org ping statistics ---
2 packets transmitted, 2 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 53.093/54.133/55.173/1.040 ms
```

<a id="config-dynamic-ip-v4"></a>
### 動的 IPv4 アドレスの設定

ネットワークに DHCP サーバがある場合、ネットワークインターフェースで DHCP を使うように設定するのは非常に簡単です。FreeBSD では DHCP クライアントとして `dhclient(8)` を使用します。`dhclient(8)` は IP アドレス、ネットマスク、デフォルトルータを自動的に設定します。

インターフェースで DHCP を使用するようにするには、次のコマンドを実行します。

```shell
# sysrc ifconfig_em0="DHCP"
```

次のコマンドを実行して、`dhclient(8)` を手動で起動することもできます。

```shell
# dhclient em0
```

出力は次のようになります。

```text
DHCPREQUEST on em0 to 255.255.255.255 port 67
DHCPACK from 192.168.1.1
unknown dhcp option value 0x7d
bound to 192.168.1.19 -- renewal in 43200 seconds.
```

このようにして、DHCP によるアドレス割り当てが正しく機能していることを確認できます。

> **ヒント**: `dhclient(8)` クライアントはバックグラウンドで起動できます。ネットワークが利用可能であることに依存するアプリケーションでは問題が生じることもありますが、多くの場合、起動が高速になります。
>
> `dhclient(8)` をバックグラウンドで実行するには、次のコマンドを実行します。

```shell
# sysrc background_dhclient="YES"
```

続いて、次のコマンドを実行して `netif` を再起動します。

```shell
# service netif restart
```

接続は `ping(8)` を使ってテストできます。

```shell
% ping -c2 www.FreeBSD.org
```

出力は次のようになります。

```text
PING web.geo.FreeBSD.org (147.28.184.45): 56 data bytes
64 bytes from 147.28.184.45: icmp_seq=0 ttl=51 time=55.173 ms
64 bytes from 147.28.184.45: icmp_seq=1 ttl=51 time=53.093 ms

--- web.geo.FreeBSD.org ping statistics ---
2 packets transmitted, 2 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 53.093/54.133/55.173/1.040 ms
```

<a id="network-ipv6"></a>
### IPv6

IPv6 は、よく知られた IP プロトコル（IPv4 とも呼ばれます）の新しいバージョンです。

IPv6 には IPv4 に比べていくつかの利点があり、多くの新機能も備えています。

* 128 ビットのアドレス空間により、340,282,366,920,938,463,463,374,607,431,768,211,456 個のアドレスを扱えます。これにより、IPv4 アドレスの不足や最終的な枯渇の問題が解消されます。
* ルータは経路表にネットワーク集約アドレスのみを保持するため、経路表の平均サイズを 8192 エントリに抑えられます。これにより、割り当てられたすべての IPv4 アドレスブロックをインターネットルータ間で交換する必要があり経路表が肥大化して効率的なルーティングができなくなる、という IPv4 のスケーラビリティの課題に対処しています。
* アドレス自動設定（[RFC4862](http://www.ietf.org/rfc/rfc4862.txt)）。
* 必須のマルチキャストアドレス。
* 組み込みの IPsec（IP セキュリティ）。
* 簡素化されたヘッダ構造。
* モバイル IP のサポート。
* IPv6 から IPv4 への移行メカニズム。

FreeBSD には [KAME プロジェクト](http://www.kame.net/)の IPv6 リファレンス実装が含まれており、IPv6 を利用するために必要なものがすべて揃っています。

この節では、IPv6 を設定して稼働させる手順に焦点を当てます。

IPv6 アドレスには 3 種類あります。

- **ユニキャスト（Unicast）**: ユニキャストアドレス宛てに送信されたパケットは、そのアドレスが割り当てられたインターフェースに届きます。
- **エニーキャスト（Anycast）**: 構文上はユニキャストアドレスと区別できませんが、複数のインターフェースからなるグループを指定します。エニーキャストアドレス宛てのパケットは、最も近いインターフェースに届きます。
- **マルチキャスト（Multicast）**: インターフェースのグループを識別します。マルチキャストアドレス宛てのパケットは、そのマルチキャストグループに属するすべてのインターフェースに届きます。IPv4 で通常 `xxx.xxx.xxx.255` として使われるブロードキャストアドレスは、IPv6 ではマルチキャストアドレスで表現されます。

IPv6 アドレスを読む際の正規表記は `x:x:x:x:x:x:x:x` で表され、各 `x` は 16 ビットの 16 進数値を示します。たとえば `FEBC:A574:382B:23C1:AA49:4592:4EFE:9982` のようになります。

アドレスにはすべて 0 からなる長い部分列が含まれることがよくあります。1 つのアドレスにつき 1 か所に限り、この部分列を `::`（二重コロン）で置き換えることができます。また、各 16 進数値の先頭にある `0` は最大 3 桁まで省略できます。たとえば `fe80::1` は、正規表記の `fe80:0000:0000:0000:0000:0000:0000:0001` に対応します。

3 つ目の表記法として、末尾 32 ビットを広く知られた IPv4 表記で書く方法があります。たとえば `2002::10.0.0.1` は 16 進数の正規表記 `2002:0000:0000:0000:0000:0000:0a00:0001` に対応し、さらに `2002::a00:1` と等価です。

FreeBSD システムの IPv6 アドレスを表示するには、次のコマンドを実行します。

```shell
# ifconfig
```

出力は次のようになります。

```text
em0: flags=8863<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        options=481249b<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,VLAN_HWCSUM,LRO,WOL_MAGIC,VLAN_HWFILTER,NOMAP>
        ether 00:1f:16:0f:27:5a
        inet 192.168.1.150 netmask 0xffffff00 broadcast 192.168.1.255
        inet6 fe80::21f:16ff:fe0f:275a%em0 prefixlen 64 scopeid 0x1
        media: Ethernet autoselect (1000baseT <full-duplex>)
        status: active
        nd6 options=23<PERFORMNUD,ACCEPT_RTADV,AUTO_LINKLOCAL>
```

この例では、`em0` インターフェースは MAC アドレスから自動生成されたリンクローカルアドレス `fe80::21f:16ff:fe0f:275a%em0` を使用しています。

一部の IPv6 アドレスは予約されています。予約済みアドレスの一覧は次の表で確認できます。

<a id="reservedip6"></a>
**表: IPv6 予約アドレスの例**

| IPv6 アドレス | 説明 | 備考 |
|---|---|---|
| `::/128` | 未指定（unspecified） | IPv4 の `0.0.0.0` に相当。 |
| `::1/128` | ループバックアドレス | IPv4 の `127.0.0.1` に相当。 |
| `::ffff:0.0.0.0/96` | IPv4 射影 IPv6 アドレス | IPv4 ホストおよびルータとの互換性のため、下位 32 ビットが IPv4 アドレスとなる。 |
| `fe80::/10` | リンクローカルユニキャスト | IPv4 の 169.254.0.0/16 に相当。 |
| `fc00::/7` | ユニークローカル | ユニークローカルアドレスはローカル通信向けであり、相互に協力するサイト群の内部でのみルーティング可能。 |
| `ff00::/8` | マルチキャスト | |
| `2000::/3` | グローバルユニキャスト | すべてのグローバルユニキャストアドレスはこのプールから割り当てられる。先頭 3 ビットは `001`。 |
| `2001:db8::/32, 3fff::/20` | ドキュメント用 | 文書内で使用するための IPv6 アドレスプレフィックス。 |

IPv6 アドレスの構造についての詳細は、[RFC4291](http://www.ietf.org/rfc/rfc4291.txt) を参照してください。

<a id="config-static-ip-v6"></a>
### 静的 IPv6 アドレスの設定

静的 IPv6 アドレスを持つ IPv6 クライアントとして FreeBSD システムを設定するには、IPv6 アドレスを指定する必要があります。

要件を満たすには、次のコマンドを実行します。

```shell
# sysrc ifconfig_em0_ipv6="inet6 2001:db8:4672:6565:2026:5043:2d42:5344 prefixlen 64"
```

デフォルトルータを割り当てるには、次のコマンドを実行してアドレスを指定します。

```shell
# sysrc ipv6_defaultrouter="2001:db8:4672:6565::1"
```

追加の IPv6 エニーキャストアドレスを設定するには、`rc.conf(5)` で定義されている `_aliasN` としてエニーキャストアドレスを指定し、後ろに `anycast` オプションを付けます。

```shell
# sysrc ifconfig_em0_alias0="inet6 2001:db8:4672:6565::a anycast"
```

アプリケーションはエニーキャストアドレスにバインドできないことに注意してください。バインドが必要な場合は、代わりにエイリアスアドレスを使用する必要があります。

<a id="config-dynamic-ip-v6"></a>
### 動的 IPv6 アドレスの設定

[SLAAC](https://docs.freebsd.org/en/books/handbook/glossary/#slaac-glossary) を使用してインターフェースの IPv6 アドレスを動的に設定するには、次のコマンドを実行します。

```shell
# sysrc ifconfig_em0_ipv6="inet6 accept_rtadv"
# sysrc rtsold_enable="YES"
```

IPv6 パケット転送が有効（すなわち `ipv6_gateway_enable=YES`）になっている場合、`sysctl(8)` 変数 `net.inet6.ip6.rfc6204w3` を 1 に設定しない限り、システムは SLAAC アドレスを設定しないことに注意してください。

<a id="chapter-07-heading-11"></a>
### ルータ広告とホストの自動設定

この節では、IPv6 ルータ上で `rtadvd(8)` を設定し、IPv6 ネットワークプレフィックスとデフォルトルートを広告する方法を示します。

`rtadvd(8)` を有効にするには、次のコマンドを実行します。

```shell
# sysrc rtadvd_enable="YES"
```

IPv6 ルータ広告を行うインターフェースを指定することが重要です。たとえば `rtadvd(8)` に `em0` を使用させるには次のようにします。

```shell
# sysrc rtadvd_interfaces="em0"
```

次に、この例のように設定ファイル `/etc/rtadvd.conf` を作成します。

```text
em0:\
	:addrs#1:addr="2001:db8:1f11:246::":prefixlen#64:tc=ether:
```

`em0` は使用するインターフェースに、`2001:db8:1f11:246::` は割り当てられたプレフィックスに置き換えてください。

専用の `/64` サブネットであれば、ほかに変更する必要はありません。それ以外の場合は、`prefixlen#` を適切な値に変更してください。

<a id="chapter-07-heading-12"></a>
### IPv6 と IPv4 のアドレスマッピング

サーバで IPv6 を有効にしている場合、IPv4 射影 IPv6 アドレスによる通信を有効にする必要が生じることがあります。この互換オプションを使うと、IPv4 アドレスを IPv6 アドレスとして表現できます。IPv6 アプリケーションと IPv4 間の相互通信を許可することは、セキュリティ上の問題になる場合があります。

ほとんどの場合、このオプションは不要であり、互換性のためだけに提供されています。このオプションにより、デュアルスタック環境で IPv6 専用アプリケーションが IPv4 と連携して動作できるようになります。IPv6 専用環境をサポートしていないサードパーティ製アプリケーションで最も役立ちます。

この機能を有効にするには、次のコマンドを実行します。

```shell
# sysrc ipv6_ipv4mapping="YES"
```

<a id="network-wireless"></a>
## 無線ネットワーク

ほとんどの無線ネットワークは [IEEE® 802.11 規格](https://en.wikipedia.org/wiki/IEEE_802.11)に基づいています。

FreeBSD は、[802.11a](https://en.wikipedia.org/wiki/IEEE_802.11a-1999)、[802.11b](https://en.wikipedia.org/wiki/IEEE_802.11b-1999)、[802.11g](https://en.wikipedia.org/wiki/IEEE_802.11g-2003)、および [802.11n](https://en.wikipedia.org/wiki/IEEE_802.11n-2009) を用いて動作するネットワークをサポートしています。

> **注**: FreeBSD における [802.11ac](https://en.wikipedia.org/wiki/IEEE_802.11ac-2013) のサポートは現在開発中です。

基本的な無線ネットワークは、2.4GHz 帯または 5GHz 帯の電波を用いて通信する複数のステーションで構成されます。ただし、使用する周波数帯は地域によって異なり、2.3GHz 帯や 4.9GHz 帯での通信も可能になりつつあります。

無線ネットワークを設定するには、次の 3 つの基本ステップがあります。

1. アクセスポイントをスキャンして選択する
2. ステーションを認証する
3. IP アドレスを設定する、または DHCP を使用する

以下の節では、それぞれのステップを説明します。

<a id="network-wireless-quick-start"></a>
### 無線ネットワーク接続のクイックスタート

FreeBSD を既存の無線ネットワークに接続するのは非常によくある状況です。

このクイックスタート手順では、基本的な認証を使用するネットワークへ接続するために必要なステップを示します。より詳しい手順は次の節で説明します。

最初のステップは、ネットワーク管理者から無線ネットワークの SSID（Service Set Identifier）と事前共有鍵（PSK: Pre-Shared Key）を入手することです。

2 つ目のステップは、このネットワーク用のエントリを `/etc/wpa_supplicant.conf` に追加することです。

ファイルが存在しない場合は作成してください。このファイルのエントリ書式の詳細は `wpa_supplicant.conf(5)` を参照してください。

```text
ctrl_interface=/var/run/wpa_supplicant
eapol_version=1
ap_scan=1
fast_reauth=1

network={
 ssid="myssid"
 psk="mypsk"
}
```

1. `ssid` は無線ネットワークの SSID です。実際の無線ネットワーク名に置き換えてください。
2. `psk` は無線ネットワークの PSK です。実際の無線ネットワークのパスワードに置き換えてください。

3 つ目のステップは、起動時にネットワークを構成するためのネットワークインターフェースのエントリを追加することです。sysctl 変数 `net.wlan.devices` を使って、ネットワークデバイスのインターフェースを取得します。以下の出力例では、この sysctl の結果からネットワークデバイスのインターフェースが `"iwm0"` であることが分かります。

```shell
# sysctl net.wlan.devices
```

出力は次のようになります。

```text
net.wlan.devices: iwm0
```

次に続く `sysrc` の行では、必要に応じて `"iwm0"` を上記の `sysctl` コマンドの出力結果に置き換えてください。

```shell
# sysrc wlans_iwm0="wlan0"
# sysrc ifconfig_wlan0="WPA DHCP"
```

* 最後のステップとして、次のコマンドを実行して `netif` サービスを再起動します。

```shell
# service netif restart
```

<a id="basic-wireless-configuration"></a>
### 基本的な無線設定

この節では、無線ネットワークカードを設定するより詳しい例を示します。システムに搭載されている無線ネットワークカードを調べるには、[ネットワークアダプタの特定](#config-identify-network-adapter)の節を参照してください。

```shell
# ifconfig wlan0 create wlandev iwm0
```

再起動後も変更を維持するには、次のコマンドを実行します。

```shell
# sysrc wlans_iwm0="wlan0"
```

> **注**: 電波法規は世界の各地域で異なるため、使用可能なチャネルに関する正しい情報を得るには、現在地に適用されるリージョンドメインを正しく設定する必要があります。
>
> 利用可能な地域定義は `/etc/regdomain.xml` に記載されています。実行時にこれらの値を設定するには `ifconfig` を使います。

```shell
# ifconfig wlan0 regdomain etsi2 country AT
```

> 設定を永続化するには、`/etc/rc.conf` に追加します。

```shell
# sysrc create_args_wlan0="country AT regdomain etsi2"
```

<a id="scan-wireless-networks"></a>
### 無線ネットワークのスキャン

利用可能な無線ネットワークは `ifconfig(8)` を使ってスキャンできます。

無線ネットワークの一覧を表示するには、次のコマンドを実行します。

```shell
# ifconfig wlan0 up list scan
```

出力は次のようになります。

```text
SSID/MESH ID                      BSSID              CHAN RATE    S:N     INT CAPS
FreeBSD                           e8:d1:1b:1b:58:ae    1   54M  -47:-96   100 EP   RSN BSSLOAD HTCAP WPS WME
NetBSD                            d4:b9:2f:35:fe:08    1   54M  -80:-96   100 EP   RSN BSSLOAD HTCAP WPS WME
OpenBSD                           fc:40:09:c6:31:bd   36   54M  -94:-96   100 EPS  VHTPWRENV APCHANREP RSN WPS BSSLOAD HTCAP VHTCAP VHTOPMODE WME
GNU-Linux                         dc:f8:b9:a0:a8:e0   44   54M  -95:-96   100 EP   WPA RSN WPS HTCAP VHTCAP VHTOPMODE WME VHTPWRENV
Windows                           44:48:b9:b3:c3:ff   44   54M  -84:-96   100 EP   BSSLOAD VHTPWRENV HTCAP WME RSN VHTCAP VHTOPMODE WPS
MacOS                             46:48:b9:b3:c3:ff   44   54M  -84:-96   100 EP   BSSLOAD VHTPWRENV HTCAP WME RSN VHTCAP VHTOPMODE WPS
```

1. `SSID/MESH ID` はネットワークの名前を示します。
2. `BSSID` はアクセスポイントの MAC アドレスを示します。
3. `CAPS` フィールドは各ネットワークの種別と、そこで動作しているステーションの機能を示します（詳細は `ifconfig(8)` の `list scan` の定義を参照してください）。

<a id="wireless-authentication"></a>
### 無線ネットワークへの接続と認証

スキャンされたネットワークの一覧から無線ネットワークを選択したら、接続と認証を行う必要があります。大半の無線ネットワークでは、ルータに設定されたパスワードを使って認証を行います。それ以外の方式では、データ通信を開始する前に、事前共有鍵やシークレット、あるいは RADIUS などのバックエンドサービスを伴うより複雑な方式を用いて暗号ハンドシェイクを完了させる必要があります。

<a id="authenticate-wpa2-wpa-personal"></a>
#### WPA2/WPA/Personal による認証

無線ネットワークにおける認証処理は `wpa_supplicant(8)` によって管理されます。

`wpa_supplicant(8)` の設定は `/etc/wpa_supplicant.conf` ファイルに記述します。詳細は `wpa_supplicant.conf(5)` を参照してください。

無線ネットワークのスキャンを行って接続先のネットワークを選び、パスワード（PSK）を用意したら、次の例のように `/etc/wpa_supplicant.conf` ファイルへその情報を追加します。

```text
network={
        scan_ssid=1
        ssid="FreeBSD"
        psk="12345678"
}
```

1. `scan_ssid=1`: SSID スキャン手法を指定します。ネットワークが非公開（ステルス）の場合にのみ使用する必要があります。
2. `ssid`: ネットワーク名。
3. `psk`: 無線ネットワークのパスワード。

次のステップは、`/etc/rc.conf` ファイルで無線接続を設定することです。

静的アドレスを使用するには、次のコマンドを実行する必要があります。

```shell
# sysrc ifconfig_wlan0="inet 192.168.1.20 netmask 255.255.255.0"
```

動的アドレスを使用するには、次のコマンドを実行する必要があります。

```shell
# sysrc ifconfig_wlan0="WPA DHCP"
```

続いて、次のコマンドを実行してネットワークを再起動します。

```shell
# service netif restart
```

> **注**: より高度な認証方法を実行する手順の詳細は、[高度な無線認証（Wireless Advanced Authentication）](35-advanced-networking.md#network-advanced-wireless)を参照してください。

<a id="authenticate-open-networks"></a>
#### オープンネットワークへの認証

> **ヒント**: いかなる認証も行われないオープンネットワークに接続する際は、**十分に**注意することが重要です。

無線ネットワークのスキャンが完了し、接続する無線ネットワークの SSID を選んだら、次のコマンドを実行します。

```shell
# ifconfig wlan0 ssid SSID
```

その後、`dhclient(8)` を実行してアドレスを設定します。

```shell
# dhclient wlan0
```

<a id="chapter-07-heading-20"></a>
### 有線接続と無線接続の併用

有線接続は高いパフォーマンスと信頼性を提供し、無線接続は柔軟性と機動性を提供します。ノート PC のユーザーは通常、この 2 種類の接続の間をシームレスに切り替えられることを望みます。

FreeBSD では、2 つ以上のネットワークインターフェースを「フェイルオーバー」方式でまとめることができます。この構成では、ネットワークインターフェースのグループから最も優先度が高く利用可能な接続を使用し、リンク状態が変化するとオペレーティングシステムが自動的に切り替えます。

リンクアグリゲーションとフェイルオーバーについては[リンクアグリゲーションとフェイルオーバー（Link Aggregation and Failover）](35-advanced-networking.md#network-aggregation)で解説しており、有線接続と無線接続を併用する例は[イーサネットインターフェースと無線インターフェース間のフェイルオーバーモード（Failover Mode Between Ethernet and Wireless Interfaces）](35-advanced-networking.md#networking-lagg-wired-and-wireless)にあります。

<a id="hostname"></a>
## ホスト名

ホスト名は、ネットワーク上におけるホストの完全修飾ドメイン名（FQDN: Fully Qualified Domain Name）を表します。

> **ヒント**: ホストにホスト名が設定されていない場合、FreeBSD は自分自身を `Amnesiac` と呼びます。

<a id="get-hostname"></a>
### 現在のホスト名の確認

現在のホスト名を確認するには `hostname(1)` を使います。

```shell
$ hostname
```

出力は次のようになります。

```text
freebsdhostname.example.com
```

<a id="change-hostname"></a>
### ホスト名の変更

ホストのホスト名を変更し、再起動後も維持するには、次のコマンドを実行します。

```shell
# sysrc hostname="freebsdhostname.example.com"
```

<a id="dns"></a>
## DNS

DNS は、IP アドレスをホスト名へ、またその逆へと対応付ける[電話帳](https://en.wikipedia.org/wiki/Telephone_directory)のようなものとして理解できます。

FreeBSD システムが DNS とどのようにやり取りするかを扱うファイルは 3 つあります。`hosts(5)`、`resolv.conf(5)`、`nsswitch.conf(5)` です。

`/etc/nsswitch.conf` ファイルで特に指定されていない限り、FreeBSD はまず `/etc/hosts` ファイルのアドレスを参照し、次に `/etc/resolv.conf` ファイルの DNS 情報を参照します。

> **注**: `nsswitch.conf(5)` ファイルは、nsdispatch（name-service switch dispatcher）がどのように動作すべきかを指定します。
>
> デフォルトでは、`/etc/nsswitch.conf` ファイルの `hosts` 行は次のようになっています。

```text
hosts: files dns
```

> たとえば `nscd(8)` サービスを使用する場合は、次のように記述して優先順位を変更できます。

```text
hosts: files cache dns
```

<a id="local-addresses"></a>
### ローカルアドレス

`/etc/hosts` ファイルは、ホスト名と IP アドレスの対応付けを提供するシンプルなテキストデータベースです。LAN 経由で接続されたローカルコンピュータのエントリをこのファイルに追加することで、DNS サーバを構築せずに簡易的な名前解決を行うことができます。さらに、`/etc/hosts` を使ってインターネット上の名前のローカル記録を用意しておけば、頻繁にアクセスする名前について外部 DNS サーバへ問い合わせる必要を減らせます。

たとえば、ローカル環境に `www/gitlab-ce` のローカルインスタンスがある場合、`/etc/hosts` ファイルに次のように追加できます。

```text
192.168.1.150 git.example.com git
```

<a id="configuring-nameserver"></a>
### ネームサーバの設定

FreeBSD システムがインターネットのドメインネームシステム（DNS）へどのようにアクセスするかは `resolv.conf(5)` によって制御されます。

`/etc/resolv.conf` で最もよく使われるエントリは次のとおりです。

| エントリ | 説明 |
|---|---|
| `nameserver` | リゾルバが問い合わせるネームサーバの IP アドレス。記述した順に最大 3 台まで問い合わせが行われる。 |
| `search` | ホスト名検索時の検索リスト。通常はローカルホスト名のドメインによって決まる。 |
| `domain` | ローカルドメイン名。 |

典型的な `/etc/resolv.conf` は次のようになります。

```text
search example.com
nameserver 147.11.1.11
nameserver 147.11.100.30
```

> **注**: `search` と `domain` のオプションは、どちらか一方のみを使用してください。

DHCP を使用している場合、`dhclient(8)` は通常、DHCP サーバから受け取った情報で `/etc/resolv.conf` を書き換えます。

> **ヒント**: 設定を行っているマシンが DNS サーバでは**ない**場合、`local-unbound(8)` を使うと DNS の名前解決性能を向上させることができます。
>
> 起動時に有効にするには、次のコマンドを実行します。

```shell
# sysrc local_unbound_enable="YES"
```

> `local-unbound(8)` サービスを開始するには、次のコマンドを実行します。

```shell
# service local_unbound start
```

<a id="troubleshooting"></a>
## トラブルシューティング

ハードウェアやソフトウェアの設定でトラブルシューティングを行うときは、まず基本的な点から確認してください。

* ネットワークケーブルは接続されているか？
* ネットワークサービスは正しく設定されているか？
* ファイアウォールは正しく設定されているか？
* NIC は FreeBSD でサポートされているか？
* ルータは正常に動作しているか？

> **ヒント**: バグ報告を送る前には、必ず [FreeBSD リリースページ](https://www.freebsd.org/releases/)のハードウェアノートを確認し、FreeBSD のバージョンを最新の STABLE 版へ更新し、メーリングリストアーカイブの確認とインターネット検索を行ってください。

<a id="wired-troubleshooting"></a>
### 有線ネットワークのトラブルシューティング

カードが動作しているにもかかわらず性能が低い場合は、`tuning(7)` を通読してください。また、誤ったネットワーク設定が通信速度の低下を引き起こすこともあるため、ネットワーク設定も確認してください。

`No route to host` メッセージは、システムが宛先ホストへパケットをルーティングできない場合に発生します。これは、デフォルトルートが指定されていない場合や、ケーブルが抜けている場合に起こります。`netstat -rn` の出力を確認し、そのホストへの有効な経路があることを確かめてください。有効な経路がない場合は、[ゲートウェイと経路（Gateways and Routes）](35-advanced-networking.md#network-routing)を参照してください。

`ping: sendto: Permission denied` エラーメッセージは、多くの場合ファイアウォールの設定ミスが原因です。FreeBSD でファイアウォールが有効になっているのにルールが一切定義されていない場合、デフォルトポリシーはすべてのトラフィック（`ping(8)` を含む）を拒否します。詳しくは[ファイアウォール（Firewalls）](34-firewalls.md#firewalls)を参照してください。

<a id="wireless-troubleshooting"></a>
### 無線ネットワークのトラブルシューティング

この節では、一般的な無線ネットワークの問題を切り分けるための手順をいくつか説明します。

* スキャンしてもアクセスポイントが一覧に表示されない場合は、設定によって無線デバイスの使用チャネルが狭い範囲に制限されていないか確認してください。
* デバイスがアクセスポイントとアソシエートできない場合は、設定がアクセスポイント側の設定と一致しているか確認してください。これには認証方式や各種セキュリティプロトコルも含まれます。設定はできるだけ単純にしてください。WPA2 や WPA などのセキュリティプロトコルを使用している場合は、いったんアクセスポイントをオープン認証かつセキュリティなしに設定し、トラフィックが通るか確認してみてください。
* システムがアクセスポイントとアソシエートできるようになったら、`ping(8)` などのツールを使ってネットワーク設定を診断します。
* より低レベルなデバッグツールも数多くあります。802.11 プロトコルサポート層のデバッグメッセージは、`wlandebug(8)` を使って有効にできます。
