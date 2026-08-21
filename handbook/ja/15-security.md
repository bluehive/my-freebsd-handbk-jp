# 第15章 セキュリティ（Security）

> **翻訳状態**: 初訳ドラフト（機械支援・要校正）  
> **上流**: https://docs.freebsd.org/en/books/handbook/security/  
> **ソース参照**: `handbook/en/15-security.adoc.txt`  
> **著作権**: 原文 © The FreeBSD Documentation Project。本日本語訳は BSD-2-Clause（リポジトリ LICENSE）。

**Part III. System Administration**

---

## 概要（Synopsis）

システムとネットワークを保護する方法については、何百もの標準的な手法が執筆されており、FreeBSD ユーザーとして、攻撃や侵入者から保護する方法を理解することは必須です。

この章では、いくつかの基本事項とテクニックについて説明します。
FreeBSD システムには複数のセキュリティレイヤーが備わっており、さらに多くのサードパーティ製ユーティリティを追加してセキュリティを強化することができます。

この章では、以下について説明します。

* FreeBSD システムの基本的なセキュリティ概念。
* FreeBSD で利用可能なさまざまな暗号化メカニズム。
* man:inetd[8] で TCP Wrappers を使用するための設定方法。
* FreeBSD での Kerberos のセットアップ方法。
* FreeBSD での OpenSSH の設定および使用方法。
* FreeBSD での OpenSSL の使用方法。
* ファイルシステム ACL の使用方法。
* pkg を使用して Ports Collection からインストールしたサードパーティ製ソフトウェアパッケージを監査する方法。
* FreeBSD セキュリティ勧告（security advisory）の活用方法。
* プロセスアカウンティング（Process Accounting）とは何か、および FreeBSD でそれを有効にする方法。
* ログインクラスまたはリソース制限データベースを使用してユーザーリソースを制御する方法。
* Capsicum とは何か、および基本的な例。

複雑さのため、特定のトピックは専用の章で説明されています。たとえば、crossref:firewalls[firewalls,Firewalls（ファイアウォール）]、crossref:mac[mac,Mandatory Access Control（強制アクセス制御）]、および extref:{vpn-ipsec}[VPN over IPsec] のような記事があります。

## はじめに（Introduction）

セキュリティは全員の責任です。
どのシステムの脆弱なエントリポイントも、侵入者に重要な情報へのアクセスを許し、ネットワーク全体に大損害を与える可能性があります。
情報セキュリティの中核的原則の 1 つが CIA トライアドです。これは、情報システムの機密性（Confidentiality）、完全性（Integrity）、可用性（Availability）を表します。

CIA トライアドは、コンピュータセキュリティの基盤となる概念であり、顧客とユーザーは自分のデータが保護されることを期待しています。
たとえば、顧客は自分のクレジットカード情報が安全に保管され（機密性）、注文が背後で変更されることがなく（完全性）、いつでも注文情報にアクセスできること（可用性）を期待します。

CIA を提供するために、セキュリティ専門家は多層防御（defense in depth）戦略を適用します。
多層防御の考え方は、複数のセキュリティレイヤーを追加して、単一のレイヤーが失敗してもセキュリティシステム全体が崩壊しないようにすることです。
たとえば、システム管理者は単にファイアウォールを有効にしただけで、ネットワークまたはシステムが安全であると見なすことはできません。
また、アカウントを監査し、バイナリの整合性を確認し、悪意のあるツールがインストールされていないことを保証する必要があります。
効果的なセキュリティ戦略を実装するには、脅威とその防御方法を理解する必要があります。

コンピュータセキュリティに関連する脅威とは何でしょうか？
脅威は、リモートの場所から許可なくシステムにアクセスしようとするリモート攻撃者だけに限定されません。
脅威には、従業員、悪意のあるソフトウェア、不正なネットワークデバイス、自然災害、セキュリティの脆弱性、さらには競合企業も含まれます。

システムとネットワークは、許可なくアクセスされることがあります。時には偶然に、時にはリモート攻撃者によって、また場合によっては企業スパイ行為や元従業員によってアクセスされます。
ユーザーとして、自分の過ちがセキュリティ侵害につながった場合に備え、それを認め、潜在的な問題をセキュリティチームに報告することが重要です。
管理者として、脅威を認識し、それらを軽減する準備をすることが重要です。

システムにセキュリティを適用する際は、まず基本的なアカウントとシステム構成の保護から始め、次にネットワークレイヤーを保護して、システムポリシーと組織のセキュリティ手順に準拠させることをお勧めします。
多くの組織では、テクノロジーデバイスの構成をカバーするセキュリティポリシーがすでに存在します。
ポリシーには、ワークステーション、デスクトップ、モバイルデバイス、電話、本番サーバー、開発サーバーのセキュリティ構成を含める必要があります。
多くの場合、標準運用手順（SOP）がすでに存在します。
疑わしい場合は、セキュリティチームに確認してください。

## アカウントの保護（Securing Accounts）

FreeBSD でアカウントを安全に維持することは、データの機密性、システムの整合性、権限分離にとって極めて重要です。不正アクセス、マルウェア、データ漏洩を防ぎ、コンプライアンスを確保し、組織の評判を保護します。

### ログインの防止（Preventing Logins）

システムを保護するには、まずアカウントの監査から始めるのが良いでしょう。ログインアクセスが不要なアカウントはすべて無効にします。

> **ヒント:**
> `root` には強力なパスワードを設定し、そのパスワードが共有されていないことを確認してください。

アカウントへのログインアクセスを拒否するには、2つの方法があります。

1つ目はアカウントをロックする方法です。次の例は、`imani` アカウントをロックする方法です:

```shell
# pw lock imani
```

2つ目は、シェルを `/usr/sbin/nologin` に変更してログインアクセスを防ぐ方法です。`nologin(8)` シェルは、ユーザーがログインしようとしたときにシステムがシェルを割り当てるのを防ぎます。

スーパーユーザーのみが他のユーザーのシェルを変更できます:

```shell
# chsh -s /usr/sbin/nologin imani
```

### パスワードハッシュ（Password Hashes）

パスワードはテクノロジーにおける必要悪です。パスワードを使用しなければならない場合は、複雑なものにし、パスワードデータベースに保存される暗号化バージョンには強力なハッシュ機構を使用する必要があります。FreeBSD は `crypt()` ライブラリで SHA256、SHA512、Blowfish ハッシュアルゴリズムを含む複数のアルゴリズムをサポートしています。詳細は `crypt(3)` を参照してください。

デフォルトの SHA512 を、より安全性の低いハッシュアルゴリズムに変更すべきではありませんが、より安全な Blowfish アルゴリズムに変更することは可能です。

> **注:**
> Blowfish は AES の一部ではなく、連邦情報処理標準（FIPS）に準拠しているとは見なされません。そのため、一部の環境では使用が許可されない場合があります。

ユーザーのパスワードの暗号化にどのハッシュアルゴリズムが使用されているかを確認するには、スーパーユーザーが FreeBSD のパスワードデータベース内のユーザーのハッシュを表示します。各ハッシュは、パスワードの暗号化に使用されたハッシュ機構の種類を示す記号で始まります。

DES が使用されている場合、先頭の記号はありません。MD5 の場合、記号は `$` です。SHA256 と SHA512 の場合、記号は `$6$` です。Blowfish の場合、記号は `$2a$` です。次の例では、`imani` のパスワードは、ハッシュが `$6$` で始まるため、デフォルトの SHA512 アルゴリズムを使用してハッシュ化されています。パスワードデータベースに保存されるのは暗号化されたハッシュであり、パスワードそのものではないことに注意してください:

