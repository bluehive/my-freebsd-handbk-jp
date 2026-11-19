<a id="dtrace"></a>
# 第28章 DTrace

> **ドラフト**: 本ファイルは翻訳作業中のドラフトです。全節の翻訳および自己校正が完了するまで仮の状態です。

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/dtrace/)の「Chapter 28. DTrace」（既存 TOC ID 27）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/dtrace/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザーのプロンプトを示します。

<a id="dtrace-synopsis"></a>
## 概要

DTrace（Dynamic Tracing：動的トレース）は、本番環境や本番前環境（pre-production）のシステムにおいて性能ボトルネックを特定するためのツールとして、Sun™ によって開発されました。性能上の問題の診断に加えて、DTrace は FreeBSD カーネルおよびユーザーランドプログラム双方で発生する予期しない動作の調査やデバッグにも利用できます。

DTrace は、システム上の問題を診断するための豊富な機能を備えた優れたプロファイリングツールです。あらかじめ用意されたスクリプトを実行してその機能を活用することもできます。また、ユーザー自身が DTrace の D 言語を使って独自のユーティリティを作成し、具体的なニーズに合わせてプロファイリングをカスタマイズすることも可能です。

FreeBSD の実装では、カーネル DTrace を完全にサポートしており、ユーザーランド DTrace についても実験的なサポートを提供しています。ユーザーランド DTrace を使うと、`pid` プロバイダによってユーザーランドプログラムの関数境界トレース（function boundary tracing）を行ったり、後からトレースできるようにユーザーランドプログラムへ静的プローブを埋め込んだりできます。`databases/postgresql12-server` や `lang/php74` など一部の port には、静的プローブを有効にするための DTrace オプションが用意されています。

