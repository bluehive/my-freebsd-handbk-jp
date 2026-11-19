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
