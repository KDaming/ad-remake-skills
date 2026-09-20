---
name: rhythm-mix-delivery
description: |
  成片节奏对齐与音频混音交付。Use when assembling ad clips into a final video with
  reference-timed cuts (节奏对齐参考片/切点对齐/视频变速), looping BGM with crossfade
  (BGM循环/背景音乐拼接), mixing BGM with original foley audio, or matching loudness
  of a previous deliverable (响度对齐/LUFS/防削波). 覆盖：trim+setpts+fps 变速公式、
  concat 多段拼接、acrossfade BGM 无缝循环、ebur128 响度实测对齐、alimiter 防削波、
  片尾卡静帧段。由 ad-remake-hermes 在 S5 阶段调度。
agent_created: true
---

# 节奏对齐与混音交付

## 适用场景

多段 clip → 按参考片切点变速对齐 → 拼接 → BGM 混音 → 响度达标的最终成片。

## 标准流程

1. **变速对齐切点**：逐段按"参考片切点秒数 ÷ 原片该段秒数"算倍速，ffmpeg 变速（公式见 `references/01-ffmpeg-recipes.md` R1）。视频 `setpts` + 音频 `atempo` 成对使用。
2. **片尾卡**：静态 PNG 循环 2.5s + anullsrc 静音轨（参数与正片一致才能 concat）。
3. **拼接**：concat filter 一次性拼全部段（统一 分辨率/帧率/48kHz 立体声后拼接）。
4. **BGM 混音**：参考片提取的 BGM → aloop 循环 → acrossfade 1.5s 无缝接缝 → atrim 到片长 → volume 0.85 + 淡入 0.3s/淡出 1.2s；原片 foley volume 0.6；amix 合并。
5. **响度对齐**（交付红线）：ebur128 实测成片与**上一版/参照版**的 Integrated LUFS；不一致则用 volume 补偿，补偿后**必须** `alimiter=limit=0.89:level=false` 防削波（真峰值 ≤ -0.5 dBFS）。

## 交付红线

- ❌ 禁止凭感觉调音量——必须 ebur128 实测，I 值对齐参照（本项目基准：-10.5 LUFS）
- ❌ 禁止 volume 提升后不压限——+6dB 后真峰值会超 0 dBFS 削波
- ❌ 禁止丢弃"无 BGM 版"中间产物——混音返工要从它重来
- ✅ 每段变速后核对 nb_frames 与预期（切点秒数 × 帧率）

## References

- `references/01-ffmpeg-recipes.md` — 全部命令配方（变速/片尾卡/concat/BGM循环/混音/响度测量）
