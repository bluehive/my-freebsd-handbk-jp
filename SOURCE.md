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

## 第1〜14章の意訳用スナップショット

- 取得日: 2026-11-04（日本時間）。
- 上流: [freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc)。
- 固定コミット: `a39743a3b0535f4498735119317889ea2bdfeb28`。
- 章のパス: `documentation/content/en/books/handbook/<章名>/_index.adoc`。
- 原文保存先: `handbook/en/through-ch14/`。各章のSHA-256と訳文の照合状態は [マニフェスト](docs/translation-through-ch14.json)に記録。
- リリース属性は同じコミットの `shared/releases.adoc` を `releases.adoc.txt` として保存。コード内の属性は原文どおり残し、章頭で置換方法を説明する。
- 画像は同じ上流コミットの `documentation/static/images/books/handbook/<章名>/` を参照し、原文と画面の版を揃える。

このスナップショットの保存だけでは各章の翻訳完了を意味しません。マニフェストの `translated` は原文全節との意訳照合を終えた章、`pending` は未照合です。以前からある `handbook/en/01-introduction.adoc.txt` 等は過去の原文であり、この作業の固定版と混同しません。

第5章の追加訳注は、[X.orgのフォント文書](https://xorg.freedesktop.org/releases/current/doc/xorg-docs/fonts/fonts.html)のcore fontとXftの区別・索引作成・組み込みフォント機能、および[X.orgのxorg.confマニュアル](https://www.x.org/archive/X11R7.0/doc/html/xorg.conf.5.html)のBusID書式も参照しています。これらは原文の旧来手順を説明するための一次資料で、現在の各FreeBSDパッケージを実機で検証したという意味ではありません。

第6章のXDG関連の訳注は、[XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/)の設定用ディレクトリと実行時ディレクトリの区別、および実行時ディレクトリの所有者・権限・寿命を参照しています。

第1〜14章の番号は本リポジトリの既存TOCに準拠します。固定上流ではネットワーク章が新設され、デスクトップ以降は番号が1つ後ろへずれています。各章の内容対応と上流番号はマニフェストの `id`・`slug`・`upstream_chapter_number` で区別します。

第10章のlpqの訳注は、[FreeBSD 15.0 lpq(1)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/usr.sbin/lpr/lpq/lpq.1)の、引数がない場合はキュー内の全ジョブを報告する説明を参照しています。

第12章では、[xrdp公式サイト](https://www.xrdp.org/)でRDPサーバであることを確認し、[X.Org xhost(1)](https://xorg.freedesktop.org/archive/X11R7.5/doc/man/man1/xhost.1.html)のlocalファミリの定義を参照して、原文のクライアントの例とユーザー限定の説明を補足しています。

第14章のUEFIの訳注は、[FreeBSD 12.4 loader.efi(8)](https://man.freebsd.org/cgi/man.cgi?manpath=FreeBSD+12.4-RELEASE&query=loader.efi&sektion=8)を参照しています。固定原文に残る「UEFI起動を開発中」という古い説明と、実装済みのUEFI起動を区別するための参照です。

第3章の訳注は、FreeBSD 15.0の [chflags(1)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/bin/chflags/chflags.1)、[execve(2)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/lib/libsys/execve.2)、[sticky(7)](https://github.com/freebsd/freebsd-src/blob/releng/15.0/share/man/man7/sticky.7)を参照し、ディレクトリのフラグ、スクリプトとnosuidでのset-IDの扱い、stickyディレクトリで削除・改名できる条件を補足しています。

## 公式Chapter 23・24の意訳用スナップショット

2026-11-04に、公式Chapter 23 ZFSとChapter 24 Other File Systemsを、`freebsd/freebsd-doc` のコミット `a39743a3b0535f4498735119317889ea2bdfeb28` から取得しました。原文は `handbook/en/ch23-ch24/`、出典・SHA-256・進捗は [マニフェスト](docs/translation-ch23-ch24.json)と[作業記録](docs/translation-ch23-ch24.md)に保存します。公式章番号と既存TOCのIDには1の差があります。今回の対象にVirtualizationは含みません。
