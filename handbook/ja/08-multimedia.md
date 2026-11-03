<a id="multimedia"></a>
# 第8章 マルチメディア

> **状態:** 意訳ドラフト。固定原文の全節・表・コード・画面例を照合しています。音声・カメラ・スキャナーの実機検証は未実施です。
> **原文:** [Multimedia](https://docs.freebsd.org/en/books/handbook/multimedia/)
> **照合版:** freebsd/freebsd-doc `a39743a3b0535f4498735119317889ea2bdfeb28`（2026-11-04取得）。[保存原文](../en/through-ch14/08-multimedia.adoc.txt)・[出典記録](../../docs/translation-through-ch14.json)
> **章番号:** 本リポジトリでは第8章、固定上流では第9章です。
> **著作権:** 原文 © The FreeBSD Documentation Project。日本語訳はリポジトリのBSD-2-Clauseに従います。

機器名・番号・IDは原文の例です。自分のハードウェアの検出結果に合わせて設定します。アプリや会議サービスの対応表も原文時点の情報であり、現在の全環境で動くことを保証するものではありません。`#` はroot、`%`・`$` は一般ユーザーのプロンプトです。

<a id="multimedia-synopsis"></a>
## この章で扱うこと

FreeBSDの音声・動画・画像処理を概観します。各種ハードウェアやメディア形式・コーデック、作成・再生のためのアプリに加え、設定、問題の切り分け、品質の調整を扱います。日常の再生からコンテンツ制作まで、実際に使い始めるための例を示します。

<a id="sound-setup"></a>
## サウンドデバイスを認識させる

通常はFreeBSDが自動検出します。対応機器は `sound(4)` を確認してください。正しく検出されていないときだけ、追加のモジュール読み込みを検討します。

機種や必要なモジュールが分からなければ、各ドライバーをまとめて試すメタドライバーを読み込めます。

```shell
# kldload snd_driver
```

起動時に読み込む場合は `/boot/loader.conf` に次を置きます。

```text
snd_driver_load="YES"
```

<a id="sound-testing"></a>
### 音を確認する

デバイスが検出されたかを調べます。

```shell
% dmesg | grep pcm
```

出力例です。

```text
pcm0: <Conexant CX20561 (Hermosa) (Analog 2.0+HP/2.0)> at nid 26,22 and 24 on hdaa0
pcm1: <Conexant CX20561 (Hermosa) (Internal Analog Mic)> at nid 29 on hdaa0
```

現在のサウンドデバイスは次でも確認できます。

```shell
# cat /dev/sndstat
```

再生・録音への対応と既定の機器が表示されます。

```text
Installed devices:
pcm0: <Conexant CX20561 (Hermosa) (Analog 2.0+HP/2.0)> (play/rec) default
pcm1: <Conexant CX20561 (Hermosa) (Internal Analog Mic)> (rec)
```

pcmデバイスがなければ、読み込んだドライバーが適切かを再確認します。認識できたら、`beep(1)` で音を出して試せます。

```shell
% beep
```

<a id="sound-mixer"></a>
### 音量を調整する

FreeBSD Sound Systemのミキサー値を表示・変更するツールがあります。

| 名前 | 原文のライセンス | 提供元 | UI |
|---|---|---|---|
| `mixer(8)` | BSD-2 | ベースシステムに含む | CLI |
| dsbmixer | BSD-2 | `audio/dsbmixer` | Qt |
| Plasmaの音量ウィジェット | GPL 2.0 | `audio/plasma6-plasma-pa` | Qt |
| mixertui | BSD-2 | `audio/mixertui` | TUI |

<a id="graphics-card-sound"></a>
### GPUの音声出力と既定デバイス

GPUにもHDMI・DisplayPort向けの音声デバイスがあり、どれが既定か分かりにくい場合があります。pcmの列挙順を確認します。

```shell
% dmesg | grep pcm
```

出力例です。

```text
pcm0: <HDA NVIDIA (Unknown) PCM #0 DisplayPort> at cad 0 nid 1 on hdac0
pcm1: <HDA NVIDIA (Unknown) PCM #0 DisplayPort> at cad 1 nid 1 on hdac0
pcm2: <HDA NVIDIA (Unknown) PCM #0 DisplayPort> at cad 2 nid 1 on hdac0
pcm3: <HDA NVIDIA (Unknown) PCM #0 DisplayPort> at cad 3 nid 1 on hdac0
hdac1: HDA Codec #2: Realtek ALC889
pcm4: <HDA Realtek ALC889 PCM #0 Analog> at cad 2 nid 1 on hdac1
pcm5: <HDA Realtek ALC889 PCM #1 Analog> at cad 2 nid 1 on hdac1
pcm6: <HDA Realtek ALC889 PCM #2 Digital> at cad 2 nid 1 on hdac1
pcm7: <HDA Realtek ALC889 PCM #3 Digital> at cad 2 nid 1 on hdac1
```

この例ではNVIDIA側が先に並び、Realtekのアナログ出力は `pcm4` です。これを既定にするには次を使います。

```shell
# sysctl hw.snd.default_unit=4
```

再起動後も維持する場合は `/etc/sysctl.conf` へ追加します。

```text
hw.snd.default_unit=4
```

数字の4は、この例の機器番号です。

<a id="automatically-switching-headphones"></a>
### ヘッドホンへの自動切り替え

出力の切り替えがうまくいかない機種では、device.hintsで調整できる場合があります。まず検出結果を確認します。

```shell
% dmesg | grep pcm
```

原文例です。

```text
pcm0: <Realtek ALC892 Analog> at nid 23 and 26 on hdaa0
pcm1: <Realtek ALC892 Right Analog Headphones> at nid 22 on hdaa0
```

この例に対する `/boot/device.hints` の指定です。

```text
hint.hdac.0.cad0.nid22.config="as=1 seq=15 device=Headphones"
hint.hdac.0.cad0.nid26.config="as=2 seq=0 device=speakers"
```

> **注意:** hdac番号・cad番号・nid・associationなどは機種依存です。この値を別の機種へそのまま適用する手順ではありません。

<a id="resampling-quality"></a>
### リサンプリング品質を調整する

音声のサンプルレートを変える処理をリサンプリングと呼びます。デジタル音声機器とアプリの受け付けるレートが異なる場合や、低いレートの音源を再生する場合などに自動で行われます。可能ならドライバーの外側でレートを合わせますが、できない場合やハードウェアの処理品質が十分でない場合は調整できます。

> **訳注:** 原文の「192000kHz」「48000kHz」は単位が混同されています。音声の例としては192000Hz＝192kHz、48000Hz＝48kHzのように区別して読みます。

通常の音楽・会議などでは既定値で十分で、多くのアプリが使う48kHzに揃っていれば変換は少なく済みます。制作・録音など品質が重要な場面で、必要に応じて高くします。

原文の最高品質の例です。

```shell
# sysctl hw.snd.feeder_rate_quality=4
# sysctl hw.snd.feeder_rate_round=0
```

- `feeder_rate_quality=4`: 阻止域100dB、164タップ、帯域97%と説明されています。
- `feeder_rate_round=0`: 大きな素数の分割も使い、高い精度を保つ設定です。

維持する場合は `/etc/sysctl.conf` へ記述します。品質を上げるとCPU負荷や遅延にも影響するため、必要性と実際の動作を確認します。詳細は `sound(4)` を参照してください。

<a id="troubleshooting-sound"></a>
### 音の問題を切り分ける

<a id="multimedia-sound-common-error-messages"></a>

`xxx: can't open /dev/dsp!` と出た場合、`fstat | grep dsp` で別のアプリがデバイスを開いたままにしていないか確認します。原文ではesoundやKDEの音声機能を例に挙げています。

PulseAudioを使うアプリでは、`hw.snd.default_unit` の変更を反映するためにデーモンの再起動が必要な場合があります。動作中に設定する方法としてpacmdもあります。

```shell
# pacmd
Welcome to PulseAudio 14.2! Use "help" for usage information.
>>>
```

原文は出力先を4へ変える例を示しています。

```text
set-default-sink 4
```

> **注意:** PulseAudioのsink番号とFreeBSDのpcm番号を、必ず同じ番号だと決めつけないでください。実際の出力先に合わせます。pacmdから抜ける際は **Ctrl+D** を使います。`exit` はインターフェースだけでなくPulseAudioデーモンを終了させると、原文は警告しています。

<a id="audio-ports"></a>
## 音楽プレーヤー

Portsで利用できる音楽再生ソフトの例です。

| 名前 | 原文のライセンス | Portsのパス | UI |
|---|---|---|---|
| Elisa | LGPL 3.0 | `audio/elisa` | Qt |
| GNOME Music | GPL 2.0 | `audio/gnome-music` | GTK+ |
| Audacious | BSD-2 | `multimedia/audacious` | Qt |
| cmus | GPL 2.0 | `audio/cmus` | TUI |

<a id="elisa"></a>
### Elisa

KDEコミュニティの、簡潔で使いやすい音楽プレーヤーです。

```shell
# pkg install elisa
```

<a id="gnome-music"></a>
### GNOME Music

曲を見つけやすい表示と、単純で分かりやすい操作の両立を目指すGNOMEの音楽アプリです。

```shell
# pkg install gnome-music
```

<a id="audacious"></a>
### Audacious


XMMSの流れを引くオープンソースの音楽プレーヤーで、資源の効率的な利用を重視します。

```shell
# pkg install audacious-qt6 audacious-plugins-qt6
```

OSSに直接対応していますが、設定のAudioタブで選ぶ必要があります。

<a id="moc-music-on-console"></a>
<a id="cmus"></a>
### cmus：C* Music Player

Unix系向けの小さく速いコンソール音楽プレーヤーです。各種入出力プラグイン、CUEシート、Unicode、last.fm・libre.fmなどへの再生記録送信、選んだファイルへの外部タグ編集ツール起動、UNIXソケット経由の制御などを備えます。

```shell
# pkg install cmus
```

<a id="video-ports"></a>
## 動画プレーヤー


動画再生ソフトの例です。

| 名前 | 原文のライセンス | Portsのパス | UI |
|---|---|---|---|
| mpv | GPL 2.0 | `multimedia/mpv` | CLI |
| SMPlayer | GPL 2.0 | `multimedia/smplayer` | Qt |
| VLC | GPL 2.0 | `multimedia/vlc` | Qt |
| Kodi | GPL 2.0 | `multimedia/kodi` | X11 |

<a id="mplayer"></a>
<a id="mpv"></a>
### mpv

コマンドラインから使える自由なメディアプレーヤーです。多数の形式・音声／動画コーデック・字幕に対応し、各プラットフォームの多くのハードウェア復号APIも利用できます。高品質な拡大・縮小、HDRからSDRへの変換を細かく調整でき、設定をプロファイルへまとめ、起動オプションやパスなどの条件で選べます。

```shell
# pkg install mpv
```

原文の `~/.config/mpv/mpv.conf` の例です。

```text
vo=gpu-next
gpu-context=wayland
hwdec=auto
screenshot-jpeg-quality=100
scale=ewa_lanczos4sharpest
dscale=ewa_lanczos4sharpest

[TTRPG]
profile-cond=path:find('ttrpg')
profile=fast
save-position-on-quit=yes

[hdr]
scale=bilinear
dscale=bilinear
dither=no
correct-downscaling=no
linear-downscaling=no
sigmoid-upscaling=no
hdr-compute-peak=yes
hdr-peak-percentile=99.995
hdr-contrast-recovery=0.30
```

- `gpu-next` は新しい描画出力を使い、関連機能や品質改善を利用します。
- `gpu-context=wayland` は、Waylandで表示崩れやクラッシュが出る場合に明示する設定として紹介されています。X11向けの環境へそのまま適用しません。
- `hwdec=auto` はGPUによる復号が使えるかを自動検出します。
- スケーリングの高品質な設定で処理が追い付かずフレームが飛ぶ場合は、軽い設定へ戻します。
- `TTRPG` は長いセッション録画向けの例で、パスに `ttrpg` があれば適用されます。組み込みのfastプロファイルでCPU／GPU負荷を抑え、終了位置を保存します。
- `hdr` は性能の低い統合GPUでHDRコンテンツを再生するための例です。

HDR用を明示する原文例です。

```text
$ mpv --profile=hdr hdr_video.mkv
```

詳しい例と設定項目はmpvのリファレンスマニュアルを参照してください。

<a id="smplayer"></a>
### SMPlayer

MPlayerのフロントエンドとして、動画・DVD・VCDの再生から各種フィルターなどの高度な操作までをGUIで扱うことを目指すプレーヤーです。

```shell
# pkg install smplayer
```

<a id="vlc"></a>
### VLC media player

MPEG-1/2/4、DivX、MP3、Oggなどの形式、DVD・VCD、各種ストリーミングに対応するクロスプラットフォームのプレーヤーです。IPv4／IPv6のユニキャスト・マルチキャスト配信サーバーとしても使え、配信や保存の際にリアルタイム変換もできます。

```shell
# pkg install vlc
```

<a id="kodi"></a>
### Kodi（旧XBMC）

オープンソースのメディアプレーヤー兼エンターテインメント環境です。ローカル・ネットワーク上の保存先やインターネットから、動画・音楽・ポッドキャストなどを再生できます。

```shell
# pkg install kodi
```

<a id="conferencing-meetings"></a>
## ビデオ会議

FreeBSDのデスクトップから会議へ参加できます。まずWebカメラを準備し、その後でブラウザーとサービスの組み合わせを確認します。

<a id="webcam-setup"></a>
### Webカメラを準備する

USBカメラやDVB USB機器を扱うwebcamdと、映像確認用のpwcviewを導入します。

```shell
# pkg install webcamd pwcview
```

webcamdを起動時に有効化します。

```shell
# sysrc webcamd_enable=YES
```

利用者はwebcamdグループへ追加します。`username` を実際の名前へ置き換えます。

```shell
# pw groupmod webcamd -m username
```

必要なcuseモジュールを読み込みます。

```shell
# kldload cuse
```

起動時にも読み込むよう設定します。

```shell
# sysrc kld_list+=cuse
```

利用可能な機器を一覧にします。

```shell
# webcamd -l
```

原文例では最初の行がカメラです。

```text
webcamd [-d ugen0.2] -N SunplusIT-Inc-HP-TrueVision-HD-Camera -S unknown -M 0
webcamd [-d ugen1.3] -N Realtek-802-11n-WLAN-Adapter -S 00e04c000001 -M 0
```

検出したカメラを指定する例です。

```shell
# sysrc webcamd_0_flags="-N SunplusIT-Inc-HP-TrueVision-HD-Camera"
```

USBの差し口を変えると識別番号が変わり、`-d` 指定やrc.confの更新が必要な場合があります。可能なら一覧に出た名前を `-N`、シリアル番号を `-S` で指定すると、接続位置の変更へ対応しやすくなります。固定された内蔵カメラなどでは `-d` も使えます。

サービスを開始します。

```shell
# service webcamd start
```

接続された例です。

```text
Starting webcamd.
webcamd 1616 - - Attached to ugen0.2[0]
```

pwcviewで映像を確認します。

```shell
% pwcview -f 30 -s vga
```

原文の表示例です。

![Webカメラを準備する：pwcview.png](https://raw.githubusercontent.com/freebsd/freebsd-doc/a39743a3b0535f4498735119317889ea2bdfeb28/documentation/static/images/books/handbook/multimedia/pwcview.png)

<a id="meetings-software-status"></a>
### 会議サービスの原文上の対応状況

以下は固定原文に記録されたブラウザー別の動作報告です。サービスやブラウザーの更新で変わるため、利用前に自分の環境で確認してください。

| サービス | Firefox | Chromium | サイト |
|---|---|---|---|
| Microsoft Teams | 動作しない | 動作する | [Teams](https://teams.live.com) |
| Google Meet | 動作する | 動作する | [Meet](https://meet.google.com/) |
| Zoom | 動作する | 動作する | [Zoom](https://zoom.us) |
| Jitsi | 動作する | 動作する | [Jitsi](https://meet.jit.si/) |
| Discord | 動作しない | 動作しない | [Discord](https://discord.com/) |
| BigBlueButton | 動作しない | 動作する | [BigBlueButton](https://bigbluebutton.org/) |

<a id="scanners"></a>
## 画像スキャナー

FreeBSDでは、Portsで提供される [SANE（Scanner Access Now Easy）](http://www.sane-project.org)を使ってスキャナーへアクセスできます。

<a id="scanners-kernel-usb"></a>
### 対応機種かを確認する

設定を始める前に、機器がSANEに対応しているか確認します。接続した状態でUSB機器を一覧にします。

```shell
# usbconfig list
```

原文例です。

```text
ugen4.2: <LITE-ON Technology USB NetVista Full Width Keyboard.> at usbus4, cfg=0 md=HOST spd=LOW (1.5Mbps) pwr=ON (70mA)
ugen4.3: <Logitech USB Optical Mouse> at usbus4, cfg=0 md=HOST spd=LOW (1.5Mbps) pwr=ON (100mA)
ugen3.2: <HP Deskjet 1050 J410 series> at usbus3, cfg=0 md=HOST spd=HIGH (480Mbps) pwr=ON (2mA)
```

対象のベンダーIDと製品IDを調べます。`3.2` は例のUSB機器番号です。

```shell
# usbconfig -d 3.2 dump_device_desc
```

USBポートを変えるとこの番号も変わる場合があります。実際の一覧に合わせて指定します。

```text
ugen3.2: <HP Deskjet 1050 J410 series> at usbus3, cfg=0 md=HOST spd=HIGH (480Mbps) pwr=ON (2mA)

bLength = 0x0012
bDescriptorType = 0x0001
bcdUSB = 0x0200
bDeviceClass = 0x0000  <Probed by interface class>
bDeviceSubClass = 0x0000
bDeviceProtocol = 0x0000
bMaxPacketSize0 = 0x0040
idVendor = 0x03f0
idProduct = 0x8911
bcdDevice = 0x0100
iManufacturer = 0x0001  <HP>
iProduct = 0x0002  <Deskjet 1050 J410 series>
bNumConfigurations = 0x0001
```

`idVendor` と `idProduct` が分かったら、[SANEの対応一覧](http://www.sane-project.org/lists/sane-mfgs-cvs.html)で製品IDを使って対象を確認します。

<a id="_sane_configuration"></a>
### SANEを設定する

SANEは機種ごとのbackendを通じてアクセスします。

```shell
# pkg install sane-backends
```

USBスキャナーによってはファームウェアが必要です。原文例のHP機では `print/hplip` の導入も必要と説明されています。

次にdevdの設定を作ります。`/usr/local/etc/devd/saned.conf` の原文例です。

```text
notify 100 {
        match "system" "USB";
        match "subsystem" "INTERFACE";
        match "type" "ATTACH";
        match "cdev" "ugen[0-9].[0-9]";
        match "vendor" "0x03f0";
        match "product" "0x8911";
        action "chown -L cups:saned /dev/\$cdev && chmod -L 660 /dev/\$cdev";
};
```

`vendor` は先に調べたidVendor、`product` はidProductです。所有者・グループを含め、このHP機用の例を実際の機器・アカウント構成に合わせます。

devdを再起動します。

```shell
# service devd restart
```

SANEに含まれる `scanimage(1)` は機器一覧と画像取得に使えます。

```shell
# scanimage -L
```

認識できた場合の表示例です。

```text
device `hpaio:/usb/Deskjet_1050_J410_series?serial=XXXXXXXXXXXXXX' is a Hewlett-Packard Deskjet_1050_J410_series all-in-one
```

認識できない場合は次のように表示されます。接続・電源、必要に応じてsane-find-scanner、付属のREADME・FAQ・manページなどを確認します。

```text
No scanners were identified. If you were expecting something different,
check that the scanner is plugged in, turned on and detected by the
sane-find-scanner tool (if appropriate). Please read the documentation
which came with this software (README, FAQ, manpages).
```

scanimageから見えれば、原文の機器認識の設定は完了です。サービスを起動時に有効化する原文の設定は次のとおりです。

```shell
# sysrc saned_enable=YES
```

コマンドラインで画像を取得するほか、次のGUIも使えます。

| アプリ | 原文のライセンス | Portsのパス |
|---|---|---|
| skanlite | GPL 2.0 | `graphics/skanlite` |
| GNOME Simple Scan | GPL 3.0 | `graphics/simple-scan` |
| XSANE | GPL 2.0 | `graphics/xsane` |
