# 公式Chapter 35 Advanced Networking（既存TOC ID 34）の意訳

対象は FreeBSD Handbook の公式 Chapter 35「Advanced Networking」（既存 TOC ID 34、`slug: advanced-networking`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（Preface、第1〜14章、第19〜20章、第23〜24章、第26〜27章と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/advanced-networking/_index.adoc`（2394行、103789バイト）
- 保存先：`handbook/en/ch35/35-advanced-networking.adoc.txt`（SHA-256: `609f4547d7051f01f6681be04505d75b7b7f1c663fa07de1dd4457fd4bea1125`）
- 訳文：`handbook/ja/35-advanced-networking.md`
- マニフェスト：`docs/translation-ch35.json`

## 構成と照合結果

- 見出し：45
- アンカー：49（見出し45 + 非見出し4：`routeflags`, `networking-lacp-aggregation-cisco`, `networking-lagg-failover`, `networking-lagg-wired-and-wireless`）
- コード例：130
- 画像：2（`static-routes.png`, `pxe-nfs.png`）
- 表：1

## 進捗状況（ドラフト）

- 状態：ドラフト（翻訳・自己校正中）

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch35_translation.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
