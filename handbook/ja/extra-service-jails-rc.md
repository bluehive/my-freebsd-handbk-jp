# FreeBSD Service Jails と rc システム解説まとめ

> **翻訳・整理状態**: おまけ章（ユーザー提供まとめを MD 化・字句整備）  
> **位置づけ**: Handbook 本編外。`rc(8)` / Service Jails / `sysrc(8)` の横断メモ  
> **関連**: [第16章 Jail](16-jails.md) / [extra-appjail-ephemeral](extra-appjail-ephemeral.md) / [Issue #1](https://github.com/bluehive/my-freebsd-handbk-jp/issues/1)  
> **注意**: 公式 Handbook の代替ではない。正確なフラグ・版依存は man と現行 docs を確認すること。  
> **著作**: 本整理文はリポジトリ BSD-2-Clause。FreeBSD の名称・概念はそれぞれのプロジェクトに帰属。

このドキュメントは、FreeBSD の **Service Jails** および **rc システム**（`rc.d` / `rc.conf` / `sysrc`）に関する一連の解説を、章立てで整理したものです。  
他のシステムやドキュメントへの転載を想定して作成しています。

---

## 1. FreeBSD Service Jails の概要

### 1.1 Service Jails とは

Service Jails は FreeBSD **15** 系統から本格導入が進んだ機能で、`rc(8)` システムを拡張し、`rc.d` サービス（デーモン）を **自動的に Jail 内で起動** できるようにしたものです。

| 項目 | 内容 |
|------|------|
| 主導 | Alexander Leidinger 氏 |
| ベース | インフラと主要な `rc.d` サービスは 15-CURRENT 系にコミット済み |
| 文書 | Handbook および関連ドキュメントも更新済み |
| Ports | 対応進行中（2024 年時点の目安: 起動スクリプト約 1,460 のうち約 80 程度が対応） |

**主な対応例**: PostgreSQL、DNS サーバ、FTP、PHP、dovecot、postfix、rspamd、amavisd-new、clamav など。

### 1.2 仕組みのポイント

- 親（ホストまたは親 Jail）のファイルシステムを **そのまま継承**（Jail の root path は `/`）
- ホストと **同じユーザーアカウント** を共有
- デフォルトで通常の Jail 制限を適用
  - プロセス可視性の制限
  - ネットワークアクセス制限
  - ファイルシステムマウント権限の制限
  - SysV IPC 制限 など
- `*_svcj_options` で **追加権限** を付与可能（例）
  - `net_basic` … 親の IPv4/IPv6 を継承し、予約ポートを開ける、など基本ネットワーク
  - `netv4` / `netv6`
  - `net_raw` / `net_all`
  - その他、サービスが必要とする権限セット（man / Handbook の一覧を参照）

### 1.3 設定方法

設定はほぼ **`rc.conf`（と `sysrc`）だけ** で完結します。

```sh
# 例: nginx を Service Jail で動かす
sysrc nginx_enable=YES
sysrc nginx_svcj=YES
sysrc nginx_svcj_options=net_basic

# 運用上の注意
# - サービスを一度停止してから svcj を有効化し、再起動する
# - Jail 名は典型的に svcj-<サービス名> になる
# - 対応サービスをまとめて有効化: svcj_all_enable=YES
```

```sh
# rc.conf に直接書く場合のイメージ
nginx_svcj="YES"
nginx_svcj_options="net_basic"
```

### 1.4 他の Jails との違い

| 項目 | Service Jails | 従来の Jails（Thick / Thin） |
|------|---------------|------------------------------|
| ファイルシステム | ホストと完全共有（FS 隔離なし） | 独立したファイルシステム |
| セットアップ | 極めて簡単（`rc.conf` の 1〜2 行） | 比較的手間がかかる |
| リソース効率 | 高い | やや重い |
| プロセス隔離 | あり | あり |
| セキュリティ強度 | 「ある程度」の保護 | より強力 |

### 1.5 用途と注意点

**適した用途**

- 既存デーモンを **最小限の手間** で隔離したい
- **プロセス可視性** を制限したい
- フル Jail の管理コストを避けつつ、セキュリティの一層を足したい

**注意点**

- **ファイルシステム隔離がない** ため、侵害時の影響がホスト全体に及びうる
- フルな隔離が必要な用途（マルチテナント、非信頼コードなど）には不向き
- データ分離・作り直し前提の運用は [appjail-ephemeral](extra-appjail-ephemeral.md) や Thick/Thin + ZFS の方が向く場合がある

---

## 2. Practical rc.d scripting in BSD の概要

公式記事 **「Practical rc.d scripting in BSD」** は、BSD の `rc.d` フレームワークで実際にサービス起動スクリプトを書くための実践解説です。

- 上流（英語）: https://docs.freebsd.org/en/articles/rc-scripting/  
  （版・ URL は Documentation Portal で確認）

### 2.1 記事の目的

- 形式的な man と、実際のスクリプト作成の **あいだを埋める**
- 「簡単な例から始めて徐々に複雑にする」形式

### 2.2 主な構成

1. Introduction — rc の歴史と `rc.d` の誕生  
2. Outlining the Task — 作成前の整理  
3. A Dummy Script — 最小例  
4. A Configurable Dummy Script — `rc.conf` 連携  
5. Startup and Shutdown of a Simple Daemon  
6. Startup and Shutdown of an Advanced Daemon — フック、追加コマンド、シグナルなど  
7. Connecting a Script to the rc.d Framework — `PROVIDE` / `REQUIRE` / `BEFORE` / `KEYWORD`  
8. Giving More Flexibility — 引数の扱い  
9. **Making a Script Ready for Service Jails**（重要）  
10. Advanced rc-scripting: Instancing — 複数インスタンス  
11. Further Reading  

### 2.3 Service Jails 対応のポイント（記事第9章相当）

- 長時間動くサービスは Service Jails 対応が **推奨**
- 不向きなスクリプト（マウント処理、カーネル設定変更など）は **明示的に無効化**
- 対応させる場合の記述例:

```sh
: ${dummy_svcj_options:=""}           # 追加権限不要
: ${dummy_svcj_options:="net_basic"}  # ネットワークが必要
```

- 無効化する場合は `load_rc_config` の後に例えば:

```sh
dummy_svcj="NO"
```

---

## 3. rc.conf(5) の概要

`rc.conf` は FreeBSD の起動時設定を制御する **中心的な設定ファイル** です。

### 3.1 役割

- ホスト名、ネットワーク、サービスの起動制御などを記述
- それ自体がコマンドを次々実行するファイルではなく、各種起動スクリプトが読んで分岐する **「設定の箱」**

### 3.2 ファイルの階層

| 順 | パス | 役割 |
|----|------|------|
| 1 | `/etc/defaults/rc.conf` | デフォルト値 |
| 2 | `/etc/rc.conf` | 管理者が上書きするメイン |
| 3 | `/etc/rc.conf.local` | ローカル上書き |

**後から読み込まれたものが優先**（後勝ち）。

### 3.3 ポイント 5 つ

1. **階層構造** — defaults → `rc.conf` → `rc.conf.local`  
2. **有効化は `*_enable="YES"` が基本** — 例: `sshd_enable="YES"`、`nginx_enable="YES"`  
3. **ネットワーク設定が充実** — `ifconfig_*`、`defaultrouter`、ファイアウォール関連など  
4. **Service Jails もここで制御**  
   - `サービス名_svcj="YES"`  
   - `サービス名_svcj_options="net_basic"`  
   - `svcj_all_enable="YES"`  
5. **編集** — 直接エディタより **`sysrc` 推奨**。重要変数変更時は復旧手段を確保  

---

## 4. rc.d と rc.conf の関係

### 4.1 役割の違い

| 項目 | 役割 | 主な場所 |
|------|------|----------|
| `rc.conf` | 設定ファイル（指示書） | `/etc/rc.conf`、`/etc/rc.conf.local` など |
| `rc.d` | 実行スクリプト（作業者） | `/etc/rc.d/`、`/usr/local/etc/rc.d/` |

### 4.2 関係性

```
rc.conf（設定） → 読み込まれる → rc.d スクリプト（実行）
```

`rc.conf` に書いた内容を、`rc.d` スクリプトが読み取り、起動・停止を行う。

### 4.3 ユーザーが管理するのはどれか

- **日常管理の主戦場は `rc.conf`（と `sysrc`）**
  - 有効化・無効化、オプション、Service Jails 設定
- `/etc/rc.d/` のベースシステム用スクリプトは **原則編集しない**（アップデートで上書きされうる）
- 独自サービスを足すときだけ `/usr/local/etc/rc.d/` にスクリプトを置く

---

## 5. sysrc コマンドの詳細な使い方

`sysrc` は `rc.conf` 系を安全に確認・変更するための公式コマンドです。

### 5.1 基本構文

```sh
sysrc [オプション] 変数名[=値]
sysrc [オプション] 変数名+=値     # リストに追加
sysrc [オプション] 変数名-=値     # リストから削除
```

### 5.2 主な使い方

**値の確認**

```sh
sysrc sshd_enable          # 値を表示
sysrc -n sshd_enable       # 値だけ
sysrc -a                   # 変更された設定一覧
sysrc -v 変数名            # どのファイルで定義されているか
```

**値の設定**

```sh
sysrc sshd_enable=YES
sysrc nginx_enable=YES
sysrc nginx_svcj=YES
sysrc nginx_svcj_options=net_basic
```

**リスト操作**

```sh
sysrc cloned_interfaces+=gif0
sysrc cloned_interfaces-=gif0
```

**変数の削除**

```sh
sysrc -x 変数名
```

### 5.3 よく使うオプション

| オプション | 意味 |
|------------|------|
| `-a` | 変更された設定だけ一覧 |
| `-A` | すべての設定を表示 |
| `-n` | 値だけ表示 |
| `-v` | 定義ファイルを表示 |
| `-f ファイル` | 指定ファイルを対象にする |
| `-x` | 変数を削除 |
| `-j jail名` | 指定 Jail 内で操作 |

### 5.4 注意点

- `sysrc` は **設定を書き換えるだけ**で、サービスを即座に起動・停止は **しない**
- `vi` 直編集より安全（構文ミスや重複を減らせる）
- リスト操作（`+=` / `-=`）は重複を自動で防いでくれることが多い

サービス反映の例:

```sh
service nginx restart
# または
service nginx stop
sysrc nginx_svcj=YES
service nginx start
```

---

## まとめ

| 項目 | 要点 |
|------|------|
| Service Jails | FreeBSD 15 系統で強化。デーモンを手軽に Jail 化できる **軽量な隔離**（FS は共有） |
| `rc.conf` | ユーザーが主に管理する設定ファイル |
| `rc.d` | 実際の起動スクリプト（ベースのものは基本触らない） |
| `sysrc` | `rc.conf` を安全に操作する **推奨コマンド** |

このまとめが、FreeBSD の起動制御と Service Jails の理解に役立てば幸いです。

---

## 関連リンク（深掘り用）

| 資源 | URL / パス |
|------|------------|
| Handbook Jails | https://docs.freebsd.org/en/books/handbook/jails/ |
| 本リポ 16 章ドラフト | [16-jails.md](16-jails.md) |
| rc-scripting 記事 | https://docs.freebsd.org/en/articles/rc-scripting/ |
| `rc.conf(5)` / `rc(8)` / `sysrc(8)` | man ページ |
| AppJail ephemeral | [extra-appjail-ephemeral.md](extra-appjail-ephemeral.md) |

## 編集メモ

- ユーザー投稿テキストに混入していた文字化け・重複（「メントへの転載…」「# Fr:」など）を文脈から整理した。
- `*_svcj_options` の正確な一覧は版によって増減しうるため、運用前に man / Handbook を照合すること。
