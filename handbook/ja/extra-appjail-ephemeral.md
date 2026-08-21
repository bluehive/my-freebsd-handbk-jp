# appjail-ephemeral(7) — 短命（ephemeral）な jail：cattle・pets・jails

> **翻訳状態**: 初訳ドラフト（おまけ章・要校正）  
> **原文**: `appjail-ephemeral(7)` — Miscellaneous Information Manual  
> **上流**: https://man.freebsd.org/cgi/man.cgi?query=appjail-ephemeral&manpath=FreeBSD+14.2-RELEASE+and+Ports  
> **ソース参照**: `handbook/en/extra-appjail-ephemeral.man.txt`（抜粋メモ）／man 全文は上記 URL  
> **manpath 表記**: FreeBSD 14.2-RELEASE and Ports（2024-04-15）  
> **著作権・原著者**: 下記 AUTHORS。本日本語訳は BSD-2-Clause（リポジトリ `LICENSE`）。  
> **位置づけ**: Handbook 本編外の **おまけ章**（AppJail）。Issue #1（jail 量産・データ分離）と相性が良い。

---

## NAME

`appjail-ephemeral` — cattle, pets and jails  
（牛のように扱うサーバ／ペットのように扱うサーバと、jail）

---

## DESCRIPTION（説明）

AppJail には、jail を **cattle（家畜／取り替え可能な群れ）** のように扱うという考え方があり、機能の多くもその前提で設計されています。これが優先事項である一方、FreeBSD 利用者は jail を **pets（ペット／一匹一匹を大事に育てる対象）** のように扱う感覚に縛られがちなことも多く、結果として AppJail は利用者ごとに **両方の流儀** をサポートしています。

「cattle vs. pets」は正式な標準規格ではなく、サーバ（ここでは jail）をどう扱うかという **慣習・たとえ** です。この比喩をはっきり説明する記事として、次が挙げられます。

