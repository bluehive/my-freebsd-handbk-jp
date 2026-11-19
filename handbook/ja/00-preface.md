<a id="book-preface"></a>
# 序文（Preface）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/)の「Preface」を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/preface/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::`（`shared/authors.adoc`、`shared/mirrors.adoc`、`shared/releases.adoc`、`attributes`、`teams.adoc`、`mailing-lists.adoc`、`urls.adoc`、`asciidoctor.adoc`）は翻訳対象外とし、本文の節のみを意訳しています。また、本リポジトリで未翻訳の章やアンカー未整備のドラフト章（第15章 Security など）への相互参照は、公式 FreeBSD Handbook（英語版）の該当ページへリンクしています。

<a id="preface-audience"></a>
## 想定読者（Intended Audience）

FreeBSD を初めて使う方は、本書の最初の部（Part）を通じてインストール手順を順を追って学びながら、UNIX® を支える基本的な考え方や慣習を無理なく身に付けることができます。
この部を読み進めるのに特別な前提知識はほとんど不要で、探求したいという意欲と、新しい概念が出てくるたびにそれを受け入れる力があれば十分です。

そこまで読み終えた先にある本書の後半（はるかに大部な部分）は、FreeBSD システム管理者が関心を寄せるあらゆる話題を網羅した総合リファレンスになっています。
章によっては事前に読んでおくべき資料を推奨している場合があり、その内容は各章冒頭の概要（Synopsis）に記載されています。