```shell
# grep imani /etc/master.passwd
```

出力は次のようになります:

```
imani:$6$pzIjSvCAn.PBYQBA$PXpSeWPx3g5kscj3IMiM7tUEUSPmGexxta.8Lt9TGSi2lNQqYGKszsBPuGME0:1001:1001::0:0:imani:/usr/home/imani:/bin/sh
```

ハッシュ機構はユーザーのログインクラスで設定されます。

現在使用されているハッシュ機構を確認するには、次のコマンドを実行します:

```shell
% grep passwd_format /etc/login.conf
```

出力は次のようになります:

```
```

例えば、アルゴリズムを Blowfish に変更するには、その行を次のように変更します:

```
```

次に、`cap_mkdb(1)` を実行して login.conf データベースを更新する必要があります:

```shell
# cap_mkdb /etc/login.conf
```

この変更は既存のパスワードハッシュには影響しないことに注意してください。つまり、ユーザーに `passwd` を実行してパスワードを変更してもらい、すべてのパスワードを再ハッシュする必要があります。

### パスワードポリシーの強制（Password Policy Enforcement）

ローカルアカウントに強力なパスワードポリシーを強制することは、システムセキュリティの基本的な側面です。FreeBSD では、パスワードの長さ、パスワードの強度、パスワードの複雑さは、組み込みの Pluggable Authentication Modules（PAM）を使用して実装できます。

このセクションでは、`pam_passwdqc(8)` モジュールを使用して、パスワードの最小長と最大長、および混合文字の強制を設定する方法を示します。このモジュールは、ユーザーがパスワードを変更するときに適用されます。

このモジュールを設定するには、スーパーユーザーになり、`/etc/pam.d/passwd` 内の `pam_passwdqc.so` を含む行のコメントを解除します。

次に、その行をパスワードポリシーに合わせて編集します:

```
password        requisite       pam_passwdqc.so         min=disabled,disabled,disabled,12,10 similar=deny retry=3 enforce=users
```

パラメータの説明は `pam_passwdqc(8)` にあります。

このファイルが保存されると、パスワードを変更するユーザーには次のようなメッセージが表示されます:

```shell
% passwd
```

出力は次のようになります:

