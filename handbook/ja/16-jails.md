# 第16章 Jail（Jails）

> **翻訳状態**: 初訳ドラフト（機械支援・要校正）  
> **上流**: https://docs.freebsd.org/en/books/handbook/jails/  
> **ソース参照**: `handbook/en/16-jails.adoc.txt`  
> **著作権**: 原文 © The FreeBSD Documentation Project。本日本語訳は BSD-2-Clause（リポジトリ LICENSE）。

**Part III. System Administration**

---

## 概要

システム管理は困難な作業であるため、管理者の作業を容易にするための多くのツールが開発されてきました。これらのツールは、システムのインストール、設定、保守の方法を向上させることがよくあります。FreeBSD システムのセキュリティを強化するために使用できるツールの 1 つが *jails*（jail）です。jail は FreeBSD 4.X から利用可能であり、その有用性、パフォーマンス、信頼性、セキュリティが現在も向上し続けています。

jail は、一連のプロセスのルートディレクトリを変更するために使用される `man chroot(2)` の概念に基づいています。これにより、システムの他の部分から分離された安全な環境が作成されます。chroot 環境内で作成されたプロセスは、その外部のファイルやリソースにアクセスできません。そのため、chroot 環境で実行されているサービスが侵害されたとしても、攻撃者がシステム全体を侵害することはできないはずです。

しかし、chroot にはいくつかの制限があります。chroot は、柔軟性や複雑で高度な機能をあまり必要としない簡単なタスクに適しています。時が経つにつれて、chroot 環境から脱出する多くの方法が見つかり、サービスを保護するための解決策としては理想とは言えなくなっています。

jail は、従来の chroot 環境の概念をいくつかの点で改良したものです。

従来の chroot 環境では、プロセスがアクセスできるファイルシステムの部分だけが制限されます。システムリソースの残り、システムユーザー、実行中のプロセス、ネットワークサブシステムは、chroot されたプロセスとホストシステムのプロセスとで共有されます。jail は、ファイルシステム、ユーザーセット、ネットワークサブシステムへのアクセスを仮想化することで、このモデルを拡張します。jail 環境へのアクセスを調整するための、より細かい制御が利用できます。jail は、オペレーティングシステムレベルの仮想化の一種と考えることができます。

この章では、以下について説明します。

* jail とは何か、FreeBSD のインストールにおいてどのような目的で使用されるか。
* さまざまなタイプの jail。
* jail のネットワークを設定するさまざまな方法。
* jail 設定ファイル。
* さまざまなタイプの jail の作成方法。
* jail のネットワークアドレス変換（NAT）の設定方法。
* jail の起動、停止、再起動の方法。
* jail の内部と外部の両方からの、jail 管理の基本。
* さまざまなタイプの jail のアップグレード方法。
* jail が使用できるリソースを制限する方法。
* jail ごとの追加のセキュリティおよび機能オプション。
* ZFS データセットを jail に委任する方法。
* さまざまな FreeBSD jail マネージャーの不完全なリスト。

<a id="jail-types"></a>

## Jail の種類

管理者によっては、jail をさまざまなタイプに分類することもありますが、基盤となる技術は同じです。各管理者は、解決すべき問題に応じて、それぞれのケースでどのタイプの jail を作成するかを判断する必要があります。

以下に、さまざまなタイプ、その特徴、および使用にあたっての考慮事項を示します。

### Thick Jail（シックジャイル）

Thick Jail は、FreeBSD Jail の伝統的な形態です。Thick Jail では、ベースシステムの完全なコピーが jail の環境内に複製されます。つまり、jail は FreeBSD ベースシステムの独立したインスタンスを保持し、ライブラリ、実行可能ファイル、設定ファイルを含みます。jail は、ほぼ完全なスタンドアロンの FreeBSD インストールと考えることができますが、ホストシステムの制約内で動作します。この分離により、jail 内のプロセスはホストや他の jail のプロセスから分離されます。

**Thick Jail の利点:**

* **高度な分離:** jail 内のプロセスは、ホストシステムや他の jail から分離されています。
* **独立性:** Thick Jail は、ホストシステムや他の jail とは異なるバージョンのライブラリ、設定、ソフトウェアを持つことができます。
* **セキュリティ:** jail は独自のベースシステムを含むため、jail 環境に影響を与える脆弱性や問題は、ホストや他の jail に直接影響しません。

**Thick Jail の欠点:**

* **リソースのオーバーヘッド:** 各 jail が独自のベースシステムを維持するため、Thick Jail は Thin Jail と比較してより多くのリソースを消費します。
* **メンテナンス:** 各 jail は、ベースシステムコンポーネントの独自のメンテナンスと更新が必要です。

### Thin Jail（シンジャイル）

Thin Jail は、OpenZFS スナップショットまたは NullFS マウントのいずれかを使用して、テンプレートからベースシステムを共有します。各 Thin Jail にはベースシステムの最小限のサブセットのみが複製されるため、Thick Jail と比較してリソース消費が少なくなります。

この2つのメカニズムは、jail が存在するようになると動作が異なります。OpenZFS 方式では、各 Thin Jail はテンプレートスナップショットのクローンとして作成されます。つまり、テンプレートと変更されていないブロックを共有する独立したコピーオンライトコピーですが、変更されるとテンプレートから分岐します。テンプレートへのその後の変更は既存のクローンには伝播せず、各クローンは Thick Jail と同様に個別に保守・更新されます。

NullFS 方式では、各 Thin Jail は実行時にテンプレートを読み取り専用でマウントするため、ベースシステムはライブで共有され、テンプレートを更新するとそれをマウントしているすべての jail が更新されます。この共有された読み取り専用のベースが、NullFS Thin Jail の分離性と独立性を Thick Jail よりも低くしている理由でもあります。共有コンポーネントの変更は、それを使用しているすべての jail に同時に影響するためです。

要約すると、FreeBSD Thin Jail は、分離された環境内にベースシステムの大部分（ただしすべてではない）を複製する FreeBSD Jail の一種です。

**Thin Jail の利点:**

* **リソース効率:** Thin Jail は Thick Jail と比較してリソース効率が高くなります。ベースシステムの大部分を共有するため、ディスク容量とメモリの消費が少なくなります。これにより、過剰なリソースを消費することなく、同じハードウェア上でより多くの jail を実行できます。
* **迅速な導入:** Thin Jail の作成と起動は、一般的に Thick Jail よりも高速です。これは、複数のインスタンスを迅速に展開する場合に特に有利です。
* **統一的メンテナンス:** NullFS 方式では、Thin Jail がベースシステムの単一の読み取り専用コピーを共有するため、共通のベースシステムコンポーネント（ライブラリやバイナリなど）の更新とメンテナンスはテンプレート上で一度だけ行うだけで済みます。これにより、各 Thick Jail に個別のベースシステムを維持する場合と比較して、メンテナンスプロセスが簡素化されます。OpenZFS クローンの Thin Jail にはこの利点はありません。各クローンは独立しているため、Thick Jail と同様に、更新は各 jail に個別に適用する必要があります。
* **リソースの共有:** Thin Jail は、ライブラリやバイナリなどの共通リソースをホストシステムとより簡単に共有できます。これにより、ディスクキャッシュの効率が向上し、jail 内のアプリケーションのパフォーマンスが改善される可能性があります。

