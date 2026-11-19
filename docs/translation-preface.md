# 00 Preface（序文）の意訳

対象は FreeBSD Handbook の「Preface（序文）」のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜20章、第23〜24章、第26〜27章と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/preface/_index.adoc`（333行、22727バイト）
- 保存先：`handbook/en/preface/00-preface.adoc.txt`（SHA-256: `87c44a462d614081a4f953f42364eb7e18c2d079896c4b7fe3da2acd6c142703`）
- 訳文：`handbook/ja/00-preface.md`
- マニフェスト：`docs/translation-preface.json`

## 構成と照合結果

- 見出し：12（`#` 1、`##` 8、`###` 3）
- アンカー：12（すべて原文の明示IDを保持）
- コード例：3（`preface-conv-examples` の `C:\>`・`#`・`%` の3例、原文のまま保持）
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::`（`authors.adoc`、`mirrors.adoc`、`releases.adoc`、`attributes`、`teams.adoc`、`mailing-lists.adoc`、`urls.adoc`、`asciidoctor.adoc`）は翻訳対象外とし、本文の節のみを意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **Organization of This Book（本書の構成）の一覧欠落**：同じ固定コミットの `book.adoc` には `network`・`containers`・`serialcomms` の3章が存在しますが、原文 `preface/_index.adoc` の一覧からは欠落しています。補完して書き足さず原文どおり訳出し、欠落している事実と `book.adoc` への参照を訳注で示しました。
- **過去の記述の保持**：`Installing FreeBSD` の「FreeBSD 9._x_ 以降」、`Electronic Mail` の `sendmail` 中心の説明、`Obtaining FreeBSD` の CDROM/DVD 記述、`Fourth Edition` の `man:hier`（セクション番号省略）は原文どおり扱い、必要に応じて訳注で補足しました。
- **コマンド例とプロンプト**：`tools\fdimage floppies\kern.flp A:` と `dd if=kern.flp of=/dev/fd0` はプロンプト表記を示すための歴史的な例であり、作業中の実行は行っていません。`C:\>`・`#`・`%` がプロンプトであること、および FreeBSD 14 以降の既定ユーザーシェルが `sh(1)` であることを訳注で補足しました。
- **相互参照**：本リポジトリで自己校正済みの章（`01`〜`14`, `16`, `19`〜`20`, `23`〜`24`, `26`〜`27`）は相対パス＋明示アンカーへリンクし、未翻訳章およびアンカー未整備のドラフト章（第15章 Security）は公式 FreeBSD Handbook（英語版）の該当ページへリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_preface_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py --require-complete`
- `pandoc --from=gfm --to=json handbook/ja/00-preface.md` による GFM 構文解析とブロック数確認
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