[.p





## 侵入検知システム（IDS）

システムファイルとバイナリの検証は、システム管理者やセキュリティチームにシステムの変更に関する情報を提供するため、重要です。システムの変更を監視するソフトウェアアプリケーションは、侵入検知システム（IDS）と呼ばれます。

FreeBSD は、`man mtree(8)` と呼ばれる基本的な IDS システムのネイティブサポートを提供します。夜間のセキュリティメールは管理者に変更を通知しますが、その情報はローカルに保存され、悪意のあるユーザーがシステムへの変更を隠すためにこの情報を変更できる可能性があります。そのため、バイナリ署名の別のセットを作成し、読み取り専用の root 所有ディレクトリ、またはできればリムーバブル USB ディスクやリモートサーバーに保存することをお勧めします。

また、更新のたびに `freebsd-update IDS` を実行することもお勧めします。

### 仕様ファイルの生成

組み込みの `man mtree(8)` ユーティリティを使用すると、ディレクトリの内容の仕様を生成できます。シード、つまり数値定数は、仕様を生成するために使用され、仕様が変更されていないことを確認するために必要です。これにより、ファイルやバイナリが変更されたかどうかを判断できます。シード値は攻撃者には知られていないため、ファイルのチェックサム値を偽造したり検証したりすることは、困難から不可能になります。

> **ヒント:**
> バイナリと設定ファイルを含むディレクトリ、および機密データを含むディレクトリの仕様を作成することをお勧めします。通常、仕様は `/bin`、`/sbin`、`/usr/bin`、`/usr/sbin`、`/usr/local/bin`、`/etc`、`/usr/local/etc` に対して作成されます。

次の例では、`/bin` 内の各システムバイナリに対して `sha512` ハッシュのセットを生成し、その値をユーザーのホームディレクトリ内の隠しファイル `/home/user/.bin_chksum_mtree` に保存します。

```shell
# mtree -s 123456789 -c -K cksum,sha512 -p /bin > /home/user/.bin_chksum_mtree
```

出力は次のようになります。

```text
mtree: /bin checksum: 3427012225
```

> **警告:**
> `123456789` という値はシードを表し、ランダムに選択する必要があります。この値は記憶しておくべきですが、*共有してはいけません*。シード値とチェックサム出力を悪意のあるユーザーから隠しておくことが重要です。

### 仕様ファイルの構造

mtree 形式は、ファイルシステムオブジェクトの集合を記述するテキスト形式です。このようなファイルは通常、ディレクトリ階層を作成または検証するために使用されます。

mtree ファイルは一連の行で構成され、各行は単一のファイルシステムオブジェクトに関する情報を提供します。先頭の空白は常に無視されます。

上記で作成した仕様ファイルを使って、形式と内容を説明します。

```text
#          user: root <1>
#       machine: machinename <2>
#          tree: /bin <3>
#          date: Thu Aug  24 21:58:37 2023 <4>

# .
/set type=file uid=0 gid=0 mode=0555 nlink=1 flags=uarch <5>
.               type=dir mode=0755 nlink=2 time=1681388848.239523000 <6>
    \133        nlink=2 size=12520 time=1685991378.688509000 \
                cksum=520880818 \
                sha512=5c1374ce0e2ba1b3bc5a41b23f4bbdc1ec89ae82fa01237f376a5eeef41822e68f1d8f75ec46b7bceb65396c122a9d837d692740fdebdcc376a05275adbd3471
    cat         size=14600 time=1685991378.694601000 cksum=3672531848 \ <7>
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
5. mtree ファイル形式はデフォルトでディレクトリ階層を記述し、この行はファイル階層に適用されるデフォルト値を指定します。この例では、デフォルトのファイルタイプ、uid、gid、パーミッションを設定します。この例の値だけでなく、より多くのデフォルト値を指定できます。
6. ピリオドで始まる行は、ディレクトリ自体を表します。
7. ファイルの一般的なエントリ: ファイル名、サイズ、時刻、cksum、sha512、およびその他のオプションを指定します。



## セキュアレベル（Secure levels）

セキュアレベル（securelevel）は、カーネルに実装されたセキュリティ機構です。  
セキュアレベルが正の値の場合、カーネルは特定のタスクを制限します。スーパーユーザー（root）であっても実行することはできません。

セキュアレベル機構は、以下の操作を制限します。

* 特定のファイルフラグ（`schg`（システム不変フラグ）など）の解除
* `/dev/mem` および `/dev/kmem` を介したカーネルメモリへの書き込み
* カーネルモジュールのロード
* ファイアウォールルールの変更

### セキュアレベルの定義

カーネルは、5 つの異なるセキュリティレベルで動作します。  
スーパーユーザーのプロセスであればレベルを上げることはできますが、どのプロセスもレベルを下げることはできません。

セキュリティレベルの定義は以下のとおりです。

**-1: 恒久的非セキュアモード（Permanently insecure mode）**  
常に非セキュアモードでシステムを実行します。これはデフォルトの初期値です。

**0: 非セキュアモード（Insecure mode）**  
不変フラグと追加専用フラグはオフにできます。  
すべてのデバイスは、そのパーミッションに従って読み取りまたは書き込みができます。

**1: セキュアモード（Secure mode）**  
システム不変フラグとシステム追加専用フラグはオフにできません。  
マウントされたファイルシステムのディスク、`/dev/mem`、`/dev/kmem` は書き込み用に開くことができません。  
`/dev/io`（プラットフォームが持つ場合）は、まったく開くことができません。  
カーネルモジュール（`man kld(4)` を参照）のロードまたはアンロードはできません。  
`debug.kdb.enter` sysctl を使用してカーネルデバッガを起動することはできません。  
`debug.kdb.panic`、`debug.kdb.panic_str` およびその他の sysctl を使用して、パニックまたはトラップを強制することはできません。

**2: 高セキュアモード（Highly secure mode）**  
セキュアモードと同じですが、さらに、ディスクはマウントされているかどうかに関係なく、書き込み用に開くことができません（`man mount(2)` による場合を除く）。  
このレベルでは、ファイルシステムをアンマウントして改ざんすることを防ぎますが、システムがマルチユーザーで動作している間は `man newfs(8)` の実行も抑制します。

**3: ネットワークセキュアモード（Network secure mode）**  
高セキュアモードと同じですが、さらに、IP パケットフィルタールール（`man ipfw(8)`、`man ipfirewall(4)`、`man pfctl(8)` を参照）は変更できず、`man dummynet(4)` または `man pf(4)` の設定も調整できません。

> **ヒント:**
> 
> 要約すると、FreeBSD のセキュアレベルにおける `Permanently Insecure Mode` と `Insecure Mode` の主な違いは、提供されるセキュリティの度合いです。  
> `Permanently Insecure Mode` はすべてのセキュリティ制限を完全に解除しますが、`Insecure Mode` は一部の制限を緩和しつつ、ある程度の制御とセキュリティを維持します。

### セキュアレベルの変更

システムのセキュアレベルを変更するには、次のコマンドを実行して `kern_securelevel_enable` を有効にする必要があります。

```shell
# sysrc kern_securelevel_enable="YES"
```

そして、`kern_securelevel` の値を目的のセキュリティレベルに設定します。

```shell
# sysrc kern_securelevel=2
```

実行中のシステムのセキュアレベルの状態を確認するには、次のコマンドを実行します。

```shell
# sysctl -n kern.securelevel
```

この出力には、現在のセキュアレベルの値が含まれます。  
0 より大きい場合は、セキュアレベルの保護機能の少なくとも一部が有効になっています。

<!-- [[security-file-flags]] -->

## ファイルフラグ

ファイルフラグを使用すると、基本的なパーミッションや所有権に加えて、ファイルやディレクトリに追加のメタデータや属性を付与できます。これらのフラグは、特別なディレクトリを作成したり拡張属性を使用したりすることなく、ファイルのさまざまな動作や特性を制御する手段を提供します。

ファイルフラグは、ファイルの削除防止、追記専用化、ファイル更新の同期など、さまざまな目的を達成するために使用できます。FreeBSD でよく使われるファイルフラグには、ファイルの変更や削除を防ぐ `immutable`（不変）フラグや、ファイルの末尾へのデータ追加のみを許可し、変更や削除を禁止する `append-only`（追記専用）フラグがあります。

これらのフラグは、FreeBSD では `man chflags(1)` コマンドで管理でき、管理者やユーザーはファイルやディレクトリの動作と特性をより細かく制御できます。ファイルフラグはファイルのアクセス方法や操作方法に影響を与える可能性があるため、通常は root または適切な権限を持つユーザーによって管理されることに注意してください。一部のフラグは、`man chflags(1)` に記載されているとおり、ファイルの所有者が使用できます。

[[security-work-file-flag]]
### ファイルフラグの操作

この例では、ユーザーのホームディレクトリにある `~/important.txt` というファイルを削除から保護したいとします。

次のコマンドを実行して、`schg` ファイルフラグを設定します。

```shell
# chflags schg ~/important.txt
```

`root` ユーザーを含むどのユーザーがこのファイルを削除しようとしても、システムは次のメッセージを表示します。

```shell
rm: important.txt: Operation not permitted
```

ファイルを削除するには、次のコマンドを実行してそのファイルのファイルフラグを削除する必要があります。

```shell
# chflags noschg ~/important.txt
```

サポートされているファイルフラグの一覧とその機能については、`man chflags(1)` を参照してください。

[[openssh]]

## OpenSSH

OpenSSH は、リモートマシンへの安全なアクセスを提供するネットワーク接続ツールのセットです。さらに、TCP/IP 接続を SSH 接続経由で安全にトンネリングまたは転送できます。OpenSSH はすべてのトラフィックを暗号化し、盗聴、接続ハイジャック、その他のネットワークレベルの攻撃を排除します。

OpenSSH は OpenBSD プロジェクトによってメンテナンスされており、FreeBSD にデフォルトでインストールされています。

データが暗号化されずにネットワーク経由で送信されると、クライアントとサーバの間のどこかにいるネットワークスニファが、ユーザー名やパスワード情報、またはセッション中に転送されたデータを盗み取る可能性があります。OpenSSH はこれを防ぐために、さまざまな認証方法と暗号化方法を提供しています。

OpenSSH の詳細については、[Web ページ](https://www.openssh.com/) を参照してください。

このセクションでは、他のシステムに安全にアクセスし、FreeBSD システムからファイルを安全に転送するための内蔵クライアントユーティリティの概要を説明します。その後、FreeBSD システム上で SSH サーバを設定する方法について説明します。

> **ヒント:** 前述のとおり、この章ではベースシステム版の OpenSSH を扱います。OpenSSH の別バージョンは package:security/openssh-portable[] パッケージでも利用でき、追加の設定オプションを提供し、新機能でより定期的に更新されています。

### SSHクライアントユーティリティの使用

SSH サーバにログインするには、man:ssh(1) を使用し、そのサーバに存在するユーザー名と、サーバの IP アドレスまたはホスト名を指定します。指定したサーバへの接続が初めての場合は、最初にサーバのフィンガープリントを確認するよう求められます。

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

SSH は、クライアント接続時にサーバの正当性を検証するためにキーフィンガープリントシステムを利用します。初回接続時にユーザーが `yes` と入力してキーのフィンガープリントを受け入れると、キーのコピーがユーザーのホームディレクトリにある `~/.ssh/known_hosts` に保存されます。以降のログイン試行は保存されたキーと照合され、サーバのキーが保存されたキーと一致しない場合、man:ssh(1) は警告を表示します。このような場合は、接続を続行する前に、キーが変更された理由をまず確認する必要があります。

> **注:** この確認方法については、この章の範囲外です。

リモートマシンとの間でファイルを安全にコピーするには、man:scp(1) を使用します。次の例では、リモートシステム上の `COPYRIGHT` を、ローカルシステムの現在のディレクトリにある同じ名前のファイルにコピーします。

```shell
# scp user@example.com:/COPYRIGHT COPYRIGHT
```

出力は次のようになります。

```
Password for user@example.com: *******
COPYRIGHT            100% |*****************************|  4735
```

このホストのフィンガープリントはすでに検証済みのため、ユーザーのパスワードを求める前にサーバのキーが自動的にチェックされます。

man:scp(1) に渡す引数は man:cp(1) に似ています。コピーするファイルが最初の引数で、コピー先が 2 番目の引数です。ファイルはネットワーク経由で取得されるため、ファイル引数の 1 つ以上が `user@host:<path_to_remote_file>` の形式になります。ディレクトリを再帰的にコピーする場合、man:scp(1) は `-r` を使用しますが、man:cp(1) は `-R` を使用することに注意してください。

ファイルをコピーするための対話型セッションを開くには、man:sftp(1) を使用します。man:sftp(1) セッション中に利用可能なコマンドの一覧については、man:sftp(1) を参照してください。

### キー認証

パスワードの代わりに、クライアントがキーを使用してリモートマシンに接続するように設定できます。セキュリティ上の理由から、これが推奨される方法です。

認証キーの生成には man:ssh-keygen(1) を使用します。公開鍵と秘密鍵のペアを生成するには、キーの種類を指定してプロンプトに従います。キーは、覚えやすくても推測が難しいパスフレーズで保護することをお勧めします。

```shell
% ssh-keygen -t rsa -b 4096
```

出力は次のようになります。

```
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa):
Created director
```

y '/home/user/.ssh/.ssh'.
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

秘密鍵は `~/.ssh/id_rsa` に、公開鍵は `~/.ssh/id_rsa.pub` に保存されます。鍵ベース認証を機能させるには、_公開_鍵をリモートマシンの `~/.ssh/authorized_keys` にコピーする必要があります。

> **警告:**
>
> OpenSSH鍵にパスフレーズを利用することは重要なセキュリティ慣行であり、不正アクセスに対する追加の保護層を提供し、全体的なサイバーセキュリティを強化します。
>
> 紛失や盗難の場合にも、これによりもう一つのセキュリティ層が追加されます。

### SSHトンネリング

OpenSSHには、別のプロトコルを暗号化セッション内にカプセル化するトンネルを作成する機能があります。

次のコマンドは、トンネルを作成するように `man ssh(1)` に指示します。

```shell
% ssh -D 8080 user@example.com
```

この例では、以下のオプションを使用しています。

- `-D`:: ローカルの「ダイナミック」アプリケーションレベルのポート転送を指定します。
- `user@foo.example.com`:: 指定されたリモートSSHサーバーで使用するログイン名です。

SSHトンネルは、指定された `localport` の `localhost` にリスニングソケットを作成することで機能します。

この方法は、SMTP、POP3、FTPなどの安全でないTCPプロトコルをいくつでもラップするために使用できます。

### SSHサーバーの有効化

組み込みのSSHクライアントユーティリティに加えて、FreeBSDシステムをSSHサーバーとして構成し、他のSSHクライアントからの接続を受け付けることができます。

> **ヒント:**
>
> 前述のとおり、この章ではベースシステムのOpenSSHバージョンについて説明します。FreeBSD portsに同梱されているOpenSSHのバージョンである `security/openssh-portable` と混同しないでください。

SSHサーバーを再起動後も有効にするには、次のコマンドを実行します。

```shell
# sysrc sshd_enable="YES"
```

次に、サービスを有効にするために次のコマンドを実行します。

```shell
# service sshd start
```

FreeBSDシステムでsshdが初めて起動すると、システムのホスト鍵が自動的に作成され、フィンガープリントがコンソールに表示されます。ユーザーにフィンガープリントを提供して、サーバーへの最初の接続時に確認できるようにしてください。

sshdの起動時に利用可能なオプションの一覧と、認証、ログインプロセス、およびさまざまな設定ファイルに関する完全な議論については、`man sshd(8)` を参照してください。

この時点で、sshdはシステム上にユーザー名とパスワードを持つすべてのユーザーが利用できるはずです。

### 公開鍵認証方式の設定

公開鍵認証を使用するようにOpenSSHを構成すると、非対称暗号を認証に活用することでセキュリティが強化されます。この方法は、弱いパスワードや送信中の傍受などのパスワード関連のリスクを排除し、さまざまなパスワードベースの攻撃を阻止します。ただし、不正アクセスを防ぐために秘密鍵を適切に保護することが不可欠です。

最初のステップは、必要な認証方式を使用するように `man sshd(8)` を構成することです。

`/etc/ssh/sshd_config` を編集し、次の設定のコメントを解除します。

```text
PubkeyAuthentication yes
```

設定が完了したら、ユーザーはシステム管理者に*公開鍵*を送信し、これらの鍵は `.ssh/authorized_keys` に追加されます。鍵の生成プロセスは「Key-based Authentication（鍵ベース認証）」で説明されています。

次に、サーバーを再起動するために次のコマンドを実行します。

```shell
# service sshd reload
```

「SSH Server Security Options（SSHサーバーのセキュリティオプション）」に示されているセキュリティ改善に従うことを強くお勧めします。

### SSHサーバーのセキュリティオプション

sshdはFreeBSDで最も広く使用されているリモート管理機能ですが、ブルートフォース攻撃やドライブバイ攻撃は、パブリックネットワークにさらされているシステムでは一般的です。

これらの攻撃の成功を防ぐために、いくつかの追加パラメータが利用可能であり、このセクションで説明します。

n. すべての設定は `/etc/ssh/sshd_config` で行います。

> **ヒント:**
>
> `/etc/ssh/sshd_config` を `/etc/ssh/ssh_config` と混同しないでください（最初のファイル名には余分な `d` が付いています）。最初のファイルはサーバーを設定し、2番目のファイルはクライアントを設定します。利用可能なクライアント設定の一覧については、man ssh_config(5) を参照してください。

デフォルトでは、認証は公開鍵とパスワードの両方で行えます。
*公開鍵のみ*の認証を許可するには（*強く推奨されます*）、次の変数を変更します:

```
PasswordAuthentication no
```

OpenSSH サーバー設定ファイルの `AllowUsers` キーワードを使用して、どのユーザーがどこから SSH サーバーにログインできるかを制限することをお勧めします。
たとえば、`user` が `192.168.1.32` からのみログインできるようにするには、次の行を `/etc/ssh/sshd_config` に追加します:

```
AllowUsers user@192.168.1.32
```

`user` がどこからでもログインできるようにするには、IP アドレスを指定せずにそのユーザーを列挙します:

```
AllowUsers user
```

複数のユーザーは、次のように同じ行に列挙します:

```
AllowUsers root@192.168.1.32 user
```

すべての変更を行った後、サービスを再起動する前に、次のコマンドを実行して、行った設定が正しいことを確認することをお勧めします:

```shell
# sshd -t
```

設定ファイルが正しければ、出力は表示されません。
設定ファイルが正しくない場合は、次のような出力が表示されます:

```
/etc/ssh/sshd_config: line 3: Bad configuration option: sdadasdasdasads
/etc/ssh/sshd_config: terminating, 1 bad configuration options
```

変更を行い、設定ファイルが正しいことを確認したら、次のコマンドを実行して sshd に設定ファイルを再読み込みさせます:

```shell
# service sshd reload
```

[[openssl]]

## OpenSSL

OpenSSL は、Secure Sockets Layer (SSL) および Transport Layer Security (TLS) ネットワークプロトコルと、多くの暗号化ルーチンを実装した暗号ツールキットです。

openssl プログラムは、シェルから OpenSSL の crypto ライブラリのさまざまな暗号機能を使用するためのコマンドラインツールです。以下の用途に使用できます。

* 秘密鍵、公開鍵、パラメータの作成と管理
* 公開鍵暗号操作
* X.509 証明書、CSR、CRL の作成
* メッセージダイジェストの計算
* 暗号化と復号化
* SSL/TLS クライアントおよびサーバーテスト
* S/MIME 署名付きまたは暗号化メールの処理
* タイムスタンプリクエストの生成と検証
* 暗号ルーチンのベンチマーク

OpenSSL の詳細については、無料の [OpenSSL Cookbook](https://www.feistyduck.com/books/openssl-cookbook/) を読んでください。

### 証明書の生成（Generating Certificates）

OpenSSL は、[CA](https://en.wikipedia.org/wiki/Certificate_authority) による検証を受ける証明書と、自己利用のための証明書の両方を生成できます。

以下の引数を指定して `man openssl(1)` コマンドを実行すると、[CA](https://en.wikipedia.org/wiki/Certificate_authority) 用の有効な証明書を生成できます。このコマンドは、カレントディレクトリに 2 つのファイルを作成します。証明書リクエスト `req.pem` は [CA](https://en.wikipedia.org/wiki/Certificate_authority) に送信できます。CA は入力された資格情報を検証し、リクエストに署名し、署名済み証明書を返します。2 番目のファイル `cert.key` は証明書の秘密鍵であり、安全な場所に保管する必要があります。これが他人の手に渡ると、ユーザーやサーバーになりすまされる可能性があります。

次のコマンドを実行して証明書を生成します。

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

あるいは、[CA](https://en.wikipedia.org/wiki/Certificate_authority) からの署名が必要ない場合は、自己署名証明書を作成できます。これにより、カレントディレクトリに秘密鍵ファイル `cert.key` と証明書自体の `cert.crt` の 2 つの新しいファイルが作成されます。これらのファイルは、`root` だけが読み取り可能なディレクトリ（できれば `/etc/ssl/` 配下）に配置する必要があります。これらのファイルにはパーミッション `0700` が適切であり、`chmod` を使用して設定できます。

次のコマンドを実行して証明書を生成します。

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
State or Province Name (full name) [Some-State]:
```

