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
