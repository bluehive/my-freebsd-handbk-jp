<a id="security"></a>
# 第16章 セキュリティ（Security）

本ファイルは、[FreeBSD Handbook（英語）](https://docs.freebsd.org/en/books/handbook/security/)の「Chapter 16. Security」（既存 TOC ID 15）を、[freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc) の固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28`（`documentation/content/en/books/handbook/security/_index.adoc`）に基づいて日本語へ意訳したものです。

> **訳注**: 原文の AsciiDoc フロントマターおよび文書属性・共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しています。掲載されているコマンドや設定例は説明のための例であり、翻訳作業中に実機で実行したものではありません。実行例中の `#` は root ユーザー、`%` や `$` は一般ユーザーのプロンプトを示します。

<a id="security-synopsis"></a>
## 概要

システムとネットワークを保護する標準的な手法は数多く執筆されており、FreeBSD の利用者にとっても、攻撃や侵入者からシステムを守る方法を理解しておくことは不可欠です。

本章では、いくつかの基本概念と実践的な手法を説明します。FreeBSD システムには複数のセキュリティ層が備わっており、さらに多くのサードパーティ製ユーティリティを追加してセキュリティを強化できます。

本章で扱う内容は次のとおりです。

* FreeBSD システムの基本的なセキュリティ概念
* FreeBSD で利用できる各種暗号化機構
* `inetd(8)` で TCP Wrappers を使うための設定方法
* FreeBSD で Kerberos を構築する方法
* FreeBSD で OpenSSH を設定・使用する方法
* FreeBSD で OpenSSL を使用する方法
* ファイルシステム ACL の使用方法
* `pkg` を使って Ports Collection からインストールしたサードパーティ製ソフトウェアパッケージを監査する方法
* FreeBSD セキュリティ勧告の活用方法
* プロセスアカウンティング（Process Accounting）とは何か、および FreeBSD で有効にする方法
* ログインクラスやリソース制限データベースを使ってユーザーのリソースを制御する方法
* Capsicum とは何か、および基本的な使用例

一部のトピックは内容が複雑なため、専用の章や文書で解説されています。たとえば、[Firewalls](34-firewalls.md#firewalls)、[Mandatory Access Control](19-mac.md#mac)、[VPN over IPsec](https://docs.freebsd.org/en/articles/vpn-ipsec/) などの記事があります。

<a id="security-intro"></a>
## はじめに

セキュリティはすべての利用者の責任です。どのシステムであっても脆弱な入口が 1 つあれば、侵入者が重要情報へアクセスし、ネットワーク全体に深刻な被害をもたらす恐れがあります。情報セキュリティの中核原則の 1 つが CIA トライアドであり、情報システムの機密性（Confidentiality）、完全性（Integrity）、可用性（Availability）を指します。

CIA トライアドはコンピュータセキュリティの基盤となる考え方であり、顧客や利用者は自身のデータが保護されることを期待しています。たとえば、顧客はクレジットカード情報が安全に保管されること（機密性）、注文内容が背後で改ざんされないこと（完全性）、そしていつでも注文情報にアクセスできること（可用性）を期待します。

CIA を確保するため、セキュリティの専門家は多層防御（defense in depth）戦略を採ります。多層防御とは、複数のセキュリティ層を重ねることで、単一の層が破られてもシステム全体の防御が崩れないようにする考え方です。たとえば、システム管理者がファイアウォールを有効にしただけで、ネットワークやシステムが安全になったと見なすことはできません。アカウントの監査やバイナリの整合性確認を行い、悪意のあるツールが導入されていないことも確かめる必要があります。効果的なセキュリティ戦略を実装するには、どのような脅威があり、どう防御するかを理解しなければなりません。

コンピュータセキュリティにおける脅威とは何でしょうか。脅威は、遠隔地から許可なくシステムへ侵入しようとするリモートの攻撃者だけに限りません。従業員、悪意のあるソフトウェア、不正なネットワーク機器、自然災害、セキュリティ脆弱性、さらには競合企業も脅威に含まれます。

システムやネットワークへの不正アクセスは、偶発的なミスやリモートの攻撃者だけでなく、企業スパイや元従業員によって引き起こされる場合もあります。利用者としては、自身の過失がセキュリティ侵害につながった可能性がある場合に備え、隠さずに認めてセキュリティチームへ報告する姿勢が重要です。管理者としては、脅威を把握し、影響を軽減できるよう備えておくことが重要です。

システムへセキュリティ対策を適用する際は、まず基本的なアカウントとシステム設定を固め、次にシステムのポリシーや組織のセキュリティ手順に沿うようにネットワーク層を保護していくことが推奨されます。多くの組織では、情報機器の設定を網羅したセキュリティポリシーがすでに定められています。ポリシーには、ワークステーション、デスクトップ、モバイル機器、携帯電話、本番サーバー、開発サーバーのセキュリティ設定を含める必要があります。多くの場合、標準運用手順（SOP）もすでに整備されています。判断に迷ったときは、セキュリティチームに確認してください。

<a id="sec-accounts"></a>
## アカウントの保護

FreeBSD でアカウントを安全に維持することは、データの機密性、システムの整合性、権限分離を保つうえで極めて重要です。これにより不正アクセス、マルウェア、情報漏洩を防ぎ、コンプライアンスを満たして組織の信用を守ることができます。

<a id="security-accounts"></a>
### ログインの防止

システムを保護するうえで、アカウントの監査はよい出発点になります。ログインアクセスを必要としないアカウントはすべて無効化してください。

> **ヒント**: `root` には強力なパスワードを設定し、そのパスワードを共有しないようにしてください。

アカウントのログインアクセスを拒否する方法は 2 つあります。

1 つ目はアカウントをロックする方法です。次の例は `imani` アカウントをロックします。

```shell
# pw lock imani
```

2 つ目は、シェルを `/usr/sbin/nologin` に変更してログインアクセスを防ぐ方法です。`nologin(8)` シェルは、ユーザーがログインしようとした際にシステムがシェルを割り当てないようにします。

他のユーザーのシェルを変更できるのはスーパーユーザーだけです。

```shell
# chsh -s /usr/sbin/nologin imani
```

<a id="security-passwords"></a>
### パスワードハッシュ

パスワードはテクノロジーにおける必要悪です。使用せざるを得ない場合は複雑なものを選び、パスワードデータベースに保存する暗号化済み表現には強力なハッシュ機構を用いる必要があります。FreeBSD は `crypt()` ライブラリで SHA256、SHA512、Blowfish などのハッシュアルゴリズムに対応しています。詳細は `crypt(3)` を参照してください。

デフォルトの SHA512 をより安全性の低いハッシュアルゴリズムへ変更すべきではありませんが、より安全な Blowfish アルゴリズムへ変更することは可能です。

> **注**: Blowfish は AES の一部ではなく、連邦情報処理標準（FIPS）に準拠しているとは見なされません。環境によっては使用が許可されない場合があります。

ユーザーのパスワードの暗号化にどのハッシュアルゴリズムが使われているかを確認するには、スーパーユーザーが FreeBSD のパスワードデータベースにある該当ユーザーのハッシュを参照します。各ハッシュは、暗号化に用いられたハッシュ機構の種類を示す記号で始まります。

DES が使われている場合は先頭の記号がありません。MD5 の場合は記号が `$`、SHA256 と SHA512 の場合は `$6$`、Blowfish の場合は `$2a$` です（訳注: 原文では MD5 を `$`、SHA256 と SHA512 の双方を `$6$` と記載していますが、FreeBSD の `crypt(3)` における実際の識別プレフィックスは MD5 が `$1$`、SHA256 が `$5$`、SHA512 が `$6$` です）。次の例では、`imani` のパスワードハッシュが `$6$` で始まっているため、デフォルトの SHA512 アルゴリズムでハッシュ化されています。パスワードデータベースに保存されているのはパスワードそのものではなく、暗号化されたハッシュである点に注意してください。

```shell
# grep imani /etc/master.passwd
```

出力は次のようになります。

```
imani:$6$pzIjSvCAn.PBYQBA$PXpSeWPx3g5kscj3IMiM7tUEUSPmGexxta.8Lt9TGSi2lNQqYGKszsBPuGME0:1001:1001::0:0:imani:/usr/home/imani:/bin/sh
```

ハッシュ機構はユーザーのログインクラスで設定します。

現在どのハッシュ機構が使われているかは、次のコマンドで確認できます。

```shell
% grep passwd_format /etc/login.conf
```

出力は次のようになります。

```
:passwd_format=sha512:\
```

たとえば、アルゴリズムを Blowfish に変更するには、その行を次のように書き換えます。

```
:passwd_format=blf:\
```

その後、`cap_mkdb(1)` を実行して `login.conf` データベースを更新する必要があります。

```shell
# cap_mkdb /etc/login.conf
```

この変更は既存のパスワードハッシュには影響しません。そのため、すべてのユーザーに `passwd` を実行してパスワードを変更してもらい、全パスワードを再ハッシュする必要があります。

<a id="security-pwpolicy"></a>
### パスワードポリシーの強制

ローカルアカウントに対して強力なパスワードポリシーを強制することは、システムセキュリティの基本です。FreeBSD では、組み込みの Pluggable Authentication Modules（PAM）を使って、パスワードの長さ、強度、複雑さを強制できます。

本節では、`pam_passwdqc(8)` モジュールを用いてパスワードの最小長・最大長および文字種の混在を強制する設定方法を示します。このモジュールは、ユーザーがパスワードを変更するときに適用されます。

このモジュールを設定するには、スーパーユーザーになり、`/etc/pam.d/passwd` 内の `pam_passwdqc.so` を含む行のコメントを解除します。

次に、その行をパスワードポリシーに合わせて編集します。

```
password        requisite       pam_passwdqc.so         min=disabled,disabled,disabled,12,10 similar=deny retry=3 enforce=users
```

各パラメータの説明は `pam_passwdqc(8)` に記載されています。

このファイルを保存すると、パスワードを変更するユーザーには次のようなメッセージが表示されます。

```shell
% passwd
```

出力は次のようになります。

```
Changing local password for user
Old Password:

You can now choose the new password.
A valid password should be a mix of upper and lower case letters,
digits and other characters.  You can use a 12 character long
password with characters from at least 3 of these 4 classes, or
a 10 character long password containing characters from all the
classes.  Characters that form a common pattern are discarded by
the check.
Alternatively, if no one else can see your terminal now, you can
pick this as your password: "trait-useful&knob".
Enter new password:
```

ポリシーに合致しないパスワードが入力された場合は警告とともに拒否され、設定されたリトライ回数の上限まで再入力できます。

組織のポリシーでパスワードの有効期限が必要な場合、FreeBSD は `/etc/login.conf` 内のユーザーのログインクラスで `passwordtime` をサポートしています。

`default` ログインクラスには次の例が含まれています。

```
#       :passwordtime=90d:\
```

このログインクラスに 90 日の有効期限を設定するには、コメント記号（`#`）を削除して編集を保存し、次のコマンドを実行します。

```shell
# cap_mkdb /etc/login.conf
```

個別のユーザーに有効期限を設定するには、有効期限の日付または期限までの日数とユーザー名を `pw` に渡します。

```shell
# pw usermod -p 30-apr-2025 -n user
```

ここで示したように、有効期限の日付は日・月・年の形式で指定します。詳細は `pw(8)` を参照してください。

<a id="security-sudo"></a>
### sudo を用いた共有管理

システム管理者は、特定の特権作業を実行できるようにユーザーへ拡張権限を付与しなければならないことがよくあります。チームメンバーが担当作業を行うために FreeBSD システムへアクセスする状況では、管理者ごとに特有の課題が生じます。そうしたメンバーが必要としているのは一般ユーザーより少し広い権限の一部にすぎないにもかかわらず、上司（経営層）に対しては「スーパーユーザー権限がないと作業できない」と訴えることが少なくありません。幸い、この要件を正確に管理するツールが存在するため、一般ユーザーにスーパーユーザー権限そのものを与える必要はありません。

> **ヒント**: 管理者であっても、不要なときは自分の特権を制限すべきです。

ここまでのセキュリティの章では、許可されたユーザーにアクセスを認め、不正アクセスを防ぐ方法を説明してきました。許可されたユーザーがシステムリソースにアクセスできるようになると、次の課題が生じます。一部のユーザーがアプリケーションの起動スクリプトへアクセスする必要があったり、複数の管理者からなるチームでシステムを保守したりするケースです。従来は、標準のユーザーとグループ、ファイルパーミッション、さらには `su(1)` コマンドでこうしたアクセスを管理していました。しかし、アプリケーションがより多くのアクセスを要求し、より多くのユーザーがシステムリソースを使うようになるにつれ、より優れた解決策が必要になりました。現在もっとも広く使われているアプリケーションが Sudo です。

Sudo を使うと、管理者はシステムコマンドへのアクセスをより厳格に設定でき、高度なログ機能も利用できます。このツールは Ports Collection の `security/sudo`、または `pkg(8)` ユーティリティからインストールできます。

インストールするには、次のコマンドを実行します。

```shell
# pkg install sudo
```

インストールが完了したら、導入された `visudo` を使って設定ファイルをテキストエディタで開きます。`visudo` には構文チェッカーが組み込まれており、保存前にエラーがないか検証できるため、使用を強く推奨します。

設定ファイルはいくつかの小さなセクションに分かれており、柔軟で詳細な設定が可能です。次の例では、Web アプリケーションの保守担当者である `user1` が、_webservice_ という名前の Web アプリケーションを起動・停止・再起動できるようにする必要があります。このユーザーにこれらの作業を実行する権限を与えるには、`/usr/local/etc/sudoers` の末尾に次の行を追加します。

```
user1   ALL=(ALL)       /usr/sbin/service webservice *
```

これで、ユーザーは次のコマンドを使って _webservice_ を起動できるようになります。

```shell
% sudo /usr/sbin/service webservice start
```

この設定では単一のユーザーに `webservice` サービスへのアクセスを許可していますが、多くの組織では Web チーム全体でサービスの管理を担当しています。1 行の設定でグループ全体に権限を付与することも可能です。次の手順では、`webteam` グループを作成し、ユーザーをそのグループに追加して、グループの全メンバーがサービスを管理できるようにします。

```shell
# pw groupadd -g 6001 -n webteam
```

同じく `pw(8)` コマンドを使って、ユーザーを `webteam` グループに追加します。

```shell
# pw groupmod -m user1 -n webteam
```

最後に、`/usr/local/etc/sudoers` に次の行を追加すると、`webteam` グループのどのメンバーでも _webservice_ を管理できるようになります。

```
%webteam   ALL=(ALL)       /usr/sbin/service webservice *
```

`su(1)` とは異なり、`sudo(8)` で必要なのはエンドユーザー自身のパスワードだけです。これにより、望ましくないパスワードの共有を避けられます。

`sudo(8)` でアプリケーションの実行を許可されたユーザーは自分のパスワードだけを入力します。`root` のパスワードを入力して `root` の全権限を取得する `su(1)` よりも安全で、よりきめ細かな制御が可能です。

> **ヒント**: 多くの組織は二要素認証モデルへ移行しつつあるか、すでに移行しています。そのような場合、ユーザーは入力すべきパスワードを持たないことがあります。
>
> `sudo(8)` では、`NOPASSWD` 変数を使うことで二要素認証モデルに対応した設定が可能です。先ほどの設定にこれを追加すると、_webteam_ グループの全メンバーがパスワードなしでサービスを管理できるようになります。

```
%webteam   ALL=(ALL)       NOPASSWD: /usr/sbin/service webservice *
```

<a id="security-doas"></a>
### doas を用いた共有管理

`doas(1)` は OpenBSD から移植されたコマンドラインユーティリティです。Unix 系システムで広く使われている `sudo(8)` コマンドの代替として機能します。

`doas` を使うと、ユーザーはシンプルでセキュリティを意識した手法を保ちながら、昇格された権限（通常は `root` ユーザー）でコマンドを実行できます。`sudo(8)` とは異なり、`doas` は単純さと最小主義を重視しており、膨大な設定オプションではなく簡潔な権限委譲に焦点を当てています。

インストールするには、次のコマンドを実行します。

```shell
# pkg install doas
```

インストール後、特定のコマンドやロールに対するユーザーへのアクセス権を付与するため、`/usr/local/etc/doas.conf` を設定する必要があります。

もっとも単純なエントリは次のようになります。これは、`doas` コマンドを実行する際にパスワードを尋ねることなく、ユーザー `local_user` に `root` 権限を付与する設定です。

```
permit nopass local_user as root
```

`doas` ユーティリティのインストールと設定が終われば、次のように昇格された権限でコマンドを実行できます。

```shell
$ doas vi /etc/rc.conf
```

さらに多くの設定例については、`doas.conf(5)` を参照してください。



<a id="security-ids"></a>
## 侵入検知システム（IDS）

システムファイルとバイナリの検証は、システム管理チームやセキュリティチームにシステム上の変更に関する情報を提供するため重要です。システムの変更を監視するソフトウェアアプリケーションは、侵入検知システム（IDS）と呼ばれます。

FreeBSD は、`mtree(8)` と呼ばれる基本的な IDS 機能のネイティブサポートを提供しています。夜間のセキュリティメールでも管理者へ変更が通知されますが、その情報はローカルに保存されるため、悪意のあるユーザーがシステムへの変更を隠す目的で改ざんするおそれがあります。そのため、バイナリ署名のセットを別途作成し、root 所有の読み取り専用ディレクトリ、あるいはできればリムーバブル USB ディスクやリモートサーバーに保存することが推奨されます。

また、アップデートのたびに `freebsd-update IDS` を実行することも推奨されます。

<a id="security-ids-generate-spec-file"></a>
### 仕様ファイルの生成

組み込みの `mtree(8)` ユーティリティを使うと、ディレクトリの内容に関する仕様（specification）を生成できます。仕様の生成にはシード（数値定数）が使われ、仕様が変更されていないかを確認する際にもこのシードが必要になります。これにより、ファイルやバイナリが改ざんされたかどうかを判別できます。シード値は攻撃者に知られていないため、ファイルのチェックサム値を偽装したり検証したりすることは極めて困難または不可能になります。

> **ヒント**: バイナリや設定ファイルを含むディレクトリだけでなく、機密データを含むディレクトリについても仕様を作成することが推奨されます。一般的には、`/bin`、`/sbin`、`/usr/bin`、`/usr/sbin`、`/usr/local/bin`、`/etc`、`/usr/local/etc` に対して仕様を作成します。

次の例では、`/bin` 内の各システムバイナリについて `sha512` ハッシュのセットを生成し、その値をユーザーのホームディレクトリにある隠しファイル `/home/user/.bin_chksum_mtree` に保存します。

```shell
# mtree -s 123456789 -c -K cksum,sha512 -p /bin > /home/user/.bin_chksum_mtree
```

出力は次のようになります。

```
mtree: /bin checksum: 3427012225
```

> **警告**: `123456789` という値はシードを表しており、ランダムに選ぶ必要があります。この値は覚えておく必要がありますが、**決して共有してはいけません**。
>
> シード値とチェックサムの出力は、悪意のあるユーザーから隠しておくことが重要です。

<a id="security-ids-spec-file-structure"></a>
### 仕様ファイルの構造

mtree 形式は、ファイルシステムオブジェクトの集合を記述するテキスト形式です。このようなファイルは通常、ディレクトリ階層の作成や検証に用いられます。

mtree ファイルは複数の行から構成され、各行が単一のファイルシステムオブジェクトに関する情報を示します。先頭の空白は常に無視されます。

先ほど作成した仕様ファイルを使って、形式と内容を説明します。

```
#          user: root
#       machine: machinename
#          tree: /bin
#          date: Thu Aug  24 21:58:37 2023

# .
/set type=file uid=0 gid=0 mode=0555 nlink=1 flags=uarch
.               type=dir mode=0755 nlink=2 time=1681388848.239523000
    \133        nlink=2 size=12520 time=1685991378.688509000 \
                cksum=520880818 \
                sha512=5c1374ce0e2ba1b3bc5a41b23f4bbdc1ec89ae82fa01237f376a5eeef41822e68f1d8f75ec46b7bceb65396c122a9d837d692740fdebdcc376a05275adbd3471
    cat         size=14600 time=1685991378.694601000 cksum=3672531848 \
                sha512=b30b96d155fdc4795432b523989a6581d71cdf69ba5f0ccb45d9b9e354b55a665899b16aee21982fffe20c4680d11da4e3ed9611232a775c69f926e5385d53a2
    chflags     size=8920 time=1685991378.700385000 cksum=1629328991 \
                sha512=289a088cbbcbeb436dd9c1f74521a89b66643976abda696b99b9cc1fbfe8b76107c5b54d4a6a9b65332386ada73fc1bbb10e43c4e3065fa2161e7be269eaf86a
    chio        size=20720 time=1685991378.706095000 cksum=1948751604 \
                sha512=46f58277ff16c3495ea51e74129c73617f31351e250315c2b878a88708c2b8a7bb060e2dc8ff92f606450dbc7dd2816da4853e465ec61ee411723e8bf52709ee
    chmod       size=9616 time=1685991378.712546000 cksum=4244658911 \
                sha512=1769313ce08cba84ecdc2b9c07ef86d2b70a4206420dd71343867be7ab59659956f6f5a458c64e2531a1c736277a8e419c633a31a8d3c7ccc43e99dd4d71d630
```

1. 仕様を作成したユーザー。
2. マシンのホスト名。
3. ディレクトリのパス。
4. 仕様が作成された日時。
5. `/set` 特殊コマンド。解析されたファイルから取得したいくつかの設定を定義します。
6. 解析対象のディレクトリを指し、種類、モード、ハードリンク数、変更時刻（UNIX 時刻形式）などの情報を示します。
7. 各ファイルを指し、サイズ、時刻、および整合性を検証するためのハッシュの一覧を示します。

<a id="security-ids-verify-specification-file"></a>
### 仕様ファイルの検証

バイナリ署名が変更されていないことを確認するには、現在のディレクトリの内容を事前に生成しておいた仕様と比較し、結果をファイルに保存します。

このコマンドには、元の仕様を生成したときに使ったシードが必要です。

```shell
# mtree -s 123456789 -p /bin < /home/user/.bin_chksum_mtree >> /home/user/.bin_chksum_output
```

これにより、仕様を作成したときと同じ `/bin` のチェックサムが出力されるはずです。このディレクトリ内のバイナリに変更がなければ、出力ファイル `/home/user/.bin_chksum_output` は空になります。

変更を模擬するため、`touch(1)` を使って `/bin/cat` の日付を変更し、検証コマンドを再度実行してみます。

```shell
# touch /bin/cat
```

検証コマンドをもう一度実行します。

```shell
# mtree -s 123456789 -p /bin < /home/user/.bin_chksum_mtree >> /home/user/.bin_chksum_output
```

その後、出力ファイルの内容を確認します（訳注: 直前のコマンド例では出力先を `/home/user/.bin_chksum_output` としていますが、原文のこの例では `/root/.bin_chksum_output` を参照しています）。

```shell
# cat /root/.bin_chksum_output
```

出力は次のようになります。

```
cat:    modification time (Fri Aug 25 13:30:17 2023, Fri Aug 25 13:34:20 2023)
```

> **警告**: これは、メタデータに変化が生じた場合にコマンドを実行すると何が表示されるかを示すための単なる例です。

<a id="security-secure-levels"></a>
## セキュアレベル

securelevel はカーネルに実装されたセキュリティ機構です。securelevel が正の値に設定されている場合、カーネルは特定の操作を制限し、スーパーユーザー（root）であっても実行できなくなります。

securelevel 機構は次の操作を制限します。

* `schg`（システム不変フラグ）などの特定のファイルフラグの解除
* `/dev/mem` および `/dev/kmem` を介したカーネルメモリへの書き込み
* カーネルモジュールの読み込み
* ファイアウォールルールの変更

<a id="security-secure-levels-definitions"></a>
### セキュアレベルの定義

カーネルは 5 つの異なるセキュリティレベルで動作します。スーパーユーザーのプロセスはレベルを上げることができますが、どのプロセスもレベルを下げることはできません。

セキュリティレベルの定義は次のとおりです。

**-1: 恒久的非セキュアモード（Permanently insecure mode）**
: 常に非セキュアモードでシステムを動作させます。これがデフォルトの初期値です。

**0: 非セキュアモード（Insecure mode）**
: 不変フラグおよび追記専用フラグを解除できます。すべてのデバイスはパーミッションに従って読み書きできます。

**1: セキュアモード（Secure mode）**
: システム不変フラグおよびシステム追記専用フラグを解除できません。マウントされたファイルシステムのディスク、`/dev/mem`、`/dev/kmem` は書き込み用に開くことができません。`/dev/io`（プラットフォームに存在する場合）は一切開くことができません。カーネルモジュール（`kld(4)` 参照）の読み込みやアンロードはできません。`debug.kdb.enter` sysctl を使ってカーネルデバッガに入ることもできません。`debug.kdb.panic`、`debug.kdb.panic_str` その他の sysctl を使ってパニックやトラップを強制的に発生させることもできません。

**2: 高セキュアモード（Highly secure mode）**
: セキュアモードと同じですが、さらにディスクがマウントされているかどうかにかかわらず、書き込み用に開くことができません（`mount(2)` による場合を除く）。このレベルではファイルシステムをアンマウントして改ざんする行為を防げますが、システムがマルチユーザーで稼働している間に `newfs(8)` を実行することもできなくなります。

**3: ネットワークセキュアモード（Network secure mode）**
: 高セキュアモードと同じですが、さらに IP パケットフィルタールール（`ipfw(8)`、`ipfirewall(4)`、`pfctl(8)` 参照）を変更できず、`dummynet(4)` や `pf(4)` の設定も調整できません。

> **ヒント**: 要約すると、FreeBSD のセキュアレベルにおける `Permanently Insecure Mode` と `Insecure Mode` の主な違いは、提供されるセキュリティの度合いです。`Permanently Insecure Mode` はすべてのセキュリティ制限を完全に解除するのに対し、`Insecure Mode` は一部の制限を緩和しつつも一定の制御とセキュリティを維持します。

<a id="security-modify-secure-levels"></a>
### セキュアレベルの変更

システムの securelevel を変更するには、次のコマンドを実行して `kern_securelevel_enable` を有効にする必要があります。

```shell
# sysrc kern_securelevel_enable="YES"
```

そして、`kern_securelevel` の値を希望するセキュリティレベルに設定します。

```shell
# sysrc kern_securelevel=2
```

稼働中のシステムの securelevel の状態を確認するには、次のコマンドを実行します。

```shell
# sysctl -n kern.securelevel
```

出力には現在の securelevel の値が表示されます。0 より大きければ、securelevel による保護機能の少なくとも一部が有効になっています。

<a id="security-file-flags"></a>
## ファイルフラグ

ファイルフラグを使うと、基本的なパーミッションや所有権に加えて、追加のメタデータや属性をファイルやディレクトリに付与できます。これらのフラグにより、特別なディレクトリを作成したり拡張属性を使ったりすることなく、ファイルのさまざまな動作や性質を制御できます。

ファイルフラグは、ファイルの削除防止、追記専用化、ファイル更新の同期など、さまざまな目的で使われます。FreeBSD でよく使われるファイルフラグには、ファイルの変更や削除を防ぐ「不変（immutable）」フラグや、ファイルの末尾へのデータ追記のみを許可して変更や削除を禁じる「追記専用（append-only）」フラグがあります。

これらのフラグは FreeBSD では `chflags(1)` コマンドで管理でき、管理者やユーザーはファイルやディレクトリの動作や特性をより細かく制御できます。ファイルフラグはファイルのアクセスや操作の方法に影響を与えるため、通常は root または適切な特権を持つユーザーが管理する点に注意してください。一部のフラグは、`chflags(1)` に記載されているとおりファイルの所有者も使用できます。

<a id="security-work-file-flag"></a>
### ファイルフラグの操作

この例では、ユーザーのホームディレクトリにある `~/important.txt` というファイルを削除から保護したいとします。

次のコマンドを実行して `schg` ファイルフラグを設定します。

```shell
# chflags schg ~/important.txt
```

`root` ユーザーを含むどのユーザーがこのファイルを削除しようとしても、システムは次のメッセージを表示します。

```
rm: important.txt: Operation not permitted
```

ファイルを削除するには、次のコマンドを実行してそのファイルのファイルフラグを解除する必要があります。

```shell
# chflags noschg ~/important.txt
```

サポートされているファイルフラグの一覧とその機能については、`chflags(1)` を参照してください。

<a id="openssh"></a>
## OpenSSH

OpenSSH は、リモートマシンへの安全なアクセスを提供するネットワーク接続ツール群です。さらに、TCP/IP 接続を SSH 接続経由で安全にトンネリング（転送）することもできます。OpenSSH はすべての通信を暗号化し、盗聴、セッション乗っ取り、その他のネットワークレベルの攻撃を防ぎます。

OpenSSH は OpenBSD プロジェクトによって保守されており、FreeBSD にデフォルトでインストールされています。

暗号化されていない状態でネットワーク上にデータが送信されると、クライアントとサーバーの間の経路上にあるネットワークスニファーによって、ユーザー名やパスワード情報、あるいはセッション中にやり取りされたデータが盗まれるおそれがあります。OpenSSH はこれを防ぐため、さまざまな認証方式と暗号化方式を提供しています。

OpenSSH の詳細は [OpenSSH の Web ページ](https://www.openssh.com/) を参照してください。

本節では、他のシステムへ安全にアクセスし、FreeBSD システムから安全にファイルを転送するための組み込みクライアントユーティリティの概要を説明します。その後、FreeBSD システム上で SSH サーバーを設定する方法を説明します。

> **ヒント**: 先述のとおり、本章ではベースシステム版の OpenSSH を扱います。`security/openssh-portable` パッケージからも OpenSSH を利用でき、こちらは追加の設定オプションを備え、新機能への更新もより頻繁に行われます。

<a id="chapter-16-heading-20"></a>
### SSH クライアントユーティリティの使用

SSH サーバーへログインするには、`ssh(1)` を使い、そのサーバーに存在するユーザー名と、サーバーの IP アドレスまたはホスト名を指定します。指定したサーバーへの接続が初めての場合、最初にサーバーのフィンガープリントを確認するよう求められます。

```shell
# ssh user@example.com
```

出力は次のようになります。

```
The authenticity of host 'example.com (10.0.0.1)' can't be established.
ECDSA key fingerprint is 25:cc:73:b5:b3:96:75:3d:56:19:49:d2:5c:1f:91:3b.
Are you sure you want to continue connecting (yes/no)? yes
Permanently added 'example.com' (ECDSA) to the list of known hosts.
Password for user@example.com: user_password
```

SSH は、クライアントの接続時にサーバーの正当性を検証するため鍵フィンガープリントの仕組みを利用します。初回接続時にユーザーが `yes` と入力して鍵のフィンガープリントを受け入れると、その鍵のコピーがユーザーのホームディレクトリの `~/.ssh/known_hosts` に保存されます。以降のログイン試行では保存された鍵と照合され、サーバーの鍵が保存済みの鍵と一致しない場合、`ssh(1)` は警告を表示します。この場合は、接続を続行する前にまず鍵が変わった理由を確認する必要があります。

> **注**: この確認手順の詳細は本章の範囲外です。

リモートマシンとの間で安全にファイルをコピーするには、`scp(1)` を使います。

次の例では、リモートシステム上の `COPYRIGHT` を、ローカルシステムのカレントディレクトリに同じ名前でコピーします。

```shell
# scp user@example.com:/COPYRIGHT COPYRIGHT
```

出力は次のようになります。

```
Password for user@example.com: *******
COPYRIGHT            100% |*****************************|  4735
```

このホストのフィンガープリントはすでに検証済みであるため、ユーザーのパスワード入力を促す前にサーバーの鍵が自動的に検証されます。

`scp(1)` に渡す引数は `cp(1)` と似ています。コピー元のファイル（複数可）が第 1 引数、コピー先が第 2 引数です。ファイルはネットワーク越しに取得されるため、少なくとも 1 つのファイル引数は `user@host:<path_to_remote_file>` の形式をとります。ディレクトリを再帰的にコピーする際、`cp(1)` が `-R` を使うのに対し、`scp(1)` は `-r` を使う点に注意してください。

ファイルをコピーするための対話的セッションを開くには、`sftp(1)` を使います。`sftp(1)` セッション中に使えるコマンドの一覧は `sftp(1)` を参照してください。

<a id="security-ssh-keygen"></a>
### 鍵ベース認証

パスワードを使う代わりに、鍵を用いてリモートマシンへ接続するようにクライアントを設定できます。セキュリティ上の理由から、この方法が推奨されます。

認証鍵の生成には `ssh-keygen(1)` を使えます。公開鍵と秘密鍵のペアを生成するには、鍵の種類を指定してプロンプトに従います。覚えやすく、かつ推測されにくいパスフレーズで鍵を保護することが推奨されます。

```shell
% ssh-keygen -t rsa -b 4096
```

出力は次のようになります。

```
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa):
Created directory '/home/user/.ssh/.ssh'.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/user/.ssh/id_rsa.
Your public key has been saved in /home/user/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:54Xm9Uvtv6H4NOo6yjP/YCfODryvUU7yWHzMqeXwhq8 user@host.example.com
The key's randomart image is:
+---[RSA 2048]----+
|                 |
|                 |
|                 |
|        . o..    |
|       .S*+*o    |
|      . O=Oo . . |
|       = Oo= oo..|
|      .oB.* +.oo.|
|       =OE**.o..=|
+----[SHA256]-----+
```

秘密鍵は `~/.ssh/id_rsa` に、公開鍵は `~/.ssh/id_rsa.pub` に保存されます。鍵ベース認証を機能させるには、**公開**鍵をリモートマシンの `~/.ssh/authorized_keys` へコピーする必要があります。

> **警告**: OpenSSH の鍵にパスフレーズを設定することは重要なセキュリティ上の習慣であり、不正アクセスに対する追加の防御層を提供してシステム全体のセキュリティを高めます。
>
> 鍵を紛失したり盗まれたりした場合にも、もう 1 つの防御層として機能します。

<a id="security-ssh-tunneling"></a>
### SSH トンネリング

OpenSSH には、別のプロトコルを暗号化されたセッション内にカプセル化するトンネルを作成する機能があります。

次のコマンドは、`ssh(1)` にトンネルを作成するよう指示します。

```shell
% ssh -D 8080 user@example.com
```

この例では次のオプションを使っています。

`-D`
: ローカルの「ダイナミック」なアプリケーションレベルポートフォワーディングを指定します。

`user@foo.example.com`
: 指定したリモート SSH サーバー上で使用するログイン名です。

SSH トンネルは、指定した `localport` で `localhost` 上に待ち受けソケットを作成することで動作します。

この手法を使うと、SMTP、POP3、FTP などの暗号化されないさまざまな TCP プロトコルを安全に保護できます。

<a id="chapter-16-heading-23"></a>
### SSH サーバーの有効化

組み込みの SSH クライアントユーティリティに加えて、FreeBSD システムを SSH サーバーとして設定し、他の SSH クライアントからの接続を受け付けることもできます。

> **ヒント**: 先述のとおり、本章ではベースシステム版の OpenSSH を扱います。FreeBSD Ports に含まれる OpenSSH である `security/openssh-portable` と混同しないよう注意してください。

再起動後も SSH サーバーが有効になるようにするには、次のコマンドを実行します。

```shell
# sysrc sshd_enable="YES"
```

続いて、次のコマンドを実行してサービスを起動します。

```shell
# service sshd start
```

FreeBSD システムで `sshd` が初めて起動すると、システムのホスト鍵が自動的に生成され、そのフィンガープリントがコンソールに表示されます。初回接続時にユーザーがサーバーを検証できるよう、このフィンガープリントをユーザーに伝えてください。

`sshd` の起動時に利用できるオプションの一覧や、認証、ログイン処理、各種設定ファイルの詳細については `sshd(8)` を参照してください。

この時点で、システム上にユーザー名とパスワードを持つすべてのユーザーが `sshd` を利用できるはずです。

<a id="config-publickey-auth"></a>
### 公開鍵認証方式の設定

OpenSSH で公開鍵認証を使うように設定すると、認証に非対称暗号を活用することでセキュリティが向上します。この方法により、脆弱なパスワードや送信中の盗聴といったパスワード関連のリスクを排除し、さまざまなパスワード攻撃を防げます。ただし、不正アクセスを防ぐために秘密鍵を厳重に保護することが不可欠です。

最初のステップとして、`sshd(8)` が必要な認証方式を使うように設定します。

`/etc/ssh/sshd_config` を編集し、次の設定行のコメントを解除します。

```
PubkeyAuthentication yes
```

設定が終わったら、ユーザーは自分の**公開鍵**をシステム管理者へ送り、管理者がその鍵を `.ssh/authorized_keys` に追加します。鍵の生成手順は「[鍵ベース認証](#security-ssh-keygen)」で説明しています。

その後、次のコマンドを実行してサーバーを再起動します（訳注: 原文は「再起動（restart）」と書いていますが、実際のコマンドは設定ファイルを再読み込みする `reload` です）。

```shell
# service sshd reload
```

「[SSH サーバーのセキュリティオプション](#security-sshd-security-options)」で示すセキュリティ強化策もあわせて実施することを強く推奨します。

<a id="security-sshd-security-options"></a>
### SSH サーバーのセキュリティオプション

`sshd` は FreeBSD で最も広く使われているリモート管理手段ですが、公開ネットワークにさらされたシステムでは総当たり攻撃（ブルートフォース攻撃）や無差別スキャンによる攻撃が日常的に発生します。

これらの攻撃が成功するのを防ぐために利用できる追加パラメータがいくつかあり、本節で説明します。設定はすべて `/etc/ssh/sshd_config` で行います。

> **ヒント**: `/etc/ssh/sshd_config` と `/etc/ssh/ssh_config` を混同しないでください（前者のファイル名には余分な `d` が付いています）。前者はサーバー用、後者はクライアント用の設定ファイルです。利用可能なクライアント設定の一覧については `ssh_config(5)` を参照してください。

デフォルトでは、公開鍵認証とパスワード認証のどちらも使用できます。公開鍵認証**のみ**を許可するには（**強く推奨されます**）、次の変数を変更します。

```
PasswordAuthentication no
```

OpenSSH サーバー設定ファイルの `AllowUsers` キーワードを使って、SSH サーバーへログインできるユーザーと接続元を制限しておくのもよい方法です。たとえば、`user` が `192.168.1.32` からのみログインできるようにするには、`/etc/ssh/sshd_config` に次の行を追加します。

```
AllowUsers user@192.168.1.32
```

`user` がどこからでもログインできるようにするには、IP アドレスを指定せずにユーザー名だけを記述します。

```
AllowUsers user
```

複数のユーザーを指定する場合は、次のように同じ行に並べて記述します。

```
AllowUsers root@192.168.1.32 user
```

すべての変更を終えたら、サービスを再起動する前に次のコマンドを実行して設定に誤りがないか検証することを推奨します。

```shell
# sshd -t
```

設定ファイルが正しければ、何も出力されません。設定ファイルに誤りがある場合は、次のような出力が表示されます。

```
/etc/ssh/sshd_config: line 3: Bad configuration option: sdadasdasdasads
/etc/ssh/sshd_config: terminating, 1 bad configuration options
```

変更を行い、設定ファイルが正しいことを確認したら、次のコマンドを実行して `sshd` に設定ファイルを再読み込みさせます。

```shell
# service sshd reload
```

<a id="openssl"></a>
## OpenSSL

OpenSSL は、Secure Sockets Layer（SSL）および Transport Layer Security（TLS）ネットワークプロトコルと多くの暗号化ルーチンを実装した暗号ツールキットです。

`openssl` プログラムは、OpenSSL の暗号ライブラリが提供する各種暗号機能をシェルから利用するためのコマンドラインツールです。次の用途に使えます。

* 秘密鍵、公開鍵、パラメータの作成と管理
* 公開鍵暗号操作
* X.509 証明書、CSR、CRL の作成
* メッセージダイジェストの計算
* 暗号方式を用いた暗号化と復号
* SSL/TLS クライアントおよびサーバーのテスト
* S/MIME 署名付きまたは暗号化メールの処理
* タイムスタンプリクエスト、生成、および検証
* 暗号ルーチンのベンチマーク

OpenSSL の詳細については、無償公開されている [OpenSSL Cookbook](https://www.feistyduck.com/books/openssl-cookbook/) を参照してください。

<a id="generating-certificates"></a>
### 証明書の生成

OpenSSL は、[認証局（CA）](https://en.wikipedia.org/wiki/Certificate_authority)による検証を受ける証明書と、自己利用のための証明書のどちらの生成にも対応しています。

[CA](https://en.wikipedia.org/wiki/Certificate_authority) 用の有効な証明書を生成するには、次の引数を指定して `openssl(1)` コマンドを実行します。このコマンドは、カレントディレクトリに 2 つのファイルを作成します。証明書署名要求（CSR）である `req.pem` は [CA](https://en.wikipedia.org/wiki/Certificate_authority) へ送ることができ、CA は入力された資格情報を検証して要求に署名し、署名済み証明書を返します。2 つ目のファイル `cert.key` は証明書の秘密鍵であり、安全な場所へ保管する必要があります。これが他人の手に渡ると、ユーザーやサーバーになりすますために悪用されるおそれがあります。

証明書要求を生成するには、次のコマンドを実行します。

```shell
# openssl req -new -nodes -out req.pem -keyout cert.key -sha3-512 -newkey rsa:4096
```

出力は次のようになります。

```
Generating a RSA private key
..................................................................................................................................+++++
......................................+++++
writing new private key to 'cert.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:ES
State or Province Name (full name) [Some-State]:Valencian Community
Locality Name (eg, city) []:Valencia
Organization Name (eg, company) [Internet Widgits Pty Ltd]:My Company
Organizational Unit Name (eg, section) []:Systems Administrator
Common Name (e.g. server FQDN or YOUR name) []:localhost.example.org
Email Address []:user@FreeBSD.org

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:123456789
An optional company name []:Another name
```

一方、[CA](https://en.wikipedia.org/wiki/Certificate_authority) からの署名が不要な場合は、自己署名証明書を作成できます。これにより、カレントディレクトリ（訳注: 次のコマンド例では `-keyout` と `-out` で `/etc/ssl/` 配下を直接指定しています）に秘密鍵ファイル `cert.key` と証明書本体 `cert.crt` の 2 つの新しいファイルが作成されます。これらは、`root` のみが読み取れるディレクトリ、できれば `/etc/ssl/` 配下に配置する必要があります。これらのファイルにはパーミッション `0700` が適切であり、`chmod` で設定できます。

証明書を生成するには、次のコマンドを実行します。

```shell
# openssl req -new -x509 -days 365 -sha3-512 -keyout /etc/ssl/private/cert.key -out /etc/ssl/certs/cert.crt
```

出力は次のようになります。

```
Generating a RSA private key
........................................+++++
...........+++++
writing new private key to '/etc/ssl/private/cert.key'
Enter PEM pass phrase:
Verifying - Enter PEM pass phrase:
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:ES
State or Province Name (full name) [Some-State]:Valencian Community
Locality Name (eg, city) []:Valencia
Organization Name (eg, company) [Internet Widgits Pty Ltd]:My Company
Organizational Unit Name (eg, section) []:Systems Administrator
Common Name (e.g. server FQDN or YOUR name) []:localhost.example.org
Email Address []:user@FreeBSD.org
```

<a id="fips-provider"></a>
### FIPS プロバイダの設定

FreeBSD 14 以降のベースシステムへ OpenSSL 3 が取り込まれたことで、プロバイダモジュール（provider module）という新しい仕組みがシステムに導入されました。ライブラリに組み込まれたデフォルトのプロバイダモジュールに加えて、_legacy_ モジュールは現在オプション扱いとなった非推奨の暗号アルゴリズムを実装し、_fips_ モジュールは OpenSSL の実装を [FIPS](https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards) 標準規格群に含まれる暗号アルゴリズムに制限します。OpenSSL のこの部分は[特別な管理](https://www.openssl.org/docs/fips.html)を受けており、[関連するセキュリティ問題の一覧](https://www.openssl.org/news/fips-cve.html)が公開されているほか、定期的に [FIPS 140 検証プロセス](https://github.com/openssl/openssl/blob/master/README-FIPS.md)の対象となっています。[FIPS 検証済みバージョンの一覧](https://www.openssl.org/source/)も公開されており、利用者は OpenSSL の利用にあたって FIPS 準拠を確認できます。

重要な点として、`fips_module(7)` は追加のセキュリティ対策で保護されており、整合性チェックに合格しなければ使用できません。このチェックはローカルのシステム管理者が設定でき、設定後は OpenSSL 3 のすべての利用者がこのモジュールを読み込めるようになります。正しく設定されていない場合、FIPS モジュールは次のように失敗します。

```shell
# echo test | openssl aes-128-cbc -a -provider fips -pbkdf2
```

出力は次のようになります。

```
aes-128-cbc: unable to load provider fips
Hint: use -provider-path option or OPENSSL_MODULES environment variable.
00206124D94D0000:error:1C8000D5:Provider routines:SELF_TEST_post:missing config data:crypto/openssl/providers/fips/self_test.c:275:
00206124D94D0000:error:1C8000E0:Provider routines:ossl_set_error_state:fips module entering error state:crypto/openssl/providers/fips/self_test.c:373:
00206124D94D0000:error:1C8000D8:Provider routines:OSSL_provider_init_int:self test post failure:crypto/openssl/providers/fips/fipsprov.c:707:
00206124D94D0000:error:078C0105:common libcrypto routines:provider_init:init fail:crypto/openssl/crypto/provider_core.c:932:name=fips
```

このチェックは、`/etc/ssl/fipsmodule.cnf` にファイルを作成し、それを OpenSSL のメイン設定ファイル `/etc/ssl/openssl.cnf` から参照することで設定できます。OpenSSL にはこの作業を支援する `openssl-fipsinstall(1)` ユーティリティが用意されており、次のように使えます。

```shell
# openssl fipsinstall -module /usr/lib/ossl-modules/fips.so -out /etc/ssl/fipsmodule.cnf
```

出力は次のようになります。

```
INSTALL PASSED
```

続いて、次の目的で `/etc/ssl/openssl.cnf` を変更する必要があります。

* 上記で生成した `/etc/ssl/fipsmodule.cnf` ファイルをインクルードする
* FIPS モジュールを使用できるように公開する
* デフォルトモジュールを明示的に有効化する

```
[...]
# For FIPS
# Optionally include a file that is generated by the OpenSSL fipsinstall
# application. This file contains configuration data required by the OpenSSL
# fips provider. It contains a named section e.g. [fips_sect] which is
# referenced from the [provider_sect] below.
# Refer to the OpenSSL security policy for more information.
.include /etc/ssl/fipsmodule.cnf

[...]

# List of providers to load
[provider_sect]
default = default_sect
# The fips section name should match the section name inside the
# included fipsmodule.cnf.
fips = fips_sect

# If no providers are activated explicitly, the default one is activated implicitly.
# See man 7 OSSL_PROVIDER-default for more details.
#
# If you add a section explicitly activating any other provider(s), you most
# probably need to explicitly activate the default provider, otherwise it
# becomes unavailable in openssl.  As a consequence applications depending on
# OpenSSL may not work correctly which could lead to significant system
# problems including inability to remotely access the system.
[default_sect]
activate = 1
```

これにより、FIPS モジュールが実際に利用可能で機能していることを確認できるはずです。

```shell
# echo test | openssl aes-128-cbc -a -provider fips -pbkdf2
```

出力は次のようになります。

```
enter AES-128-CBC encryption password:
Verifying - enter AES-128-CBC encryption password:
U2FsdGVkX18idooW6e3LqWeeiKP76kufcOUClh57j8U=
```

この手順は、システムのアップデートを実行した後やベースシステムの OpenSSL に影響するセキュリティ修正を適用した後など、FIPS モジュールが変更されるたびに繰り返す必要があります。

<a id="kerberos5"></a>
## Kerberos

Kerberos は、潜在的に悪意あるネットワーク上でも安全に認証を提供する方法として、もともとマサチューセッツ工科大学（MIT）によって開発されたネットワーク認証プロトコルです。Kerberos プロトコルは強力な暗号技術を用いるため、クライアントとサーバーの双方がネットワーク上に暗号化されていない秘密情報を送信することなく互いの身元を証明できます。Kerberos は、身元確認を行うプロキシシステムであり、信頼できる第三者による認証システムと言えます。ユーザーが Kerberos で認証すると、その後の通信を暗号化してプライバシーとデータ整合性を保証できます。

Kerberos の唯一の機能は、ネットワーク上のユーザーとサーバーに対して安全な認証を提供することです。認可（authorization）や監査（auditing）の機能は提供しません。Kerberos は、認可や監査サービスを提供する他のセキュリティ手法と併用することが推奨されます。

現在のプロトコルバージョンはバージョン 5 であり、RFC 4120 に規定されています。このプロトコルには複数のフリーな実装があり、幅広いオペレーティングシステムに対応しています。MIT は現在も Kerberos パッケージの開発を続けています。これは米国では暗号製品として広く使われており、歴史的に米国の輸出規制の対象となってきました。FreeBSD では、MIT Kerberos は `security/krb5` パッケージまたは port として利用できます。Heimdal Kerberos 実装は、輸出規制を回避するために米国外で明示的に開発されました。Heimdal Kerberos ディストリビューションは FreeBSD のベースシステムに含まれており、より多くの設定オプションを備えた別のディストリビューションが Ports Collection の `security/heimdal` として利用できます。

Kerberos では、ユーザーとサービスは「プリンシパル（principal）」として識別され、「レルム（realm）」と呼ばれる管理上のグループに属します。一般的なユーザープリンシパルは `user@REALM` の形式になります（レルムは慣例的に大文字で表記されます）。

本節では、FreeBSD に含まれる Heimdal ディストリビューションを使って Kerberos を構築する方法を説明します。

Kerberos の導入例を示すため、名前空間は次のように設定します。

* DNS ドメイン（ゾーン）は `example.org`
* Kerberos レルムは `EXAMPLE.ORG`

> **注**: Kerberos を構築する際は、内部ネットワークのみで運用する場合であっても実際のドメイン名を使用してください。これにより DNS の問題を回避し、他の Kerberos レルムとの相互運用性を確保できます。

<a id="chapter-16-heading-30"></a>
### Heimdal KDC の構築

Key Distribution Center（KDC）は、Kerberos が提供する中央集権型の認証サービス、すなわちシステムの「信頼できる第三者」です。クライアントがサーバーに対して認証する際に使う Kerberos チケットを発行するコンピューターにあたります。KDC は Kerberos レルム内の他のすべてのコンピューターから信頼されるため、セキュリティ上の配慮が特に重要になります。KDC への直接アクセスは制限すべきです。

KDC の実行自体は計算リソースをほとんど必要としませんが、セキュリティ上の理由から、KDC としてのみ動作する専用マシンを用意することが推奨されます。

まず、次のように `security/heimdal` パッケージをインストールします。

```shell
# pkg install heimdal
```

次に、`sysrc` を使って `/etc/rc.conf` を次のように更新します。

```shell
# sysrc kdc_enable=yes
# sysrc kadmind_enable=yes
```

続いて、`/etc/krb5.conf` を次のように編集します。

```
[libdefaults]
    default_realm = EXAMPLE.ORG
[realms]
    EXAMPLE.ORG = {
	kdc = kerberos.example.org
	admin_server = kerberos.example.org
    }
[domain_realm]
    .example.org = EXAMPLE.ORG
```

この例では、KDC に完全修飾ホスト名 `kerberos.example.org` を使います。KDC のホスト名は DNS で名前解決できなければなりません。

Kerberos は、`/etc/krb5.conf` の `[realms]` セクションの代わりに DNS を使って KDC を検索することもできます。独自の DNS サーバーを持つ大規模組織では、上記の例を次のように簡略化できます。

```
[libdefaults]
      default_realm = EXAMPLE.ORG
[domain_realm]
    .example.org = EXAMPLE.ORG
```

あわせて、`example.org` のゾーンファイルに次の行を含めます。

```
_kerberos._udp      IN  SRV     01 00 88 kerberos.example.org.
_kerberos._tcp      IN  SRV     01 00 88 kerberos.example.org.
_kpasswd._udp       IN  SRV     01 00 464 kerberos.example.org.
_kerberos-adm._tcp  IN  SRV     01 00 749 kerberos.example.org.
_kerberos           IN  TXT     EXAMPLE.ORG
```

> **注**: クライアントが Kerberos サービスを見つけられるようにするには、完全に設定された `/etc/krb5.conf` を用意するか、**または**最小限に設定された `/etc/krb5.conf` と適切に設定された DNS サーバーの**両方**を用意する必要があります。

次に、すべてのプリンシパル（ユーザーおよびホスト）の鍵をマスターパスワードで暗号化して格納する Kerberos データベースを作成します。このパスワードは `/var/heimdal/m-key` に保存されるため覚えておく必要はなく、この目的には 45 文字のランダムなパスワードを使うのが妥当です。マスター鍵を作成するには、`kstash` を実行してパスワードを入力します。

```shell
# kstash
```

出力は次のようになります。

```
Master key: xxxxxxxxxxxxxxxxxxxxxxx
Verifying password - Master key: xxxxxxxxxxxxxxxxxxxxxxx
```

マスター鍵を作成したら、データベースを初期化します。Kerberos 管理ツール `kadmin(8)` は、KDC 上で `kadmin -l` として実行することで、`kadmind(8)` ネットワークサービスを経由せずデータベースを直接操作するモードで使えます。これにより、データベースを作成する前にそのデータベースへ接続しようとする「鶏と卵」の問題を回避できます。`kadmin` プロンプトで `init` を使い、レルムの初期データベースを作成します。

```shell
# kadmin -l
kadmin> init EXAMPLE.ORG
Realm max ticket life [unlimited]:
```

最後に、`kadmin` を開いたまま `add` を使って最初のプリンシパルを作成します。プリンシパルのオプションは後で `modify` を使って変更できるため、ここではデフォルトのオプションのままで構いません。プロンプトで `?` と入力すると利用可能なオプションが表示されます。

```shell
kadmin> add tillman
```

出力は次のようになります。

```
Max ticket life [unlimited]:
Max renewable life [unlimited]:
Principal expiration time [never]:
Password expiration time [never]:
Attributes []:
Password: xxxxxxxx
Verifying password - Password: xxxxxxxx
```

続いて、次のコマンドを実行して KDC サービスを起動します。

```shell
# service kdc start
# service kadmind start
```

この時点では Kerberos 対応デーモンはまだ稼働していませんが、作成したばかりのプリンシパルのチケットを取得することで、KDC が機能しているかを確認できます。

```shell
% kinit tillman
```

出力は次のようになります。

```
tillman@EXAMPLE.ORG's Password:
```

`klist` を使って、チケットが正常に取得できたことを確認します。

```shell
% klist
```

出力は次のようになります。

```
Credentials cache: FILE:/tmp/krb5cc_1001
	Principal: tillman@EXAMPLE.ORG

  Issued                Expires               Principal
Aug 27 15:37:58 2013  Aug 28 01:37:58 2013  krbtgt/EXAMPLE.ORG@EXAMPLE.ORG
```

テストが終わったら、一時的なチケットは破棄できます。

```shell
% kdestroy
```

<a id="chapter-16-heading-31"></a>
### Kerberos を使用するサーバーの設定

Kerberos 認証を使うようにサーバーを設定する最初のステップは、`/etc/krb5.conf` に正しい設定が入っていることを確認することです。KDC 上のものをそのまま使うか、新しいシステム上で作り直します。

次に、サーバー上に `/etc/krb5.keytab` を作成します。これはサービスの「Kerberos 化」における中核作業であり、サービスと KDC の間で共有される秘密情報を生成する処理にあたります。その秘密情報は暗号鍵であり、「keytab」に格納されます。keytab にはサーバーのホスト鍵が含まれており、サーバーと KDC が互いの身元を検証できるようになります。鍵が外部に漏れるとサーバーのセキュリティが破られるため、安全な方法でサーバーへ転送しなければなりません。通常、`keytab` は管理者の信頼できるマシン上で `kadmin` を使って生成し、`scp(1)` などで安全にサーバーへ転送します。求めるセキュリティポリシーに沿うのであれば、サーバー上で直接作成することも可能です。

keytab を安全な方法でサーバーへ転送することは非常に重要です。この鍵が第三者に知られると、その第三者はサーバーに対して任意のユーザーになりすますことができてしまいます。KDC データベース内のホストプリンシパルのエントリも `kadmin` を使って作成するため、サーバー上で直接 `kadmin` を使う方法は便利です。

もちろん、`kadmin` 自体も Kerberos 対応サービスです。ネットワークサービスへの認証には Kerberos チケットが必要ですが、`kadmin` を実行しているユーザーが本当に本人であること（セッションが乗っ取られていないこと）を確実にするため、`kadmin` は新しいチケットを取得するパスワードの入力を求めます。`kadmin` サービスに対して認証するプリンシパルは、`/var/heimdal/kadmind.acl` で指定されたとおり、`kadmin` インターフェースの使用を許可されている必要があります。アクセス制御リストの設計に関する詳細は、`info heimdal` の「Remote administration」の節を参照してください。リモートの `kadmin` アクセスを有効にする代わりに、管理者がローカルコンソールや `ssh(1)` で KDC に安全に接続し、`kadmin -l` を使ってローカルで管理作業を行うこともできます。

`/etc/krb5.conf` を配置したら、`kadmin` 内で `add --random-key` を実行します。これによりサーバーのホストプリンシパルがデータベースに追加されますが、ホストプリンシパル鍵のコピーはまだ keytab へ抽出されません。keytab を生成するには、`ext` を使ってサーバーのホストプリンシパル鍵を専用の keytab に抽出します。

```shell
# kadmin
```

出力は次のようになります。

```
kadmin> add --random-key host/myserver.example.org
Max ticket life [unlimited]:
Max renewable life [unlimited]:
Principal expiration time [never]:
Password expiration time [never]:
Attributes []:
kadmin> ext_keytab host/myserver.example.org
kadmin> exit
```

`ext_keytab` はデフォルトで抽出した鍵を `/etc/krb5.keytab` に保存します。これは Kerberos 化するサーバー上で直接実行する場合には適切ですが、別の場所で keytab を抽出する場合は `--keytab path/to/file` 引数を使用する必要があります。

```shell
# kadmin
```

出力は次のようになります。

```
kadmin> ext_keytab --keytab=/tmp/example.keytab host/myserver.example.org
kadmin> exit
```

その後、`scp(1)` またはリムーバブルメディアを使って、その keytab をサーバーへ安全にコピーできます。システムの keytab に不要な鍵を追加しないよう、必ずデフォルト以外の keytab 名を指定してください。

この時点で、サーバーは `krb5.keytab` に保存された共有鍵を使って KDC からの暗号化メッセージを読み取れるようになります。これで Kerberos を使うサービスを有効化する準備が整いました。もっとも一般的なサービスの 1 つが `sshd(8)` であり、GSS-API 経由で Kerberos に対応しています。`/etc/ssh/sshd_config` に次の行を追加します。

```
GSSAPIAuthentication yes
```

この変更を行った後は、新しい設定を反映させるために `service sshd restart` で `sshd(8)` を再起動する必要があります。

<a id="chapter-16-heading-32"></a>
### Kerberos を使用するクライアントの設定

サーバーの場合と同様に、クライアントにも `/etc/krb5.conf` の設定が必要です。ファイルを（安全に）所定の場所へコピーするか、必要に応じて再作成してください。

クライアント上で `kinit`、`klist`、`kdestroy` を使い、既存のプリンシパルに対するチケットの取得、表示、削除を行ってクライアントの動作をテストします。Kerberos アプリケーションは、Kerberos 対応サーバーにも接続できるはずです。チケットの取得はできるのにサーバーへ接続できない場合、問題はクライアントや KDC ではなくサーバー側にある可能性が高いです。Kerberos 対応の `ssh(1)` の場合、GSS-API はデフォルトで無効になっているため、`ssh -o GSSAPIAuthentication=yes hostname` を使ってテストしてください。

Kerberos 対応アプリケーションをテストする際は、`tcpdump` などのパケットスニファーを使い、機密情報が平文で送信されていないことを確認してみてください。

さまざまな Kerberos クライアントアプリケーションが利用できます。認証に SASL を使うアプリケーションが GSS-API 機構も利用できるようにするブリッジの登場により、Jabber クライアントから IMAP クライアントまで、幅広いクライアントアプリケーションが認証に Kerberos を使えるようになっています。

レルム内のユーザーは通常、自身の Kerberos プリンシパルがローカルのユーザーアカウントに対応付けられています。場合によっては、一致する Kerberos プリンシパルを持たない人にローカルユーザーアカウントへのアクセスを許可したいことがあります。たとえば、`tillman@EXAMPLE.ORG` がローカルユーザーアカウント `webdevelopers` へアクセスする必要がある場合や、他のプリンシパルもそのローカルアカウントへアクセスする必要がある場合です。

ユーザーのホームディレクトリに配置する `.k5login` および `.k5users` ファイルを使うと、この問題を解決できます。たとえば、次の内容の `.k5login` を `webdevelopers` のホームディレクトリに置くと、パスワードを共有しなくても、記載された両方のプリンシパルがそのアカウントへアクセスできるようになります。

```
tillman@example.org
jdoe@example.org
```

`.k5users` の詳細は `ksu(1)` を参照してください。

<a id="chapter-16-heading-33"></a>
### MIT との違い

MIT 実装と Heimdal 実装の大きな違いは、`kadmin` のコマンドセットが同等ではあっても異なり、使用するプロトコルも異なる点です。KDC が MIT の場合、Heimdal 版の `kadmin` を使って KDC をリモート管理することはできず、その逆も同様です。

クライアントアプリケーションでも、同じ作業を行うためのコマンドラインオプションがわずかに異なる場合があります。[http://web.mit.edu/Kerberos/www/](http://web.mit.edu/Kerberos/www/) の手順に従うことが推奨されます。パスの問題にも注意してください。MIT port はデフォルトで `/usr/local/` にインストールされるため、`PATH` でシステムディレクトリが先に並んでいると、MIT 版ではなく FreeBSD ベースシステムのアプリケーションが実行されてしまいます。

FreeBSD 上で MIT Kerberos を KDC として使用する場合は、次のコマンドを実行して必要な設定を `/etc/rc.conf` に追加します。

```shell
# sysrc kdc_program="/usr/local/sbin/krb5kdc"
# sysrc kadmind_program="/usr/local/sbin/kadmind"
# sysrc kdc_flags=""
# sysrc kdc_enable="YES"
# sysrc kadmind_enable="YES"
```

<a id="chapter-16-heading-34"></a>
### Kerberos のヒント、コツ、トラブルシューティング

Kerberos の設定やトラブルシューティングを行う際は、次の点に留意してください。

* Ports から導入した Heimdal または MIT Kerberos を使う場合は、システム版より先に ports 版のクライアントアプリケーションが見つかるように `PATH` を設定してください。
* レルム内のすべてのコンピューターで時刻設定が同期されていないと、認証が失敗することがあります。NTP を使って時刻を同期する方法は「[NTP による時刻同期](33-network-servers.md#network-ntp)」で解説しています。
* ホスト名を変更した場合は、`host/` プリンシパルを変更して keytab を更新する必要があります。これは、Apache の `www/mod_auth_kerb` で使われる `HTTP/` プリンシパルなどの特殊な keytab エントリにも当てはまります。
* レルム内のすべてのホストは DNS で正引き・逆引きの双方が解決できるか、最低限 `/etc/hosts` に記載されている必要があります。CNAME も動作しますが、A レコードと PTR レコードが正しく設定されていなければなりません。名前解決できないホストに対するエラーメッセージは直感的ではなく、`Kerberos5 refuses authentication because Read req failed: Key table entry not found` となります。
* KDC のクライアントとして動作する一部のオペレーティングシステムでは、`ksu` のパーミッションが setuid `root` に設定されていません。その場合、`ksu` は動作しません。これは KDC のエラーではなくパーミッションの問題です。
* MIT Kerberos で、デフォルトの 10 時間を超えるチケット有効期間をプリンシパルに許可するには、`kadmin(8)` プロンプトで `modify_principal` を使い、対象プリンシパルと `krbtgt` プリンシパルの両方の `maxlife` を変更します。その後、そのプリンシパルは `kinit -l` を使ってより長い有効期間のチケットを要求できます。
* ワークステーションから `kinit` を実行しながら KDC 上でトラブルシューティングのためにパケットスニファーを動かすと、パスワードを入力する前であっても Ticket Granting Ticket（TGT）が即座に送信されるのが見えます。これは、Kerberos サーバーが未認証の要求に対しても TGT をそのまま送信するためです。ただし、すべての TGT はユーザーのパスワードから導出された鍵で暗号化されています。ユーザーがパスワードを入力しても、そのパスワード自体は KDC へは送信されず、`kinit` がすでに取得した TGT を復号するために使われます。復号の結果、有効なタイムスタンプを持つ正当なチケットが得られれば、ユーザーは有効な Kerberos 資格情報を得たことになります。これらの資格情報には、今後 Kerberos サーバーと安全な通信を確立するためのセッション鍵と、Kerberos サーバー自身の鍵で暗号化された実際の TGT が含まれます。この 2 層目の暗号化により、Kerberos サーバーは各 TGT の正当性を検証できます。
* ホストプリンシパルもチケットの有効期間を長く持つことができます。ユーザープリンシパルの有効期間が 1 週間であっても、接続先ホストの有効期間が 9 時間であれば、ユーザーキャッシュ内のホストプリンシパルが期限切れになり、チケットキャッシュが期待どおりに動作しなくなります。
* `kadmind(8)` に記載されているように、特定の脆弱なパスワードの使用を防ぐ目的で `krb5.dict` を設定する場合、これが適用されるのはパスワードポリシーが割り当てられたプリンシパルだけである点に注意してください。`krb5.dict` の書式は 1 行につき 1 文字列です。`/usr/share/dict/words` へのシンボリックリンクを作成すると便利な場合があります。

<a id="chapter-16-heading-35"></a>
### Kerberos の制約の緩和

Kerberos は「すべてか無か（all or nothing）」のアプローチであるため、ネットワーク上で有効化されているすべてのサービスを Kerberos 対応にするか、あるいは別の手段でネットワーク攻撃から保護しなければなりません。これは、ユーザーの資格情報が盗まれて再利用されるのを防ぐためです。たとえば、すべてのリモートシェルで Kerberos を有効にしているにもかかわらず、Kerberos 非対応の POP3 メールサーバーが平文でパスワードを送信している場合がそれにあたります。

KDC は単一障害点となります。設計上、KDC はそのマスターパスワードデータベースと同等に安全でなければなりません。KDC 上では他のサービスを一切動かさず、物理的にも保護すべきです。Kerberos は KDC 上のファイルとして保存された同じマスター鍵で全パスワードを暗号化するため、危険性は高くなります。

マスター鍵が漏洩したとしても、それ自体は一般に懸念されるほど致命的ではありません。マスター鍵は、Kerberos データベースの暗号化と乱数生成器のシードとしてのみ使われます。KDC へのアクセス自体が安全に保たれている限り、攻撃者がマスター鍵だけを使ってできることは多くありません。

KDC が利用できなくなると認証を実行できなくなるため、ネットワークサービスも利用できなくなります。これは、1 台のマスター KDC と 1 台以上のスレーブを用意し、さらに PAM を使ったセカンダリ認証やフォールバック認証を慎重に実装することで緩和できます。

Kerberos ではユーザー、ホスト、サービスが相互に認証を行えますが、ユーザー、ホスト、サービスに対して KDC 自身の正当性を認証する仕組みはありません。つまり、トロイの木馬化された `kinit` があれば、すべてのユーザー名とパスワードを記録できてしまいます。`security/tripwire` のようなファイルシステム整合性チェックツールを使うことで、このリスクを軽減できます。

<a id="chapter-16-heading-36"></a>
### 参考資料と詳細情報

* [The Kerberos FAQ](http://www.faqs.org/faqs/Kerberos-faq/general/preamble.html)
* [Designing an Authentication System: a Dialog in Four Scenes](http://web.mit.edu/Kerberos/www/dialogue.html)
* [RFC 4120, The Kerberos Network Authentication Service (V5)](https://www.ietf.org/rfc/rfc4120.txt)
* [MIT Kerberos ホームページ](http://web.mit.edu/Kerberos/www/)
* [Heimdal Kerberos プロジェクト Wiki ページ](https://github.com/heimdal/heimdal/wiki)

<a id="tcpwrappers"></a>
## TCP Wrappers

TCP Wrappers は、ホストベースのネットワークアクセス制御システムです。TCP Wrappers は、着信したネットワーク要求が実際のネットワークサービスに到達する前にそれを横取りし、設定ファイルにあらかじめ定義されたルールに基づいて、送信元 IP アドレスへのアクセスを許可するか拒否するかを判定します。

ただし、TCP Wrappers は基本的なアクセス制御を提供するものの、より強固なセキュリティ対策の代替として考えるべきではありません。包括的な保護のためには、適切なユーザー認証の運用や侵入検知システムとあわせて、ファイアウォールなどの高度な技術を用いることが推奨されます。

<a id="tcpwrappers-initial-configuration"></a>
### 初期設定

TCP Wrappers は `inetd(8)` でデフォルトで有効になっています。したがって、最初のステップは次のコマンドを実行して `inetd(8)` を有効にすることです。

```shell
# sysrc inetd_enable="YES"
# service inetd start
```

続いて、`/etc/hosts.allow` を適切に設定します。

> **警告**: TCP Wrappers の他の実装とは異なり、FreeBSD では `hosts.deny` の使用は非推奨です。設定オプションはすべて `/etc/hosts.allow` に記述してください。

もっとも単純な設定では、`/etc/hosts.allow` 内のオプションに応じて、デーモンへの接続ポリシーを許可または遮断のいずれかに設定します。FreeBSD のデフォルト設定では、`inetd` から起動されるデーモンへの接続がすべて許可されています。

基本的な設定は通常 `daemon : address : action` の形式をとります。ここで `daemon` は `inetd` が起動したデーモン、`address` は有効なホスト名、IP アドレス、または角括弧（`[ ]`）で囲んだ IPv6 アドレス、`action` は `allow` または `deny` のいずれかです。TCP Wrappers は先頭一致（first rule match）のセマンティクスを採用しており、設定ファイルを先頭から走査して一致するルールを探します。一致するルールが見つかるとそのルールが適用され、検索処理はそこで終了します。

たとえば、`mail/qpopper` デーモン経由の POP3 接続を許可するには、`/etc/hosts.allow` に次の行を追記します。

```
# This line is required for POP3 connections:
qpopper : ALL : allow
```

このファイルを編集したら、毎回 `inetd` を再起動してください。

```shell
# service inetd restart
```

<a id="tcpwrappers-advanced-config"></a>
### 高度な設定

TCP Wrappers には、接続の扱い方をより細かく制御するための高度なオプションが用意されています。場合によっては、特定のホストやデーモン接続に対してコメントを返すのが適切なこともあります。あるいは、ログエントリを記録したり、管理者へメールを送信したりしたい場合もあります。ローカル接続に対してのみサービスを使えるようにする必要がある場面もあるでしょう。これらはいずれも、ワイルドカード、展開文字、外部コマンド実行と呼ばれる設定オプションを用いることで実現できます。ワイルドカードとそれに関連する機能の詳細は、`hosts_access(5)` を参照してください。

<a id="fs-acl"></a>
## アクセス制御リスト（ACL）

アクセス制御リスト（ACL）は、ファイルまたはディレクトリ単位でユーザーやグループに対するきめ細かなアクセス制御を可能にすることで、従来の UNIX® ファイルパーミッションを拡張します。各 ACL エントリでは、ユーザーまたはグループと、それに紐づく読み取り・書き込み・実行などの権限を定義します。FreeBSD には ACL を管理するための `getfacl(1)` や `setfacl(1)` などのコマンドが用意されています。

ACL は、標準のパーミッションよりも具体的なアクセス制御が求められる場面で有用であり、マルチユーザー環境や共有ホスティングでよく使われます。ただし、複雑さが増すことは避けられないため、求めるセキュリティ特性が確実に満たされるよう慎重な設計が必要です。

> **注**: FreeBSD は、UFS と OpenZFS の双方で NFSv4 ACL の実装に対応しています。`setfacl(1)` コマンドの一部の引数は POSIX ACL のみで動作し、別の引数は NFSv4 ACL で動作する点に注意してください。

<a id="acl-enabling-support-ufs"></a>
### UFS での ACL サポートの有効化

ACL はマウント時の管理用フラグ `acls` によって有効化され、このフラグは `/etc/fstab` に追加できます。

したがって、`/etc/fstab` を開き、options 欄に次のように `acls` フラグを追加する必要があります。

```
# Device        Mountpoint        FStype    Options     Dump      Pass#
/dev/ada0s1a    /                 ufs       rw,acls     1         1
```

<a id="security-acl-info"></a>
### ACL 情報の取得

`getfacl(1)` を使うと、ファイルやディレクトリの ACL を確認できます。

たとえば、`~/test` ファイルの ACL 設定を表示するには、次のコマンドを実行します。

```shell
% getfacl test
```

NFSv4 ACL を使用している場合、出力は次のようになります。

```
# file: test
# owner: freebsduser
# group: freebsduser
            owner@:rw-p--aARWcCos:-------:allow
            group@:r-----a-R-c--s:-------:allow
         everyone@:r-----a-R-c--s:-------:allow
```

また、POSIX.1e ACL を使用している場合、出力は次のようになります。

```
# file: test
# owner: freebsduser
# group: freebsduser
user::rw-
group::r--
other::r--
```

<a id="security-working-acls"></a>
### ACL の操作

`setfacl(1)` を使うと、ファイルやディレクトリに ACL を追加、変更、または削除できます。

前述のとおり、`setfacl(1)` の一部の引数は NFSv4 ACL では動作せず、逆も同様です。本節では POSIX ACL と NFSv4 ACL それぞれに対するコマンドの実行方法を説明し、双方の例を示します。

たとえば、POSIX.1e デフォルト ACL の必須要素を設定するには次のようにします。

```shell
% setfacl -d -m u::rwx,g::rx,o::rx,mask::rwx directory
```

次の例では、`file` に対してファイル所有者の POSIX.1e ACL エントリに読み取り・書き込み・実行権限を設定し、`mail` グループに読み取り・書き込み権限を設定します。

```shell
% setfacl -m u::rwx,g:mail:rw file
```

直前の例と同じことを NFSv4 ACL で行うには次のようにします。

```shell
% setfacl -m owner@:rwxp::allow,g:mail:rwp::allow file
```

POSIX.1e ACL において、`file` から必須の 3 エントリ以外のすべての ACL エントリを削除するには次のようにします。

```shell
% setfacl -bn file
```

NFSv4 ACL ですべての ACL エントリを削除するには次のようにします。

```shell
% setfacl -b file
```

これらのコマンドで利用できるオプションの詳細は、`getfacl(1)` および `setfacl(1)` を参照してください。

<a id="capsicum"></a>
## Capsicum

Capsicum は、ハイブリッドケーパビリティシステムモデルを実装した軽量な OS ケーパビリティおよびサンドボックスフレームワークです。ケーパビリティとは、委譲可能であり、かつ操作を実行する際に提示しなければならない偽造不可能な権限トークンのことです。Capsicum はファイル記述子をケーパビリティとして扱えるようにします。

Capsicum はアプリケーションやライブラリの区画化（compartmentalisation）、すなわちセキュリティポリシーを実装してソフトウェア脆弱性の影響を限定する目的で大きなソフトウェア群を隔離（サンドボックス化）されたコンポーネントへ分解するために利用できます。

<a id="security-accounting"></a>
## プロセスアカウンティング

プロセスアカウンティングは、管理者がシステムリソースの使用状況やユーザーごとの割り当て状況を追跡し、システムの監視を行って、ユーザーの実行コマンドを最小限記録できるようにするセキュリティ手法です。

プロセスアカウンティングには利点と欠点の双方があります。利点の 1 つは、侵入経路を侵入点まで絞り込める可能性がある点です。欠点は、プロセスアカウンティングによって生成されるログの量と、それが必要とするディスク容量です。本節では、管理者がプロセスアカウンティングの基本を把握できるように解説します。

> **注**: よりきめ細かな監査記録が必要な場合は、[Security Event Auditing](20-audit.md#audit) を参照してください。

<a id="chapter-16-heading-46"></a>
### プロセスアカウンティングの有効化と利用

プロセスアカウンティングを利用する前に、次のコマンドを使って有効にする必要があります。

```shell
# sysrc accounting_enable=yes
# service accounting start
```

アカウンティング情報は `/var/account` 内のファイルに保存されます。このディレクトリは、アカウンティングサービスを初めて起動した際に必要であれば自動的に作成されます。これらのファイルには、すべてのユーザーが発行した全コマンドを含む機密情報が含まれます。ファイルへの書き込みアクセスは `root` のみに制限されており、読み取りアクセスは `root` と `wheel` グループのメンバーに制限されています。`wheel` のメンバーによる読み取りも防ぐには、`/var/account` ディレクトリのモードを変更して `root` のみがアクセスできるようにしてください。

有効化すると、アカウンティングは CPU 統計情報や実行されたコマンドなどの情報の追跡を開始します。アカウンティングログはすべて人間が直接読めない形式になっており、`sa(8)` を使って閲覧できます。オプションを何も指定せずに実行すると、`sa(8)` はユーザーごとの呼び出し回数、総経過時間（分）、総 CPU 時間およびユーザー時間（分）、I/O 操作の平均回数などの情報を出力します。出力を制御する利用可能なオプションの一覧は、`sa(8)` を参照してください。

ユーザーが発行したコマンドを表示するには、`lastcomm` を使います。

たとえば、次のコマンドは端末 `ttyp1` 上で `trhodes` が `ls` を使用した履歴をすべて出力します。

```shell
# lastcomm ls trhodes ttyp1
```

この他にも有用なオプションが多数存在し、`lastcomm(1)`、`acct(5)`、`sa(8)` で説明されています。

<a id="security-resourcelimits"></a>
## リソース制限

FreeBSD におけるリソース制限とは、プロセスやユーザーに対する各種システムリソースの割り当てを制御・管理する仕組みを指します。これらの制限は、単一のプロセスやユーザーが過剰なリソースを消費してパフォーマンス低下やシステム不安定を引き起こすのを防ぐために設計されています。リソース制限により、システム上で稼働しているすべてのプロセスとユーザーの間で公平なリソース配分を保てます。

FreeBSD には、管理者が個々のユーザーが使用できるシステムリソース量を制限するための方法がいくつか用意されています。

従来の方法では、`/etc/login.conf` を編集してログインクラスを定義します。この方法も引き続きサポートされていますが、変更を加えるたびに、このファイルを編集し、リソースデータベースを再構築し、必要に応じて `/etc/master.passwd` を変更して、パスワードデータベースを再構築するという複数の手順が必要になります。設定対象のユーザー数によっては、時間がかかることがあります。

`rctl(8)` を使うと、よりきめ細かな方法でリソース制限を制御できます。このコマンドはユーザー単位の制限だけでなく、プロセスや jail に対するリソース制約の設定にも対応しています。

本節では、従来の方法から順に、リソースを制御するための両方の方法を説明します。

<a id="security-resource-limits-types"></a>
### リソースの種類

FreeBSD では、次のようなさまざまな種類のリソースに対して制限を設定できます。

**表: リソースの種類**

| 種類 | 説明 |
|---|---|
| CPU 時間（CPU Time） | プロセスが消費できる CPU 時間を制限します |
| メモリ（Memory） | プロセスが使用できる物理メモリ量を制御します |
| オープンファイル数（Open Files） | プロセスが同時に開けるファイル数を制限します |
| プロセス数（Processes） | ユーザーまたはプロセスが生成できるプロセス数を制御します |
| ファイルサイズ（File Size） | プロセスが作成できるファイルの最大サイズを制限します |
| コアダンプ（Core Dumps） | プロセスによるコアダンプファイルの生成を許可するかどうかを制御します |
| ネットワークリソース（Network Resources） | プロセスが使用できるネットワークリソース（ソケットなど）の量を制限します |

すべての種類の完全な一覧は、`login.conf(5)` および `rctl(8)` を参照してください。

<a id="users-limiting"></a>
### ログインクラスの設定

従来の方法では、ログインクラスとそこに適用するリソース制限を `/etc/login.conf` で定義します。各ユーザーアカウントにはログインクラスを割り当てることができ、デフォルトのログインクラスは `default` です。各ログインクラスには、一連のログインケーパビリティ（login capability）が関連付けられています。ログインケーパビリティは `name=value` のペアであり、`name` は既知の識別子、`value` は `name` に応じて適切に処理される任意の文字列です。

リソース制限を設定する最初のステップとして、次のコマンドを実行して `/etc/login.conf` を開きます。

```shell
# ee /etc/login.conf
```

次に、変更対象となるユーザークラスのセクションを探します。この例ではユーザークラス名を `limited` とし、存在しない場合は新規に作成します。

```
limited:\
        :maxproc=50:\
        :tc=default:
```

1. ユーザークラスの名前。
2. `limited` クラスに属するユーザーに対して、最大プロセス数（`maxproc`）を 50 に設定します。
3. このユーザークラスが `default` クラスからデフォルト設定を継承することを示します。

`/etc/login.conf` ファイルを変更したら、`cap_mkdb(1)` を実行して、FreeBSD がこれらの設定を適用するために使うデータベースを生成します。

```shell
# cap_mkdb /etc/login.conf
```

目的のユーザーのクラスを変更するには、次のコマンドを実行して `chpass(1)` を使用します。

```shell
# chpass username
```

テキストエディタが開くので、次のように新しい `limited` クラスを設定します。

```
#Changing user information for username.
Login: username
Password: $6$2H.419USdGaiJeqK$6kgcTnDadasdasd3YnlNZsOni5AMymibkAfRCPirc7ZFjjv
DVsKyXx26daabdfqSdasdsmL/ZMUpdHiO0
Uid [#]: 1001
Gid [# or name]: 1001
Change [month day year]:
Expire [month day year]:
Class: limited
Home directory: /home/username
Shell: /bin/sh
Full Name: User &
Office Location:
Office Phone:
Home Phone:
Other information:
```

これで、`limited` クラスに割り当てられたユーザーの最大プロセス数の上限が 50 になります。これは `/etc/login.conf` ファイルを使ってリソース制限を設定する一例にすぎません。

`/etc/login.conf` ファイルを変更した後は、変更を有効にするためにユーザーが一度ログアウトして再度ログインする必要がある点に注意してください。また、システム設定ファイルを編集する際、特に特権アクセスを用いる場合は常に慎重に作業してください。

<a id="security-rctl"></a>
### リソース制限の有効化と設定

`rctl(8)` システムを使うと、個々のプロセスやユーザーに対してよりきめ細かくリソース制限を設定・管理できます。ユーザークラスに関係なく、特定のプロセスやユーザーへ動的にリソース制限を割り当てることが可能です。

`rctl(8)` を使うための最初のステップは、`/boot/loader.conf` に次の行を追加して有効にし、システムを再起動することです。

```
kern.racct.enable=1
```

続いて、次のコマンドを実行して `rctl(8)` サービスを有効化し、起動します。

```shell
# sysrc rctl_enable="YES"
# service rctl start
```

その後、`rctl(8)` を使ってシステムのルールを設定できます。

ルール構文（`rctl.conf(5)`）は、subject（主体）、subject-id（主体 ID）、resource（リソース）、action（アクション）を使って指定します。次のルール例を参照してください。

```
subject:subject-id:resource:action=amount/per
```

たとえば、ユーザーが 10 個を超えるプロセスを作成できないように制限するには、次のコマンドを実行します。

```shell
# rctl -a user:username:maxproc:deny=10/user
```

適用されているリソース制限を確認するには、`rctl(8)` コマンドを実行します。

```shell
# rctl
```

出力は次のようになります。

```
user:username:maxproc:deny=10
```

ルールを `/etc/rctl.conf` に追加しておくと、再起動後も設定が維持されます。書式は先頭のコマンドを除いたルールそのものです。たとえば、先ほどのルールは次のように追加できます。

```
user:username:maxproc:deny=10
```

<a id="security-pkg"></a>
## サードパーティ製ソフトウェアのセキュリティ問題の監視

近年、セキュリティの世界では脆弱性評価の扱いが大きく進歩しました。現在利用できるほぼすべてのオペレーティングシステムにサードパーティ製ユーティリティが導入・設定されるようになり、システムへの侵入の脅威は高まっています。

脆弱性評価はセキュリティにおける重要な要素です。FreeBSD はベースシステムについてセキュリティ勧告を公開していますが、すべてのサードパーティ製ユーティリティに対して勧告を出すことは FreeBSD Project の対応能力を超えています。しかし、サードパーティ製ソフトウェアの脆弱性リスクを軽減し、既知のセキュリティ問題を管理者に警告する方法があります。FreeBSD のアドオンユーティリティである `pkg` には、まさにこの目的のためのオプションが備わっています。

`pkg` はセキュリティ問題に関するデータベースに問い合わせを行います。このデータベースは FreeBSD セキュリティチームと ports 開発者によって更新・保守されています。

インストール時には、`pkg audit` データベースを保守するための `periodic(8)` 設定ファイルが提供され、データベースを最新の状態に保つための自動化された手段も用意されています。

インストール後、Ports Collection の一部として導入したサードパーティ製ユーティリティを監査したいときはいつでも、次のコマンドを実行してデータベースを更新し、インストール済みパッケージの既知の脆弱性を確認できます。

```shell
% pkg audit -F
```

出力は次のようになります。

```
vulnxml file up-to-date
chromium-116.0.5845.96_1 is vulnerable:
  chromium -- multiple vulnerabilities
  CVE: CVE-2023-4431
  CVE: CVE-2023-4427
  CVE: CVE-2023-4428
  CVE: CVE-2023-4429
  CVE: CVE-2023-4430
  WWW: https://vuxml.FreeBSD.org/freebsd/5fa332b9-4269-11ee-8290-a8a1599412c6.html

samba413-4.13.17_5 is vulnerable:
  samba -- multiple vulnerabilities
  CVE: CVE-2023-3347
  CVE: CVE-2023-34966
  CVE: CVE-2023-34968
  CVE: CVE-2022-2127
  CVE: CVE-2023-34967
  WWW: https://vuxml.FreeBSD.org/freebsd/441e1e1a-27a5-11ee-a156-080027f5fec9.html

2 problem(s) in 2 installed package(s) found.
```

表示された URL を Web ブラウザーで開くことで、管理者はその脆弱性に関する詳しい情報を得られます。

そこには FreeBSD の port バージョン基準で影響を受けるバージョンや、セキュリティ勧告を掲載している他の Web サイトへの情報も含まれています。

<a id="security-advisories"></a>
## FreeBSD セキュリティ勧告

高品質なオペレーティングシステムを提供する多くの開発元と同様に、FreeBSD Project にもセキュリティチームがあり、各 FreeBSD リリースのサポート終了（End-of-Life: EoL）日を決定し、まだ EoL に達していないサポート対象リリースへセキュリティアップデートを提供する役割を担っています。FreeBSD セキュリティチームやサポート対象リリースの詳細は、[FreeBSD セキュリティページ](https://www.FreeBSD.org/security)で確認できます。

セキュリティチームの業務の 1 つは、FreeBSD オペレーティングシステムで報告されたセキュリティ脆弱性への対応です。脆弱性が確認されると、セキュリティチームは修正に必要な手順を検証してソースコードに修正を反映します。その後、詳細を「セキュリティ勧告（Security Advisory）」として公開します。セキュリティ勧告は [FreeBSD Web サイト](https://www.FreeBSD.org/security/advisories/)で公開されるほか、`freebsd-security-notifications`、`freebsd-security`、`freebsd-announce` の各メーリングリストにも送信されます。

<a id="chapter-16-heading-53"></a>
### セキュリティ勧告の形式

以下は、FreeBSD セキュリティ勧告の例です。

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

=============================================================================
FreeBSD-SA-23:07.bhyve                                      Security Advisory
                                                          The FreeBSD Project

Topic:          bhyve privileged guest escape via fwctl

Category:       core
Module:         bhyve
Announced:      2023-08-01
Credits:        Omri Ben Bassat and Vladimir Eli Tokarev from Microsoft
Affects:        FreeBSD 13.1 and 13.2
Corrected:      2023-08-01 19:48:53 UTC (stable/13, 13.2-STABLE)
                2023-08-01 19:50:47 UTC (releng/13.2, 13.2-RELEASE-p2)
                2023-08-01 19:48:26 UTC (releng/13.1, 13.1-RELEASE-p9)
CVE Name:       CVE-2023-3494

For general information regarding FreeBSD Security Advisories,
including descriptions of the fields above, security branches, and the
following sections, please visit <URL:https://security.FreeBSD.org/>.

I.   Background

bhyve(8)'s fwctl interface provides a mechanism through which guest
firmware can query the hypervisor for information about the virtual
machine.  The fwctl interface is available to guests when bhyve is run
with the "-l bootrom" option, used for example when booting guests in
UEFI mode.

bhyve is currently only supported on the amd64 platform.

II.  Problem Description

The fwctl driver implements a state machine which is executed when the
guest accesses certain x86 I/O ports.  The interface lets the guest copy
a string into a buffer resident in the bhyve process' memory.  A bug in
the state machine implementation can result in a buffer overflowing when
copying this string.

III. Impact

A malicious, privileged software running in a guest VM can exploit the
buffer overflow to achieve code execution on the host in the bhyve
userspace process, which typically runs as root.  Note that bhyve runs
in a Capsicum sandbox, so malicious code is constrained by the
capabilities available to the bhyve process.

IV.  Workaround

No workaround is available.  bhyve guests that are executed without the
"-l bootrom" option are unaffected.

V.   Solution

Upgrade your vulnerable system to a supported FreeBSD stable or
release / security branch (releng) dated after the correction date.

Perform one of the following:

1) To update your vulnerable system via a binary patch:

Systems running a RELEASE version of FreeBSD on the amd64, i386, or
(on FreeBSD 13 and later) arm64 platforms can be updated via the
freebsd-update(8) utility:

# freebsd-update fetch
# freebsd-update install

Restart all affected virtual machines.

2) To update your vulnerable system via a source code patch:

The following patches have been verified to apply to the applicable
FreeBSD release branches.

a) Download the relevant patch from the location below, and verify the
detached PGP signature using your PGP utility.

[FreeBSD 13.2]
# fetch https://security.FreeBSD.org/patches/SA-23:07/bhyve.13.2.patch
# fetch https://security.FreeBSD.org/patches/SA-23:07/bhyve.13.2.patch.asc
# gpg --verify bhyve.13.2.patch.asc

[FreeBSD 13.1]
# fetch https://security.FreeBSD.org/patches/SA-23:07/bhyve.13.1.patch
# fetch https://security.FreeBSD.org/patches/SA-23:07/bhyve.13.1.patch.asc
# gpg --verify bhyve.13.1.patch.asc

b) Apply the patch.  Execute the following commands as root:

# cd /usr/src
# patch < /path/to/patch

c) Recompile the operating system using buildworld and installworld as
described in <URL:https://www.FreeBSD.org/handbook/makeworld.html>.

Restart all affected virtual machines.

VI.  Correction details

This issue is corrected by the corresponding Git commit hash or Subversion
revision number in the following stable and release branches:

Branch/path                             Hash                     Revision
- -------------------------------------------------------------------------
stable/13/                              9fe302d78109    stable/13-n255918
releng/13.2/                            2bae613e0da3  releng/13.2-n254625
releng/13.1/                            87702e38a4b4  releng/13.1-n250190
- -------------------------------------------------------------------------

Run the following command to see which files were modified by a
particular commit:

# git show --stat <commit hash>

Or visit the following URL, replacing NNNNNN with the hash:

<URL:https://cgit.freebsd.org/src/commit/?id=NNNNNN>

To determine the commit count in a working tree (for comparison against
nNNNNNN in the table above), run:

# git rev-list --count --first-parent HEAD

VII. References

<URL:https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-3494>

The latest revision of this advisory is available at
<URL:https://security.FreeBSD.org/advisories/FreeBSD-SA-23:07.bhyve.asc>
-----BEGIN PGP SIGNATURE-----

iQIzBAEBCgAdFiEEthUnfoEIffdcgYM7bljekB8AGu8FAmTJdsIACgkQbljekB8A
Gu8Q1Q/7BFw5Aa0cFxBzbdz+O5NAImj58MvKS6xw61bXcYr12jchyT6ENC7yiR+K
qCqbe5TssRbtZ1gg/94gSGEXccz5OcJGxW+qozhcdPUh2L2nzBPkMCrclrYJfTtM
cnmQKjg/wFZLUVr71GEM95ZFaktlZdXyXx9Z8eBzow5rXexpl1TTHQQ2kZZ41K4K
KFhup91dzGCIj02cqbl+1h5BrXJe3s/oNJt5JKIh/GBh5THQu9n6AywQYl18HtjV
fMb1qRTAS9WbiEP5QV2eEuOG86ucuhytqnEN5MnXJ2rLSjfb9izs9HzLo3ggy7yb
hN3tlbfIPjMEwYexieuoyP3rzKkLeYfLXqJU4zKCRnIbBIkMRy4mcFkfcYmI+MhF
NPh2R9kccemppKXeDhKJurH0vsetr8ti+AwOZ3pgO21+9w+mjE+EfaedIi+JWhip
hwqeFv03bAQHJdacNYGV47NsJ91CY4ZgWC3ZOzBZ2Y5SDtKFjyc0bf83WTfU9A/0
drC0z3xaJribah9e6k5d7lmZ7L6aHCbQ70+aayuAEZQLr/N1doB0smNi0IHdrtY0
JdIqmVX+d1ihVhJ05prC460AS/Kolqiaysun1igxR+ZnctE9Xdo1BlLEbYu2KjT4
LpWvSuhRMSQaYkJU72SodQc0FM5mqqNN42Vx+X4EutOfvQuRGlI=
=MlAY
-----END PGP SIGNATURE-----
```

すべてのセキュリティ勧告では、次の形式が用いられています。

* 各セキュリティ勧告は Security Officer の PGP 鍵で署名されています。Security Officer の公開鍵は [OpenPGP Keys](https://docs.freebsd.org/en/books/handbook/pgpkeys/#pgpkeys) で確認できます。
* セキュリティ勧告の名称は常に `FreeBSD-SA-`（FreeBSD Security Advisory の略）で始まり、2 桁の年号（`23:`）、その年の勧告番号（`07.`）、影響を受けるアプリケーションまたはサブシステム名（`bhyve`）が続きます。
* `Topic` フィールドは脆弱性の概要を示します。
* `Category` は影響を受けるシステムの部分を示し、`core`、`contrib`、`ports` のいずれかになります。`core` カテゴリは脆弱性が FreeBSD オペレーティングシステムのコアコンポーネントに影響することを意味します。`contrib` カテゴリは BIND など FreeBSD に同梱されているソフトウェアに影響することを意味します。`ports` カテゴリは Ports Collection を通じて提供されるソフトウェアに影響することを示します。
* `Module` フィールドはコンポーネントの場所を示します。この例では `bhyve` モジュールが影響を受けているため、この脆弱性はオペレーティングシステムに同梱されているアプリケーションに影響します。
* `Announced` フィールドはセキュリティ勧告が公開された日付を示します。これは、セキュリティチームが問題の存在を確認し、修正が FreeBSD ソースコードリポジトリへコミットされたことを意味します。
* `Credits` フィールドは、脆弱性に気付いて報告した個人または組織への謝辞を示します。
* `Affects` フィールドは、どの FreeBSD リリースがこの脆弱性の影響を受けるかを説明します。
* `Corrected` フィールドは、修正された日時、タイムゾーンオフセット、およびリリースを示します。括弧内の部分は修正がマージされた各ブランチと、そのブランチに対応するリリースのバージョン番号を表します。リリース識別子自体にはバージョン番号と、該当する場合はパッチレベルが含まれます。パッチレベルは文字 `p` に続く数字で表され、パッチの連番を示すため、どのパッチがすでにシステムへ適用済みかを追跡できます。
* `CVE Name` フィールドは、公開されている [cve.mitre.org](http://cve.mitre.org) のセキュリティ脆弱性データベースに該当番号がある場合に、その勧告番号を記載します。
* `Background` フィールドは、影響を受けるモジュールの説明を提供します。
* `Problem Description` フィールドは、脆弱性を説明します。これには欠陥のあるコードや、ユーティリティが悪用される方法に関する情報が含まれる場合があります。
* `Impact` フィールドは、その問題がシステムにどのような影響を与えうるかを説明します。
* `Workaround` フィールドは、直ちにパッチを適用できないシステム管理者向けに回避策が利用可能かどうかを示します。
* `Solution` フィールドは、影響を受けるシステムへパッチを適用する手順を提供します。これは、システムへパッチを適用して安全に稼働させるためのテスト済み・検証済みの段階的な方法です。
* `Correction Details` フィールドは、修正されたコードを含む影響対象の各 Subversion または Git ブランチとリビジョン番号を表示します。
* `References` フィールドは、脆弱性に関する追加情報の参照元を提供します。
