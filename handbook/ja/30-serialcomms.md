<a id="serialcomms"></a>
# 第30章 シリアル通信（Serial Communications）

> **訳注（ドラフト）**: 本章は現在意訳作業中です。全節の翻訳および原文との突き合わせ校正が完了するまでドラフト扱いです。

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/serialcomms/)の「Chapter 30. Serial Communications」（既存 TOC ID 29）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/serialcomms/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` は一般ユーザーのプロンプトを示します。

<a id="serial-synopsis"></a>
## 概要

UNIX® では、最初期の UNIX® マシンがユーザーの入出力にシリアル回線を利用していたことから、常にシリアル通信をサポートしてきました。一般的な端末が毎秒 10 文字のシリアルプリンタとキーボードで構成されていた時代から、状況は大きく変わりました。本章では、FreeBSD でシリアル通信を利用するいくつかの方法を説明します。

本章を読むと、次の内容を学べます。

* FreeBSD システムに端末を接続する方法
* モデムを使ってリモートホストへダイヤルアウトする方法
* モデム経由でリモートユーザーが FreeBSD システムへログインできるようにする方法
* シリアルコンソールから FreeBSD システムを起動する方法

本章を読む前に、次の準備を整えておいてください。

* [カスタムカーネルを設定してインストールする方法](09-kernelconfig.md#kernelconfig)を理解しておくこと
* [FreeBSD のパーミッションとプロセス](03-basics.md#basics)を理解しておくこと
* FreeBSD で使用するシリアルハードウェアの技術マニュアルを手元に用意しておくこと
