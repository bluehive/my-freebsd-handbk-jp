# 公式Chapter 7 Network（既存TOC ID なし）の意訳

対象は FreeBSD Handbook の公式 Chapter 7「Network」（既存 TOC ID なし、slug `network`）のみです。既存の `07-desktop.md` 等は旧 TOC 番号（公式 Chapter 8 以降）のまま維持し、他章には触れていません。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/network/_index.adoc`（975行、33774バイト）
- 保存先：`handbook/en/ch07/07-network.adoc.txt`（SHA-256: `1184065b01b76c506140ac2dcfd2f5e1b947fef8b2c12f9c94fbea9c0c2bd1f7`）
- 訳文：`handbook/ja/07-network.md`
- マニフェスト：`docs/translation-ch07.json`

## 構成と照合結果

- 見出し：29（`#` 1、`##` 7、`###` 19、`####` 2）
- アンカー：30（原文の明示ID 27、生成ID 3）
- コード例：57
- 表：2（`reservedip6` の IPv6 予約アドレス表、および `resolv.conf` エントリの無題表）
- 画像：0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **冒頭訳注**：AsciiDoc フロントマター・文書属性・共有 `include::` を翻訳対象外としていること、掲載コマンドや設定例を翻訳作業中に実機実行していないこと、プロンプト記号（`#` が root、`%`・`$` が一般ユーザー）の意味を明記しました。
- **`pciconf` 出力例の `iwm0` と本文の `iwn(4)` の差異**：「ネットワークアダプタの特定」節の出力例では 2 つ目のデバイス名が `iwm0` となっていますが、直後の本文では `iwn(4)` と記載されているため、双方とも原文どおり保持したうえで訳注で差異を明記しました。
- **相互参照**：本リポジトリで自己校正済みの章（`35-advanced-networking.md`、`34-firewalls.md`）は相対パス＋明示アンカーへリンクし、未翻訳の用語集（`glossary#slaac-glossary`）は公式 FreeBSD Handbook（英語版）の該当アンカーへリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch07_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/07-network.md` による GFM 構文解析とブロック数確認（Header 29、CodeBlock 57、Table 2）
- `git diff --check origin/main...HEAD`（rc=0、警告なし）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
