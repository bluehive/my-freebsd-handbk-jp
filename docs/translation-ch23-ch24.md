# 公式Chapter 23・24の意訳

対象は公式HandbookのChapter 23「The Z File System (ZFS)」とChapter 24「Other File Systems」です。ユーザーの指定は公式章番号を意味します。Virtualizationは対象外です。

既存のhandbook/TOC.mdはネットワーク章の追加前の番号を使っているため、OpenZFSはID 22、Other File SystemsはID 23になっています。今回の新しいファイル名は公式章番号に合わせ、23-zfs.mdと24-filesystems.mdとします。既存の第1〜14章などを一括改番する作業は行いません。

## 出典

- 上流：freebsd/freebsd-doc
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`
- 取得日：2026-11-04（日本時間）
- 原文：`documentation/content/en/books/handbook/{zfs,filesystems}/_index.adoc`
- 保存先：`handbook/en/ch23-ch24/`。SHA-256は `translation-ch23-ch24.json` に記録。

## 進捗

| 公式章 | 内容 | 状態 |
|---|---|---|
| 23 | ZFS | 作業中。導入・クイックスタートの7見出しを意訳。以降のプール・データセット・暗号化・用語などは未完了。 |
| 24 | Other File Systems | 全10見出し・14コード例を意訳・自己校正済み。 |

原文の手順・選択肢・注意点を保ち、自然な日本語に意訳します。コードと出力は原文を保持し、古い例や説明の食い違い、対象デバイスを取り違える危険は訳注で区別します。ZFSのプール作成・破棄、ファイル削除などの例を実際に実行したという意味ではありません。

## 検証

`python3 scripts/check_ch23_ch24_translations.py` は原文ハッシュと翻訳済み章の節・階層・アンカー・コード・画像・リンクを検査します。`--require-complete` は両章の完了を要求するため、現在は第23章が未完了として失敗します。構造検査は訳文の意味やFreeBSD実機動作の保証ではありません。

全章の意訳・照合と最終検証が終わってからPRの承認を依頼します。マージは承認前に行いません。
