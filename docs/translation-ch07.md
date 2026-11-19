# 公式Chapter 7 Network（既存TOC ID なし）の意訳

対象は FreeBSD Handbook の公式 Chapter 7「Network」（既存 TOC ID なし、slug `network`）のみです。既存の `07-desktop.md` 以降は旧 TOC 番号（公式 Chapter 8 以降）のまま維持し、他章には触れません。

## 状態

- **ドラフト**（原文固定・検査器・CI の初期構成を作成済み。各節の意訳を順次進行）

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/network/_index.adoc`（975行、33774バイト）
- 保存先：`handbook/en/ch07/07-network.adoc.txt`（SHA-256: `1184065b01b76c506140ac2dcfd2f5e1b947fef8b2c12f9c94fbea9c0c2bd1f7`）
- 訳文：`handbook/ja/07-network.md`
- マニフェスト：`docs/translation-ch07.json`

## 構成（固定原文）

- 見出し：29（`#` 1、`##` 7、`###` 19、`####` 2）
- アンカー：30（原文の明示ID 27、生成ID 3）
- コード例：57
- 表：2
- 画像：0

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch07_translation.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `git diff --check origin/main...HEAD`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
