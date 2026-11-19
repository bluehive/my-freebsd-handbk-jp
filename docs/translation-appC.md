# 公式Appendix C Resources on the Internet（既存TOC ID C）の意訳

対象は FreeBSD Handbook の公式 Appendix C「Resources on the Internet」（既存 TOC ID C、slug `eresources`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/eresources/_index.adoc`（199行、9853バイト）
- 保存先：`handbook/en/appC/C-eresources.adoc.txt`（SHA-256: `d4b2b63ce017b73f720be55668257a544c214a674005f41669867aeab4efb1b6`）
- 訳文：`handbook/ja/C-eresources.md`
- マニフェスト：`docs/translation-appC.json`

## 構成と照合結果

- 見出し：10（`#` 1、`##` 3、`###` 6）
- アンカー：11（原文の明示ID 8、生成ID 3：`appendix-C-heading-08`〜`10`）
- コード例：0
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::`（`shared/authors.adoc`、`shared/mirrors.adoc`、`shared/releases.adoc`、`attributes`、`teams.adoc`、`mailing-lists.adoc`、`urls.adoc`、`asciidoctor.adoc`）は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注・属性解決の記録

- **冒頭の訳注**：原文の AsciiDoc フロントマターおよび共有ファイルの `include::` を翻訳対象外とした旨を明記しました。
- **本文のない小節への訳注**：`Other UNIX® Newsgroups of Interest`（`appendix-C-heading-09`）および `X Window System`（`appendix-C-heading-10`）は、原文では見出しの下に説明文がなくニュースグループ名のみが記載されています。原文にない説明文を足さず、構造検査の日本語本文要件を満たすため、明示的な訳注を置きました。
- **メーリングリスト属性・外部参照の解決**：`{freebsd-doc}`、`{freebsd-announce}`、`{freebsd-test}`、`{freebsd-chat}`、`{mailing-lists-url}`、および `extref:{freebsd-questions-article}`・`extref:{mailing-list-faq}` は、同じ固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28` の `shared/en/mailing-lists.adoc` および `shared/en/urls.adoc` を参照して URL を解決しました。
- **原文の注意書き**：原文の `[NOTE]` 2か所はいずれも `> **注**:` に統一しました。
- **原文の末尾空白**：固定原文 `handbook/en/appC/C-eresources.adoc.txt` の 109 行目には上流由来の空白 1 文字のみの行がありますが、原文改変禁止の方針に従いそのまま保持しています。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_appC_translation.py --require-complete`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/C-eresources.md` による GFM 構文解析とブロック数確認（Header 10、CodeBlock 0、Table 0、BulletList 11、BlockQuote 5）
- `git diff --check origin/main...HEAD`（rc=0、警告なし）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