その他の情報源の一覧については、[参考文献（Bibliography）](https://docs.freebsd.org/en/books/handbook/bibliography/#bibliography)を参照してください。

<a id="preface-changes-from4"></a>
## 第四版以降の改訂（Fourth Edition）

現在の Handbook は、すべての内容を点検・更新してきたワーキンググループの継続的な取り組みの集大成です。
Handbook 第四版以降の主な変更点は次のとおりです。

* Handbook のソース形式を [DocBook](https://docbook.org/) から [Hugo](https://gohugo.io/) と [AsciiDoctor](https://asciidoctor.org/) へ移行しました。
* [FreeBSD Documentation Portal](https://docs.FreeBSD.org) を新設しました。
* [第1章 はじめに（Introduction）](01-introduction.md#introduction)を更新し、FreeBSD の歴史の記述を改善して細かな誤記を修正しました。
* [FreeBSDのインストール（Install）](02-bsdinstall.md#bsdinstall)を更新し、概要（Synopsis）の刷新、インストーラの最新変更の反映、画像の更新と代替テキスト（alt text）の追加、特定バージョン番号への言及の削除を行いました。
* [FreeBSDの基本（Basics）](03-basics.md#basics)の表、コマンド出力例、および `hier(7)` に沿ったディレクトリ構造の記述を更新しました。
* [パッケージとPorts（Ports）](04-ports.md#ports)を更新し、パッケージ検索の説明を簡素化しました。ソフトウェア例も刷新し（Apache を Nginx に置き換え）、`pkg(8)` のブートストラップ手順を改善したほか、パッケージのロック・ロック解除を含む設定・管理手順を追加しました。
* [X Window System（X11）](05-x11.md#x11)を更新し、FreeBSD におけるグラフィックスの現状を反映しました。古い Intel ドライバや設定、Compiz への古い言及を削除し、KDE Plasma や GNOME などのデスクトップ環境が X11 に加えて Wayland にも対応したことから、それらの手順をデスクトップ環境の章へ移設しました。
* [Wayland](06-wayland.md#wayland) の章を新設し、FreeBSD での Wayland のインストールと設定方法を追加しました。
* [Network](https://docs.freebsd.org/en/books/handbook/network/#network) の章を新設し、ホスト名・DNS・トラブルシューティングを含む有線／無線ネットワークの基本設定をまとめました。有線ネットワーク、無線、IPv6 の各節を移動・更新し、コマンド出力例の改善、`sysrc` の利用、AsciiDoc 記法の整理を行っています。
* [デスクトップ環境（Desktop）](07-desktop.md#desktop)を更新し、KDE Plasma、GNOME、XFCE、MATE、Cinnamon、LXQt のインストール手順を刷新しました。また、Web ブラウザの選択肢を拡充し、開発ツール節を新設したほか、オフィススイート・文書ビューア・家計／財務関連の節を更新しました。
* [マルチメディア（Multimedia）](08-multimedia.md#multimedia)を改訂し、サウンド節の更新、サウンドミキサー・音声プレーヤー・動画プレーヤーの一覧表の新設、ヘッドホン自動切り替えの案内、会議・通話（conferencing and meetings）節の新設、イメージスキャナ節の改訂を行いました。
* [Linuxバイナリ互換機能（Linuxemu）](11-linuxemu.md#linuxemu)を改善し、`debootstrap` を使って Debian/Ubuntu のベースシステムを構築する手順を更新しました。
* [設定とチューニング（Config）](13-config.md#config-tuning)は内容を正確に表す章名へ改め、サービス管理、`cron` と `periodic`、`syslog`、電源管理、スワップの各節を更新しました。設定ファイルに関する項目を新設し、時代遅れとなっていたチューニング節は削除しました。
* [セキュリティ（Security）](https://docs.freebsd.org/en/books/handbook/security/#security)を更新し、IPsec による VPN、アカウント保護、パスワードハッシュ、`sudo`/`doas`、OpenSSH/OpenSSL の解説を強化しました。さらに IDS、セキュアレベル（securelevel）、ファイルフラグ、Capsicum、NFSv4 ACL、リソース制限を扱う節を新設しました。
* [Jails](16-jails.md#jails) を更新し、jail の種類（Thick、Thin、VNET、Linux Jail）、ホストシステム設定、ネットワーク構成オプション、jail 設定ファイル、構築手順、アップグレード方法、リソース制限、各種 jail 管理ツールやコンテナ関連ソリューションを収録しました。
* [電子メール（Mail）](https://docs.freebsd.org/en/books/handbook/mail/#mail)を更新し、DMA（DragonFly Mail Agent）の情報、Sendmail のアップグレード、DMA や Sendmail から別の MTA へ切り替える手順を追加しました。あわせて Dialup 節と Fetchmail 節を削除し、章全体の構成を整理しました。
* [参考文献（Bibliography）](https://docs.freebsd.org/en/books/handbook/bibliography/#bibliography)を大幅に更新しました。

> **訳注**: 原文の `Basics` の項目には `man:hier`（セクション番号省略）と書かれていますが、`hier(7)` を指しています。また、`Mail` の項目にある「DMA」はベースシステムに含まれる軽量なメール配送エージェント `dma(8)`（DragonFly Mail Agent）のことです。

<a id="preface-changes-from3"></a>
## 第三版以降の改訂（Third Edition）

現在のオンライン版 Handbook は、過去 10 年にわたる何百人もの貢献者の努力が積み重なった成果です。
2004 年に 2 分冊の第三版が刊行されて以降の主な変更点は次のとおりです。

* FreeBSD 上で Windows® アプリケーションを動かす方法を解説する [WINE](12-wine.md#wine) を追加しました。
* 強力な性能解析ツールである DTrace を解説する [DTrace](https://docs.freebsd.org/en/books/handbook/dtrace/#dtrace) を追加しました。
* Sun™ 由来の ZFS など、FreeBSD 非ネイティブのファイルシステムを扱う [その他のファイルシステム（Other File Systems）](24-filesystems.md#filesystems) を追加しました。
* FreeBSD の新しい監査機能とその使い方を解説する [セキュリティイベント監査（Security Event Auditing）](20-audit.md#audit) を追加しました。
* 仮想化ソフトウェア上へ FreeBSD をインストールする方法を解説する [仮想化（Virtualization）](https://docs.freebsd.org/en/books/handbook/virtualization/#virtualization) を追加しました。
* 新しいインストールユーティリティ `bsdinstall` を用いた FreeBSD のインストール手順を解説する [FreeBSDのインストール（Installing FreeBSD）](02-bsdinstall.md#bsdinstall) を追加しました。

<a id="preface-changes-from2"></a>
## 第二版からの改訂：第三版（Second Edition (2004)）

第三版は、FreeBSD Documentation Project の献身的なメンバーによる 2 年以上の作業の結晶でした。
印刷版は大部になったため、2 巻に分冊して刊行する必要が生じました。
この新版における主な変更点は次のとおりです。

* [設定とチューニング（Configuration and Tuning）](13-config.md#config-tuning)を拡充し、ACPI による電源・リソース管理、`cron` システムユーティリティ、さらに多くのカーネルチューニング項目を追加しました。
* [セキュリティ（Security）](https://docs.freebsd.org/en/books/handbook/security/#security)を拡充し、仮想プライベートネットワーク（VPN）、ファイルシステムのアクセス制御リスト（ACL）、セキュリティ勧告（Security Advisories）の解説を追加しました。
* [必須アクセス制御（Mandatory Access Control）](19-mac.md#mac)をこの版で新設しました。MAC とは何か、そしてこの仕組みを使って FreeBSD システムをどのように保護できるかを解説しています。
* [ストレージ（Storage）](https://docs.freebsd.org/en/books/handbook/disks/#disks)を拡充し、USB ストレージデバイス、ファイルシステムスナップショット、ファイルシステムクォータ、ファイル／ネットワークバックドファイルシステム、暗号化ディスクパーティションの解説を追加しました。
* [PPP](https://docs.freebsd.org/en/books/handbook/ppp-and-slip/#ppp-and-slip) にトラブルシューティング節を追加しました。
* [電子メール（Electronic Mail）](https://docs.freebsd.org/en/books/handbook/mail/#mail)を拡充し、代替メール配送エージェント（MTA）の利用、SMTP 認証、UUCP、fetchmail、procmail などの高度な話題を追加しました。
* [ネットワークサーバ（Network Servers）](https://docs.freebsd.org/en/books/handbook/network-servers/#network-servers)をこの版で完全新設しました。Apache HTTP Server や `ftpd` の設定、Samba を使った Microsoft® Windows® クライアント向けサーバの構築などを扱います。説明をわかりやすくするため、[高度なネットワーク（Advanced Networking）](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)から一部の節をここへ移動しました。
* [高度なネットワーク（Advanced Networking）](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)を拡充し、FreeBSD での Bluetooth® デバイスの利用、無線ネットワークの構築、ATM（Asynchronous Transfer Mode）ネットワークの解説を追加しました。
* 本書全体で使われる技術用語の定義を一か所にまとめた用語集（Glossary）を追加しました。
* 本書全体の表と図について、見やすさの改善を多数行いました。

<a id="preface-changes"></a>
## 初版からの改訂：第二版（First Edition (2001)）

第二版は、FreeBSD Documentation Project の献身的なメンバーによる 2 年以上の作業の結晶でした。
この版における主な変更点は次のとおりです。

* 完全な索引（Index）を追加しました。
* すべてのアスキーアート図をグラフィカルな図版へ置き換えました。
* 各章に標準形式の概要（Synopsis）を追加し、その章で扱う内容と読者に期待される前提知識を素早く把握できるようにしました。
* 構成を論理的に整理し、「Getting Started（はじめに）」「System Administration（システム管理）」「Appendices（付録）」の 3 部構成にしました。
* [FreeBSDの基本（FreeBSD Basics）](03-basics.md#basics)を拡充し、プロセス、デーモン、シグナルに関する情報を追加しました。
* [アプリケーションの導入：PackagesとPorts（Installing Applications: Packages and Ports）](04-ports.md#ports)を拡充し、バイナリパッケージ管理の解説を追加しました。
* [X Window System（The X Window System）](05-x11.md#x11)を全面的に書き直し、XFree86™ 4.X 上で KDE や GNOME といったモダンなデスクトップ環境を使う点に重点を置きました。
* [FreeBSDの起動処理（The FreeBSD Booting Process）](14-boot.md#boot)を拡充しました。
* [ストレージ（Storage）](https://docs.freebsd.org/en/books/handbook/disks/#disks)は、以前「Disks」と「Backups」に分かれていた 2 つの章を統合して書き直しました。1 つの章にまとめたほうが話題を理解しやすいと考えたためです。RAID（ハードウェア RAID・ソフトウェア RAID の双方）に関する節も追加しました。
* [シリアル通信（Serial Communications）](https://docs.freebsd.org/en/books/handbook/serialcomms/#serialcomms)を全面的に再構成し、FreeBSD 4.X/5.X 向けに更新しました。
* [PPP](https://docs.freebsd.org/en/books/handbook/ppp-and-slip/#ppp-and-slip) を大幅に更新しました。
* [高度なネットワーク（Advanced Networking）](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)に多くの新しい節を追加しました。
* [電子メール（Electronic Mail）](https://docs.freebsd.org/en/books/handbook/mail/#mail)を拡充し、`sendmail` の設定に関する情報を増やしました。
* [Linux®バイナリ互換機能（Linux® Binary Compatibility）](11-linuxemu.md#linuxemu)を拡充し、Oracle® や SAP® R/3® のインストール情報を追加しました。
* 第二版では、さらに次の新しい話題を取り上げました。

  * [設定とチューニング（Configuration and Tuning）](13-config.md#config-tuning)
  * [マルチメディア（Multimedia）](08-multimedia.md#multimedia)

<a id="preface-overview"></a>
## 本書の構成（Organization of This Book）

本書は、役割の異なる 5 つの部（section）に分かれています。
第 1 部 *Getting Started（導入編）* では、FreeBSD のインストールと基本的な使い方を扱います。
この部は先頭から順に読み進めることを想定していますが、すでに馴染みのある話題の章は読み飛ばしても構いません。
第 2 部 *Common Tasks（日常的な作業）* では、FreeBSD でよく使われる機能を扱います。
この部以降のすべての部は、順序に関係なく好きな章から読むことができます。
各章の冒頭には簡潔な概要（Synopsis）があり、その章で扱う内容と読者に期待される予備知識がまとめられています。
これにより、必要なときに興味のある章だけを選んで拾い読みしやすくなっています。
第 3 部 *System Administration（システム管理）* ではシステム管理に関する話題を、第 4 部 *Network Communication（ネットワーク通信）* ではネットワークとサーバに関する話題を扱います。
第 5 部には、リファレンス情報をまとめた付録（Appendices）を収録しています。

*[第1章 はじめに（Introduction）](01-introduction.md#introduction)*
: 初めて FreeBSD に触れる読者向けの導入章です。FreeBSD Project の歴史、目標、開発モデルを説明します。

*[FreeBSDのインストール（Installing FreeBSD）](02-bsdinstall.md#bsdinstall)*
: `bsdinstall` を使って FreeBSD 9._x_ 以降をインストールする全手順を順を追って案内します。

*[FreeBSDの基本（FreeBSD Basics）](03-basics.md#basics)*
: FreeBSD オペレーティングシステムの基本コマンドと基本機能を扱います。Linux® や他の UNIX® 系 OS に慣れている読者は、本章を読み飛ばしても問題ないでしょう。

*[アプリケーションの導入：PackagesとPorts（Installing Applications: Packages and Ports）](04-ports.md#ports)*
: FreeBSD 独自の「Ports Collection（ポート集）」と標準のバイナリパッケージの両方を使った、サードパーティ製ソフトウェアの導入方法を解説します。

*[X Window System（The X Window System）](05-x11.md#x11)*
: X Window System 全般と、特に FreeBSD 上での X11 の利用方法を説明します。KDE や GNOME といった代表的なデスクトップ環境についても触れます。

*[Wayland](06-wayland.md#wayland)*
: Wayland ディスプレイサーバ全般と、特に FreeBSD 上での Wayland の利用方法を説明します。Wayfire、Hikari、Sway などの代表的なコンポジタについても触れます。

*[デスクトップ環境とアプリケーション（Desktop Applications）](07-desktop.md#desktop)*
: Web ブラウザやオフィススイートなど代表的なデスクトップアプリケーションを挙げ、FreeBSD へのインストール方法を説明します。

*[マルチメディア（Multimedia）](08-multimedia.md#multimedia)*
: システムで音声や動画の再生を有効にする方法を示します。代表的な音声・動画アプリケーションの例も紹介します。

*[FreeBSDカーネルの設定（Configuring the FreeBSD Kernel）](09-kernelconfig.md#kernelconfig)*
: 新しいカーネルを構成する必要性を説明し、カスタムカーネルの設定・構築・インストールの詳しい手順を提供します。

*[印刷（Printing）](10-printing.md#printing)*
: FreeBSD でのプリンタ管理について、バナーページ、印刷アカウンティング、初期設定などの情報を解説します。

*[Linux®バイナリ互換機能（Linux® Binary Compatibility）](11-linuxemu.md#linuxemu)*
: FreeBSD の Linux® 互換機能を説明します。Oracle® や Mathematica® など、多くの代表的な Linux® アプリケーションの詳しいインストール手順も提供します。

*[WINE](12-wine.md#wine)*
: WINE の概要と詳しいインストール手順を説明します。さらに WINE の動作原理、GUI ヘルパーの導入、FreeBSD 上での Windows® アプリケーションの実行方法に加え、その他のヒントや解決策も紹介します。

*[設定とチューニング（Configuration and Tuning）](13-config.md#config-tuning)*
: システム管理者が FreeBSD システムを最適な性能へ調整するために利用できるパラメータを説明します。また、FreeBSD で使われる各種設定ファイルとその配置場所も解説します。

*[FreeBSDの起動処理（The FreeBSD Booting Process）](14-boot.md#boot)*
: FreeBSD の起動処理を説明し、設定オプションを使って起動処理をどのように制御できるかを解説します。

*[セキュリティ（Security）](https://docs.freebsd.org/en/books/handbook/security/#security)*
: Kerberos、IPsec、OpenSSH など、FreeBSD システムを安全に保つために利用できるさまざまなツールを説明します。

*[Jails](16-jails.md#jails)*
: jail フレームワークと、FreeBSD の従来からの `chroot` 機能に対する jail の利点を説明します。

*[必須アクセス制御（Mandatory Access Control）](19-mac.md#mac)*
: 必須アクセス制御（Mandatory Access Control、MAC）とは何か、そしてこの仕組みを使って FreeBSD システムをどのように保護できるかを説明します。

*[セキュリティイベント監査（Security Event Auditing）](20-audit.md#audit)*
: FreeBSD のイベント監査とは何か、どのように導入・設定するか、そして監査証跡をどのように検査・監視するかを説明します。

*[ストレージ（Storage）](https://docs.freebsd.org/en/books/handbook/disks/#disks)*
: FreeBSD で記憶媒体とファイルシステムを管理する方法を説明します。物理ディスク、RAID アレイ、光学メディア・テープメディア、メモリバックドディスク、ネットワークファイルシステムが含まれます。

*[GEOM: モジュラーディスク変換フレームワーク（GEOM: Modular Disk Transformation Framework）](https://docs.freebsd.org/en/books/handbook/geom/#geom)*
: FreeBSD の GEOM フレームワークとは何か、また対応する各種 RAID レベルをどのように構成するかを説明します。

*[OpenZFS ストレージプラットフォーム（The OpenZFS storage platform）](23-zfs.md#zfs)*
: OpenZFS ストレージプラットフォームを説明し、クイックスタートガイドおよび FreeBSD 上で OpenZFS を運用するための高度な話題を提供します。

*[その他のファイルシステム（Other File Systems）](24-filesystems.md#filesystems)*
: ext2、ext3、ext4 など、FreeBSD 非ネイティブのファイルシステムへの対応状況を解説します。

*[仮想化（Virtualization）](https://docs.freebsd.org/en/books/handbook/virtualization/#virtualization)*
: 仮想化システムが何を提供し、FreeBSD と組み合わせてどのように利用できるかを説明します。

*[ローカライズ：i18n・L10nの利用と設定（Localization - i18n/L10n Usage and Setup）](26-l10n.md#l10n)*
: 英語以外の言語で FreeBSD を使う方法を説明します。システムレベルとアプリケーションレベルの双方のローカライズを扱います。

*[FreeBSDの更新とアップグレード（Updating and Upgrading FreeBSD）](27-cutting-edge.md#updating-upgrading)*
: FreeBSD-STABLE、FreeBSD-CURRENT、FreeBSD リリースの違いを説明します。開発ブランチを追跡する利点がある利用者像とその手順を概説し、最新のセキュリティリリースへシステムを更新するための方法も解説します。

*[DTrace](https://docs.freebsd.org/en/books/handbook/dtrace/#dtrace)*
: FreeBSD 上で Sun™ 由来の DTrace ツールを設定・利用する方法を説明します。動的トレーシングによりリアルタイムのシステム解析を行い、性能上の問題箇所を特定できます。

*[USB デバイスモード / USB OTG（USB Device Mode / USB OTG）](https://docs.freebsd.org/en/books/handbook/usb-device-mode/#usb-device-mode)*
: FreeBSD における USB Device Mode と USB On-The-Go（USB OTG）の使い方を説明します。

*[PPP](https://docs.freebsd.org/en/books/handbook/ppp-and-slip/#ppp-and-slip)*
: FreeBSD で PPP を使ってリモートシステムへ接続する方法を説明します。

*[電子メール（Electronic Mail）](https://docs.freebsd.org/en/books/handbook/mail/#mail)*
: メールサーバの各構成要素を説明し、代表的なメールサーバソフトウェアである `sendmail` を例に基本的な設定の話題を掘り下げます。

*[ネットワークサーバ（Network Servers）](https://docs.freebsd.org/en/books/handbook/network-servers/#network-servers)*
: FreeBSD マシンをネットワークファイルシステムサーバ、ドメインネームサーバ（DNS）、ネットワーク情報システム（NIS）サーバ、時刻同期サーバとして構築するための詳しい手順と設定ファイル例を提供します。

*[ファイアウォール（Firewalls）](https://docs.freebsd.org/en/books/handbook/firewalls/#firewalls)*
: ソフトウェアベースのファイアウォールの考え方を説明し、FreeBSD で利用できる各種ファイアウォールの詳しい設定方法を提供します。

*[高度なネットワーク（Advanced Networking）](https://docs.freebsd.org/en/books/handbook/advanced-networking/#advanced-networking)*
: LAN 内の他コンピュータとのインターネット接続共有、高度なルーティング、無線ネットワーク、Bluetooth®、ATM、IPv6 など、多くのネットワークトピックを説明します。

*[FreeBSDの入手（Obtaining FreeBSD）](https://docs.freebsd.org/en/books/handbook/mirrors/#mirrors)*
: CDROM や DVD で FreeBSD メディアを入手するさまざまな方法や、FreeBSD をダウンロード・インストールできるインターネット上の各種サイトを一覧にしています。

*[参考文献（Bibliography）](https://docs.freebsd.org/en/books/handbook/bibliography/#bibliography)*
: 本書は多彩な話題を扱うため、さらに詳しい解説を求める読者もいるでしょう。参考文献では、本文中で参照している多くの優れた書籍を紹介しています。

*[インターネット上の情報源（Resources on the Internet）](https://docs.freebsd.org/en/books/handbook/eresources/#eresources)*
: FreeBSD ユーザーが質問を投稿したり、FreeBSD に関する技術的な議論に参加したりできる数多くのフォーラムを紹介します。

*[OpenPGP 鍵（OpenPGP Keys）](https://docs.freebsd.org/en/books/handbook/pgpkeys/#pgpkeys)*
: 一部の FreeBSD 開発者の PGP フィンガープリントを一覧にしています。

> **訳注**: 上記の章一覧は固定原文（`preface/_index.adoc`）の記述どおりに訳出しています。同じ固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28` の [`book.adoc`](https://github.com/freebsd/freebsd-doc/blob/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/content/en/books/handbook/book.adoc) には、`network`（Part I、Wayland の後）、`containers`（Part III、Jails の後）、`serialcomms`（Part IV、PPP の前）の 3 章が含まれていますが、原文のこの一覧からは欠落しています。また、`Installing FreeBSD` の「FreeBSD 9._x_ 以降」、`Electronic Mail` の `sendmail` 中心の説明、`Obtaining FreeBSD` の CDROM/DVD に関する記述は、いずれも固定原文時点の表記をそのまま保持しています。

<a id="preface-conv"></a>
## 本書の表記規則（Conventions used in this book）

一貫性があり読みやすい文章にするため、本書全体でいくつかの表記規則に従っています。

<a id="preface-conv-typographic"></a>
### 書体の使い分け（Typographic Conventions）

*イタリック体（Italic）*
: ファイル名、URL、強調したい語句、技術用語の初出には *イタリック体* を使います。

`等幅フォント（Monospace）`
: エラーメッセージ、コマンド、環境変数、Port 名、ホスト名、ユーザー名、グループ名、デバイス名、変数、コード断片には `等幅フォント` を使います。

**太字（Bold）**
: アプリケーション名、コマンド名、キー名には **太字** を使います。

<a id="preface-conv-commands"></a>
### ユーザー入力（User Input）

キーは本文と区別しやすいよう **太字** で示します。
同時に押す必要があるキーの組み合わせは、次のようにキーの間を `+` でつないで表記します。

**Ctrl**+**Alt**+**Del**

これは **Ctrl**、**Alt**、**Del** の各キーを同時に押すことを意味します。

順番に続けて入力するキーは、次のようにカンマで区切って表記します。

**Ctrl**+**X**, **Ctrl**+**S**

これは **Ctrl** キーと **X** キーを同時に押し、続いて **Ctrl** キーと **S** キーを同時に押すことを意味します。

<a id="preface-conv-examples"></a>
### 入力例（Examples）

`C:\>` で始まる例は、MS-DOS® のコマンドを示します。
特に断りがない限り、これらのコマンドは近年の Microsoft® Windows® 環境の「コマンドプロンプト」ウィンドウから実行できます。

```shell
C:\> tools\fdimage floppies\kern.flp A:
```

`#` で始まる例は、FreeBSD でスーパーユーザー（`root`）として実行する必要があるコマンドを示します。
`root` としてログインして入力するか、一般アカウントでログインしたうえで `su(1)` を使ってスーパーユーザー権限を取得してください。

```shell
# dd if=kern.flp of=/dev/fd0
```

`%` で始まる例は、一般ユーザーアカウントから実行すべきコマンドを示します。
特に断りがない限り、環境変数の設定やその他のシェルコマンドには C シェル（csh）構文を使います。

```shell
% top
```

> **訳注**: 上記の `C:\>`・`#`・`%` はプロンプト表記の例であり、実際の入力時にプロンプト文字自体は打ち込みません。また、フロッピーイメージを書き込む `fdimage` や `dd if=kern.flp of=/dev/fd0` はプロンプト例を示すための歴史的な記述です。そのまま実機のデバイスに対して `dd` を実行しないでください。さらに、原文は C シェル構文を前提としていますが、FreeBSD 14.0 以降、root ユーザーの既定シェルは `sh(1)` に変更されています（[FreeBSD 14.0-RELEASE リリースノート](https://www.freebsd.org/releases/14.0R/relnotes/)）。

<a id="preface-acknowledgements"></a>
## 謝辞（Acknowledgments）

本書は、世界中の何百人もの人々による取り組みの結晶です。
誤字脱字の修正を送ってくれた方から、丸ごと 1 章を寄稿してくれた方まで、あらゆる貢献が本書を支えてきました。

複数の企業も、著者に専任で執筆する報酬を支払ったり、出版費用を負担したりすることで本文書の開発を支援してきました。
特に BSDi（後に [Wind River Systems](http://www.windriver.com) に買収）は、2000 年 3 月の印刷版初版（ISBN 1-57176-241-8）の刊行に向けて、FreeBSD Documentation Project のメンバーに専任で本書の改善に取り組むための報酬を支払いました。
その後、Wind River Systems はさらに数名の著者に報酬を支払い、印刷物出力基盤の改良や本文への新章追加を進めました。
この取り組みは、2001 年 11 月の印刷版第二版（ISBN 1-57176-303-1）の刊行として結実しました。
2003〜2004 年には FreeBSD Mall Inc. が複数の貢献者に報酬を支払い、印刷版第三版に向けた Handbook の改善を支援しました。
印刷版第三版は 2 巻に分冊され、*The FreeBSD Handbook 3rd Edition Volume 1: User Guide*（ISBN 1-57176-327-9）および *The FreeBSD Handbook 3rd Edition Volume 2: Administrators Guide*（ISBN 1-57176-328-7）の 2 巻として刊行されました。
