# 原文・出典

## 上流

- プロジェクト: [FreeBSD Documentation Project](https://www.freebsd.org/docproj/)
- 英語 Handbook: https://docs.freebsd.org/en/books/handbook/
- ソースリポジトリ: https://github.com/freebsd/freebsd-doc  
  パス例: `documentation/content/en/books/handbook/`
- 著作権表示（原文）: Copyright © 1995–2026 The FreeBSD Documentation Project

## 本リポジトリの扱い

- 日本語訳および独自の見積・用語メモは **BSD-2-Clause**（ルート `LICENSE`）。
- 原文からの翻訳である旨を各 MD 先頭に記載する。
- 公式の最新内容は常に docs.freebsd.org を正とする。本訳は学習・参照用の進行中スナップショット。

## 取得日メモ

| 日付 | 内容 |
|------|------|
| 2026-08-17 | freebsd-doc から introduction 章を抽出し `handbook/en/01-introduction.adoc.txt` を作成 |

## 第16章の校正に用いた原文

- 原文: `handbook/en/16-jails.adoc.txt`。
- 本リポジトリでの原文追加コミット: `6eceb3782150540e668175efae8ca2ae250df1bb`。
- 2026-11-04の照合基点: `d6ce50909e0cfe63851b0d652960da72c34e750a`（PR #3マージ後）。これは上流コミットではありません。
- 原文ファイルのSHA-256: `92a503c41b482492207461cc610fdb0b575b6d384bcaab4ad2b8ea15c1309600`。
- 想定される上流パス: `freebsd/freebsd-doc` の `documentation/content/en/books/handbook/jails/_index.adoc`。
- **元の取得時の上流コミットと取得日時は記録がなく不明です。** ローカル追加コミットの日付を上流の取得日時として扱いません。最新の上流と完全一致することは未確認です。
- 機械可読の照合情報: [docs/jails-source.json](docs/jails-source.json)。原文を更新する際は先に差分を確認し、翻訳を照合してからハッシュを更新します。

原文の説明に食い違いがある箇所は本文の訳注として区別しています。追加で参照した一次資料は [FreeBSD 15.0 jail(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/jail/jail.8)、[rctl(8)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.bin/rctl/rctl.8)、[OpenZFS zfs-promote(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-promote.8.html) です。全章を最新上流へ同期した記録ではありません。
