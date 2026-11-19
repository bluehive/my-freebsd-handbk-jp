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

<a id="userppp"></a>
## PPP の設定

FreeBSD には、`ppp(8)` を使ってダイヤルアップ PPP 接続を管理するための機能が標準で組み込まれています。デフォルトの FreeBSD カーネルは、モデムハードウェアとのやり取りに使用される `tun` をサポートしています。設定は 1 つ以上の設定ファイルを編集することで行い、サンプルを含む設定ファイルも用意されています。設定後、`ppp` を使って接続を開始・管理します。

PPP 接続を利用するには、次の項目が必要です。

* インターネットサービスプロバイダ（ISP）のダイヤルアップアカウント
* ダイヤルアップモデム
* ISP のダイヤルアップ電話番号
* ISP から割り当てられたログイン名とパスワード
* 1 台以上の DNS サーバーの IP アドレス。通常は ISP から提供されますが、提供されない場合でも、FreeBSD 側で DNS ネゴシエーションを使うように設定できます。

必要な情報のいずれかが不足している場合は、ISP に問い合わせてください。

以下の情報は ISP から提供される場合もありますが、必須ではありません。

* デフォルトゲートウェイの IP アドレス。この情報がわからない場合でも、接続の確立時に ISP が正しい値を自動的に提供します。FreeBSD で PPP を設定する際、このアドレスは `HISADDR` として参照されます。
* サブネットマスク。ISP から提供されていない場合、`ppp(8)` の設定ファイルでは `255.255.255.255` が使用されます。
* ISP から固定 IP アドレスとホスト名が割り当てられている場合は、それらを設定ファイルに記入します。そうでない場合、これらの情報は接続の確立時に自動的に提供されます。

この節の残りでは、一般的な PPP 接続シナリオにおける FreeBSD の設定方法を説明します。必要な設定ファイルは `/etc/ppp/ppp.conf` であり、追加のファイルやサンプルは `/usr/share/examples/ppp/` に用意されています。

> **注**: この節を通じて、多くのファイル例に行番号を付けています。これらの行番号は解説を追いやすくするために付けたものであり、実際のファイルに記述するものではありません。
>
> 設定ファイルを編集する際は、適切なインデントが重要です。`:` で終わる行は 1 列目（行頭）から始め、それ以外のすべての行は例に示されているとおりスペースまたはタブでインデントしてください。

<a id="userppp-staticIP"></a>
### 基本設定

PPP 接続を設定するには、まず `/etc/ppp/ppp.conf` を編集して ISP のダイヤルイン情報を記述します。このファイルの内容は次のとおりです。

```
1     default:
2       set log Phase Chat LCP IPCP CCP tun command
3       ident user-ppp VERSION
4       set device /dev/cuau0
5       set speed 115200
6       set dial "ABORT BUSY ABORT NO\\sCARRIER TIMEOUT 5 \
7                 \"\" AT OK-AT-OK ATE1Q0 OK \\dATDT\\T TIMEOUT 40 CONNECT"
8       set timeout 180
9       enable dns
10
11    provider:
12      set phone "(123) 456 7890"
13      set authname foo
14      set authkey bar
15      set timeout 300
16      set ifaddr x.x.x.x/0 y.y.y.y/0 255.255.255.255 0.0.0.0
17      add default HISADDR
```

**1 行目**
: `default` エントリを識別します。このエントリ内のコマンド（2〜9 行目）は、`ppp` を実行すると自動的に実行されます。

**2 行目**
: 接続テスト用に詳細なログ出力パラメータを有効にします。設定が問題なく動作するようになったら、この行は次のように簡略化してください。

```
set log phase tun
```

**3 行目**
: 接続先の PPP ソフトウェアに対して `ppp(8)` のバージョンを通知します。

**4 行目**
: モデムが接続されているデバイスを指定します。`COM1` は `/dev/cuau0`、`COM2` は `/dev/cuau1` です。

**5 行目**
: 接続速度を設定します。古いモデムで `115200` が動作しない場合は、代わりに `38400` を試してください。

