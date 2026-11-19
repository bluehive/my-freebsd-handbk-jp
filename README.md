# FreeBSD Handbook 日本語翻訳（Markdown）

[![License](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](./LICENSE)

FreeBSD 公式 **Handbook** の日本語翻訳を、**Markdown** で進める公開リポジトリです。  
GitHub: https://github.com/bluehive/my-freebsd-handbk-jp

- 原文: [FreeBSD Handbook (English)](https://docs.freebsd.org/en/books/handbook/)
- ライセンス: **BSD-2-Clause**（`LICENSE`）。原文は FreeBSD Documentation Project の著作物です（`SOURCE.md`）。
- メンテナ起票: bluehive
- 作業エージェント: Hermes（進捗は本 README に追記）

## 目的

1. Handbook を章単位の MD で読みやすく翻訳する  
2. 用語集を育て、訳の揺れを減らす  
3. 工数見積（`docs/translation-estimate.md`）に沿って優先度を決める  

**公式の代替ではありません。** 最新・正確な情報は docs.freebsd.org を確認してください。

意訳作業を引き継ぐエージェントは、[手順・方針・注意点](docs/translation-handoff.md)を参照してください。

## ディレクトリ

```
LICENSE
README.md                 ← 進捗ログ（このファイル）
SOURCE.md                 ← 原文出典
docs/
  translation-estimate.md ← 章別工数概算
handbook/
  TOC.md                  ← 目次と翻訳ステータス
  en/                     ← 翻訳用に抜粋した英語テキスト
  ja/                     ← 日本語 Markdown
```

## 進捗ログ（新しいものが上）

### 2026-11-20 — 公式Chapter 18 OCI Containers（既存TOC ID 17）を意訳

- 公式Chapter 18 [OCI Containers](handbook/ja/17-containers.md)（既存TOC ID 17）の既存ドラフトを固定原文と全文照合して書き直し・補完し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全50見出し・50アンカー・60コード例を意訳・自己校正しました（旧スナップショット `handbook/en/17-containers.adoc.txt` は履歴として未変更のまま保持）。
- リリース属性（`{rel-latest}`=15.1、`{rel-latest-previous}`=15.0）、`pkg-static bootstrap` の FreeBSD 14 出力例、`localhost` リダイレクトに関する章内記述の差異は原文を保持したまま訳注で区別しています。
- [作業・検証記録](docs/translation-ch18.md) / [原文ハッシュと状態](docs/translation-ch18.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 32 Electronic Mail（既存TOC ID 31）を意訳

- 公式Chapter 32 [Electronic Mail](handbook/ja/32-mail.md)（既存TOC ID 31）を追加し、`handbook/TOC.md` と `SOURCE.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全22見出し・22アンカー・49コード例・8画像・全相互参照を意訳・自己校正しました。
- 原文のコマンド・設定例・表記（`/etc/sendmail.cf` 等）はそのまま保持し、FreeBSD の標準パスとの差異は訳注で区別しています。
- [作業記録](docs/translation-ch32.md) / [原文ハッシュと状態](docs/translation-ch32.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Appendix C Resources on the Internet（既存TOC ID C）を意訳

- 公式Appendix C [Resources on the Internet](handbook/ja/C-eresources.md)（既存TOC ID C）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全10見出し・11アンカー（明示ID 8、生成ID 3）・全外部リンクおよびメーリングリスト属性を意訳・自己校正しました。
- メーリングリスト属性（`{freebsd-doc}` 等）や `extref:` は同じ固定コミットの `shared/en/mailing-lists.adoc`・`shared/en/urls.adoc` に照合して解決しています。
- [作業・検証記録](docs/translation-appC.md) / [原文ハッシュと状態](docs/translation-appC.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 31 PPP（既存TOC ID 30）を意訳

- 公式Chapter 31 [PPP](handbook/ja/31-ppp-and-slip.md)（既存TOC ID 30）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全20見出し・20アンカー・61コード例・全相互参照を意訳・自己校正しました。
- 原文のコマンド・出力例および表記（`115,200 kbps`、認証完了時の `Ppp ON example>` 重複、`sendmail` 記述の文末欠落）は保持したうえで訳注で区別しています。
- [作業記録](docs/translation-ch31.md) / [原文ハッシュと状態](docs/translation-ch31.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 7 Network（既存TOC ID なし）を意訳

- 公式Chapter 7 [Network](handbook/ja/07-network.md)（既存TOC ID なし）を追加し、`handbook/TOC.md` に新規行を追加しました（既存の `07-desktop.md` 等は旧TOC番号のまま維持）。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全29見出し・30アンカー・57コード例・2表・全相互参照を意訳・自己校正しました。
- 原文のコマンド・設定・出力例（`pciconf` 出力の `iwm0` と本文の `iwn(4)` の差異を含む）は保持し、注意点を訳注で区別しています。
- [作業記録](docs/translation-ch07.md) / [原文ハッシュと状態](docs/translation-ch07.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Appendix D OpenPGP Keys（既存TOC ID D）を意訳

- 公式Appendix D [OpenPGP Keys](handbook/ja/D-pgpkeys.md)（既存TOC ID D）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全6見出し・6アンカー・全リンクおよび属性解決を意訳・自己校正しました。
- 共有インクルードの公開鍵ファイル本体（`documentation/static/pgpkeys/*.key`）は翻訳対象外として転記・改変せず、固定コミットの原文ファイルおよび公式の `pgpkeys.txt` への参照を訳注で明記しています。
- [作業・検証記録](docs/translation-appD.md) / [原文ハッシュと状態](docs/translation-appD.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Appendix B Bibliography（既存TOC ID B）を意訳

- 公式Appendix B [Bibliography](handbook/ja/B-bibliography.md)（既存TOC ID B）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全5見出し・5アンカー・全25文献を意訳・自己校正しました。
- 原文の書名・URL・ISBN/ISSN はそのまま保持しています。
- [作業記録](docs/translation-appB.md) / [原文ハッシュと状態](docs/translation-appB.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 29 USB Device Mode / USB OTG（既存TOC ID 28）を意訳

- 公式Chapter 29 [USB Device Mode / USB OTG](handbook/ja/29-usb-device-mode.md)（既存TOC ID 28）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全12見出し・12アンカー・19コード例を意訳・自己校正しました。
- 原文のコマンド・設定例は保持し、`ctl.conf` 例の `naa.50015178f369f092`（16桁）と原文説明（32桁）の差異などを訳注で区別しています。
- [作業記録](docs/translation-ch29.md) / [原文ハッシュと状態](docs/translation-ch29.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 28 DTrace（既存TOC ID 27）を意訳

- 公式Chapter 28 [DTrace](handbook/ja/28-dtrace.md)（既存TOC ID 27）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全6見出し・6アンカー・9コード例・全相互参照を意訳・自己校正しました。
- [作業記録](docs/translation-ch28.md) / [原文ハッシュと状態](docs/translation-ch28.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Appendix A Obtaining FreeBSD（既存TOC ID A）を意訳

- 公式Appendix A [Obtaining FreeBSD](handbook/ja/A-mirrors.md)（既存TOC ID A、slug `mirrors`）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全11見出し・12アンカー・4コード例・3表（コミュニティミラー50行・プロトコルリンク185件・連絡先26件・SSHホスト鍵フィンガープリント6件を含む）・全相互参照を意訳・自己校正しました。
- コミュニティミラー一覧の `{mirrors-*-email}` 属性は同じ固定コミットの `shared/mirrors.adoc` から解決し、訳注で明記しています。
- [作業記録](docs/translation-appA.md) / [原文ハッシュと状態](docs/translation-appA.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 30 Serial Communications（既存TOC ID 29）を意訳

- 公式Chapter 30 [Serial Communications](handbook/ja/30-serialcomms.md)（既存TOC ID 29）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全28見出し・33アンカー・37コード例・5表・全相互参照を意訳・自己校正しました。
- 原文のコマンド・設定例（`cu115200` エントリの `br#57600` を含む）は保持し、注意点を訳注で区別しています。
- [作業記録](docs/translation-ch30.md) / [原文ハッシュと状態](docs/translation-ch30.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 22 GEOM（既存TOC ID 21）を意訳

- 公式Chapter 22 [GEOM](handbook/ja/22-geom.md)（既存TOC ID 21）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全25見出し・25アンカー・85コード例・1画像・全相互参照を意訳・自己校正しました。
- 原文のコマンド例（`/dev/ad2`・`/dev/ad3` 等の旧 ATA デバイス名を含む）は保持し、近年の `adaX` との違いを訳注で区別しています。
- [作業記録](docs/translation-ch22.md) / [原文ハッシュと状態](docs/translation-ch22.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-20 — 公式Chapter 16 Security（既存TOC ID 15）を意訳・改稿

- 既存ドラフト [Security](handbook/ja/15-security.md)（公式 Chapter 16 / 既存 TOC ID 15）を固定原文へ全面照合・改稿し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全53見出し・53アンカー・119コード例・1表・全相互参照を意訳・自己校正しました。
- 旧スナップショット `handbook/en/15-security.adoc.txt` は履歴として残し、固定原文 `handbook/en/ch16/16-security.adoc.txt` との差分（ヘッダおよび欠落していた4行のコード例）を復元・記録しました。
- [作業・検証記録](docs/translation-ch16.md) / [原文ハッシュと状態](docs/translation-ch16.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-19 — 公式Chapter 21 Storage（既存TOC ID 20）を意訳

- 公式Chapter 21 [Storage](handbook/ja/21-disks.md)（既存TOC ID 20）を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全50見出し・51アンカー・153コード例・全相互参照を意訳・自己校正しました。
- 原文のコマンド例（`ssh -c blowfish`、`carp-hast-switch` スクリプト等）は保持し、仕様上の注意点を訳注で区別しています。
- [作業記録](docs/translation-ch21.md) / [原文ハッシュと状態](docs/translation-ch21.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-19 — 公式Chapter 25 Virtualization（仮想化）を意訳

- [仮想化（Virtualization）](handbook/ja/25-virtualization.md)を追加し、`handbook/TOC.md` の既存 TOC ID 24 へ対応付けました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全58見出し・76アンカー・126コード例・38画像・1表を意訳・自己校正しました。
- 原文のコード例や表記（`ums_load` の全角引用符、`/boot.loader.conf`、`WITH_BHYVE_SNAPHOT=yes`、`nmdbbhyve0A/B`、Xen `freebsd.cfg` の `tank` vs `zroot`）は保持したまま訳注で区別しています。
- [作業・検証記録](docs/translation-ch25.md) / [原文ハッシュと状態](docs/translation-ch25.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-19 — 公式Chapter 35 Advanced Networking（既存TOC ID 34）を意訳

- 公式の章番号に従い、[Advanced Networking](handbook/ja/35-advanced-networking.md) を追加し、`handbook/TOC.md` の既存 TOC ID 34 へ対応付けました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` から原文（`advanced-networking/_index.adoc`、103789バイト）を固定し、全45見出し・49アンカー・130コード例・2画像・1表を意訳・自己校正しました。
- リリース属性 `{rel121-current}` は `shared/releases.adoc` に従い FreeBSD 12.1 として解決し、訳注で補足しています。
- [作業・検証記録](docs/translation-ch35.md) / [原文ハッシュと状態](docs/translation-ch35.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-19 — 公式Chapter 34 Firewalls を意訳

- [Firewalls](handbook/ja/34-firewalls.md)（公式 Chapter 34 / 既存 TOC ID 33）を追加し、`handbook/TOC.md` と `SOURCE.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全43見出し・43アンカー・152コード例・1表・全相互参照を意訳・自己校正しました。
- 原文のコマンド・設定例・ルールセットはそのまま保持し、`ipfw.rules` のシェル構文に関する補足を訳注で明記しています。
- [作業・検証記録](docs/translation-ch34.md) / [原文ハッシュと状態](docs/translation-ch34.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-19 — 公式Chapter 33 Network Servers を意訳

- 公式の章番号に従い、[Network Servers](handbook/ja/33-network-servers.md)を追加し、`handbook/TOC.md`（既存ID 32）を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全69見出し・70アンカー・143コード例・7表を意訳・自己校正しました。
- 原文のコードと出力は保持し、古い記述や上流の表記ゆれ（`passwd_format=des`、`mod_php74`、`mod_python`、`samba_enable`、`/host/foobar/usr`、`config-network-setup` の移設先リンク等）は訳注で区別しています。
- [作業・検証記録](docs/translation-ch33.md) / [原文ハッシュと状態](docs/translation-ch33.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-19 — 00 Preface（序文）を意訳

- [序文（Preface）](handbook/ja/00-preface.md)を追加し、`handbook/TOC.md` を更新しました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全12見出し・12アンカー・3コード例・全相互参照を意訳・自己校正しました。
- 「Organization of This Book」の章一覧から `network`・`containers`・`serialcomms` が欠落している原文の仕様は補完せず、`book.adoc` への参照を訳注で明記しました。共有 `include::` や古いコマンド例・プロンプト表記も訳注で区別しています。
- [作業・検証記録](docs/translation-preface.md) / [原文ハッシュと状態](docs/translation-preface.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-04 — 公式Chapter 26 Localization・27 Updating and Upgradingを意訳（Codex）

- [ローカライズ](handbook/ja/26-l10n.md)と[FreeBSDの更新](handbook/ja/27-cutting-edge.md)を追加。公式章番号に合わせ、既存TOCのID 25・26へ対応付けました。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全58見出し・67アンカー・105コード例・6表を意訳・照合。
- 古い文字コード・コンソール設定、過去のリリース番号、実験的なpkgbase手順は、原文の前提と訳注を区別しました。
- 原文注釈を取り除いた末尾空行の正規化を共通検査器で修正。新章と、既存第1〜14・16・23・24章の検査が成功。
- [出典・検証記録](docs/translation-ch26-ch27.md) / [原文ハッシュと章別状態](docs/translation-ch26-ch27.json)。実機のロケール変更・更新・ビルドと第三者専門校閲は未実施。

### 2026-11-04 — 公式Chapter 19 MAC・20 Security Event Auditingを意訳

- 公式の章番号に従い、[MAC](handbook/ja/19-mac.md)と[Security Event Auditing](handbook/ja/20-audit.md)を追加。既存TOCのID 18・19へ対応付け、他章の一括改番は行っていません。他の章を作業中の別ブランチと競合しないよう、専用ブランチ `docs/translate-ch19-ch20-mac-audit` で作業。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、38見出し・40アンカー・49コード例・2表を照合。全節を意訳・自己校正しました。
- 原文のコードと出力は保持し、設定例の不備や古い記述（`login.conf` の継続記号漏れ、`mac_portacl` のカーネル設定行、`www/apache22` など）は訳注で区別。
- [作業・検証記録](docs/translation-ch19-ch20.md) / [原文ハッシュと章別状態](docs/translation-ch19-ch20.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-04 — 公式Chapter 23 ZFS・24 Other File Systemsを意訳（Codex）

- 公式の章番号に従い、[ZFS](handbook/ja/23-zfs.md)と[Other File Systems](handbook/ja/24-filesystems.md)を追加。既存TOCのID 22・23へ対応付け、他章の一括改番は行っていません。
- 上流コミット `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、91見出し・147アンカー・206コード例を照合。ZFSの用語50項目を含め、全節を意訳・自己校正しました。
- 原文の手順と条件を保ち、古い例、説明の食い違い、プール破棄や巻き戻しなどの影響は訳注で区別。
- [作業・検証記録](docs/translation-ch23-ch24.md) / [原文ハッシュと章別状態](docs/translation-ch23-ch24.json)。FreeBSD実機検証と第三者専門校閲は未実施。

### 2026-11-04 — 第1〜14章の意訳（14/14章を原文照合済み）

- 第1〜14章すべての意訳・自己校正を実施。第1章を再照合し、第3章の訳抜け・途中切れも復元。
- 公式原文を `a39743a3b0535f4498735119317889ea2bdfeb28` に固定し、全14章とリリース属性を保存。
- 原文の390見出し・574コード例・95画像を照合。手順・条件・警告・表を意訳し、原文の古い例や食い違いは訳注で区別。
- `scripts/check_handbook_translations.py --require-complete` が成功。CIでも全14章の完成状態と原文ハッシュ・節・アンカー・コード・画像・リンクを検査。
- 全章をPandocのGFMとして解析し、45表を確認。固定コミットでの画像パスと、相対リンクのフラグメントも確認。
- 章番号は既存TOCを維持。上流の新設ネットワーク章による番号差は、マニフェストで内容対応とともに記録。
- [PR #5](https://github.com/bluehive/my-freebsd-handbk-jp/pull/5) / [進捗・検証範囲](docs/translation-through-ch14.md) / [出典と章別状態](docs/translation-through-ch14.json)。実機検証・第三者専門校閲は未実施。

### 2026-11-04 — 第16章全体の原文照合・自己校正（Codex）

- 保存済み英語スナップショットに対応する66見出しを照合し、139個のコード・出力例を復元・確認。
- Thin Jail、テンプレート複製、VNET、Linux Jail、NAT、Service Jail、管理・移行、アップグレード、権限、ZFS委任の欠落・途中切れを修復。既に校正したホスト設定は保持。
- OpenZFSクローンとNullFSの更新の違い、`zfs promote`、ソース更新時の設定保持など、原文の食い違いを訳注で明示。
- `scripts/check_jails_translation.py` とGitHub Actionsで、原文ハッシュ・見出し・コード例・フェンス・アンカー・内部リンクを継続検査。
- `SOURCE.md` / `docs/jails-source.json` に照合基点と原文ハッシュを記録。上流コミット・取得日時は未記録のため不明と明記。
- 状態は「自己校正済」。最新上流との全差分同期・第三者校閲・FreeBSD実機検証を終えたという意味ではない。
- 検証範囲・再現方法: [第16章の校正記録](docs/jails-proofreading.md)。他章とIssue #1のDokuWiki/Caddy実験は別作業。

### 2026-11-04 — 第16章のディレクトリ構成・Jail設定ファイルを部分校正（Codex）

- 保存済み英語原文と照合し、途中で切れていた `jail.conf` の設定例とパラメータ解説を復元。
- 共通設定・変数、起動停止フックと依存関係、devfs ルールセットの欠落訳を復元。
- `host-configuration-directories` から `classic-jail` の直前まで、Markdown の見出し・コードフェンス・明示アンカー・リンクを整備。
- 対象範囲のコードブロック10個が原文と一致（原文のコールアウト記号を除く）。範囲外の本文が不変であること、フェンスの対応と内部リンクの参照先を確認。
- 第16章全体は引き続きドラフト。Thin Jail 節などの残りの校正、最新上流との差分確認、FreeBSD 実機検証は未実施。

### 2026-11-01 — 第16章のホスト設定を部分校正（Codex）

- `handbook/en/16-jails.adoc.txt` と照合し、ホスト準備・jail の起動制御・ネットワーク方式・IP アドレス管理の欠落訳を復元。
- 壊れていた `ysrc` を `sysrc` に復元し、ループバック・ホストサービス節まで Markdown の見出し、コードフェンス、アンカー、リンクを整備。
- 対象は `host-configuration` から `host-configuration-directories` の直前まで。第16章全体は引き続きドラフト。
- 関連: [Issue #1](https://github.com/bluehive/my-freebsd-handbk-jp/issues/1)、[PR #2（進捗・検証・引き継ぎメモ）](https://github.com/bluehive/my-freebsd-handbk-jp/pull/2)。FreeBSD 実機での動作確認は未実施。


### 2026-08-22 — おまけ: Service Jails と rc / sysrc まとめ

| ファイル | 内容 |
|----------|------|
| [`handbook/ja/extra-service-jails-rc.md`](handbook/ja/extra-service-jails-rc.md) | Service Jails 概要、rc.d 記事の見取り図、`rc.conf`、`sysrc` 使い方 |
| TOC | おまけ表に **X2** を追加 |

ユーザー提供の解説メモを MD 化（文字化け箇所は文脈で整備）。Handbook 本編外。

### 2026-08-21 — おまけ: appjail-ephemeral(7) 日本語訳

| ファイル | 内容 |
|----------|------|
| [`handbook/ja/extra-appjail-ephemeral.md`](handbook/ja/extra-appjail-ephemeral.md) | man `appjail-ephemeral(7)` の日本語 MD（cattle / pets / 短命 jail） |
| `handbook/en/extra-appjail-ephemeral.man.txt` | 出典メモ |
| 上流 | https://man.freebsd.org/cgi/man.cgi?query=appjail-ephemeral&manpath=FreeBSD+14.2-RELEASE+and+Ports |

Handbook 本編外。jail データ分離・量産（[Issue #1](https://github.com/bluehive/my-freebsd-handbk-jp/issues/1)）の参考。`handbook/TOC.md` おまけ表に追記。

### 2026-08-21 — 優先4章の初訳（機械支援）

対象: **03 Basics / 15 Security / 16 Jails / 17 Containers**

| ファイル | 状態 |
|----------|------|
| `handbook/ja/03-basics.md` | ドラフト |
| `handbook/ja/15-security.md` | ドラフト |
| `handbook/ja/16-jails.md` | ドラフト |
| `handbook/ja/17-containers.md` | ドラフト |
| `handbook/en/03,15,16,17-*.adoc.txt` | 原文抜粋 |

DeepSeek (`deepseek-v4-flash`) 分割翻訳。**要校正**。関連: [Issue #1](https://github.com/bluehive/my-freebsd-handbk-jp/issues/1)

### 2026-08-21 — リポジトリ名変更

- `bluehive/freebsd-handbook-ja` → **`bluehive/my-freebsd-handbk-jp`**
- ローカル: `~/my-project/my-freebsd-handbk-jp`
- URL: https://github.com/bluehive/my-freebsd-handbk-jp


### 2026-08-17 — セッション1（制限時間 20 分）

| 時刻目安 | 内容 |
|----------|------|
| 開始 | 20 分タイマー起動。要件: 公開リポ・BSD・MD 翻訳・README 進捗・20 分で中断報告 |
| +1–3 分 | `bluehive/my-freebsd-handbk-jp` を **public** 作成（GitHub）。ローカル `~/my-project/my-freebsd-handbk-jp` |
| +3–8 分 | `freebsd/freebsd-doc` を sparse clone。Handbook 章構成確認。introduction / basics / zfs 等の語数ざっくり計測 |
| +8–18 分 | リポジトリ骨組み: LICENSE (BSD-2-Clause), SOURCE, TOC, 工数見積 MD, 用語集種, en スナップショット |
| +8–18 分 | **第1章 Introduction の日本語初訳** → `handbook/ja/01-introduction.md`（Synopsis〜追加ドキュメントまで一通り） |
| ~5 分時点 | push 完了・**中断報告**（制限20分より早期に区切り。追加翻訳は次回） |

**成果物**

- [x] Public リポジトリ + BSD-2-Clause  
- [x] 見積もり文書のリポジトリ化  
- [x] 第1章 JA ドラフト（自己校正の第2パスは未）  
- [x] TOC / 用語集種 / 原文スナップショット  
- [ ] 第2章以降  
- [ ] 公式 ja 版との差分方針の確定  

**次にやるとよいこと（優先案）**

1. 第1章の通読校正（コマンド・固有名の揺れ）  
2. `preface` または工数の軽い章のドラフト  
3. 公式日本語版との関係（差分翻訳 vs 独立訳）を README に方針化  
4. 重い章（Install / ZFS / Security）は語数計測して見積を再スケール  

**注意（20 分枠のため未実施）**

- AsciiDoc からの機械一括変換パイプライン  
- CI  
- 画像・ビルド  
- Upstream 追従スクリプト  

---

## 翻訳の進め方（短い）

1. `handbook/TOC.md` で章を選ぶ  
2. 必要なら `freebsd-doc` から該当 `_index.adoc` を `handbook/en/` に抜粋  
3. `handbook/ja/NN-name.md` に翻訳  
4. 用語は `handbook/ja/glossary.md` を更新  
5. 第16章を変更した場合は `python3 scripts/check_jails_translation.py` を実行（[検証範囲](docs/jails-proofreading.md)）
6. TOC の状態列を更新し、**本 README の進捗ログに1エントリ追加**

## リンク

- 英語 Handbook: https://docs.freebsd.org/en/books/handbook/  
- 本リポジトリ: https://github.com/bluehive/my-freebsd-handbk-jp  
