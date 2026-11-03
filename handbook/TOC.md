# 目次と翻訳ステータス

原文構成は [FreeBSD Handbook (en)](https://docs.freebsd.org/en/books/handbook/) および `freebsd/freebsd-doc` に準拠。

凡例: `未着手` / `ドラフト` / `自己校正済` / `完了`

| ID | 章 | 日本語 MD | 状態 | 備考 |
|----|-----|-----------|------|------|
| 00 | Preface | — | 未着手 | |
| 01 | Introduction | [01-introduction.md](ja/01-introduction.md) | **自己校正済（意訳）** | 2026-11-04 固定原文11見出し・1コード例へ再照合 |
| 02 | Installing FreeBSD (bsdinstall) | [02-bsdinstall.md](ja/02-bsdinstall.md) | **自己校正済（意訳）** | 2026-11-04 原文31見出し・5コード例を照合。実機検証は未実施 |
| 03 | FreeBSD Basics | [03-basics.md](ja/03-basics.md) | **自己校正済（意訳）** | 2026-11-04 固定原文40見出し・69コード例を再照合。実機検証は未実施 |
| 04 | Packages and Ports | [04-ports.md](ja/04-ports.md) | **自己校正済（意訳）** | 2026-11-04 原文34見出し・73コード例を照合。実機検証は未実施 |
| 05 | X Window System | [05-x11.md](ja/05-x11.md) | **自己校正済（意訳）** | 2026-11-04 原文21見出し・47コード例を照合。実機検証は未実施 |
| 06 | Wayland | [06-wayland.md](ja/06-wayland.md) | **自己校正済（意訳）** | 2026-11-04 原文10見出し・47コード例を照合。実機検証は未実施 |
| 07 | Desktop Applications | [07-desktop.md](ja/07-desktop.md) | **自己校正済（意訳）** | 2026-11-04 原文62見出し・70コード例を照合。実機検証は未実施 |
| 08 | Multimedia | [08-multimedia.md](ja/08-multimedia.md) | **自己校正済（意訳）** | 2026-11-04 原文25見出し・49コード例を照合。実機検証は未実施 |
| 09 | Kernel Configuration | [09-kernelconfig.md](ja/09-kernelconfig.md) | **自己校正済（意訳）** | 2026-11-04 原文7見出し・17コード例を照合。実機検証は未実施 |
| 10 | Printing | [10-printing.md](ja/10-printing.md) | **自己校正済（意訳）** | 2026-11-04 原文29見出し・47コード例を照合。実機検証は未実施 |
| 11 | Linux Binary Compatibility | [11-linuxemu.md](ja/11-linuxemu.md) | **自己校正済（意訳）** | 2026-11-04 原文13見出し・35コード例を照合。実機検証は未実施 |
| 12 | WINE | [12-wine.md](ja/12-wine.md) | **自己校正済（意訳）** | 2026-11-04 原文54見出し・23コード例を照合。実機検証は未実施 |
| 13 | Configuration and Tuning | [13-config.md](ja/13-config.md) | **自己校正済（意訳）** | 2026-11-04 原文42見出し・79コード例を照合。実機検証は未実施 |
| 14 | Booting Process | [14-boot.md](ja/14-boot.md) | **自己校正済（意訳）** | 2026-11-04 原文11見出し・12コード例を照合。実機検証は未実施 |
| 15 | Security | [15-security.md](ja/15-security.md) | **ドラフト** | 2026-08-21 高工数 |
| 16 | Jails | [16-jails.md](ja/16-jails.md) | **自己校正済** | 2026-11-04 保存済み原文の全66見出し・139コード例を照合。[検証記録](../docs/jails-proofreading.md)。実機検証・最新上流同期は未実施 |
| 17 | Containers | [17-containers.md](ja/17-containers.md) | **ドラフト** | 2026-08-21 Podman/OCI |
| 18 | MAC | — | 未着手 | |
| 19 | Security Event Auditing | — | 未着手 | |
| 20 | Storage / Disks | — | 未着手 | |
| 21 | GEOM | — | 未着手 | |
| 22 | OpenZFS | — | 未着手 | 最重量級 |
| 23 | Other File Systems | — | 未着手 | |
| 24 | Virtualization | — | 未着手 | |
| 25 | Localization | — | 未着手 | |
| 26 | Updating and Upgrading | — | 未着手 | |
| 27 | DTrace | — | 未着手 | |
| 28 | USB Device Mode | — | 未着手 | |
| 29 | Serial Communications | — | 未着手 | |
| 30 | PPP | — | 未着手 | |
| 31 | Electronic Mail | — | 未着手 | |
| 32 | Network Servers | — | 未着手 | 高工数 |
| 33 | Firewalls | — | 未着手 | 高工数 |
| 34 | Advanced Networking | — | 未着手 | 高工数 |
| A | Obtaining FreeBSD | — | 未着手 | |
| B | Bibliography | — | 未着手 | |
| C | Resources | — | 未着手 | |
| D | OpenPGP Keys | — | 未着手 | |
| G | Glossary | [glossary.md](ja/glossary.md) | ドラフト（種） | |

### おまけ（Handbook 本編外）

| ID | 文書 | 日本語 MD | 状態 | 備考 |
|----|------|-----------|------|------|
| X1 | appjail-ephemeral(7) | [extra-appjail-ephemeral.md](ja/extra-appjail-ephemeral.md) | **ドラフト** | 2026-08-21 / cattle·pets·短命 jail。Issue #1 関連 |
| X2 | Service Jails + rc / sysrc | [extra-service-jails-rc.md](ja/extra-service-jails-rc.md) | **ドラフト** | 2026-08-22 / ユーザーまとめ整理 |

英語スナップショット: `en/`（翻訳者向け原文テキスト）。
