# 公式Chapter 31 PPP（既存TOC ID 30）の意訳

対象は FreeBSD Handbook の公式 Chapter 31「PPP」（既存 TOC ID 30、slug `ppp-and-slip`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/ppp-and-slip/_index.adoc`（942行、31380バイト）
- 保存先：`handbook/en/ch31/31-ppp-and-slip.adoc.txt`（SHA-256: `fafc8c3b0608f5741f8d552d25cb397bd6203b0d20addb3474caa5a34fd13941`）
- 訳文：`handbook/ja/31-ppp-and-slip.md`
- マニフェスト：`docs/translation-ch31.json`

## 構成と照合結果

- 見出し：20（`#` 1、`##` 5、`###` 12、`####` 2）
- アンカー：20（原文の明示ID 12、生成ID 8）
- コード例：61
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **冒頭訳注（翻訳範囲・プロンプト表記）**：AsciiDoc フロントマター・文書属性・共有 `include::` が翻訳対象外であること、コマンド例を実機実行していないこと、`#`（root）と `%`（一般ユーザー）のプロンプト表記を明記しました。
- **`sendmail` と PPP リンクに関する原文の文末欠落**：`userppp-final` 節の "The downside is that `sendmail` is forced to re-examine the mail queue whenever the ppp link." は原文で語句が欠落していますが、直後の `ppp.linkup` による自動化の説明に合わせて訳し、その旨を訳注で明記しました。
- **接続速度の単位表記（`115,200 kbps`）**：`set speed 115200` の説明では原文どおり `115,200 kbps` と訳したうえで、[FreeBSD 15.0 ppp(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/ppp/ppp.8) を参照し、実際には bps 単位（115,200 bps = 115.2 kbps）である旨を訳注で補足しました。
- **認証完了時のプロンプト例（`Ppp ON example>` の重複）**：手動接続節の認証完了時のプロンプト例は原文どおり `Ppp ON example>` を保持し、[FreeBSD 15.0 ppp(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/ppp/ppp.8) では認証完了時に 2 文字目の `p` も大文字になり `PPp ON ...>` となる旨を訳注で補足しました。
- **相互参照**：本リポジトリで自己校正済みの章（`30-serialcomms.md#dialup`）へ相対パス＋明示アンカーでリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch31_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/31-ppp-and-slip.md` による GFM 構文解析とブロック数確認（Header 20、CodeBlock 61、Table 0）
- `git diff --check origin/main...HEAD`（警告なし、rc=0）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