- [The History of Pets vs Cattle and How to Use the Analogy Properly](https://cloudscaling.com/blog/cloud-computing/the-history-of-pets-vs-cattle/)

本文書では、どちらがあなたに最適か（ニーズと仕事の仕方次第）は論じません。代わりに、AppJail 誕生当初から著者が実質的に適用してきた **「The Ephemeral Concept（短命／一時的であるという考え方）」** に沿って AppJail を使う方法を説明します。FreeBSD・AppJail・動かしているアプリケーションについて十分な知識がある前提で、**責任を持って** この流儀を使ってください。

---

## THE EPHEMERAL CONCEPT（短命という考え方）

ephemeral concept とは、jail を **可能な限り ephemeral（作り直し可能）** に扱え、という意味です。

これは「再起動や jail 停止のたびに jail が消えるべきだ」という意味では **ありません**。  
意味するのは次のことです。

> jail を **作り直したあとも残すべきデータ** と、  
> **残さなくてよい（再生成で足りる）データ** を、はっきり分けている。

何が ephemeral で、何がそうでないか。  
最も単純な ephemeral データの例は、**バイナリ** と、jail を再作成すればまた揃う jail 構成要素全般です。  
壊してはいけないのは **アプリケーションデータ** です。例えば jail 内で DBMS を動かしているなら、そのデータベースは消すべきではありません。

設定ファイル（および類似のもの）は non-ephemeral とみなすこともできますが、多くの場合、アプリケーションデータとの主な違いは **入れ直し方** です。

| 種類 | 典型的な扱い |
|------|----------------|
| 設定ファイルなど | jail を作り直すたびに **コピーし直す**（ただし jail または内部サービス **起動前** に） |
| アプリデータ | 多くの場合 `mount_nullfs(8)` などで **ホスト側から jail 内にマウント** |

---

## IMPLEMENTING THE EPHEMERAL CONCEPT（実装）

AppJail で作った jail に ephemeral concept を使う説明は、bottom-up より **top-down** が簡単です。言い換えると、jail 内のデータディレクトリにホスト側ディレクトリをマウントした jail を作ってみます。

```shell
# mkdir -p .volumes/wwwdir
# appjail makejail -j darkhttpd -f gh+AppJail-makejails/darkhttpd \
    -o virtualnet=":<random> default" \
    -o nat \
    -o fstab="$PWD/.volumes/wwwdir /usr/local/www/darkhttpd"
# ...
# appjail fstab jail darkhttpd
NRO ENABLED  NAME  DEVICE                         MOUNTPOINT                 TYPE    OPTIONS  DUMP  PASS
0   1        -     /home/dtxdf/.volumes/wwwdir    /usr/local/www/darkhttpd   nullfs  rw       0     0
# echo "<h1>Hello!</h1>" > .volumes/wwwdir/index.html
# appjail jail list -j darkhttpd
STATUS  NAME       TYPE  VERSION       PORTS  NETWORK_IP4
UP      darkhttpd  thin  13.3-RELEASE  -      10.0.0.5
# curl http://10.0.0.5
<h1>Hello!</h1>
```

このセッションの結果は自明です。静的 Web サーバ入りの jail を作り、Web サーバが使うディレクトリへホスト側ディレクトリをマウントしました。ディレクトリはホスト上にあるのでファイルを書けます。そこで HTML を書き、接続クライアントに Hello! を見せました。  
ephemeral concept が言うとおり、**残すべきデータとそうでないデータを分離** しました。jail を破棄して作り直してみます。

```shell
# appjail makejail -j darkhttpd -f gh+AppJail-makejails/darkhttpd \
    -o virtualnet=":<random> default" \
    -o nat \
    -o fstab="$PWD/.volumes/wwwdir /usr/local/www/darkhttpd"
# ...
# appjail fstab jail darkhttpd
# appjail jail list -j darkhttpd
# curl http://10.0.0.5
<h1>Hello!</h1>
```

素晴らしい。ephemeral concept を実装できました。簡単ですが、実運用で向き合う問題はまだ出ていません。特に次の **2 点** です。

1. **ファイルシステムのパーミッション**  
2. **中身のあるディレクトリへのホスト側ディレクトリのマウント**

これらは jail 内アプリに影響する場合としない場合があります。上の例では、実行プロセスと同じ UID/GID でファイルを書く必要がなければ影響しません（この例ではその必要はありません）。

### Filesystem Permissions（ファイルシステム権限）

jail 内アプリはデータへ普通に書ける前提で動き、プロセスは多くの場合 **専用ユーザ** で動きます。そのため、その前提なしにホスト側ディレクトリをマウントすべきではありません。  
あらかじめ **UID・GID・ファイルモード・マウントポイント** を知る必要があります。知るのは簡単です。いったん jail を作ってアプリを入れ、必要な情報を調べます。この時点ではディレクトリ設定は不要で、正しい情報が揃う前に設定すべきでもありません。

```shell
# appjail makejail -j rustypaste -f gh+AppJail-makejails/rustypaste \
    -o virtualnet=":<random> default" \
    -o nat
# appjail cmd jexec rustypaste ls -ld /var/db/rustypaste
drwxr-xr-x  5 rustypaste  rustypaste  512 Apr 15 05:37 /var/db/rustypaste
# appjail cmd jexec rustypaste pw usershow rustypaste
rustypaste:*:498:498::0:0:Minimal file upload/pastebin service:/nonexistent:/usr/sbin/nologin
# appjail cmd jexec rustypaste pw groupshow rustypaste
rustypaste:*:498:
```

もちろん上の例では著者がディレクトリを先に知っているので「ズル」です。よく知らないアプリでは、ドキュメントと、付いていれば `rc(8)` スクリプトを読むことを推奨します。

最後に: 多くのサービスは **空のディレクトリ** から始まり、その中にファイルやサブディレクトリを置きます。知るべきは、そのディレクトリが **空か、既にファイルがあるか** です。これは重要です。サービスがそれらのファイルを必要とする場合、ホスト側をそのままマウントすると **重なって** サービスから見えなくなるからです。対処は次節「中身のあるディレクトリへのマウント」を参照。

情報が揃ったら、アプリが必要とする属性でディレクトリを作ります。

```shell
# mkdir -p .volumes/db
# chmod 755 .volumes/db
# chown -f 498:498 .volumes/db
```

同じ makejail に、今作ったディレクトリを指す `fstab` を付けて作り直せます。

```shell
# appjail makejail -j rustypaste -f gh+AppJail-makejails/rustypaste \
    -o virtualnet=":<random> default" \
    -o nat \
    -o fstab="$PWD/.volumes/db /var/db/rustypaste"
# appjail jail list -j rustypaste
# appjail cmd jexec rustypaste cat /var/log/rustypaste.log
# echo "Hello!" | rpaste -s http://10.0.0.7:8000 -
# curl http://10.0.0.7:8000/able-locust.txt
Hello!
```

**まったく同じコマンド** で jail を作り直せば、破棄がなかったかのようにアプリを使えます。

```shell
# appjail makejail -j rustypaste -f gh+AppJail-makejails/rustypaste \
    -o virtualnet=":<random> default" \
    -o nat \
    -o fstab="$PWD/.volumes/db /var/db/rustypaste"
# curl http://10.0.0.7:8000/able-locust.txt
Hello!
```

### Mounting a Directory from the Host to a Directory Containing Data  
（中身のあるディレクトリへホスト側をマウントする）

ホストから jail へファイルやディレクトリを載せる定番は `mount_nullfs(8)` ですが、誤用すると問題になります。  
例えば `A/` に `A/foo.txt`、`B/` に `B/bar.txt` があるとき `mount_nullfs B/ A/` すると、`ls A/` では **`A/bar.txt` だけ** が見えます。`mount_nullfs(8)` の不具合ではなく、こう動く前提で正しく使う必要があります。

つまり、jail 側のファイルをホストへ移してから、いつものようにホスト→jail マウントが必要です。しかも **サービス起動前** に済ませる必要があります。実運用ではサービスは jail 起動直後に立ち上がることが多いので、実質 **jail 起動前** です。

幸い AppJail は `<pseudofs>` 疑似ファイルシステムでこれを容易にします。詳細は `appjail-fstab(1)` を参照。

```shell
# appjail makejail -j mariadb -f gh+AppJail-makejails/mariadb \
    -o virtualnet=":<random> address:10.0.0.70 default" \
    -o nat -- \
      --mariadb_user "wpuser" \
      --mariadb_password "123" \
      --mariadb_database "wordpress" \
      --mariadb_root_password "321"
# appjail makejail -j wordpress -f gh+AppJail-makejails/wordpress \
    -o virtualnet=":<random> default" \
    -o nat -- \
      --wp_db_name "wordpress" \
      --wp_db_user "wpuser" \
      --wp_db_password "123" \
      --wp_db_host "10.0.0.70"
# appjail cmd jexec wordpress ls /usr/local/www/apache24/data/wp-content
index.php      plugins        themes
# mkdir -p .volumes/wp-content
# chown www:www .volumes/wp-content
# appjail makejail -j mariadb -f gh+AppJail-makejails/mariadb \
    -o virtualnet=":<random> address:10.0.0.70 default" \
    -o nat \
    -o fstab="$PWD/.volumes/wp-content /usr/local/www/apache24/data/wp-content <pseudofs>" -- \
      --mariadb_user "wpuser" \
      ...
# （ログ例）Compiling fstab ... Moving .../wp-content/plugins/... -> .volumes/wp-content/...
# appjail fstab jail wordpress
# appjail fstab jail wordpress mounted
```

幸い多くのプログラムはカスタムディレクトリを使え、初期は空、あるいは少数のファイルだけ、という場合が多いです。

---

## VOLUMES（ボリューム）

AppJail における **volume** は、jail 内アプリが生成するデータを保持する仕組みです。特定のファイルシステムに縛られませんが、好ましいのは `nullfs(5)` です。  
とはいえ、毎回モード・UID・GID を直し、マウントポイントを覚え直すのは繰り返し作業です。スクリプトでもできますが、アプリを配布・展開するなら、正式な手段があった方がよいでしょう。

正式な手段が `appjail-volume(1)`（`appjail-fstab(1)` と併用）です。通常これらの仕様はエンドユーザではなく **Makejail を書いた開発者** が作ります。ボリューム仕様はイメージに含めて配布することが多く、その形式で保持されます。

```shell
# mkdir -p .volumes/db
# appjail makejail -j rustypaste -f gh+AppJail-makejails/rustypaste \
    -o virtualnet=":<random> default" \
    -o nat \
    -o fstab="$PWD/.volumes/db rustypaste-db <volumefs>"
# appjail fstab jail rustypaste
# appjail fstab jail rustypaste mounted
# appjail volume list rustypaste
NAME           MOUNTPOINT           TYPE        UID  GID  PERM
rustypaste-db  /var/db/rustypaste   <pseudofs>  498  498  -
# ls -ld .volumes/db
drwxr-xr-x  5 498 498 512 Apr 16 03:09 .volumes/db
```

`<volumefs>` がエンドユーザ向けの作業の多くを引き受けます。ユーザはディレクトリを作ればよく、モード・UID・GID は `appjail-volume(1)` のエントリに従い `appjail-fstab(1)` が設定します。マウント先パスを知らなくてもよく、**ボリューム名** だけで足ります。

---

## UPDATE / UPGRADE（更新／アップグレード）

ここで 「cattle vs. pets」の差が強く出ます。前述のとおり FreeBSD 利用者は jail をかわいいペットのように扱い、つまり jail 上で `freebsd-update(8)` を回すことを期待しがちです。  
**thin jail ではそれはできず**、**thick jail では可能**です。thin jail では `freebsd-update(8)` は release（一部の文書でいう base ディレクトリ）に対して動かします。  
「更新（update）だけ」ならまだしも、問題は **upgrade（メジャーなど大きな上げ）** です。

upgrade は単純な update より複雑です。改変済みシステムに変更を当てるため衝突が起き得ます。thin jail は release/base に結び付くため、さらに面倒です。必要なのは、**アプリとデータを載せた新しい jail** を、**新しい FreeBSD 版の release** で作ることです。  
thick jail でも、ストレージ（現代では問題になりにくい場合もある）や、時間・帯域・CPU など、jail ごとに upgrade するコストが残ります。こうした場面で pets 扱いは現実的でないことが多いです。

ephemeral concept で upgrade するには？  
13.3-RELEASE の release を使う jail を 14.0-RELEASE に上げたいとします。ephemeral に従っているならデータは破棄・再作成後も残るので、**14.0-RELEASE の release で作り直す** だけです。

```shell
# cat << EOF > Makejail
OPTION start
OPTION overwrite=force
OPTION virtualnet=:<random> default
OPTION nat
OPTION pkg=darkhttpd
OPTION fstab=$PWD/.volumes/wwwdir /usr/local/www/darkhttpd

SERVICE darkhttpd oneenable
SERVICE darkhttpd start
EOF
# appjail fetch list | grep -Ee '^ARCH' -e '[0-9]+.[0-9]+-RELEASE'
# appjail makejail -j darkhttpd -o osversion=13.3-RELEASE
# appjail jail list -j darkhttpd
# echo "<h1>Hello!</h1>" > .volumes/wwwdir/index.html
# appjail update release -v 14.0-RELEASE
# appjail makejail -j darkhttpd -o osversion=14.0-RELEASE
# appjail jail list -j darkhttpd
# curl http://10.0.0.2
<h1>Hello!</h1>
```

良い点は、ファイルマージ類を気にしなくてよいことです。一方で、**作り直し後も残すファイル**（特に `/etc`、`/usr/local/etc`、アプリ設定）は意識が必要です。それらは **作成時にだけ** 入れ、変更するならホスト側を直し **jail を作り直す** のが基本です。幸い多くの場合、全設定をいじり倒すわけではありません。

最後に: 古い設定が新しい FreeBSD やアプリ版で意味を持つかは場合によります。後方互換を重視するプロジェクトは多いですが、この点は常に頭に置いてください。

---

## BACKUP / RESTORE（バックアップ／復元）

ボリュームのバックアップに魔法はありません。次を意識します。

- **必要なら jail を止める**  
  多くの場合、jail または内部サービス停止が必要です。常に変わるデータを取ると、正しく戻せないことがあります。整合性が重要です。
- **バックアップ時と同じ形で戻す**  
  データだけでなく **メタデータ**（モード、UID、GID、その他アプリが要するもの）も。`tar(1)` などが頼りになります。
- **適切なバックアップ手段を使う**  
  サービス固有のバックアップツールがあるなら、状況によってはボリューム丸ごとよりそちらがよい場合があります。
- **バックアップを同一システムに置きっぱなしにしない**  
  RAID があっても、同一筐体だけ、は悪手になりがちです。

---

## SEE ALSO（関連）

- `appjail(1)`
- `appjail-fstab(1)`
- `appjail-image(1)`
- `appjail-jail(1)`
- `appjail-makejail(1)`
- `appjail-update(1)`
- `appjail-upgrade(1)`
- `appjail-volume(1)`
- `appjail-makejail(5)`
- `mount_nullfs(8)`

本リポジトリの関連:

- [第16章 Jail](16-jails.md)
- [第17章 OCI コンテナ](17-containers.md)
- [Issue #1: jail + ZFS 量産解析](https://github.com/bluehive/my-freebsd-handbk-jp/issues/1)

---

## AUTHORS（著者）

Jesús Daniel Colmenares Oviedo \<DtxdF@disroot.org\>

（man ページ表記の文字化け `JesAos` は Jesús と解釈して記載）

---

## 翻訳メモ

| 英語 | 採用訳 | 備考 |
|------|--------|------|
| cattle vs. pets | cattle（取り替え可能） vs. pets（手厚く育てる） | 定訳なし。初出で説明 |
| ephemeral | 短命／作り直し可能（ephemeral） | 概念名は英語併記 |
| thin / thick jail | シン／シック jail | glossary と揃える |
| volume | ボリューム | AppJail 用語 |
| Makejail | Makejail | 固有名 |
| `<pseudofs>` / `<volumefs>` | そのまま | AppJail の疑似 FS |

- コマンド例・パスは原文のまま。  
- 本訳は公式 AppJail プロジェクトの正式訳ではありません。  
- Issue #1 の「アプリは clone、データは別 dataset／マウント」と直接つながる読み物です。