Valencian Community
Locality Name (eg, city) []:Valencia
Organization Name (eg, company) [Internet Widgits Pty Ltd]:My Company
Organizational Unit Name (eg, section) []:Systems Administrator
Common Name (e.g. server FQDN or YOUR name) []:localhost.example.org
Email Address []:user@FreeBSD.org
....

[[fips-provider]]
=== FIPS プロバイダの設定

FreeBSD 14 以降のベースシステムへの OpenSSL 3 の取り込みにより、プロバイダモジュールという新しい概念がシステムに導入されました。ライブラリに組み込まれたデフォルトのプロバイダモジュールに加えて、_legacy_ モジュールは、現在ではオプションとなった非推奨の暗号化アルゴリズムを実装し、_fips_ モジュールは、OpenSSL の実装を [FIPS](https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards) 標準セットに含まれる暗号化アルゴリズムに限定します。OpenSSL のこの部分は [特に注意](https://www.openssl.org/docs/fips.html) が払われており、[関連するセキュリティ問題のリスト](https://www.openssl.org/news/fips-cve.html) を含み、定期的に [FIPS 140 検証プロセス](https://github.com/openssl/openssl/blob/master/README-FIPS.md) の対象となっています。[FIPS 検証済みバージョンのリスト](https://www.openssl.org/source/) も利用できます。これにより、ユーザーは OpenSSL の使用において FIPS 準拠を保証できます。

重要なのは、`man fips_module(7)` が追加のセキュリティ対策によって保護されており、整合性チェックを通過しない限り使用できないことです。このチェックはシステム管理者が設定でき、OpenSSL 3 のすべてのユーザーがこのモジュールをロードできるようになります。正しく設定されていない場合、FIPS モジュールは次のように失敗します:

```shell
# echo test | openssl aes-128-cbc -a -provider fips -pbkdf2
```

出力は次のようになるはずです:

```text
aes-128-cbc: unable to load provider fips
Hint: use -provider-path option or OPENSSL_MODULES environment variable.
00206124D94D0000:error:1C8000D5:Provider routines:SELF_TEST_post:missing config data:crypto/openssl/providers/fips/self_test.c:275:
00206124D94D0000:error:1C8000E0:Provider routines:ossl_set_error_state:fips module entering error state:crypto/openssl/providers/fips/self_test.c:373:
00206124D94D0000:error:1C8000D8:Provider routines:OSSL_provider_init_int:self test post failure:crypto/openssl/providers/fips/fipsprov.c:707:
00206124D94D0000:error:078C0105:common libcrypto routines:provider_init:init fail:crypto/openssl/crypto/provider_core.c:932:name=fips
```

このチェックは、`/etc/ssl/fipsmodule.cnf` にファイルを作成することで設定でき、その後 OpenSSL のメイン設定ファイル `/etc/ssl/openssl.cnf` から参照されます。OpenSSL はこのプロセスを支援する `man openssl-fipsinstall(1)` ユーティリティを提供しており、次のように使用できます:

```shell
# openssl fipsinstall -module /usr/lib/ossl-modules/fips.so -out /etc/ssl/fipsmodule.cnf
```

出力は次のようになるはずです:

```text
INSTALL PASSED
```

次に、`/etc/ssl/openssl.cnf` を以下の目的で変更する必要があります:

* 上記で生成した `/etc/ssl/fipsmodule.cnf` ファイルを組み込む
* FIPS モジュールを使用可能な状態で公開する
* そして、デフォルトモジュールを明示的に有効化する

```text
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

これで、FIPS モジュールが実際に利用可能で動作していることを確認できるはずです:

[s

# echo test | openssl aes-128-cbc -a -provider fips -pbkdf2
```

出力は次のようになります。

```
enter AES-128-CBC encryption password:
Verifying - enter AES-128-CBC encryption password:
U2FsdGVkX18idooW6e3LqWeeiKP76kufcOUClh57j8U=
```

この手順は、FIPS モジュールが変更されるたびに繰り返す必要があります。たとえば、システムのアップデート後や、ベースシステムの OpenSSL に影響を与えるセキュリティ修正を適用した後などです。

[[kerberos5]]

## Kerberos

Kerberos は、元々マサチューセッツ工科大学（MIT）によって開発されたネットワーク認証プロトコルで、潜在的に敵対的なネットワーク上でも安全に認証を提供するための手段です。Kerberos プロトコルは強力な暗号技術を用いることで、クライアントとサーバーの両方が、ネットワーク上に暗号化されていない秘密情報を送信することなく、互いの身元を証明できます。Kerberos は、身元確認を行うプロキシシステム、また信頼できる第三者による認証システムと表現できます。ユーザーが Kerberos で認証すると、その後の通信は暗号化され、プライバシーとデータ整合性が保証されます。

Kerberos の唯一の機能は、ネットワーク上のユーザーとサーバーに安全な認証を提供することです。認可（authorization）や監査（auditing）の機能は提供しません。Kerberos は、認可と監査サービスを提供する他のセキュリティ方法と併用することが推奨されます。

現在のプロトコルのバージョンは 5 であり、RFC 4120 で解説されています。このプロトコルにはフリーの実装がいくつかあり、幅広いオペレーティングシステムをカバーしています。MIT は現在も Kerberos パッケージを開発し続けています。これは米国では暗号製品として一般的に使用されており、歴史的に米国の輸出規制の対象となってきました。FreeBSD では、MIT Kerberos は `security/krb5` パッケージまたはポートとして利用できます。Heimdal Kerberos 実装は、輸出規制を回避するために米国外で明示的に開発されました。Heimdal Kerberos ディストリビューションは FreeBSD のベースシステムに含まれており、より多くの設定オプションを備えた別のディストリビューションが Ports Collection の `security/heimdal` として利用できます。

Kerberos では、ユーザーとサービスは「プリンシパル（principal）」として識別され、それらは「レルム（realm）」と呼ばれる管理上のグループに含まれます。一般的なユーザープリンシパルは `_user_@_REALM_` の形式になります（レルムは伝統的に大文字で表記されます）。

このセクションでは、FreeBSD に含まれる Heimdal ディストリビューションを使用して Kerberos をセットアップする方法について説明します。

Kerberos インストールのデモンストレーションのために、名前空間は次のようにします。

* DNS ドメイン（ゾーン）は `example.org`。
* Kerberos レルムは `EXAMPLE.ORG`。

> **注:**
> Kerberos をセットアップする際は、内部で実行する場合でも、実際のドメイン名を使用してください。これにより、DNS の問題を回避し、他の Kerberos レルムとの相互運用を保証できます。

### Heimdal KDC のセットアップ

Key Distribution Center（KDC）は、Kerberos が提供する中央集権的な認証サービス、つまりシステムの「信頼できる第三者」です。これは、クライアントがサーバーに対して認証するために使用する Kerberos チケットを発行するコンピューターです。KDC は Kerberos レルム内の他のすべてのコンピューターから信頼されていると見なされるため、セキュリティ上の懸念が高まります。KDC への直接アクセスは制限されるべきです。

KDC の実行にはほとんどコンピューティングリソースを必要としませんが、セキュリティ上の理由から、KDC としてのみ機能する専用マシンを使用することをお勧めします。

まず、以下のように `security/heimdal` パッケージをインストールします。

```shell
# pkg install heimdal
```

次に、`sysrc` を使用して `/etc/rc.conf` を以下のように更新します。

```shell
# sysrc kdc_enable=yes
# sysrc kadmind_enable=yes
```

次に、`/etc/krb5.conf` を以下のように編集します。

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

この例では、KDC は完全修飾ホスト名 `kerberos.example.org` を使用します。KDC のホスト名は DNS で解決可能である必要があります。

Kerberos は、`/etc/krb5.conf` の `[realms]` セクションの代わりに、DNS を使用して KDC を探すこともできます。独自の DNS サーバーを持つ大規模な組織では、上記の例を次のように簡略化できます。

```
[libdefaults]
      default_realm = EXAMPLE.ORG
[domain_realm]
    .example.org = EXAMPLE.ORG
```

そして、`example.org` ゾーンファイルに以下の行を含めます。

```
_kerberos._udp      IN  SRV     01 00 88 kerberos.example.org.
_kerberos._tcp      IN  SRV     01 00 88 kerberos.example.org.
_kpasswd._udp       IN  SRV     01 00 464 kerberos.example.org.
_kerberos-adm._tcp  IN  SRV     01 00 749 kerberos.example.org.
_kerberos           IN  TXT     EXAMPLE.ORG
```

> **注:**
> クライアントが Kerberos サービスを見つけられるようにするには、クライアントは完全に設定された `/etc/krb5.conf` か、最小限に設定された `/et
-----

`/etc/krb5.conf` と、適切に設定された DNS サーバー。

次に、全プリンシパル（ユーザーとホスト）の鍵をマスターパスワードで暗号化して保持する Kerberos データベースを作成します。このパスワードは `/var/heimdal/m-key` に保存されるため、覚えておく必要はありません。この目的には、45文字のランダムなパスワードを使うのが妥当です。マスターキーを作成するには、`kstash` を実行してパスワードを入力してください。

```shell
# kstash
```

出力は次のようになります。

```text
Master key: xxxxxxxxxxxxxxxxxxxxxxx
Verifying password - Master key: xxxxxxxxxxxxxxxxxxxxxxx
```

マスターキーを作成したら、データベースを初期化します。Kerberos 管理ツール `man kadmin(8)` は、`kadmin -l` のように、`man kadmind(8)` ネットワークサービスを使用せずにデータベースを直接操作するモードで KDC 上で使用できます。これにより、データベースを作成する前に接続しようとする「鶏と卵」の問題を解決できます。`kadmin` プロンプトで、`init` を使ってレルムの初期データベースを作成します。

```shell
# kadmin -l
kadmin> init EXAMPLE.ORG
Realm max ticket life [unlimited]:
```

最後に、`kadmin` 内で `add` を使って最初のプリンシパルを作成します。プリンシパルのオプションは後で `modify` で変更できるため、今はデフォルトのままにしておきます。利用可能なオプションを確認するには、プロンプトで `?` と入力します。

```shell
kadmin> add tillman
```

出力は次のようになります。

```text
Max ticket life [unlimited]:
Max renewable life [unlimited]:
Principal expiration time [never]:
Password expiration time [never]:
Attributes []:
Password: xxxxxxxx
Verifying password - Password: xxxxxxxx
```

次に、以下のコマンドで KDC サービスを起動します。

```shell
# service kdc start
# service kadmind start
```

この時点では Kerberos 化されたデーモンは稼働していませんが、作成したばかりのプリンシパルのチケットを取得することで、KDC が機能していることを確認できます。

```shell
% kinit tillman
```

出力は次のようになります。

```text
tillman@EXAMPLE.ORG's Password:
```

`klist` を使って、チケットが正常に取得されたことを確認します。

```shell
% klist
```

出力は次のようになります。

```text
Credentials cache: FILE:/tmp/krb5cc_1001
	Principal: tillman@EXAMPLE.ORG

  Issued                Expires               Principal
Aug 27 15:37:58 2013  Aug 28 01:37:58 2013  krbtgt/EXAMPLE.ORG@EXAMPLE.ORG
```

テストが終わったら、一時チケットを破棄できます。

```shell
% kdestroy
```

### Kerberos を使用するサーバーの設定

Kerberos 認証を使用するサーバーを設定する最初のステップは、`/etc/krb5.conf` に正しい設定があることを確認することです。KDC のバージョンをそのまま使用するか、新しいシステム上で再生成することができます。

次に、サーバー上で `/etc/krb5.keytab` を作成します。これはサービスの「Kerberos 化」の主要部分であり、サービスと KDC の間で共有される秘密情報の生成に相当します。秘密情報は暗号鍵であり、「keytab」に保存されます。keytab にはサーバーのホスト鍵が含まれており、サーバーと KDC が互いの身元を確認できるようになります。鍵が公開されるとサーバーのセキュリティが破られる可能性があるため、keytab は安全な方法でサーバーに転送する必要があります。通常、keytab は管理者の信頼できるマシン上で `kadmin` を使って生成され、その後 `man scp(1)` などでサーバーに安全に転送されます。希望するセキュリティポリシーに合致する場合は、サーバー上で直接作成することもできます。

keytab を安全な方法でサーバーに転送することは非常に重要です。もし鍵を他の誰かに知られたら、その者は任意のユーザーになりすましてサーバーにアクセスできてしまいます。KDC データベース内のホストプリンシパルのエントリも `kadmin` を使って作成されるため、サーバー上で直接 `kadmin` を使用するのは便利です。

もちろん、`kadmin` は Kerberos 化されたサービスです。ネットワークサービスに対する認証には Kerberos チケットが必要ですが、`kadmin` を実行しているユーザーが実際に存在する（そしてセッションが乗っ取られていない）ことを確実にするため、`kadmin` は新しいチケットを取得するためにパスワードを要求します。kadmin サービスに対して認証するプリンシパルは、`/var/heimdal/kadmind.acl` で指定されているように、`kadmin` インターフェースの使用を許可されている必要があります。「Remote administration（リモート管理）」というタイトルのセクションを参照してください。

アクセス制御リストの設計に関する詳細は、`info heimdal` の管理（administration）に関する節を参照してください。

リモートの `kadmin` アクセスを有効にする代わりに、管理者はローカルコンソールまたは `man ssh(1)` を使用して KDC に安全に接続し、`kadmin -l` を使用してローカルで管理を実行できます。

`/etc/krb5.conf` をインストールしたら、`kadmin` で `add --random-key` を使用します。これにより、サーバーのホストプリンシパルがデータベースに追加されますが、ホストプリンシパルキーのコピーは keytab に抽出されません。keytab を生成するには、`ext` を使用してサーバーのホストプリンシパルキーを独自の keytab に抽出します。

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

`ext_keytab` はデフォルトで抽出したキーを `/etc/krb5.keytab` に保存することに注意してください。これは Kerberos 化されるサーバー上で実行する場合は適切ですが、keytab を別の場所で抽出する場合は `--keytab _path/to/file_` 引数を使用する必要があります。

```shell
# kadmin
```

出力は次のようになります。

```
kadmin> ext_keytab --keytab=/tmp/example.keytab host/myserver.example.org
kadmin> exit
```

その後、keytab は `man scp(1)` またはリムーバブルメディアを使用してサーバーに安全にコピーできます。システムの keytab に不要なキーを挿入しないように、デフォルト以外の keytab 名を指定してください。

この時点で、サーバーは `/etc/krb5.keytab` に保存された共有キーを使用して KDC から暗号化されたメッセージを読み取ることができます。これで Kerberos を使用するサービスを有効にする準備ができました。最も一般的なサービスの 1 つは `man sshd(8)` で、GSS-API を介して Kerberos をサポートします。`/etc/ssh/sshd_config` に次の行を追加します。

```
GSSAPIAuthentication yes
```

この変更を行った後、新しい構成を有効にするために `man sshd(8)` を再起動する必要があります: `service sshd restart`。

### Kerberos を使用するクライアントの構成

サーバーの場合と同様に、クライアントは `/etc/krb5.conf` の構成が必要です。ファイルを（安全に）所定の場所にコピーするか、必要に応じて再入力します。

クライアントで `kinit`、`klist`、`kdestroy` を使用して、既存のプリンシパルのチケットを取得、表示、削除することでクライアントをテストします。Kerberos アプリケーションは、Kerberos 対応サーバーに接続できるはずです。それが機能せず、チケットの取得が機能する場合、問題はおそらくサーバーにあり、クライアントや KDC にはありません。

Kerberos 化された `man ssh(1)` の場合、GSS-API はデフォルトで無効になっているため、`ssh -o GSSAPIAuthentication=yes _hostname_` を使用してテストします。

Kerberos 化されたアプリケーションをテストするときは、`tcpdump` などのパケットスニッファを使用して、機密情報が平文で送信されていないことを確認してください。

さまざまな Kerberos クライアントアプリケーションが利用可能です。認証に SASL を使用するアプリケーションが GSS-API メカニズムも使用できるようにするブリッジの登場により、Jabber クライアントから IMAP クライアントまで、多くの種類のクライアントアプリケーションが認証に Kerberos を使用できます。

レルム内のユーザーは通常、自分の Kerberos プリンシパルがローカルユーザーアカウントにマッピングされています。一致する Kerberos プリンシパルを持たない誰かにローカルユーザーアカウントへのアクセスを許可する必要がある場合があります。たとえば、`tillman@EXAMPLE.ORG` がローカルユーザーアカウント `webdevelopers` へのアクセスを必要とする場合があります。他のプリンシパルもそのローカルアカウントへのアクセスを必要とする場合があります。

ユーザーのホームディレクトリに配置された `.k5login` ファイルと `.k5users` ファイルは、この問題を解決するために使用できます。たとえば、次の `.k5login` が `webdevelopers` のホームディレクトリに配置されている場合、リストされている両方のプリンシパルは、共有パスワードを必要とせずにそのアカウントにアクセスできます:

```
tillman@example.org
jdoe@example.org
```

`.k5users` の詳細については、`man ksu(1)` を参照してください。

### MIT との違い

MIT 実装と Heimdal 実装の主な違いは、`kadmin` が異なるが同等なコマンドセットを持ち、異なるプロトコルを使用することです。KDC が MIT の場合、Heimdal バージョンの `kadmin` を使用して KDC をリモート管理することはできません。逆も同様です。

クライアントアプリケーションも、同じタスクを実行するために若干異なるコマンドラインオプションを使用する場合があります。http://web.mit.edu/Kerberos/www の指示に従ってください。

推荐使用 [MIT Kerberos](http://web.mit.edu/Kerberos/www/)。注意路径问题：MIT port 默认安装到 `/usr/local/`，如果 `PATH` 将系统目录放在前面，则会运行 FreeBSD 系统应用程序而不是 MIT 版本。

在 FreeBSD 上使用 MIT Kerberos 作为 KDC 时，执行以下命令以将所需配置添加到 `/etc/rc.conf`：

```shell
# sysrc kdc_program="/usr/local/sbin/krb5kdc"
# sysrc kadmind_program="/usr/local/sbin/kadmind"
# sysrc kdc_flags=""
# sysrc kdc_enable="YES"
# sysrc kadmind_enable="YES"
```

### Kerberos 提示、技巧和故障排除

在配置和排查 Kerberos 问题时，请牢记以下几点：

- 当使用来自 ports 的 Heimdal 或 MIT Kerberos 时，确保 `PATH` 将 ports 版本的客户端应用排在系统版本之前。
- 如果领域中的所有计算机没有同步时间设置，认证可能会失败。crossref:network-servers[network-ntp, “使用 NTP 进行时钟同步”] 描述了如何使用 NTP 同步时钟。
- 如果主机名更改，`host/` principal 也必须更改，并更新 keytab。这也适用于特殊的 keytab 条目，例如 Apache 的 `www/mod_auth_kerb` 包所使用的 `HTTP/` principal。
- 领域中的所有主机都必须在 DNS 中能够正向和反向解析，或至少存在于 `/etc/hosts` 中。CNAME 可以工作，但 A 和 PTR 记录必须正确且存在。无法解析主机时出现的错误消息并不直观：`Kerberos5 refuses authentication because Read req failed: Key table entry not found`.
- 某些作为 KDC 客户端的操作系统不会将 `ksu` 的权限设置为 setuid `root`。这意味着 `ksu` 无法工作。这是权限问题，不是 KDC 错误。
- 使用 MIT Kerberos 时，若要允许某个 principal 的票据寿命超过默认的十小时，请在 man kadmin(8) 提示符下使用 `modify_principal` 更改相关 principal 和 `krbtgt` principal 的 `maxlife`。然后该 principal 可以使用 `kinit -l` 请求更长寿命的票据。
- 在 KDC 上运行数据包嗅探器以帮助排查从工作站执行 `kinit` 的问题时，票据授予票据（TGT）会在输入密码之前立即发送。这是因为 Kerberos 服务器会向任何未经授权的请求自由传输 TGT。但是，每个 TGT 都使用从用户密码派生的密钥加密。当用户输入密码时，密码不会发送到 KDC，而是用于解密 `kinit` 已经获取的 TGT。如果解密过程产生带有有效时间戳的有效票据，则用户拥有有效的 Kerberos 凭据。这些凭据包括一个用于将来与 Kerberos 服务器建立安全通信的会话密钥，以及实际的 TGT，该 TGT 使用 Kerberos 服务器自身的密钥加密。这第二层加密使 Kerberos 服务器能够验证每个 TGT 的真实性。
- 主机 principal 可以拥有更长的票据寿命。如果用户 principal 的寿命为一周，而所连接的主机寿命为九小时，则用户缓存将包含过期的主机 principal，票据缓存将无法按预期工作。
- 在按照 man kadmind(8) 中的描述设置 `krb5.dict` 以防止使用特定的不良密码时，请记住它仅适用于分配了密码策略的 principal。`krb5.dict` 使用的格式是每行一个字符串。创建指向 `/usr/share/dict/words` 的符号链接可能会很有用。

### 缓解 Kerberos 的限制

由于 Kerberos 是一种“全有或全无”的方法，网络上启用的每个服务都必须要么进行修改以与 Kerberos 配合使用，要么以其他方式防范网络攻击。这是为了防止用户凭据被盗用和重用。例如，Kerberos 已在所有远程 shell 上启用，但未启用 Kerberos 的 POP3 邮件服务器仍以明文发送密码。

KDC 是单点故障。按照设计，KDC 必须与其主密码数据库一样安全。KDC 上绝对不能运行任何其他服务，并且必须进行物理安全保护。风险很高，因为 Kerberos 使用同一个主密钥加密所有密码，而该主密钥以文件形式存储在 KDC 上。

一个被攻破的主密钥是

これは、それほど恐れるほどのものではありません。マスターキーは、Kerberos データベースの暗号化と、乱数生成器のシードとしてのみ使用されます。KDC へのアクセスが安全である限り、攻撃者がマスターキーを利用してできることはほとんどありません。

KDC が利用できない場合、認証を実行できないため、ネットワークサービスは利用できなくなります。これは、1 つのマスター KDC と 1 つ以上のスレーブを使用し、PAM を使用したセカンダリまたはフォールバック認証を慎重に実装することで緩和できます。

Kerberos では、ユーザー、ホスト、サービスが相互に認証できますが、KDC をユーザー、ホスト、サービスに対して認証するメカニズムはありません。つまり、トロイの木馬化された `kinit` がすべてのユーザー名とパスワードを記録する可能性があります。`security/tripwire` パッケージのようなファイルシステム整合性チェックツールを使用すると、これを軽減できます。

### 参考資料と詳細情報

* [The Kerberos FAQ](http://www.faqs.org/faqs/Kerberos-faq/general/preamble.html)
* [Designing an Authentication System: a Dialog in Four Scenes](http://web.mit.edu/Kerberos/www/dialogue.html)
* [RFC 4120, The Kerberos Network Authentication Service (V5)](https://www.ietf.org/rfc/rfc4120.txt)
* [MIT Kerberos ホームページ](http://web.mit.edu/Kerberos/www/)
* [Heimdal Kerberos プロジェクト Wiki ページ](https://github.com/heimdal/heimdal/wiki)

[[tcpwrappers]]









...設定ファイル、特に特権アクセスを使用する場合。

<a id="security-rctl"></a>

### リソース制限の有効化と設定

`man rctl(8)` システムは、個々のプロセスおよびユーザーに対してリソース制限を設定・管理する、より細かい方法を提供します。
ユーザークラスに関係なく、特定のプロセスやユーザーにリソース制限を動的に割り当てることができます。

`man rctl(8)` を使用する最初の手順は、`/boot/loader.conf` に次の行を追加して有効にし、システムを再起動することです。

```
kern.racct.enable=1
```

次に、以下のコマンドを実行して `man rctl(8)` サービスを有効化し、起動します。

```shell
# sysrc rctl_enable="YES"
# service rctl start
```

その後、`man rctl(8)` を使用してシステムのルールを設定できます。

ルール構文（`man rctl.conf(5)`）は、subject（主体）、subject-id（主体 ID）、resource（リソース）、action（アクション）を使用して制御されます。次のルール例のとおりです。

```
subject:subject-id:resource:action=amount/per
```

たとえば、ユーザーが 10 を超えるプロセスを追加できないように制限するには、次のコマンドを実行します。

```shell
# rctl -a user:username:maxproc:deny=10/user
```

適用されたリソース制限を確認するには、`man rctl(8)` コマンドを実行します。

```shell
# rctl
```

出力は次のようになります。

```
user:username:maxproc:deny=10
```

ルールは、`/etc/rctl.conf` に追加されていれば、再起動後も保持されます。
形式は、前述のコマンドを含まないルールです。たとえば、前のルールは次のように追加できます。

```
user:username:maxproc:deny=10
```

<a id="security-pkg"></a>

## サードパーティー製ソフトウェアのセキュリティ問題の監視

近年、セキュリティの世界では、脆弱性評価の扱いが大きく改善されました。現在利用可能なほとんどすべてのオペレーティングシステムにサードパーティー製ユーティリティがインストールされ設定されるにつれて、システムへの侵入の脅威は増大しています。

脆弱性評価はセキュリティにおける重要な要素です。FreeBSD はベースシステムに関するアドバイザリをリリースしますが、すべてのサードパーティー製ユーティリティについてそれを実行することは、FreeBSD Project の能力を超えています。サードパーティーの脆弱性を軽減し、既知のセキュリティ問題を管理者に警告する方法があります。pkg として知られる FreeBSD のアドオン・ユーティリティには、この目的のためのオプションが明示的に含まれています。

pkg はセキュリティ問題についてデータベースを照会します。このデータベースは、FreeBSD セキュリティチームと ports 開発者によって更新・維持されています。

インストールにより、pkg audit データベースを維持するための man periodic(8) 設定ファイルが提供され、それを最新の状態に保つプログラム的な方法も提供されます。

インストール後、いつでも Ports Collection の一部としてサードパーティー製ユーティリティを監査するために、管理者はデータベースを更新し、インストール済みパッケージの既知の脆弱性を表示することができます。

```shell
% pkg audit -F
```

出力は次のようになります。

```text
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

表示された URL を Web ブラウザーで開くことにより、管理者はこの脆弱性に関する詳細情報を得ることができます。

これには、FreeBSD port バージョンで影響を受けるバージョンと、セキュリティアドバイザリを含む可能性のある他の Web サイトが含まれます。

<a id="security-advisories"></a>

## FreeBSD セキュリティ勧告

高品質なオペレーティングシステムを提供する多くのプロジェクトと同様に、FreeBSD Project にはセキュリティチームがあります。このチームは、各 FreeBSD リリースのサポート終了 (End-of-Life: EoL) 日を決定し、まだ EoL に達していないサポート対象リリースにセキュリティ更新を提供する責任を負っています。

FreeBSD セキュリティチームとサポート対象リリースの詳細については、[FreeBSD セキュリティページ](https://www.FreeBSD.org/security) を参照してください。

セキュリティチームの任務の 1 つは、FreeBSD オペレーティングシステムで報告されたセキュリティ脆弱性に対応することです。脆弱性が確認されると、セキュリティチームは脆弱性の修正に必要な手順を検証し、修正をソースコードに反映します。その後、詳細を「セキュリティ勧告」(Security Advisory) として公開します。

セキュリティ勧告は [FreeBSD ウェブサイト](https://www.FreeBSD.org/security/advisories/) で公開され、`freebsd-security-notifications`、`freebsd-security`、`freebsd-announce` の各メーリングリストに送信されます。

### セキュリティ勧告の形式

以下は、FreeBSD セキュリティ勧告の例です。

```text
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

c) Recompile the oper
```



* `Background` フィールドは、影響を受けるモジュールの説明を提供します。
* `Problem Description` フィールドは、脆弱性を説明します。これには、欠陥のあるコードや、ユーティリティが悪意を持って使用される方法に関する情報が含まれます。
* `Impact` フィールドは、問題がシステムに与える可能性のある影響の種類を説明します。
* `Workaround` フィールドは、システムに直ちにパッチを適用できないシステム管理者に対して、回避策が利用可能かどうかを示します。
* `Solution` フィールドは、影響を受けるシステムにパッチを適用するための手順を提供します。これは、システムにパッチを適用して安全に動作させるための、テスト済みで検証済みの段階的な方法です。
* `Correction Details` フィールドは、修正されたコードを含む各影響を受ける Subversion または Git ブランチをリビジョン番号とともに表示します。
* `References` フィールドは、脆弱性に関する追加情報のソースを提供します。

---

## 翻訳メモ

- 機械支援初訳。コマンド例は原文照合推奨。
- 用語は `handbook/ja/glossary.md` と揃える。
