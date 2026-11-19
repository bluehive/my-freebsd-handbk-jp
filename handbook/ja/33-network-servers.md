<a id="network-servers"></a>
# 第33章 ネットワークサーバ（Network Servers）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/network-servers/)の「Chapter 33. Network Servers」を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/network-servers/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。本ファイルは章単位の作業中ドラフトであり、コマンド例・設定例は原文のまま保持しています（実機検証・第三者専門校閲は未実施）。

<a id="network-servers-synopsis"></a>
## 概要（Synopsis）

この章では、UNIX® システムでよく使われる代表的なネットワークサービスについて、インストール・設定・動作確認・運用の手順を解説します。本文中には、設定例となるファイルもあわせて掲載しています。

この章を読み終えると、次のことがわかるようになります。

* `inetd` デーモンの管理方法
* Network File System（NFS）の構築方法
* ユーザーアカウントを一元管理・共有するための Network Information Server（NIS）の構築方法
* FreeBSD を LDAP サーバまたはクライアントとして構成する方法
* DHCP を使ったネットワーク設定の自動割り当て方法
* Domain Name Server（DNS）の構築方法
* Apache HTTP Server の構築方法
* File Transfer Protocol（FTP）サーバの構築方法
* Samba を使った Windows® クライアント向けファイル／プリントサーバの構築方法
* Network Time Protocol（NTP）を使った日時同期とタイムサーバの構築方法
* iSCSI の構築方法

この章を読むにあたっては、次の基本的な知識を前提としています。

* `/etc/rc` スクリプトの仕組み
* ネットワークの基本用語
* サードパーティ製ソフトウェアの追加インストール方法（[アプリケーションの導入: Packages と Ports](04-ports.md#ports)）
