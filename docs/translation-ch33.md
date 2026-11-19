# 公式Chapter 33 Network Serversの意訳

対象は公式Handbookの Chapter 33「Network Servers」（既存 `handbook/TOC.md` の ID 32、`slug: network-servers`）です。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/network-servers/_index.adoc`（3042行、124644バイト）
- 保存先：`handbook/en/ch33/33-network-servers.adoc.txt`（SHA-256: `bd0c56b2ef912bf049cceb1d7ed1718047e195677591e92573e7c9cdade5621a`）
- 訳文：`handbook/ja/33-network-servers.md`
- マニフェスト：`docs/translation-ch33.json`

## 構成（固定原文）

- 見出し：69（`#` 1、`##` 13、`###` 31、`####` 24）
- アンカー：70（原文の明示ID 25、自動付与アンカー 45）
- コード例：143
- 表：7
- 画像：0

原文の AsciiDoc フロントマターおよび共有 `include::` は翻訳対象外とし、本文の節のみを意訳します。

## 進捗

- [x] 原文固定・マニフェスト・検査器・CI（ドラフト設定）・初期訳文作成
- [x] `#network-servers` / `#network-servers-synopsis`（章タイトル・概要）
- [x] `#network-inetd`（inetd スーパーサーバ）
- [x] `#network-nfs`（Network File System (NFS)）
- [x] `#network-nis`（Network Information System (NIS)）
- [x] `#network-ldap`（Lightweight Directory Access Protocol (LDAP)）
- [x] `#network-dhcp`（Dynamic Host Configuration Protocol (DHCP)）
- [x] `#network-dns`（Domain Name System (DNS)）
- [x] `#network-zeroconf`（Zeroconf）
- [x] `#network-apache`（Apache HTTP Server）
- [x] `#network-ftp`（File Transfer Protocol (FTP)）
- [x] `#network-samba`（File and Print Services for Microsoft Windows Clients (Samba)）
- [x] `#network-ntp`（Clock Synchronization with NTP）
- [x] `#network-iscsi`（iSCSI Initiator and Target Configuration）
- [x] 全節自己校正・最終検査

## 訳注で区別した主な原文の仕様・古い記述

- `autofs(5)` 節の本文中の `/host/foobar/usr` と、直前の例・既定の `/net` マウントポイントの違いを訳注で補足しました。
- NIS 節の旧章番号に基づく表番号（表 28.1〜28.3）、`pw useradd smith` 表記、および `login.conf` の `passwd_format=des` の例を訳注で区別しました。
- DHCP 節の `config-network-setup` への相互参照は、上流で独立した `network` 章へ移設されており本リポジトリでは未翻訳のため、公式英語版へリンクし訳注を付けました。
- Apache 節の `mod_php74` / `php74-*`、`mod_python` の記述、`h2h2chttp/1.1` 表記、`report` 表記、および Samba 節の `samba_enable` 表記を訳注で補足しました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch33_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py --require-complete`
- `pandoc --from=gfm --to=json handbook/ja/33-network-servers.md` による GFM 構文解析とブロック数確認（Header 69 / CodeBlock 143 / Table 7）
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。

## 改訂記録

- 2026-11-19: PR #10 レビュー指摘に基づき、第33章の6点（DES 表現、Apache 節の `ServerAdmin` エスケープ記号残骸および `report` 表記の訳注、Samba 節の `passdb backend` / `tdbsam` 表現および `samba_enable` 訳注の補足、NTP 節の 1000 秒超過表現）を修正し、検査を再実行しました。
