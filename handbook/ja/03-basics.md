<a id="basics"></a>
# 第3章 FreeBSDの基本

FreeBSDを使ううえで基礎となる、ログイン、アカウント、アクセス権、ファイルシステム、プロセス、シェル、エディタ、マニュアルの読み方を説明します。

<a id="basics-synopsis"></a>
## 概要

本章ではFreeBSDの基本的なコマンドと機能を学びます。多くはほかのUNIX系OSにも共通します。初めてFreeBSDを使う方は、ひととおり目を通してください。

扱う内容は、仮想コンソール、ユーザーとグループ、ファイルのアクセス権とフラグ、ディレクトリ階層とディスク構成、マウント・アンマウント、プロセスとシグナル、シェルとログイン環境、テキストエディタ、デバイスノード、マニュアルの調べ方です。

<a id="consoles"></a>
## 仮想コンソールと端末

起動時にGUIを自動起動する設定がなければ、通常は次のような文字ベースのログイン画面になります。

```text
FreeBSD/amd64 (pc3.example.org) (ttyv0)

login:
```

`amd64` は64ビットx86、`pc3.example.org` はホスト名、`ttyv0` はシステムコンソールを示します。`login:` で入力を待っています。

FreeBSDは複数ユーザーを区別するため、それぞれのユーザー名とパスワードでログインします。[インストール時に作成したユーザー](02-bsdinstall.md#bsdinstall-addusers)の名前を入力してEnterを押し、続いてパスワードを入力してEnterを押します。**パスワードは入力しても画面に表示されません。**

認証に成功すると、MOTD（Message of the Day）とコマンドプロンプトが表示されます。シェルなどの設定に応じて `$`、`%`、`#` などの記号が使われ、コマンドを入力できる状態になったことを示します。一般に `#` はrootの例に用いられますが、プロンプト文字は変更可能です。

<a id="consoles-virtual"></a>
### 仮想コンソールを使う

システムコンソールには既定でシステムメッセージが流れ、作業中の画面に重なることがあります。通常の作業には別の仮想コンソールを使うと便利です。各コンソールは独立したログイン画面とシェルを持ち、GUIで複数のウィンドウを開くように切り替えられます。

原文の標準構成では、Alt+F1がシステムコンソール `ttyv0`、Alt+F2が `ttyv1`、Alt+F3が `ttyv2` という対応で、Alt+F8までを使います。Xorgの画面から文字コンソールへ戻るにはCtrl+Alt+F1などを使います。切り替えても、元のコンソールのプログラムは動き続けます。

コンソールとキーボードの詳しい説明は `kbdcontrol(1)`、`vidcontrol(1)`、`atkbd(4)`、`syscons(4)`、`vt(4)` を参照してください。数や起動するプログラムは `/etc/ttys` で設定します。次は原文の例です。

```shell
# name    getty                         type  status comments
#
ttyv0   "/usr/libexec/getty Pc"         xterm   on  secure
# Virtual terminals
ttyv1   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv2   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv3   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv4   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv5   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv6   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv7   "/usr/libexec/getty Pc"         xterm   on  secure
ttyv8   "/usr/X11R6/bin/xdm -nodaemon"  xterm   off secure
```

不要な仮想コンソールは、対応行の先頭へ `#` を付けて無効にできます。原文では `ttyv5`〜`ttyv8` の行をコメントにする例を挙げていますが、掲載例の `ttyv8` はもともと `off` です。行数と実際に有効なコンソール数を区別してください。**システムコンソール `ttyv0` の行はコメントにしないでください。**

`ttyv8` のxdmと `/usr/X11R6` は旧来のGUI構成例です。GUIの利用は[第5章](05-x11.md)の構成と合わせて確認します。各列の意味は `ttys(5)` を参照してください。

<a id="consoles-singleuser"></a>
### シングルユーザーモード

起動メニューの **Boot Single User** は、修復のための特別なモードです。正常に起動できないシステムの修復や、忘れたrootパスワードの再設定などに使います。通常のネットワークや別の仮想コンソールは利用できませんが、既定ではrootパスワードなしで広い権限を得られます。そのため、コンソールへ物理的にアクセスできる人を管理することが重要です。

関連する `/etc/ttys` の例です。

```shell
# name  getty                           type  status  comments
#
# If console is marked "insecure", then init will ask for the root password
# when going to single-user mode.
console none                            unknown  off  secure
```

`secure` は、コンソールへの物理アクセスを信頼する設定です。`insecure` に変えると、物理環境を信頼しないものとして、シングルユーザーモードへ入る際にrootパスワードを求めます。名前と認証の関係に注意してください。

rootパスワードを忘れた場合には、この設定によって復旧の手順が難しくなります。変更前に復旧方法を確認してください。[起動処理の章](14-boot.md#boot-singleuser)にも説明があります。

<a id="consoles-vidcontrol"></a>
### コンソールの表示モードを変える

原文では、VESA対応の従来のコンソール構成で、1024×768や1280×1024など、機器が対応するモードへ変える方法を説明しています。**使用するコンソールドライバやUEFI・KMS環境によって方法が異なるため、すべての環境に共通する手順ではありません。**

VESAモジュールを読み込みます。

```shell
# kldload vesa
```

対応する表示モードを調べます。

```shell
# vidcontrol -i mode
```

表示されたモードから選びます。次の番号は原文の例です。

```shell
# vidcontrol MODE_279
```

正常に使えることを確かめたら、起動時の設定を `/etc/rc.conf` に記載できます。

```text
allscreens_flags="MODE_279"
```

<a id="users-synopsis"></a>
## ユーザーとアカウントの管理

FreeBSDでは、ネットワーク接続などを通じて複数ユーザーが同時に作業できます。利用者ごとに専用のアカウントを用意します。

本節では、アカウントの種類、追加・削除・変更、資源利用の制限に関する設定、グループの作成とメンバー管理を説明します。

<a id="users-introduction"></a>
### アカウントの種類

システムへのアクセスとプロセスの実行はアカウントに結び付いています。主な種類は、サービスを実行するシステムアカウント、人が使うユーザーアカウント、管理用のスーパーユーザーアカウントです。

<a id="users-system"></a>
#### システムアカウント

DNS、メール、ウェブサーバなどのサービスを実行するためのアカウントです。すべてをrootで動かすと制限のない権限を与えることになるため、サービスに応じた権限へ分離します。原文の例には `daemon`、`operator`、`bind`、`news`、`www` がありますが、存在や権限は構成によります。

`nobody` は汎用の非特権アカウントです。ただし、多くのサービスを同じnobodyで動かすと、そのアカウントがアクセスできるファイルやプロセスが増えます。「nobodyなら常に最小権限」とは限りません。

<a id="users-user"></a>
#### ユーザーアカウント

人がログインして使うアカウントです。一人ずつ分けることで、誰が何をしたかを把握しやすくし、ほかの人の設定を不用意に変更することも防げます。各ユーザーはシェル、エディタ、キー割り当て、言語などを選べます。

アカウントに結び付く主な情報は次のとおりです。

| 項目 | 内容 |
|---|---|
| ユーザー名 | `login:` に入力する一意の名前。規則は `passwd(5)` を参照。原文は古いアプリケーションとの互換性のため、小文字で8文字以下を勧めていますが、これはシステム全体の最大長という意味ではありません。 |
| パスワード | アカウントの認証に使う情報。 |
| UID | システム内部でユーザーを識別する番号。ユーザー名を指定するコマンドも内部ではUIDへ変換します。原文は一部ソフトとの互換性から65535未満を勧めています。 |
| GID | 主グループを識別する番号。個人単位ではなくグループ単位で資源へのアクセスを制御でき、補助グループにも所属できます。原文は互換性のため65535以下を勧めています。 |
| ログインクラス | ユーザー別の環境や資源制限を柔軟に指定する仕組み。[ログインクラス](https://docs.freebsd.org/en/books/handbook/security/#users-limiting)を参照。 |
| パスワード変更期限 | 既定では失効しませんが、ユーザーごとに期限を設けて変更を求められます。 |
| アカウント有効期限 | 既定では無期限。学生用など期間限定のアカウントは `pw(8)` で期限を設定できます。期限後はログインできなくなりますが、ファイルは残ります。 |
| フルネーム | 実名などの説明。ユーザー名とは別で、空白や大文字、8文字を超える文字列も使えます。 |
| ホームディレクトリ | ログイン時の開始場所で、個人ファイルを保存します。通常は `/home/username` や `/usr/home/username`。 |
| シェル | システムを操作するコマンド環境。利用者の好みに合わせて選べます。 |

<a id="users-superuser"></a>
#### スーパーユーザー

通常 `root` と呼ばれ、システム管理に必要な強い権限を持ちます。メール、普段の調査、プログラミングなどの日常作業には一般ユーザーを使い、管理が必要な操作だけ権限を切り替えます。一般ユーザーにも自分のデータを失う危険はありますが、rootでの誤操作はシステム全体へ及びます。空白一つ、文字一つの違いにも注意してください。

rootで直接ログインするより、必要なときに `su(1)` を使います。`su -` はrootのログイン環境も読み込みます。標準的な設定では、実行ユーザーがwheelグループに属し、rootパスワードを知っている必要があります。

次はビルドを一般ユーザーで行い、インストール時だけ切り替える原文の例です。終了後は `exit` で元へ戻ります。

```shell
% configure
% make
% su -
Password:
# make install
# exit
%
```

単独の管理者ならsuでも管理できますが、`security/sudo` を導入すると、実行記録や、ユーザーごとに許可する管理コマンドの制限を設定できます。

<a id="users-modifying"></a>
### アカウント管理の道具

<a id="users-modifying-utilities"></a>

よく使うコマンドをまとめます。詳細と使用例は、それぞれのマニュアルを確認してください。

| コマンド | 用途 |
|---|---|
| `adduser(8)` | 対話式でユーザーを追加するための推奨ツール。 |
| `rmuser(8)` | ユーザーを削除するための推奨ツール。 |
| `chpass(1)` | ユーザーデータベースの情報を変更。 |
| `passwd(1)` | パスワードを変更。 |
| `pw(8)` | ユーザーとグループを柔軟に管理。 |
| `bsdconfig(8)` | アカウント管理も行えるシステム設定ツール。 |

<a id="users-adduser"></a>
#### ユーザーを追加する

<a id="users-modifying-adduser"></a>

rootで `adduser(8)` を実行します。ユーザーデータベースやグループ情報を更新し、ホームディレクトリを作成して `/usr/share/skel` から初期設定をコピーします。必要なら歓迎メールも送れます。

質問に順番に答え、角括弧内の既定値でよければEnterを押します。次の例では `jru` をwheelグループにも追加し、suを利用できるようにしています。これは管理権限を与える判断なので、全ユーザーへ一律に追加するものではありません。

```shell
# adduser
```

```text
Username: jru
Full name: J. Random User
Uid (Leave empty for default):
Login group [jru]:
Login group is jru. Invite jru into other groups? []: wheel
Login class [default]:
Shell (sh csh tcsh zsh nologin) [sh]: zsh
Home directory [/home/jru]:
Home directory permissions (Leave empty for default):
Use password-based authentication? [yes]:
Use an empty password? (yes/no) [no]:
Use a random password? (yes/no) [no]:
Enter password:
Enter password again:
Lock out the account after creation? [no]:
Username   : jru
Password   : ****
Full Name  : J. Random User
Uid        : 1001
Class      :
Groups     : jru wheel
Home       : /home/jru
Shell      : /usr/local/bin/zsh
Locked     : no
OK? (yes/no): yes
adduser: INFO: Successfully added (jru) to the user database.
Add another user? (yes/no): no
Goodbye!
```

最後に、続けて別のユーザーを追加するか尋ねられます。パスワードは入力時に表示されないため、打ち間違いに注意してください。選べるシェルなどは導入済みの環境によって異なります。

<a id="users-rmuser"></a>
#### ユーザーを削除する

rootで `rmuser(8)` を使います。原文が挙げる処理は次のとおりです。

1. そのユーザーのcrontabを削除します。
2. 予約されたatジョブを削除します。
3. 所有するプロセスへSIGKILLを送ります。
4. ローカルのユーザーデータベースから削除します。
5. ユーザー所有のホームディレクトリを、実体へのシンボリックリンクの扱いも含めて削除します。
6. `/var/mail` の受信メールを削除します。
7. `/tmp`、`/var/tmp`、`/var/tmp/vi.recover` にある所有ファイルを削除します。
8. `/etc/group` の所属から外します。ユーザー名と同名のグループが空になった場合は、それも削除します。
9. 所有するメッセージキュー、共有メモリ、セマフォを削除します。

**必要なデータを退避してから実行してください。** また、上記以外の場所にある全所有ファイルを自動的に探して消すという意味ではありません。スーパーユーザーの削除には使えません。

既定の対話操作の例です。対象とホームディレクトリの削除を確認します。

```shell
# rmuser jru
```

```text
Matching password entry:
jru:*:1001:1001::0:0:J. Random User:/home/jru:/usr/local/bin/zsh
Is this the entry you wish to remove? y
Remove user's home directory (/home/jru)? y
Removing user (jru): mailspool home passwd.
```

<a id="users-chpass"></a>
#### ユーザー情報を変更する

<a id="users-modifying-chpass-su"></a>
<a id="users-modifying-chpass-ru"></a>

`chpass(1)` は、一般ユーザーなら自分のシェルや個人情報、rootならほかのユーザーを含む広い範囲の情報を変更できます。ユーザー名以外のオプションなしで実行するとエディタが開き、終了時に変更を反映します。root以外ではパスワードを求められます。

rootによる操作例です。

```shell
# chpass jru
```

```shell
# Changing user database information for jru.
Login: jru
Password: *
Uid [#]: 1001
Gid [# or name]: 1001
Change [month day year]:
Expire [month day year]:
Class:
Home directory: /home/jru
Shell: /usr/local/bin/zsh
Full Name: J. Random User
Office Location:
Office Phone:
Home Phone:
Other information:
```

一般ユーザーの場合は、変更できる最後の六項目だけが表示されます。

```text
#Changing user database information for jru.
Shell: /usr/local/bin/zsh
Full Name: J. Random User
Office Location:
Office Phone:
Home Phone:
Other information:
```

`chfn`、`chsh`、`ypchpass`、`ypchfn`、`ypchsh` はchpassへのリンクです。NISへの対応は自動なので、`yp` 付きの名前が必須というわけではありません。NISの設定は[ネットワークサーバ](https://docs.freebsd.org/en/books/handbook/network-servers/)を参照してください。

<a id="users-passwd"></a>
#### パスワードを変更する

自分のパスワードは `passwd(1)` で変更します。意図しない変更を防ぐため、最初に現在のパスワードを求められます。

```shell
% passwd
```

```text
Changing local password for jru.
Old password:
New password:
Retype new password:
passwd: updating the database...
passwd: done
```

rootはユーザー名を指定することで、そのユーザーのパスワードを変更できます。この場合は古いパスワードを求めないため、忘れた場合の再設定にも使えます。

```shell
# passwd jru
```

```text
Changing local password for jru.
New password:
Retype new password:
passwd: updating the database...
passwd: done
```

`yppasswd` はpasswdへのリンクで、どちらの名前でもNISに対応します。

<a id="users-pw"></a>
#### pwでユーザーとグループを管理する

`pw(8)` は、ユーザー・グループの作成、削除、変更、表示を行う、システムのアカウント情報への操作窓口です。豊富なコマンドラインオプションがあり、シェルスクリプトにも適しますが、初めて使う場合は対話式ツールより複雑に感じるかもしれません。

<a id="users-groups"></a>
### グループを管理する

グループは名前とGIDで識別され、ユーザーをまとめてアクセス権を管理します。カーネルはプロセスのUIDと所属グループを使い、許可する操作を判断します。通常GIDとだけ言う場合は主グループを指し、ほかに補助グループにも所属できます。

`/etc/group` は、グループ名、パスワード欄、GID、カンマ区切りのメンバー一覧という四つの欄を `:` で区切ったテキストです。書式は `group(5)` を参照してください。rootが直接編集することもできますが、よくある誤りを検出できる `vigr(8)`、または `pw(8)` を使うとよいでしょう。

**operatorグループは、停止・再起動や、グループに許可された `/dev` 内の機器へのアクセスなど、強い権限を与える場合があります。安易に追加しないでください。**

次は `teamtwo` を作り、確認する例です。

```shell
# pw groupadd teamtwo
# pw groupshow teamtwo
```

```text
teamtwo:*:1100:
```

GIDは1100、まだメンバーは空です。次はメンバーをjruに設定します。

```shell
# pw groupmod teamtwo -M jru
# pw groupshow teamtwo
```

```text
teamtwo:*:1100:jru
```

`-M` はカンマ区切りの一覧で**既存メンバーを置き換える**指定です。追加だけを行うときは小文字の `-m` を使います。

```shell
# pw groupmod teamtwo -m db
# pw groupshow teamtwo
```

```text
teamtwo:*:1100:jru,db
```

こちらは既存のjruを残し、dbを追加しています。pwによるグループ編集は `/etc/group` のメンバー欄を扱います。`/etc/passwd` 側で主グループとして指定された所属は、`pw groupshow` のメンバー欄に列挙されないことがあるため、全所属の確認には `id(1)` なども使います。

```shell
% id jru
```

```text
uid=1001(jru) gid=1001(jru) groups=1001(jru), 1100(teamtwo)
```

この例ではjruは主グループjruと補助グループteamtwoの両方に所属しています。詳細は `pw(8)` と `group(5)` を参照してください。

<a id="permissions"></a>
## アクセス権

ファイルとディレクトリにはアクセス権があり、必要な人が使え、ほかの利用者やOSのファイルを不当に扱えないよう制御します。本節は従来のUNIXの権限を説明します。より細かな設定は[ACL](https://docs.freebsd.org/en/books/handbook/security/#fs-acl)を参照してください。

基本は読み取り `r`、書き込み `w`、実行 `x` です。所有者、所有グループ、その他の三者へそれぞれ設定します。数値ではrが4、wが2、xが1で、許可する値を足します。

| 値 | 許可する操作 | 表示 |
|---|---|---|
| 0 | なし | `---` |
| 1 | 実行 | `--x` |
| 2 | 書き込み | `-w-` |
| 3 | 書き込み・実行 | `-wx` |
| 4 | 読み取り | `r--` |
| 5 | 読み取り・実行 | `r-x` |
| 6 | 読み取り・書き込み | `rw-` |
| 7 | 読み取り・書き込み・実行 | `rwx` |

`ls -l` で確認できます。

```shell
% ls -l
```

```text
total 530
-rw-r--r--  1 root  wheel     512 Sep  5 12:31 myfile
-rw-r--r--  1 root  wheel     512 Sep  5 12:31 otherfile
-rw-r--r--  1 root  wheel    7680 Sep  5 12:31 email.txt
```

`myfile` の最初の `-` は通常ファイルを示します。その後の三文字ずつが所有者・グループ・その他の権限です。この例の `rw-r--r--` は、所有者が読み書きでき、グループとその他は読むだけなので、数値では644です。先頭の種類の欄は、ディレクトリ、デバイス、ソケットなどでは別の文字になります。

ハードウェアの多くも、プログラムが読み書きする `/dev` の特殊ファイルを介して扱います。これらにもアクセス権があります。

ディレクトリの権限は少し意味が異なります。`x` は中へ移動・通過し、名前の分かる項目へアクセスするための検索権限です。中のファイル自体の権限も別途適用されます。`r` は項目名の一覧を読む権限で、名前の分かるファイルを削除するには、通常その親ディレクトリに `w` と `x` が必要です。ファイル自身が書き込み禁止でも、削除可否はそれだけでは決まりません。

setuidやsticky bitなどの追加ビットもあります。設定方法の詳細は `chmod(1)` を参照してください。

<a id="chapter-03-heading-20"></a>
### 記号でアクセス権を指定する

`chmod(1)` では8進数の代わりに、**誰に・どうするか・どの権限を**という記号形式も使えます。

| 要素 | 記号 | 意味 |
|---|---|---|
| 誰に | `u` | 所有者 |
| 誰に | `g` | 所有グループ |
| 誰に | `o` | その他 |
| 誰に | `a` | 全員 |
| 操作 | `+` | 追加 |
| 操作 | `-` | 削除 |
| 操作 | `=` | 指定内容に設定 |
| 権限 | `r` | 読み取り |
| 権限 | `w` | 書き込み |
| 権限 | `x` | 実行・検索 |
| 権限 | `t` | sticky bit |
| 権限 | `s` | setuidまたはsetgid |

次は、グループとその他に対する通常の権限を空にする例です。`FILE` は対象のファイル名です。

```shell
% chmod go= FILE
```

複数の変更はカンマで区切れます。次はグループとその他の書き込みを外し、全員に実行権限を追加します。

```shell
% chmod go-w,a+x FILE
```

<a id="chapter-03-heading-21"></a>
### FreeBSDのファイルフラグ

通常のアクセス権に加え、FreeBSDにはファイルフラグがあります。削除禁止・変更禁止などを指定でき、フラグとsecurelevelの組み合わせによってはrootの操作も制限されます。

**訳注：** 原文はディレクトリを対象外としていますが、[chflags(1)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/bin/chflags/chflags.1)はディレクトリにも適用できます。使用できる属性や制約はファイルシステムにも依存します。

`chflags(1)` で、システムの削除禁止フラグを設定する例です。

```shell
# chflags sunlink file1
```

解除するときは名前に `no` を付けます。

```shell
# chflags nosunlink file1
```

表示には `ls -lo` を使います。

```shell
# ls -lo file1
```

```text
-rw-r--r--  1 trhodes  trhodes  sunlnk 0 Mar  1 05:54 file1
```

rootだけが変更できるフラグと、所有者も変更できるフラグがあります。変更可否はsecurelevelにも左右されます。詳細は `chflags(1)`、`chflags(2)` を参照してください。

<a id="chapter-03-heading-22"></a>
### setuid・setgid・sticky bit

通常のrwxに加えて、setuid、setgid、sticky bitを理解することも重要です。

プロセスには、起動した利用者などを表す**実UID**と、権限判定に使う**実効UID**があります。たとえば `passwd(1)` は一般ユーザーが起動しても、パスワードデータベースを更新するための実効UIDを持ちます。対応する実行ファイルでsetuidが有効なら、所有者の実効UIDで実行されます。

次はビットを付ける操作例です。**ファイル名が `.sh` の例では、後述のとおりスクリプト自体の権限昇格は起きません。**

```shell
# chmod u+s suidexample.sh
```

数値なら先頭に4を付けます。

```shell
# chmod 4755 suidexample.sh
```

```text
-rwsr-xr-x   1 trhodes  trhodes    63 Aug 29 06:36 suidexample.sh
```

所有者の実行欄が `s` になっています。`nosuid` でマウントされたファイルシステムではset-IDビットは適用されません。原文の「黙って失敗する」という表現は、プログラムの実行そのものが必ず失敗するという意味ではありません。また、原文はラッパープログラム経由などでは期待した制限にならない可能性も注意しています。権限を持つプログラムの全体の動作まで、このマウント指定だけで隔離できるわけではありません。[execve(2)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/lib/libsys/execve.2)も参照してください。

実効UIDの確認例として、端末Aで一般ユーザーがpasswdを起動し、入力待ちにします。

```text
Changing local password for trhodes
Old Password:
```

端末Bでプロセスを調べます。

```shell
# ps aux | grep passwd
```

```text
trhodes  5232  0.0  0.2  3420  1608   0  R+    2:10AM   0:00.00 grep passwd
root     5211  0.0  0.2  3620  1724   2  I+    2:09AM   0:00.01 passwd
```

passwdの所有者表示がrootとなり、実効UIDが使われていることが分かります。

setgidは同様に実効GIDをファイルの所有グループへ切り替えます。記号で設定する例です。

```shell
# chmod g+s sgidexample.sh
```

数値では先頭に2を付けます。

```shell
# chmod 2755 sgidexample.sh
```

```text
-rwxr-sr-x   1 trhodes  trhodes    44 Aug 31 01:49 sgidexample.sh
```

グループの実行欄に `s` が表示されます。ただし、**インタプリタで実行するスクリプトのset-IDビットは適用されません**。原文のシェルスクリプト例はビットの表示を示すもので、スクリプトが `setuid(2)` を呼べないからという説明だけで一般化しないでください。

setuid・setgidは強い権限を与えるため、設定するプログラムの安全性が重要です。一方、ディレクトリのsticky bitは、共有場所で他人のファイルを削除・改名することを制限します。原文は「ファイル所有者だけ」と説明していますが、実際には必要なディレクトリ権限に加え、ファイル所有者、ディレクトリ所有者、スーパーユーザーであることが条件になります。[sticky(7)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/share/man/man7/sticky.7)を参照してください。

`/tmp` に付ける例です。

```shell
# chmod +t /tmp
```

数値では先頭に1を付けます。

```shell
# chmod 1777 /tmp
```

末尾の `t` で確認できます。

```shell
# ls -al / | grep tmp
```

```text
drwxrwxrwt  10 root  wheel         512 Aug 31 01:49 tmp
```

<a id="dirstructure"></a>
## ディレクトリ階層

最上位はルートディレクトリ `/` です。起動時に最初にマウントされ、マルチユーザーモードへ移るための基本部分や、ほかのファイルシステムを接続する場所を持ちます。**マウントポイント**は、別のファイルシステムをつなぐディレクトリです。[ディスク構成](#disk-organization)で詳しく説明します。

`/usr`、`/var`、`/tmp`、`/mnt`、`/media` などはマウントポイントにも使えますが、必ず別ファイルシステムという意味ではありません。`/etc/fstab` にある多くの項目は、`noauto` を付けない限りrcの起動処理でマウントされます。[fstab](#disks-fstab)を参照してください。

主な配置は次のとおりです。全体は `hier(7)` を参照してください。

| パス | 内容 |
|---|---|
| `/` | ファイルシステム階層の最上位。 |
| `/bin/` | シングル・マルチユーザー両環境の基本コマンド。 |
| `/boot/` | 起動用プログラムと設定。 |
| `/boot/defaults/` | 起動設定の既定値。`loader.conf(5)` を参照。 |
| `/dev/` | `devfs(5)` が管理するデバイス特殊ファイル。 |
| `/etc/` | システム設定とスクリプト。 |
| `/etc/defaults/` | システム設定の既定値。`rc(8)` を参照。 |
| `/etc/periodic/` | cronから日次・週次・月次に実行する保守スクリプト。`periodic(8)` を参照。 |
| `/lib/` | `/bin`・`/sbin` の実行に必要な主要ライブラリ。 |
| `/libexec/` | 重要なシステム用ファイル。 |
| `/media/` | CD、USBストレージ、フロッピーなどのマウント先。 |
| `/mnt/` | 管理者が一時的なマウントに使う、通常は空のディレクトリ。 |
| `/net/` | 自動マウントするNFS共有。`auto_master(5)` を参照。 |
| `/proc/` | プロセスファイルシステムのマウント先。`procfs(5)` を参照。 |
| `/rescue/` | 緊急復旧用の静的リンクプログラム。`rescue(8)` を参照。 |
| `/root/` | rootのホームディレクトリ。 |
| `/sbin/` | 両動作モードで必要な管理コマンド。 |
| `/tmp/` | 一時ファイル。通常は再起動後の保持を期待しません。`tmpmfs` 関連のrc.conf設定やfstabにより、メモリ上のファイルシステムを使う構成もあります。`mdmfs(8)` を参照。 |
| `/usr/` | 多くのユーザー用コマンド・アプリケーション。 |
| `/usr/bin/` | 一般コマンド、開発ツール、アプリケーション。 |
| `/usr/include/` | 標準Cヘッダ。 |
| `/usr/lib/` | ライブラリ。 |
| `/usr/libdata/` | ユーティリティのデータ。 |
| `/usr/libexec/` | 他のプログラムから起動するデーモン・補助ツール。 |
| `/usr/local/` | 追加ソフトウェアのプログラム・ライブラリ。Portsの標準導入先。基本は `/usr` に似た配置です。原文はmanを直下、Ports文書を `share/doc/port` に置く例を挙げますが、配置はパッケージ・版ごとに確認します。 |
| `/usr/ports/` | Ports Collection（任意）。 |
| `/usr/sbin/` | ユーザーが起動する管理ツール・デーモン。 |
| `/usr/share/` | アーキテクチャに依存しないファイル。 |
| `/usr/src/` | 基本システムやローカルのソース。 |
| `/var/` | ログ、一時データ、スプールなど変化するファイル。 |
| `/var/log/` | システムログ。 |
| `/var/tmp/` | 通常は再起動をまたいで保持する一時ファイル。 |

<a id="disk-organization"></a>
## ディスクとパスの構成

ファイルを識別する基本は名前です。大文字と小文字を区別するため、`readme.txt` と `README.TXT` は別の名前です。FreeBSD自体は、拡張子だけで実行プログラムか文書かを判定しません。

ファイルを収めるディレクトリは、さらに別のディレクトリを含むことができ、階層を作ります。名前を `/` でつないだものが**パス**です。たとえばfooの中のbarにあるreadme.txtは `foo/bar/readme.txt` と表せます。Windowsの `c:\foo\bar\readme.txt` と異なり、区切りにバックスラッシュを使わず、ドライブ文字も付けません。

<a id="disks-file-systems"></a>
### ファイルシステムをつなぐ

各ファイルシステムは、一つの最上位ディレクトリを持ちます。そのうちシステム全体の `/` となるものを**ルートファイルシステム**とし、ほかはその下へマウントします。ディスクが複数あっても、一つの階層として見えます。

A・B・Cという三つのファイルシステムがあり、それぞれにA1・A2、B1・B2、C1・C2というディレクトリがあるとします。Aを `/` にすると、最初は次のように見えます。

![ファイルシステムをつなぐ：example-dir1.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/basics/example-dir1.png)

BをA1へマウントすると、A1の位置にBのルートが見えるようになります。

![ファイルシステムをつなぐ：example-dir2.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/basics/example-dir2.png)

Bの中へは `/A1/B1`、`/A1/B2` とたどれます。もともとA1にあった内容は削除されず、一時的に隠れます。Bをアンマウントすれば再び見えます。

BをA2へマウントした場合です。

![ファイルシステムをつなぐ：example-dir3.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/basics/example-dir3.png)

今度は `/A2/B1`、`/A2/B2` となります。さらにB1へCをマウントすることもできます。

![ファイルシステムをつなぐ：example-dir4.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/basics/example-dir4.png)

あるいはCをAのA1へ直接マウントできます。

![ファイルシステムをつなぐ：example-dir5.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/basics/example-dir5.png)

一つの大きなルートファイルシステムだけで構成することも可能です。原文は複数へ分ける利点を次のように説明しています。

- マウントオプションを個別に選べます。ルートを読み取り専用にしたり、ユーザーが書き込む `/home` を分けて `nosuid` にし、そこにある実行ファイルのsetuid・setgidを無効にしたりできます。
- 小さなファイルを頻繁に書く用途と、大きなファイルが少数ある用途で、配置の最適化を分けられる場合があります。
- 電源断などで一部が壊れても、ほかの領域で起動し、バックアップから復旧できる可能性が高まります。

反対に、容量を固定した複数領域では、ある領域だけが不足することがあります。一つにまとめると容量配分の制約が減ります。ただし「拡張には必ず作り直しが必要」というわけではありません。原文も `growfs(8)` による拡張を補足しています。拡張先はそのパーティション内の空き領域で、パーティションの後ろに空きがあれば `gpart(8)` でパーティション自体を伸ばせる場合があります。仮想ディスクを拡張し、最後のパーティションを伸ばす構成も該当します。

これらは主に従来のパーティション・UFS構成を念頭に置いた説明です。ZFSのプールやデータセットの管理を、すべて同じ固定容量のモデルで考えないようにしてください。

<a id="disks-partitions"></a>
### パーティションとデバイス名

<a id="disks-naming"></a>
<a id="basics-disk-slice-part"></a>

ディスクは、GPTやMBRなどの方式で領域に分けます。[手動パーティション設定](02-bsdinstall.md#bsdinstall-part-manual)も参照してください。GPTでは開始位置・大きさ・種類を持つ多数のパーティションを扱え、原文は利用可能ならGPTを勧めています。デバイス名の後へ `p1`、`p2` と番号を付けます。

従来のMBRの領域はFreeBSDでは**スライス**と呼び、異なるOSを置けます。FreeBSD用スライスの中を、さらにBSDラベル（`bsdlabel(8)`）のパーティションへ分けます。スライスは `s1` から数え、`da0s1` は最初のdaディスクの第1スライスです。MBRの基本スライスは最大四つですが、拡張領域内の論理スライスを使う構成もあり、その番号は5から始まります。`ada0s5` が例です。

通常、一つのGPTまたはBSDパーティションに一つのファイルシステムを作り、マウント先やデバイス名で呼びます。スワップは、利用していないメモリ内容の一部をディスクへ退避し、必要時に戻すための領域です。これをページングと呼び、物理メモリより大きな仮想メモリを扱う助けになります。

BSDラベルには次の慣習があります。

| 文字 | 用途 |
|---|---|
| `a` | 通常はルートファイルシステム。 |
| `b` | 通常はスワップ。 |
| `c` | 通常はスライス全体と同じ範囲。全体を扱う検査などのために使い、普通のファイルシステムは作りません。 |
| `d` | 以前の特別な意味はなくなり、通常のパーティションとして使えます。 |

BSDパーティションの文字はa〜hです。スライスを作らない旧来の「dangerously dedicated」構成の `da0a` は、最初のdaディスクのaパーティションです。`ada1s3e` は2台目のadaディスク、第3スライス、5番目のBSDパーティションです。**ディスクの番号は0から、スライス・GPTパーティションの番号は1から**数えます。

| ドライブの種類 | デバイス名の接頭辞 |
|---|---|
| SATA・IDEハードディスク | `ada` |
| SCSIディスク・USBストレージ | `da` |
| NVMeストレージ | `nvd` または `nda` |
| SATA・IDE CD-ROM | `cd` |
| SCSI CD-ROM | `cd` |
| フロッピー | `fd` |
| SCSIテープ | `sa` |
| RAID | 原文の例はAdaptec AdvancedRAIDの `aacd`、Mylexの `mlxd`・`mlyd`、AMI MegaRAIDの `amrd`、Compaq Smart RAIDの `idad`、3ware RAIDの `twed`。使用するドライバによって異なります。 |

| 名前の例 | 意味 |
|---|---|
| `ada0s1a` | 最初のSATAディスク、第1スライス、aパーティション。 |
| `da1s2e` | 2台目のSCSIディスク、第2スライス、eパーティション。 |

次は250GBのSATAディスクを、Windows用80GBのスライスとFreeBSD用170GBのスライスへ分けた、原文の概念図です。Windows側はNTFSのCドライブ、FreeBSD側はaが `/`、dが `/var`、eが `/tmp`、fが `/usr`、bがスワップです。cはスライス全体を指すため、通常のデータ領域として使いません。

<a id="basics-concept-disk-model"></a>

![パーティションとデバイス名：disk-layout.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/basics/disk-layout.png)

インストール時は、MBRならスライスとその中のパーティション、GPTなら各パーティションを作り、ファイルシステムやスワップの用途とマウント先を決めます。操作は `gpart(8)` を参照してください。ZFSなどの構成では、プールとファイルシステムの関係も考慮します。

<a id="mount-unmount"></a>
## ファイルシステムをマウント・アンマウントする

ファイルシステムの階層は `/` を根とし、`/dev`、`/usr`、`/usr/local` などへ枝分かれする木にたとえられます。一部を別のファイルシステムに分ける理由には、容量や媒体の違いがあります。

たとえばログやスプール、一時ファイルを持つ `/var` が埋まってもルートに影響しにくいよう、分離できます。また、別の物理ディスク、[NFS](https://docs.freebsd.org/en/books/handbook/network-servers/#network-nfs)の共有、CD-ROMなども、同じ階層へマウントして利用します。

<a id="disks-fstab"></a>
### fstabファイル

[起動時](14-boot.md)には、通常 `/etc/fstab` の項目を自動マウントします。`noauto` の項目は対象外です。基本書式は次のとおりです。

```text
device       /mount-point fstype     options      dumpfreq     passno
```

| 欄 | 意味 |
|---|---|
| `device` | 存在するデバイスの名前。[命名規則](#disks-partitions)も参照。 |
| `mount-point` | マウント先の、存在するディレクトリ。 |
| `fstype` | mountへ渡すファイルシステム種別。原文はUFSを基本の例としています。 |
| `options` | 読み書きの `rw`、読み取り専用の `ro` と、必要な追加オプション。起動時に自動マウントしないなら `noauto`。 |
| `dumpfreq` | `dump(8)` がバックアップ対象の判断に使う値。省略時は0。 |
| `passno` | 再起動後のUFSの `fsck(8)` の検査順序。対象外は0、ルートは1、ほかは1より大きい値。同じ値の項目は可能なら並列検査します。 |

詳細は `fstab(5)` と `mount(8)` を確認してください。ZFSの管理プロパティなど、すべてのファイルシステムをこの表だけで管理するとは限りません。

<a id="disks-mount"></a>
### mountコマンド

基本形は次のとおりです。

```shell
# mount device mountpoint
```

fstabに登録してある場合は、マウント先だけを指定することもできます。主なオプションは次のとおりです。詳しくは `mount(8)` を参照してください。

| オプション | 動作 |
|---|---|
| `-a` | fstabの対象をまとめてマウント。`noauto`、`-t` による除外、すでにマウント済みの項目は除きます。 |
| `-d` | 実際のマウントシステムコールを実行せず、動作を確認。`-v` との併用が便利です。 |
| `-f` | 不整合なファイルシステムの強制マウントや、読み書きから読み取り専用へ変更する際の書き込みアクセスの取り消し。危険を伴います。 |
| `-r` | 読み取り専用。`-o ro` と同じです。 |
| `-t fstype` | 種別を指定。`-a` と組み合わせると対象種別を絞ります。原文の既定はufsです。 |
| `-u` | マウントオプションを更新。 |
| `-v` | 詳細表示。 |
| `-w` | 読み書き可能でマウント。 |

`-o` には追加指定をカンマ区切りで渡せます。`nosuid` はそのファイルシステム上のsetuid・setgidビットを適用しないための指定です。

<a id="disks-umount"></a>
### umountコマンド

アンマウントには `umount(8)` を使い、マウントポイントまたはデバイス名を指定します。`-a` や `-A` でまとめて解除でき、`-t` で対象種別を絞ることもできます。`-A` はルートファイルシステムを解除しません。

`-v` は詳細表示、`-f` は強制解除です。**強制解除はシステム停止やデータ破損につながる場合があり、通常の対処として安易に使わないでください。**

<a id="basics-processes"></a>
## プロセスとデーモン

実行中のプログラムを**プロセス**と呼びます。FreeBSDでは多数のプロセスが並行して動きます。外部コマンドは通常プロセスとして実行されますが、シェル組み込みコマンドなど、入力したコマンドが毎回必ず新しいプロセスになるわけではありません。

各プロセスはPIDという番号で識別され、所有者とグループなどの資格情報によって、ファイルやデバイスへのアクセスが判定されます。通常は起動した親プロセスがあり、シェルから実行したプログラムの親はそのシェルになります。ユーザー空間の初期化を担う特別なプロセス `init(8)` はPID 1です。

ウェブサーバやメールサーバのように、端末から継続的に入力を受けず、バックグラウンドで要求を処理するものを**デーモン**と呼びます。ギリシャ神話の、善悪のどちらでもなく目に見えず働く存在に由来し、BSDのマスコットもスニーカーと熊手を持つdaemonです。

名前の末尾にdを付ける慣習があり、BINDの `named`、Apacheの `httpd`、印刷用の `lpd` が例です。ただし決まりではなく、Sendmailは `maild` ではなく `sendmail` です。

<a id="chapter-03-heading-32"></a>
### プロセスを表示する

`ps(1)` はある時点の一覧、`top(1)` は定期更新する対話画面を表示します。既定のpsは通常、自分のプロセスの一部を表示します。

```shell
% ps
```

```text
 PID TT  STAT    TIME COMMAND
8203  0  Ss   0:00.59 /bin/csh
8895  0  R+   0:00.00 ps
```

`PID` は識別番号、`TT` は端末、`STAT` は状態、`TIME` はCPUを使用した累積時間、`COMMAND` はコマンドです。TIMEは起動からの経過時間とは異なります。原文はPIDを1から99999まで割り当てて循環させる例を示していますが、範囲はシステムの設定・実装によります。使用中の番号を別プロセスへ同時に再割り当てはしません。

よく使う組み合わせが `ps auxww` です。`a` でほかのユーザーを含む対象を広げ、`u` でユーザー名やメモリ使用量を表示し、`x` で制御端末のないプロセスも含め、`ww` で長いコマンド行を切り詰めずに表示します。

topの表示例です。数値や列は版・環境によって変わります。

```shell
% top
```

```text
last pid:  9609;  load averages:  0.56,  0.45,  0.36              up 0+00:20:03  10:21:46
107 processes: 2 running, 104 sleeping, 1 zombie
CPU:  6.2% user,  0.1% nice,  8.2% system,  0.4% interrupt, 85.1% idle
Mem: 541M Active, 450M Inact, 1333M Wired, 4064K Cache, 1498M Free
ARC: 992M Total, 377M MFU, 589M MRU, 250K Anon, 5280K Header, 21M Other
Swap: 2048M Total, 2048M Free

  PID USERNAME    THR PRI NICE   SIZE    RES STATE   C   TIME   WCPU COMMAND
  557 root          1 -21  r31   136M 42296K select  0   2:20  9.96% Xorg
 8198 dru           2  52    0   449M 82736K select  3   0:08  5.96% kdeinit4
 8311 dru          27  30    0  1150M   187M uwait   1   1:37  0.98% firefox
  431 root          1  20    0 14268K  1728K select  0   0:06  0.98% moused
 9551 dru           1  21    0 16600K  2660K CPU3    3   0:01  0.98% top
 2357 dru           4  37    0   718M   141M select  0   0:21  0.00% kdeinit4
 8705 dru           4  35    0   480M    98M select  2   0:20  0.00% kdeinit4
 8076 dru           6  20    0   552M   113M uwait   0   0:12  0.00% soffice.bin
 2623 root          1  30   10 12088K  1636K select  3   0:09  0.00% powerd
 2338 dru           1  20    0   440M 84532K select  1   0:06  0.00% kwin
 1427 dru           5  22    0   605M 86412K select  1   0:05  0.00% kdeinit4
```

上部には最近のPID、負荷平均、起動からの時間と現在時刻、プロセス数、CPU状態の割合、メモリ・スワップの状況が並びます。ZFSのARC欄はキャッシュのメモリ使用状況です。原文はキャッシュから読んだデータ量のように説明していますが、掲載例の `Total`、`MFU`、`MRU` などはキャッシュ構成のサイズを示し、そのまま読み取りバイト数やヒット率ではありません。

下部はプロセスごとのPID、ユーザー、CPU時間、メモリなどです。`SIZE` は仮想アドレス空間の大きさ、`RES` は現在メモリ上に常駐する部分の目安であり、単純な「過去に必要だった量」と「今使う量」の比較ではありません。通常は2秒ごとに更新し、`-s` で間隔を変えられます。

<a id="basics-daemons"></a>
### シグナルを送る・プロセスを終了する

`kill(1)` は、動作中のプロセスやデーモンへ**シグナル**を送るコマンドです。名前に反して、用途は強制終了だけではありません。通常は自分のプロセスに送れ、ほかのユーザーのプロセスには権限が必要です。rootは広い操作権限を持ちます。

OSから送るシグナルもあります。不正なメモリアクセスでは `SIGSEGV`、`alarm(3)` で指定した時間の経過では `SIGALRM` が例です。

終了を求めるときは、まず **SIGTERM** を使うと、プログラムが後始末を行う機会を持てます。処理によっては無視・延期されることもあります。**SIGKILL** はプログラム側で捕捉・無視できず、通常はすぐ終了しますが、カーネル内で割り込み不能の待ち状態にある場合は、その待ちが解消するまで終了しないこともあります。原文は利用不能なネットワーク先のファイル読み込みで、約2分のタイムアウト後に終了する例を挙げていますが、待ち時間や復旧条件は状況によります。

`SIGHUP`、`SIGUSR1`、`SIGUSR2` の意味はアプリケーションによって異なります。設定の再読み込みにSIGHUPを使うデーモンなら、停止・再起動による一時中断を避けられる場合がありますが、必ずそのプログラムの文書で確認してください。

**対象PIDとシグナルを実行前に確認し、無関係なプロセスを終了しないでください。** とくにPID 1のinitは特別です。原文は `/bin/kill -s KILL 1` による停止を挙げていますが、推奨手順ではありません。通常の停止・再起動には[shutdown](14-boot.md#boot-shutdown)を使います。

<a id="shells"></a>
## シェル

<a id="shell-env-vars"></a>

シェルはコマンドを受け取り、OSを操作するためのプログラムです。ファイル名の展開、入力行の編集、コマンドの短縮、環境変数などで日常作業を助けます。FreeBSDにはPOSIXシェルの `sh(1)` や、Cシェル系の `tcsh(1)` があり、zshやbashなどはPortsから追加できます。構文や機能が異なるため、好みと用途で選びます。

便利な機能の一つがTabによる補完です。`foobar` と `football` があるとき、`rm foo` まででは両方に一致し、確定できません。候補を表示したり音で知らせたりするシェルもあります。原文は続いてtを入力する例を挙げていますが、それで選ばれるのは `football` のほうです。`foobar` を消したいならbを補い、対象を確かめてください。

**環境変数**は名前と値の組で、起動したプログラムへ設定を引き継ぐために使います。慣習的に大文字の名前を使いますが、小文字が構文上禁止という意味ではありません。

| 名前 | 内容 |
|---|---|
| `USER` | ログインユーザー名。 |
| `PATH` | コマンドを探すディレクトリ。コロン区切り。 |
| `DISPLAY` | Xorgで接続する表示先。 |
| `SHELL` | 通常はログインシェルの指定。今実行中のシェルと必ず同じとは限りません。 |
| `TERM` | 端末の種類と機能を識別する名前。 |
| `TERMCAP` | 端末の制御コードに関する情報。 |
| `OSTYPE` | OSの種類。シェルによって提供の有無が異なります。 |
| `MACHTYPE` | CPUアーキテクチャなどの情報。シェルによって異なります。 |
| `EDITOR` | 通常使うテキストエディタ。 |
| `PAGER` | ページ単位でテキストを読むプログラム。 |
| `MANPATH` | manページを探す場所。コロン区切り。 |

設定の構文はシェルによって違います。csh・tcshでは `setenv` を使います。

```shell
% setenv EDITOR /usr/local/bin/emacs
```

sh・bashでは `export` を使います。

```shell
% export EDITOR="/usr/local/bin/emacs"
```

値を参照するには `$` を前へ付け、たとえば `echo $TERM` で表示します。

`*` などのメタ文字は特別に解釈され、ファイル名の展開に使えます。`echo *` は、一致する名前をシェルが展開してechoへ渡す例です。`ls` と似た一覧になりますが、隠しファイルの扱いや表示方法などまで完全に同じではありません。

特別扱いを止めるにはバックスラッシュでエスケープします。`echo \$TERM` なら、変数の値ではなく文字列 `$TERM` を表示します。

<a id="changing-shells"></a>
### ログインシェルを変更する

`chsh` を実行すると、`EDITOR` で指定したエディタ（原文の既定はvi）が開きます。`Shell:` を新しいシェルの絶対パスへ変えます。エディタを使わず指定するには `-s` を使います。

```shell
% chsh -s /usr/local/bin/bash
```

パスワードを入力して変更し、ログアウトして入り直すと、新しいログインシェルを使えます。

新しいシェルは `/etc/shells` に登録されている必要があります。[Ports](04-ports.md)から導入した場合は通常自動登録されます。導入済みなのに欠けている場合は、実際のパスを確認し、重複登録を避けて追加します。

```shell
# echo /usr/local/bin/bash >> /etc/shells
```

その後 `chsh` をやり直します。

<a id="chapter-03-heading-36"></a>
### リダイレクトとパイプ

シェルはコマンドを起動するだけでなく、入出力をファイルや別のコマンドへつなげます。出力をファイルへ保存する例です。`>` は既存内容を上書きするので、保存先に注意してください。

```shell
% ls > directory_listing.txt
```

逆に、ファイルを入力として渡すには `<` を使います。

```shell
% sort < directory_listing.txt
```

sortが読み込んで並べ替え、結果を画面へ出します。その出力も保存できます。

```shell
% sort < directory_listing.txt > sorted.txt
```

UNIXでは、標準入力（stdin）、標準出力（stdout）、標準エラー出力（stderr）などのファイル記述子を使います。通常は端末に結び付きますが、ファイルやほかのプログラムへ接続できます。エラーメッセージは通常の出力とは別なので、stdoutのリダイレクトだけでは一緒に保存されないことがあります。

パイプ記号 `|` は、前のコマンドの標準出力を次の標準入力へ渡します。

```shell
% cat directory_listing.txt | sort | less
```

この例はファイル内容をsortで並べ替え、lessへ渡して、自分のペースで前後に移動しながら読めるようにします。

<a id="editors"></a>
## テキストエディタ

FreeBSDの設定の多くはテキストファイルの編集で行うため、エディタに慣れておきましょう。基本システムに含まれるものに加え、Portsからも多数選べます。

**ee（easy editor）** は覚えやすいエディタです。`ee ファイル名` で起動すると、画面上部に主な操作が表示されます。`^` はCtrlを表し、`^e` はCtrl+Eです。終了はEscでメニューを開き、**leave editor**を選びます。変更があれば保存するか尋ねられます。

基本システムには `vi(1)` もあり、Portsには `editors/emacs` や `editors/vim` があります。機能が多い分、習得には時間がかかりますが、長期的には作業を効率化できます。

設定変更ツールが自動的に開くエディタは、[環境変数EDITOR](#shells)で変更できます。

<a id="basics-devices"></a>
## デバイスとデバイスノード

ディスク、プリンタ、グラフィックスカード、キーボードなどの機器を**デバイス**と呼びます。起動メッセージの多くは検出したデバイスに関するもので、その写しは `/var/run/dmesg.boot` に保存されます。

名前と番号で区別し、原文の `ada0` は最初のSATAディスク、`kbd0` はキーボードの例です。多くのデバイスへは、`/dev` にある**デバイスノード**という特殊ファイルを介してアクセスします。

<a id="basics-more-information"></a>
## マニュアルページを読む

FreeBSDの詳細な資料の基本はmanページです。多くのプログラムに、動作と引数を説明するリファレンスがあります。

```shell
% man command
```

`command` は調べたい名前へ置き換えます。lsなら次のとおりです。

```shell
% man ls
```

マニュアルは次のセクションに分かれています。

1. 一般ユーザー用コマンド。
2. システムコールとエラー番号。
3. Cライブラリ関数。
4. デバイスドライバ。
5. ファイル形式。
6. ゲームなど。
7. その他の解説。
8. システム管理・運用コマンド。
9. カーネル内部のインターフェース。

同名の項目が複数のセクションにあることもあります。たとえばchmodはコマンドとシステムコールの両方です。コマンドの説明を指定するには次のようにします。

```shell
% man 1 chmod
```

文書中の `chmod(1)` はセクション1のコマンド、`chmod(2)` はセクション2のシステムコールを表します。

名前が分からなければ、説明文のキーワードを検索できます。

```shell
% man -k mail
```

これは `apropos(1)` と同じ用途です。`/usr/sbin` にあるコマンドの短い説明をまとめて読む例です。

```shell
% cd /usr/sbin
% man -f * | more
```

または次のようにします。

```shell
% cd /usr/sbin
% whatis * |more
```

<a id="basics-info"></a>
### GNU Info文書

Free Software Foundation（FSF）由来のアプリケーションには、manページのほか、ハイパーテキスト形式のInfo文書が付く場合があります。`info(1)`、またはEmacsのInfoモードで読みます。利用中の環境に必要なプログラムがあることを確認してください。

```shell
% info
```

`h` で簡単な入門、`?` で操作の早見を表示します。