**6〜7 行目**
: expect-send 構文で記述されたダイヤル文字列です。詳細は `chat(8)` を参照してください。
  なお、このコマンドは読みやすさのために次の行へ継続しています。`/etc/ppp/ppp.conf`（`ppp.conf`）では、行末の文字を `\` にすることで任意のコマンドを次の行へ継続できます。

**8 行目**
: リンクのアイドルタイムアウトを秒単位で設定します。

**9 行目**
: ピア（接続先）に対して DNS 設定を確認するよう指示します。ローカルネットワークで独自の DNS サーバーを運用している場合は、行頭に `#` を付けてコメントアウトするか、この行を削除してください。

**10 行目**
: 読みやすくするための空行です。空行は `ppp(8)` によって無視されます。

**11 行目**
: `provider` という名前のエントリを識別します。ここは ISP の名前に変更することもでき、そうすれば `load` *ISP* で接続を開始できます。

**12 行目**
: ISP の電話番号を指定します。コロン（`:`）またはパイプ文字（`|`）を区切り文字として複数の電話番号を指定できます。番号を順番にローテーションさせるにはコロンを使い、常に最初の番号へ最初にダイヤルを試みて失敗した場合にのみ他の番号を使うにはパイプ文字を使います。ダイヤル失敗を防ぐため、電話番号の指定全体は必ず二重引用符（`"`）で囲んでください。

**13〜14 行目**
: ISP のユーザー名とパスワードを指定します。

**15 行目**
: 接続のデフォルトアイドルタイムアウトを秒単位で設定します。この例では、300 秒間通信がないと接続が自動的に切断されます。タイムアウトを無効にするには、この値を 0 に設定します。

**16 行目**
: インターフェースのアドレスを設定します。使用する値は、ISP から固定 IP アドレスを取得しているか、接続時に動的 IP アドレスをネゴシエーションするかによって異なります。
  ISP から固定 IP アドレスとデフォルトゲートウェイが割り当てられている場合は、*x.x.x.x* を固定 IP アドレスに、*y.y.y.y* をデフォルトゲートウェイの IP アドレスに置き換えます。ISP から固定 IP アドレスのみが提供され、ゲートウェイアドレスが提供されていない場合は、*y.y.y.y* を `10.0.0.2/0` に置き換えます。
  接続のたびに IP アドレスが変わる場合は、この行を次のように変更します。これにより、`ppp(8)` は IP Configuration Protocol（IPCP）を使用して動的 IP アドレスをネゴシエーションするようになります。

```
set ifaddr 10.0.0.1/0 10.0.0.2/0 255.255.255.255 0.0.0.0
```

**17 行目**
: この行はゲートウェイへのデフォルトルートを追加するため、そのまま残します。`HISADDR` は 16 行目で指定したゲートウェイアドレスに自動的に置き換えられます。この行は必ず 16 行目より後ろに記述する必要があります。

`ppp(8)` を手動で起動するか自動で起動するかによっては、次の行を含む `/etc/ppp/ppp.linkup` の作成も必要になる場合があります。このファイルは `ppp` を `-auto` モードで実行する際に必要です。このファイルは接続が確立された後に使用されます。その時点では IP アドレスが割り当て済みになっているため、ルーティングテーブルのエントリを追加できるようになります。このファイルを作成するときは、*provider* が `ppp.conf` の 11 行目で示した値と一致していることを確認してください。

```
provider:
      add default HISADDR
```

固定 IP アドレス構成でデフォルトゲートウェイアドレスを「推測」する場合にも、このファイルが必要です。その場合は、`ppp.conf` から 17 行目を削除し、上記の 2 行を含む `/etc/ppp/ppp.linkup` を作成してください。このファイルの他の例は `/usr/share/examples/ppp/` にあります。

デフォルトでは、`ppp` は `root` として実行する必要があります。このデフォルトを変更するには、`ppp` を実行させたいユーザーのアカウントを `/etc/group` の `network` グループに追加します。

