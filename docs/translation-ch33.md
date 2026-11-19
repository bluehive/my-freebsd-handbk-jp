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
- コード例：136
- 表：7
- 画像：0

原文の AsciiDoc フロントマターおよび共有 `include::` は翻訳対象外とし、本文の節のみを意訳します。

## 進捗

- [x] 原文固定・マニフェスト・検査器・CI（ドラフト設定）・初期訳文作成
- [x] `#network-servers` / `#network-servers-synopsis`（章タイトル・概要）
- [x] `#network-inetd`（inetd スーパーサーバ）
- [x] `#network-nfs`（Network File System (NFS)）
- [x] `#network-nis`（Network Information System (NIS)）
- [ ] `#network-ldap`（Lightweight Directory Access Protocol (LDAP)）
- [ ] `#network-dhcp`（Dynamic Host Configuration Protocol (DHCP)）
- [ ] `#network-dns`（Domain Name System (DNS)）
- [ ] `#network-zeroconf`（Zeroconf）
- [ ] `#network-apache`（Apache HTTP Server）
- [ ] `#network-ftp`（File Transfer Protocol (FTP)）
- [ ] `#network-samba`（File and Print Services for Microsoft Windows Clients (Samba)）
- [ ] `#network-ntp`（Clock Synchronization with NTP）
- [ ] `#network-iscsi`（iSCSI Initiator and Target Configuration）
- [ ] 全節自己校正・最終検査

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch33_translation.py`（ドラフト時）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
