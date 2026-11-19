# 公式Chapter 21 Storage（既存TOC ID 20）の意訳

対象は FreeBSD Handbook の公式 Chapter 21「Storage」（既存 TOC ID 20、slug `disks`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜20章、第23〜24章、第26〜27章、Preface と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/disks/_index.adoc`（2491行、97404バイト）
- 保存先：`handbook/en/ch21/21-disks.adoc.txt`（SHA-256: `cc2047bb41f820515868d31b13119b8cc7d38a431428877dbaf13bf83a837d0b`）
- 訳文：`handbook/ja/21-disks.md`
- マニフェスト：`docs/translation-ch21.json`

## 構成と照合結果

- 見出し：50（`#` 1、`##` 12、`###` 35、`####` 2）
- アンカー：51（原文の明示ID 28、生成ID 23）
- コード例：153
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **`ssh -c blowfish` の例**：`dump` を SSH 経由で実行する例では固定原文どおり `ssh -c blowfish` を保持し、近年の OpenSSH では Blowfish 暗号が削除されている旨を訳注で補足しました。
- **`carp-hast-switch` スクリプトの構文**：フェイルオーバー例の `secondary)` 節にある `if ! mount ... then` の直後に本体がなく `else` が続く構文は固定原文どおり保持し、`/bin/sh` では構文エラーとなるため実運用時は修正が必要である旨を訳注で補足しました。
- **過去の記述の保持**：FreeBSD 10.x より前の `atapicam` / `acd0` の記述、および FreeBSD 15.0 で削除された `gbde` の警告・手順は固定原文どおり保持しました。
- **相互参照**：本リポジトリで自己校正済みの章（`03-basics.md`、`09-kernelconfig.md`、`13-config.md`、`19-mac.md`、`23-zfs.md`）は相対パス＋明示アンカーへリンクし、未翻訳章（`partiv`、`advanced-networking`、`network-servers`）は公式 FreeBSD Handbook（英語版）の該当ページへリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch21_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `pandoc --from=gfm --to=json handbook/ja/21-disks.md` による GFM 構文解析とブロック数確認（Header 50、CodeBlock 153、Table 0）
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。

## PR #14 レビュー指摘対応・履歴整理（2026-11-19）

- NOTE / TIP に相当する注記ラベル20か所を `> **注**:` / `> **ヒント**:` に統一し、「原文の NOTE / TIP に相当します。」の定型文を削除。
- `carp-hast-switch` の要約（他方のノードでのプライマリ昇格）を原文どおりに改め、スクリプト実動作との差異を訳注で補足。
- `geli init` の3つのキーファイル例に、原文の「generates」と実際の例との差異を説明する訳注を追記。
- ブランチを1コミットへ集約し、最新 `origin/main` へ rebase。
