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
