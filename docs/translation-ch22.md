# 公式Chapter 22 GEOM: Modular Disk Transformation Framework（既存TOC ID 21）の意訳

対象は FreeBSD Handbook の公式 Chapter 22「GEOM: Modular Disk Transformation Framework」（既存 TOC ID 21、slug `geom`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/geom/_index.adoc`（1305行、50810バイト）
- 保存先：`handbook/en/ch22/22-geom.adoc.txt`（SHA-256: `90c1eb66118e7afafdd9d66e461723c03aa5ca543895a8b32766735de31bbb14`）
- 訳文：`handbook/ja/22-geom.md`
- マニフェスト：`docs/translation-ch22.json`
- 画像：同じ固定コミットの `documentation/static/images/books/handbook/geom/`（`striping.png` 1点、HTTP 200 確認済み）

## 構成と照合結果

- 見出し：25（`#` 1、`##` 9、`###` 15）
- アンカー：25（原文の明示ID 22、生成ID 3）
- コード例：85
- 画像：1（`striping.png`）
- 表：0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **旧来の ATA デバイス名（`adX`：`/dev/ad2`・`/dev/ad3` 等）**：`gstripe` 等の例にある旧来の ATA デバイス名は固定原文のまま保持し、近年の FreeBSD（9.0 以降の CAM ベース ATA）では `ada0` から検出順に `adaY` へ番号が振られ旧名と一致するとは限らないこと、および旧名の互換リンクが FreeBSD 11 で廃止されていることを訳注で補足しました。
- **相互参照**：本リポジトリで自己校正済みの章（`09-kernelconfig.md#kernelconfig`、`21-disks.md#disks`、`33-network-servers.md#network-nfs`）および章内アンカーへリンクし、`extref:{gjournal-desktop}` は公式記事 URL（`https://docs.freebsd.org/en/articles/gjournal-desktop/`）へリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch22_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `pandoc --from=gfm --to=json handbook/ja/22-geom.md` による GFM 構文解析とブロック数確認（Header 25、CodeBlock 85、Table 0）
- `git diff --check origin/main...HEAD`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。

## レビュー反映（PR #16）

2026-11-20 の PR #16 レビュー指摘を受け、`handbook/ja/22-geom.md` の次の 5 点を修正しました。

- 誤訳修正：「メモリイメージ」→「USB メモリ」（原文 `memory stick`）
- 主語の明確化：`ggated`／`ggatec` の説明でリクエスト処理の主体がサーバデーモンであることを明示
- 訳注の訂正：旧来の ATA デバイス名（`adX`）に関する訳注を、9.0 以降の CAM ベース ATA での検出順採番（`adaY`）と旧名との不一致、および FreeBSD 11 での互換リンク廃止に修正
- 訳語のずれ修正：「最も適しています」→「主に適しています」（原文 `mostly suitable`）
- 表記ゆれ統一：「Soft Updates」→「ソフトアップデート」（章内表記に統一）
