# 公式Chapter 26・27の意訳・検証記録

対象は公式HandbookのChapter 26「Localization - i18n/L10n Usage and Setup」とChapter 27「Updating and Upgrading FreeBSD」です。既存TOCはネットワーク章追加前のID 25・26を維持しているため、新しい訳文を公式番号のファイル名へ対応付けています。他の章の一括改番は行いません。

## 固定原文

- 上流：freebsd/freebsd-doc。
- コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`。
- 取得日：2026-11-04（日本時間）。
- 原文は `handbook/en/ch26-ch27/`、SHA-256と状態は [マニフェスト](translation-ch26-ch27.json)。

## 意訳・照合の範囲

| 公式章 | 見出し | アンカー | コード・出力 | 表 | 状態 |
|---|---:|---:|---:|---:|---|
| 26 Localization | 13 | 17 | 27 | 4 | 全節を意訳・自己校正済み |
| 27 Updating and Upgrading | 45 | 50 | 78 | 2 | 全節を意訳・自己校正済み |

画像は両原文にありません。原文の手順・選択肢・表・警告を保ち、読みやすい日本語へ意訳しました。コードと出力は原文を保持し、AsciiDocの注釈番号だけを除いています。章末までの欠落や未翻訳記号がないことも確認しました。

第26章はロケール名、ログインクラス、シェル、コンソール、Xorg、入力方式、言語別設定を対象としています。LC_ALLの優先順位、古いsysconsの構成、Portsのカテゴリや提供状況などは訳注を区別しています。

第27章はバージョンと移行経路、freebsd-update、GENERICとABI更新、状態比較、文書更新、CURRENT/STABLE、n-number、ソースビルドとetcupdate、pkgbaseの変換・更新、ZFSの有無によるメジャー移行、ローカル配布、複数台の構築、非FreeBSDホストを全て対象としています。古いリリース番号を現在の移行先に勧める説明ではなく、実験的な経路と操作の前提も明示しています。

## 検証

```shell
python3 scripts/check_ch26_ch27_translations.py --require-complete
python3 scripts/check_ch23_ch24_translations.py --require-complete
python3 scripts/check_handbook_translations.py --require-complete
python3 scripts/check_jails_translation.py
```

- 新章の原文ハッシュ、58見出しの順序・階層、67アンカー、105コード例、内部リンクと相対リンク先の明示アンカーを照合。
- 両章をPandocのGFMとして解析し、58見出し・105コードブロック・6表を確認。原文で挙げる全Ports名の記載も確認。
- 負例6種（コード内容変更、アンカー削除、階層変更、内部リンク不備、未置換記号、原文ハッシュ変更）を検出。
- n-numberの原文にある「注釈記号だけの最終行」を除去すると末尾空行が残る問題に対し、共通検査器の正規化を修正。コード内容の変更を引き続き検出することも確認。
- 共通検査器の修正後、第1〜14章、第16章、第23〜24章の検査も成功。これらの既存訳文は変更していません。
- `git diff --check` 成功。新章の完了を必須にするGitHub Actionsを追加。

この検証は固定原文と訳文・文書構造の確認です。FreeBSD実機のロケール変更、OS更新、再起動、ビルド、pkgbase変換は未実施です。第三者の専門校閲、取得後の上流変更への追随も未実施です。構造検査だけで実機動作やすべての訳文の正確さを保証するものではありません。

PRを作成してCIの結果を確認し、ユーザーの承認後にマージします。

他のエージェント向けの共通手順・方針・注意点は、[意訳作業の引き継ぎ](translation-handoff.md)にまとめています。
