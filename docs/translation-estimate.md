# FreeBSD Handbook 日本語翻訳 — 工数見積もり（概算）

> 出典: プロジェクト起票時に整理した概算（2026-08）。  
> 前提の詳細は本文のとおり。**単語数計測前の相対見積**です。

## 概要（簡潔）

FreeBSD Handbook は FreeBSD Documentation Project が維持する公式包括ドキュメントです。インストールから日常利用、管理、ネットワーク、セキュリティ、ストレージ（特に ZFS）、仮想化までを扱います。Part I〜V 相当で本編約 35 章＋付録。対象リリースは主に 15.x/14.x。PDF は約 25MB、オンラインは実質 1000 ページ超相当。

## 前提

| 含む | 含まない |
|------|----------|
| 初訳・自己校正・最低限の用語集 | 第三者専門校閲 |
| 実用レベル（用語一貫・コマンド正確） | AsciiDoc 細構造・画像 L10n |
| | 継続的 upstream 同期・出版最終校正 |

- 翻訳者: 技術英日＋ FreeBSD/Unix 知識あり（薄い場合 1.5〜2×）
- 生産性目安: 原文 200〜400 語/時
- **本編総工数目安: 1,400〜2,200 人時**

## 章別（人時）

### Part I Getting Started

| 章 | 時間 |
|----|------|
| 1 Introduction | 20–35 |
| 2 Installing FreeBSD | 90–140 |
| 3 FreeBSD Basics | 70–110 |
| 4 Packages and Ports | 80–120 |
| 5 X Window System | 50–80 |
| 6 Wayland | 35–55 |

### Part II Common Tasks

| 章 | 時間 |
|----|------|
| 7 Desktop / ネットワーク基礎 | 40–70 |
| 8 Multimedia | 40–65 |
| 9 Kernel config | 50–80 |
| 10 Printing | 30–50 |
| 11 Linux Binary Compatibility | 35–55 |
| 12 WINE | 30–50 |

### Part III System Administration

| 章 | 時間 |
|----|------|
| 13 Config and Tuning | 60–95 |
| 14 Booting | 40–65 |
| 15 Security | 100–160 |
| 16 Jails | 80–130 |
| 17 OCI Containers | 40–70 |
| 18 MAC | 50–80 |
| 19 Security Event Auditing | 40–65 |
| 20 Storage | 70–110 |
| 21 GEOM | 50–80 |
| 22 OpenZFS | 120–180 |
| 23 Other File Systems | 35–55 |
| 24 Virtualization | 70–110 |
| 25 Localization | 40–65 |
| 26 Updating/Upgrading | 50–80 |
| 27 DTrace | 40–70 |
| 28 USB Device Mode | 25–45 |

### Part IV Network

| 章 | 時間 |
|----|------|
| 29 Serial | 30–50 |
| 30 PPP | 30–50 |
| 31 Electronic Mail | 50–80 |
| 32 Network Servers | 90–140 |
| 33 Firewalls | 80–130 |
| 34 Advanced Networking | 90–140 |

### 付録など

| 章 | 時間 |
|----|------|
| Preface | 15–30 |
| A Obtaining FreeBSD | 20–35 |
| B Bibliography | 15–25 |
| C Internet Resources | 15–25 |
| D OpenPGP Keys | 10–20 |
| Glossary | 30–50（用語統一の影響大） |

## 注意

- ZFS / Security / Jails / Network Servers / Advanced Networking / Install が重い
- 既存 ja 版・他言語用語集の活用で短縮可
- 現実的には分担＋用語集先行。一人フルタイムなら数ヶ月〜半年以上
- 精度向上には AsciiDoc 語数計測が有効
