<a id="printing"></a>
# 第10章 印刷

> **状態:** 意訳ドラフト。固定原文の全節・表・コマンドとフィルターを照合しています。実機プリンターでの出力は未検証です。
> **原文:** [Printing](https://docs.freebsd.org/en/books/handbook/printing/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/10-printing.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **章番号:** 本リポジトリでは第10章、固定上流では第11章です。
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

印刷には「データをプリンターへ届けること」と「プリンターが理解できる形式へすること」の2つが必要です。本章は主に従来のLPDを扱い、末尾でCUPSなどを案内します。Ghostscript 9などの古いパッケージ名や機器依存の例は原文のままです。実際の提供版・接続先に合わせてください。`#` はroot、`%` は一般ユーザーのプロンプトです。

<a id="printing-quick-start"></a>
## ASCIIテキストを印刷してみる

ここでは、プレーンなASCIIを直接印刷できるプリンターを使います。ほかの形式は[フィルター](#printing-lpd-filters)で変換します。日本語などASCII以外の文字をそのまま正しく印刷できることまでは意味しません。

1. 印刷待ちのファイルを置くスプールディレクトリを作ります。

```shell
# mkdir -p /var/spool/lpd/lp
# chown daemon:daemon /var/spool/lpd/lp
# chmod 770 /var/spool/lpd/lp
```

2. rootで `/etc/printcap` にプリンターを登録します。USB接続の例です。

```text
lp:\
lp=/dev/unlpt0:\
sh:\
mx#0:\
sd=/var/spool/lpd/lp:\
lf=/var/log/lpd-errs:
```

パラレル接続ならデバイス行を次へ変えます。

```text
:lp=/dev/lpt0:\
```

ネットワークへ直接つながるプリンターなら次を使えます。

```text
:lp=:rm=network-printer-name:rp=raw:\
```

`network-printer-name` を実際のDNSホスト名へ置き換えます。

3. `/etc/rc.conf` でLPDを有効にします。

```text
lpd_enable="YES"
```

サービスを起動します。

```shell
# service lpd start
Starting lpd.
```

4. テストします。

```shell
# printf "1. This printer can print.\n2. This is the second line.\n" | lpr
```

2行目が左端に戻らず階段状になる場合は[改行の変換](#printing-lpd-filters-stairstep)を確認します。

以後はlprへファイル名を指定するか、出力をパイプで渡せます。

```shell
% lpr textfile.txt
% ls -lh | lpr
```

<a id="printing-connections"></a>
## プリンターへの接続

<a id="printing-connections-usb"></a>
<a id="printing-connections-parallel"></a>
<a id="printing-connections-serial"></a>
<a id="printing-connections-network"></a>

USB、パラレル、ネットワーク、まれにシリアルなどの接続があります。FreeBSDはこれらを扱えます。

**USB**

検出されると通常 `/dev/ulpt0` と `/dev/unlpt0` ができます。どちらへ送ってもプリンターへ届きますが、ulpt0はジョブの後にUSBポートをリセットします。一部機種では問題になるため、リセットしないunlpt0を使うことが一般的です。

**パラレル（IEEE 1284）**

デバイスは `/dev/lpt0` です。自動検出ではなく、接続されていなくても存在します。古いポートなので最近の機種にはない場合もあります。USB変換ならUSBプリンターとして扱え、プリントサーバー機器でネットワークへつなぐ方法もあります。

**シリアル（RS-232）**

特殊用途以外では少ない接続です。配線・コネクターは機種ごとに異なります。マザーボード内蔵なら `/dev/cuau0`・`/dev/cuau1`、USB変換なら `/dev/cuaU0` などになります。通信速度とパリティなどを合わせる必要があり、原文のよくある例は9600bps・パリティなしです。

**ネットワーク**

DNSホスト名を確認します。DHCPでIPが変わる場合はDNS側も更新される必要があり、問題を避けるため固定IPを使うことも多くあります。

多くはLPDプロトコルに対応し、キュー名を指定できます。`raw` はそのまま、`text` は改行へ復帰文字を加えるなど、キューによって処理が異なる場合があります。また、TCP 9100へ直接送ったデータを印刷できる機種も多くあります。

<a id="printing-connections-summary"></a>
### 接続方式の選び方

原文では、有線ネットワークが共有しやすく設定・速度の面でも扱いやすく、直接つなぐならUSBが簡単と説明されています。パラレルはケーブル長や速度の制限があり、シリアルは配線・速度・パリティの調整が必要なので、より複雑です。

<a id="printing-pdls"></a>
## プリンターが理解するデータ形式

<a id="print-pdls-ascii"></a>
<a id="print-pdls-postscript"></a>
<a id="print-pdls-pcl"></a>
<a id="print-pdls-host-based"></a>

ページの内容をプリンターへ伝える形式を、ページ記述言語（PDL）と呼びます。

**ASCII**

文字Aを送るとAが印刷される、単純な文字列です。フォントやプロポーショナルな字間などの細かい書式は指定できません。その分、変換をほとんどせず送れます。ただし安価な機種の中にはASCIIを直接印刷できないものもあります。

**PostScript**

ページを描画するプログラムとして記述し、フォントや図を扱えます。通常はアプリが生成するため、利用者がプログラムを書く必要はありません。対応機能を省いて価格を下げた機種もあります。

**PCL（Printer Command Language）**

ASCIIへ書式・フォント・図形のエスケープシーケンスを加えたものです。PCL5のほか、後発のPCL6／PCLXLに対応する機種があります。高速化できる場合がありますが、送る形式は機器が対応するものへ合わせます。

**ホストベース方式**

プリンター本体の処理装置やメモリを小さくし、文字や図のビットマップをコンピューター側のドライバーで作って送ります。プレーンテキストを直接印刷することはできません。独自・非公開の通信方式だと、対応OSが限られる場合があります。

<a id="print-pdls-table"></a>
### PostScriptから別の形式へ変換する

<a id="print-pdls-ps-to-other-tbl"></a>

PortsのアプリやFreeBSDのツールにはPostScript出力を作るものがあります。原文で挙げられた変換先とツールは次のとおりです。

| 出力形式 | 原文のPorts名 | 設定例 |
|---|---|---|
| PCL／PCL5 | `print/ghostscript9-base` | 白黒 `-sDEVICE=ljet4`、カラー `-sDEVICE=cljet5` |
| PCLXL／PCL6 | `print/ghostscript9-base` | 白黒 `-sDEVICE=pxlmono`、カラー `-sDEVICE=pxlcolor` |
| ESC/P2 | `print/ghostscript9-base` | `-sDEVICE=uniprint` |
| XQX | `print/foo2zjs` | 原文の追加指定なし |

古いGhostscriptのport名は、実際の提供版・対応ドライバーを確認して読み替えます。

<a id="print-pdls-summary"></a>
### 対応形式を確認する

原文は、PostScript対応機なら変換が少なく簡単で、次にPCL対応機が扱いやすいと説明しています。Ghostscriptで変換すれば、PCL機でもPostScriptの出力を利用できます。両形式へ直接対応する機種の多くはASCIIにも対応します。

従来型のインクジェットなどはPostScript／PCLを持たず、ASCIIや別のPDLを使う場合があります。Ghostscriptが対応する機種もありますが、ページ全体の画像を送ると転送・印刷が遅くなりがちです。

ホストベース機は独自PDLのため設定が難しく、利用できないものもあります。実際の機種のPDLは [OpenPrinting](http://www.openprinting.org/printers)などで確認します。原文は対応の明らかな機種を選ぶ方が容易だとしています。

<a id="printing-direct"></a>
## データを直接送って印刷する

時々印刷するだけなら、キューを設定せず直接デバイスへ送る方法もあります。sample.txtをUSBへ送る例です。

```shell
# cp sample.txt /dev/unlpt0
```

ネットワーク機でTCP 9100に対応する場合は `nc(1)` を使えます。ホスト名netlaserの例です。

```shell
# nc netlaser 9100 < sample.txt
```

いずれも、プリンターがそのファイル形式を理解できることが前提です。

<a id="printing-lpd"></a>
## LPDで印刷を待ち行列へ入れる

印刷をバックグラウンドで進める仕組みをスプーリングと呼びます。遅い印刷の完了を待たず、ほかの作業を続けられます。FreeBSDには `lpd(8)` があり、ジョブの投入は `lpr(1)` で行います。

<a id="printing-lpd-setup"></a>
### LPDの初期設定

ジョブの保存先を作り、所有者とアクセス権を設定します。ほかの利用者が内容を読めないようにします。

```shell
# mkdir -p /var/spool/lpd/lp
# chown daemon:daemon /var/spool/lpd/lp
# chmod 770 /var/spool/lpd/lp
```

`/etc/printcap` に、名前・接続先・設定を登録します。

```text
lp:\
	:lp=/dev/unlpt0:\
	:sh:\
	:mx#0:\
	:sd=/var/spool/lpd/lp:\
	:lf=/var/log/lpd-errs:
```

- `lp`: プリンター名。lprは `-P` で指定しなければ既定のlpへ送ります。
- `lp=`: 接続先のデバイス。接続方式に合う値へ変えます。
- `sh`: ジョブ先頭のヘッダーページを抑制します。
- `mx#0`: ジョブサイズの上限を設けません。
- `sd=`: このプリンター用のスプールディレクトリ。プリンターごとに分けます。
- `lf=`: エラーの記録先です。

書式を検査します。

```shell
# chkprintcap
```

問題があれば直してから、rc.confへ追加します。

```text
lpd_enable="YES"
```

サービスを起動します。

```shell
# service lpd start
```

<a id="printing-lpd-lpr"></a>
### lprで印刷する

ファイル名を渡す方法と、標準入力から渡す方法があります。以下はどちらもdoc.txtを既定のプリンターへ送ります。

```shell
% lpr doc.txt
% cat doc.txt | lpr
```

別のプリンターは `-P` で指定します。laserの例です。

```shell
% lpr -Plaser doc.txt
```

<a id="printing-lpd-filters"></a>
### 入力フィルターで形式を変換する

これまでの例はファイルの内容をそのまま送っていました。プリンターが理解できない形式なら、入力フィルターで変換します。ASCIIからPostScript／PCLへの変換だけでなく、ページ番号やソースコードの強調なども追加できます。

ファイル作成前に `su(1)` などでrootになります。`/etc/printcap` の `if=` が入力フィルターを指定します。lf2crlfを使う例です。

```text
lp:\
	:lp=/dev/unlpt0:\
	:sh:\
	:mx#0:\
	:sd=/var/spool/lpd/lp:\
	:if=/usr/local/libexec/lf2crlf:\
	:lf=/var/log/lpd-errs:
```

printcapの行末のバックスラッシュは行継続です。実際にはコロンで区切られた1本の長いエントリであり、次の1行でも同じ意味になります。

```text
lp:lp=/dev/unlpt0:sh:mx#0:sd=/var/spool/lpd/lp:if=/usr/local/libexec/lf2crlf:lf=/var/log/lpd-errs:
```

<a id="printing-lpd-filters-stairstep"></a>
#### テキストが階段状に印刷される場合

FreeBSDのテキストの改行は通常LFだけです。LFで紙を進めても左端へ戻らないプリンターでは、次のようにずれていきます。

```text
A printed file looks
                    like the steps of a staircase
                                                 scattered by the wind
```

LFへCRを加えるフィルターを `/usr/local/libexec/lf2crlf` に作ります。

```text
#!/bin/sh
CR=$'\r'
/usr/bin/sed -e "s/$/${CR}/g"
```

実行できる権限を付けます。

```shell
# chmod 555 /usr/local/libexec/lf2crlf
```

printcapへ入力フィルターとして指定します。

```text
:if=/usr/local/libexec/lf2crlf:\
```

同じテキストを再印刷し、各行が左端から始まることを確かめます。

<a id="printing-lpd-filters-enscript"></a>
#### Enscriptでテキストを整形する

GNU EnscriptはテキストをPostScriptへ変換し、ページ番号や長い行の折り返しなどを加えます。用紙に合わせて `print/enscript-letter` または `print/enscript-a4` を導入します。

`/usr/local/libexec/enscript` を作ります。

```text
#!/bin/sh
/usr/local/bin/enscript -o -
```

実行可能にします。

```shell
# chmod 555 /usr/local/libexec/enscript
```

printcapへ指定します。

```text
:if=/usr/local/libexec/enscript:\
```

PostScript対応機へプレーンテキストを送って試します。

<a id="printing-lpd-filters-ps2pcl"></a>
#### PostScriptをPCL機で印刷する

PostScriptを生成するアプリは多い一方、プリンターがASCII／PCLしか理解しない場合があります。GhostscriptでPCLへ変換してから送れます。原文のPorts名は `print/ghostscript9-base` ですが、実際に利用する版の提供状況を確認します。

`/usr/local/libexec/ps2pcl` を作ります。

```text
#!/bin/sh
/usr/local/bin/gs -dSAFER -dNOPAUSE -dBATCH -q -sDEVICE=ljet4 -sOutputFile=- -
```

実行可能にします。

```shell
# chmod 555 /usr/local/libexec/ps2pcl
```

printcapに指定すると、このスクリプトへ渡ったPostScriptがPCLへ変換されます。

```text
:if=/usr/local/libexec/ps2pcl:\
```

原文の小さなPostScriptテストです。

```shell
% printf "%%\!PS \n /Helvetica findfont 18 scalefont setfont \
72 432 moveto (PostScript printing successful.) show showpage \004" | lpr
```

<a id="printing-lpd-filters-smart"></a>
#### 入力形式を判定するフィルター

PostScriptの先頭は通常 `%!` です。これを判定し、PostScriptならそのまま、テキストならEnscriptで変換すると便利です。PostScriptプリンター用に `/usr/local/libexec/psif` を作る例です。

```text
#!/bin/sh
#
#  psif - Print PostScript or plain text on a PostScript printer
#
IFS="" read -r first_line
first_two_chars=`expr "$first_line" : '\(..\)'`

case "$first_two_chars" in
%!)
    # %! : PostScript job, print it.
    echo "$first_line" && cat && exit 0
    exit 2
    ;;
*)
    # otherwise, format with enscript
    ( echo "$first_line"; cat ) | /usr/local/bin/enscript -o - && exit 0
    exit 2
    ;;
esac
```

実行可能にします。

```shell
# chmod 555 /usr/local/libexec/psif
```

printcapへ指定します。

```text
:if=/usr/local/libexec/psif:\
```

PostScriptとテキストの両方を印刷して、判定と出力を確認します。

<a id="printing-lpd-queues"></a>
### 1台に複数のキューを用意する

printcapのエントリは、厳密にはプリンターそのものではなくキューの定義です。1台に複数キューを作り、異なるフィルターを使えます。

ネットワーク上のPostScriptレーザープリンターへ、テキスト用とPostScript直接印刷用を作る例です。

```text
textprinter:\
	:lp=9100@officelaser:\
	:sh:\
	:mx#0:\
	:sd=/var/spool/lpd/textprinter:\
	:if=/usr/local/libexec/enscript:\
	:lf=/var/log/lpd-errs:

psprinter:\
	:lp=9100@officelaser:\
	:sh:\
	:mx#0:\
	:sd=/var/spool/lpd/psprinter:\
	:lf=/var/log/lpd-errs:
```

`textprinter` はEnscriptで整形し、`psprinter` は変換せず送ります。キューごとに専用のスプールディレクトリを用意します。この方法で、通常の片面用と、両面印刷の命令を加えるフィルターを通す両面用なども分けられます。

<a id="printing-lpd-monitor"></a>
### ジョブとプリンターを監視・操作する

ジョブの確認・削除や、キューの受付・印刷の開始と停止には、以下のツールを使います。

<a id="printing-lpd-monitor-lpq"></a>
#### lpq：待ち行列の確認

指定プリンターのジョブを確認します。

```shell
% lpq -Plp
Rank   Owner      Job  Files                                 Total Size
1st    jsmith     0    (standard input)                      12792 bytes
```

全プリンターのローカルキューを確認します。

```shell
% lpq -a
lp:
Rank   Owner      Job  Files                                 Total Size
1st    jsmith     1    (standard input)                      27320 bytes

laser:
Rank   Owner      Job  Files                                 Total Size
1st    jsmith     287  (standard input)                      22443 bytes
```

> **訳注:** 原文は「自分のジョブだけが表示される」としていますが、FreeBSDの [lpq(1)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/lpr/lpq/lpq.1) は、引数で絞らなければキュー内の全ジョブを報告すると説明しています。ユーザー名やジョブ番号を引数にすると絞り込めます。他人のジョブが見えないことを前提にした保護機能としては扱いません。

<a id="printing-lpd-monitor-lprm"></a>
#### lprm：ジョブの削除

一般ユーザーが削除できるのは自分のジョブだけです。rootは任意のジョブや全ジョブを削除できます。

指定プリンターの全待機ジョブをrootで消す例です。

```shell
# lprm -Plp -
dfA002smithy dequeued
cfA002smithy dequeued
dfA003smithy dequeued
cfA003smithy dequeued
dfA004smithy dequeued
cfA004smithy dequeued
```

単体を消す場合はlpqで番号を調べます。

```shell
% lpq
Rank   Owner      Job  Files                                 Total Size
1st    jsmith     5    (standard input)                      12188 bytes

% lprm -Plp 5
dfA005smithy dequeued
cfA005smithy dequeued
```

<a id="printing-lpd-monitor-lpc"></a>
#### lpc：受付と印刷の制御

`lpc(8)` に操作名とプリンター名を渡します。`all` は全プリンターです。一般ユーザーは状態の閲覧、rootは状態の変更を行えます。

全体の状態を表示します。

```shell
% lpc status all
lp:
	queuing is enabled
	printing is enabled
	1 entry in spool area
	printer idle
laser:
	queuing is enabled
	printing is enabled
	1 entry in spool area
	waiting for laser to come up
```

新規ジョブの受付だけを止め、再開する例です。

```shell
# lpc disable lp
lp:
	queuing disabled
# lpc enable lp
lp:
	queuing enabled
```

受付を続けたまま印刷を止め、再開する例です。

```shell
# lpc stop lp
lp:
	printing disabled
# lpc start lp
lp:
	printing enabled
	daemon started
```

障害後にプリンター側の処理を再起動します。

```shell
# lpc restart lp
lp:
	no daemon to abort
	printing enabled
	daemon restarted
```

受付と印刷を止め、利用者向けの説明も設定します。

```shell
# lpc down lp Repair parts will arrive on Monday
lp:
	printer and queuing disabled
	status message is now: Repair parts will arrive on Monday
```

停止中のものを再度有効にします。

```shell
# lpc up lp
lp:
	printing enabled
	daemon started
```

ほかの操作とオプションはlpcのmanページを確認します。

<a id="printing-lpd-shared"></a>
### プリンターを共有する

学校や職場などで複数ユーザーが共有する場合、別名や区切りページを用意すると運用しやすくなります。

<a id="printing-shared-aliases"></a>
#### 利用者向けの別名を付ける

printcapの最初の行に、縦棒で区切って別名を追加できます。

```text
lp|repairsprinter|salesprinter:\
```

営業部はsalesprinterとして印刷できます。

```shell
% lpr -Psalesprinter sales-report.txt
```

修理部はrepairsprinterを使えます。

```shell
% lpr -Prepairsprinter repairs-report.txt
```

どちらも同じ1台へ送ります。後で営業部専用のプリンターを増やした場合、salesprinterの別名を共有機から外し、新しいエントリの名前にできます。利用者は同じコマンドを使い続けられます。

<a id="printing-shared-headers"></a>
#### ヘッダーページを使う

混雑した共有プリンターでは、利用者名・文書名をジョブの前に印刷するページが、取り違えの防止に役立ちます。バナー／区切りページとも呼びます。

USB・パラレル・シリアルの直接接続では、printcapの `sh`（Suppress Header）の行を削除して有効にします。ヘッダーはLFだけを使うため、階段状になる機種では `/usr/share/examples/printing/hpif` を利用できます。これはPCL機へ、LFを受けたらCRとLFの両方を行う設定を送ります。

ネットワークプリンターのヘッダーは機器自身で設定します。原文ではこの場合printcapのヘッダー指定は無視され、操作パネルやWeb設定画面で構成すると説明されています。

<a id="printing-lpd-references"></a>
### 参考資料

サンプルは `/usr/share/examples/printing/` にあります。原文は「4.3BSD Line Printer Spooler Manual」の `/usr/share/doc/smm/07.lpd/paper.ascii.gz` も案内しています。

関連するmanページは `printcap(5)`、`lpd(8)`、`lpr(1)`、`lpc(8)`、`lprm(1)`、`lpq(1)` です。古い文書パスは導入内容によって存在しない場合があります。

<a id="printing-other"></a>
## ほかの印刷システム

ベースのLPD以外にも、追加のプロトコルや機能を提供する印刷システムがあります。

<a id="printing-other-cups"></a>
### CUPS

多くのOSで使われる印刷システムです。FreeBSDでの導入・設定は別記事の [CUPS](https://docs.freebsd.org/en/articles/cups/)を参照してください。

<a id="printing-other-hplip"></a>
### HPLIP

HPの多くのインクジェット・レーザープリンターに対応します。Portsは `print/hplip` で、FreeBSD向けの導入処理をまとめています。[公式情報](https://developers.hp.com/hp-linux-imaging-and-printing)と[設定・導入案内](https://developers.hp.com/hp-linux-imaging-and-printing/install)も参照できます。

<a id="printing-other-lprng"></a>
### LPRng

LPDを拡張した代替システムです。Portsは `sysutils/LPRng`、文書は [LPRng公式サイト](https://lprng.sourceforge.net/)にあります。
