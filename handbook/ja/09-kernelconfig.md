<a id="kernelconfig"></a>
# 第9章 FreeBSDカーネルの設定

> **状態:** 意訳ドラフト。固定原文の全節・コマンド・設定例を照合しています。FreeBSD上でのビルド・起動・復旧試験は未実施です。
> **原文:** [Configuring the FreeBSD Kernel](https://docs.freebsd.org/en/books/handbook/kernelconfig/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/09-kernelconfig.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **章番号:** 本リポジトリでは第9章、固定上流では第10章です。
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

原文は本章の操作をrootで行うものとしています。設定・ビルド・導入には管理者権限が必要です。コードや古い機器の表示例は原文を保持しており、実際のアーキテクチャとOSのソースに合わせます。

<a id="kernelconfig-synopsis"></a>
## この章で行うこと

カーネルはFreeBSDの中心で、メモリ、セキュリティ、ネットワーク、ディスクアクセスなどを管理します。多くは動的に設定できますが、独自カーネルが必要な場合もあります。

この章では、独自ビルドが必要になる条件、ハードウェアの調査、設定ファイルの変更、ビルドと導入、問題発生時の復旧を説明します。

<a id="kernelconfig-custom-kernel"></a>
## 独自カーネルが必要かを考える

従来のカーネルは対応デバイスを大きな1つのプログラムに固定し、変更にはビルドと再起動が必要でした。現在は多くの機能を必要に応じて読み込み・取り外しできるモジュールとして提供し、動作中にハードウェアや機能を追加できます。

それでも、カーネルへ密接に結び付いた機能や、モジュールの読み込みを認めないセキュリティ環境では、静的に組み込む設定が必要になる場合があります。

広い機種を支えるGENERICから、自分の機器に必要なものだけへ絞ると、次の利点が得られる場合があります。

- 検出対象が減り、起動が速くなる。
- 未使用の機能・ドライバーを省き、常駐するカーネルのメモリを減らせる。RAMの少ない環境では特に意味がある。
- GENERICにないデバイス対応を追加できる。

> **警告:** 独自構成はGENERICほど広く試験されていません。ビルドや実行時の問題が増える場合があります。明確な理由があり、必要なら調査・デバッグできる経験者向けの作業です。

ビルドする前に、目的の機能が既存のモジュールにないかを確認します。多くのドライバーは `/boot/kernel` にモジュールがあり、`kldload(8)` で動的に読み込めます。対応するmanページにも案内があります。ath無線ドライバーの原文の抜粋です。

```text
Alternatively, to load the driver as a module at boot time, place the
following line in man:loader.conf[5]:

    if_ath_load="YES"
```

つまり `/boot/loader.conf` に `if_ath_load="YES"` を入れると起動時に読み込めます。サブシステムによっては対応モジュールがなく、静的な設定が必要です。

<a id="kernelconfig-devices"></a>
## ハードウェアを一覧にする

設定を削る前に、搭載機器を調べます。デュアルブートなら他OSのデバイスマネージャーなども利用できます。Windowsの版によってはSystemアイコンから開けます。

FreeBSDだけなら、`dmesg(8)` で起動時に検出した機器を確認します。各ドライバーのmanページには対応ハードウェアが記載されています。psmがマウスを検出した原文例です。

```text
psm0: <PS/2 Mouse> irq 12 on atkbdc0
psm0: [GIANT-LOCKED]
psm0: [ITHREAD]
psm0: model Generic PS/2 mouse, device ID 0
```

実際に使う機器なので、このドライバーを設定から削除しないようにします。dmesgから起動時の内容が流れてしまっていれば `/var/run/dmesg.boot` を読みます。

`pciconf(8)` はより詳しい情報を表示します。

```shell
% pciconf -lv
ath0@pci0:3:0:0:        class=0x020000 card=0x058a1014 chip=0x1014168c rev=0x01 hdr=0x00
    vendor     = 'Atheros Communications Inc.'
    device     = 'AR5212 Atheros AR5212 802.11abg wireless'
    class      = network
    subclass   = ethernet
```

例ではathがAtherosの無線デバイスを認識しています。機器名・メーカー名に対応するmanページを探すには `man -k` も使えます。

```shell
# man -k Atheros
ath(4)                   - Atheros IEEE 802.11 wireless network driver
ath_hal(4)               - Atheros Hardware Access Layer (HAL)
```

調査した一覧を手元に置き、必要なドライバーを削除しないよう照合しながら編集します。

<a id="kernelconfig-config"></a>
## カーネル設定ファイルを作る

完全なFreeBSDソースツリーが必要です。`/usr/src` がない、または空なら、[Gitによるソース取得](https://docs.freebsd.org/en/books/handbook/mirrors/#git)を行います。

`/usr/src/sys` にはアーキテクチャ別のディレクトリと、共通のコードがあります。各アーキテクチャのconf配下にGENERICがあります。原文はamd64・i386・powerpc・sparc64を例に挙げていますが、実際の対応構成は利用するソース版に従います。

**GENERICは直接編集せず、別名へコピー**します。名前は大文字にする慣例があり、複数機種を管理するならホスト名を使うと区別しやすくなります。amd64でMYKERNELを作る例です。

```shell
# cd /usr/src/sys/amd64/conf
# cp GENERIC MYKERNEL
```

viや、初心者にも扱いやすいeeなどのASCIIテキストエディターで編集できます。各行はデバイス／サブシステムのキーワード、引数、説明からなり、`#` 以降はコメントです。行頭へ `#` を付けると、その対応を外せます。意味が分からない行の有効・無効を変えないでください。

> **警告:** 必要な機能を外すと起動できなくなります。たとえばATAディスクのシステムでataドライバーを消す場合などです。判断できなければ残します。

詳しい説明は、そのアーキテクチャのGENERICと同じ場所のNOTES、および共通の `/usr/src/sys/conf/NOTES` にあります。

完成した設定は `/usr/src` の外にも保存します。別の場所で保管し、confからシンボリックリンクを張る方法もあります。

```shell
# cd /usr/src/sys/amd64/conf
# mkdir /root/kernels
# cp GENERIC /root/kernels/MYKERNEL
# ln -s /root/kernels/MYKERNEL
```

小さな追加だけなら、`include` でGENERICを読み込み、差分だけを保つ方法もあります。

```text
include GENERIC
ident MYKERNEL

options         IPFIREWALL
options         DUMMYNET
options         IPFIREWALL_DEFAULT_TO_ACCEPT
options         IPDIVERT
```

これならGENERICに追加された機能も継承します。除外する項目は `nooptions` や `nodevice` で指定します。ディレクティブの一覧は `config(5)` を参照してください。

全オプションを含むファイルを生成する原文例です。`arch` は実際のアーキテクチャ、たとえばamd64へ置き換えます。

```shell
# cd /usr/src/sys/arch/conf && make LINT
```

<a id="kernelconfig-building"></a>
## ビルドして導入する

設定を保存したら、次の順で進めます。

1. ソースツリーの先頭へ移動します。

```shell
# cd /usr/src
```

2. 作成した設定名を指定してビルドします。

```shell
# make buildkernel KERNCONF=MYKERNEL
```

3. 同じ設定名で導入します。

```shell
# make installkernel KERNCONF=MYKERNEL
```

新カーネルは `/boot/kernel/kernel`、元のカーネルは `/boot/kernel.old/kernel` に置かれます。正しく終了・再起動して新カーネルを使います。失敗した場合は[起動できないとき](#kernelconfig-noboot)を参照します。

通常は全カーネルモジュールも再ビルドします。必要ならビルド前に `/etc/make.conf` で対象を絞れます。次は列挙したモジュールだけを作る設定です。

```text
MODULES_OVERRIDE = linux acpi
```

次は列挙したものを除外します。

```text
WITHOUT_MODULES = linux acpi sound
```

次はモジュールを作らず、カーネル本体だけを作ります。

```text
NO_MODULES = yes
```

`graphics/drm-kmod` や `emulators/virtualbox-ose-kmod` などPorts側のモジュールもカーネルインターフェースへ依存します。`PORTS_MODULES` を指定すると、カーネルを作るたびに対象portも新しいソースに合わせて再ビルドできます。カーネルとPortsのツリーは併せて更新することを原文は勧めています。

```text
PORTS_MODULES = drm-kmod virtualbox-ose-kmod
```

これらは目的に応じて選ぶ設定例です。ほかの変数は `make.conf(5)` を参照してください。

<a id="kernelconfig-trouble"></a>
## 問題が起きたとき


主に4つのケースがあります。

**configが失敗する**

問題の行番号が出ます。次の例なら17行目をGENERICやNOTESと比較し、入力を確認します。

```text
config: line 17: syntax error
```

**makeが失敗する**

configでは見つからない設定上の問題などが考えられます。設定を見直し、不明なら構成ファイルを添えて [freebsd-questions](https://lists.freebsd.org/)で相談できます。

<a id="kernelconfig-noboot"></a>

**カーネルが起動しない・機器を認識しない**

ブートメニューの `Escape to a loader prompt` へ入り、`boot kernel.old`、または動作が確認できている別のカーネル名を指定して起動します。起動できたら設定を見直して作り直します。`/var/log/messages` は成功した各起動の記録、dmesgは現在の起動の記録として役立ちます。

動くカーネル、たとえばGENERICを必ず残します。新しいカーネルを導入するたびにkernel.oldは直前のものへ上書きされるため、それが起動可能とは限りません。

原文は動作する版のディレクトリを名前で保全・復元する例として次を示しています。

```shell
# mv /boot/kernel /boot/kernel.bad
# mv /boot/kernel.good /boot/kernel
```

> **訳注:** `/boot/kernel.good` は、既に動作確認済みのカーネルをその名前で保存してある場合の例です。この章の前の手順だけで自動作成される名前ではありません。存在と中身を確かめずに、そのまま移動する手順ではありません。

**カーネルは動くがpsなどが動かない**

カーネルとシステムのユーティリティを異なる版のソースから作ると、psやvmstatなどが動かない場合があります。たとえばRELEASEのシステムへCURRENTのカーネルだけを入れる場合です。[同じソース版からworldを作り直す](https://docs.freebsd.org/en/books/handbook/cutting-edge/#makeworld)必要があります。カーネルとOSの残りを異なる版で運用することは勧められません。
