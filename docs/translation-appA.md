# 公式Appendix A Obtaining FreeBSD（既存TOC ID A）の意訳

対象は FreeBSD Handbook の公式 Appendix A「Obtaining FreeBSD」（既存 TOC ID A、slug `mirrors`）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第16章、第19〜27章、第30章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/mirrors/_index.adoc`（440行、20806バイト）
- 保存先：`handbook/en/appA/A-mirrors.adoc.txt`（SHA-256: `d4398bc07c55b1cb0a6b24606f9ff98cb18f1e1787c14582bd14701f6782b6a5`）
- 訳文：`handbook/ja/A-mirrors.md`
- マニフェスト：`docs/translation-appA.json`

## 構成と照合結果

- 見出し：11（`#` 1、`##` 2、`###` 8）
- アンカー：12（原文の明示ID 7、生成ID 5：`appendix-A-heading-01`・`07`・`08`・`10`・`11`）
- コード例：4（すべて原文のまま保持）
- 表：3（公式ミラーサービス 7行、コミュニティミラー一覧 50行・プロトコルリンク 185件・連絡先 26件、FreeBSD Git リポジトリ URL 一覧 6行）
- 画像：0
- SSH ホスト鍵フィンガープリント：6件（`gitrepo.FreeBSD.org` 3件、`git.FreeBSD.org` 3件、すべて原文のまま保持）

原文の AsciiDoc ヘッダ・共有 `include::`（`shared/authors.adoc`、`shared/mirrors.adoc`、`shared/releases.adoc`、`attributes`、`teams.adoc`、`mailing-lists.adoc`、`urls.adoc`、`asciidoctor.adoc`）は翻訳対象外とし、本文の全節を意訳してその旨を訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **共有属性の解決**：コミュニティミラー一覧の各国の連絡先メールアドレス（`{mirrors-*-email}`）は、同じ固定コミット `a39743a3b0535f4498735119317889ea2bdfeb28` の `shared/mirrors.adoc` の定義を参照して解決し、訳注で明記しました。`{committers-guide}` は同じ固定コミットの `shared/en/urls.adoc` に従い `https://docs.freebsd.org/en/articles/committers-guide/#git-mini-primer` へ解決しています。
- **本文のない見出し（`== Using Git`）**：原文の `== Using Git` の直下には本文がなく、小節（`=== Introduction` 以下）が続く構成のため、明示的な訳注（`原文ではこの見出しの下に本文がなく、内容は以下の小節にあります。`）を置きました。
- **コマンド例・原文表記の保持**：`pkg install git`、`git clone -o freebsd https://git.FreeBSD.org/src.git /usr/src`、`git checkout stable/13`、`git pull --rebase`、およびコミュニティミラー表のホスト名・プロトコル（`ftp2.za.FreeBSD.org` の `ftp_v6` のみ表記等）は固定原文どおり保持しました。
- **相互参照**：本リポジトリで自己校正済みの章（`27-cutting-edge.md#updating-upgrading-freebsdupdate`）は相対パス＋明示アンカーへリンクし、未翻訳の付録（Appendix C Resources の `eresources-mail`）は公式 FreeBSD Handbook（英語版）の該当ページへリンクしました。同一付録内（`#git`、`#external-mirrors`）は内部アンカーリンクとしています。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_appA_translation.py --require-complete`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/A-mirrors.md` による GFM 構文解析とブロック数確認（Header 11、CodeBlock 4、Table 3）
- `git diff --check origin/main...HEAD`（rc=0、警告なし）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
