# FreeBSD Handbook 日本語翻訳（Markdown）

[![License](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](./LICENSE)

FreeBSD 公式 **Handbook** の日本語翻訳を、**Markdown** で進める公開リポジトリです。  
GitHub: https://github.com/bluehive/freebsd-handbook-ja

- 原文: [FreeBSD Handbook (English)](https://docs.freebsd.org/en/books/handbook/)
- ライセンス: **BSD-2-Clause**（`LICENSE`）。原文は FreeBSD Documentation Project の著作物です（`SOURCE.md`）。
- メンテナ起票: bluehive（Hiroki Kato）
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

### 2026-08-17 — セッション1（制限時間 20 分）

| 時刻目安 | 内容 |
|----------|------|
| 開始 | 20 分タイマー起動。要件: 公開リポ・BSD・MD 翻訳・README 進捗・20 分で中断報告 |
| +1–3 分 | `bluehive/freebsd-handbook-ja` を **public** 作成（GitHub）。ローカル `~/my-project/freebsd-handbook-ja` |
| +3–8 分 | `freebsd/freebsd-doc` を sparse clone。Handbook 章構成確認。introduction / basics / zfs 等の語数ざっくり計測 |
| +8–18 分 | リポジトリ骨組み: LICENSE (BSD-2-Clause), SOURCE, TOC, 工数見積 MD, 用語集種, en スナップショット |
| +8–18 分 | **第1章 Introduction の日本語初訳** → `handbook/ja/01-introduction.md`（Synopsis〜追加ドキュメントまで一通り） |
| 20 分 | **作業中断・本 README に記録・push・状況報告**（予定） |

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
5. TOC の状態列を更新し、**本 README の進捗ログに1エントリ追加**  

## リンク

- 英語 Handbook: https://docs.freebsd.org/en/books/handbook/  
- 本リポジトリ: https://github.com/bluehive/freebsd-handbook-ja  
