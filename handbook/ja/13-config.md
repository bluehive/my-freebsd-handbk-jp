<a id="config-tuning"></a>
# 第13章 設定・サービス・ログ・電源管理

FreeBSDの設定ファイル、サービスの起動、定期処理、ログ管理、省電力設定、スワップの追加を説明します。機種や運用目的に応じて設定を選び、例の値を一律に適用しないようにしてください。

<a id="config-synopsis"></a>
## 概要

適切なシステム設定はFreeBSDの運用の基本です。本章では設定方法と、動作を調整するための主なパラメータを説明します。[FreeBSDの基本](03-basics.md)を理解してから読むと役立ちます。

本章では、`/etc` 以下の設定ファイル、`rc.conf` と `/usr/local/etc/rc.d` の起動スクリプト、`sysctl(8)` による調整、電源管理を学びます。

<a id="configtuning-configfiles"></a>
## 設定ファイルの配置

FreeBSDは基本システムと追加アプリケーションを明確に分けています。この区別は設定ファイルの場所にも表れます。基本システムの設定は `/etc`、Portsやパッケージで追加したソフトウェアの設定は通常 `/usr/local/etc` に置かれます。

カーネルの実行時設定を起動時に適用するファイルは `/etc/sysctl.conf` です。仕組みは[sysctl](#configtuning-sysctl)で説明します。ディレクトリ構成の全体像は `hier(7)` を参照してください。

設定ファイルの構文には、全ソフトウェア共通の規格があるわけではありません。`#` をコメントに使い、一行ごとに変数を指定する形式はよく使われますが、個々のマニュアルを確認してください。`pkg(8)` などでは [Universal Configuration Language（UCL）](https://github.com/vstakhov/libucl)も使われています。

<a id="chapter-13-heading-04"></a>
### /etcディレクトリ

`/etc` は基本システムの設定を保持します。**誤った変更によって正常動作や起動ができなくなることもあるため、十分注意してください。**

| パス | 内容 |
|---|---|
| `/etc` | システム設定ファイルとスクリプト。 |
| `/etc/defaults` | 既定の設定。`rc(8)` を参照。 |
| `/etc/fstab` | ファイルシステムの構成情報。`fstab(5)` を参照。 |
| `/etc/mail` | `sendmail(8)` の追加設定や、ほかのMTAの設定。 |
| `/etc/mtree` | ディレクトリ階層の検査などに使う `mtree(8)` の設定。 |
| `/etc/pam.d` | PAM（Pluggable Authentication Modules）の設定。 |
| `/etc/periodic` | cron経由で日次・週次・月次に実行するスクリプト。`periodic(8)` を参照。 |
| `/etc/rc.d` | システムやデーモンの起動・制御スクリプト。`rc(8)` を参照。 |
| `/etc/rc.conf` | ホスト名、ネットワークインターフェース、起動するサービスなど。[個別設定](#configtuning-core-configuration)を参照。 |
| `/etc/security` | OpenBSMによる監査の設定。`audit(8)` を参照。 |
| `/etc/ppp` | `ppp(8)` の設定。 |
| `/etc/ssh` | OpenSSHの設定。`ssh(1)` を参照。 |
| `/etc/ssl` | OpenSSLの設定。 |
| `/etc/sysctl.conf` | カーネルの設定。[sysctl](#configtuning-sysctl)を参照。 |

<a id="configtuning-sysctl"></a>
### sysctlでカーネルの状態を調べる・変更する

`sysctl(8)` は稼働中のカーネルの状態を読み取り、適切な権限があれば変更も行う道具です。項目名はManagement Information Base（MIB）形式の階層で、要素をドットで区切ります。

| 最上位の名前 | 主な内容 |
|---|---|
| `sysctl` | MIB自身の管理情報、いわゆる「マジックナンバー」。 |
| `kern` | カーネルの機能。 |
| `vm` | 仮想メモリ。 |
| `vfs` | ファイルシステム。 |
| `net` | ネットワーク。 |
| `debug` | デバッグ用パラメータ。 |
| `hw` | ハードウェア。 |
| `machdep` | 機種依存の情報。 |
| `user` | ユーザーランド。 |
| `p1003_1b` | POSIX 1003.1B関連。 |

読み取り可能な項目をまとめて表示するには、次を実行します。

```shell
% sysctl -a
```

出力例です。表示される項目や値はシステムによって異なります。

```text
kern.ostype: FreeBSD
...
vm.swap_enabled: 1
vm.overcommit: 0
vm.domain.0.pidctrl.kdd: 8
vm.domain.0.pidctrl.kid: 4
vm.domain.0.pidctrl.kpd: 3
...
vfs.zfs.sync_pass_rewrite: 2
vfs.zfs.sync_pass_dont_compress: 8
vfs.zfs.sync_pass_deferred_free: 2
```

一つの項目だけを読むには、名前を指定します。

```shell
% sysctl kern.maxproc
```

```text
kern.maxproc: 1044
```

階層の途中までを指定すると、その下の項目を表示できます。

```shell
% sysctl net
```

```text
net.local.stream.recvspace: 8192
net.local.stream.sendspace: 8192
net.local.dgram.recvspace: 16384
net.local.dgram.maxdgram: 2048
net.local.seqpacket.recvspace: 8192
net.local.seqpacket.maxseqpacket: 8192
net.local.sockcount: 60
net.local.taskcount: 25
net.local.recycled: 0
net.local.deferred: 0
net.local.inflight: 0
net.inet.ip.portrange.randomtime: 1
net.inet.ip.portrange.randomcps: 9999
[...]
```

値を変更するには `変数名=値` の形で指定します。

```shell
# sysctl kern.maxfiles=5000
```

```text
kern.maxfiles: 2088 -> 5000
```

この変更を再起動後も適用したい場合は、次節の `/etc/sysctl.conf` に記録します。ただし、すべての項目が実行時に変更できるわけではありません。

<a id="configtuning-sysctlconf"></a>
### /etc/sysctl.confで起動時の値を指定する

`/etc/sysctl.conf` は `変数名=値` の形式で設定します。原文はマルチユーザーモードへ移行した後に値が設定されると説明しています。この段階では変更できない項目もあるため、各項目の説明を確認してください。

次は、致命的シグナルによる終了の記録を抑え、異なるUIDのプロセス情報を一般ユーザーから見えなくする例です。運用上必要な可視性や記録に影響するので、目的に応じて選びます。

```shell
# Do not log fatal signal exits (e.g., sig 11)
kern.logsigexit=0

# Prevent users from seeing information about processes that
# are being run under another UID.
security.bsd.see_other_uids=0
```

項目の意味を表示するには `-d` を使います。

```shell
% sysctl -d kern.dfldsiz
```

```text
kern.dfldsiz: Initial data size limit
```

<a id="configtuning-core-configuration"></a>
### システム固有の設定を管理する

`/etc/rc.conf` は、起動時の設定の中心となるファイルです。`rc*` スクリプトが参照し、`/etc/defaults/rc.conf` の既定値を上書きします。**`/etc/defaults/rc.conf` は直接編集せず、個別の変更は `/etc/rc.conf` に書きます。**

複数台を管理する場合、共通設定とホスト固有設定を分けると保守が容易になります。原文は、固有設定を `/etc/rc.conf.local` に置く方法を勧めています。たとえば、すべてのホストに共通の `/etc/rc.conf` は次のようにします。

```text
sshd_enable="YES"
keyrate="fast"
defaultrouter="10.1.1.254"
```

ホストごとの `/etc/rc.conf.local` には、次のような値を置きます。ホスト名・インターフェース名・アドレスは環境に合わせてください。

```text
hostname="node1.example.org"
ifconfig_fxp0="inet 10.1.1.1/8"
```

共通ファイルをrsyncやPuppetなどで配布し、`.local` は各ホストで管理します。`/etc/rc.conf` はシステムのアップグレードで既定値へ置き換えるためのファイルではなく、ローカル設定を維持するためのものです。

両ファイルは `sh(1)` で解釈されるため、シェル構文による柔軟な設定も可能です。詳細は `rc.conf(5)` を参照してください。

<a id="configtuning-rcd"></a>
## FreeBSDのサービスを管理する

FreeBSDは起動時の初期化やサービス管理に `rc(8)` のスクリプトを使います。`/etc/rc.d` の基本サービスは、`service(8)` の `start`、`stop`、`restart` などで制御できます。追加ソフトウェアのスクリプトは通常 `/usr/local/etc/rc.d` に配置されます。

基本的なスクリプトの例です。

```text
#!/bin/sh
#
# PROVIDE: utility
# REQUIRE: DAEMON
# KEYWORD: shutdown

. /etc/rc.subr

name=utility
rcvar=utility_enable

command="/usr/local/sbin/utility"

load_rc_config $name

#
# DO NOT CHANGE THESE DEFAULT VALUES HERE
# SET THEM IN THE /etc/rc.conf FILE
#
utility_enable=${utility_enable-"NO"}
pidfile=${utility_pidfile-"/var/run/utility.pid"}

run_rc_command "$1"
```

独自のrcスクリプトを作る方法は、[rcスクリプトの解説記事](https://docs.freebsd.org/en/articles/rc-scripting/)を参照してください。

<a id="configtuning-starting-services"></a>
### サービスを起動する

Portsから追加した `security/openssh-portable` や `www/nginx` などのサービスも、起動時に自動実行できます。通常の `start`、`stop`、`restart` は、対応する有効化変数が `/etc/rc.conf` などで設定されている場合に動作します。

nginxを有効にする例です。

```shell
# sysrc nginx_enable="YES"
```

これで起動時の対象になります。今すぐ起動するには次を実行します。

```shell
# service nginx start
```

有効化設定によらず一度だけ実行したい場合は、操作名の前に `one` を付けます。たとえば次は起動だけを行い、起動時の有効化設定は変更しません。

```shell
# service nginx onestart
```

`onestop`、`onerestart` も同様です。また、サービスを自動的にjail内へ入れる仕組みは[Service Jail](16-jails.md#service-jails)で説明しています。

<a id="configtuning-status-services"></a>
### サービスの状態を確認する

`status` で実行状態を確認できます。nginxの例です。

```shell
# service nginx status
```

次のように表示されます。PIDは実行ごとに異なります。

```text
nginx is running as pid 27871.
```

<a id="configtuning-reload-services"></a>
### 設定を再読み込みする

対応するサービスでは `reload` を使い、プロセスへシグナルを送って設定ファイルの再読み込みを要求できます。多くの場合は `SIGHUP` を使いますが、**すべてのサービスが対応するわけではありません**。

rcの役割はネットワークサービスだけではなく、システム初期化全般に及びます。たとえば `/etc/rc.d/bgfsck` は、起動時のバックグラウンドファイルシステム検査に際して次のメッセージを表示します。

```text
Starting background file system checks in 60 seconds.
```

また、サービスには起動順の依存関係があります。`yp(8)` などのRPCを使うサービスは、`rpcbind(8)` が起動していないと正しく開始できないことがあります。詳細は `rc(8)` と `rc.subr(8)` を参照してください。

<a id="chapter-13-heading-12"></a>
### ほかの仕組みでサービスを起動する

`inetd(8)` を通じて起動するサービスもあります。設定方法は[inetdスーパーサーバ](https://docs.freebsd.org/en/books/handbook/network-servers/#network-inetd)を参照してください。

用途によっては `cron(8)` が適する場合もあります。ユーザーcrontabの所有者として実行されるため、一般ユーザーも自分のアプリケーションを管理できます。時刻指定の代わりに `@reboot` を使うと、cronが起動したとき、通常はシステム起動時に実行されます。

<a id="cron-periodic"></a>
## cronとperiodicによる定期処理

日時を指定した処理には `cron(8)` を使います。FreeBSDには、保守や確認のための定期的なバックグラウンド処理をまとめた `periodic(8)` も用意されています。

<a id="configtuning-cron"></a>
### cronの仕組み

cronはバックグラウンドで動作し、システム用の `/etc/crontab` と `/var/cron/tabs` 内のユーザーcrontabを調べ、指定時刻に処理を実行します。一つの実行指定を **cronジョブ** と呼びます。

システムcrontabとユーザーcrontabでは書式が異なります。前者には実行ユーザーを指定する `who` 列がありますが、後者にはなく、作成したユーザーとして実行されます。`root` も自分用のユーザーcrontabを持てます。独自の処理を追加するときは、標準のシステムcrontabを編集するのではなく、ユーザーcrontabを使います。書式の詳細は `crontab(5)` を参照してください。

以下は原文の `/etc/crontab` の例です。

```shell
# /etc/crontab - root's crontab for FreeBSD
#
#
#
SHELL=/bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
#
#minute hour    mday    month   wday    who     command
#
# Save some entropy so that /dev/random can re-seed on boot.
*/11    *       *       *       *       operator /usr/libexec/save-entropy
#
# Rotate log files every hour, if necessary.
0       *       *       *       *       root    newsyslog
#
# Perform daily/weekly/monthly maintenance.
1       3       *       *       *       root    periodic daily
15      4       *       *       6       root    periodic weekly
30      5       1       *       *       root    periodic monthly
#
# Adjust the time zone if the CMOS clock keeps local time, as opposed to
# UTC time.  See adjkerntz(8) for details.
1,31    0-5     *       *       *       root    adjkerntz -a
```

- `#` で始まる行はコメントです。コマンド行末にコメントを書いても、その一部として解釈されるため、コメントは別行にします。空行は無視されます。
- `=` で環境変数を指定します。例では `SHELL` と `PATH` を設定しています。`SHELL` を省くと既定のPOSIXシェルを使います。コマンド探索を暗黙に期待せず、必要な `PATH` または絶対パスを指定してください。
- システムcrontabの列は、分・時・日・月・曜日・実行ユーザー・コマンドです。時刻は24時間制で、`*` はその欄のすべての値を表します。ユーザーcrontabでは実行ユーザーの列を省きます。
- `*/11` の例では、毎時の分欄を11刻みで指定し、`operator` として `/usr/libexec/save-entropy` を実行します。分は `0,11,22,33,44,55` なので、時をまたいでも常に厳密な11分間隔になるわけではありません。

原文は長いコマンドをバックスラッシュで継続する説明もしています。複雑な処理はスクリプトへ分け、使用するcronの `crontab(5)` で改行などの扱いを確認してください。

<a id="configtuning-installcrontab"></a>
### ユーザーcrontabを作成する

編集モードで起動します。

```shell
% crontab -e
```

既定のエディタで開きます。初回は空で、以後は登録済みの内容が表示されます。冒頭に実行環境と列の意味を書いておくと分かりやすくなります。

```text
SHELL=/bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
# Order of crontab fields
# minute hour mday month wday command
```

次は毎日14時に自作スクリプトを実行する例です。スクリプトの場所は `PATH` にないため絶対パスを使います。

```text
0 14 * * * /home/user/bin/mycustomscript.sh
```

スクリプトには実行権限を付け、cronの限られた環境でも正しく動くかを事前に試します。原文では次のように環境を絞る例を示しています。これは上の `PATH` と完全に同一ではないため、実際に登録する環境に合わせて確認してください。

```text
env -i SHELL=/bin/sh PATH=/etc:/bin:/sbin:/usr/bin:/usr/sbin HOME=/home/user LOGNAME=user /home/user/bin/mycustomscript.sh
```

環境の詳細は `crontab(5)` を参照してください。ワイルドカードでファイルを削除する処理は、とくに慎重な確認が必要です。

編集を保存するとcrontabが登録され、指定時刻に実行されます。登録内容の一覧は次で表示します。

```shell
% crontab -l
```

```text
0 14 * * * /home/user/bin/mycustomscript.sh
```

そのユーザーのジョブを**すべて削除する**コマンドは次です。

```shell
% crontab -r
```

原文の確認表示例です。

```text
remove crontab for user? y
```

<a id="configtuning-periodic"></a>
### periodicによる保守処理

サブシステムの状態確認、セキュリティ検査、ログ関連の保守などを、日次・週次・月次で実行するスクリプト群です。`periodic(8)` が管理し、設定は `periodic.conf(5)` に従います。先のシステムcrontabから呼び出されます。

基本システムのスクリプトは `/etc/periodic/`、追加ソフトウェアのものは `/usr/local/etc/periodic/` にあり、`daily`、`weekly`、`monthly`、`security` の各サブディレクトリに分類されます。

<a id="enable-disable-periodic"></a>
### 定期処理を有効・無効にする

既定で有効な処理もあります。設定を変えるには `/etc/periodic.conf` を編集します。

```shell
# ee /etc/periodic.conf
```

たとえばZFSの状態報告を有効にするには次を記載します。

```text
daily_status_zfs_enable="YES"
```

既定で有効な項目を無効にしたい場合は、対象の値を `NO` にします。

<a id="configuring-output-periodic-tasks"></a>
### periodicの出力先を指定する

`/etc/periodic.conf` の `daily_output`、`weekly_output`、`monthly_output` で結果の送付先を指定します。既定ではroot宛てのメールになるため、rootのメールを読むか、監視しているメールボックスへ転送する必要があります。

別の宛先へ送る場合は、アドレスを空白区切りで指定します。

```text
daily_output="email1@example.com email2@example.com"
weekly_output="email1@example.com email2@example.com"
monthly_output="email1@example.com email2@example.com"
```

メールではなくログに保存する場合は、次のようにパスを指定します。これらのファイルは `newsyslog(8)` の設定に従ってローテーションされます。

```text
daily_output=/var/log/daily.log
weekly_output=/var/log/weekly.log
monthly_output=/var/log/monthly.log
```

<a id="configtuning-syslog"></a>
## システムログを設定する

ログは、ハードウェアやソフトウェアの問題、設定の誤りを発見するための重要な情報です。セキュリティ監査やインシデント対応にも役立ち、多くのデーモンやアプリケーションが記録を生成します。

FreeBSDでは `syslogd(8)` がシステムのログを扱い、既定では起動時に有効になります。本節ではローカル保存、別ホストへの転送、ローテーションを説明します。

<a id="chapter-13-heading-20"></a>
### ローカルのログを設定する

`/etc/syslog.conf` は、受信したメッセージをどう扱うかを指定するファイルです。**facility**はカーネルやメールなどの発生元の分類、**level**は重要度を表します。アプリケーション名や、リモート記録では発生元ホスト名を使う条件指定もできます。

一行は「選択条件」と「処理先」からなります。基本の条件は `facility.level` で、指定した分類の、その重要度**以上**のメッセージに一致します。重要度の前へ比較記号を置けば、範囲をより厳密に指定できます。同じ処理先へ複数の条件を適用するには `;` で区切り、`*` はすべてに一致します。処理先にはファイルやリモートのログホストなどを指定します。

原文に掲載された既定設定の例です。

```shell
#       Spaces ARE valid field separators in this file. However,
#       other *nix-like systems still insist on using tabs as field
#       separators. If you are sharing this file between systems, you
#       may want to use only tabs as field separators here.
#       Consult the syslog.conf(5) manpage.
*.err;kern.warning;auth.notice;mail.crit                /dev/console
*.notice;authpriv.none;kern.debug;lpr.info;mail.crit;news.err   /var/log/messages
security.*                                      /var/log/security
auth.info;authpriv.info                         /var/log/auth.log
mail.info                                       /var/log/maillog
cron.*                                          /var/log/cron
!-devd
*.=debug                                        /var/log/debug.log
*.emerg                                         *
daemon.info                                     /var/log/daemon.log
# uncomment this to log all writes to /dev/console to /var/log/console.log
# touch /var/log/console.log and chmod it to mode 600 before it will work
#console.info                                   /var/log/console.log
# uncomment this to enable logging of all log messages to /var/log/all.log
# touch /var/log/all.log and chmod it to mode 600 before it will work
#*.*                                            /var/log/all.log
# uncomment this to enable logging to a remote loghost named loghost
#*.*                                            @loghost
# uncomment these if you're running inn
# news.crit                                     /var/log/news/news.crit
# news.err                                      /var/log/news/news.err
# news.notice                                   /var/log/news/news.notice
# Uncomment this if you wish to see messages produced by devd
# !devd
# *.>=notice                                    /var/log/devd.log
!*
include                                         /etc/syslog.d
include                                         /usr/local/etc/syslog.d
```

`*.err;kern.warning;auth.notice;mail.crit` は、すべての分類のerr以上に加え、kernのwarning以上、authのnotice以上、mailのcrit以上をコンソールへ送ります。`mail.info` はメール関連のinfo以上を `/var/log/maillog` へ保存します。`*.=debug` の `=` はdebug**だけ**を選びます。

`!devd` は、後続のルールの対象をdevdに限定するプログラム指定の例です。掲載例ではコメントになっているため、記録するには関連する行を有効にします。詳細と高度な条件指定は `syslog.conf(5)` を参照してください。

<a id="logging-facilities"></a>
### facility：発生元の分類

facilityで記録の発生元を分けると、目的のログを探しやすくなります。

| 名前 | 内容 |
|---|---|
| `auth` | `login(1)`、`su(1)`、`getty(8)` などの認証・認可関連。 |
| `authpriv` | authと同種の情報。rootだけが読めるファイルへ記録するための分類。実際の保護は保存先の設定にも依存します。 |
| `console` | カーネルのコンソール出力ドライバが `/dev/console` へ書くメッセージ。 |
| `cron` | cronデーモンのメッセージ。 |
| `daemon` | `routed(8)` など、専用分類のないシステムデーモン。 |
| `ftp` | `ftpd(8)`、`tftpd(8)` などのファイル転送デーモン。 |
| `kern` | カーネル由来のメッセージ。原文ではユーザープロセスの生成する分類と区別しています。 |
| `lpr` | `lpr(1)`、`lpc(8)`、`lpd(8)` などの印刷スプーラ。 |
| `mail` | メールシステム。 |
| `mark` | 定期的な目印。原文では20分ごとの記録と説明しています。 |
| `news` | ネットニュース。 |
| `ntp` | ネットワーク時刻同期。 |
| `security` | `ipfw(4)` などのセキュリティ関連。 |
| `syslog` | syslogd自身の内部メッセージ。 |
| `user` | 一般のユーザープロセス。分類を省略したときの既定値。 |
| `uucp` | 旧来のUnix-to-Unix Copy。現在では見かける機会が少ない分類。 |
| `local0`〜`local7` | ローカルな用途のために予約された分類。 |

<a id="logging-levels"></a>
### level：メッセージの重要度

重要度は次の順で高いものから低いものへ並びます。`none` は通常の重要度ではなく、指定分類を除外するための特別な値です。

| 名前 | 内容 |
|---|---|
| `emerg` | システムが利用できないような緊急状態。通常は全ユーザーへ通知されます。 |
| `alert` | システムデータベースの破損など、直ちに対処すべき状態。 |
| `crit` | 重大なデバイスエラーなどの危機的状態。 |
| `err` | エラー。 |
| `warning` | 警告。 |
| `notice` | エラーではないが、特別な対応が必要になる可能性のある状態。 |
| `info` | 情報通知。 |
| `debug` | 主にプログラムのデバッグに役立つ情報。 |
| `none` | 特定のfacilityを記録対象から除外する指定。 |

<a id="read-log-messages"></a>
### ログを読む

FreeBSDの既定のログ形式は、原文では [RFC 3164（BSD syslog Protocol）](https://datatracker.ietf.org/doc/html/rfc3164)として説明されています。ほかの形式や設定は `syslogd(8)` を参照してください。典型的には次の形です。

```text
date time hostname program[pid]: the message
```

`/var/log/cron` の例では、日時、ホスト名、実行プログラムとPID、メッセージが並びます。

```text
[...]
Jul 16 12:40:00 FreeBSD /usr/sbin/cron[81519]: (root) CMD (/usr/libexec/atrun)
Jul 16 12:44:00 FreeBSD /usr/sbin/cron[83072]: (operator) CMD (/usr/libexec/save-entropy)
[...]
```

facilityとlevelも記録したい場合は、syslogdの詳細表示オプションを設定します。

```shell
# sysrc syslogd_flags="-vv"
```

このコマンドは起動時の設定を変更するので、稼働中のsyslogdへ反映するには再起動も必要です。有効になった後は、次のように `<cron.info>` が付加されます。

```text
[...]
Jul 16 17:40:00 <cron.info> FreeBSD /usr/sbin/cron[1016]: (root) CMD (/usr/libexec/atrun)
Jul 16 17:44:00 <cron.info> FreeBSD /usr/sbin/cron[1030]: (operator) CMD (/usr/libexec/save-entropy)
[...]
```

<a id="chapter-13-heading-24"></a>
### ログを管理・ローテーションする

増え続けるログは容量を消費し、必要な情報も探しにくくなります。`newsyslog(8)` はファイルを定期的に切り替え、圧縮し、必要に応じて未作成のログを作成したり、書き込み元のプログラムへ通知したりします。

newsyslog自体はcronから呼び出されるため、呼び出し間隔より頻繁な処理はできません。既定では毎時実行されます。原文の設定例です。

```shell
# configuration file for newsyslog
#
# Entries which do not specify the '/pid_file' field will cause the
# syslogd process to be signalled when that log file is rotated.  This
# action is only appropriate for log files which are written to by the
# syslogd process (ie, files listed in /etc/syslog.conf).  If there
# is no process which needs to be signalled when a given log file is
# rotated, then the entry for that file should include the 'N' flag.
#
# Note: some sites will want to select more restrictive protections than the
# defaults.  In particular, it may be desirable to switch many of the 644
# entries to 640 or 600.  For example, some sites will consider the
# contents of maillog, messages, and lpd-errs to be confidential.  In the
# future, these defaults may change to more conservative ones.
#
# logfilename          [owner:group]    mode count size when  flags [/pid_file] [sig_num]
/var/log/all.log                        600  7     *    @T00  J
/var/log/auth.log                       600  7     1000 @0101T JC
/var/log/console.log                    600  5     1000 *     J
/var/log/cron                           600  3     1000 *     JC
/var/log/daily.log                      640  7     *    @T00  JN
/var/log/debug.log                      600  7     1000 *     JC
/var/log/init.log                       644  3     1000 *     J
/var/log/kerberos.log                   600  7     1000 *     J
/var/log/maillog                        640  7     *    @T00  JC
/var/log/messages                       644  5     1000 @0101T JC
/var/log/monthly.log                    640  12    *    $M1D0 JN
/var/log/devd.log                       644  3     1000 *     JC
/var/log/security                       600  10    1000 *     JC
/var/log/utx.log                        644  3     *    @01T05 B
/var/log/weekly.log                     640  5     *    $W6D0 JN
/var/log/daemon.log                     644  5     1000 @0101T JC

<include> /etc/newsyslog.conf.d/[!.]*.conf
<include> /usr/local/etc/newsyslog.conf.d/[!.]*.conf
```

各列の意味は次のとおりです。

- `logfilename`：対象のログファイル名。
- `[owner:group]`：任意指定の所有者とグループ。
- `mode`：ログとアーカイブのアクセス権。所有者・グループ・その他への読み書き権を指定します。原文の「0666」は読み書きに使うビットの範囲を示し、全ファイルを0666にする推奨ではありません。
- `count`：保存するアーカイブの最大数。
- `size`：サイズによる切り替えのしきい値（キロバイト）。`*` はサイズを条件にしません。
- `when`：時間間隔、特定の時刻、またはその組み合わせ。
- `flags`：圧縮方法やファイル作成などの指定。
- `[/pid_file]`：必要なら、通知対象のデーモンやプロセスグループを特定するPIDファイル。
- `[sig_num]`：必要なら、切り替え時に送るシグナル番号。

後ろの二列は省略可能です。書式やフラグの詳細は `newsyslog.conf(5)` を参照してください。

<a id="network-syslogd"></a>
### リモートのログを集約する

台数が増えると、各ホストのログを個別に読むのは大変です。syslogdとnewsyslogを使って、一か所に収集し、保存・ローテーションを管理できます。

以下は、ホストAの `logserv.example.com` を収集サーバ、ホストBの `logclient.example.com` を送信クライアントとする例です。ホスト名やネットワーク設定は自分の環境へ置き換えてください。

<a id="chapter-13-heading-26"></a>
#### ログサーバを設定する

事前に、クライアントからサーバのUDP 514番ポートへの通信を、間にあるファイアウォールも含めて許可します。また、両者の正引き・逆引きができるよう、DNSまたは各ホストの `/etc/hosts` を整えます。名前が食い違うと受信を拒否する原因になります。

サーバ側の `/etc/syslog.conf` へ、受信元と保存先を記載します。次はBからの全facilityを `/var/log/logclient.log` へ保存する例です。

```text
+logclient.example.com
*.*     /var/log/logclient.log
```

複数クライアントを分けて保存する場合は、対応する二行を追加します。条件指定の詳細は `syslog.conf(5)` を参照してください。

続いてサービスと許可する送信元を設定します。

```shell
# sysrc syslogd_enable="YES"
# sysrc syslogd_flags="-a logclient.example.com -v -v"
```

`-a` は許可するクライアントを指定し、`-v -v` はfacilityとlevelを表示して、分類の確認を容易にします。`-a` は複数指定でき、IPアドレスやネットワーク範囲も使えます。詳細は `syslogd(8)` を参照してください。

保存先を作成します。ログの機密性に応じた所有者とアクセス権も設定してください。

```shell
# touch /var/log/logclient.log
```

再起動し、プロセスを確認します。

```shell
# service syslogd restart
# pgrep syslog
```

PIDが返ることは稼働確認の手掛かりですが、実際の受信は後述のテストでも確かめます。起動しない場合は `/var/log/messages` のエラーを調べてください。

<a id="chapter-13-heading-27"></a>
#### ログクライアントを設定する

クライアントは自分のログをローカルにも残しながら、サーバへ転送します。サーバの準備ができたら、クライアントで次を設定します。

```shell
# sysrc syslogd_enable="YES"
# sysrc syslogd_flags="-s -v -v"
```

`-s` は他ホストのログを受け付けない指定、`-v -v` は詳細表示です。次に `/etc/syslog.conf` に転送先を追加します。`@` はリモートホストを表します。

```text
*.*  @logserv.example.com
```

変更を反映します。

```shell
# service syslogd restart
```

`logger(1)` でテストメッセージを送ります。

```shell
# logger "Test message from logclient"
```

クライアントの `/var/log/messages` と、サーバの `/var/log/logclient.log` の両方に記録されたことを確認します。

<a id="chapter-13-heading-28"></a>
#### ログ転送の問題を調べる

受信できないときは、ネットワーク、名前解決、設定の誤記を切り分けます。まず、`/etc/rc.conf` に設定したホスト名で互いに `ping` できるかを調べ、配線、ファイアウォール、DNSや `/etc/hosts` の内容を確認します。ただし、ICMPを制限する環境ではpingの成否だけでUDPログ転送の可否は断定できません。

名前解決や疎通が確認できてもログが届かない場合は、サーバ側で一時的にデバッグ出力を増やします。

```text
sysrc syslogd_flags="-d -a logclient.example.com -v -v"
```

```shell
# service syslogd restart
```

再起動すると、コンソールに次のような情報が表示されます。

```text
logmsg: pri 56, flags 4, from logserv.example.com, msg syslogd: restart
syslogd: restarted
logmsg: pri 6, flags 4, from logserv.example.com, msg syslogd: kernel boot file is /boot/kernel/kernel
Logging to FILE /var/log/messages
syslogd: kernel boot file is /boot/kernel/kernel
cvthname(192.168.1.10)
validate: dgram from IP 192.168.1.10, port 514, name logclient.example.com;
rejected in rule 0 due to name mismatch.
```

この例の `name mismatch` は、設定した名前と受信元の名前が一致していないことを示します。原文本文は `logclien` と `logclient` の誤記を例に挙げていますが、掲載出力には誤記箇所自体は表示されていません。実際の許可設定と名前解決の結果を照合して直します。

```shell
# service syslogd restart
```

修正後の例です。

```text
logmsg: pri 56, flags 4, from logserv.example.com, msg syslogd: restart
syslogd: restarted
logmsg: pri 6, flags 4, from logserv.example.com, msg syslogd: kernel boot file is /boot/kernel/kernel
syslogd: kernel boot file is /boot/kernel/kernel
logmsg: pri 166, flags 17, from logserv.example.com,
msg Dec 10 20:55:02 <syslog.err> logserv.example.com syslogd: exiting on signal 2
cvthname(192.168.1.10)
validate: dgram from IP 192.168.1.10, port 514, name logclient.example.com;
accepted in rule 0.
logmsg: pri 15, flags 0, from logclient.example.com, msg Dec 11 02:01:28 trhodes: Test message 2
Logging to FILE /var/log/logclient.log
Logging to FILE /var/log/messages
```

`accepted` と保存先の表示を確認し、実際にファイルへ記録されていることを確かめます。調査が終わったら、不要なデバッグ出力を戻します。

<a id="chapter-13-heading-29"></a>
#### ログ収集のセキュリティ

ログにはサービス、ユーザー、システム設定などの機密情報が含まれることがあります。この例のネットワーク転送には暗号化もパスワードによる保護もありません。原文は暗号化が必要な場合に `security/stunnel` を検討するよう述べていますが、これはUDPの例へ導入するだけで暗号化されるという意味ではなく、トンネルに対応する転送構成を別途設計する必要があります。

保存したログやローテーション後のアーカイブも、自動的には暗号化されません。ローカルユーザーが読むことのできる範囲を、適切な所有者とアクセス権で制限します。newsyslogは新規・切り替え後のファイルの権限を設定できます。所有者だけに読み書きを許可するなら `600` が一つの設定です。詳細は `newsyslog.conf(5)` を参照してください。

<a id="acpi-overview"></a>
## 電源とハードウェア資源の管理

ハードウェア資源を効率よく使うには、電源状態や温度、負荷などを把握することが大切です。電源・資源管理の機能は、システムの状態や制限を監視し、関連するイベントに応じて動作を変えるために使われます。

<a id="acpi-config"></a>
### ACPIの設定

FreeBSDでは `acpi(4)` が電源やハードウェア資源の管理を担います。対応するシステムでは通常、起動時に読み込まれます。システムバスが各種ハードウェアとのやり取りに利用するため、**起動後にアンロードできません**。

メーカー固有のACPI機能には追加モジュールがあり、ファン、キーボードのバックライト、画面の明るさなどの機能を提供する場合があります。モジュールの一覧を調べる例です。

```shell
% ls /boot/kernel | grep acpi
```

```text
acpi_asus.ko
acpi_asus_wmi.ko
acpi_dock.ko
acpi_fujitsu.ko
acpi_hp.ko
acpi_ibm.ko
acpi_panasonic.ko
acpi_sony.ko
acpi_toshiba.ko
acpi_video.ko
acpi_wmi.ko
sdhci_acpi.ko
uacpi.ko
```

対応するIBM/LenovoのノートPCで `acpi_ibm(4)` を読み込む例です。どのモジュールが適切かは機種ごとに確認します。

```shell
# kldload acpi_ibm
```

起動時にも読み込むには `/boot/loader.conf` に追加します。

```text
acpi_ibm_load="YES"
```

画面の明るさには `acpi_video(4)` のほか、汎用の `backlight(9)` ドライバもあります。GENERICカーネルに含まれ、対応する機器では `backlight(8)` で照会・調整できます。次は明るさを10%下げる原文の例です。

```shell
% backlight decr 10
```

<a id="cpu-power-management"></a>
### CPUの電力管理

CPUは消費電力の大きい部品の一つです。FreeBSDは `powerd(8)` や `cpufreq(4)` などを通じて、Intel Turbo Boost、AMD Turbo Core、Intel Speed Shiftなどの仕組みを扱います。利用できる機能はCPUとドライバによって異なります。

まずCPUの情報を調べます。ここで `0` は最初のCPUデバイスを示します。

```shell
% sysctl dev.cpu.0
```

```text
dev.cpu.0.cx_method: C1/mwait/hwc C2/mwait/hwc C3/mwait/hwc/bma
dev.cpu.0.cx_usage_counters: 3507294 0 0
dev.cpu.0.cx_usage: 100.00% 0.00% 0.00% last 3804us
dev.cpu.0.cx_lowest: C3 <1>
dev.cpu.0.cx_supported: C1/1/1 C2/2/1 C3/3/57 <2>
dev.cpu.0.freq_levels: 2267/35000 2266/35000 1600/15000 800/12000 <3>
dev.cpu.0.freq: 1600 <4>
dev.cpu.0.temperature: 40.0C <5>
dev.cpu.0.coretemp.throttle_log: 0
dev.cpu.0.coretemp.tjmax: 105.0C
dev.cpu.0.coretemp.resolution: 1
dev.cpu.0.coretemp.delta: 65
dev.cpu.0.%parent: acpi0
dev.cpu.0.%pnpinfo: _HID=none _UID=0 _CID=none
dev.cpu.0.%location: handle=\_PR_.CPU0
dev.cpu.0.%driver: cpu
dev.cpu.0.%desc: ACPI CPU
```

原文の番号は次の項目を指しています。`cx_lowest` はアイドル時に使用する最も深いC-state、`cx_supported` は対応するC-state、`freq_levels` は周波数と電力の組、`freq` は現在の周波数（MHz）、`temperature` は温度です。表示項目や値は環境によって異なります。

温度が表示されない場合、対応するIntel CPUでは `coretemp(4)`、AMD CPUでは `amdtemp(4)` の読み込みを確認します。

powerdによる制御が適する構成では、まず自動起動を有効にします。[Speed Shift](#hwpstate_intel)を使う環境では後述の違いに注意してください。

```shell
# sysrc powerd_enable=YES
```

動作パラメータの例です。

```shell
# sysrc powerd_flags="-a hiadaptive -i 25 -r 85 -N"
```

`-a` はAC電源時のモードを選び、例では `hiadaptive` を指定しています。`-i 25` は省電力側へ下げる負荷の目安、`-r 85` は性能を上げる負荷の目安です。`-N` はniceで優先度を下げた処理の時間をアイドルと見なし、その処理だけで周波数を上げないための指定です。詳しい挙動は `powerd(8)` を参照してください。

設定後、サービスを起動します。

```shell
# service powerd start
```

<a id="cpufreq"></a>
### CPUの周波数制御

`cpufreq(4)` はCPU周波数制御の共通インターフェースです。管理者、`powerd(8)`、`sysutils/powerdxx` などがこれを利用して、性能と消費電力のバランスを取ります。一般に低い周波数では電力と発熱が減り、高い周波数では性能を得る代わりに消費電力と発熱が増えます。

<a id="est"></a>
### Intel Enhanced SpeedStep

対応するIntel CPUでは `est(4)` がEnhanced SpeedStepによる周波数制御を提供します。`sysctl(8)` や `/etc/rc.d/power_profile` で調整したり、powerd・powerdxxで負荷に応じて変えたりできます。原文は汎用cpufreqドライバに代わるものと説明していますが、利用側からはcpufreqのインターフェースを通じて扱います。

ドライバ、対応周波数と推定電力、現在の周波数を確認する例です。

```shell
# sysctl dev.cpufreq.0.freq_driver dev.cpu.0.freq_levels dev.cpu.0.freq
```

```text
dev.cpufreq.0.freq_driver: est0
dev.cpu.0.freq_levels: 3001/53000 3000/53000 2900/50301 2700/46082 2600/43525 2400/39557 2300/37137 2100/33398 2000/31112 1800/27610 1700/25455 1500/22171 1400/20144 1200/17084 1100/15181 900/12329 800/10550
dev.cpu.0.freq: 800
```

原文の例で最大定格より1MHz高い値は、Turbo Boost機能を示すための表示です。必ずその周波数で固定動作するという意味ではありません。

<a id="hwpstate_intel"></a>
### Intel Speed Shift

FreeBSD 13では、対応する新しいIntel CPU向けに `hwpstate_intel(4)` が導入され、従来の `est(4)` に代わってSpeed Shiftによる制御を有効にする構成が加わりました。ハードウェアがコアごとに周波数を動的に調整できます。

使用中のドライバを調べます。ほかのCPUデバイスでは番号を置き換えます。

```shell
# sysctl dev.cpufreq.0.freq_driver
```

```text
dev.cpufreq.0.freq_driver: hwpstate_intel0
```

この表示ならhwpstate_intelを使用しています。この構成では `freq_levels` に最大周波数だけが表示され、電力欄は `-1` になることがあります。現在の周波数は `dev.cpu.番号.freq` で確認します。

```shell
# sysctl dev.cpu.0.freq_levels dev.cpu.0.freq
```

```text
dev.cpu.0.freq_levels: 3696/-1
dev.cpu.0.freq: 898
```

性能と省電力のバランス設定、ドライバを無効にする方法などは `hwpstate_intel(4)` を参照してください。この方式ではハードウェア側が制御するため、以前のpowerdやpowerdxxが同じように周波数を調整するとは限りません。原文も、従来のツールに慣れた利用者へこの違いを注意しています。

<a id="graphics-card-power-management"></a>
### グラフィックスカードの電力管理

GPUの消費電力も無視できません。原文はIntelグラフィックスを `graphics/drm-kmod` で使う場合の調整例として、`/boot/loader.conf` に次の項目を挙げています。対応するドライバ・機種・版を確認して選択します。

```text
compat.linuxkpi.fastboot=1
compat.linuxkpi.enable_dc=2
compat.linuxkpi.enable_fbc=1
```

順に、起動時の不要な表示モード設定を省く試み、ディスプレイの省電力C-stateの有効化、フレームバッファ圧縮の有効化を意図しています。すべてのGPUやドライバに共通する設定ではありません。

<a id="chapter-13-heading-37"></a>
### サスペンドと復帰

サスペンドは、実行中の状態を保持しながら消費電力を抑え、復帰時に作業を続ける仕組みです。正常な動作にはグラフィックスドライバなどの対応が重要です。原文はKMS非対応のカードでは `sc(4)` を使う必要があると述べていますが、コンソールドライバの利用可否は機種・起動方式によっても異なります。[X Window Systemの章](05-x11.md)と使用するドライバの説明を確認してください。

ACPIで定義される主な状態は次のとおりです。これはすべての状態をFreeBSDが利用できるという意味ではありません。

| 状態 | 内容 |
|---|---|
| S1 | メモリを保持する浅い休止。CPUは省電力状態になりますが、多くの周辺機器は動作を続けます。 |
| S2 | 基本はS1に似ていますが、より深い省電力状態。対応しないシステムも多くあります。 |
| S3（Sleep） | メモリ以外の多くの機器への給電を止め、メモリのリフレッシュを維持します。 |
| S4（Hibernation） | 状態をディスクへ保存して電源を切り、復帰時に読み戻す方式。**固定原文ではFreeBSD未対応です。** |
| S5 | 正常にシャットダウンし、電源を切った状態。 |

<a id="configure-suspend-resume"></a>
#### サスペンドと復帰を設定する

まずハードウェアが報告する状態を確認します。

```shell
% sysctl hw.acpi.supported_sleep_state
```

```text
hw.acpi.supported_sleep_state: S3 S4 S5
```

**S4が一覧に出ても、FreeBSDが実装として利用できることを示すわけではありません。** 原文ではS4は未対応です。

S3を試すには `acpiconf(8)` を使います。作業を保存し、復帰できる手段を確認してから試してください。成功すると画面が消え、多くの機器への給電が止まりますが、通常の電源断とは異なりメモリの内容は保持されます。

```shell
# acpiconf -s 3
```

ノートPCのふたを閉じたときにS3へ入る設定は、`/etc/sysctl.conf` に次を追加します。手動のサスペンドと復帰が正常に動くことを先に確認してください。

```text
hw.acpi.lid_switch_state=S3
```

<a id="troubleshooting-suspend-resume"></a>
#### サスペンドや復帰がうまくいかない場合

改善は続けられていますが、すべてのノートPCで同じように動作するわけではありません。原文は、Bluetoothを無効にする、適切なグラフィックスドライバを読み込む、といった確認を挙げています。

機種ごとの状況や切り分けの情報は、[FreeBSD WikiのSuspend/Resume](https://wiki.freebsd.org/SuspendResume)も参照してください。

<a id="adding-swap-space"></a>
## スワップ領域を追加する

スワップが不足した場合、ディスク上の専用パーティションを追加する方法と、既存ファイルシステム上へスワップファイルを作る方法があります。暗号化の理由や選択肢は[スワップの暗号化](https://docs.freebsd.org/en/books/handbook/disks/#swap-encrypting)を参照してください。

<a id="new-drive-swap"></a>
### ディスクやパーティションをスワップにする

原文は、既存ディスクの別パーティションより、専用の別ディスクを使うほうが性能上有利と説明しています。実際の効果は媒体や負荷によります。[ディスクの追加](https://docs.freebsd.org/en/books/handbook/disks/#disks-adding)と[パーティション設計](02-bsdinstall.md#configtuning-initial)も参照してください。

**未マウントのパーティションでも、中にデータが残っていることがあります。`swapon` でスワップとして使うとそのデータを破壊します。対象が本当にスワップ用であることを、実行前に確認してください。** 次のデバイス名は原文の例です。

```shell
# swapon /dev/ada1p2
```

起動時にも有効にするには `/etc/fstab` に追加します。

```text
/dev/ada1p2 none swap sw 0 0
```

各列の意味は `fstab(5)` を参照してください。

<a id="create-swapfile"></a>
### スワップファイルを作成する

<a id="swapfile-10-and-later"></a>

次は `/usr/swap0` という512MBのファイルを作る例です。

**ZFS上のスワップファイルは、スワップ処理によってシステムが停止するおそれがあるため、強く非推奨とされています。この例をZFS上でそのまま使わないでください。**

まずファイルを作成します。指定先に既存ファイルがないことと、十分な空き容量を確認してください。

```shell
# dd if=/dev/zero of=/usr/swap0 bs=1m count=512
```

所有者以外が読み書きできないよう、アクセス権を設定します。

```shell
# chmod 0600 /usr/swap0
```

`/etc/fstab` に追加します。

```text
md none swap sw,file=/usr/swap0,late 0 0
```

以後は起動時に有効になります。今すぐ有効にするには次を実行します。

```shell
# swapon -aL
```
