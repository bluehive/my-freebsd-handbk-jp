# 公式Chapter 28 DTrace（既存TOC ID 27）の意訳

対象は FreeBSD Handbook の公式 Chapter 28「DTrace」（既存 TOC ID 27、slug `dtrace`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/dtrace/_index.adoc`（286行、13316バイト）
- 保存先：`handbook/en/ch28/28-dtrace.adoc.txt`（SHA-256: `1852b9a5ea44fa362c82617656e31707206cecf4bcdd3e968053f3780bf5bdc8`）
- 訳文：`handbook/ja/28-dtrace.md`
- マニフェスト：`docs/translation-ch28.json`

## 構成と照合結果

- 見出し：6（`#` 1、`##` 5）
- アンカー：6（原文の明示ID 6、生成ID 0）
- コード例：9
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注・原文保持の方針

- **冒頭の訳注**：AsciiDoc フロントマターおよび共有ファイルの `include::` は翻訳対象外であること、掲載コマンドは説明例であり実機実行していないこと、実行例中の `#` は root ユーザーのプロンプトであることを明記しました。
- **過去の記述の保持**：固定原文に含まれる旧バージョンの port 例（`databases/postgresql12-server`、`lang/php74`）や FreeBSD 9.2 / 10.0 の記載、コマンド・出力例は改変せずそのまま保持しています。
- **相互参照**：本リポジトリで自己校正済みの章（`03-basics.md#basics`、`15-security.md#security`、`09-kernelconfig.md#kernelconfig`）へ相対パス＋明示アンカーでリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch28_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `git diff --check origin/main...HEAD`（rc=0、警告なし）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
