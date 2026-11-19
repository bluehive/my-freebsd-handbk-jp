# 公式Chapter 32 Electronic Mail（既存TOC ID 31）の意訳

対象は FreeBSD Handbook の公式 Chapter 32「Electronic Mail」（既存 TOC ID 31、slug `mail`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜21章、第23〜27章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/mail/_index.adoc`（969行、38378バイト）
- 保存先：`handbook/en/ch32/32-mail.adoc.txt`（SHA-256: `68acd6aa52ac7a2ca5abaf5a9ae4ecadf6277a9cf17675212f09858b83f39385`）
- 画像：同じ固定コミットの `documentation/static/images/books/handbook/mail/`（8枚：`mutt1.png`〜`mutt3.png`、`pine1.png`〜`pine5.png`）
- 訳文：`handbook/ja/32-mail.md`
- マニフェスト：`docs/translation-ch32.json`

## 構成と照合結果

- 見出し：22（`#` 1、`##` 7、`###` 11、`####` 3）
- アンカー：22（原文の明示ID 22、生成ID 0）
- コード例：49
- 画像：8
- 表：0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳・自己校正してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **冒頭訳注**：原文の AsciiDoc フロントマター・文書属性・共有 `include::` が翻訳対象外であること、掲載コマンドが実機実行したものではないこと、および `#` / `%` プロンプトの意味を明記しました。
- **`/etc/sendmail.cf` の表記**：「ドメイン宛てのメール（Mail for a Domain）」節の原文に記載されている `/etc/sendmail.cf` はそのまま保持し、FreeBSD の Sendmail マスター設定ファイルは通常 `/etc/mail/sendmail.cf` に配置される旨を訳注で補足しました。
- **相互参照**：章内リンクは明示アンカー（`#mail-agents`、`#configuring-dragonfly-mail-agent`）へリンクし、未翻訳の付録（`bibliography`）は公式 FreeBSD Handbook（英語版）の該当ページへリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch32_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/32-mail.md` による GFM 構文解析とブロック数確認（Header 22、CodeBlock 49、Table 0、Image 8）
- `git diff --check origin/main...HEAD`（rc=0、警告なし）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