次に、`/etc/ppp/ppp.conf` で `allow` を使用して、そのユーザーに 1 つ以上のエントリへのアクセス権を付与します。たとえば、`fred` と `mary` に `provider:` エントリのみの権限を与えるには、`provider:` セクションに次の行を追加します。

```
allow users fred mary
```

指定したユーザーにすべてのエントリへのアクセス権を与えるには、代わりに `default` セクションへその行を記述します。

<a id="chapter-31-heading-05"></a>
### 高度な設定

PPP は、要求に応じて DNS および NetBIOS ネームサーバーのアドレスを供給するように設定することもできます。

PPP バージョン 1.x でこれらの拡張機能を有効にするには、`/etc/ppp/ppp.conf` の該当セクションに次の行を追加します。

```
enable msext
set ns 203.14.100.1 203.14.100.2
set nbns 203.14.100.5
```

PPP バージョン 2 以降では次のようにします。

```
accept dns
set dns 203.14.100.1 203.14.100.2
set nbns 203.14.100.5
```

これにより、プライマリおよびセカンダリのネームサーバーアドレスと、NetBIOS ネームサーバーのホストがクライアントに通知されます。

バージョン 2 以降では、`set dns` 行を省略すると、PPP は `/etc/resolv.conf` に記載されている値を使用します。

<a id="userppp-PAPnCHAP"></a>
#### PAP および CHAP 認証

一部の ISP では、接続時の認証を PAP または CHAP 認証メカニズムのいずれかで行うようにシステムを構成しています。この場合、ISP は接続時に `login:` プロンプトを表示せず、直ちに PPP 通信を開始します。

PAP は CHAP より安全性が低いものの、PAP ではパスワードが平文で送信されるとはいえシリアル回線上のみを流れるため、通常はセキュリティ上の問題にはなりません。クラッカーが「盗聴」できる余地はあまりないためです。

次の変更を行う必要があります。

```
13      set authname MyUserName
14      set authkey MyPassword
15      set login
```

**13 行目**
: PAP/CHAP のユーザー名を指定します。*MyUserName* には正しい値を入力してください。

**14 行目**
: PAP/CHAP のパスワードを指定します。*MyPassword* には正しい値を入力してください。意図を明確にするために、次のような行を追加することもできます。

```
16      accept PAP
```

あるいは

```
16      accept CHAP
```

ただし、PAP と CHAP はどちらもデフォルトで受け入れられます。

**15 行目**
: PAP または CHAP を使用する場合、通常 ISP はサーバーへのログインを要求しません。そのため、`"set login"` の文字列を無効にします。

<a id="userppp-nat"></a>
#### PPP のネットワークアドレス変換（NAT）機能の利用

PPP には、カーネルの divert 機能を使わずに内部 NAT を利用する機能があります。この機能は、`/etc/ppp/ppp.conf` に次の行を追加することで有効にできます。

```
nat enable yes
```

あるいは、コマンドラインオプション `-nat` で NAT を有効にすることもできます。また、`/etc/rc.conf` には `ppp_nat` という設定項目もあり、デフォルトで有効になっています。

この機能を使用する場合、着信接続の転送を有効にするために `/etc/ppp/ppp.conf` に次のオプションを含めると便利です。

```
nat port tcp 10.0.0.2:ftp ftp
nat port tcp 10.0.0.2:http http
```

あるいは、外部からの接続を一切信頼しない場合は次のようにします。

```
nat deny_incoming yes
```

<a id="userppp-final"></a>
### 最終的なシステム設定

これで `ppp` の設定は完了しましたが、`/etc/rc.conf` にもいくつか編集が必要です。

このファイルを上から順に確認し、`hostname=` 行が設定されていることを確かめてください。

```
hostname="foo.example.com"
```

ISP から固定 IP アドレスとホスト名が提供されている場合は、その名前をホスト名として使用します。

次に `network_interfaces` 変数を確認します。必要に応じて ISP へオンデマンドダイヤルするようにシステムを設定する場合は、`tun0` デバイスがリストに含まれていることを確認し、そうでなければ削除します。

```
network_interfaces="lo0 tun0"
ifconfig_tun0=
```

