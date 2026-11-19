# 公式Chapter 29 USB Device Mode / USB OTG（既存TOC ID 28）の意訳

対象は FreeBSD Handbook の公式 Chapter 29「USB Device Mode / USB OTG」（既存 TOC ID 28、slug `usb-device-mode`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/usb-device-mode/_index.adoc`（316行、11215バイト）
- 保存先：`handbook/en/ch29/29-usb-device-mode.adoc.txt`（SHA-256: `36ea6729de7bd258730c3290fd72d85a68ce40dc26b9bb2737c6a306d591d568`）
- 訳文：`handbook/ja/29-usb-device-mode.md`
- マニフェスト：`docs/translation-ch29.json`

## 構成と照合結果

- 見出し：12（`#` 1、`##` 4、`###` 7）
- アンカー：12（原文の明示ID 5、生成ID 7）
- コード例：19
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **冒頭訳注**：原文の AsciiDoc フロントマター・文書属性・共有 `include::` を翻訳対象外としていること、掲載コマンドは説明用で実機未実行であること、`#` が root プロンプトであることを明記しました。
- **`usb-device-mode-terminals` 見出し直下の空本文**：原文では `== USB Virtual Serial Ports` の直下に本文がなくそのまま小節へ続くため、構造検査器が要求する日本語本文として、原文にない説明を足さず明示的な訳注を置きました。
- **`naa.50015178f369f092` の桁数**：`/etc/ctl.conf` 例の説明で原文は「32 random hexadecimal digits」（32 桁の 16 進数）としていますが、例示されている `naa.50015178f369f092` の数値部（`50015178f369f092`）は実際には 16 桁（64 ビット）です。原文どおり訳したうえで、[FreeBSD 15.0 ctl.conf(5)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/ctld/ctl.conf.5) でも同じ 16 桁の例（`target naa.50015178f369f092`）が使われている旨を訳注で補足しました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch29_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/29-usb-device-mode.md` による GFM 構文解析とブロック数確認（Header 12、CodeBlock 19、Table 0）
- `git diff --check origin/main...HEAD`（rc=0、警告なし）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
