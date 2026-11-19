# 公式Chapter 30 Serial Communications（既存TOC ID 29）の意訳

対象は FreeBSD Handbook の公式 Chapter 30「Serial Communications」（既存 TOC ID 29、slug `serialcomms`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜21章、第23〜27章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/serialcomms/_index.adoc`（1219行、49481バイト）
- 保存先：`handbook/en/ch30/30-serialcomms.adoc.txt`（SHA-256: `10508c90d2175ab5e9001bcd9354926a3c88ffc64b05013afd8f05fe5042d1ed`）
- 訳文：`handbook/ja/30-serialcomms.md`
- マニフェスト：`docs/translation-ch30.json`

## 構成と照合結果

- 見出し：28（`#` 1、`##` 6、`###` 21）
- アンカー：33（原文の明示ID 31、生成ID 2）
- コード例：37
- 表：5
- 画像：0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **`cu115200` エントリの速度指定**：`/etc/remote` の例ではエントリ名が `cu115200`（115200bps）となっている一方で設定値が `br#57600` になっています。原文どおり保持し、その旨を訳注で明記しました。
- **相互参照**：本リポジトリで自己校正済みの章（`03-basics.md`、`09-kernelconfig.md`、`14-boot.md`）は相対パス＋明示アンカーへリンクし、章内参照は明示アンカーへリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch30_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/30-serialcomms.md` による GFM 構文解析とブロック数確認（Header 28、CodeBlock 37、Table 5）
- `git diff --check origin/main...HEAD`（警告なし、rc=0）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