**Thin Jail の欠点:**

* **分離性の低下:** Thin Jail の主な欠点は、Thick Jail と比較して分離性が低いことです。特に NullFS 方式では、jail がテンプレートのベースシステムのライブコピーを共有するため、これらの共有コンポーネントに影響を与える脆弱性や問題が、複数の jail に同時に影響を与える可能性があります。
* **セキュリティ上の懸念:** Thin Jail の分離性の低下は、...

セキュリティリスクを引き起こす可能性があります。ある jail が侵害された場合、他の jail やホストシステムに影響を及ぼす可能性が高くなるためです。

* 依存関係の競合: 複数のシン jail が同じライブラリやソフトウェアの異なるバージョンを必要とする場合、依存関係の管理が複雑になることがあります。場合によっては、互換性を確保するために追加の作業が必要になることもあります。
* 互換性の課題: シン jail 内のアプリケーションは、テンプレートが提供する共有コンポーネントとは異なるベースシステム環境を想定している場合、互換性の問題に遭遇する可能性があります。

[[service-jails]]
### Service Jails

サービス jail は、ホストとファイルシステムツリー全体を直接共有し（jail ルートパスは `/`）、そのためホスト上のあらゆるファイルにアクセスして変更でき、ホストと同じユーザーアカウントを共有します。デフォルトではネットワークや jail で制限されている他のリソースにアクセスできませんが、ホストのネットワークを再利用し、jail の制限の一部を解除するように設定できます。サービス jail のユースケースは、最小限の設定で、サービスの必要なファイルに関する知識なしに、サービス/デーモンを jail 内に自動的に隔離することです。サービス jail は FreeBSD 15.0 以降で利用可能です。

サービス jail の利点:

* ゼロ管理: サービス jail 対応のサービスは、`/etc/rc.conf` に設定を 1 行追加するだけで済みます。サービス jail 非対応のサービスは、2 行の設定が必要です。
* リソース効率: サービス jail はシン jail よりもリソース効率が高く、追加のディスク容量やネットワークリソースを必要としません。
* 高速なデプロイ: 個別のサービス/デーモンだけを jail 化し、同じサービス/デーモンの並列インスタンスが必要ない場合、サービス jail の作成と起動は一般的にシン jail よりも高速です。
* 共有リソース: サービス jail はライブラリやバイナリなどのすべてのリソースをホストシステムと共有します。これにより、ディスクキャッシュがより効率的になり、jail 内のアプリケーションのパフォーマンスが向上する可能性があります。
* プロセス分離: サービス jail は特定のサービスを分離します。サービス jail の子プロセスではないプロセスは、同じユーザーアカウントで実行されている場合でも、サービス jail からは見えません。

サービス jail の欠点:

* 分離の低下: サービス jail の主な欠点は、シック jail やシン jail と比較してファイルシステムの分離が提供されないことです。
* セキュリティ上の懸念: サービス jail の分離の低下はセキュリティリスクを引き起こす可能性があります。ある jail が侵害された場合、ホストシステム上のすべてに影響を及ぼす可能性が高くなるためです。

