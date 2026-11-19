# 公式Chapter 16 Security（既存TOC ID 15）の意訳

対象は FreeBSD Handbook の公式 Chapter 16「Security」（既存 TOC ID 15、slug `security`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜21章、第23〜27章、第33〜35章、Preface と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/security/_index.adoc`（2183行、94868バイト）
- 保存先：`handbook/en/ch16/16-security.adoc.txt`（SHA-256: `ffdcea842b969971bc80f65443abb850d21eacc059c15296aff8bbb8b2862404`）
- 訳文：`handbook/ja/15-security.md`（既存の初訳ドラフトのパスを維持して全面改稿・照合）
- マニフェスト：`docs/translation-ch16.json`

## 旧スナップショットとの差分

- 旧スナップショット `handbook/en/15-security.adoc.txt` は履歴として変更・削除せず残しています。
- 固定原文 `handbook/en/ch16/16-security.adoc.txt` との差分は次のとおりです。
  1. 固定原文には YAML front matter（`title: Chapter 16. Security` 等）および AsciiDoc ヘッダ属性・共有 `include::` が含まれる一方、旧スナップショットでは先頭ヘッダが省略されています。
  2. 旧スナップショットのコードブロック内から、`login.conf` 例の `:passwd_format=sha512:\`・`:passwd_format=blf:\` および `limited:\` 例の `:maxproc=50:\ <.>`・`:tc=default: <.>` の計4行が欠落していました。固定原文ではこれらがすべて揃っています。

## 構成と照合結果

- 見出し：53（`#` 1、`##` 14、`###` 38）
- アンカー：53（原文の明示ID 42、生成ID 11）
- コード例：119
- 表：1（Resource Limits 種別表）
- 画像：0

## 進捗

- 状態：自己校正済（意訳）。全53見出し・53アンカー・119コード例・1表を固定原文と照合し、欠落していた節（`mtree` 検証、TCP Wrappers、ACL、Capsicum、Process Accounting、Resource Limits、セキュリティ勧告末尾）とコード例を復元しました。

## 訳注で区別した原文の仕様・注意点

- **冒頭訳注**：AsciiDoc フロントマター・文書属性・共有 `include::` を翻訳対象外としていること、コマンド例は説明用であり実機実行していないこと、プロンプト記号（`#` / `%` / `$`）の意味を明記しました。
- **`crypt(3)` のハッシュプレフィックス**：原文では MD5 を `$`、SHA256 と SHA512 の双方を `$6$` と記載していますが、原文どおり保持したうえで `crypt(3)` における実際の識別プレフィックス（MD5 は `$1$`、SHA256 は `$5$`、SHA512 は `$6$`）を訳注で補足しました。
- **`mtree` 検証の出力先パス**：直前のコマンド例では `/home/user/.bin_chksum_output` へ出力している一方、確認コマンド例では `/root/.bin_chksum_output` を参照している点を原文どおり保持し、訳注で区別しました。
- **自己署名証明書の出力先**：本文ではカレントディレクトリに作成する旨が書かれている一方、コマンド例では `-keyout` / `-out` で `/etc/ssl/` 配下を直接指定している点を原文どおり保持し、訳注で補足しました。
- **相互参照**：本リポジトリで自己校正済みの章（`19-mac.md`、`20-audit.md`、`33-network-servers.md`、`34-firewalls.md`）は相対パス＋明示アンカーへリンクし、未翻訳章（`pgpkeys`、記事 `vpn-ipsec`）は公式 FreeBSD ドキュメント（英語版）へリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch16_translation.py --require-complete`
- `pandoc --from=gfm --to=json handbook/ja/15-security.md` による GFM 構文解析とブロック数確認（Header 53、CodeBlock 119、Table 1）
- `git diff --check origin/main...HEAD`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
