<a id="geom"></a>
# 第22章 GEOM: モジュラーディスク変換フレームワーク（GEOM: Modular Disk Transformation Framework）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/geom/)の「Chapter 22. GEOM: Modular Disk Transformation Framework」（既存 TOC ID 21）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/geom/_index.adoc`）に基づいて日本語へ意訳したものです。（※作業中ドラフト）

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` は一般ユーザーのプロンプトを示します。

<a id="geom-synopsis"></a>
## 概要

FreeBSD の GEOM フレームワークは、プロバイダ（`/dev` 配下のディスクデバイス）を通じて、マスターブートレコード（MBR）や BSD ラベルなどのクラスへのアクセスと制御を可能にします。GEOM はさまざまなソフトウェア RAID 構成に対応しており、OS やシステムユーティリティに対して透過的なアクセスを提供します。

本章では、FreeBSD の GEOM フレームワーク配下でディスクを扱う方法を説明します。対象には、構成管理にこのフレームワークを利用する主要な RAID 制御ユーティリティも含まれます。本章は RAID 構成全般の網羅的な解説ではなく、GEOM が対応している RAID の分類のみを扱います。

本章を読むと、次の内容を学べます。

* GEOM を通じて利用できる RAID の種類
* ベースユーティリティを使って各種 RAID レベルを構成・保守・操作する方法
* GEOM を通じてディスクデバイスのミラーリング、ストライピング、暗号化、リモート接続を行う方法
* GEOM フレームワークに接続されたディスクのトラブルシューティング方法

本章を読む前に、次の内容を理解しておいてください。

* FreeBSD がディスクデバイスをどのように扱うか（[Storage](21-disks.md#disks)）
* 新しいカーネルを設定してインストールする方法（[FreeBSD カーネルの設定](09-kernelconfig.md#kernelconfig)）

<a id="geom-striping"></a>
## RAID0 - ストライピング

ストライピングは、複数のディスクドライブを 1 つのボリュームにまとめる手法です。ハードウェア RAID コントローラを使って実行することもできますが、GEOM ディスクサブシステムは、RAID ディスクコントローラを使わずに RAID0 とも呼ばれるディスクストライピングをソフトウェアでサポートしています。

RAID0 では、データをブロックに分割してアレイ内のすべてのドライブへ分散して書き込みます。次の図のように、1 台のディスクに 256k を書き込むのを待つ代わりに、アレイ内の 4 台のディスクそれぞれへ 64k ずつ同時に書き込めるため、優れた I/O 性能が得られます。複数のディスクコントローラを併用すると、この性能をさらに引き上げることができます。

![ディスクストライピングの図解](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/geom/striping.png)

RAID0 ストライプでは、I/O リクエストをインターリーブして複数ディスクへ並列に読み書きするため、すべてのディスクが同じサイズでなければなりません。

> **注**: RAID0 には**冗長性がありません**。つまり、アレイ内のディスクが 1 台でも故障すると、ディスク上のデータはすべて失われます。重要なデータを扱う場合は、リモートのシステムやデバイスへ定期的にバックアップを保存する運用を用意してください。

汎用ディスクを使い、FreeBSD システム上に GEOM ベースのソフトウェア RAID0 を作成する手順は次のとおりです。ストライプの作成後、既存のストライプを操作する方法の詳細は `gstripe(8)` を参照してください。

**手順: 未フォーマットの ATA ディスクでストライプを作成する**

1. `geom_stripe.ko` モジュールを読み込みます。

```shell
# kldload geom_stripe
```

2. 適切なマウントポイントがあることを確認します。このボリュームをルートパーティションにする場合は、一時的に `/mnt` などの別のマウントポイントを使います。
3. ストライプ化するディスクのデバイス名を確認し、新しいストライプデバイスを作成します。たとえば、未使用かつ未パーティションの 2 台の ATA ディスク `/dev/ad2` と `/dev/ad3` をストライプ化する場合は次のようにします。

> **訳注**: 例中の `/dev/ad2`・`/dev/ad3` は旧来の ATA ドライバに基づくデバイス名です。近年の FreeBSD（CAM ベースの ATA ドライバ）では `ada2` のように `adaX` として認識されますが、コマンド例は固定原文のまま保持しています。

```shell
# gstripe label -v st0 /dev/ad2 /dev/ad3
Metadata value stored on /dev/ad2.
Metadata value stored on /dev/ad3.
Done.
```

4. 新しいボリュームに標準ラベル（パーティションテーブル）を書き込み、デフォルトのブートストラップコードをインストールします。

```shell
# bsdlabel -wB /dev/stripe/st0
```

5. この処理により、`/dev/stripe` 内に `st0` に加えて `st0a` と `st0c` の 2 つのデバイスが作成されます。この段階で、`newfs` を使って `st0a` 上に UFS ファイルシステムを作成できます。

```shell
# newfs -U /dev/stripe/st0a
```

   画面に多くの数値が流れたあと、数秒で処理が完了します。これでボリュームが作成され、マウントできる状態になります。

6. 作成したディスクストライプを手動でマウントするには次のようにします。

```shell
# mount /dev/stripe/st0a /mnt
```

7. 起動時にこのストライプファイルシステムを自動マウントするには、`/etc/fstab` にボリューム情報を記述します。次の例では、`stripe` という名前の恒久的なマウントポイントを作成しています。

```shell
# mkdir /stripe
# echo "/dev/stripe/st0a /stripe ufs rw 2 2" \
>> /etc/fstab
```

8. システム初期化時に `geom_stripe.ko` モジュールを自動読み込みするため、`/boot/loader.conf` に次の行を追加します。

```shell
# echo 'geom_stripe_load="YES"' >> /boot/loader.conf
```
