# 25 Virtualization（仮想化）の意訳

対象は FreeBSD Handbook の公式 Chapter 25「Virtualization」（既存 TOC ID 24）のみです。他の章・付録は対象外です。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜20章、第23〜24章、第26〜27章、Preface と同じ）
- 取得日：2026-11-19（日本時間）
- 原文：`documentation/content/en/books/handbook/virtualization/_index.adoc`（2566行、100586バイト）
- 保存先：`handbook/en/ch25/25-virtualization.adoc.txt`（SHA-256: `b22724e7efe5f3c3c8d48edc51dc551e1e5f0207048c454b362dff956e600979`）
- 訳文：`handbook/ja/25-virtualization.md`
- マニフェスト：`docs/translation-ch25.json`

## 構成と照合結果

- 見出し：58（`#` 1、`##` 8、`###` 35、`####` 14）
- アンカー：76（見出し58 + 図表等18、すべて原文の明示IDを保持）
- コード例：126（すべて原文のまま保持）
- 画像：38（`documentation/static/images/books/handbook/virtualization/` の固定コミット版を参照）
- 表：1（bhyve マネージャ一覧、全6行）

## 訳注で区別した原文の仕様・注意点

- **VMware Fusion の `ums_load` 例**：原文コードブロック内の `# ums_load=“YES”`（コメントアウトと全角引用符）をそのまま保持し、実際に有効化する際の注意を訳注で補足しました。
- **QEMU シリアルコンソールの `/boot.loader.conf` 表記**：原文の注記にある `/boot.loader.conf` は `/boot/loader.conf` として訳出し、原文表記を併記しました。
- **bhyve スナップショットの `WITH_BHYVE_SNAPHOT=yes`**：原文コードブロック内の綴り（`SNAPHOT`）を保持し、訳注で明記しました。
- **jail 化 bhyve の `nmdm` デバイス名**：`devfs.rules` 例の `nmdmbhyve*` と起動例の `/dev/nmdbbhyve0A`・`/dev/nmdbbhyve0B` の表記差を訳注で補足しました。
- **Xen DomU の `freebsd.cfg` プール名**：直前の手順で作成した `zroot/xendisk0` に対し、`freebsd.cfg` 例が `/dev/zvol/tank/xendisk0` となっている点を訳注で補足しました。
- **相互参照**：本リポジトリで自己校正済みの章（`02`, `03`, `04`, `05`, `07`, `16`, `23`, `27`）は相対パス＋明示アンカーへリンクし、未翻訳章およびアンカー未整備のドラフト章（`security`, `firewalls`, `advanced-networking`）は公式 FreeBSD Handbook（英語版）の該当ページへリンクしました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch25_translation.py --require-complete`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`
- `pandoc --from=gfm --to=json handbook/ja/25-virtualization.md` による GFM 構文解析とブロック数確認（Header 58、Image 38、CodeBlock 126、Table 1）
- `git diff --check`：コード例の5か所（1396・1414・1429・1449・1514 行目）で `space before tab in indent` の警告が出ます。上流原文の空白をそのまま保持しているためで、コード例は変更していません。

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。

## PR #13 レビュー指摘による修正

- 最新 `main` へ rebase を行いました。
- `### 利用のヒント` 直下に足し込んでいた一文を削除し、検査器の「各節に日本語説明」要件を満たすため、本文のない見出しである旨の訳注に置き換えました。
- bhyve UEFI 節のインラインコード内に残っていた AsciiDoc 由来の `_` を削除しました。
- `git diff --check` に関する記録を実測値（5か所の `space before tab in indent` 警告）に合わせて訂正しました。
