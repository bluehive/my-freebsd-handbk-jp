<a id="filesystems"></a>
# 第24章 その他のファイルシステム

本章では、Linux、Windows、macOSで使われるファイルシステムをFreeBSDから利用する方法を説明します。対応範囲と手順は、固定した公式原文に基づきます。

<a id="filesystems-synopsis"></a>
## 概要

ファイルシステムは、データを保存・整理し、必要なときに取り出すための仕組みです。ハードディスク、フラッシュメモリ、USBストレージなどを普段の作業で使えるようにします。OSによって、標準で使うファイルシステムは異なります。

FreeBSDでは従来からUFSを使い、改良版のUFS2も標準的な選択肢です。高度な機能、堅牢性、信頼性を備えるZFSも利用できます。詳しくは[ZFSの章](https://docs.freebsd.org/en/books/handbook/zfs/)を参照してください。

これらに加え、他のOSのファイルシステムにも対応しています。ただし、読み書きの対応範囲や利用方法は同じではありません。カーネルモジュールを読み込むものも、追加のユーザーランドツールを必要とするものもあります。

読む前に、[UNIXとFreeBSDの基本](03-basics.md)、[追加ソフトウェアの導入](04-ports.md)、[ディスクとデバイス名の基本](03-basics.md#disk-organization)および[ストレージ管理](https://docs.freebsd.org/en/books/handbook/disks/)を理解しておくと役立ちます。

本章で、標準のファイルシステムと追加対応の違い、各形式の対応範囲、機能の有効化とマウントの手順を学びます。

以下の `/dev/ada0s1` などは原文の例です。自分のパーティション名へ置き換え、マウント先のディレクトリが存在することを確認してください。原文のパッケージ名とPortsのカテゴリ名は異なる場合があるため、両方を区別して示します。

<a id="filesystems-linux"></a>
## Linuxのファイルシステム

FreeBSDには、Linux由来のファイルシステムを扱う機能もあります。本節ではEXT系列の対応範囲とマウント方法を説明します。

<a id="ext"></a>
### EXT：ext2・ext3・ext4

EXT系列を扱うカーネルの機能はFreeBSD 2.2からあります。`ext2fs(4)` ドライバは、ext2・ext3・ext4の読み書きに対応します。

**固定原文では、ジャーナリングと暗号化は未対応です。** 「ext4を扱える」ことを、ext4のすべての機能を利用できるという意味に受け取らないでください。

対象のパーティションと既存のマウント先を指定します。次は `/dev/ada1s1` を `/mnt` へマウントする例です。

```shell
# mount -t ext2fs /dev/ada1s1 /mnt
```

<a id="filesystems-windows"></a>
## Windowsのファイルシステム

FreeBSDではFAT、exFAT、NTFSを扱い、Windowsなどでフォーマットしたストレージへアクセスできます。形式ごとに使うドライバやツールが異なります。

<a id="fat"></a>
### FAT

FATは単純で、広く普及したファイルシステムです。新しい形式と比べると性能、信頼性、拡張性に制約がありますが、多くのOSが対応しているため、機器間のデータ交換によく使われます。

FATのパーティションと既存のマウント先を指定します。次は `/dev/ada0s1` を `/mnt` へ接続する例です。

```shell
# mount -t msdosfs /dev/ada0s1 /mnt
```

<a id="ex-fat"></a>
### exFAT

exFAT（Extended File Allocation Table）は、USBメモリやSDカードなどのフラッシュストレージに適した軽量な形式です。大きなファイルを扱え、多くのプラットフォームで使われるため、外付けストレージでのデータ交換に向きます。

FreeBSDでは、原文で `filesystems/exfat` として紹介されるPortのパッケージを導入し、FUSEカーネルモジュールを読み込みます。原文のパッケージ名は `fusefs-exfat` です。

```shell
# pkg install fusefs-exfat
```

FUSEのファイルシステムを使う前に、`fusefs(4)` を読み込みます。

```shell
# kldload fusefs
```

起動時にも読み込むには、`sysrc(8)` で `kld_list` に追加します。

```shell
# sysrc kld_list+=fusefs
```

対象のパーティションと既存のマウント先を指定します。

```shell
# mount.exfat /dev/ada0s1 /mnt
```

<a id="using-ntfs"></a>
### NTFS

NTFSはMicrosoftが開発した、Windowsで広く使われるファイルシステムです。FreeBSDでは、原文で `filesystems/ntfs` として紹介される追加ソフトウェアを通じて、NTFSの読み書きを行えます。

まずパッケージを導入します。原文のパッケージ名は `fusefs-ntfs` です。

```shell
# pkg install fusefs-ntfs
```

FUSEカーネルモジュールを読み込みます。

```shell
# kldload fusefs
```

起動時にも読み込む設定です。

```shell
# sysrc kld_list+=fusefs
```

`ntfs-3g` に対象のパーティションと既存のマウント先を指定します。

```shell
# ntfs-3g /dev/ada0s1 /mnt
```

<a id="filesystems-macos"></a>
## macOSのファイルシステム

FreeBSDでは、Appleのシステムで使われてきたHFS・HFS+のストレージへアクセスできます。以下はHFS/HFS+の説明であり、APFSのマウント手順ではありません。

<a id="hfs"></a>
### HFS・HFS+

HFS・HFS+は、APFSが登場する前のmacOSで主に使われた形式で、古いMacや外付けドライブなどに見られます。FreeBSDでは `filesystems/hfsfuse` を利用します。**固定原文で説明する対応範囲は読み取り専用です。**

まずパッケージを導入します。原文のパッケージ名は `fusefs-hfsfuse` です。

```shell
# pkg install fusefs-hfsfuse
```

FUSEカーネルモジュールを読み込みます。

```shell
# kldload fusefs
```

起動時にも読み込む設定です。

```shell
# sysrc kld_list+=fusefs
```

`hfsfuse` に対象のパーティションと既存のマウント先を指定します。

```shell
# hfsfuse /dev/ada0s1 /mnt
```
