<a id="updating-upgrading"></a>
# 第27章 FreeBSDの更新とアップグレード

FreeBSDの基本システムを、安全に更新するための考え方と、freebsd-update、Gitによるソース構築、基本システムのパッケージによる方法を説明します。

**本章の例には13.1・13.2など古いリリースや、固定原文時点で実験的なpkgbaseの手順が含まれます。** 現在のサポート状況や目標版への移行手順を、その版のリリース文書で確認してください。例の番号をそのまま更新先へ選ぶものではありません。実機のアップグレードをここで実行したという意味でもありません。

<a id="updating-upgrading-synopsis"></a>
## 概要

リリースの間も開発は続き、正式版にもセキュリティ・重要不具合の修正が提供されます。正式リリースを使う場合も、開発の進捗を追う場合も、適切な方法で更新を続ける必要があります。

本章では、freebsd-updateやGitによる更新、既知の正常状態との比較、文書の更新、CURRENTとSTABLEの違い、基本システム全体の再構築と再導入を学びます。

事前に[ネットワーク](https://docs.freebsd.org/en/books/handbook/advanced-networking/)と[追加アプリケーションの導入](04-ports.md)を理解してください。ソースの取得・更新にはGitを使います。必要なら `devel/git` のPortまたはパッケージを導入します。

<a id="updating-introduction"></a>
## 更新を始める前に

最初に、バージョンの読み方、更新とアップグレードの違い、サポートされる移行経路を確認します。

<a id="chapter-27-heading-04"></a>
### メジャー・マイナーバージョン

FreeBSD 6.0以降のリリースは、基本的に二段階の番号です。14.3-RELEASEなら14がメジャー、3がマイナーです。修正を適用したリリースはパッチレベルを持ち、0なら省略し、修正のまとまりごとにp1、p2と増えます。14.3-RELEASE-p7はその系列の第7段階の例です。

複数のメジャー系列を並行して保守する[サポートモデル](https://www.freebsd.org/security/#model)のため、リリース時刻の順番と、番号を大きい順に並べた結果は同じとは限りません。原文は14.2、13.5、14.3、15.0、14.4、15.1の順を例に挙げています。番号だけでなく、公開時期も確認します。

<a id="chapter-27-heading-05"></a>
### updateとupgrade

本章の**更新（update）**は、主に同じリリースへセキュリティ修正・errataを適用し、パッチレベルを上げる操作です。**アップグレード（upgrade）**は、別のバージョン番号の基本システムへ入れ替える操作を指します。

<a id="chapter-27-heading-06"></a>
### アップグレードの経路

[バイナリ修正](#updating-upgrading-freebsdupdate)、[パッケージ](#pkgbase)、[ソース構築](#makeworld)のいずれでも、原文がサポート対象とするのは、時系列で古い版から新しい版への移行です。

同じリリースの新しいパッチレベル、同じメジャーの新しいマイナー、または次のメジャーの、より後に公開された版へ進めます。例として14.3から14.4、14.3から15.0や15.1が挙げられています。

同じメジャーの古い版へ戻す、次のメジャーでも先に公開された版へ移る、メジャーを飛び越す経路は、ツールが受け付けても推奨・サポートされません。原文の例では、2026年3月の14.4から2025年12月の15.0へ進むことや、13.5から15.1へ飛ぶことが該当します。

<a id="updating-upgrading-freebsdupdate"></a>
## freebsd-update

`freebsd-update(8)` は、対応するリリースへバイナリのセキュリティ・errata修正を適用し、別リリースへのアップグレードも行う道具です。カーネルや修正を毎回手元でコンパイルする必要を減らせます。

対応する版・アーキテクチャ・終了予定は[FreeBSD Security](https://www.freebsd.org/security/)、移行時の注意は[リリース情報](https://www.freebsd.org/releases/)を確認してください。原文の「サポートする全アーキテクチャ」という説明を、現在のどの方式・リリースでも必ず利用できる保証として扱わないでください。

**OSのアップグレード前には、freebsd-updateを自動実行するcron設定を無効にします。** 以下では設定、通常の修正、リリース変更、状態比較を説明します。

<a id="freebsdupdate-config-file"></a>
### freebsd-updateの設定ファイル

通常は既定の `/etc/freebsd-update.conf` を使えます。変更する場合は、ファイルのコメントと `freebsd-update.conf(5)` を確認します。

```shell
# Components of the base system which should be kept updated.
Components world kernel
```

Componentsは対象の構成要素です。既定はworldとkernelで、src/base・src/sysなどへ細分化できますが、必要な要素を漏らすとソースとバイナリが食い違うため、理由なく対象を絞らないようにします。

```shell
# Paths which start with anything matching an entry in an IgnorePaths
# statement will be ignored.
IgnorePaths /boot/kernel/linker.hints
```

IgnorePathsに一致するパスは変更しません。ローカル変更を残せますが、修正が適用されない範囲にもなるため、/binや/sbinなどを広く除外する影響を理解します。

```shell
# Paths which start with anything matching an entry in an UpdateIfUnmodified
# statement will only be updated if the contents of the file have not been
# modified by the user (unless changes are merged; see below).
UpdateIfUnmodified /etc/ /var/ /root/ /.cshrc /.profile
```

UpdateIfUnmodifiedは、利用者が変更していない場合に更新する範囲です。ローカル変更があるものを自動で置き換えないための指定で、関連するKeepModifiedMetadataの扱いも確認します。

```shell
# When upgrading to a new FreeBSD release, files which match MergeChanges
# will have any local changes merged into the version from the new release.
MergeChanges /etc/ /var/named/etc/ /boot/device.hints
```

MergeChangesはローカル変更のマージを試みる範囲です。diffによる差分の適用や、エディタでの競合解決が必要な場合があります。原文は迷ったら/etcを退避してマージを受け入れる方法も述べていますが、**重要設定は内容を確認せず一律に承認しないでください。**

```shell
# Directory in which to store downloaded updates and temporary
# files used by FreeBSD Update.
# WorkDir /var/db/freebsd-update
```

WorkDirは取得物と一時作業の場所です。原文はリリース変更時に少なくとも約1GBの空きが必要としています。実際の更新量や余裕も見積もります。

```shell
# When upgrading between releases, should the list of Components be
# read strictly (StrictComponents yes) or merely as a list of components
# which *might* be installed of which FreeBSD Update should figure out
# which actually are installed and upgrade those (StrictComponents no)?
# StrictComponents no
```

StrictComponents=yesなら、Componentsを完全な対象一覧と見なし、その範囲の全ファイルを更新しようとします。noなら実際に導入された構成を判定するための候補として扱います。

<a id="freebsdupdate-security-patches"></a>
### セキュリティ修正を適用する

[セキュリティ勧告](https://docs.freebsd.org/en/books/handbook/security/#security-advisories)も確認し、修正を取得して適用します。

```shell
# freebsd-update fetch
# freebsd-update install
```

fetchは対象と変更予定ファイルを調べて取得し、installが適用します。カーネルを更新した場合は再起動し、実行中のプログラムを更新した場合はそのプログラムも再起動します。原文は、インストール済みカーネルの `freebsd-version -k` と、実行中の `uname -r` が違うかを目安として挙げています。ユーザーランドを含む全体の版は別に確認してください。

日次に確認・取得だけを行うシステムcrontabの例です。

```text
@daily                                  root    freebsd-update cron
```

このcronは自動適用せず、rootへメールを送ります。確認後、管理者がinstallします。これはシステムcrontab形式で、個人用crontabに実行ユーザー列をそのまま入れないでください。

直前の変更を取り消す例です。

```shell
# freebsd-update rollback
Uninstalling updates... done.
```

カーネル・モジュールが戻ったなら再起動し、影響するプログラムも再起動します。

自動的にバイナリ更新できるのはGENERICです。独自カーネルは必要に応じて構築・導入し直します。原文は復旧やアップグレードのため、`/boot/GENERIC` に対応するGENERICを保持するよう勧めています。[取得方法](#freebsd-update-custom-kernel-9x)を参照してください。

ソースが導入され、設定が対象に含む場合は、カーネルソースも更新されます。カーネル側に変更がなければ毎回再構築する必要はありませんが、原文はnewvers.shがパッチレベルの表示に関係する点を説明しています。unameのカーネル番号だけで、すべてのユーザーランド修正の状態を判断しないようにします。

<a id="freebsdupdate-upgrade"></a>
### マイナー・メジャーリリースをアップグレードする

更新先のリリースを指定してupgradeします。**バックアップ、復旧手段、空き容量、リリース固有の注意を先に確認してください。** 独自カーネルなら、対応するGENERICを `/boot/GENERIC` に用意します。

原文は13.1・13.2の例で、パッケージのビルド基盤が、新リリースの公開直後には古い方の環境を使う期間があると説明しています。カーネルモジュールは、そのままでは新しいカーネルと適合しない場合があり、マイナー更新でもソースからの構築が必要になることがあります。

まず現在の版の修正を適用します。

```shell
# freebsd-update fetch
# freebsd-update install
```

**次は13.1から13.2への原文の過去の例です。現在の移行先を示すものではありません。**

```shell
# freebsd-update -r 13.2-RELEASE upgrade
```

導入済みと判定した構成要素を確認します。

```text
Looking up update.FreeBSD.org mirrors... 1 mirrors found.
Fetching metadata signature for 13.1-RELEASE from update1.FreeBSD.org... done.
Fetching metadata index... done.
Inspecting system... done.

The following components of FreeBSD seem to be installed:
kernel/smp src/base src/bin src/contrib src/crypto src/etc src/games
src/gnu src/include src/krb5 src/lib src/libexec src/release src/rescue
src/sbin src/secure src/share src/sys src/tools src/ubin src/usbin
world/base world/info world/lib32 world/manpages

The following components of FreeBSD do not seem to be installed:
kernel/generic world/catpages world/dict world/doc world/games
world/proflibs

Does this look reasonable (y/n)? y
```

必要なファイルを取得し、場合によっては追加の判断を求められます。独自カーネルなら次の警告が出ます。

```text
WARNING: This system is running a "MYKERNEL" kernel, which is not a
kernel configuration distributed as part of FreeBSD 13.1-RELEASE.
This kernel will not be updated: you MUST update the kernel manually
before running "/usr/sbin/freebsd-update install"
```

この段階で無視できるのは、**対応するGENERICを用意し、それを中間の起動に使う手順を実行する場合**です。自分のカーネルが自動更新されるという意味ではありません。

設定を作業ディレクトリでマージし、競合があれば解決します。成功した結果も確認してください。原文はmaster.passwdやgroupなどの退避も勧めています。ここまでは、基本的に作業用領域での準備です。確認後、installで適用します。

```shell
# freebsd-update install
```

まずカーネルとモジュールを更新します。独自カーネルの構成で、次回は用意したGENERICを使う指定です。

```shell
# nextboot -k GENERIC
```

**起動と遠隔接続に必要なディスク・ネットワークのドライバがGENERICにもあるか確認してください。** 独自カーネルへ組み込んでいた機能が必要なら、loader.confなどで必要なモジュールを読み込む準備をします。原文は不要なサービスやディスク・ネットワークマウントを、移行完了まで止めることも勧めています。

```shell
# shutdown -r now
```

再起動後、保存された進捗から続行します。

```shell
# freebsd-update install
```

原文本文はここで古い共有ライブラリを削除するようにも説明しますが、**メジャー移行ではアプリケーションを更新してから、次節の最終installで古いライブラリを整理する段階があります。** 必要なinstall回数はライブラリの版変更などで二回・三回と異なります。メジャー更新なら[追加アプリケーションの更新](#freebsdupdate-portsrebuild)まで完了させます。

<a id="freebsd-update-custom-kernel-9x"></a>
#### 独自カーネルを使う場合のGENERICの用意

原文はFreeBSD 9.X以降の方法として説明しています。freebsd-updateで必要となる、現在のOS版に対応したGENERICを `/boot/GENERIC` に保持します。

独自カーネルを一度しか導入しておらず、kernel.oldが元のGENERICと確認できるなら、そのディレクトリを移す方法があります。回数や内容が分からなければ決め付けず、現在の版に合うものを取得します。

インストールメディアからの展開例です。**この例は `/boot/kernel/kernel` へ展開するため、稼働中カーネルの保存場所や退避先、最終的な `/boot/GENERIC` への配置を確認し、必要なカーネルを上書きしないでください。** `/media` のマウント元も環境に合わせます。

```shell
# mount /media
# cd /media/usr/freebsd-dist
# tar -C/ -xvf kernel.txz boot/kernel/kernel
```

一致するソースからGENERICをビルド・導入する例です。

```shell
# cd /usr/src
# make buildkernel __MAKE_CONF=/dev/null SRCCONF=/dev/null
# make installkernel __MAKE_CONF=/dev/null SRCCONF=/dev/null
```

GENERIC設定ファイルを改変せず、追加の特別なビルド設定を使わないようにします。原文は、freebsd-updateがGENERICの存在を必要とする段階では、それへ直ちに再起動する必要はないと説明しています。構築・導入だけで目的の保存先になったと決め付けず、実際の配置を確かめます。

<a id="freebsdupdate-portsrebuild"></a>
#### メジャー移行後にパッケージを更新する

マイナー更新では多くのアプリケーションがそのまま動きますが、メジャー変更ではABIが変わるため、追加パッケージ・Portsも対応する版へ更新します。パッケージの番号が同じでも、別ABI向けのビルドへ入れ替える必要があります。

強制的にリポジトリの版へ更新する例です。

```shell
# pkg-static upgrade -f
```

`ports-mgmt/portmaster` で、Portsを全面的に構築し直す原文の例です。

```shell
# portmaster -af
```

オプション画面での操作を避ける場合、原文は-Gを加える方法を挙げています。選ばれる設定と手元の管理方針を確認します。

ソフトウェア更新後、最後の整理を行います。

```shell
# freebsd-update install
```

一時的にGENERICを使った場合は、ここで[独自カーネル](09-kernelconfig.md)を新しいソースから再構築・導入できます。最後に再起動し、全体が新しい版で動くことを確認します。

<a id="freebsdupdate-system-comparison"></a>
### 既知の正常状態と比較する

`freebsd-update IDS` は、システムのコマンド、ライブラリ、設定を、既知のリリース情報と比較します。ただし、ローカルに保存する基準情報自身が改ざんされる可能性もあり、**完全な侵入検知システムの代わりではありません。** 原文は `security/snort` のようなIDSとは役割が違うと注意しています。

securelevelや基準情報を読み取り専用に置く方法もありますが、信頼して保管したDVD・外部媒体との比較など、比較元の信頼性を別に確保することが重要です。[バイナリ検証](https://docs.freebsd.org/en/books/handbook/security/#security-ids)も参照してください。

結果をファイルへ追記する例です。

```shell
# freebsd-update IDS >> outfile.ids
```

期待値と現在のSHA256などが出力されます。差のあるファイル名だけを取り出す例です。

```shell
# cat outfile.ids | awk '{ print $1 }' | more
/etc/master.passwd
/etc/motd
/etc/passwd
/etc/pf.conf
```

差があれば即座に侵入という意味ではなく、ユーザー追加によるpasswd変更や、修正済みモジュールなどもあります。比較から外す必要があるパスは、freebsd-update.confのIDSIgnorePathsへ指定します。

<a id="updating-bootcode"></a>
## 起動コードを更新する

ブートコードやloaderの更新は、`gpart(8)`、`gptboot(8)`、`gptzfsboot(8)`、`loader.efi(8)` を参照してください。BIOS・UEFI、パーティション構成、起動する媒体に合う方法を選びます。ZFSの新機能を使う場合は、[プールと起動コードの互換性](23-zfs.md#zfs-zpool-upgrade)も確認します。

<a id="updating-upgrading-documentation"></a>
## ドキュメントを更新する

最新の文書は[Documentation Portal](https://docs.freebsd.org/)で読めますが、ウェブサイト、Handbook、FAQ、記事などをローカルにも保持しておくと便利です。ソースや文書用Portsを使って更新できます。

文書の編集・修正提案は[FreeBSD Documentation Project Primer](https://docs.freebsd.org/en/books/fdp-primer/)を参照してください。

<a id="updating-installed-documentation"></a>
### 文書をソースから構築する

基本システムに含まれない構築用ツールが必要です。[Documentation Project Primerの導入手順](https://docs.freebsd.org/en/books/fdp-primer/overview/#overview-quick-start)で用意し、新しい作業ディレクトリへ取得します。

```shell
# git clone https://git.FreeBSD.org/doc.git /usr/doc
```

初回取得の完了を待ちます。以後は取得した `/usr/doc` のGit作業ツリー内で更新します。

```shell
# git pull
```

原文の構築例です。

```shell
# cd /usr/doc
# make
```

このmakeが何を生成・配置するかは、その時点の文書ツリーの手順を確認してください。ソースを更新しただけで、既存のすべての導入済み文書を自動更新したことにはなりません。

<a id="current-stable"></a>
## 開発ブランチを追う

FreeBSDの開発にはCURRENTとSTABLEがあります。どちらも正式リリースと同じ利用方針ではなく、対象となる利用者と追跡方法を理解して選びます。

<a id="current"></a>
### FreeBSD-CURRENT

CURRENTは最新の開発ソースで、進行中・実験中の変更や、次の正式版へ残るか未定の仕組みも含みます。高い技術力を前提とし、一時的にビルドできないこともあります。同じCURRENTでも取得時点によって結果は異なります。

主な対象は、ソースを開発する人、問題調査や修正提案へ時間をかけられるテスター、最新の実装を調査・参照する人です。単に新機能やバグ修正を早く得るための安全な近道ではなく、新しい変更が別の不具合を生む場合もあります。原文は正式サポート対象ではないと明記しています。

追跡する場合は次を行います。

1. [freebsd-current](https://lists.freebsd.org/subscription/freebsd-current)と[dev-commits-src-main](https://lists.freebsd.org/subscription/dev-commits-src-main)を購読し、重要な通知とコミットの副作用を確認します。全ブランチの変更はdev-commits-src-allを使います。購読は[メーリングリスト](https://lists.freebsd.org/)から行えます。
2. Gitのmainブランチを取得します。[Gitの利用](https://docs.freebsd.org/en/books/handbook/mirrors/#git)も参照してください。
3. 調査だけなら一部のソースでも済みますが、OSを構築するなら全ソースが必要です。`/usr/src/Makefile`、`/usr/src/UPDATING` とメーリングリストを読み、[ソースからの更新](#makeworld)と、必要な中間手順に従います。
4. 問題や改善案を報告し、可能なら修正コードも提供します。

<a id="stable"></a>
### FreeBSD-STABLE

STABLEはリリースへ向けた開発ブランチです。通常はCURRENTで先に試した変更を、より慎重に取り込みます。ただし、**STABLEも開発用であり、「常に不具合がない正式版」という意味ではありません。** 試験する余裕がない利用者へ、原文は正式リリースを勧めています。

CURRENTでは見つからなかった環境依存の不具合も現れます。とくに本番サーバへは、検証用環境で十分に試さず導入しないでください。次のリリースの開発・試験へ関わる人が主な対象です。

追跡する場合は、[freebsd-stable](https://lists.freebsd.org/subscription/freebsd-stable)と、対象ブランチのコミット通知dev-commits-src-branchesを購読します。全体を追うならdev-commits-src-allも利用できます。依存関係や変更予定の議論を確認し、問題があれば開発者へ知らせます。

新規導入にはSTABLEの[スナップショット](https://www.freebsd.org/snapshots/)などを利用できます。既存システムならGitで目的のstable系列を選びます。原文のstable/13は例で、現在の対象と対応状況は[リリースエンジニアリング情報](https://www.freebsd.org/releng/)で確認してください。構築前にMakefile・UPDATING・メーリングリストを読み、[ソース更新の手順](#makeworld)へ進みます。

<a id="translate-n-number"></a>
### n-numberを読む

不具合調査には、どのソースから作ったシステムかの特定が重要です。カーネルへ埋め込まれた情報をunameで見ます。以下は原文の過去の出力例です。

```shell
% uname -v
FreeBSD 14.0-CURRENT #112 main-n247514-031260d64c18: Tue Jun 22 20:43:19 MDT 2021     fred@machine:/usr/home/fred/obj/usr/home/fred/git/head/amd64.amd64/sys/FRED
```

末尾にはカーネル名、ビルドした人と場所などが入ります。ブランチ付近の表記を分解すると次のとおりです。

```text
main-n247514-031260d64c18

main
n247514
031260d64c18

```

mainはブランチ、n247514は先頭親をたどったコミット数、031260d64c18はソースのGitハッシュです。未コミット変更があれば-dirtyが付く場合があります。例は変更のない作業ツリーなので付きません。

対応する数は、次で求められます。

```shell
% git rev-list --first-parent --count 031260d64c18
247514
```

修正の前後を素早く判断する手掛かりですが、**同じ公開ブランチの対応する履歴で比較する必要があります。** ローカルブランチの数は親と重なり、別ブランチ間の大小だけでは修正の有無を断定できません。浅いクローンは履歴を省くため、同じ方法で正しい数を比較できません。勧告やerrataが示すブランチ・ハッシュも合わせて確認します。

<a id="makeworld"></a>
## FreeBSDをソースから更新する

ソース構築では、ハードウェア向けの最適化、非既定の設定、不要部分の省略などを選べます。バイナリ更新より時間がかかる一方、カーネルとユーザーランドを用途に合わせて作れます。

<a id="updating-src-quick-start"></a>
### ソース更新のクイックスタート

以下は典型的な流れの要約です。実際には、移行元・先のUPDATINGと詳細な節を先に確認してください。

**mergemasterからetcupdateへ初めて切り替える場合、ソース更新と新worldの構築前に、etcupdateの比較元を準備します。** これを省くと、不要な競合が発生する場合があります。

```shell
# etcupdate extract
# etcupdate diff
```

extractで標準設定の比較用データベースを作り、diffでローカル差分を確認します。不要な変更を整理しておくと、次のマージを減らせます。

通常の更新の概要です。**`check /usr/src/UPDATING` は原文の作業指示であり、その名前のコマンドをそのまま実行する意味ではありません。**

```shell
# git -C /usr/src pull
check /usr/src/UPDATING
# cd /usr/src
# make -j4 buildworld
# make -j4 kernel
# shutdown -r now
# etcupdate -p
# cd /usr/src
# make installworld
# etcupdate -B
# shutdown -r now
```

順に、ソース更新、UPDATINGの確認、world構築、カーネル構築・導入、再起動、installworld前の設定更新、world導入、残りの設定マージ、再起動です。`make kernel` はbuildkernelとinstallkernelを行います。-j4は四つの並列ジョブの例で、使用機器へ合わせます。

<a id="updating-src-preparing"></a>
### ソース更新の準備

`/usr/src/UPDATING` を読み、更新前後に必要な手動操作を確認します。一般的な手順だけで、その版固有の移行条件を置き換えないでください。

<a id="updating-src-obtaining-src"></a>
### ソースを更新・取得する

<a id="synching"></a>
<a id="updating-src-obtaining-src-repopath"></a>

通常の保存先は `/usr/src` です。Gitで管理されているか、取得元を確認します。

```shell
# cd /usr/src
# git remote --v
origin  https://git.freebsd.org/src.git (fetch)
origin  https://git.freebsd.org/src.git (push)
```

適切なリポジトリ・ブランチであることを確認してからpullします。remoteが表示されるだけで、目的のブランチを使っている証明にはなりません。

```shell
# git -C /usr/src pull
```

not a git repositoryなら、未取得か、別の方法で導入したソースです。新しい作業ツリーを用意します。

| 系列 | Gitブランチ | 性質 |
|---|---|---|
| X.Y-RELEASE | `releng/X.Y` | 主にセキュリティと重要不具合の修正。原文が多くのユーザーへ勧める系列。 |
| X.Y-STABLE | `stable/X` | 同じメジャー系列内の開発を取り込みます。STABLEはABIの安定性を意図する名前で、常に無不具合の意味ではありません。既存ソフトが動くよう配慮されますが、例外や不具合はあり得ます。 |
| X-CURRENT | `main` | 未リリースの最新開発。大きい不具合や互換性変更があり、上級者向け。 |

使用中の版を調べる原文の例です。

```shell
# uname -r
13.2-RELEASE
```

13.2-RELEASEならreleng/13.2を選ぶ、という対応例です。現在の対象は自分の利用・移行計画に合わせます。既存ソースを退避し、指定ブランチを取得します。

```shell
# mv /usr/src /usr/src.bak
# git clone --branch releng/13.2 https://git.FreeBSD.org/src.git /usr/src
```

**既存の `/usr/src.bak` や、未保存の独自変更を失わないよう確認します。** ブランチはURLへ付加するのではなく、このコマンドでは--branchで指定しています。最後の引数はローカル保存先です。

<a id="updating-src-building"></a>
### ソースをビルドする

まずカーネル以外の基本システムであるworldを作り、新しいカーネルを構築する道具も準備します。その後カーネルを構築します。

```shell
# cd /usr/src
# make buildworld
# make buildkernel
```

生成物は通常 `/usr/obj` 以下です。以下のオプションで作業を調整できます。

<a id="updating-src-building-clean-build"></a>
#### クリーンビルド

以前の生成物を再利用すると速くなる場合がありますが、すべてを作り直すには、構築前にcleanworldを使います。

```shell
# make cleanworld
```

ソースと生成物を取り違えず、必要な空き容量・所要時間も確保します。

<a id="updating-src-building-jobs"></a>
#### 並列ジョブ数

<a id="updating-src-building-jobs-example"></a>

マルチコアでは `-j` で並列数を増やすと速くなる場合があります。`sysctl hw.ncpu` が手掛かりですが、CPU、RAM、ストレージ、構築対象によって適切な数は異なります。原文はCPU数の半分〜二倍程度から試す方法を挙げています。負荷やメモリ不足も見ながら測定します。

四ジョブでworldとカーネルを作る例です。

```shell
# make -j4 buildworld buildkernel
```

<a id="updating-src-building-only-kernel"></a>
#### カーネルだけをビルドする

ソースが変わった場合は、対応するbuildworldを先に完了させます。その後、同じソースと構築環境でカーネルだけを再構築できます。

```shell
# cd /usr/src
# make buildkernel
```

<a id="updating-src-building-custom-kernel"></a>
#### 独自カーネルをビルドする

標準のGENERICは、多くの機器で必要なドライバとオプションを含みます。メモリの少ない組み込み機器などでは、不要な部分を除く独自構成が役立つ場合があります。

設定は `/usr/src/sys/アーキテクチャ/conf/` にあり、原文はuname -mで機種を調べる例を示しています。amd64なら `/usr/src/sys/amd64/conf/` です。`/usr/src` は作り直すことがあるため、独自ファイルは/rootなど別の場所へ保存し、リンクを張る方法が勧められています。

```shell
# cp /usr/src/sys/amd64/conf/GENERIC /root/STORAGESERVER
# cd /usr/src/sys/amd64/conf
# ln -s /root/STORAGESERVER .
```

/root/STORAGESERVERを `config(5)` に従って編集します。**ビルドは `/usr/src` へ戻って行い**、KERNCONFに名前を指定します。原文の直前のcd先はconfなので、そのまま同じ場所でビルドを続ける例と誤解しないでください。

```shell
# make buildkernel KERNCONF=STORAGESERVER
```

<a id="updating-src-installing"></a>
### ビルド結果を導入する

buildworld・buildkernelの後に、まず新しいカーネルを入れて再起動し、そのカーネル上でworldを入れる概要です。**この短い例だけで設定マージを省かず、[クイックスタート](#updating-src-quick-start)と後述のetcupdate、UPDATINGが要求する順序も守ってください。**

```shell
# cd /usr/src
# make installkernel
# shutdown -r now
# cd /usr/src
# make installworld
# shutdown -r now
```

独自カーネルは導入時も同じKERNCONFを指定します。

```shell
# cd /usr/src
# make installkernel KERNCONF=STORAGESERVER
# shutdown -r now
# cd /usr/src
# make installworld
# shutdown -r now
```

再起動可能な旧カーネルや復旧手段、遠隔接続のためのドライバも確保しておきます。

<a id="updating-src-completing"></a>
### 更新の仕上げ

設定ファイルをマージし、不要になったファイル・ライブラリを確認して整理し、再起動します。必要なライブラリを使うアプリケーションの更新も、削除前に計画します。

<a id="updating-src-completing-merge-etcupdate"></a>
#### etcupdateで設定をマージする

`etcupdate(8)` は、installworldだけでは更新しない/etcなどの設定を、標準の旧版・新版・ローカル変更の三方向でマージし、手動作業を減らす道具です。

初めて使う際など、比較結果を確認するにはdiffを使います。

```shell
# etcupdate diff
```

自動解決できないものは、resolveで対話的に処理します。

```shell
# etcupdate resolve
```

**mergemasterからの切り替えでは、新ソースの取得・構築前に**比較用データを準備し、差分を確認します。

```shell
# etcupdate extract
# etcupdate diff
```

extractは標準設定の基準を準備する操作です。すでに新しいソースへ進んでから、古いローカル設定の基準として無条件に使わないよう、etcupdateの説明を確認してください。

<a id="updating-src-completing-check-old"></a>
#### 古いファイルとライブラリを確認する

通常は `/usr/src` で、不要になったファイルを調べます。

```shell
# make check-old
```

確認後、削除できます。

```shell
# make delete-old
```

古いライブラリは別に確認します。

```shell
# make check-old-libs
```

削除する操作です。

```shell
# make delete-old-libs
```

**そのライブラリを使うプログラムは、削除すると動かなくなります。** 必要なプログラムを対応版へ再構築・交換する順序と復旧手段を確認してください。すべて安全と判断できた場合のみ、個別の確認を省く指定も使えます。

```shell
# make BATCH_DELETE_OLD_FILES=yes delete-old-libs
```

<a id="updating-src-completing-restart"></a>
#### 更新後に再起動する

最後に再起動し、新しいカーネルとユーザーランド、サービスが適切に動くことを確認します。

```shell
# shutdown -r now
```

<a id="pkgbase"></a>
## 基本システムをパッケージで更新する

FreeBSDの基本システムもpkgで配布・管理する仕組みがあり、従来pkgbaseと呼ばれてきました。原文は公式パッケージの公開開始を[2023年10月の案内](https://lists.freebsd.org/archives/freebsd-pkgbase/2023-October/000221.html)として紹介し、14系列での利用は実験的、15.0からの `freebsd-base(7)` はインストール・マイナー更新・メジャー更新のtech previewと説明しています。

**これは固定原文の開発段階の説明です。** 将来的にbase.txz・kernel.txzなどの配布セットやfreebsd-updateを置き換え、freebsd-updateがpkgを扱う計画にも触れていますが、すべてが完了したという意味ではありません。利用する版の文書と制約を確認してください。

基本システムのパッケージは、[ソースからの独自構築](#makeworld)を排除するものではありません。公式パッケージだけでなく、独自カーネル・ユーザーランドをパッケージ化する方法もあります。

<a id="chapter-27-heading-36"></a>
### 既存ホストをfreebsd-baseへ移行する

原文では14.0以降を移行対象とし、それより前はまずfreebsd-updateで対応版へ進める必要があると説明しています。[FreeBSD Foundationのpkgbasify](https://github.com/FreeBSDFoundation/pkgbasify)を紹介しており、実際の利用時にはその版の手順を確認します。freebsd-updateがpkg・pkgbasifyを利用するようになる、という記述は原文の将来計画です。

**原文は追加で最大約5GiBの空きが必要で、当時のツールがそれを検査しないと警告しています。** ダウンロード・展開・競合ファイルの移動に必要な容量を、利用者が事前に確保します。

原文が列挙する主な処理は、ZFSならbectlで退避用ブート環境を作る、リポジトリ設定を作る、base・kernel・lib32・debugなどを更新する、設定をマージする、passwdやcapabilityのデータベースを更新する、**sshdを即時再起動する**、の六つです。遠隔作業は接続と復旧手段も確認します。元文は[レビューD51594](https://reviews.freebsd.org/D51594)や[Portの要望](https://wiki.freebsd.org/WantedPorts#O-P)にも触れ、実装・提供形態が変わり得る状態を表しています。

<a id="chapter-27-heading-37"></a>
### freebsd-baseを使うホストを更新する

<a id="pgk-base-repo-configuration"></a>
<a id="table-of-packagebase-branches"></a>

原文は、この方法がまだ開発中で、とくに既存ホストの変換では注意が必要だと警告しています。バックアップと復旧方法を用意し、対象リリースの手順を確認してください。

独自のリポジトリ設定用ディレクトリを作ります。

```shell
# mkdir -p /usr/local/etc/pkg/repos/
```

FreeBSD-base.confの例です。`${ABI}` と `${VERSION_MINOR}` は設定内の変数であり、翻訳で特定の値へ固定しません。

```text
FreeBSD-base {
    url = "pkg+https://pkg.freebsd.org/${ABI}/base_release_${VERSION_MINOR}";
    mirror_type = "srv";
    signature_type = "fingerprints";
    fingerprints = "/usr/share/keys/pkg";
    enabled = yes;
}
```

書式は `pkg.conf(5)` を参照します。URLにより対象のブランチ・更新頻度を選びます。**以下は固定原文の表であり、現在の提供状態や実行時刻の保証ではありません。** 時刻は原文どおりUTCです。

| ブランチ | 公開頻度の例 | URL |
|---|---|---|
| main | 毎日2回、00:00・12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_latest` |
| main | 週1回、日曜12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_weekly` |
| stable/14 | 毎日2回、00:00・12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_latest` |
| stable/14 | 週1回、日曜12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_weekly` |
| releng/14.3 | 毎日2回、00:00・12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_release_3` |
| releng/15.0 | 毎日2回、00:00・12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_release_0` |
| stable/15 | 毎日2回、00:00・12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_latest` |
| stable/15 | 週1回、日曜12:00 UTC | `pkg+https://pkg.freebsd.org/${ABI}/base_weekly` |

ABIも含め、意図する系列の設定にしたうえで更新します。メジャー変更は、次節のABI指定などの追加手順が必要です。

```shell
# pkg update -r FreeBSD-base
# pkg upgrade -r FreeBSD-base
```

提案された変更・削除のパッケージが正しいか確認してから受け入れます。完了後は再起動します。

```shell
# shutdown -r now
```

<a id="pkgbase-major-upgrade"></a>
#### pkgbaseによるメジャーアップグレード

ZFSなら別のブート環境へ変更を適用し、稼働中の環境を残して試せます。**共有データセットまで隔離されるわけではありません。** Root-on-ZFSでないシステムは、とくに事前のバックアップと復旧が必要です。いずれも原文では実験的な経路を含みます。

<a id="chapter-27-heading-39"></a>
##### メジャー移行の準備

FreeBSD-base.confを目的の系列へ合わせます。次は15.0のbase_release_0の例です。原文は、今後リリースへ標準同梱される際にファイルの場所が変わる可能性も注意しています。

```text
FreeBSD-base {
    url = "pkg+https://pkg.freebsd.org/${ABI}/base_release_0";
    mirror_type = "srv";
    signature_type = "fingerprints";
    fingerprints = "/usr/share/keys/pkg";
    enabled = yes;
}
```

原文は、14から15へのpkgbase移行で、条件によってpkg自身が削除され、異常終了する[既知の問題](https://github.com/freebsd/pkg/issues/2475)を挙げています。回避策として、更新前にpkgをロックする例です。

```shell
# pkg -c /mnt/upgrade lock pkg
```

**このコマンドは `/mnt/upgrade` をchroot先として使います。後述のZFS手順でその場所へ対象ブート環境をマウントしてから実行するもので、準備段階の空ディレクトリへそのまま実行する順序ではありません。** ZFSを使わない手順へ同じchroot指定を流用しないでください。

原文は、14から15または16-CURRENTへの実験的移行後に、FreeBSD-set-minimalメタパッケージの導入も必要としています。対象版の実際の移行条件を確認します。

追加パッケージを復元する手掛かりとして、Portのorigin一覧を保存します。

```text
pkg prime-origins | sort -u > /var/tmp/pkg-prime-origins.txt
```

この一覧だけでデータや全設定がバックアップされるわけではありません。

<a id="pkgbase-major-zfs"></a>
##### ZFSのブート環境へメジャー更新する

移行先の名前でブート環境を作ります。既存の同名環境がないか確認します。

```shell
# bectl create 15.0-RELEASE
```

作業ディレクトリを作り、そこへマウントします。

```shell
# mkdir /mnt/upgrade
# bectl mount 15.0-RELEASE /mnt/upgrade
```

必要なら前節のpkgロックを、このマウント済み環境に対して行います。次は移行先ABIを指定し、pkg-staticをその環境で実行する例です。**非baseのパッケージやデスクトップが削除される場合があるので、提案を確認してください。** 15とamd64は、実際の移行先・アーキテクチャへ合わせます。

```shell
# env ABI=FreeBSD:15:amd64 pkg-static -c /mnt/upgrade upgrade -r FreeBSD-base
```

版の不一致に関する確認例です。

```text
Newer FreeBSD version for package FreeBSD-zoneinfo:
To ignore this error set IGNORE_OSVERSION=yes
- package: 1500058
- running userland: 1500000
Ignore the mismatch and continue? [y/N]:
```

原文は確認して続けると説明していますが、**意図した移行による差かを判断せず、すべての不一致を無条件に無視しないでください。** 新環境内でカーネルとユーザーランドの版を確認します。

```shell
# chroot /mnt/upgrade
# freebsd-version -ku
# exit
```

一度だけ新環境を選び、再起動します。

```shell
# bectl activate -t 15.0-RELEASE
# shutdown -r now
```

問題があれば再起動すると旧環境へ戻る仕組みですが、起動・接続不能時の操作手段も確保しておきます。正常動作を確認できたら恒久的に有効化します。

```text
bectl activate 15.0-RELEASE
```

共有側へ書き込んだデータは、旧ブート環境へ戻しても元に戻らない点に注意してください。[ブート環境](23-zfs.md#zfs-boot-environments)も参照します。

<a id="pkgbase-major-non-zfs"></a>
##### ZFSを使わない場合のメジャー更新

別のZFSブート環境へ逃がさず、現在の基本システムを更新する方法です。**実行前に復元可能なバックアップを用意し、停止時間と失敗時の復旧手順を確認してください。** 移行先ABIと正しいリポジトリを指定します。

```shell
# env ABI=FreeBSD:15:amd64 pkg-static upgrade -r FreeBSD-base
```

版の差に対する確認例です。

```text
Newer FreeBSD version for package FreeBSD-zoneinfo:
To ignore this error set IGNORE_OSVERSION=yes
- package: 1500058
- running userland: 1500000
Ignore the mismatch and continue? [y/N]:
```

対象の版が計画どおりか判断して続行します。完了後は `freebsd-version -ku` で確認し、再起動します。ZFS版の一時有効化・自動的な旧環境への戻り方は、この手順にはありません。

<a id="chapter-27-heading-42"></a>
##### メジャー更新後の作業

pkgを回避策としてロックした場合は、更新後に解除します。

```shell
# pkg unlock pkg
```

追加パッケージも、新しいABIに合う版へ更新します。

```shell
# pkg upgrade
```

前節の実験的経路で要求されるメタパッケージの導入なども確認します。問題時は[FreeBSDのサポート情報](https://www.freebsd.org/support/)を参照してください。

<a id="build-pkgbase-packages-locally"></a>
### pkgbaseを自分で構築し、ローカルネットワークへ配布する

独自の基本システムパッケージは、FreeBSDのソースを取得して作れます。原文の取得例です。

```shell
# cd /usr/src
# git clone https://github.com/freebsd/freebsd-src.git /usr/src
```

**clone先の `/usr/src` は新規または空である必要があります。** 原文の最初のcdを、その場所に既存ソースがあるまま続けてcloneする指示と読まないでください。既存の変更を確認し、適切な親ディレクトリから新しい取得先へcloneするか、既存のGitツリーを利用します。

対象ブランチを選ぶ例です。

```shell
# git checkout releng/14.3
```

八ジョブの構築例です。実際のCPU・メモリなどへ合わせます。

```shell
# make -j8 buildworld && make -j8 buildkernel && make -j8 packages
```

頻繁に構築する場合は `devel/ccache` で再利用できる場合があります。原文の生成先例は `/usr/obj/usr/src/repo/FreeBSD:14:amd64/14.3p2` で、実際の版・設定により異なります。

nginxで配布するlocationの例です。

```text
 location /FreeBSD:14:amd64 {
   alias /usr/obj/usr/src/repo/FreeBSD:14:amd64/;
   autoindex on;
 }
```

設定を確認してnginxをreloadします。原文はHTTP配布を使うクライアント側の例として、`/usr/local/etc/pkg/repos/upgrade.conf` を示しています。

```text
upgrade: {
	url         = http://ip.of.the.server/FreeBSD:14:amd64/14.3p2
	enabled     = yes
}
```

`ip.of.the.server`、ABI、版を実環境へ置き換え、更新コマンドのリポジトリ指定もFreeBSD-baseではなくupgradeにします。**掲載例だけでは通信暗号化やリポジトリ署名の設定を示していません。** 配布元の信頼性と署名検証・通信保護は、実際の配布方針に合わせて構成します。

<a id="small-lan"></a>
## 複数台を同じソースで更新する

同じバイナリを使うマシン群ごとに、一台でソース取得と構築を行い、残りへNFSで共有すると、容量・回線・CPUの重複を減らせます。[NFS](https://docs.freebsd.org/en/books/handbook/network-servers/#network-nfs)の設定も参照してください。

まず同じユーザーランドを使う**ビルド対象群**を決め、十分なCPUのあるビルド機を選びます。カーネルは各機専用でも構いません。別に、停止や不具合を許容できる試験機を用意します。ビルド機と同一でも構いませんが、検証前に本番へ導入しません。

対象群の各機は、ビルド機の `/usr/src` と `/usr/obj` をNFSで参照します。複数群がある場合、ソース自体を一台から共有する構成も可能です。make.conf・src.confの設定を整合させ、各機が必要な基本システムの要素をすべて構築します。各クライアントは自分のKERNCONF、ビルド機は全対象カーネルを列挙し、自分のものを先頭にします。全機のカーネル設定もビルド機に置きます。

[ソース更新](#makeworld)に従って構築したら、最初はビルド機へ導入せず、試験機へ入れます。試験機で必要なNFS共有を利用できることを確かめ、原文はshutdown nowでシングルユーザーモードへ移り、カーネル・world・etcupdateを導入する流れを示しています。起動に必要な構成とNFSの可用性を確認し、完了後は再起動して通常モードで試します。正常と確認してから残りへ同じ方法で展開します。

Portsでも `/usr/ports` を共有できます。distfilesの共有はmake.confのDISTDIRを共通の場所へ向け、NFSでrootがマッピングされる先のユーザーが書けるようにします。各機で構築するならWRKDIRPREFIXはローカルへ向けます。ビルド機でパッケージまで作るなら、PACKAGESを配布用の共通ディレクトリへ指定します。

<a id="building-on-non-freebsd-hosts"></a>
## FreeBSD以外のホストで構築する

LinuxやmacOSからもFreeBSDを構築できます。原文は `tools/build/make.py` を推奨しています。これはFreeBSDが使うbmakeのラッパーで、必要なmakeなどの道具と環境、XCC・XLDなどの外部ツールチェーン設定を準備し、-jや構築ターゲットを渡せます。

新しいbmakeを直接使う方法もありますが、必要な環境変数を自分で指定します。`tools/build/make.py --debug` が設定を調べる手掛かりになります。

macOSではLLVMが必要で、Homebrewでの導入例です。

```text
brew install llvm
```

Linuxでは原文はClang 10.0以降と、libarchive・libbz2のヘッダ（しばしばlibarchive-dev・libbz2-dev）を挙げています。**構築するソースの版によって必要なツールの最低版は変わり得るため、古い最低値だけで十分と決め付けず、そのツリーの構築条件も確認してください。**

八ジョブでworldを作る例です。

```text
MAKEOBJDIRPREFIX=/tmp/obj tools/build/make.py -j 8 TARGET=arm64 TARGET_ARCH=aarch64 buildworld
```

この例はTARGET=arm64、TARGET_ARCH=aarch64で、生成物を `/tmp/obj` に置きます。非FreeBSDホストではMAKEOBJDIRPREFIX・TARGET・TARGET_ARCHが必須で、生成先ディレクトリも先に用意します。詳細は `arch(7)`、`build(7)` を参照してください。