DTrace の公式ガイドは、illumos プロジェクトによって [illumos Dynamic Tracing Guide](https://illumos.org/books/dtrace/bookinfo.html) として保守されています。

本章を読むと、次の内容を学べます。

* DTrace とは何か、どのような機能を提供するのか
* Solaris™ の DTrace 実装と FreeBSD が提供する実装との違い
* FreeBSD で DTrace を有効にして使用する方法

本章を読む前に、次の内容を理解しておいてください。

* UNIX® と FreeBSD の基本（[FreeBSD の基本](03-basics.md#basics)）
* セキュリティおよび FreeBSD におけるセキュリティの扱いについての基礎知識（[セキュリティ](15-security.md#security)）

<a id="dtrace-implementation"></a>
## 実装の違い

FreeBSD の DTrace は Solaris™ のものと似ていますが、いくつかの違いがあります。最大の違いは、FreeBSD では DTrace が一連のカーネルモジュールとして実装されており、モジュールを読み込むまで DTrace を使用できない点です。必要なモジュールをすべて読み込むには、次のように実行します。

```shell
# kldload dtraceall
```

FreeBSD 10.0-RELEASE 以降では、`dtrace(1)` を実行するとモジュールが自動的に読み込まれます。

FreeBSD では、カーネルモジュールおよびカーネル本体から `ctf(5)` データを読み込む機能を有効にするために、`DDB_CTF` カーネルオプションを使用します。`CTF` は Solaris™ の Compact C Type Format であり、`DWARF` や古くからある stabs に似た簡略化デバッグ情報を格納する形式です。`CTF` データは、`ctfconvert(1)` および `ctfmerge(1)` というビルドツールによってバイナリに付加されます。`ctfconvert` ユーティリティはコンパイラが生成した `DWARF` の `ELF` デバッグセクションを解析し、`ctfmerge` はオブジェクトファイル群の `CTF` `ELF` セクションを実行ファイルまたは共有ライブラリへ統合します。

FreeBSD には Solaris™ とは異なるプロバイダも存在します。最も注目すべきは `dtmalloc` プロバイダで、FreeBSD カーネル内で型ごとに `malloc(9)` をトレースできます。一方で、Solaris™ にあるプロバイダの一部（`cpc` など）は FreeBSD には存在しませんが、今後の FreeBSD のバージョンで追加される可能性があります。さらに、両方の OS で利用できるプロバイダであっても、プローブの引数の型が異なるという意味で互換性がない場合があります。そのため、Solaris™ で書かれた `D` スクリプトは FreeBSD 上で無修正のまま動作するとは限らず、その逆も同様です。

セキュリティ上の違いにより、FreeBSD では `root` のみが DTrace を使用できます。Solaris™ には FreeBSD にまだ実装されていない低レベルのセキュリティチェックがいくつか備わっています。そのため、`/dev/dtrace/dtrace` へのアクセスは厳格に `root` に限定されています。

DTrace は Common Development and Distribution License（`CDDL`）ライセンスの下で提供されています。FreeBSD 上でこのライセンスを確認するには、`/usr/src/cddl/contrib/opensolaris/OPENSOLARIS.LICENSE` を参照するか、オンラインの [https://opensource.org/licenses/CDDL-1.0](https://opensource.org/licenses/CDDL-1.0) をご覧ください。DTrace サポートを含む FreeBSD カーネル自体は `BSD` ライセンスですが、モジュールがバイナリ形式で配布される場合や、バイナリが読み込まれる場合には `CDDL` が適用されます。

<a id="dtrace-enable"></a>
## DTrace サポートの有効化

FreeBSD 9.2 および 10.0 では、DTrace サポートは `GENERIC` カーネルにあらかじめ組み込まれています。それ以前のバージョンの FreeBSD を使用している場合や、DTrace サポートをカーネルに静的に組み込みたい場合は、カスタムカーネル設定ファイルに次の行を追加し、[FreeBSD カーネルのコンフィギュレーション](09-kernelconfig.md#kernelconfig)の手順に従ってカーネルを再コンパイルしてください。

```
options         KDTRACE_HOOKS
options         DDB_CTF
makeoptions	DEBUG=-g
makeoptions	WITH_CTF=1
```

AMD64 アーキテクチャを使用している場合は、次の行も追加してください。

```
options         KDTRACE_FRAME
```

このオプションは `dtrace_fbt(4)` のサポートを提供します。このオプションがなくても DTrace は動作しますが、関数境界トレースのサポートは制限されます。

新しいカーネルで FreeBSD システムを再起動するか、`kldload dtraceall` を使って DTrace カーネルモジュールを読み込んだら、システム情報を収集するための既製スクリプト集である最新の DTrace Toolkit（`sysutils/dtrace-toolkit`）をインストールします。ここには、開いているファイル、メモリ、CPU 使用率などを確認するためのスクリプトが多数含まれています。FreeBSD のベースシステムにもいくつかのスクリプトが含まれており、`/usr/share/dtrace` で確認できます。

> **注**: `/usr/share/dtrace` にあるスクリプトは、FreeBSD 向けに特別に移植されたものです。DTrace Toolkit に含まれるスクリプトのすべてが FreeBSD でそのまま動作するわけではなく、FreeBSD 上で動作させるために手直しが必要なものもあります。

DTrace Toolkit には、DTrace 専用の言語で書かれたスクリプトが多数含まれています。この言語は D 言語と呼ばれ、C++ によく似ています。この言語の詳しい解説は本書の範囲を超えています。FreeBSD 上での D 言語の概要については、FreeBSD の `d(7)` man ページを参照してください。また、D 言語は [illumos Dynamic Tracing Guide](https://www.illumos.org/books/dtrace/bookinfo.html) でも詳しく解説されています。

<a id="dtrace-out-of-kernel"></a>
## カーネル外モジュールでの DTrace 有効化

開発やデバッグに役立つよう、カーネル外モジュール（out-of-kernel module）に DTrace サポートを追加するには、そのモジュールの Makefile に次の行を含めます。

```
CFLAGS+= -DKDTRACE_HOOKS
```

このフラグはコンパイル時に DTrace フックを有効にし、モジュールの高度なデバッグや監視を可能にします。DTrace 機能を有効にするため、この変更を行った後に必ずモジュールを再コンパイルしてください。
