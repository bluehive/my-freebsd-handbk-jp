# 公式Chapter 18 OCI Containers（既存TOC ID 17）の意訳

対象は FreeBSD Handbook の公式 Chapter 18「OCI Containers」（既存 TOC ID 17、slug `containers`）のみです。既存の訳文ファイル `handbook/ja/17-containers.md` のパスを維持したまま、固定原文と全文照合して書き直し・補完を行います。

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

## 構成（固定原文）

- 見出し：50（`#` 1、`##` 18、`###` 22、`####` 9）
- アンカー：50（原文の明示ID 46、生成ID 4）
- コード例：60
- 表・画像：各 0

## 進捗

- 状態：ドラフト（意訳・自己校正作業中）
- FreeBSD 実機での動作確認、第三者による専門校閲、および取得後の上流変更への追随は未実施です。
