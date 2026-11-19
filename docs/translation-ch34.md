# 第34章 Firewalls の意訳

対象は FreeBSD Handbook 公式 Chapter 34「Firewalls」（既存 TOC ID 33、slug: `firewalls`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜20章、第23〜24章、第26〜27章、Preface と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/firewalls/_index.adoc`（2691行、123801バイト）
- 保存先：`handbook/en/ch34/34-firewalls.adoc.txt`（SHA-256: `59d166966e604c5564548036577be575aa27922f9a8a516761e16aa83cd5229a`）
- 訳文：`handbook/ja/34-firewalls.md`
- マニフェスト：`docs/translation-ch34.json`

## 構成（原文）

- 見出し：43（`#` 1、`##` 6、`###` 23、`####` 12、`#####` 1）
- アンカー：43（明示ID 24、自動生成ID 19）
- コード例：152
- 表：1
- 画像：0

## 進捗状況（自己校正済）

- [x] 01–03: 冒頭・Introduction・Firewall Concepts
- [x] 04–16: PF（Packet Filter）
- [x] 17–28: IPFW
- [x] 29–35: IPFILTER (IPF)
- [x] 36–43: Blacklistd

## 訳注で区別した原文の仕様・注意点

- **AsciiDoc ヘッダ・共有 `include::` の除外**：フロントマターや文書属性、共有ファイルの `include::` は翻訳対象外とし、本文の節のみを意訳しました。
- **ルールスクリプトのシェル構文**：`Building a Rule Script` 節で原文が `sh(1)`・`csh(1)`・`tcsh(1)` 互換と説明している箇所について、掲載スクリプトが `#!/bin/sh` の `VAR="value"` 代入構文を用いている点を訳注で補足しました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch34_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py --require-complete`
- `pandoc --from=gfm --to=json handbook/ja/34-firewalls.md` による GFM 構文解析（43見出し・152コードブロック・1表）
- `git diff --check`

FreeBSD 実機での動作確認（`pfctl`・`ipfw`・`ipf`・`blocklistd` 等のコマンド実行）、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
