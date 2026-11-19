# 公式Appendix D OpenPGP Keys（既存TOC ID D）の意訳

対象は FreeBSD Handbook の公式 Appendix D「OpenPGP Keys」（既存 TOC ID D、slug `pgpkeys`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/pgpkeys/_index.adoc`（75行、2083バイト）
- 保存先：`handbook/en/appD/D-pgpkeys.adoc.txt`（SHA-256: `7d6200e0f9eb409416afa210d4fbd6516dc916666c5026ba7528be2449fb070f`）
- 訳文：`handbook/ja/D-pgpkeys.md`
- マニフェスト：`docs/translation-appD.json`

## 構成と照合結果

- 見出し：6（`#` 1、`##` 1、`###` 4）
- アンカー：6（原文の明示ID 2：`pgpkeys`・`pgpkeys-officers`、生成ID 4：`appendix-D-heading-03`〜`appendix-D-heading-06`）
- コード例：0
- 表・画像：各 0

原文の AsciiDoc フロントマター・文書属性・共有 `include::`（`shared/authors.adoc`、`shared/mirrors.adoc`、`shared/releases.adoc`、`shared/attributes/attributes-en.adoc`、`shared/en/teams.adoc`、`shared/en/mailing-lists.adoc`、`shared/en/urls.adoc`、`shared/asciidoctor.adoc`）および各担当役員の公開鍵ファイル（`documentation/static/pgpkeys/*.key`）の本体は翻訳対象外とし、本文と構成を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **共有インクルード（公開鍵ファイル本体）の扱い**：原文の4つの小節に含まれる `include::{pgpkeys-path}static/pgpkeys/*.key[]`（`security-officer.key`、`core-secretary.key`、`portmgr-secretary.key`、`doceng-secretary.key`）は共有インクルードのため翻訳対象外とし、鍵本体や指紋は転記・改変せず、固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28` の各 `.key` ファイルへの参照と公式の `pgpkeys.txt` / OpenPGP Keys ページへの案内を訳注で明示しました。
- **属性の解決**：見出し中の担当役員名・メールアドレス属性（`{security-officer-name}` 等）は同じ固定コミットの `shared/en/teams.adoc` から、また `extref:{pgpkeys}[PGP Keys]` のリンク先は同じ固定コミットの `shared/en/urls.adoc`（`https://docs.freebsd.org/en/articles/pgpkeys/`）から確認・解決しました。
- **`doceng-secretary@FreeBSD.org` 見出しの表記**：原文の4つ目の小節見出しのみ `{doceng-secretary-name}` と山括弧がなくメールアドレスのみが記載されているため、黙って補完せず原文どおり保持し、訳注で補足しました。
- **`Officers` 見出し直下の本文**：原文では `== Officers` の直下に本文がないため、原文にない説明文を足さず明示的な訳注のみを配置しました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_appD_translation.py --require-complete`（rc=0）
- `git diff --check origin/main...HEAD`（警告なし、rc=0）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
