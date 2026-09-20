# ffmpeg 命令配方（2176×1440 / 24fps / 48kHz 立体声 为基准，按需替换）

## R1 变速对齐切点（取前 D 秒、K 倍速）

```bash
ffmpeg -i clip.mp4 -filter_complex \
  "[0:v]trim=duration=D,setpts=(PTS-STARTPTS)/K,fps=24[v]; \
   [0:a]atrim=duration=D,atempo=K,asetpts=PTS-STARTPTS,aresample=48000[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 seg.mp4
# 验证：ffprobe -select_streams v:0 -show_entries stream=nb_frames seg.mp4
# 预期 nb_frames = round(D/K × 24)
```

## R2 片尾静帧卡（2.5s + 静音轨）

```bash
ffmpeg -loop 1 -i endcard.png -f lavfi -i anullsrc=r=48000:cl=stereo \
  -t 2.5 -c:v libx264 -crf 16 -pix_fmt yuv420p -r 24 -c:a aac -shortest endcard.mp4
```

## R3 多段拼接（6 段示例，段数改 n 与输入数）

```bash
ffmpeg -i s1.mp4 -i s2.mp4 -i s3.mp4 -i s4.mp4 -i s5.mp4 -i s6.mp4 -filter_complex \
  "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a][4:v][4:a][5:v][5:a]concat=n=6:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 out_noBGM.mp4
```

## R4 BGM 无缝循环 + 混音（BGM 长 16.138s 示例）

```bash
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out_noBGM.mp4)
ffmpeg -i out_noBGM.mp4 -i bgm.m4a -filter_complex \
  "[1:a]aresample=48000,aloop=loop=1:size=32000000,asetpts=PTS-STARTPTS[bg]; \
   [bg]asplit[b1][b2];[b1]atrim=0:16.138[ba];[b2]atrim=16.138:32.276,asetpts=PTS-STARTPTS[bb]; \
   [ba][bb]acrossfade=d=1.5:c1=tri:c2=tri[bgm]; \
   [bgm]atrim=0:${DUR},asetpts=PTS-STARTPTS,volume=0.85,afade=t=in:st=0:d=0.3,afade=t=out:st=DUR-1.2:d=1.2[bgmf]; \
   [0:a]volume=0.6[fo]; \
   [fo][bgmf]amix=inputs=2:duration=first:dropout_transition=0,aresample=48000[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -ar 48000 -ac 2 final.mp4
# 要点：aloop 循环两遍 → asplit → 接缝处 acrossfade 1.5s 消除循环断点
```

## R5 响度测量与对齐

```bash
# 测量（参照版与新版各测一次）
ffmpeg -nostats -i file.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -14
# 关注：Integrated I (LUFS) 与 True Peak (dBFS)

# 补偿 + 压限（例：+6.1dB 对齐参照）
ffmpeg -i final.mp4 -af "volume=6.1dB,alimiter=limit=0.89:level=false" \
  -c:v copy -c:a aac -ar 48000 -ac 2 -b:a 192k final_limited.mp4
# 验收：I 与参照差 ≤0.5 LU；True Peak ≤ -0.5 dBFS
```

## 速查

- 切点倍速公式：K = 原段时长 ÷ 参考片该幕时长
- atempo 范围 0.5~100，K<0.5 时链式 atempo
- concat 失败先查：各段 分辨率/fps/采样率/声道 是否一致
