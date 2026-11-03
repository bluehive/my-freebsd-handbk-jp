<a id="jails"></a>
# 第16章 Jail（Jails）

> **翻訳状態:** 保存済み英語原文との全章照合・自己校正済み（FreeBSD 実機検証は未実施）。
> **上流:** https://docs.freebsd.org/en/books/handbook/jails/
> **ソース参照:** `handbook/en/16-jails.adoc.txt`。取得元リビジョンの記録状況と照合基点は [SOURCE.md](../../SOURCE.md) を参照してください。
> **著作権:** 原文 © The FreeBSD Documentation Project。本日本語訳は BSD-2-Clause（リポジトリ LICENSE）。

本章は保存済みスナップショットの翻訳です。コード内の `{rel-latest}` は原文のリリース属性を表すプレースホルダーであり、そのままシェルへ入力せず、利用する配布物のリリース番号に置き換えてください。インターフェース名・IP アドレス・プール名も環境に合わせて変更します。`#` は root のプロンプトです。コードブロック中の英語コメントと出力例は照合のため原文を保持しています。

<a id="jails-synopsis"></a>
## 概要

システム管理は難しい作業であるため、インストール・設定・保守を容易にするさまざまなツールが開発されてきました。FreeBSD のセキュリティを強化するツールの 1 つが jail です。FreeBSD 4.X から利用でき、有用性・性能・信頼性・セキュリティの改善が続いています。

jail は、プロセス群のルートディレクトリを変更する `chroot(2)` の概念を発展させたものです。chroot は、システムの他の部分から切り離した環境を作り、その外のファイルや資源へのアクセスを制限します。これはサービスの侵害がシステム全体に及ぶことを防ぐための仕組みですが、chroot から脱出する方法も見つかっており、柔軟性や高度な機能を要するサービスの保護には制約があります。

従来の chroot が制限するのはアクセスできるファイルシステムの範囲だけで、他のシステム資源、ユーザー、実行中のプロセス、ネットワークはホストと共有します。jail はファイルシステム・ユーザー集合・ネットワークへのアクセスを仮想化し、さらに細かな制御を加えます。OS レベルの仮想化の一種と考えられます。

本章では次を説明します。

- jail の概要と FreeBSD での用途。
- jail の種類とネットワークの設定方式。
- jail 設定ファイルと各種 jail の作成。
- NAT の設定。
- jail の起動・停止・再起動。
- ホスト側と jail 内からの管理。
- jail のアップグレード。
- リソース制限。
- jail ごとのセキュリティ・機能オプション。
- ZFS データセットの委任。
- FreeBSD の jail マネージャーの紹介（一部）。

<a id="jail-types"></a>
## Jail の種類

基盤となる技術は共通ですが、管理者は構成によって jail をいくつかの種類に分類します。解決したい問題に応じて、適した種類を選びます。以下では特徴と利用上の考慮点を説明します。

<a id="thick-jails"></a>
### Thick Jail

Thick Jail は伝統的な FreeBSD jail です。ライブラリ、実行ファイル、設定ファイルを含むベースシステム全体を jail 内に複製します。ホストの制約内で動く、ほぼ独立した FreeBSD インストールと考えられ、プロセスはホストや他の jail から分離されます。

利点は次のとおりです。

- **分離:** ホストや他の jail とプロセスを分離します。
- **独立性:** ホストや他の jail と異なるライブラリ、設定、ソフトウェアを持てます。
- **セキュリティ:** jail 内に独自のベースシステムを持つため、その環境の問題がホストや他の jail のベースシステムへ直接反映されません。

欠点は、個別のベースシステムの分だけ Thin Jail より資源を消費し、各 jail を個別に保守・更新する必要があることです。

> **訳注:** どの jail もホストのカーネルを共有します。ベースシステムの独立性は、カーネルを分離することを意味しません。

<a id="thin-jails"></a>
### Thin Jail

Thin Jail は、OpenZFS スナップショットまたは NullFS マウントを使ってテンプレートのベースシステムを共有し、各 jail に複製する部分を減らします。Thick Jail と比べて資源消費を抑えられますが、作成後の動作は方式によって異なります。

OpenZFS 方式では、テンプレートのスナップショットから独立したコピーオンライトのクローンを作成します。未変更ブロックは共有しますが、変更によって内容は分岐します。その後のテンプレートの変更は既存クローンへ伝播せず、Thick Jail と同様に個別の保守・更新が必要です。

NullFS 方式では、実行時にテンプレートを読み取り専用でマウントし、ベースシステムを直接共有します。テンプレートを更新すると、それを利用するすべての jail に変更が反映されます。この共通部分への依存により、Thick Jail より独立性が低くなります。つまり Thin Jail は、ベースシステムの大部分を共有し、一部を個別に持つ構成です。

利点は次のとおりです。

- **資源効率:** ベースの共有によりディスク容量やメモリの消費を抑え、同じハードウェアで多くの jail を動かせます。
- **展開速度:** 一般に Thick Jail より作成・起動が速く、多数のインスタンスの展開に向きます。
- **保守の集約:** NullFS 方式なら共通ライブラリやバイナリの保守をテンプレート上で一度行えます。独立した OpenZFS クローンにはこの利点はなく、各 jail の更新が必要です。
- **共有資源:** ライブラリやバイナリの共有によりディスクキャッシュの効率や性能が向上する可能性があります。

欠点は次のとおりです。

- **分離性:** 特に NullFS 方式ではベースを直接共有するため、その問題が複数の jail に同時に影響し得ます。
- **セキュリティ:** 分離の低下により、ある jail の侵害が他の jail やホストに影響するリスクを検討する必要があります。
- **依存関係:** jail ごとに異なるバージョンのライブラリやソフトウェアが必要な場合、依存関係と互換性の管理が複雑になります。
- **互換性:** アプリケーションが想定するベース環境とテンプレートの共通部分が異なると、問題が起きる場合があります。

<a id="service-jails"></a>
### Service Jail

Service Jail はホストのファイルシステムツリー全体を直接共有し、ルートパスは `/` です。ホストのファイルにアクセス・変更でき、ユーザーアカウントも共有します。デフォルトではネットワークなど jail が制限する資源にアクセスできませんが、ホストのネットワークを再利用したり、一部の制限を解除したりできます。必要なファイルを洗い出さずに、少ない設定でサービスやデーモンを jail に閉じ込める用途です。FreeBSD 15.0 以降で利用できます。

利点は次のとおりです。

- **少ない管理作業:** 対応サービスなら `/etc/rc.conf` に 1 行、非対応サービスなら 2 行の設定で利用できます。
- **資源効率:** 追加のディスク領域やネットワーク資源が不要で、Thin Jail よりも軽量です。
- **展開速度:** 同じサービスの複数インスタンスを必要とせず、個々のサービスだけを jail 化する場合、一般に Thin Jail より作成・起動が速くなります。
- **資源共有:** ライブラリやバイナリをすべてホストと共有し、ディスクキャッシュや性能の改善が期待できます。
- **プロセス分離:** 同じユーザーのプロセスであっても、Service Jail の子でないプロセスは見えません。

欠点は、Thick Jail や Thin Jail と異なりファイルシステムを分離しないことです。侵害されたサービスがホスト上の広い範囲に影響し得ます。

