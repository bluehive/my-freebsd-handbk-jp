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

- 見出し：45（`#` 1、`##` 11、`###` 25、`####` 7、`#####` 1）
- アンカー：49（見出し45 + 非見出し4：`routeflags`, `networking-lacp-aggregation-cisco`, `networking-lagg-failover`, `networking-lagg-wired-and-wireless`）
- コード例：130（すべて原文のまま保持。注記ブロック内のコードブロックは共通検査器の仕様に合わせてトップレベルへ配置）
- 画像：2（`static-routes.png`, `pxe-nfs.png` — 固定コミットの `documentation/static/images/books/handbook/advanced-networking/` を参照し HTTP 200 を確認）
- 表：1（`routeflags`）

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳・自己校正しました。

## 訳注で区別した原文の仕様・注意点

- **リリース属性 `{rel121-current}`**：同じ固定コミットの `shared/releases.adoc`（`handbook/en/through-ch14/releases.adoc.txt`）に従い `12.1`（FreeBSD 12.1）として解決し、より新しいリリースでも `kld_list` によるカーネルモジュール読み込みが有効である旨を訳注で補足しました。
- **相互参照**：本リポジトリで自己校正済みの章（`04-ports.md#ports`, `09-kernelconfig.md#kernelconfig`, `14-boot.md#boot`, `27-cutting-edge.md#makeworld`）は相対パス＋明示アンカーへリンクし、未翻訳章（`network`）は公式 FreeBSD Handbook（英語版）へリンクしました。また、章内の `crossref:advanced-networking[_debugging_pxe_problems,...]` は、原文見出しに明示アンカーがないため共通検査器の規則に従い `#chapter-35-heading-42` へリンクしています。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch35_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py --require-complete`
- `pandoc --from=gfm --to=json handbook/ja/35-advanced-networking.md` による GFM 構文解析とブロック数確認（Header 45 / CodeBlock 130 / Table 1 / Image 2）
- `git diff --check`

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。

## PR #12 レビュー指摘への対応（2026-11-19）

- 最新 `main` へ rebase し、`README.md`・`SOURCE.md`・`handbook/TOC.md` の競合を解消しました。
- PR #12 のレビュー指摘に基づき、`handbook/ja/35-advanced-networking.md` の 6 点（PEAP の証明書認証に関する訳注追加、CARP の FreeBSD バージョン範囲表現、IBSS のポイントツーポイント表記、CCMP と TKIP の関係表現、表 1 の C フラグ説明の重複語句削除、`` `driver_load="YES"` `` の余分な `*` 削除）を修正し、検査を再実行しました。
