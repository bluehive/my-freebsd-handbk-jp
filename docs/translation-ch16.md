# 公式Chapter 16 Security（既存TOC ID 15）の意訳

対象は FreeBSD Handbook の公式 Chapter 16「Security」（既存 TOC ID 15、slug `security`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜21章、第23〜27章、第33〜35章、Preface と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/security/_index.adoc`（2517行、94868バイト）
- 保存先：`handbook/en/ch16/16-security.adoc.txt`（SHA-256: `ffdcea842b969971bc80f65443abb850d21eacc059c15296aff8bbb8b2862404`）
- 訳文：`handbook/ja/15-security.md`（既存の初訳ドラフトのパスを維持して全面改稿・照合）
- マニフェスト：`docs/translation-ch16.json`

## 旧スナップショットとの差分

- 旧スナップショット `handbook/en/15-security.adoc.txt` は履歴として変更・削除せず残しています。
- 固定原文 `handbook/en/ch16/16-security.adoc.txt` との差分は次のとおりです。
  1. 固定原文には YAML front matter（`title: Chapter 16. Security` 等）および AsciiDoc ヘッダ属性・共有 `include::` が含まれる一方、旧スナップショットでは先頭ヘッダが省略されています。
  2. 旧スナップショットのコードブロック内から、`login.conf` 例の `:passwd_format=sha512:\`・`:passwd_format=blf:\` および `limited:\` 例の `:maxproc=50:\ <1>`・`:tc=default: <2>` の計4行が欠落していました。固定原文ではこれらがすべて揃っています。

## 構成と照合結果

- 見出し：53（`#` 1、`##` 14、`###` 38）
- アンカー：53（原文の明示ID 42、生成ID 11）
- コード例：119
- 表：1（Resource Limits 種別表）
- 画像：0

## 進捗

- 状態：ドラフト（固定原文取得・検査基盤整備完了、各節の改稿・自己校正を順次実施）

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch16_translation.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `git diff --check origin/main...HEAD`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
