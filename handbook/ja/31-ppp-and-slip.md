<a id="ppp-and-slip"></a>
# 第31章 PPP

> **注（ドラフト）**: 本ファイルは意訳作業中のドラフトです。全節の翻訳および原文照合・自己校正が完了するまでドラフト扱いとします。

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/ppp-and-slip/)の「Chapter 31. PPP」（既存 TOC ID 30）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/ppp-and-slip/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` は一般ユーザーのプロンプトを示します。

<a id="ppp-and-slip-synopsis"></a>
## 概要

FreeBSD は、ダイヤルアップモデムを使ってネットワーク接続やインターネット接続を確立できる Point-to-Point プロトコル（PPP）をサポートしています。本章では、FreeBSD でモデムを用いた通信サービスを設定する方法を説明します。

本章を読むと、次の内容を学べます。

* PPP 接続の設定・利用・トラブルシューティングの方法
* PPP over Ethernet（PPPoE）のセットアップ方法
* PPP over ATM（PPPoA）のセットアップ方法

本章を読む前に、次の内容を理解しておいてください。

* 基本的なネットワーク用語に慣れていること
* ダイヤルアップ接続と PPP の基本および目的を理解していること
