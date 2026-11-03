# 公式Chapter 19・20の意訳

対象は公式HandbookのChapter 19「Mandatory Access Control」とChapter 20「Security Event Auditing」です。ユーザーの指定は公式章番号を意味します。Chapter 21以降は対象外です。

既存のhandbook/TOC.mdはネットワーク章の追加前の番号を使っているため、MACはID 18、Security Event AuditingはID 19になっています。今回の新しいファイル名は公式章番号に合わせ、19-mac.mdと20-audit.mdとします。既存章を一括改番する作業は行いません。別の作業ブランチで進む他章の意訳と競合しないよう、この作業は専用ブランチに分け、他章のファイル・検査器・ワークフローには触れていません。

## 出典

- 上流：freebsd/freebsd-doc
- 固定コミット：`a39743a3b0535f4498735119317889ea2bdfeb28`（第1〜14章、第23・24章と同じ）
- 取得日：2026-11-04（日本時間）
- 原文：`documentation/content/en/books/handbook/{mac,audit}/_index.adoc`
- 保存先：`handbook/en/ch19-ch20/`。SHA-256は `translation-ch19-ch20.json` に記録。

## 進捗

| 公式章 | 内容 | 状態 |
|---|---|---|
| 19 | Mandatory Access Control | 全27見出し・27アンカー・35コード例を意訳・自己校正済み。 |
| 20 | Security Event Auditing | 全11見出し・13アンカー・14コード例・2表を意訳・自己校正済み。 |

原文の手順・選択肢・注意点を保ち、自然な日本語に意訳します。コードと出力は原文を保持します。原文の設定例の不備や古い記述は、訳注で原文と区別して示します。MACの例を実際にFreeBSDへ適用したという意味ではありません。

## 訳注で区別した原文の問題

- 第19章：`insecure` ログインクラスの例で `:path=` 行の末尾に継続記号 `:\` が抜けている。
- 第19章：`mac_portacl` の「カーネル設定行」だけ `options` が付いていない。
- 第19章：LOMACの例で `getfmac` にもラベルを渡している。
- 第19章：Nagios例が古い `www/apache22` を前提にしている。
- 第20章：`expire-after:10M` が合計サイズによる期限指定であることを補足。

補足の根拠は、FreeBSD 15.1のマニュアル [mac_portacl(4)](https://man.freebsd.org/cgi/man.cgi?query=mac_portacl&sektion=4)、[getfmac(8)](https://man.freebsd.org/cgi/man.cgi?query=getfmac&sektion=8)、[audit_control(5)](https://man.freebsd.org/cgi/man.cgi?query=audit_control&sektion=5)で確認しました（2026-11-04）。固定原文の時点の仕様との差は未確認です。継続記号の漏れとapache22は、固定原文の内容と手元の記述から判断した補足で、一次資料での確認対象ではありません。

## 再校正（2026-11-04）

PR #7で追加された[引き継ぎ文書](translation-handoff.md)の方針に沿って、再度全節を見直しました。

- 訳注は原文と区別し、技術的な補足はFreeBSD 15.1のマニュアルで確認してリンクを残した（上記）。
- 最新のmain（PR #7の取り込み後）へリベースし、新しい共通検査器と他範囲の検査がすべて成功することを確認。
- マニフェストのcounts（見出し・アンカー・コード・表）を、実ファイルおよびPandocのAST集計と照合。
- `expire-after` の訳注を、期間・合計サイズ・両者の組み合わせという一次資料の説明に合わせて修正。
- 監査パイプの説明は、「複製型」を「クローン型（cloning）」に直した。
- 原文の `.txt` に末尾空白があるため、固定原文を改変せずに `git diff --check` を通せるよう、`handbook/en/` を対象外とする `.gitattributes` を追加。

## 検証

`python3 scripts/check_ch19_ch20_translations.py` は原文ハッシュと翻訳済み章の節・階層・アンカー・コード・画像・リンクを検査します。`--require-complete` は両章の完了を要求します。構造検査は訳文の意味やFreeBSD実機動作の保証ではありません。

## 最終確認（2026-11-04）

- 両章の38見出し・40アンカー・49コード例を固定原文と照合。画像は原文にありません。
- 両章をPandocのGFMとして解析。第19章は27見出し・35コードブロック、第20章は11見出し・14コードブロック・2表を確認。
- 検査器の負例（コード変更、アンカー欠落、見出し階層変更、原文ハッシュ変更）が失敗することを確認。
- 両章の完了を必須とするGitHub Actionsを追加。
- 既存第1〜14章、第16章、第23・24章の検査も成功。これらの章の訳文・検査器は変更していません。
- 第15章（Security）に対応するアンカーが未整備のため、Securityへの参照は公式サイトへのリンクにしています。

FreeBSD実機でのMACポリシーの適用・監査設定の試験は未実施です。第三者の専門校閲と、取得後の上流変更への追随も未実施です。状態の「自己校正済」はこれらを終えた意味ではありません。