以下で扱う設定の多くは Service Jail には不要ですが、仕組みを理解するうえで役立ちます。具体的な設定は [Service Jail の設定](#service-jails-config)を参照してください。

<a id="vnet-jails"></a>
### VNET Jail

VNET Jail は、その中のプロセスに独立したネットワークスタックを提供し、ネットワーク資源を分離・制御します。ホストや他の jail とネットワークトラフィックを分離でき、高度なネットワーク分割に役立ちます。

VNET はネットワークの構成方式を追加するものなので、Thick Jail と Thin Jail のどちらにも組み合わせられます。

<a id="linux-jails"></a>
### Linux Jail

Linux Jail は、FreeBSD jail 内で Linux バイナリやアプリケーションを動かす機能です。互換レイヤーが一部の Linux システムコールなどを FreeBSD カーネル上で扱えるようにします。別の Linux 仮想マシンを用意せずに Linux ソフトウェアを実行するためのものです。

<a id="host-configuration"></a>

## ホストの設定

ホスト上に jail を作成する前に、ホストの設定と情報の確認が必要です。
`jail(8)` ユーティリティを設定し、jail の設定・インストールに必要なディレクトリを作成します。また、ホストのネットワーク情報を調べ、ファイルシステムが OpenZFS と UFS のどちらであるかを確認します。

> **ヒント:** jail 内で動かす FreeBSD のバージョンは、ホストのバージョンより新しくすることはできません。

<a id="host-configuration-jail-utility"></a>

### Jail ユーティリティ

jail の管理には `jail(8)` を使います。
システム起動時に jail を起動するには、次のコマンドを実行します。

```sh
# sysrc jail_enable="YES"
# sysrc jail_parallel_start="YES"
```

> **ヒント:** `jail_parallel_start` を有効にすると、設定された jail はバックグラウンドで起動します。

標準では、設定ファイルに定義されたすべての jail がシステム起動時に起動します。
特定の jail だけを起動する場合は、名前を `jail_list` に列挙します。

```sh
# sysrc jail_list="www db"
```

名前は空白で区切り、`/etc/jail.conf` または `/etc/jail.conf.d/` 内で定義した jail 名と一致させます。
列挙した jail だけが指定順に起動し、含まれていない jail は手動で起動する必要があります。
`jail_list` が空の場合は、設定ファイルで定義されたすべての jail が起動します。

シャットダウン時に `jail_list` の逆順で停止させるには、次のように設定します。

```sh
# sysrc jail_reverse_stop="YES"
```

> **注:** `jail_parallel_start` が有効な場合、バックグラウンドで起動するため `jail_list` の順序は保証されません。
> ある jail より先に別の jail を起動する必要がある場合は、リスト順に頼らず `/etc/jail.conf` の `depend` パラメータで依存関係を指定してください。
> 依存する jail は `jail_list` にかかわらず先に作成され、停止時には逆順に停止します。
> `depend` については「[Jail 設定ファイル](#jail-configuration-files)」を参照してください。

<a id="jails-networking"></a>

### ネットワーク

FreeBSD jail のネットワークは、複数の方式で設定できます。

**ホストネットワークモード（IP 共有）**

jail は専用のネットワークスタックを持たず、ホストのスタックを共有します。
スタックを共有することと、IP アドレスを共有することは同じではありません。
一般的な構成では jail に専用の `ip4.addr`（必要なら `ip6.addr`）を割り当て、`jail(8)` がホストのインターフェイスにエイリアスとして追加します。
jail とホストは同じスタックを使いながら、別々のアドレスで応答します。
`ip4 = inherit` を指定した場合には、ホストの IPv4 アドレス全体を継承し、ホスト自身のアドレスで応答します。

**仮想ネットワーク（VNET）**

VNET は、基本的なホストネットワーク方式より高度で柔軟な構成を提供します。
jail ごとに独立したネットワークスタックを作成し、専用の IP アドレス、ルーティングテーブル、ネットワークインターフェイスを持たせます。
これによりネットワークの分離を強め、ネットワークに関しては別々の仮想マシンのように動作させることができます。

**netgraph システム**

`netgraph(4)` は、独自のネットワーク構成を作るための汎用的なカーネルフレームワークです。
jail とホストの間、および jail 同士の間でトラフィックがどう流れるかを定義できます。

<a id="jail-ip-comes-from"></a>

#### Jail の IP アドレスはどこから来るか

スタックを共有する jail は、ホストのインターフェイス上のアドレスを使ってネットワークに接続します。
`interface` は使用するインターフェイスを指定します。
`jail(8)` は、`ip4.addr` と `ip6.addr` に指定した各アドレスのエイリアスを jail の作成前に追加し、jail の削除後に取り除きます。
ホスト側であらかじめアドレスを設定しておく必要はありません。

アドレスごとにインターフェイスを指定することもできます。次の例では、アドレスと、それを割り当てるインターフェイスを1行で結び付けます。

```text
ip4.addr = "em0|192.168.1.151/24";
```

ホストの別のサービスがそのアドレスを使う場合や、`interface` を指定しない場合など、jail の存続と無関係にアドレスを維持する必要がある場合は、ホストの `rc.conf` にエイリアスを設定し、`jail(8)` による管理の対象から外します。

```sh
# sysrc ifconfig_em0_aliases="inet 192.168.1.151/32"
```

古い番号付き形式の `ifconfig_em0_alias0="inet 192.168.1.151/32"` も引き続き動作しますが、新しい設定では `_aliases` 形式が推奨されます。
番号付き形式では `alias0`、`alias1`、`alias2` という切れ目のない連番が必要ですが、`_aliases` 形式ならその制約を避けられます。

<a id="loopback-addresses-shared-ip-Jails"></a>
#### 共有 IP Jail におけるループバックアドレス

共有スタック jail には、専用のループバックインターフェイスがありません。
FreeBSD カーネルはこれを補います。非 VNET jail では、`127.0.0.1` または `::1` がその jail 自身のアドレスのいずれでもない場合、カーネルはループバックアドレスに対する `bind()` と `connect()` の両方を、その jail の最初の `ip4.addr` または `ip6.addr` に静かに書き換えます。
この動作は `jail(8)` には文書化されていませんが、セキュリティ上の影響を伴うため重要です。

> **警告:** サービスを `localhost` にバインドすれば jail 内に閉じ込められると考えてはなりません。
共有 IP jail では、`127.0.0.1` で待ち受けるよう指示されたデーモンは、実際には jail の最初のアドレスにバインドされます。これは多くの場合 LAN 側に面したアドレスであり、したがってネットワークから到達可能になります。

標準的な対策は、jail にプライベートなループバックアドレスを割り当て、それを先頭にリストすることです。
ホスト上に専用のループバックインターフェイスをクローン作成し、`127.0.0.0/8` の範囲（またはプライベートな RFC 1918 アドレス）のアドレスを割り当てます。

```sh
# sysrc cloned_interfaces="lo1"
# sysrc ifconfig_lo1="inet 127.0.1.1/32"
```

次に、そのアドレスを jail の `ip4.addr` の先頭に、ルーティング可能なアドレスより前にリストします。これにより、ループバックのリマップが LAN 側のアドレスではなくプライベートアドレスに着地します。

<a id="preparing-host-services"></a>
#### ホストサービスの準備

各 jail エイリアスアドレスはホストのポートを共有します。
ワイルドカードアドレスにバインドされたホストデーモン（リスナー一覧では `*:port` と表示されます）は、すべての jail エイリアスでも待ち受けることになり、jail 自身のサービスがそのポートを要求する前にポートを占有してしまいます。
jail を起動する前に、ホストが現在何を待ち受けているかを監査してください。

```sh
# sockstat -4 -6 -l
```

ワイルドカードアドレスにバインドする各デーモンを、ホスト自身のアドレスだけを使用し、jail のアドレスを解放したままにするように制限します。

* `syslogd(8)`: `/etc/rc.conf` で `syslogd_flags="-ss"` を設定します。
`-s` が 1 つの場合、syslogd はセキュアモードで実行され、リモートのログメッセージを待ち受けません。syslogd(8) によれば、`-s` が「2 回指定された場合、ネットワークソケットはまったく開かれません」。これにより、syslogd がリモートホストへの送信も停止します。
* `sshd(8)`: `/etc/ssh/sshd_config` の `ListenAddress` をデフォルトのワイルドカードのままにせず、ホストのアドレスに固定します。
* `ntpd(8)` と `sendmail(8)`: それぞれの設定を通じて、ホスト自身のアドレスだけにバインドするよう設定します。

jail が使用できるアドレスをファイアウォールレベルで制御するには、[英語 Handbook の「Firewalls」章](https://docs.freebsd.org/en/books/handbook/firewalls/) を参照してください。

<a id="host-configuration-directories"></a>
### Jail ディレクトリツリーのセットアップ

jail のファイルを置く場所に特別な決まりはありません。管理者によって `/jail`、`/usr/jail`、`/usr/local/jails` などが使われます。この章では `/usr/local/jails` を使用します。

その下に、次のディレクトリを作成します。

- `media`: ダウンロードしたユーザーランドの圧縮ファイル。
- `templates`: Thin Jail 用のテンプレート。
- `containers`: jail 本体。

OpenZFS を使用する場合は、次のコマンドでデータセットを作成します。
```shell
# zfs create -o mountpoint=/usr/local/jails zroot/jails
# zfs create zroot/jails/media
# zfs create zroot/jails/templates
# zfs create zroot/jails/containers
```


> **ヒント:** この例では親データセットに `zroot` を使用していますが、別のデータセットも使用できます。

jail ごとに個別の子データセットを作成すると、jail 単位のスナップショット、クローン、クォータ、データセット委任が可能になります。各 jail ディレクトリが独自のデータセットになるため、OpenZFS の `quota` と `reservation` プロパティでディスク使用量の上限と予約容量を設定できます。[Jail リソース制限](#jail-resource-limits)を参照してください。

UFS を使用する場合は、次のコマンドでディレクトリを作成します。
```shell
# mkdir /usr/local/jails/
# mkdir /usr/local/jails/media
# mkdir /usr/local/jails/templates
# mkdir /usr/local/jails/containers
```

<a id="jail-configuration-files"></a>
### Jail 設定ファイル

jail の設定方法は 2 つあります。`/etc/jail.conf` に jail ごとのエントリを追加する方法と、`/etc/jail.conf.d/` に jail ごとのファイルを作成する方法です。

ホスト上の jail が少数であれば、`/etc/jail.conf` に各エントリを追加できます。多数の場合は、`/etc/jail.conf.d/` に jail ごとに 1 ファイルを置く方法が適しています。

`/etc/jail.conf.d/` 内のファイルには `.conf` 拡張子を付け、`/etc/jail.conf` から次のように読み込みます。
```text
.include "/etc/jail.conf.d/*.conf";
```


典型的な jail のエントリは次のようになります。
```text
jailname {
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc";
  exec.stop = "/bin/sh /etc/rc.shutdown";
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;

  # HOSTNAME/PATH
  host.hostname = "${name}";
  path = "/usr/local/jails/containers/${name}";

  # NETWORK
  ip4.addr = 192.168.1.151;
  ip6.addr = "2001:db8::151";
  interface = em0;
}
```


- `jailname`: jail の名前。
- `exec.start`: jail 作成時に jail 内で実行するコマンド。通常は `/bin/sh /etc/rc` です。
- `exec.stop`: jail 削除前に jail 内で実行するコマンド。通常は `/bin/sh /etc/rc.shutdown` です。
- `exec.consolelog`: コマンドの標準出力と標準エラー出力を書き込むファイル。
- `allow.raw_sockets`: jail 内での raw ソケット作成を許可します。これにより `ping(8)` や `traceroute(8)` などを利用できます。
- `exec.clean`: クリーンな環境でコマンドを実行します。
- `mount.devfs`: jail 内から見えるデバイスを制限するため、chroot 先の `/dev` に `devfs(5)` をマウントします。`devfs_ruleset` で指定したルールセットを適用します。このパラメータがデフォルトの `0` の場合は、`mount.devfs` の既定のルールセット 4（`devfsrules_jail`）を使用し、jail 向けの最小限のデバイス以外を隠します。[Devfs ルールセット](#jail-conf-devfs)を参照してください。
- `host.hostname`: jail のホスト名。
- `path`: jail のルートとなるディレクトリ。jail 内で `jail` や `jexec(8)` によって実行されるコマンドは、このディレクトリをルートとして実行されます。
- `ip4.addr`: jail に割り当てる IPv4 アドレス 1 つ、またはカンマ区切りのアドレス一覧。指定すると `ip4 = new` が暗黙に設定されます。`ip4` は独立したデフォルト値のままにはなりません。`ip4` には、指定アドレスに制限する `new`、ホストのすべての IPv4 アドレスへの無制限なアクセスを許す `inherit`、IPv4 を無効にする `disable` を指定できます。`ip4` と `ip4.addr` のいずれも指定しない jail は `inherit` と同様に動作します。`inherit` では `interface` と `ip4.addr` は効果を持ちません。複数アドレスがある場合、`ip4.saddrsel` はバインドされていないソケットの外向き接続でカーネルによる送信元アドレス選択を許可し、`ip4.nosaddrsel` は一覧の先頭アドレスを強制します。
- `ip6.addr`: jail に割り当てる IPv6 アドレス 1 つ、またはカンマ区切りのアドレス一覧。`ip6` も `ip4` と同じく `new`、`inherit`、`disable` を取り、`ip6.saddrsel` と `ip6.nosaddrsel` で送信元アドレスの選択を制御します。IPv4 のみの jail では `ip6 = disable`、IPv6 のみの jail では `ip4 = disable` を使用します。
- `interface`: jail の IP アドレスを追加するネットワークインターフェース。通常はホストのインターフェースです。

> **注:** jail には仮想コンソールがありません。`init(8)` と `getty(8)` は jail 内で動作しないため、対話的に接続するコンソールはありません。`exec.consolelog` が記録するのは `exec.*` コマンドの標準出力と標準エラー出力、すなわち `/etc/rc` と `/etc/rc.shutdown` スクリプトの出力です。対話的な操作には [jail へのアクセス](https://docs.freebsd.org/en/books/handbook/jails/#access-jail)で説明する `jexec(8)`、または jail 内で動作させた `sshd(8)` を使います。jail 内のデーモンがその後に出力するログは、jail 自身の syslog に送られます。

> **ヒント:** `exec.consolelog` のファイルは制限なく増大します。`newsyslog(8)` でローテーションするため、たとえば `/etc/newsyslog.conf.d/jail` に次の glob エントリを追加します。
```text
/var/log/jail_console_*.log            640  7     100  *     J
```

<a id="global-settings-wildcards-variables"></a>
#### 共通設定、ワイルドカード、変数

jail ブロックの外に設定したパラメータは、ワイルドカードのデフォルト値になります。`jail.conf(5)` は、`*` ワイルドカード節に書いた場合と同様に、すべての jail に適用します。共通パラメータを一度だけ設定することで、各 jail のブロックを短くできます。

ドル記号を前置した名前（必要に応じて波括弧で囲む）は、対応するパラメータや変数の値に置き換えられます。組み込みの `${name}` は jail 自身の名前に展開されます。独自の変数は、名前の先頭にドル記号を付け、パラメータと同じように定義します。

次の `/etc/jail.conf` は共通設定を先頭に一度だけ定義し、jail ごとに異なる値だけを上書きします。
```text
# Shared defaults applied to every jail
exec.start = "/bin/sh /etc/rc";
exec.stop = "/bin/sh /etc/rc.shutdown";
exec.consolelog = "/var/log/jail_console_${name}.log";
exec.clean;
mount.devfs;
host.hostname = "${name}";
path = "/usr/local/jails/containers/${name}";
interface = em0;

www {
    ip4.addr = 192.168.1.151;
}

db {
    host.hostname = "database.example.com";
    ip4.addr = 192.168.1.152;
}
```


`www` は共通設定をすべて継承してアドレスだけを設定し、`db` はさらに `host.hostname` も上書きします。

<a id="jail-conf-hooks"></a>
#### コマンドフック

`jail(8)` は一連のライフサイクルフックを通じて jail を管理します。各フックがホスト側と jail 内のどちらで実行されるかを区別することが重要です。作成時の実行順序は次のとおりです。

| フック | 実行場所とタイミング |
|---|---|
| `exec.prestart` | ホスト側で、jail を作成する前に実行。 |
| `exec.created` | ホスト側で、jail が作成された後、jail 内でプロセスが起動する前に実行。 |
| `exec.start` | jail 内で実行。通常は `/bin/sh /etc/rc` でサービスを起動。 |
| `exec.poststart` | ホスト側で、jail が起動した後に実行。 |

停止時は逆の流れになります。

| フック | 実行場所とタイミング |
|---|---|
| `exec.prestop` | ホスト側で、jail を停止する前に実行。 |
| `exec.stop` | jail 内で実行。通常は `/bin/sh /etc/rc.shutdown`。 |
| `exec.poststop` | ホスト側で、jail が停止した後に実行し、`exec.prestart` で準備したものを片付ける。 |

`+=` を使って追加すると、1 つのフックに複数のコマンドを割り当てられます。
```text
exec.poststart += "logger jail ${name} started";
```


`exec.timeout` は `jail(8)` がコマンドの終了を待つ時間に上限を設け、`exec.consolelog` はこれらのコマンドの出力を記録します。[VNET Jail](#creating-vnet-jail)では、`exec.prestart` と `exec.poststop` を使い、ホスト上で各 jail のネットワーク接続を構築・撤去します。

フックが単一 jail 内のコマンドの順序を制御するのに対し、`depend` パラメータは jail 間の順序を制御します。`depend = otherjail;` と書くと、`jail(8)` はこの jail が `otherjail` に依存すると判断します。依存先を先に作成し、その最後の `exec.poststart` コマンドが完了してから、この jail を作成します。停止・削除は逆順で行われます。

<a id="jail-conf-devfs"></a>
#### Devfs ルールセット

`mount.devfs` を設定した jail では、`/dev` に表示するデバイスノードを devfs ルールセットで制御します。`devfs_ruleset` の指定があればその値を、指定がなければ `mount.devfs` のデフォルトであるルールセット 4 を使います。

`devfs.rules(5)` の名前付きルールセットは `/etc/defaults/devfs.rules` に定義されています。jail 向けのものは 2 つあります。ルールセット 4 の `devfsrules_jail` は jail 用の標準的な最小デバイス集合です。ルールセット 5 の `devfsrules_jail_vnet` は、VNET jail が独自のファイアウォールを動かせるよう `/dev/pf` を追加します。VNET jail の例は `devfs_ruleset = 5`、Linux jail の例は `devfs_ruleset = 4` を指定します。クラシック jail と Thin Jail の例は `mount.devfs` のみを設定するため、デフォルトのルールセット 4 を使います。

追加のデバイスを公開するには、標準ルールセットを取り込み、必要なデバイスを表示する独自ルールセットを `/etc/devfs.rules` に記述します。次の例は `devfsrules_jail` を基に、`bpf(4)` デバイスも表示します。
```text
[devfsrules_jail_bpf=100]
add include $devfsrules_jail
add path 'bpf*' unhide
```


ルールを再読み込みします。
```shell
# service devfs restart
```


続いて jail の設定で、新しいルールセットを番号で指定します。
```text
devfs_ruleset = 100;
```


`/etc/devfs.rules` にあるルールセットは、同じ番号の `/etc/defaults/devfs.rules` のルールセットを上書きします。それ以外は、両ファイルのルールセットが統合されます。

設定変数の詳細は `jail(8)` と `jail.conf(5)` を参照してください。

<a id="classic-jail"></a>
## クラシック Jail（Thick Jail）

これらの jail は通常の FreeBSD システムに似ており、ホストとほぼ同様に管理し、個別に更新できます。

<a id="creating-classic-jail"></a>
### クラシック Jail の作成

原則として jail に必要なのは、ホスト名、ルートディレクトリ、IP アドレス、ユーザーランドです。ユーザーランドは FreeBSD の公式ダウンロードサーバーから取得できます。

次のコマンドでダウンロードします。

```shell
# fetch https://download.freebsd.org/releases/amd64/amd64/{rel-latest}-RELEASE/base.txz -o /usr/local/jails/media/{rel-latest}-RELEASE-base.txz
```

取得したファイルを jail のディレクトリに展開します。

```shell
# mkdir -p /usr/local/jails/containers/classic
# tar -xf /usr/local/jails/media/{rel-latest}-RELEASE-base.txz -C /usr/local/jails/containers/classic --unlink
```

タイムゾーンと DNS サーバーの設定ファイルをコピーします。

```shell
# cp /etc/resolv.conf /usr/local/jails/containers/classic/etc/resolv.conf
# cp /etc/localtime /usr/local/jails/containers/classic/etc/localtime
```

最新のパッチレベルに更新します。

```shell
# freebsd-update -b /usr/local/jails/containers/classic/ fetch install
```

最後に、`/etc/jail.conf` または `/etc/jail.conf.d/` 内のファイルに jail のパラメータを追加します。

```text
classic {
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc";
  exec.stop = "/bin/sh /etc/rc.shutdown";
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;

  # HOSTNAME/PATH
  host.hostname = "${name}";
  path = "/usr/local/jails/containers/${name}";

  # NETWORK
  ip4.addr = 192.168.1.151;
  interface = em0;
}
```

次のコマンドで起動します。

```shell
# service jail start classic
```

操作方法の詳細は [Jail の管理](#jail-management)を参照してください。

<a id="creating-jail-userland"></a>
### Jail ユーザーランドの取得

上のダウンロードと展開は、ルートディレクトリを準備する従来の方法です。同じユーザーランドを `bsdinstall(8)`、ベースシステムのパッケージ、ローカルでビルドしたソースツリーからインストールすることもできます。

`bsdinstall(8)` の `jail` ターゲットは、指定ディレクトリに `jail(8)` 用ユーザーランドを構築します。カーネルをインストールせず配布セットを取得・展開し、通常のインストールにあるディスク分割やネットワーク設定を省くため、手動の fetch と `tar(1)` の代わりに、1 コマンドでスクリプト化できます。

```shell
# bsdinstall jail /usr/local/jails/containers/classic
```

`jail` ターゲットはデフォルトで `base.txz` をインストールします。FreeBSD 15.0 以降では `pkgbase` ターゲットでベースシステムのパッケージから構築することもできます。

FreeBSD 15.0 からはベースシステムもパッケージとして公開されているため、`FreeBSD-base` リポジトリから `pkg(8)` でユーザーランド全体をインストールできます。グローバルオプション `--rootdir` で jail のルートを指定し、ベースセットの jail 向けバリアントをインストールします。

```shell
# pkg --rootdir /usr/local/jails/containers/classic install -r FreeBSD-base FreeBSD-set-base-jail
```

最小構成には `FreeBSD-set-base-jail` の代わりに `FreeBSD-set-minimal-jail` を使用します。この方法で作成した jail は、その後も `freebsd-update(8)` ではなく `pkg(8)` で更新します。[pkgbase Jail のアップグレード](#jail-upgrade-pkgbase)を参照してください。

> **注（保存済み原文の説明）:** FreeBSD 15.0 のベースシステムパッケージはテクノロジープレビューです。`FreeBSD-base` は `/etc/pkg/FreeBSD.conf` に定義されていますが、デフォルトでは無効のため `install -r FreeBSD-base` で明示的に選択します。対象ルートと、その下の `var/cache/pkg`、`var/db/pkg` を先に作成する必要がある場合があります。15.0 でも `base.txz` は引き続き公開され、従来のダウンロード・展開方式を利用できます。

ソースからビルドしたユーザーランドは、`DESTDIR` を指定して jail のルートへインストールできます。`-STABLE` や独自ビルドを jail で使うための方法です。

```shell
# cd /usr/src
# make buildworld
# make installworld DESTDIR=/usr/local/jails/containers/classic
# make distribution DESTDIR=/usr/local/jails/containers/classic
```

`make distribution` は jail の `/etc` にデフォルト設定を入れるため、初期構築時に一度だけ実行します。更新時に繰り返すと jail 内の設定を上書きします。ソースから更新する場合はホストと同じ順序で、同じ `DESTDIR` を指定した `installworld`、jail のルートを指定した `etcupdate -D` による設定のマージ、同じ `DESTDIR` での `make delete-old delete-old-libs` による古いファイル・ライブラリの削除を行います。`freebsd-update(8)` は使いません。全手順は[ソースからの FreeBSD の更新](https://docs.freebsd.org/en/books/handbook/cutting-edge/#makeworld)を参照してください。

<a id="classic-jail-clone"></a>
### Jail をテンプレートとして複製する

パッケージをインストールし、サービスとローカル設定を整えた Thick Jail は、同一構成の jail を素早く展開するテンプレートイメージとして利用できます。

OpenZFS では設定済み jail のデータセットのスナップショットからクローンを作ります。元の jail は独立したデータセット上に置く必要があるため、先ほどのクラシック jail 作成手順にある `mkdir` の代わりに `zfs create` を使って準備します。

```shell
# zfs create -p zroot/jails/containers/classic
```

整合性のあるイメージを作るため jail を停止し、スナップショットを作成して、新しい jail ごとにクローンを作ります。

```shell
# service jail stop classic
# zfs snapshot zroot/jails/containers/classic@template
# zfs clone zroot/jails/containers/classic@template zroot/jails/containers/web1
```

UFS ホストでは設定済み jail のディレクトリツリーをコピーします。

```shell
# cp -a /usr/local/jails/containers/classic /usr/local/jails/containers/web1
```

各複製には、固有の名前・パス・IP アドレスを持つ設定を `/etc/jail.conf` または `/etc/jail.conf.d/` に用意します。上の例は `path` と `host.hostname` を `${name}` から求めるため、ブロック名とアドレスだけを変更できます。

```text
web1 {
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc";
  exec.stop = "/bin/sh /etc/rc.shutdown";
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;

  # HOSTNAME/PATH
  host.hostname = "${name}";
  path = "/usr/local/jails/containers/${name}";

  # NETWORK
  ip4.addr = 192.168.1.152;
  interface = em0;
}
```

テンプレートイメージの複製は、読み取り専用ベースを実行時に共有する NullFS の [Thin Jail](#thin-jail)とは異なり、全体が書き込み可能で、[Jail のアップグレード](#jail-upgrading)のとおり個別に保守します。OpenZFS クローンは未変更ブロックをスナップショットと共有するコピーオンライトの複製として始まり、origin スナップショットへの依存を持ちます。`zfs promote` で依存関係を変更できます。完全に独立した複製や別プール・別ホストへの複製には `zfs clone` の代わりに `zfs send` と `zfs receive` のパイプを使います。

> **訳注:** 保存済み原文のこの節は Thin Jail を読み取り専用ベース共有として一括して説明していますが、[種類の説明](#thin-jails)にあるとおり、OpenZFS 方式の Thin Jail は独立したクローンです。テンプレートの更新が既存 jail に一括反映されるのは NullFS 方式です。[zfs-promote(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-promote.8.html) のとおり、`zfs promote` は origin との依存関係を逆転させる操作であり、データを物理的に独立コピーする操作ではありません。

<a id="thin-jail"></a>
## Thin Jail

Thin Jail は Thick Jail と同じ技術を使いますが、作成方法が異なります。OpenZFS スナップショットから作成する方式と、テンプレートを NullFS で共有する方式があります。前者はスナップショットから素早く作成でき、後者は共通テンプレートの更新で複数の jail を更新できる利点があります。

<a id="creating-thin-jail-openzfs-snapshots"></a>
### OpenZFS スナップショットを使用した Thin Jail の作成

FreeBSD と OpenZFS の統合により、スナップショットから Thin Jail を容易に作成できます。まず [Jail ディレクトリツリーのセットアップ](#host-configuration-directories)に従って保存先を準備します。

続いて新しい jail の作成元となるテンプレートを作ります。テンプレートは新規作成のためだけに利用し、変更されないベースから jail を作るためのものです。原文はこれを「読み取り専用」と表現しています。以下では、作成したスナップショットが不変の作成元になります。

テンプレート用データセットを作成します。

```shell
# zfs create -p zroot/jails/templates/{rel-latest}-RELEASE
```

ユーザーランドをダウンロードします。

```shell
# fetch https://download.freebsd.org/releases/amd64/amd64/{rel-latest}-RELEASE/base.txz -o /usr/local/jails/media/{rel-latest}-RELEASE-base.txz
```

テンプレートに展開します。

```shell
# tar -xf /usr/local/jails/media/{rel-latest}-RELEASE-base.txz -C /usr/local/jails/templates/{rel-latest}-RELEASE --unlink
```

タイムゾーンと DNS サーバーの設定をコピーします。

```shell
# cp /etc/resolv.conf /usr/local/jails/templates/{rel-latest}-RELEASE/etc/resolv.conf
# cp /etc/localtime /usr/local/jails/templates/{rel-latest}-RELEASE/etc/localtime
```

最新のパッチレベルに更新します。

```shell
# freebsd-update -b /usr/local/jails/templates/{rel-latest}-RELEASE/ fetch install
```

これでテンプレートの準備ができました。スナップショットを作成します。

```shell
# zfs snapshot zroot/jails/templates/{rel-latest}-RELEASE@base
```

スナップショットから、OpenZFS のクローン機能で必要な数の jail を作成できます。次は `thinjail` を作る例です。

```shell
# zfs clone zroot/jails/templates/{rel-latest}-RELEASE@base zroot/jails/containers/thinjail
```

最後に `/etc/jail.conf` または `/etc/jail.conf.d/` のファイルへ設定を追加します。

```text
thinjail {
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc";
  exec.stop = "/bin/sh /etc/rc.shutdown";
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;

  # HOSTNAME/PATH
  host.hostname = "${name}";
  path = "/usr/local/jails/containers/${name}";

  # NETWORK
  ip4 = inherit;
  interface = em0;
}
```

> **訳注:** 原文例の `ip4 = inherit` は、ホストのすべての IPv4 アドレスへのアクセスを許可します。このモードでは `interface` によって特定のアドレスに制限されません。固有の IP に制限する構成は [Jail 設定ファイル](#jail-configuration-files)を参照してください。

起動します。

```shell
# service jail start thinjail
```

管理方法は [Jail の管理](#jail-management)を参照してください。既存クローンへテンプレートの更新は伝播しません。

<a id="creating-thin-jail-nullfs"></a>
### NullFS を使用した Thin Jail の作成

NullFS を使ってホスト上の特定ディレクトリを jail に共有すると、システムファイルの重複を減らせます。

まず、テンプレートの保存先を作成します。OpenZFS の場合はデータセットを作ります。

```shell
# zfs create -p zroot/jails/templates/{rel-latest}-RELEASE-base
```

UFS の場合はディレクトリを作ります。

```shell
# mkdir /usr/local/jails/templates/{rel-latest}-RELEASE-base
```

ユーザーランドをダウンロードします。

```shell
# fetch https://download.freebsd.org/releases/amd64/amd64/{rel-latest}-RELEASE/base.txz -o /usr/local/jails/media/{rel-latest}-RELEASE-base.txz
```

取得後、テンプレートに展開します。

```shell
# tar -xf /usr/local/jails/media/{rel-latest}-RELEASE-base.txz -C /usr/local/jails/templates/{rel-latest}-RELEASE-base --unlink
```

タイムゾーンと DNS サーバーの設定をコピーします。

```shell
# cp /etc/resolv.conf /usr/local/jails/templates/{rel-latest}-RELEASE-base/etc/resolv.conf
# cp /etc/localtime /usr/local/jails/templates/{rel-latest}-RELEASE-base/etc/localtime
```

最新のパッチレベルに更新します。

```shell
# freebsd-update -b /usr/local/jails/templates/{rel-latest}-RELEASE-base/ fetch install
```

ベーステンプレートとは別に、jail ごとのローカルディレクトリを保持する `skeleton` を準備し、一部のディレクトリをテンプレートから移します。OpenZFS の場合は次のデータセットを作ります。

```shell
# zfs create -p zroot/jails/templates/{rel-latest}-RELEASE-skeleton
```

UFS の場合は次のディレクトリを作ります。

```shell
# mkdir /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton
```

`skeleton` のディレクトリを作り、jail 固有の書き込み可能な部分を移動します。

```shell
# mkdir -p /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/home
# mkdir -p /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/usr
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/etc /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/etc
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/usr/local /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/usr/local
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/tmp /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/tmp
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/var /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/var
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/root /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/root
```

ベース側から `skeleton` を参照するシンボリックリンクを作成します。

```shell
# cd /usr/local/jails/templates/{rel-latest}-RELEASE-base/
# mkdir skeleton
# ln -s skeleton/etc etc
# ln -s skeleton/home home
# ln -s skeleton/root root
# ln -s ../skeleton/usr/local usr/local
# ln -s skeleton/tmp tmp
# ln -s skeleton/var var
```

`skeleton` の準備ができたら、各 jail にコピーします。OpenZFS ではスナップショットとクローンで必要な数を作成できます。

```shell
# zfs snapshot zroot/jails/templates/{rel-latest}-RELEASE-skeleton@base
# zfs clone zroot/jails/templates/{rel-latest}-RELEASE-skeleton@base zroot/jails/containers/thinjail
```

UFS では `cp(1)` を使います。

```shell
# cp -R /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton /usr/local/jails/containers/thinjail
```

ベーステンプレートと skeleton をマウントする場所を作ります。

```shell
# mkdir -p /usr/local/jails/thinjail-nullfs-base
```

`/etc/jail.conf` または `/etc/jail.conf.d/` のファイルに次のエントリを追加します。

```text
thinjail {
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc";
  exec.stop = "/bin/sh /etc/rc.shutdown";
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;

  # HOSTNAME/PATH
  host.hostname = "${name}";
  path = "/usr/local/jails/${name}-nullfs-base";

  # NETWORK
  ip4.addr = 192.168.1.153;
  interface = em0;

  # MOUNT
  mount.fstab = "/usr/local/jails/${name}-nullfs-base.fstab";
}
```

`/usr/local/jails/thinjail-nullfs-base.fstab` を作成します。

```text
/usr/local/jails/templates/{rel-latest}-RELEASE-base  /usr/local/jails/thinjail-nullfs-base/ nullfs   ro          0 0
/usr/local/jails/containers/thinjail     /usr/local/jails/thinjail-nullfs-base/skeleton nullfs  rw  0 0
```

この fstab は `mount_nullfs(8)` によるベースと skeleton の見せ方を指定します。ベースは読み取り専用（`ro`）で、各 jail が共通のベースを共有します。jail ごとの skeleton は読み書き可能（`rw`）で、独自の `/etc`、`/var`、`/usr/local` などを保持します。

共通ベースを更新すると、それをマウントするすべての NullFS jail に反映されます。個別に更新する OpenZFS クローンとの違いです。

次のコマンドで起動します。

```shell
# service jail start thinjail
```

<a id="creating-vnet-jail"></a>
## VNET Jail の作成

VNET Jail は、インターフェース、IP アドレス、ルーティングテーブル、ファイアウォールルールを含む独自のネットワークスタックを持ちます。

まず `bridge(4)` を作成します。

```shell
# ifconfig bridge create
```

出力例です。

```text
bridge0
```

> **警告（保存済み原文の説明）:** ブリッジのメンバーであるインターフェースへの IP アドレス割り当ては非推奨です。ホストのアドレスは `em0` ではなく、下の rc.conf のとおり `bridge0` 自身に割り当てます。FreeBSD 15.0 ではアドレス付きインターフェースをブリッジに追加するとカーネル警告が出ます。`net.link.bridge.member_ifaddrs` をデフォルトの `1` から `0` にすると `EINVAL` で拒否します。原文の `bridge(4)` の説明では、16.0 でこの sysctl を削除し、メンバーへのアドレス設定を許可しなくなる予定とされています。

ブリッジに `em0` を接続し、両方を有効にします。

```shell
# ifconfig bridge0 addm em0 up
# ifconfig em0 up
```

再起動後も保持するには `/etc/rc.conf` に次を追加します。

```text
defaultrouter="192.168.1.1"
cloned_interfaces="bridge0"
ifconfig_bridge0="inet 192.168.1.150/24 addm em0 up"
ifconfig_em0="up"
```

詳細は[ネットワークブリッジ](https://docs.freebsd.org/en/books/handbook/advanced-networking/#network-bridging)を参照してください。

次に [クラシック Jail](#classic-jail) または [Thin Jail](#thin-jail) の手順で jail を作成します。変わるのは `/etc/jail.conf` の設定です。ここではルートを `/usr/local/jails/containers/vnet` とします。

```text
vnet {
  # STARTUP/LOGGING
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;
  devfs_ruleset = 5;

  # PATH/HOSTNAME
  path = "/usr/local/jails/containers/${name}";
  host.hostname = "${name}";

  # VNET/VIMAGE
  vnet;
  vnet.interface = "${epair}b";

  # NETWORKS/INTERFACES
  $id = "154";
  $ip = "192.168.1.${id}/24";
  $gateway = "192.168.1.1";
  $bridge = "bridge0";
  $epair = "epair${id}";

  # ADD TO bridge INTERFACE
  exec.prestart  = "/sbin/ifconfig ${epair} create up";
  exec.prestart += "/sbin/ifconfig ${epair}a up descr jail:${name}";
  exec.prestart += "/sbin/ifconfig ${bridge} addm ${epair}a up";
  exec.start    += "/sbin/ifconfig ${epair}b ${ip} up";
  exec.start    += "/sbin/route add default ${gateway}";
  exec.start    += "/bin/sh /etc/rc";
  exec.stop      = "/bin/sh /etc/rc.shutdown";
  exec.poststop = "/sbin/ifconfig ${bridge} deletem ${epair}a";
  exec.poststop += "/sbin/ifconfig ${epair}a destroy";
}
```

- `$id` は、epair 名（`epair${id}`）と IP アドレスの末尾（`192.168.1.${id}`）の両方に使う、jail ごとの固有番号です。同じブリッジ上の各 jail で異なる値を使います。
- `$bridge` は先ほど作成したブリッジを指します。

`vnet.interface` は、jail 作成後に `jail(8)` が jail のスタックへ移すインターフェースを指定します。ここでは epair の jail 側 `${epair}b` です。jail の実行中はホスト側から消え、停止すると自動的にホストへ戻ります。物理 NIC や SR-IOV の仮想機能も同様に渡せるため、ブリッジや epair を使わない専用ネットワークも構成できます。

`devfs_ruleset = 5` は `/etc/defaults/devfs.rules` の `devfsrules_jail_vnet` を適用し、標準 jail 用ルールセットに `/dev/pf` を追加します。そのため jail 内の `pf_enable="YES"` と独自の `pf.conf` で、ホストとは独立した `pf(4)` を利用できます。[Devfs ルールセット](#jail-conf-devfs)と[ファイアウォール](https://docs.freebsd.org/en/books/handbook/firewalls/)を参照してください。

<a id="jail-vnet-jib"></a>
### jib による VNET ネットワークの自動化

多くの jail で `exec.prestart` と `exec.poststop` に epair の作成・ブリッジ接続を手書きするのは手間がかかります。ベースシステム付属の `/usr/share/examples/jails/jib` は、その処理を自動化するヘルパースクリプトです。

上の 5 行の手動 `ifconfig(8)` コマンドの代わりに、フックから次のように呼び出します。

```text
  exec.prestart += "jib addm ${name} em0";
  exec.poststop += "jib destroy ${name}";

  vnet.interface = "e0b_${name}";
```

`jib addm` は、ホスト側が `e0a_<name>`、jail 側が `e0b_<name>` の epair を作成し、ホスト側を自動作成したブリッジに追加します。ブリッジ名はメンバーインターフェースに由来し、`em0` なら `em0bridge` です。jail 側の名前を `vnet.interface` に指定します。停止時は `jib destroy` が epair を削除します。管理中のインターフェースは `jib show` で表示できます。

> **訳注:** 例はフック設定の抜粋です。`jib` を実行できるパスの準備、jail 内の IP・経路設定などは別途必要です。

<a id="jail-vnet-jng"></a>
### jng による Netgraph VNET ネットワーク

[ネットワーク](#jails-networking)で紹介した第 3 の方式は、`bridge(4)` と epair の代わりに `netgraph(4)` を使います。ベースシステムの `/usr/share/examples/jails/jng` は、jail ごとの `ng_eiface` を `ng_bridge` につなぐヘルパーです。

```text
  exec.prestart += "jng bridge ${name} em0";
  exec.poststop += "jng shutdown ${name}";

  vnet.interface = "ng0_${name}";
```

`jng bridge` は netgraph ノードと jail 側の `ng0_<name>` を作成します。この名前を `vnet.interface` に指定します。停止時に `jng shutdown` が構成を撤去します。機能は epair とブリッジの構成に相当しますが、`bridge(4)` ではなく netgraph ノードで実現します。

<a id="jail-vnet-firewall"></a>
### VNET Jail 内でのファイアウォールと DHCP

`devfs_ruleset = 5` は `/dev/pf` を公開するため、VNET jail は独自のファイアウォールを実行できます。通常のホストと同様に jail 内の `/etc/rc.conf` に `pf_enable="YES"` を設定し、独自の `/etc/pf.conf` を用意します。

ただし、ルールセット 5 は `/dev/bpf` を公開しません。たとえば jail 内の rc.conf に `ifconfig_e0b_myjail="SYNCDHCP"` を設定すると、DHCP クライアント `dhclient(8)` は bpf を必要とするため、そのままでは失敗します。[Devfs ルールセット](#jail-conf-devfs)に従い、ホストの `/etc/devfs.rules` に `devfsrules_jail_vnet` を基に bpf を追加した独自ルールセットを作成します。

```text
[devfsrules_jail_vnet_dhcp=101]
add include $devfsrules_jail_vnet
add path 'bpf*' unhide
```

ホストで `service devfs restart` を実行した後、jail に `devfs_ruleset = 101;` を指定します。

<a id="creating-linux-jail"></a>
## Linux Jail の作成

FreeBSD は [Linux バイナリ互換機能](https://docs.freebsd.org/en/books/handbook/linuxemu/)と `sysutils/debootstrap` を使い、jail 内で Linux ユーザーランドを実行できます。jail は独自のカーネルを持たず、ホストのカーネルを使うため、ホスト側で Linux バイナリ互換機能を有効にする必要があります。

起動時に Linux ABI を有効にします。

```shell
# sysrc linux_enable="YES"
```

再起動せずに開始するには次を実行します。

```shell
# service linux start
```

続いて、たとえば [OpenZFS スナップショットからの Thin Jail](#creating-thin-jail-openzfs-snapshots)の手順で jail を作ります。ただし通常の設定は行わず、以下の Linux 用設定を使います。

コマンドラインだけで jail を作ってきたホストなど、`/etc/jail.conf` が存在しない場合は、後で `service(8)` による停止ができるよう空のファイルを作ります。

```shell
# touch /etc/jail.conf
```

jail の rc スクリプトは停止時に `/etc/jail.conf` を読むため、存在しないと停止コマンドが失敗します。既にある場合はこの作業は不要です。

次のコマンドは、jail.conf のエントリを使わずに設定と起動を行います。`-c` は作成、`-m` は既存 jail の変更です。`-cm` は、なければ作成し、あれば更新します。

```shell
# jail -cm \
    name=ubuntu \
    host.hostname="ubuntu.example.com" \
    path="/usr/local/jails/containers/ubuntu" \
    interface="em0" \
    ip4.addr="192.168.1.155" \
    exec.start="/bin/sh /etc/rc" \
    exec.stop="/bin/sh /etc/rc.shutdown" \
    mount.devfs \
    devfs_ruleset=4 \
    allow.mount \
    allow.mount.devfs \
    allow.mount.fdescfs \
    allow.mount.procfs \
    allow.mount.linprocfs \
    allow.mount.linsysfs \
    allow.mount.tmpfs \
    enforce_statfs=1
```

作成した jail に root で入ります。

```shell
# jexec -u root ubuntu sh
```

ここからは jail 内で `sysutils/debootstrap` をインストールし、`/compat/ubuntu` に Ubuntu ユーザーランドを構築します。debootstrap は構築用ツールであり、以後 jail に入るために必要なものではありません。`pkg(7)` は初回実行時に自動でブートストラップされます。

```shell
# pkg install debootstrap
# debootstrap jammy /compat/ubuntu
```

`jammy` は Ubuntu 22.04 LTS を選びます。linuxulator 上で動くことを確認できれば、`noble`（24.04）などの新しい LTS を選ぶこともできます。

`Base system installed successfully` と表示されたら、ホストに戻って jail を停止します。まだ rc.conf で有効化されておらず jail.conf にも登録されていないため、有効化されていなくても動作する `one` 接頭辞付きの操作を使います。

```shell
# service jail onestop ubuntu
```

`onestart` と `onestop` は、`jail_enable` で有効化されていない jail や `jail_list` にない jail を扱うための `start`、`stop` に相当する操作です。

次に Linux jail のエントリを `/etc/jail.conf` へ追加します。

```text
ubuntu {
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc";
  exec.stop = "/bin/sh /etc/rc.shutdown";
  exec.consolelog = "/var/log/jail_console_${name}.log";

  # PERMISSIONS
  allow.raw_sockets;
  exec.clean;
  mount.devfs;
  devfs_ruleset = 4;

  # HOSTNAME/PATH
  host.hostname = "${name}";
  path = "/usr/local/jails/containers/${name}";

  # NETWORK
  ip4.addr = 192.168.1.155;
  interface = em0;

  # MOUNT
  mount += "devfs     $path/compat/ubuntu/dev     devfs     rw  0 0";
  mount += "tmpfs     $path/compat/ubuntu/dev/shm tmpfs     rw,size=1g,mode=1777  0 0";
  mount += "fdescfs   $path/compat/ubuntu/dev/fd  fdescfs   rw,linrdlnk 0 0";
  mount += "linprocfs $path/compat/ubuntu/proc    linprocfs rw  0 0";
  mount += "linsysfs  $path/compat/ubuntu/sys     linsysfs  rw  0 0";
  mount += "/tmp      $path/compat/ubuntu/tmp     nullfs    rw  0 0";
  mount += "/home     $path/compat/ubuntu/home    nullfs    rw  0 0";
}
```

> **ヒント:** jail 内の Linux プログラムに、独自の Linux カーネル識別情報を提示できます。`linux` はホストの Linux エミュレーション環境を継承する `inherit` と独自環境の `new` を選び、`linux.osname`、`linux.osrelease`、`linux.oss_version` は OS 名・リリース・OSS バージョンを指定します。たとえば `linux.osrelease=6.1.0` は、ホスト全体の `compat.linux.osrelease` の代わりに、その値を `uname(1)` やバージョン検査を行う Linux プログラムに報告します。

通常の方法で起動します。

```shell
# service jail start ubuntu
```

Ubuntu 環境へ入ります。

```shell
# jexec ubuntu chroot /compat/ubuntu /bin/bash
```

詳細は [Linux バイナリ互換機能](https://docs.freebsd.org/en/books/handbook/linuxemu/)を参照してください。

<a id="jail-nat"></a>
## Jail の NAT とポート転送

`lo1` など複製した `lo(4)`、プライベートブリッジ、内部ネットワーク上の VNET epair にプライベートアドレスを割り当てた jail は、それだけではインターネットに到達できません。ホストが通信を経路制御可能なアドレスへ変換し、外からサービスへ接続するには受信接続を jail へ転送します。

ホストでインターフェース間のパケット転送を有効にします。起動時と現在の両方に反映するには次を実行します。

```shell
# sysrc gateway_enable="YES"
# sysctl net.inet.ip.forwarding=1
```

IPv6 では `ipv6_gateway_enable="YES"` と `net.inet6.ip6.forwarding=1` を使います。

続いてホストの `pf(4)` で NAT を設定します。次の `/etc/pf.conf` は、`192.168.0.0/24` の jail から外部インターフェース `em0` 経由で通信できるようにし、ホストの TCP ポート 80 を jail 内の Web サーバーへ転送します。

```text
ext_if = "em0"

# Translate outbound jail traffic to the host address
nat on $ext_if from 192.168.0.0/24 to any -> ($ext_if)

# Forward inbound web traffic to the jailed server
rdr on $ext_if proto tcp to port 80 -> 192.168.0.151
```

`rdr` の転送先には jail 自身のアドレスを指定します。

pf を有効にして起動します。

```shell
# sysrc pf_enable="YES"
# service pf start
```

> **注（保存済み原文の説明）:** FreeBSD 15.0 では OpenBSD 形式のインライン `nat-to` と `rdr-to` 構文が追加され、`pass` や `match` ルールに変換を記述できます。例は `match out on $ext_if from 192.168.0.0/24 to any nat-to ($ext_if)` です。上の従来形式 `nat on`、`rdr on` は 14.x と 15.x の両方で利用できます。

完全なルールセットや `ipfw(8)` による NAT を含む説明は[ファイアウォール](https://docs.freebsd.org/en/books/handbook/firewalls/)を参照してください。

<a id="service-jails-config"></a>
## Service Jail の設定

Service Jail は FreeBSD 15.0 以降で利用でき、設定は `/etc/rc.conf` または `sysrc(8)` だけで行います。ベースシステムのサービスは Service Jail に対応しており、必要なネットワークや制限解除の設定を持ちます。起動・停止時にマウントを操作するもの、経路やファイアウォールだけを設定するものなど、jail 内で動かす意味がないサービスは、rc.conf で有効にしても Service Jail として起動しないよう構成されています。

サードパーティーのサービスは対応しているとは限りません。次のコマンドで確認できます。

```shell
# grep _svcj_options /path/to/rc.d/servicename
```

出力がなければ、非対応か、ネットワークなどの追加権限が不要なサービスです。

非対応のサービスがネットワークを必要とする場合は、rc.conf に必要な設定を追加します。

```shell
# sysrc servicename_svcj_options=net_basic
```

利用できる `_svcj_options` は `rc.conf(5)` を参照してください。

特定サービスを jail 化するには、まず停止してから `servicename_svcj` を `YES` にします。`syslogd(8)` の例です。

```shell
# service syslogd stop
# sysrc syslogd_svcj=YES
# service syslogd start
```

`servicename_svcj` を変更する前に、必ずサービスを停止します。停止せずに変更すると rc フレームワークが状態を正しく判断できず、要求した操作に失敗します。

Service Jail は `rc.conf(5)`／`sysrc(8)` と `service(8)` だけで管理します。[Jail の管理](#jail-management)の `jls(8)` などは動作の調査に利用できますが、管理に `jail(8)` を直接使うことは想定されていません。

<a id="jail-management"></a>
## Jail の管理

作成した jail には、起動・再起動・削除やソフトウェアのインストールなどを行えます。この節ではホスト側からの操作を説明します。

<a id="list-running-jails"></a>
### 実行中の jail の一覧

ホスト上で実行中の jail は `jls(8)` で一覧表示できます。

```shell
# jls
```

出力例です。

```text
   JID  IP Address      Hostname                      Path
     1  192.168.1.151  classic                       /usr/local/jails/containers/classic
```

`jls(8)` は `--libxo` に対応し、`libxo(3)` を通じて JSON や HTML などでも出力できます。JSON の例です。

```shell
# jls --libxo=json
```

出力例です。

```text
{"__version": "2", "jail-information": {"jail": [{"jid":1,"ipv4":"192.168.1.151","hostname":"classic","path":"/usr/local/jails/containers/classic"}]}}
```

デフォルトの一覧は取得できる情報の一部です。`-v` は状態や cpuset ID を含む複数行の詳細を表示します。

```shell
# jls -v
```

`-h` は指定したパラメータの値の上に、フィールド名のヘッダーを表示します。

```shell
# jls -h jid name path
```

`-j` に名前を指定すると、単一 jail の指定パラメータを問い合わせられます。

```shell
# jls -j classic path host.hostname ip4.addr
```

出力例です。

```text
/usr/local/jails/containers/classic classic 192.168.1.151
```

通常は非表示になる停止処理中（dying 状態）の jail も含めるには `-d` を使います。

```shell
# jls -d
```

<a id="start-jail"></a>
### Jail の起動・再起動・停止

ホスト側で `service(8)` を使って jail を起動・再起動・停止します。

```shell
# service jail start jailname
```

`start` を `restart` または `stop` に置き換えると、対応する操作になります。

停止は単なるプロセスの強制終了ではありません。まず `jail(8)` は jail 内で `exec.stop`（通常は `/bin/sh /etc/rc.shutdown`）を実行し、サービスを正常に終了させます。その後、残ったプロセスに `SIGTERM` を送り、`stop.timeout` 秒（デフォルト 10 秒）待ちます。時間が過ぎると jail を削除し、残存プロセスを `SIGKILL` で終了します。

`stop.timeout` が `0` なら `SIGTERM` を送らず、直ちに jail を削除します。停止が遅いデーモンでは 10 秒間止まったように見えることがあります。データベースなど正常終了に時間が必要なサービスでは、`/etc/jail.conf` の `stop.timeout` を増やします。

<a id="destroy-jail"></a>
### Jail の破棄

jail の破棄は、停止してディレクトリと jail.conf のエントリを削除するだけとは限りません。FreeBSD のファイルフラグには root でも削除できないファイルを保護するものがあり、UFS 上の jail では削除前に解除する必要があります。

まず対象 jail を停止します。

```shell
# service jail stop classic
```

次に `chflags(1)` でフラグを解除します。`classic` は削除対象の名前です。

```shell
# chflags -R 0 /usr/local/jails/containers/classic
```

ディレクトリを削除します。

```shell
# rm -rf /usr/local/jails/containers/classic
```

以上のフラグ解除とディレクトリ削除は UFS 用です。[Jail ディレクトリツリー](#host-configuration-directories)のように jail が独立した ZFS データセットにある場合は、データセットを破棄します。データセット破棄はファイルフラグで妨げられないため、`chflags(1)` は不要です。

```shell
# service jail stop classic
# zfs destroy zroot/jails/containers/classic
```

そのデータセットのスナップショットも破棄する場合は `-r` を追加します。

> **注:** [Thin Jail](#thin-jail)として作った ZFS クローンは、元のテンプレートのスナップショットに依存します。クローンが残っている間は `zfs(8)` が元のスナップショットの破棄を拒否し、依存クローンを表示します。テンプレートを廃止するには、そこから作った jail をすべて破棄するか、クローンに `zfs promote` を実行して依存関係を変更します。[テンプレートとしての複製](#classic-jail-clone)の訳注も参照してください。

最後に `/etc/jail.conf` または `/etc/jail.conf.d/` からエントリを削除します。NullFS Thin Jail では、その `.fstab` と空になったマウント先ディレクトリも削除します。

<a id="handle-packages-jail"></a>
### Jail 内のパッケージ操作

`pkg(8)` は `-j` で jail 内のパッケージを操作できます。次は **ホスト側から** `www/nginx-lite` をインストールする例です。

```shell
# pkg -j classic install nginx-lite
```

詳細は[アプリケーションのインストール: Packages と Ports](https://docs.freebsd.org/en/books/handbook/ports/)を参照してください。

<a id="jail-services-host"></a>
### ホストから jail 内のサービスを管理する

`jexec(8)` で入らずに、ホストから jail 内のサービスを有効化・操作できます。`service(8)` と `sysrc(8)` は両方とも `-j` で jail の ID または名前を指定でき、その jail の `rc(8)` 設定を扱います。

先ほどの `classic` jail で nginx を有効化して起動する例です。

```shell
# sysrc -j classic nginx_enable=YES
# service -j classic nginx start
```

`jexec(8)` 経由で `sysrc(8)` や `service(8)` を実行するのと同じ効果ですが、ホスト側の管理やスクリプトを通常のシステムと同じ書き方にできます。

<a id="access-jail"></a>
### Jail に入る

基本的にはホストから管理するのが適していますが、`jexec(8)` で jail 内へ入ることもできます。ホストで次を実行します。

```shell
# jexec -u root jailname
```

`-u` は **ホスト側** のパスワードデータベースでユーザー名を解決します。**jail 内** のデータベースを使うには `-U` を指定します。例のようにコマンドを省略すると、そのユーザーのログインシェルを jail 内で開始します。

`-l` はクリーンなログイン環境にし、`HOME`、`SHELL`、`TERM`、`USER` だけを保持し、`PATH` を `/bin:/usr/bin` に設定します。`-d` は作業ディレクトリを指定し、デフォルトは jail のルートです。jail に入ると `motd(5)` で設定したメッセージが表示されます。

<a id="execute-commands-jail"></a>
### Jail 内でコマンドを実行する

ホストから jail 内のコマンドを実行するには `jexec(8)` を使います。次は jail 内の nginx を停止する例です。

```shell
# jexec -l jailname service nginx stop
```

<a id="jail-view-processes"></a>
### ホストから jail のプロセスとソケットを表示する

ホストは各 jail のプロセスとソケットを見ることができ、jail ごとに絞り込めます。`ps(1)` の `-J` に JID または名前を指定します。

```shell
# ps -J classic
```

出力例です。`STAT` の `J` は jail 内のプロセスを表します。

```text
 PID TT  STAT    TIME COMMAND
2841  -  IsJ  0:00.02 /usr/sbin/syslogd -ss
2903  -  IsJ  0:00.00 nginx: master process /usr/local/sbin/nginx
```

`ps -J 0` はホスト自身のプロセスだけを表示します。`-o` の出力形式に `jail` や `jid` を追加することもできます。全プロセスと所属 jail の一覧は次のとおりです。

```shell
# ps ax -o pid,jail,command
```

`top(1)` の `-J` は表示を指定 jail に絞り、`-j` も暗黙に指定して `JID` 列を追加します。

```shell
# top -J classic
```

`sockstat(1)` の `-j` は指定 jail のソケットを表示します。サービス起動後に、デーモンがどのポートで待ち受けているかを確認するのに適しています。

```shell
# sockstat -4 -6 -l -j classic
```

jail 内からは逆に、その jail 自身のプロセスとソケットだけが見え、ホストや他の jail のものは見えません。

<a id="jail-manage-cli"></a>
### jail ユーティリティによる直接管理

起動時の管理には通常 `service(8)` を使いますが、`jail(8)` で直接作成・変更・削除することもできます。スクリプトや rc を介さない設定の試験に便利です。

設定済み jail を名前で作成します。

```shell
# jail -c classic
```

実行中の jail を削除します。その jail が作成した子 jail も削除され、内部のプロセスも終了します。

```shell
# jail -r classic
```

`-m` は実行中の jail を再起動せずに変更します。IPv4 アドレスの追加例です。

```shell
# jail -m name=classic ip4.addr+=192.168.250.71
```

ただし、実行中に変更できないパラメータもあります。`path` や `vnet` などは再起動が必要です。

`-e` は作成・変更・削除を行わず、設定済みの非ワイルドカード jail とパラメータを表示します。引数はパラメータを区切る文字列であり、設定ファイルの確認に利用できます。

```shell
# jail -e ,
```

<a id="jail-backup"></a>
### Jail のバックアップと移行

jail はおおむね自己完結しているため、バックアップや別ホストへの移行は主にファイルと設定のコピーです。

整合性のあるコピーには先に jail を停止します。ZFS 上では稼働中のスナップショットも可能です。独立した ZFS データセット上の jail では、再帰スナップショットを取り、移行先へ送信します。

```shell
# service jail stop classic
# zfs snapshot -r zroot/jails/containers/classic@migrate
# zfs send -R zroot/jails/containers/classic@migrate | ssh newhost zfs receive zroot/jails/containers/classic
```

増分転送を含む `zfs-send(8)` と `zfs-receive(8)` の詳細は [ZFS のレプリケーション](https://docs.freebsd.org/en/books/handbook/zfs/#zfs-zfs-send)を参照してください。

UFS 上では、所有者・アクセス権・ファイルフラグを保持するため `tar(1)` の `-p` を使います。

```shell
# tar -cpf classic.tar -C /usr/local/jails/containers classic
```

移行先では root として `tar -xpf` で展開します。独立した UFS ファイルシステム全体を jail が占める場合は `dump(8)` と `restore(8)` も使えますが、ファイルシステム全体を扱うため、本章のように共有ファイルシステム内のディレクトリとして jail を置く構成には適用できません。

最後に jail.conf のブロックまたは jail.conf.d のファイルを移行先へコピーし、`interface`、`ip4.addr`、VNET のブリッジなどホスト固有の値を調整して起動します。

> **注意:** 移行先の FreeBSD は、jail のユーザーランドより古くできません。NullFS Thin Jail は自己完結しておらず、テンプレートと skeleton も移行するか、先に Thick Jail 相当のコピーへ変換します。`/etc/rctl.conf` に保存したルールも別途移行します。

> **訳注:** 稼働中のスナップショットだけではアプリケーションの整合性まで保証しません。必要な停止・静止化と、別データセットに置いたデータや設定のバックアップも考慮してください。

<a id="jail-inside"></a>
## Jail 内からの管理

管理の多くはホストから行いますが、jail 内で行う作業もあります。スクリプトが jail 内で動作しているかを知るには `security.jail.jailed` を読みます。jail 内は `1`、ホストは `0` です。

```shell
# sysctl security.jail.jailed
security.jail.jailed: 1
```

jail 内は意図的に制限されています。

- 見えるのは自身の jail のプロセス・ソケット・ファイルシステムで、ホストや他の jail のものは見えません。
- カーネルの状態は大部分が読み取り専用です。カーネル調整値の変更、`kldload(8)`、`kldunload(8)` は許可されません。`allow.read_msgbuf` がなければ `dmesg(8)` とカーネルメッセージバッファも利用できません。
- 境界を越える特権操作はホストが明示的に許可しない限り拒否されます。`ping(8)` や `traceroute(8)` の raw ソケットには `allow.raw_sockets`、マウントには `allow.mount` と種類別の子パラメータが必要です。`chflags(1)` もデフォルトでは制限されます。[Jail 設定ファイル](#jail-configuration-files)と[アップグレード](#jail-upgrading)を参照してください。

`kern.hostname`、`kern.domainname`、`kern.hostid`、`kern.hostuuid`、`kern.securelevel`、`security.bsd.suser_enabled` など、一部の jail 単位の sysctl はホストに影響せず jail 内で変更できます。利用可能な jail パラメータの説明は次で一覧できます。

```shell
# sysctl -d security.jail.param
```

jail 内のサービス管理は通常のシステムと同じです。`service(8)` と `sysrc(8)` は jail 自身の rc 設定を操作します。ホスト側の [service -j と sysrc -j](#jail-services-host)に対応する操作です。

<a id="jail-upgrading"></a>
## Jail のアップグレード

jail を更新することで、隔離環境のセキュリティを維持し、新しい機能や改善を利用できます。更新ツールはユーザーランドの導入方法で決まります。

- 配布セット（`base.txz` または `bsdinstall(8)` で導入）: FreeBSD 14.x と 15.x とも、ホストから `freebsd-update(8)` の `-j` で更新します。
- ベースパッケージ（FreeBSD 15.0 から利用可能）: `pkg(8)` で更新します。`freebsd-update(8)` は適用しません。
- ソースビルド: ソースからのインストール手順で更新します。同じ jail でこれらの方式を混在させません。

> **訳注:** 原文のこの箇所はソース更新に `make distribution` も列挙していますが、[ユーザーランドの取得](#creating-jail-userland)で説明するとおり、これは初期構築時だけの処理です。更新時には既存設定を保持し、`etcupdate -D` でマージします。

> **注（保存済み原文の説明）:** 配布セットのサポートは FreeBSD 16 で廃止予定ですが、15 の stable ブランチの存続期間は `freebsd-update(8)` とともに継続する予定です。15.0 のベースパッケージはテクノロジープレビューで、将来の標準方式になることが見込まれています。

OpenZFS では、更新前に jail のデータセットのスナップショットを作ると、失敗時に戻せます。

```shell
# zfs snapshot zroot/jails/containers/classic@preupgrade
```

失敗した場合は jail を停止して `zfs rollback zroot/jails/containers/classic@preupgrade` を実行します。jail が独立したデータセットである必要があります。OpenZFS Thin Jail のクローンは既に独立していますが、`mkdir` で作成したクラシック jail はそうではないため、初めから `zfs create` で用意します。NullFS Thin Jail ではテンプレートのデータセットをスナップショットにします。`zfs-rollback(8)` は通常最新のスナップショットにだけ戻れます。新しいスナップショットを破棄して古いものに戻すには `-r` が必要です。

<a id="jails-updating"></a>
### クラシック Jail／OpenZFS Thin Jail の更新

配布セットから導入した jail は **ホスト側から更新**します。FreeBSD は jail 内での `chflags(1)` をデフォルトで制限するため、一部ファイルを更新できず、内部からの更新は失敗します。

同一リリースの最新パッチへ更新するには、ホストで次を実行します。

```shell
# freebsd-update -j classic fetch install
# service jail restart classic
```

メジャー／マイナーバージョンを上げる場合は、先に[ホストのアップグレード](https://docs.freebsd.org/en/books/handbook/cutting-edge/#freebsdupdate-upgrade)と再起動を完了し、その後 jail を更新します。バージョン間の更新では、新しい jail を作る方が容易な場合もあります。

`classic` を `{rel-latest}-RELEASE` に上げる例です。実際の対象リリースへ置き換え、ホストで実行します。

```shell
# freebsd-update -j classic -r {rel-latest}-RELEASE upgrade
# freebsd-update -j classic install
# service jail restart classic
# freebsd-update -j classic install
# service jail restart classic
```

`install` を 2 回行うのは意図的です。jail はホストのカーネルを使うので、ここでカーネルを更新するわけではありません。最初の `install` で新しいユーザーランドを書き込み、再起動後の 2 回目で旧バージョンが使用中だったため置き換えられなかった部分を仕上げます。

メジャーバージョン間では ABI が変わるため、ホスト側からすべてのインストール済みパッケージを再インストールし、再起動します。

```shell
# pkg -j classic upgrade -f
# service jail restart classic
```

<a id="jail-upgrade-zfs-template"></a>
### OpenZFS Thin Jail の更新

[OpenZFS スナップショットから作った Thin Jail](#creating-thin-jail-openzfs-snapshots)は、作成後はテンプレートと独立しています。テンプレートを更新しても既存クローンは更新されず、クローンを更新してもテンプレートは変わりません。保守には 2 通りあります。

第 1 は、[クラシック Jail と同じ方法](#jails-updating)で各クローンを `freebsd-update(8)` により個別に更新する方法です。少数の jail には単純ですが、変更したブロックが各 jail に複製されるため共有による容量削減が減り、メジャー更新ではユーザーランドの大部分が書き換わります。

第 2 は、テンプレートを更新してクローンを作り直す方法です。まずホストでテンプレートにパッチを適用します。

```shell
# freebsd-update -b /usr/local/jails/templates/{rel-latest}-RELEASE/ fetch install
```

> **注:** `freebsd-update(8)` の `-b` はテンプレートではなくホストの `uname -r` から実行中リリースを判断します。テンプレートがホストより古い場合は `--currently-running <template-release>` を追加します。[NullFS Thin Jail の更新](#upgrading-thin-jail)も参照してください。

新しいスナップショットを作り、以後の jail をそこから複製します。

```shell
# zfs snapshot zroot/jails/templates/{rel-latest}-RELEASE@base-p2
# zfs clone zroot/jails/templates/{rel-latest}-RELEASE@base-p2 zroot/jails/containers/newjail
```

既存クローンは、新しいスナップショットから作り直すまで元のベースのままです。メジャー／マイナー更新では、既存テンプレートをその場で更新する代わりに、[作成手順](#creating-thin-jail-openzfs-snapshots)に沿って新リリース用データセットを作り、その `@base` から新しい jail を作成します。

アプリケーションのデータや設定を別データセットまたは jail 固有のストレージに分けて保持すると、更新済みテンプレートからの再作成が容易になり、すべてのクローンを個別に更新するより適した運用にできます。

<a id="upgrading-thin-jail"></a>
### NullFS Thin Jail の更新

NullFS Thin Jail はシステムディレクトリの大部分を共有するため、テンプレートの更新で複数の jail をまとめて更新できます。

同一リリースの最新パッチへ更新するには、ホストで次を実行します。

```shell
# freebsd-update -b /usr/local/jails/templates/{rel-latest}-RELEASE-base/ fetch install
# service jail restart
```

メジャー／マイナー更新では、先に[ホストの更新と再起動](https://docs.freebsd.org/en/books/handbook/cutting-edge/#freebsdupdate-upgrade)を済ませます。

その結果ホストがテンプレートより新しくなるため、`-b` だけではホストの `uname -r` の新しいバージョンで判定されます。jail 自身のユーザーランドを検出する `-j` とは異なります。テンプレートの実際のリリースを `--currently-running <template-release>` で指定します。

次は 14.2-RELEASE のテンプレートを 14.3-RELEASE に更新する原文例です。適用するリリースに置き換えてください。

```shell
# freebsd-update -b /usr/local/jails/templates/14.2-RELEASE-base/ --currently-running 14.2-RELEASE -r 14.3-RELEASE upgrade
# freebsd-update -b /usr/local/jails/templates/14.2-RELEASE-base/ install
# service jail restart
# freebsd-update -b /usr/local/jails/templates/14.2-RELEASE-base/ install
# service jail restart
```

<a id="jail-upgrade-pkgbase"></a>
### pkgbase Jail の更新

FreeBSD 15.0 以降でベースパッケージから導入した jail は、`freebsd-update(8)` ではなく `FreeBSD-base` に対する `pkg(8)` で更新します。

保存済み原文では、15.0 の `FreeBSD-base` は `/etc/pkg/FreeBSD.conf` に定義されているもののデフォルトで無効のため、更新前に有効化すると説明されています。

ホストから `-r`（`--rootdir`）でルートを指定します。

```shell
# pkg -r /usr/local/jails/containers/pkgjail update
# pkg -r /usr/local/jails/containers/pkgjail upgrade
# service jail restart pkgjail
```

jail 内から通常の `pkg upgrade` を実行する方法もあります。

```shell
# jexec -l pkgjail pkg upgrade
# service jail restart pkgjail
```

`pkg(8)` は `/etc` 内の設定ファイルとして識別されたファイルを 3 ウェイマージします。自動マージできない場合は新しい版を `<file>.pkgnew` に残し、それまでパッケージ管理されていなかったファイルを引き継ぐ場合は旧版を `<file>.pkgsave` に保存します。更新後に `/etc` を確認し、これらを手動で調整してください。

pkgbase では `pkg(8)` 自身が設定をマージするため、`etcupdate(8)` は実行しません。ホスト側の説明は [FreeBSD の更新とアップグレード](https://docs.freebsd.org/en/books/handbook/cutting-edge/)を参照してください。

<a id="jail-resource-limits"></a>
## Jail のリソース制限

管理者はホストから jail の資源使用量を制御できます。`rctl(8)` を使って設定します。`/boot/loader.conf` で `kern.racct.enable` を有効にしておく必要があります。

構文は次のとおりです。

```text
rctl -a jail:<jailname>:resource:action=amount[/per]
```

省略可能な `per` は割合ではなく、制限を集計する対象です。`process`、`user`、`loginclass`、`jail` のいずれかを指定します。`deny=2G/jail` は jail 全体の合計、`deny=2G/process` は各プロセスに個別に適用します。割合を使うのは `pcpu` で、単一 CPU コアに対する百分率です。

RAM 使用量を制限する例です。

```shell
# rctl -a jail:classic:memoryuse:deny=2G
```

ホスト再起動後も保持するには `/etc/rctl.conf` にルールを追加します。

```text
jail:classic:memoryuse:deny=2G/jail
```

メモリ以外にも、`pcpu`（単一コアに対する CPU 使用率）、`maxproc`（プロセス数）、`openfiles`（開いたファイル記述子数）、`vmemoryuse`（アドレス空間）、`swapuse`（スワップ）などを制限できます。

```shell
# rctl -a jail:classic:pcpu:deny=80
# rctl -a jail:classic:maxproc:deny=1000
# rctl -a jail:classic:openfiles:deny=5000
# rctl -a jail:classic:vmemoryuse:deny=4G
```

ディスク転送量は `readbps` と `writebps` です。これらは `deny` に対応しないため `throttle` を使います。

```shell
# rctl -a jail:classic:writebps:throttle=1m
```

資源名の後のアクションは上限到達時の処理です。`deny` は割り当てを拒否し、`log` は警告を記録し、`devctl` は `devd(8)` を通じて通知します。

> **訳注:** 原文は `log` の出力先をシステムログとしていますが、FreeBSD 15.0 の [rctl(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.bin/rctl/rctl.8) はコンソールへの警告と説明しています。

`-u` で現在の使用量、`-h` で読みやすい単位を表示します。

```shell
# rctl -hu jail:classic
```

適用ルールを一覧表示します。

```shell
# rctl jail:classic
```

`-r` で jail に一致するルールをすべて削除します。

```shell
# rctl -r jail:classic
```

詳細は Security 章の[リソース制限](https://docs.freebsd.org/en/books/handbook/security/#security-resourcelimits)を参照してください。

<a id="jail-cpu-pinning"></a>
### cpuset による CPU 固定

`rctl(8)` の `pcpu` は CPU 使用量を制限しますが、特定のコアへ固定しません。使用コアの指定には `cpuset(1)` を使います。実行中の jail を名前または JID で指定します。

```shell
# cpuset -l 0-3 -j classic
```

現在許可されているコアは `-g` で確認します。

```shell
# cpuset -g -j classic
```

割り当てた集合の ID は `jls -v` の cpuset 列にも表示されます。CPU アフィニティを指定する jail.conf パラメータはないため、ホスト側で実行される `exec.created` または `exec.poststart` から `cpuset(1)` を呼び出します。

```text
exec.poststart = "cpuset -l 0-3 -j classic";
```

<a id="limiting-disk-space"></a>
### ディスク容量の制限

`rctl(8)` にはファイルシステムの容量を制限する資源がありません。jail ごとに ZFS データセットを使う場合は、quota と reservation で上限と予約容量を設定します。

```shell
# zfs set quota=20G zroot/jails/containers/classic
# zfs set reservation=5G zroot/jails/containers/classic
```

独立したデータセットが必要です。先ほどの ZFS Thin Jail はそうなっていますが、クラシック jail の例は共通の `containers` 内に `mkdir` で作るため、これらのコマンドを使うなら先に `zfs create` で作成します。構成は [Jail ディレクトリツリー](#host-configuration-directories)、プロパティは `zfs-set(8)` を参照してください。

<a id="jail-more-options"></a>
## 追加の Jail オプション

`jail(8)` には本章の例以外にも多くのパラメータがあります。jail は強い分離境界ですが、絶対的なものではありません。`allow.*` による制限緩和は機能と引き換えに分離性を下げ、jail 内の特権ユーザーをホストの root の権限へ近づけます。処理に必要な権限だけを許可し、それ以外は制限の厳しいデフォルトのままにします。

全一覧は `jail(8)` と `jail.conf(5)` にあります。以下ではよく使うものを説明します。

<a id="allow-permissions"></a>
### allow.* による権限

`allow.*` は個別の権限を渡す真偽値パラメータです。原文が参照する `jail(8)` では、`allow.set_hostname` と `allow.reserved_ports` を除いてデフォルトは無効と説明されています。必要な機能を明示的に許可します。

| パラメータ | デフォルト | 効果 |
|---|---|---|
| `allow.set_hostname` | 有効 | jail 自身のホスト名を変更可能にする。 |
| `allow.reserved_ports` | 有効 | jail 内の root に 1024 未満の予約ポートへのバインドを許可する。 |
| `allow.raw_sockets` | 無効 | raw ソケットを有効にし、`ping(8)` や `traceroute(8)` を利用可能にする。 |
| `allow.chflags` | 無効 | jail 内の root がシステムファイルフラグを操作できる。 |
| `allow.mount` | 無効 | 対応する `allow.mount.*` と組み合わせてマウント・アンマウントを許可する。 |
| `allow.quotas` | 無効 | ファイルシステムのクォータ管理を許可する。 |
| `allow.read_msgbuf` | 無効 | `dmesg(8)` によるカーネルメッセージバッファの読み取りを許可する。 |
| `allow.socket_af` | 無効 | IPv4、IPv6、local、route 以外のソケットアドレスファミリーを許可する。 |
| `allow.mlock` | 無効 | `mlock(2)` による物理メモリのロックを許可する。 |
| `allow.unprivileged_proc_debug` | 無効 | 非特権ユーザーが自身のプロセスにデバッグ機能を使える。 |
| `allow.vmm` | 無効 | `vmm(4)` による `bhyve(8)` ゲストの実行を許可する。 |
| `allow.nfsd` | 無効 | NFS サーバーの実行を許可する。 |

制限緩和で何が公開されるかを検討します。`allow.raw_sockets` はパケットの偽装を、`allow.chflags` はホストが保護に使う immutable や append-only フラグの解除を可能にします。`allow.mount` はファイルシステムの名前空間を開放します。

FreeBSD 14.0 のリリースノートでも紹介された jail 内 NFS サーバーには、`allow.nfsd`、VNET jail、ファイルシステムのマウントポイント自体を jail のルートとすること、`enforce_statfs` を `0` にしないことが必要です。

<a id="system-v-ipc"></a>
### System V IPC

System V の共有メモリ・セマフォ・メッセージキューを使うデータベースなどは、`sysvmsg`、`sysvsem`、`sysvshm` でモジュールごとに制御します。

- `inherit`: ホストの IPC オブジェクトを jail に公開します。
- `new`: jail 固有のキー名前空間を作成します。
- `disable`: 対応するシステムコールを失敗させます。

PostgreSQL を動かす典型的な例では、ホストの名前空間を見せず独自の共有メモリ環境を用意する `new` が適しています。

```text
sysvmsg = new;
sysvsem = new;
sysvshm = new;
```

古い `allow.sysvipc` は非推奨です。3 パラメータすべてを `inherit` にするのと同じで、ホスト全体の IPC 名前空間を共有するため、上のモジュール別パラメータを使います。

<a id="mounting-filesystems"></a>
### ファイルシステムのマウント

`allow.mount` は jail 内からのマウントを許可し、`allow.mount.devfs`、`allow.mount.fdescfs`、`allow.mount.fusefs`、`allow.mount.nullfs`、`allow.mount.procfs`、`allow.mount.linprocfs`、`allow.mount.linsysfs`、`allow.mount.tmpfs`、`allow.mount.zfs` で種類を選びます。それぞれ、`allow.mount` があり、`enforce_statfs` が `2` 未満の場合にだけ有効です。

`mount.devfs`、`mount.fdescfs`、`mount.procfs` は指定ファイルシステムを jail 用に自動マウントし、`mount.fstab` は追加のマウントを記述した fstab を指します。

`enforce_statfs` は見えるマウントポイントと、上述のマウント権限の有効性を制御します。

| 値 | jail から見えるマウントポイント |
|---|---|
| `0` | ホストのすべてのマウントポイント。制限なし。 |
| `1` | jail のルートディレクトリ配下だけ。 |
| `2`（デフォルト） | jail のルートが置かれている単一のマウントポイントだけ。 |

`allow.mount.*` は `2` 未満を必要とするため、jail 自身でマウントする構成では通常 `enforce_statfs = 1` を使います。

<a id="per-jail-securelevel"></a>
### Jail ごとの securelevel

`securelevel` は jail の `kern.securelevel` を設定し、jail 内の immutable フラグやデバイスの保護を強化します。jail の securelevel は親より低くできませんが、高くすることはできます。そのためホストをデフォルトのままにし、ネットワークに面した jail を `securelevel = 3` で動かす構成も可能です。

<a id="hierarchical-jails"></a>
### 階層化された Jail

jail が子 jail を作成すると、入れ子・階層構成になります。`children.max` は作成できる子 jail の数で、デフォルトの `0` は作成不可です。読み取り専用の `children.cur` は現在の数を示します。

子に親より大きい権限を与えることはできません。jail 内のプロセスは、自身が与えられた権限を超えて他者へ許可できないためです。この仕組みで jail 内から jail マネージャーを実行できます。

<a id="empty-persistent-jails"></a>
### 空の Jail と永続 Jail

通常 jail はプロセスが動いている間だけ存在し、最後のプロセスが終了すると消えます。`persist` を設定するとプロセスがなくても存在できます。空の jail を作成して内容を準備する間や、ネットワーク状態だけを持つ VNET jail を維持するのに使えます。

実験用に空の jail を作成して維持する例です。

```shell
# jail -c name=test path=/rescue persist
```

`nopersist` でフラグを解除すると、再びプロセスがなくなった時点で削除されるようになります。

<a id="jail-osrelease"></a>
### 異なる OS リリースの提示

jail のユーザーランドはホストより古くできますが、指定がなければ内部の `uname(1)` はホストのバージョンを読みます。`osrelease` は `kern.osrelease` と `uname -r` の文字列、`osreldate` は `kern.osreldate` と `uname -K` の数値を設定します。

古いユーザーランドに対応した値にすると、`uname(1)` や `sysctl(8)` の利用側、バージョンを検出するビルドツールなどが適切に動作します。原文は jail 内で実行する `freebsd-update(8)` も挙げていますが、配布セットの更新場所は[アップグレード手順](#jails-updating)のとおりホスト側です。

`pkg(8)` は `uname(1)` ではなく jail 自身のバイナリの ELF notes から ABI を求めるため、この設定でパッケージ管理の ABI は変わりません。ユーザーランドをホストのカーネルより新しくできないという規則も変わりません。[Jail のアップグレード](#jail-upgrading)を参照してください。

<a id="jails-zfs"></a>
## Jail と ZFS

jail に ZFS データセットを委任すると、jail 内の root はホスト管理者を介さず、子データセットの作成・スナップショット・クローン・ロールバックを行えます。書き込み可能でスナップショットを利用できる独自ストレージを渡す方法です。

ホストはデータセットの所有を維持し、指定ツリーとその子孫の管理だけを委任します。`jailed` プロパティと `zfs jail` の関係は [ZFS と Jail](https://docs.freebsd.org/en/books/handbook/zfs/#zfs-zfs-jail)を参照してください。

<a id="delegating-dataset-manually"></a>
### データセットを手動で委任する

この方法は、原文が対象とするサポート中の FreeBSD リリースで利用できます。

ホストで委任するデータセットを作成し、`jailed` を設定します。

```shell
# zfs create zroot/jails/data
# zfs set jailed=on zroot/jails/data
```

`jailed` は jail 内から管理することを示し、ホストは自動マウントしなくなります。

次に、jail に ZFS マウントを許可し、作成時にデータセットを接続します。jail.conf の対象ブロックに追加します。

```text
allow.mount;
allow.mount.zfs;
enforce_statfs = 1;
exec.created += "zfs jail ${name} zroot/jails/data";
```

`allow.mount.zfs` には `allow.mount` と `2` 未満の `enforce_statfs` が必要です。[追加オプション](#jail-more-options)も参照してください。停止時に接続が解除されるため、起動ごとに `exec.created` で接続し直します。`${name}` は jail 名に展開されます。実行中の jail へは `zfs jail <jid|name> zroot/jails/data` でも接続できます。

> **注:** jail は `/dev/zfs` へアクセスできる必要があります。標準の `devfsrules_jail`（ルールセット 4）は既に公開するため、ZFS 委任のための独自ルールセットは不要です。

jail 内で委任したデータセットをマウントして操作します。

```shell
# zfs mount -a
# zfs create zroot/jails/data/work
# zfs snapshot zroot/jails/data/work@monday
```

jail 内の root は委任ツリー内で作成・スナップショット・クローン・ロールバックを行えますが、委任元データセットの `quota` はホスト側でのみ設定できます。

<a id="attaching-datasets-automatically"></a>
### データセットを自動接続する

`zfs.dataset` は FreeBSD 15.0 で追加されたパラメータです。14.3 の `jail(8)` にはありません。

15.0 以降では、`jail(8)` がデータセットを接続でき、手動の `jailed` 設定と `zfs jail` の手順を省けます。委任するデータセットを列挙します。

```text
allow.mount;
allow.mount.zfs;
enforce_statfs = 1;
zfs.dataset = "zroot/jails/data";
```

起動時に列挙したデータセットを接続するため、上の `exec.created` フックは不要です。`allow.mount.zfs` が必要です。

まだ `zfs.dataset` に対応しない古い jail マネージャーのために、rc.d/jail は `/etc/rc.conf` の従来変数 `jail_<jailname>_zfs_dataset` も扱います。

<a id="accessing-snapshots-inside-jail"></a>
### Jail 内からスナップショットへアクセスする

FreeBSD 14.x と 15.x の `zfs.mount_snapshot` は、データセット全体を委任せずにスナップショットの内容へアクセスする機能です。`1` にすると jail 内のユーザーが `.zfs/snapshot` 配下を読めます。

```text
zfs.mount_snapshot = 1;
```

ホストで取ったスナップショットから個々のファイルを復元するのに便利です。`allow.mount.zfs` もあれば、jail 内でスナップショットをマウントすることもできます。`.zfs` の表示はデータセットの `snapdir` プロパティで制御します。

> **警告:** データセットの委任と `allow.mount.zfs` を組み合わせると、jail 内の root はマウント関連の ZFS プロパティを設定し、ファイルシステムをマウントできます。独自ストレージの管理を信頼できる jail にだけ、意図して許可してください。

<a id="jail-managers-and-containers"></a>
## Jail マネージャーとコンテナ

各種 jail は手動で作成・設定できますが、設定や管理を容易にするサードパーティーツールもあります。以下は原文にある一部の例です。

| 名前 | ライセンス | Ports のパス | ドキュメント |
|---|---|---|---|
| BastilleBSD | BSD-3 | `sysutils/bastille` | [Documentation](https://bastille.readthedocs.io/en/latest/) |
| pot | BSD-3 | `sysutils/pot` | [Documentation](https://pot.pizzamig.dev/) |
| cbsd | BSD-2 | `sysutils/cbsd` | [Documentation](https://github.com/cbsd/cbsd) |
| AppJail | BSD-3 | `sysutils/appjail`、開発版 `sysutils/appjail-devel` | [Documentation](https://github.com/DtxdF/AppJail#getting-started) |
| iocage | BSD-2 | `sysutils/iocage` | [Documentation](https://freebsd.github.io/iocage/) |
| ezjail | [Beer Ware](https://erdgeist.org/beerware.html) | `sysutils/ezjail` | [Documentation](https://erdgeist.org/arts/software/ezjail/) |

FreeBSD は 14.3-RELEASE から公式の OCI ベースシステムイメージを公開しています。同じ jail 技術を基盤に Podman で管理する OCI（Docker 形式）コンテナは、[Containers 章](17-containers.md)で説明します。ネイティブ jail を扱う本章とあわせて参照してください。
