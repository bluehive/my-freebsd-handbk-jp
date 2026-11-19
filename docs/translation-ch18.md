# 公式Chapter 18 OCI Containers（既存TOC ID 17）の意訳

対象は FreeBSD Handbook の公式 Chapter 18「OCI Containers」（既存 TOC ID 17、slug `containers`）のみです。既存の訳文ファイル `handbook/ja/17-containers.md` のパスを維持したまま、固定原文と全文照合して書き直し・補完・自己校正を行いました。

## 出典

- 上流：`freebsd/freebsd-doc`
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第19〜21章、第23〜27章、第33〜35章、Preface と同じ）
- 取得日：2026-11-20（日本時間）
- 原文：`documentation/content/en/books/handbook/containers/_index.adoc`（1110行、41706バイト）
- 保存先：`handbook/en/ch18/18-containers.adoc.txt`（SHA-256: `e666506444b45f33115e8a6de8fc65062ff38388eae3a9dc3cfe718bcb9baf5e`）
- 旧スナップショット：`handbook/en/17-containers.adoc.txt`（SHA-256: `f866940aca688f0738313cf1b121681954dfd7b47d8963cd641aae55ef9ba802`、履歴として未変更のまま保持）
- 訳文：`handbook/ja/17-containers.md`
- マニフェスト：`docs/translation-ch18.json`

## 旧スナップショットとの主な差分

旧スナップショット（`handbook/en/17-containers.adoc.txt`、1008行・38266バイト）と固定原文（`handbook/en/ch18/18-containers.adoc.txt`、1110行・41706バイト）の間には次の差分があります。

- フロントマターおよび AsciiDoc ヘッダ・共有 `include::` の有無（旧スナップショットでは省略）。
- `containers-preparing` 節に `/etc/fstab` への `fdescfs` 追記例を追加。
- `containers-networking`（Configuring Networking）節を独立して新設し、`pf.conf` の設定例（`v4egress_if` / `v6egress_if` / `rdr-anchor` / `nat-anchor` / `table <cni-nat>`）、`service pf enable` / `start`、`sysctl net.pf.filter_local=1` と `/etc/sysctl.conf` を詳述。
- `containers-config-files`（Additional Configuration Files）節を独立させ、`pkg list | grep /etc/containers/` に更新。
- `containers-first`（Running Your First Container）節を新設し、`podman run -it --rm ghcr.io/freebsd/freebsd-notoolchain:{rel-latest}` の実行例を追加。
- 従来の `[[containers-networking]]` アンカーを `[[containers-name-resolution]]` へ改名。

## 構成と照合結果

- 見出し：50（`#` 1、`##` 18、`###` 22、`####` 9）
- アンカー：50（原文の明示ID 46、生成ID 4）
- コード例：60
- 表・画像：各 0

原文の AsciiDoc ヘッダ・共有 `include::` は翻訳対象外とし、本文の全節を意訳してその旨を冒頭の訳注で明記しました。

## 訳注で区別した原文の仕様・注意点

- **リリース属性とプロンプト**：固定コミットの `shared/releases.adoc`（`handbook/en/through-ch14/releases.adoc.txt`）に従い、本文中の `{rel-latest}` は `15.1`、`{rel-latest-previous}` は `15.0` として解決しました。コード例中の属性は原文どおり保持し、置換方法とプロンプト表記（`#` / `$`）を冒頭の訳注で説明しています。
- **直下に本文がない見出し**：`containers-naming-tagging`、`containers-tag-structure`、`chapter-18-heading-14`、`containers-advanced`、`containers-troubleshooting` の 5 箇所は原文で直下に本文がないため、内容が以下の小節にある旨を明示的な訳注として置いています。
- **FreeBSD 14 出力例の保持**：`containers-volumes` の `pkg-static bootstrap` 例ではコマンド行が `{rel-latest}`（15.1）である一方、出力例は `FreeBSD:14:amd64/latest` となっています。出力例は原文どおり保持し、訳注で区別しています。
- **ホストから `localhost` へのリダイレクト記述の差異**：`containers-building-containerfile` の注記ではホストから `localhost` / `127.0.0.1` への接続はリダイレクトされないと述べている一方、新設された `containers-networking` 節では `nat-anchor "cni-rdr/*"` と `sysctl net.pf.filter_local=1` によりホストから `localhost` 宛ての接続をリダイレクトできると説明しています。双方を原文どおり訳出し、訳注で関連箇所を示しました。

## 検証

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_ch18_translation.py --require-complete`（rc=0）
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_handbook_translations.py`（rc=0）
- `pandoc --from=gfm --to=json handbook/ja/17-containers.md` による GFM 構文解析とブロック数確認（Header 50、CodeBlock 60、Table 0）
- `git diff --check origin/main...HEAD`（警告なし、rc=0）

FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