> **注**: `ifconfig_tun0` 変数は空のままにし、`/etc/start_if.tun0` というファイルを作成してください。このファイルには次の行を記述します。

```
ppp -auto mysystem
```

> このスクリプトはネットワーク設定時に実行され、ppp デーモンを自動モードで起動します。このマシンがゲートウェイとして機能する場合は、`-alias` の追加を検討してください。詳細は man ページを参照してください。

`/etc/rc.conf` に次の行を記述し、ルータープログラムが `NO` に設定されていることを確認します。

```
router_enable="NO"
```

`routed` デーモンが起動されないようにすることが重要です。`routed` は、`ppp` が作成したデフォルトルーティングテーブルのエントリを削除してしまう傾向があるためです。

また、`sendmail_flags` 行に `-q` オプションが含まれていないことを確認しておくとよいでしょう。含まれていると、`sendmail` が時折ネットワーク参照を試み、マシンが意図せずダイヤルアウトしてしまう可能性があります。次のように設定してみてください。

```
sendmail_flags="-bd"
```

欠点は、PPP リンクが確立されるたびに `sendmail` へメールキューを再検査させなければならない点です。これを自動化するには、`ppp.linkup` に `!bg` を含めます。

> **訳注**: 原文は "The downside is that `sendmail` is forced to re-examine the mail queue whenever the ppp link." と文末の語句が欠落していますが、直後の `ppp.linkup` による自動化の説明に合わせ、PPP リンク確立時にメールキューを再検査させる趣旨として訳しています。

```
1     provider:
2       delete ALL
3       add 0 0 HISADDR
4       !bg sendmail -bd -q30m
```

別の方法として、SMTP トラフィックをブロックする「dfilter」を設定することもできます。詳細はサンプルファイルを参照してください。

<a id="chapter-31-heading-09"></a>
### `ppp` の利用

残る作業はマシンの再起動だけです。再起動後、次のように入力します。

```shell
# ppp
```

続いて `dial provider` と入力して PPP セッションを開始します。あるいは、`start_if.tun0` が存在しない状態で、外向きトラフィックが発生したときに自動的にセッションを確立するよう `ppp` を起動するには、次のように入力します。

```shell
# ppp -auto provider
```

適切な診断用ポートを設定しておけば、バックグラウンドで実行中の `ppp` プログラムと対話することもできます。これを行うには、設定に次の行を追加します。

```
set server /var/run/ppp-tun%d DiagnosticPassword 0177
```

これにより、PPP は指定された UNIX® ドメインソケットで待ち受け、アクセスを許可する前にクライアントへ指定されたパスワードを要求するようになります。名前の中の `%d` は、使用中の `tun` デバイス番号に置き換えられます。

ソケットを設定しておけば、実行中のプログラムをスクリプトから操作したい場合に `pppctl(8)` プログラムを使用できます。

<a id="userppp-mgetty"></a>
### ダイヤルインサービスの設定

