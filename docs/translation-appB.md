# Appendix B Bibliography（参考文献）の意訳

対象は FreeBSD Handbook の「Appendix B. Bibliography（参考文献）」（既存 TOC ID B）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/bibliography/_index.adoc`（94行、5652バイト）
- 保存先：`handbook/en/appB/B-bibliography.adoc.txt`（SHA-256: `70af57a95bbe4533a6f6f40dbb523ea19b8053d85cf4b4700ca5a119c4c49f99`）
- 訳文：`handbook/ja/B-bibliography.md`
- マニフェスト：`docs/translation-appB.json`

## 構成と照合結果

- 見出し：5（`#` 1、`##` 4）
- アンカー：5（すべて原文の明示IDを保持）
- コード例・表・画像：各 0
- 掲載文献・刊行物：全25件（FreeBSD Bibliography 11件、Security Reference 2件、UNIX History 9件、Periodicals, Journals, and Magazines 3件）

原文の AsciiDoc ヘッダ・共有 `include::`（`authors.adoc`、`mirrors.adoc`、`releases.adoc`、`attributes`、`teams.adoc`、`mailing-lists.adoc`、`urls.adoc`、`asciidoctor.adoc`）は翻訳対象外とし、本文の節のみを意訳してその旨を訳注で明記しました。

## 翻訳・表記上の注意点

- 書名・刊行物名は原文の原題をそのまま保持しています（`The Design And Implementation Of The Freebsd Operating System` の大文字小文字や、`FreeBSD Journal` の `ISBN: 978-0-615-88479-0`、URL・`file://localhost/usr/share/misc/bsd-family-tree` も原文どおり保持）。
- 冒頭の `manual pages` は用語集に従い「man ページ」と訳しています。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_appB_translation.py --require-complete`（rc=0）
- `git diff --check origin/main...HEAD`（警告なし、rc=0）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
