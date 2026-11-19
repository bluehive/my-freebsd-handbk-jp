# 25 Virtualization（仮想化）の意訳

対象は FreeBSD Handbook の公式 Chapter 25「Virtualization」（既存 TOC ID 24）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜20章、第23〜24章、第26〜27章、Preface と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/virtualization/_index.adoc`（2566行、100586バイト）
- 保存先：`handbook/en/ch25/25-virtualization.adoc.txt`（SHA-256: `b22724e7efe5f3c3c8d48edc51dc551e1e5f0207048c454b362dff956e600979`）
- 訳文：`handbook/ja/25-virtualization.md`
- マニフェスト：`docs/translation-ch25.json`

## 構成（固定原文）

- 見出し：58（`#` 1、`##` 8、`###` 35、`####` 14）
- アンカー：76（見出し58 + 図表等18、すべて原文の明示IDを保持）
- コード例：126
- 画像：38（`documentation/static/images/books/handbook/virtualization/` の固定コミット版を参照）
- 表：1

## 進捗状態

- 状態：ドラフト（翻訳作業中）

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch25_translation.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