以下で説明する jail の設定のほとんどは、サービス jail には必要ありません。jail の仕組みを理解するには、これらの設定オプションを理解しておくことをお勧めします。サービス jail の設定に必要な詳細は、[Service Jails](#service-jails-config) セクションにあります。

[[vnet-jails]]
### VNET Jails

FreeBSD VNET jail は、その中で実行されるプロセスのネットワークリソースの分離と制御を可能にする仮想化環境です。jail 内のプロセスに対して別個のネットワークスタックを作成することで、高度なネットワークセグメンテーションとセキュリティを提供し、jail 内のネットワークトラフィックがホストシステムや他の jail から分離されることを保証します。

本質的に、FreeBSD VNET jail はネットワーク設定メカニズムを追加します。つまり、VNET jail はシック jail またはシン jail として作成できます。

[[linux-jails]]
### Linux Jails

FreeBSD Linux Jail は、FreeBSD オペレーティングシステムの機能であり、FreeBSD jail 内で Linux バイナリとアプリケーションを使用できるようにします。この機能は、特定の Linux システムコールとライブラリを FreeBSD カーネル上で変換して実行できるようにする互換レイヤーを組み込むことで実現されます。Linux Jail の目的は、別の Linux 仮想マシンや環境を必要とせずに、FreeBSD システム上で Linux ソフトウェアを実行できるようにすることです。

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

[[loopback-addresses-shared-ip-Jails]]
==== 共有 IP Jail におけるループバックアドレス

共有スタック jail には、専用のループバックインターフェイスがありません。
FreeBSD カーネルはこれを補います。非 VNET jail では、`127.0.0.1` または `::1` がその jail 自身のアドレスのいずれでもない場合、カーネルはループバックアドレスに対する `bind()` と `connect()` の両方を、その jail の最初の `ip4.addr` または `ip6.addr` に静かに書き換えます。
この動作は man:jail(8) には文書化されていませんが、セキュリティ上の影響を伴うため重要です。

[WARNING]
====
サービスを `localhost` にバインドすれば jail 内に閉じ込められると考えてはなりません。
共有 IP jail では、`127.0.0.1` で待ち受けるよう指示されたデーモンは、実際には jail の最初のアドレスにバインドされます。これは多くの場合 LAN 側に面したアドレスであり、したがってネットワークから到達可能になります。
====

標準的な対策は、jail にプライベートなループバックアドレスを割り当て、それを先頭にリストすることです。
ホスト上に専用のループバックインターフェイスをクローン作成し、`127.0.0.0/8` の範囲（またはプライベートな RFC 1918 アドレス）のアドレスを割り当てます。

[source,shell]
....
# sysrc cloned_interfaces="lo1"
# sysrc ifconfig_lo1="inet 127.0.1.1/32"
....

次に、そのアドレスを jail の `ip4.addr` の先頭に、ルーティング可能なアドレスより前にリストします。これにより、ループバックのリマップが LAN 側のアドレスではなくプライベートアドレスに着地します。

[[preparing-host-services]]
==== ホストサービスの準備

各 jail エイリアスアドレスはホストのポートを共有します。
ワイルドカードアドレスにバインドされたホストデーモン（リスナー一覧では `*:port` と表示されます）は、すべての jail エイリアスでも待ち受けることになり、jail 自身のサービスがそのポートを要求する前にポートを占有してしまいます。
jail を起動する前に、ホストが現在何を待ち受けているかを監査してください。

[source,shell]
....
# sockstat -4 -6 -l
....

ワイルドカードアドレスにバインドする各デーモンを、ホスト自身のアドレスだけを使用し、jail のアドレスを解放したままにするように制限します。

* man:syslogd(8): [.filename]#/etc/rc.conf# で `syslogd_flags="-ss"` を設定します。
`-s` が 1 つの場合、syslogd はセキュアモードで実行され、リモートのログメッセージを待ち受けません。syslogd(8) によれば、`-s` が「2 回指定された場合、ネットワークソケットはまったく開かれません」。これにより、syslogd がリモートホストへの送信も停止します。
* man:sshd(8): [.filename]#/etc/ssh/sshd_config# の `ListenAddress` をデフォルトのワイルドカードのままにせず、ホストのアドレスに固定します。
* man:ntpd(8) と man:sendmail(8): それぞれの設定を通じて、ホストアドレスにもバインドします。

jail が使用できるアドレスをファイアウォールレベルで制御するには、crossref:firewalls[firewalls,ファイアウォール] を参照してください。

[[host-configuration-directories]]
=== Jail ディレクトリツリーのセットアップ

jail のファイルを置く場所に特別な決まりはありません。

[.filename]#/jail# を使用する管理者もいれば、[.filename]#/usr/jail# を使用する管理者もおり、さらに [.filename]#/usr/local/jails# を使用する管理者もいます。
この章では [.filename]#/usr/local/jails# を使用します。

[.filename]#/usr/local/jails# の他に、以下のディレクトリも作成されます。

* [.filename]#media# には、ダウンロードしたユーザーランドの圧縮ファイルが格納されます。
* [.filename]#templates# には、Thin Jail を使用する際のテンプレートが格納されます。
* [.filename]#containers# には、jail が格納されます。

OpenZFS を使用する場合は、次のコマンドを実行してこれらのディレクトリのデータセットを作成します。

[source,shell]
....
# zfs create -o mountpoint=/usr/local/jails zroot/jails
# zfs create zroot/jails/media
# zfs create zroot/jails/templates
# zfs create zroot/jails/containers
....

[TIP]
====
この例では親データセットに `zroot` を使用しましたが、他のデータセットを使用することもできました。
====

jail ごとに個別の子データセットを作成することで、jail ごとのスナップショット、クローン、クォータ、データセット委任が後で可能になります。
各 jail ディレクトリが独自のデータセットになるため、OpenZFS は `quota` プロパティと `reservation` プロパティを使用してディスク使用量を上限設定および保証の両方ができます。crossref:jails[jail-resource-limits,Jail リソース制限] を参照してください。

UFS を使用する場合は、次のコマンドを実行してディレクトリを作成します。

[source,shell]
....
# mkdir /usr/local/jails/
# mkdir /usr/local/jails/media
# mkdir /usr/local/jails/templates
# mkdir /usr/local/jails/containers
....

<a id="jail-configuration-files"></a>
=== Jail 設定ファイル

jail を設定する方法は 2 つあります。

f

ホストシステムに jail が少数しかない場合は、各 jail のエントリを `/etc/jail.conf` ファイルに追加できます。  
もう 1 つの方法は、`/etc/jail.conf.d/` ディレクトリ内に各 jail 用のファイルを作成する方法です。

ホストシステムに jail が多数ある場合は、`/etc/jail.conf.d/` ディレクトリに jail ごとに 1 つの設定ファイルを置くことをお勧めします。

`/etc/jail.conf.d/` 内のファイルは、拡張子が `.conf` であり、かつ `/etc/jail.conf` にインクルードされる必要があります:

```text
.include "/etc/jail.conf.d/*.conf";
```

典型的な jail エントリは次のようになります:

```text
jailname { (1)
  # STARTUP/LOGGING
  exec.start = "/bin/sh /etc/rc"; (2)
  exec.stop = "/bin/sh /etc/rc.shutdown"; (3)
  exec.consolelog = "/var/log/jail_console_${name}.log"; (4)

  # PERMISSIONS
  allow.raw_sockets; (5)
  exec.clean; (6)
  mount.devfs; (7)

  # HOSTNAME/PATH
  host.hostname = "${name}"; (8)
  path = "/usr/local/jails/containers/${name}"; (9)

  # NETWORK
  ip4.addr =

#### グローバル設定、ワイルドカ

`man jail(8)` および `man jail.conf(5)` を参照してください。

<a id="classic-jail"></a>

## クラシック Jail (Thick Jail)

これらの jail は実際の FreeBSD システムに似ています。  
通常のホストシステムとほぼ同様に管理でき、独立して更新できます。

### クラシック Jail の作成

原則として、jail に必要なものはホスト名、ルートディレクトリ、IP アドレス、そしてユーザーランドだけです。

jail 用のユーザーランドは、公式の FreeBSD ダウンロードサーバーから取得できます。

以下のコマンドを実行して、ユーザーランドをダウンロードします:

```shell
# fetch https://download.freebsd.org/releases/amd64/amd64/{rel-latest}-RELEASE/base.txz -o /usr/local/jails/media/{rel-latest}-RELEASE-base.txz
```

ダウンロードが完了したら、jail のディレクトリにコンテンツを展開する必要があります。

以下のコマンドを実行して、ユーザーランドを jail のディレクトリに展開します:

```shell
# mkdir -p /usr/local/jails/containers/classic
# tar -xf /usr/local/jails/media/{rel-latest}-RELEASE-base.txz -C /usr/local/jails/containers/classic --unlink
```

ユーザーランドを jail ディレクトリに展開したら、タイムゾーンと DNS サーバーのファイルをコピーする必要があります:

```shell
# cp /etc/resolv.conf /usr/local/jails/containers/classic/etc/resolv.conf
# cp /etc/localtime /usr/local/jails/containers/classic/etc/localtime
```

ファイルをコピーしたら、次のコマンドを実行して最新のパッチレベルに更新します:

```shell
# freebsd-update -b /usr/local/jails/containers/classic/ fetch install
```

最後のステップは、jail を設定することです。jail のパラメータを設定ファイル `/etc/jail.conf` または `jail.conf.d` に追加する必要があります。

例は次のとおりです:

```
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

以下のコマンドを実行して、jail を起動します:

```shell
# service jail start classic
```

jail の管理方法の詳細は、「Jail の管理」のセクションを参照してください。

### Jail ユーザーランドの取得

上記の fetch と展開の手順は、jail のルートディレクトリを準備する従来の方法ですが、これだけが唯一の方法ではありません。同じユーザーランドは、`bsdinstall(8)` を使って、ベースシステムのパッケージから、またはローカルで構築したソースツリーからインストールすることもできます。

`bsdinstall(8)` には、指定したディレクトリに新しいユーザーランドを設定して `jail(8)` で使用するための専用の `jail` ターゲットがあります。これは、カーネルをインストールせずに配布セットを取得・展開し、通常のインストールのディスク分割やネットワークの手順をスキップするため、手動の fetch と `tar(1)` の一連の操作に代わる、1 コマンドでスクリプト化可能な方法です:

```shell
# bsdinstall jail /usr/local/jails/containers/classic
```

`jail` ターゲットは、デフォルトでベース配布セット (`base.txz`) をインストールします。FreeBSD 15.0 以降では、`bsdinstall(8)` の `pkgbase` ターゲットを使って、ベースシステムのパッケージからルートディレクトリを準備することもできます。このパッケージベースの方法については、次で説明します。

FreeBSD 15.0 以降、ベースシステムはパッケージとしても公開されているため、jail ユーザーランドは `FreeBSD-base` リポジトリから `pkg(8)` を使って完全にインストールできます。`pkg(8)` をグローバルオプション `--rootdir` で jail のルートディレクトリに向け、ベースセットの jail バリアントをインストールします:

```shell
# pkg --rootdir /usr/local/jails/containers/classic install -r FreeBSD-base FreeBSD-set-base-jail
```

最小限のユーザーランドにするには、`FreeBSD-set-base-jail` の代わりに `FreeBSD-set-minimal-jail` を使用します。この方法でインストールされた jail は、その後、`freebsd-update(8)` ではなく `pkg(8)` でパッチ適用・アップグレードされます。詳しくは、「pkgbase Jail のアップグレード」のセクションを参照してください。

> **注:** ベースシステムパッケージは FreeBSD 15.0 におけるテクノロジープレビューです。`FreeBSD-base` リポジトリは `/etc/pkg/FreeBSD.conf` で定義されていますが、デフォルトでは無効になっているため、`install -r FreeBSD-base` で明示的に選択してください。ターゲットのルートディレクトリと、その `var/cache/pkg` および `var/db/pkg` サブディレクトリは、あらかじめ作成しておく必要がある場合があります。従来の



## Thin Jails

Thin Jails は Thick Jails と同じテクノロジーを使用していますが、その作成手順は異なります。  
Thin Jails は、OpenZFS スナップショットを使用するか、テンプレートと NullFS を使用して作成できます。  
OpenZFS スナップショットや NullFS を使用したテンプレートには、従来の jails に比べていくつかの利点があります。たとえば、スナップショットからより速く作成できることや、NullFS を使用して複数の jails を更新できることなどです。

### OpenZFS スナップショットを使用した Thin Jail の作成 {#creating-thin-jail-openzfs-snapshots}

FreeBSD と OpenZFS の統合が優れているため、OpenZFS スナップショットを使用して新しい Thin Jails を簡単に作成できます。

OpenZFS スナップショットを使用して Thin Jail を作成するには、まず『Jail ディレクトリツリーのセットアップ』の手順に従って jail ディレクトリツリーを作成します（jails の章を参照）。

次に、テンプレートを作成します。  
テンプレートは新しい jails を作成するためにのみ使用されます。  
そのため、テンプレートは「読み取り専用」モードで作成され、jails が不変のベースで作成されるようにします。

テンプレート用の dataset を作成するには、次のコマンドを実行します。

```shell
# zfs create -p zroot/jails/templates/{rel-latest}-RELEASE
```

次に、以下のコマンドを実行して userland をダウンロードします。

```shell
# fetch https://download.freebsd.org/releases/amd64/amd64/{rel-latest}-RELEASE/base.txz -o /usr/local/jails/media/{rel-latest}-RELEASE-base.txz
```

ダウンロードが完了したら、次のコマンドを実行して、テンプレートディレクトリに内容を展開する必要があります。

```shell
# tar -xf /usr/local/jails/media/{rel-latest}-RELEASE-base.txz -C /usr/local/jails/templates/{rel-latest}-RELEASE --unlink
```

templates ディレクトリに userland を展開したら、次のコマンドを実行して、タイムゾーンと DNS サーバーのファイルをテンプレートディレクトリにコピーする必要があります。

```shell
# cp /etc/resolv.conf /usr/local/jails/templates/{rel-latest}-RELEASE/etc/resolv.conf
# cp /etc/localtime /usr/local/jails/templates/{rel-latest}-RELEASE/etc/localtime
```

次に、以下のコマンドを実行して、最新のパッチレベルに更新します。

```shell
# freebsd-update -b /usr/local/jails/templates/{rel-latest}-RELEASE/ fetch install
```

更新が完了すると、テンプレートの

eebsd.org/releases/amd64/amd64/{rel-latest}-RELEASE/base.txz -o /usr/local/jails/media/{rel-latest}-RELEASE-base.txz

ダウンロードが完了したら、次のコマンドを実行してテンプレートディレクトリに内容を展開する必要があります。

```shell
# tar -xf /usr/local/jails/media/{rel-latest}-RELEASE-base.txz -C /usr/local/jails/templates/{rel-latest}-RELEASE-base --unlink
```

テンプレートディレクトリにユーザーランドが展開されたら、次のコマンドを実行して、タイムゾーンファイルとDNSサーバーファイルをテンプレートディレクトリにコピーする必要があります。

```shell
# cp /etc/resolv.conf /usr/local/jails/templates/{rel-latest}-RELEASE-base/etc/resolv.conf
# cp /etc/localtime /usr/local/jails/templates/{rel-latest}-RELEASE-base/etc/localtime
```

ファイルをテンプレートに移動したら、次に次のコマンドを実行して最新のパッチレベルに更新します。

```shell
# freebsd-update -b /usr/local/jails/templates/{rel-latest}-RELEASE-base/ fetch install
```

ベーステンプレートに加えて、`skeleton`（スケルトン）を配置するディレクトリも作成する必要があります。一部のディレクトリはテンプレートから`skeleton`にコピーされます。

OpenZFSを使用する場合は、次のコマンドを実行して`skeleton`用のデータセットを作成します。

```shell
# zfs create -p zroot/jails/templates/{rel-latest}-RELEASE-skeleton
```

UFSを使用する場合は、次のコマンドを実行します。

```shell
# mkdir /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton
```

次に`skeleton`ディレクトリを作成します。`skeleton`ディレクトリにはjailのローカルディレクトリが保持されます。

次のコマンドを実行してディレクトリを作成します。

```shell
# mkdir -p /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/home
# mkdir -p /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/usr
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/etc /usr/local/jails/templates/{rel-latest}-RELEASE-skeleton/etc
# mv /usr/local/jails/templates/{rel-latest}-RELEASE-base/usr/local /

`ase.fstab` ファイルは次のようになります:

```shell
/usr/local/jails/templates/{rel-latest}-RELEASE-base  /usr/local/jails/thinjail-nullfs-base/ nullfs   ro          0 0
/usr/local/jails/containers/thinjail     /usr/local/jails/thinjail-nullfs-base/skeleton nullfs  rw  0 0
```

この `fstab` ファイルは、man:mount_nullfs(8) がベーステンプレートとスケルトンを jail 内でどのように提示するかを制御します。
ベーステンプレートは読み取り専用 (`ro`) でマウントされるため、すべての NullFS jail がベースシステムの不変のコピーを 1 つ共有します。
jail ごとのスケルトンは読み書き可能 (`rw`) でマウントされ、各 jail は独自の書き込み可能な `/etc`、`/var`、`/usr/local` などのローカルディレクトリをここに保持します。
すべての jail が単一の読み取り専用ベーステンプレートを共有するため、テンプレートを 1 つ更新するだけで、すべての NullFS jail が一度に更新されます。これは、それぞれを個別に更新する必要がある独立した OpenZFS クローンとは対照的です。

以下のコマンドを実行して jail を起動します:

```shell
# service jail start thinjail
```

[[creating-vnet-jail]]



ベースシステムには、この配線処理（plumbing）を自動的に行うヘルパースクリプト [.filename]#/usr/share/examples/jails/jib# が同梱されています。

手書きの man:ifconfig[8] の5行の代わりに、jail のフックから次のように参照します：

```shell
  exec.prestart += "jib addm ${name} em0";
  exec.poststop += "jib destroy ${name}";

  vnet.interface = "e0b_${name}";
```

`jib addm` は、ホスト側が `e0a_<name>`、jail 側が `e0b_<name>` という名前の epair を作成し、ホスト側を、メンバーインターフェイスにちなんで名付けられたブリッジ（`em0` の場合、ブリッジは `em0bridge`）に自動的に接続します。その jail 側を `vnet.interface` に指定します。jail が停止すると、`jib destroy` が epair を削除します。このスクリプトには、管理しているインターフェイスを一覧表示する `jib show` サブコマンドもあります。

[[jail-vnet-jng]]
### jng による Netgraph VNET ネットワーキング

「ネットワーキング」の概要で触れた3つ目のネットワーキングモードは、man:bridge[4] と epair の代わりに man:netgraph[4] を使用します。ベースシステムには2つ目のヘルパー [.filename]#/usr/share/examples/jails/jng# が同梱されており、各 jail に接続された `ng_bridge` と `ng_eiface` を構築します：

```shell
  exec.prestart += "jng bridge ${name} em0";
  exec.poststop += "jng shutdown ${name}";

  vnet.interface = "ng0_${name}";
```

`jng bridge` は netgraph ノードと、`ng0_<name>` という名前の jail 側インターフェイスを作成し、それを `vnet.interface` に指定します。`jng shutdown` は jail が停止したときにトポロジーを破棄します。結果は機能的には epair とブリッジの構成と同等ですが、man:bridge[4] ではなく netgraph ノード上に構築されます。

[[jail-vnet-firewall]]
### VNET Jail 内でのファイアウォールと DHCP の実行

`devfs_ruleset = 5` は [.filename]#/dev/pf# を公開するため、VNET jail は独自のファイアウォールを実行できます。ホスト上とまったく同様に、jail の [.filename]#/etc/rc.conf# で `pf_enable="YES"` を設定し、独自の [.filename]#/etc/pf.conf# を用意することで、jail 内でファイアウォールを有効にできます。

ただし、ルールセット5は [.filename]#/dev/bpf# を公開しません。DHCP でアドレスを取得する VNET jail（たとえば [.filename]#/etc/rc.conf# の `ifconfig_e0b_myjail="SYNCDHCP"`）は man:dhclient[8] を実行しますが、これには bpf が必要なため、ルールセット5では失敗します。「Devfs ルールセット（Devfs Rulesets）」のレシピに従い、[.filename]#/etc/devfs.rules# に `devfsrules_jail_vnet` から始まり、さらに bpf デバイスの非表示を解除するカスタムルールセットを定義します：

```shell
[devfsrules_jail_vnet_dhcp=101]
add include $devfsrules_jail_vnet
add path 'bpf*' unhide
```

ホスト上で `service devfs restart` を実行した後、jail の設定で `devfs_ruleset = 101;` を指定して新しいルールセットを参照させます。

<!-- [[creating-linux-jail]] -->

## Linux Jail

FreeBSD は、Linux バイナリ互換（Linux Binary Compatibility）と `sysutils/debootstrap` を利用することで、jail 内で Linux ユーザーランドを実行できます。jail にはカーネルがありません。jail はホストのカーネル上で動作します。したがって、ホストシステムで Linux バイナリ互換を有効にする必要があります。

起動時に Linux ABI を有効にするには、次のコマンドを実行します。

```shell
# sysrc linux_enable="YES"
```

有効にすると、再起動せずに次のコマンドで開始できます。

```shell
# service linux start
```

次の手順は、上記で示したとおり、たとえば「OpenZFS スナップショットを使用したシン Jail の作成」の手順で jail を作成することですが、*設定は行わない*でください。FreeBSD Linux jail には、以下で詳しく説明する特定の設定が必要です。

ホストに `/etc/jail.conf` がまだない場合（たとえば、これまでコマンドラインからのみ jail を作成してきたシステム）は、後で `man service(8)` が jail を停止できるように、空のファイルを作成します。

```shell
# touch /etc/jail.conf
```

`man service(8)` の jail スクリプトは jail を停止する際に `/etc/jail.conf` を読み取るため、ファイルが存在しないと停止コマンドは失敗します。以前の節で `/etc/jail.conf` がすでにある場合は、この手順は不要です。

次の `man jail(8)` コマンドは、jail に必要な設定を実行し、`/etc/jail.conf` のエントリなしで直接起動します。`-c` フラグは新しい jail を作成し、`-m` は既存の jail を変更します。`-cm` と組み合わせると、`man jail(8)` は jail が存在しなければ作成し、存在すれば更新します。

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

新しく作成した jail に `root` として `man jexec(8)` でアクセスします。

```shell
# jexec -u root ubuntu sh
```

jail 内で、`sysutils/debootstrap` をインストールし、それを使用して `/compat/ubuntu` の下に Ubuntu ユーザーランドを構築します。`sysutils/debootstrap` は Linux ユーザーランドを構築するツールです。その後、jail に入るために必要になることはありません。`man pkg(7)` を初めて実行すると、自動的にブートストラップされます。

```shell
# pkg install debootstrap
# debootstrap jammy /compat/ubuntu
```

`jammy` は Ubuntu 22.04 LTS を選択します。linuxulator で動作する限り、`noble`（Ubuntu 24.04）などの新しい LTS を代わりに選択することもできます。

プロセスが完了し、コンソールに `Base system installed successfully` というメッセージが表示されたら、ホストシステムから jail を停止します。この jail は `/etc/rc.conf` で有効化されておらず、`/etc/jail.conf` にもまだ記載されていないため、有効化されていない jail でも実行できる `one` 接頭辞付きの `man service(8)` アクションを使用します。

```shell
# service jail onestop ubuntu
```

`onestart` アクションと `onestop` アクションは、`jail_enable` によって有効化されていない、または `jail_list` に記載されていない jail に対する `start` と `stop` の対応物です。

次に、Linux jail 用のエントリを `/etc/jail.conf` に追加します。

```
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

> **ヒント:**
> 
> jail は（原文ここで途切れています）

また、jail 内で実行されるプログラムに対して、特定の Linux カーネル識別情報を提示します。
`linux` パラメータは、jail がホストの Linux エミュレーション環境を継承するか (`inherit`)、独自の環境を持つか (`new`) を選択します。また、`linux.osname`、`linux.osrelease`、`linux.oss_version` は、Linux バイナリが認識する OS 名、リリース、OSS バージョンを設定します。
たとえば、`linux.osrelease=6.1.0` と設定すると、jail 内の `man uname(1)` やバージョンを確認する Linux プログラムは、ホスト全体の `compat.linux.osrelease` 値ではなく、そのカーネルリリースを報告するようになります。

その後、jail は以下のコマンドで通常どおり起動できます。

```shell
# service jail start ubuntu
```

Ubuntu 環境には、以下のコマンドでアクセスできます。

```shell
# jexec ubuntu chroot /compat/ubuntu /bin/bash
```

詳細については、Linux バイナリ互換（Linux Binary Compatibility）の章を参照してください。

<a id="jail-nat"></a>



## Jail の管理

jail を作成したら、起動、再起動、削除、ソフトウェアのインストールなど、実行できる操作がいくつかあります。このセクションでは、ホストから jail に対して行えるさまざまな操作について説明します。

### 実行中の jail の一覧表示 {#list-running-jails}

ホストシステム上で実行中の jail を一覧表示するには、`man jls(8)` コマンドを使用します。

```shell
# jls
```

出力は次のようになります。

```
   JID  IP Address      Hostname                      Path
     1  192.168.1.151  classic                       /usr/local/jails/containers/classic
```

`man jls(8)` は `--libxo` 引数をサポートしており、`man libxo(3)` ライブラリを通じて `JSON` や `HTML` などの他の形式で表示できます。

たとえば、`JSON` 出力を得るには次のコマンドを実行します。

```shell
# jls --libxo=json
```

出力は次のようになります。

```
{"__version": "2", "jail-information": {"jail": [{"jid":1,"ipv4":"192.168.1.151","hostname":"classic","path":"/usr/local/jails/containers/classic"}]}}
```

デフォルトの一覧は、`man jls(8)` が報告できる内容のほんの一部にすぎません。各 jail の状態と割り当てられた cpuset ID を含む、詳細な複数行の要約を表示するには、`-v` フラグを追加します。

```shell
# jls -v
```

要求したパラメータの値の上にフィールド名を持つヘッダー行を表示するには、`-h` を使用します。

```shell
# jls -h jid name path
```

単一の jail の特定のパラメータを照会するには、`-j` で名前を指定し、表示するパラメータを列挙します。

```shell
# jls -j classic path host.hostname ip4.addr
```

出力は次のようになります。

```
/usr/local/jails/containers/classic classic 192.168.1.151
```

シャットダウン中の jail も含めるには `-d` を追加します。シャットダウン中の jail は、dying 状態の間は通常は表示されません。

```shell
# jls -d
```

### jail の起動、再起動、停止 {#start-jail}

`man service(8)` は、ホスト上で jail を起動、再起動、または停止するために使用されます。

たとえば、jail を起動するには、次のコマンドを実行します。

```shell
# service jail start jailname
```

jail に対して他の操作を行うには、`start` 引数を `restart` または `stop` に変更します。

jail の停止は、その中のプロセスを kill するだけではありません。jail が停止されると、`man jail(8)` は最初に `exec.stop` パラメータ（通常は `/bin/sh /etc/rc.shutdown`）のコマンドを jail 内で実行し、サービスがクリーンにシャットダウンされるようにします。次に、jail 内でまだ実行中のプロセスに `SIGTERM` を送信し、それらが終了するまで `stop.timeout` 秒（デフォルトでは 10 秒）待機します。その時間が経過すると、jail は削除され、残っているプロセスは `SIGKILL` で強制終了されます。`stop.timeout` がゼロに設定されている場合、`SIGTERM` は送信されず、jail は直ちに削除されます。これが、停止に時間のかかるデーモンを実行している jail が、停止中に 10 秒間フリーズしているように見える理由です。データベースや、正常にシャットダウンするためにより長い時間を必要とするサービスを実行している jail の場合は、`/etc/jail.conf` 内の `stop.timeout` を引き上げてください。

### jail の破棄 {#destroy-jail}

jail の破棄は、`man service(8)` を使用して jail を停止し、jail ディレクトリと `/etc/jail.conf` エントリを削除するだけでは済みません。

FreeBSD はシステムセキュリティを非常に重視しています。そのため、root ユーザーでも削除できないファイルがいくつかあります。この機能は File Flags（ファイルフラグ）として知られています。ファイルが UFS ファイルシステム上にある jail の場合、jail ディレクトリを削除する前に、これらのフラグをクリアする必要があります。

最初のステップは、次のコマンドを実行して目的の jail を停止することです。

```shell
# service jail stop classic
```

2 番目のステップは、`man chflags(1)` を使用してこれらのフラグを削除することです。次のコマンドを実行します。ここで `classic` は削除する jail の名前です。

```shell
# chflags -R 0 /usr/local/jails/containers/classic
```

3 番目のステップは、jail があったディレクトリを削除することです。

```shell
# rm -rf /usr/local/jails/containers/classic
```

上記の 2 つのステップは、UFS ファイルシステムに保存されている jail に適用されます。独自の ZFS dataset によってバックアップされている jail（[Jail Directory Tree の設定](#host-configuration-directories) で作成したもの）は、代わりに dataset を破棄することで削除されます。dataset の破棄はファイルフラグによってブロックされないため、この場合 `man chflags(1)` のステップは不要です。

```shell
# service jail stop classic
# zfs destroy zroot/jails/containers/cl
```

`-r` を追加すると、データセットが保持するスナップショットも破棄されます。

> **注:** テンプレートスナップショットのクローンによって作成された ZFS シンジャイル（Thin Jails 参照）は、そのスナップショットに依存します。クローンが存在する間、`man zfs(8)` はテンプレートスナップショットの破棄を拒否し、依存するクローンのリストを表示します。テンプレートを廃止するには、まずそれからクローンされたすべてのジャイルを破棄するか、クローン上で `zfs promote` を実行して、テンプレートに依存しないようにします。

最後に、どちらの場合でも、`/etc/jail.conf` または `/etc/jail.conf.d` からジャイルのエントリを削除します。NullFS シンジャイルの場合は、`.fstab` ファイルと、空になったマウントポイントディレクトリも削除してください。

### ジャイル内のパッケージを扱う

`man pkg(8)` ツールは、ジャイル内にインストールされたパッケージを扱うために `-j` 引数をサポートしています。

たとえば、`www/nginx-lite` パッケージをジャイルにインストールするには、*ホストから*次のコマンドを実行できます。

```shell
# pkg -j classic install nginx-lite
```

FreeBSD でのパッケージ操作の詳細については、ports の章の「Installing Applications: Packages and Ports」を参照してください。

### ホストからジャイル内のサービスを管理する

ジャイル内のサービスは、`man jexec(8)` でジャイルに入らずに、ホストから有効化および制御できます。`man service(8)` と `man sysrc(8)` はどちらも、ID または名前で対象のジャイルを指定する `-j` 引数を受け付け、そのジャイルの `man rc(8)` 設定を操作します。

上記のパッケージの例に続けて、`classic` ジャイル内の nginx をホストから直接有効化して起動します：

```shell
# sysrc -j classic nginx_enable=YES
# service -j classic nginx start
```

これらのコマンドは、`man jexec(8)` を介して `man sysrc(8)` と `man service(8)` を実行するのと同じ効果がありますが、ホスト側の管理とスクリプト作成を、ジャイル化されていないシステムと統一して行えます。

### ジャイルにアクセスする

前述のように、ジャイルの管理はホストシステムから行うのが最善ですが、`man jexec(8)` でジャイルに入ることもできます。

ホストから `man jexec(8)` を実行することでジャイルに入れます：

```shell
# jexec -u root jailname
```

`-u` フラグは、実行するユーザーを選択し、*ホスト*のパスワードデータベースに対して名前を解決します。代わりに *ジャイル* 自身のパスワードデータベースに対してユーザーを解決するには、`-U` を使用します。ここで示すようにコマンドが指定されていない場合、`man jexec(8)` はそのユーザーのログインシェルをジャイル内で起動します。`-l` を追加すると、`HOME`、`SHELL`、`TERM`、`USER` のみを保持し、`PATH` を `/bin:/usr/bin` にリセットして、新しいログインのように動作するクリーンなログイン環境で実行できます。`-d` は作業ディレクトリを設定し、デフォルトはジャイルのルートです。

ジャイルにアクセスすると、`man motd(5)` で設定されたメッセージが表示されます。

### ジャイル内でコマンドを実行する

ジャイル内でホストシステムからコマンドを実行するには、`man jexec(8)` を使用できます。

たとえば、ジャイル内で実行中のサービスを停止するには、次のコマンドを実行します：

```shell
# jexec -l jailname service nginx stop
```

### ホストからジャイル内のプロセスとソケットを表示する

ホストからは、すべてのジャイルのプロセスとソケットが見え、ジャイルごとにフィルタリングできます。

`man ps(1)` は `-J` を受け付け、JID または名前で指定された単一のジャイルに出力を制限します：

```shell
# ps -J classic
```

出力は次のようになります。`STAT` 列の `J` は、ジャイル内で実行中のプロセスを示します：

```text
 PID TT  STAT    TIME COMMAND
2841  -  IsJ  0:00.02 /usr/sbin/syslogd -ss
2903  -  IsJ  0:00.00 nginx: master process /usr/local/sbin/nginx
```

`ps -J 0` を使用すると、ホスト自身のプロセスのみが表示されます。`-o` 出力形式に `jail` キーワードと `jid` キーワードを追加して、各プロセスがどのジャイルに属しているかを表示することもできます。たとえば、ホスト上のすべてのプロセスを、そのジャイルと一緒に一覧表示するには、次のようにします：

```shell
# ps ax -o pid,jail,command
```

`man top(1)` は `-J` を指定すると、ライブ表示を 1 つのジャイルにフィルタリングし、`-j` を暗黙的に指定して `JID` 列を追加します：

```shell
# top -J classic
```

`man sockstat(1)` は、`-j` を指定するとジャイルに属するソケットを一覧表示します。これは、ジャイル内でサービスを起動した後、そのジャイルのデーモンが実際にバインドしたポートを確認する自然な方法です：

```shell
# sockstat -4 -6 -l -j classic
```

ジャイルの内部からは状況が逆転します。ジャイル内のプロセスは、自分自身のジャイルのプロセスとソケットだけが見え、ホストや他のジャイルのものは決して見えません。









自動的に、新しいバージョンは `<file>.pkgnew` として残され、以前はパッケージ化されていなかったファイルを引き継ぐ場合には、古いコピーが `<file>.pkgsave` として保存されます。アップグレード後に `/etc` を確認し、そのようなファイルを手動で調整してください。

pkgbase システムでは `man etcupdate(8)` を実行しないでください。`man pkg(8)` が設定ファイルのマージを処理します。

ホスト側のベースパッケージのワークフローについては、「Updating and Upgrading FreeBSD」を参照してください。

<a id="jail-resource-limits"></a>

## Jail Resource Limits（jail リソース制限）

ホストシステムから jail が使用するリソースを制御することは、システム管理者が考慮すべき業務です。

jail がホストシステムから使用できるリソースを管理するには、`man rctl(8)` を使用します。

> **ヒント:**
>
> `kern.racct.enable` チューナブルを /boot/loader.conf で有効にする必要があります。

jail のリソースを制限する構文は次のとおりです:

```
rctl -a jail:<jailname>:resource:action=amount[/per]
```

省略可能な `per` 要素はパーセンテージではなく、制限が適用される会計対象（accounting entity）であり、`process`、`user`、`loginclass`、`jail` のいずれかです。たとえば、`deny=2G/jail` は jail 全体の合計を制限し、`deny=2G/process` は同じ値を各プロセス個別に適用します。パーセンテージが意味を持つのは `pcpu` リソースだけであり、その量は単一 CPU コアに対するパーセンテージで表されます。

たとえば、jail がアクセスできる最大 RAM を制限するには、次のコマンドを実行します:

```shell
# rctl -a jail:classic:memoryuse:deny=2G
```

この制限をホストシステムの再起動後も持続させるには、ルールを /etc/rctl.conf ファイルに次のように追加する必要があります:

```
jail:classic:memoryuse:deny=2G/jail
```

`man rctl(8)` はメモリ以外にも多くのものを制限できます。jail に最も関連するリソースには、`pcpu`（単一 CPU コアのパーセンテージ）、`maxproc`（プロセス数）、`openfiles`（オープン中のファイルディスクリプタ数）、`vmemoryuse`（アドレス空間）、`swapuse`（スワップ領域）があります。それぞれは同じ方法で設定します:

```shell
# rctl -a jail:classic:pcpu:deny=80
# rctl -a jail:classic:maxproc:deny=1000
# rctl -a jail:classic:openfiles:deny=5000
# rctl -a jail:classic:vmemoryuse:deny=4G
```

ディスクスループットは `readbps` と `writebps` で制限しますが、これらのリソースは `deny` アクションをサポートしていません。代わりに `throttle` と組み合わせます:

```shell
# rctl -a jail:classic:writebps:throttle=1m
```

リソースの後のアクションは、制限に達したときに何が起こるかを選択します: `deny` は操作をブロックし、`log` はシステムログに記録し、`devctl` は `man devd(8)` を通じて通知を送ります。

`-u` フラグで jail の現在のリソース使用量を報告し、`-h` を追加すると人間が読みやすい単位になります:

```shell
# rctl -hu jail:classic
```

jail に適用されるルールを一覧表示します:

```shell
# rctl jail:classic
```

`-r` で jail に一致するすべてのルールを削除します:

```shell
# rctl -r jail:classic
```

リソース制限の詳細については、セキュリティ章の「Resource Limits（リソース制限）」セクションを参照してください。

## CPU Pinning with cpuset（cpuset による CPU 固定）

`pcpu` を指定した `man rctl(8)` は、jail が消費できる CPU 時間を制限しますが、jail を特定のコアに固定するわけではありません。代わりに `man cpuset(1)` が特定のコアを割り当てます。

実行中の jail を名前または JID で CPU セットに制限します:

```shell
# cpuset -l 0-3 -j classic
```

`-g` で jail が現在使用を許可されているコアを照会します:

```shell
# cpuset -g -j classic
```

割り当てられたセットは `jls -v` の cpuset 列にも表示されます。jail.conf には CPU アフィニティ用のパラメータがないため、ホスト環境で実行される `exec.created` または `exec.poststart` フックから `man cpuset(1)` を実行して、起動時に jail を固定します:

```
exec.poststart = "cpuset -l 0-3 -j classic";
```

## Limiting Disk Space（ディスク容量の制限）

`man rctl(8)` にはファイルシステム領域用のリソースがありません。各 jail が独自の ZFS dataset にある場合は、代わりに ZFS の quota（クォータ）と reservation（予約）でディスク使用量を制限・保証します:

```shell
# zfs set quota=20G zroot/jails/containers/classic
# zfs set reservation=5G zroot/jails/containers/classic
```

これには、jail が独自の dataset である必要があります。先ほど作成した ZFS thin jail はすでにそうですが、Classic Jail の手順では共有 `containers` dataset 内に `mkdir` で jail ディレクトリを作成するため、これらのコマンドを適用するにはまず `zfs create` で作成してください。dataset の構成については「Setting Up the Jail Directory Tree（jail ディレクトリツリーの設定）」を、`quota` と `reservation` プロパティについては `man zfs-set(8)` を参照してください。

<a id="jail-more-options"></a>



制限事項。

| 値 | 説明 |
|:---|:---|
| `1` | jail のルートディレクトリ以下のマウントポイントのみ。 |
| `2`（デフォルト） | jail のルートディレクトリが配置されている単一のマウントポイントのみ。 |

`allow.mount.*` 許可は `2` 未満の値を必要とするため、自身のファイルシステムをマウントする必要がある jail は、通常 `enforce_statfs = 1` で設定されます。

### Per-Jail securelevel {#per-jail-securelevel}

`securelevel` パラメータは、jail の `kern.securelevel` を設定し、jail 内のカーネルの immutable フラグとデバイス保護を強化します。
`man jail(8)` によれば、「jail は親システムよりも低い securelevel になることはありませんが、このパラメータを設定することで、より高い securelevel にすることができます」。
したがって、ネットワークに面した jail は、ホストがデフォルトのままでも、強化された `securelevel = 3` で実行できます。

### Hierarchical Jails {#hierarchical-jails}

jail はそれ自体が子 jail を作成できます。これが、ネストされた、または階層的な jail 階層が構築される仕組みです。
`children.max` パラメータは、jail が作成できる子 jail の数を設定します。デフォルトは `0` で、子 jail は許可されないことを意味し、読み取り専用の `children.cur` は現在存在する数を報告します。
子は親の権限を超えることはできません。`man jail(8)` によれば、「jail 内のプロセスは、自分自身に与えられた権限よりも大きな権限を付与することは許可されていません」。
これにより、jail 内で jail マネージャを実行することが可能になります。

### Empty and Persistent Jails {#empty-persistent-jails}

デフォルトでは、jail は実行中のプロセスがある間だけ存在し、最後のプロセスが終了すると jail は消滅します。
`persist` パラメータを設定すると、`man jail(8)` の言葉を借りれば、「プロセスなしで jail が存在できるようになります」。
これは、空の状態で作成されてから何かが投入されるまでの間、jail を存続させ、ネットワーク状態のみを保持する VNET jail を固定するものです。
jail を空で作成し、実験のために存続させることができます:

```shell
# jail -c name=test path=/rescue persist
```

`nopersist` でフラグを解除すると、再びアイドル状態になった jail が削除されるようになります。

### Presenting a Different OS Release {#jail-osrelease}

jail のユーザーランドはホストカーネルより古い場合がありますが、その中のツールは、特に指定がない限り、`man uname(1)` を通じてホストのバージョンを読み取ります。
`osrelease` パラメータは、jail の `kern.osrelease` と `uname -r` によって報告される文字列を設定し、`osreldate` は `kern.osreldate` と `uname -K` によって報告される数値を設定します。
古いユーザーランドが自身のリリースを報告するように設定すると、`man uname(1)`、`man sysctl(8)` の利用者、およびバージョンを検出するビルドツールが正しく動作し、jail 内で実行される `man freebsd-update(8)` も含めて正しく動作します。
パッケージ管理はどちらの場合でも影響を受けません。`man pkg(8)` は `man uname(1)` ではなく、jail 自身のバイナリの ELF ノートから ABI を導出するためです。
これは、jail のユーザーランドがホストカーネルより新しいことは決してないという規則を補完します。[Jail Upgrading](#jail-upgrading) を参照してください。

<a id="jails-zfs"></a>

---

## Jails と ZFS（Jails and ZFS）

jail に 1 つ以上の ZFS dataset の制御を与えることができます。これにより、jail 内の root ユーザーは、ホスト管理者の関与なしに、子 dataset の作成、スナップショット、クローン、ロールバックを行えます。これは、jail に独自の書き込み可能でスナップショット対応のストレージを提供するための推奨方法です。

ホストは dataset の所有権を保持し、委任されたツリーとその子孫の管理のみを jail に委任します。`jailed` プロパティ、`zfs jail`

## Jail マネージャーとコンテナ

前述のとおり、FreeBSD Jail の各タイプは手動で作成・設定できますが、設定と管理を容易にするためのサードパーティ製ユーティリティも存在します。

以下は、さまざまな FreeBSD Jail マネージャーの一覧です（不完全なリストです）。

.Jail マネージャー
[options="header", cols="1,1,1,1"]
|===
| 名称 | ライセンス | パッケージ | ドキュメント

| BastilleBSD
| BSD-3
| package:sysutils/bastille[]
| link:https://bastille.readthedocs.io/en/latest/[ドキュメント]

| pot
| BSD-3
| package:sysutils/pot[]
| link:https://pot.pizzamig.dev/[ドキュメント]

| cbsd
| BSD-2
| package:sysutils/cbsd[]
| link:https://github.com/cbsd/cbsd[ドキュメント]

| AppJail
| BSD-3
| package:sysutils/appjail[]、開発版は package:sysutils/appjail-devel[]
| link:https://github.com/DtxdF/AppJail#getting-started[ドキュメント]

| iocage
| BSD-2
| package:sysutils/iocage[]
| link:https://freebsd.github.io/iocage/[ドキュメント]

| ezjail
| link:https://erdgeist.org/beerware.html[Beer Ware]
| package:sysutils/ezjail[]
| link:https://erdgeist.org/arts/software/ezjail/[ドキュメント]

|===

FreeBSD は FreeBSD 14.3-RELEASE 以降、公式の OCI ベースシステムイメージを公開しています。OCI（Docker スタイル）コンテナは、同じ jail テクノロジー上に構築され、Podman ツールキットで管理されます。これらについては、本章で説明するネイティブ jail を補完するものとして、crossref:containers[containers,Containers] の章で説明しています。

---

## 翻訳メモ

- 機械支援初訳。コマンド例は原文照合推奨。
- 用語は `handbook/ja/glossary.md` と揃える。
