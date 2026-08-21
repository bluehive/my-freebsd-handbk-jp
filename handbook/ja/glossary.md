# 用語集（作業用）

本リポジトリの訳語を揃えるための最小セット。Handbook 全体の公式用語集の代替ではない。

| 英語 | 日本語（採用） | 備考 |
|------|----------------|------|
| FreeBSD Handbook | FreeBSD ハンドブック | 書名は Handbook 併記可 |
| Ports Collection | Ports Collection（ポート集） | |
| package | パッケージ | `pkg` はコマンドのまま |
| jail | jail | 訳さない |
| committer | コミッター | |
| core team | Core チーム | |
| CURRENT | CURRENT | ブランチ名 |
| base system | 基本システム／ベースシステム | 文脈で |
| OpenZFS | OpenZFS | |
| root-on-ZFS | root-on-ZFS | |
| Boot Environment | ブート環境（BE） | |
| Mandatory Access Control | 必須アクセス制御（MAC） | 初出併記 |
| Capsicum | Capsicum | |
| encumbered | 権利付き（encumbered） | 歴史節 |
| snapshot | スナップショット | |
| man page | man ページ | |
| thick jail | シック jail | 完全なユーザランド |
| thin jail | シン jail | テンプレ共有／NullFS 等 |
| VNET jail | VNET jail | 仮想ネットワークスタック |
| Podman | Podman | OCI ランタイム |
| OCI | OCI | Open Container Initiative |
| securelevel | securelevel | セキュアレベル |
| IDS | IDS | 侵入検知 |
| OpenSSH | OpenSSH | |
| ACL | ACL | アクセス制御リスト |
| sudo / doas | sudo / doas | 権限委譲 |
| AppJail | AppJail | jail 管理フレームワーク（ports） |
| ephemeral | 短命／作り直し可能（ephemeral） | appjail-ephemeral(7) |
| cattle vs. pets | cattle（取替可能）vs pets（手厚く育成） | 運用比喩 |
| Makejail | Makejail | AppJail の定義ファイル |
| volume（AppJail） | ボリューム | 永続データ用 |
| nullfs | nullfs | ホスト→jail マウント |
| Service Jails | Service Jails | rc 連携の軽量 jail（FS 共有） |
| rc.conf | rc.conf | 起動設定の中心 |
| rc.d | rc.d | サービス起動スクリプト群 |
| sysrc | sysrc | rc.conf を安全に編集する公式 CLI |
| svcj | svcj | Service Jail 関連の rc 変数接尾辞 |

更新ルール: 章翻訳で迷ったらここに追記し、既存と衝突したら issue で決める。