[ダイヤルインサービス](30-serialcomms.md#dialup)では、`getty(8)` を使用してダイヤルアップサービスを有効にする方法が詳しく説明されています。

`getty` の代替として、ダイヤルアップ回線を念頭に置いて設計された高機能版 `getty` である `comms/mgetty+sendfax` port があります。

`mgetty` を使用する利点は、モデムと能動的に*対話*できる点です。つまり、`/etc/ttys` でポートが無効になっていれば、モデムは電話に応答しません。

以降のバージョンの `mgetty`（0.99beta 以降）では PPP ストリームの自動検出もサポートされており、クライアントはスクリプトなしでサーバーへアクセスできます。

`mgetty` の詳細については、[http://mgetty.greenie.net/doc/mgetty_toc.html](http://mgetty.greenie.net/doc/mgetty_toc.html) を参照してください。

デフォルトでは、`comms/mgetty+sendfax` port は `AUTO_PPP` オプションが有効になっており、`mgetty` が PPP 接続の LCP フェーズを検出して自動的に ppp シェルを起動できます。ただし、デフォルトのログイン／パスワード入力手順が行われないため、PAP または CHAP のいずれかを使ってユーザーを認証する必要があります。

この節では、システム上で `comms/mgetty+sendfax` port のコンパイルとインストールが完了していることを前提とします。

`/usr/local/etc/mgetty+sendfax/login.config` に次の行が含まれていることを確認します。

```
/AutoPPP/ -     - /etc/ppp/ppp-pap-dialup
```

これにより、PPP 接続が検出された際に `mgetty` が `ppp-pap-dialup` を実行するようになります。

次の内容を含む実行可能ファイル `/etc/ppp/ppp-pap-dialup` を作成します。

```
#!/bin/sh
exec /usr/sbin/ppp -direct pap$IDENT
```

`/etc/ttys` で有効にした各ダイヤルアップ回線について、対応するエントリを `/etc/ppp/ppp.conf` に作成します。これは、先ほど作成した定義と問題なく共存できます。

```
pap:
  enable pap
  set ifaddr 203.14.100.1 203.14.100.20-203.14.100.40
  enable proxy
```

この方法でログインする各ユーザーは、`/etc/ppp/ppp.secret` にユーザー名とパスワードを登録しておく必要があります。あるいは、次のオプションを追加して、`/etc/passwd` を使って PAP でユーザーを認証することもできます。

```
enable passwdauth
```

特定のユーザーに固定 IP アドレスを割り当てるには、`/etc/ppp/ppp.secret` の 3 番目の引数としてそのアドレスを指定します。例については `/usr/share/examples/ppp/ppp.secret.sample` を参照してください。

<a id="ppp-troubleshoot"></a>
## PPP 接続のトラブルシューティング

この節では、モデム接続で PPP を使用する際に発生し得るいくつかの問題を取り上げます。ISP によっては `ssword` というプロンプトを表示するところもあれば、`password` を表示するところもあります。`ppp` のスクリプトがそれに合わせて書かれていないと、ログインに失敗します。`ppp` 接続をデバッグする最も一般的な方法は、この節で説明するように手動で接続することです。

<a id="chapter-31-heading-12"></a>
### デバイスノードの確認

カスタムカーネルを使用している場合は、カーネル設定ファイルに次の行が含まれていることを確認してください。

```
device   uart
```

`uart` デバイスはすでに `GENERIC` カーネルに含まれているため、標準カーネルを使用している場合は追加の手順は不要です。次のコマンドで `dmesg` の出力からモデムデバイスを確認してください。

```shell
# dmesg | grep uart
```

これにより、`uart` デバイスに関する該当出力が表示されます。これらが必要な COM ポートです。モデムが標準のシリアルポートとして動作する場合、`uart1`（`COM2`）として表示されるはずです。その場合、カーネルの再構築は不要です。対応を確認すると、モデムが `uart1` に接続されている場合、モデムデバイスは `/dev/cuau1` になります。

<a id="chapter-31-heading-13"></a>
### 手動での接続

`ppp` を手動で操作してインターネットに接続する方法は手早く簡単であり、接続をデバッグしたり、ISP が `ppp` クライアント接続をどのように扱っているかを調べたりするのに非常に有効です。コマンドラインから PPP を起動してみましょう。以下の例ではすべて、PPP を実行しているマシンのホスト名として *example* を使用します。`ppp` を起動するには次のように入力します。

```shell
# ppp
```

```shell
ppp ON example> set device /dev/cuau1
```

この 2 番目のコマンドで、モデムデバイスを `cuau1` に設定します。

```shell
ppp ON example> set speed 115200
```

これで接続速度が 115,200 kbps に設定されます。

> **訳注**: 原文では `115,200 kbps` と記載されていますが、[FreeBSD 15.0 ppp(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/ppp/ppp.8) のとおり `set speed 115200` は bps 単位（115,200 bps、すなわち 115.2 kbps）の設定です。

```shell
ppp ON example> enable dns
```

これにより、`ppp` はリゾルバを設定し、`/etc/resolv.conf` にネームサーバーの行を追加します。`ppp` がホスト名を特定できない場合は、後で手動設定できます。

```shell
ppp ON example> term
```

これにより、モデムを手動で操作するための「ターミナル」モードに切り替わります。

```
deflink: Entering terminal mode on /dev/cuau1
type '~h' for help
```

```shell
at
OK
atdt123456789
```

`at` でモデムを初期化し、続いて `atdt` と ISP の電話番号を入力してダイヤルイン処理を開始します。

```shell
CONNECT
```

接続の確認表示です。ハードウェア以外の接続問題がある場合は、この段階で原因の切り分けを行います。

```shell
ISP Login:myusername
```

このプロンプトが表示されたら、ISP から提供されたユーザー名を入力して応答します。

```shell
ISP Pass:mypassword
```

このプロンプトでは、ISP から提供されたパスワードを入力します。FreeBSD へのログイン時と同様、パスワードは画面にエコーバックされません。

```shell
Shell or PPP:ppp
```

ISP によっては、このプロンプトは表示されない場合があります。表示された場合は、プロバイダ側でシェルを使うか `ppp` を起動するかを尋ねています。この例では、インターネット接続を確立するために `ppp` を選択しました。

```shell
Ppp ON example>
```

この例では、最初の `p` が大文字になっていることに注目してください。これは ISP への接続に成功したことを示しています。

```shell
Ppp ON example>
```

ISP との認証に成功し、IP アドレスの割り当てを待っている状態です。

> **訳注**: 原文のコード例は直前と同じ `Ppp ON example>` となっていますが、[FreeBSD 15.0 ppp(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/ppp/ppp.8) では認証完了時に 2 文字目の `p` も大文字になり `PPp ON ...>` となります。コード例は原文どおり保持しています。

```shell
PPP ON example>
```

IP アドレスの合意が成立し、接続が正常に完了しました。

```shell
PPP ON example>add default HISADDR
```

ここでデフォルトルートを追加します。この時点では接続が確立している相手はピアだけなので、外部と通信できるようにするにはこの操作が必要です。既存のルートが原因で失敗する場合は、`add` の前に感嘆符 `!` を付けてください。あるいは、実際に接続する前にこの設定を行っておけば、それに応じて新しいルートがネゴシエーションされます。

すべてうまくいけば、インターネットへのアクティブな接続が確立されているはずです。これは `Ctrl`+`Z` でバックグラウンドへ移すことができます。`PPP` が `ppp` に戻った場合、接続は切断されています。これは接続状態を示すものとして覚えておくと便利です。大文字の `P` は ISP に接続中であることを表し、小文字の `p` は接続が失われたことを表します。

<a id="chapter-31-heading-14"></a>
### デバッグ

接続を確立できない場合は、`set ctsrts off` を使用してハードウェアフロー制御（CTS/RTS）をオフにしてみてください。これは主に PPP 対応のターミナルサーバーの一部へ接続する際に起こり、PPP が通信リンクへデータを書き込もうとして決して届かない Clear To Send（CTS）信号を待ち続け、ハングしてしまうケースに該当します。このオプションを使う場合は、エンドツーエンドで特定の文字（ほとんどの場合 XON/XOFF）を通すことに依存するハードウェアへの対策として、`set accmap` も併せて指定してください。このオプションの詳細と使い方については `ppp(8)` を参照してください。

古いモデムでは `set parity even` が必要になる場合があります。パリティはデフォルトでは none に設定されていますが、古いモデムではトラフィックが大きく増加した際のエラーチェックに使用されます。

PPP がコマンドモードに戻らない場合、通常は ISP 側がネゴシエーション開始を待っているネゴシエーションエラーです。このタイミングで `~p` を入力すると、ppp に設定情報の送信を強制的に開始させることができます。

ログインプロンプトがまったく表示されない場合は、PAP または CHAP 認証が必要である可能性が高いです。PAP または CHAP を使用するには、ターミナルモードに入る前に次のオプションを PPP に追加します。

```shell
ppp ON example> set authname myusername
```

ここで *myusername* は、ISP から割り当てられたユーザー名に置き換えてください。

```shell
ppp ON example> set authkey mypassword
```

ここで *mypassword* は、ISP から割り当てられたパスワードに置き換えてください。

接続は確立しているのにどのドメイン名も解決できない場合は、IP アドレスを指定して `ping(8)` を試してください。パケット損失が 100 パーセント（100%）になる場合は、デフォルトルートが割り当てられていない可能性が高いです。接続時に `add default HISADDR` が設定されたかを再確認してください。リモートの IP アドレスへ接続できる場合は、`/etc/resolv.conf` にリゾルバのアドレスが追加されていない可能性があります。このファイルは次のようになっているはずです。

```
domain example.com
nameserver x.x.x.x
nameserver y.y.y.y
```

ここで *x.x.x.x* と *y.y.y.y* は、ISP の DNS サーバーの IP アドレスに置き換えてください。

PPP 接続のログを記録するように `syslog(3)` を設定するには、`/etc/syslog.conf` に次の行があることを確認してください。

```
!ppp
*.*     /var/log/ppp.log
```

<a id="pppoe"></a>
## PPP over Ethernet（PPPoE）の利用

この節では、PPP over Ethernet（PPPoE）のセットアップ方法を説明します。

動作する `ppp.conf` の例を次に示します。

```
default:
  set log Phase tun command # add more detailed logging when needed
  set ifaddr 10.0.0.1/0 10.0.0.2/0

name_of_service_provider:
  set device PPPoE:xl1 # replace xl1 with the Ethernet device
  set authname THELOGINNAME
  set authkey THEPASSWORD
  set dial
  set login
  add default HISADDR
```

`root` として次を実行します。

```shell
# ppp -ddial name_of_service_provider
```

`/etc/rc.conf` に次を追加します。

```
ppp_enable="YES"
ppp_mode="ddial"
ppp_nat="YES"	# when needing to enable nat for the local network, otherwise NO
ppp_profile="name_of_service_provider"
```

<a id="chapter-31-heading-16"></a>
### PPPoE サービスタグの利用

接続を確立するためにサービスタグの使用が必要になる場合があります。サービスタグは、特定のネットワークに接続されている複数の異なる PPPoE サーバーを区別するために使用されます。

必要なサービスタグの情報は、ISP から提供されたドキュメントに記載されているはずです。

最後の手段として、`net/rr-pppoe` パッケージまたは port のインストールを試すこともできます。ただし、これを行うとモデムの設定が初期化されて使用不能になる可能性があるため、実行する前に慎重に検討してください。モデムに付属のプログラムをインストールし、そのプログラムから「System」メニューにアクセスするだけです。そこにプロファイル名が表示されているはずです。通常は *ISP* です。

このプロファイル名（サービスタグ）は、`ppp.conf` の PPPoE 設定エントリで `set device` のプロバイダ部分として使用します。詳細は `ppp(8)` を参照してください。次のようになります。

```
set device PPPoE:xl1:ISP
```

*xl1* はお使いのイーサネットカードに対応する適切なデバイス名に変更してください。

*ISP* は実際のプロファイル名に変更してください。

追加情報については、Renaud Waldura による [Cheaper Broadband with FreeBSD on DSL](http://renaud.waldura.com/doc/freebsd/pppoe/) を参照してください。

<a id="ppp-3com"></a>
### 3Com® HomeConnect™ ADSL Modem Dual Link での PPPoE

このモデムは、[RFC 2516](http://www.faqs.org/rfcs/rfc2516.html) で定義されている PPPoE 仕様に準拠していません。

FreeBSD がこのデバイスと通信できるようにするには、sysctl を設定する必要があります。起動時に自動的に設定するには `/etc/sysctl.conf` を更新します。

```
net.graph.nonstandard_pppoe=1
```

あるいは、次のコマンドで即座に設定することもできます。

```shell
# sysctl net.graph.nonstandard_pppoe=1
```

残念ながら、これはシステム全体の設定であるため、通常の PPPoE クライアントまたはサーバーと 3Com® HomeConnect™ ADSL Modem の両方と同時に通信することはできません。
