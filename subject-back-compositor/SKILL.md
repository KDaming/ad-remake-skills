---
name: subject-back-compositor
description: |
  "文字/图形压在主体背后"视频分层合成器。Use when overlaying large text, countdown digits,
  logos or graphics BEHIND people/animals in a video (文字压主体背后/数字在人物后面/倒计时叠到墙上)，
  or when fixing 抠像透字/白毛透字/数字闪烁 problems in such composites.
  核心方法：rembg 逐帧抠像（u2net+isnet 双模型并集）+ fill_holes 孔洞填充 +
  时序蒙版平滑（±12帧逐像素 max + .npy 缓存）→ 数字只显示在非主体墙面区域。
  内含可直接运行的 scripts/composite_countdown_v2.py。由 ad-remake-hermes 在 S4 阶段调度。
agent_created: true
---

# 文字压主体背后 · 分层合成

## 适用场景

视频画面中有大幅文字/数字/图形需要"贴在背景墙上、被人物动物遮挡"（如倒计时 3-2-1、巨幕标语）。
**不要**用 ffmpeg drawtext 顶层叠加——会压发丝、穿帮。

## 标准流程

1. **抽帧**：`ffmpeg -i clip.mp4 frames/%03d.png`（保留原帧率）
2. **准备叠加层**：与视频同尺寸的透明底 PNG（如 `_digit_1.png`），文字/图形已定位
3. **运行合成**（venv python，需 rembg + u2net/isnet 模型，见下）：
   ```bash
   python scripts/composite_countdown_v2.py <frames_dir> <digit_dir> <spec> <out_dir> [model] [W]
   # spec 例: "3:1-54,2:55-107"（数字:起帧-止帧，可多段）；model 默认 union；W 默认 4，闪烁场景用 12
   ```
4. **重编码**：帧序列 → mp4（crf 16、原帧率），音频从原 clip copy
5. **QC**：抽帧检查透字/闪烁（见 `references/01-troubleshooting.md` 的量化检测法）

## 方法管线（脚本内部，勿跳步）

```
rembg 双模型（u2net + isnet-general-use）逐帧推理
  → np.maximum 蒙版并集（两模型误判区域互补）
  → 时序平滑：±W 帧蒙版逐像素 max（W=12 根治闪烁；.npy 缓存可复用）
  → MaxFilter(9) 膨胀 → fill_holes 孔洞填充 → GaussianBlur(2) 羽化
  → 叠加层 alpha × (1 - 主体蒙版) = 只显示在墙面
```

**核心原则：宁遮勿透**——文字被毛发多遮一点不违和，透过白毛露色必违和。

## 环境依赖

- venv：`C:/Users/ZJM/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（已装 rembg）
- onnx 模型走 hf-mirror 下载放 `~/.rembg/models/<model>/`（GitHub 直连会 0 字节）
- rembg 安装坑：`pip install --no-deps rembg pooch pymatting`，pymatting 写桩模块（禁用 alpha matting）
- union 模式速度约为单模型 2 倍（107 帧 ≈ 20 分钟），**蒙版 .npy 缓存**在 out_dir/_mask_cache/，调参重跑零重算

## References

- `references/01-troubleshooting.md` — 透字/闪烁五级踩坑链 + 量化 QC 法 + 帧区间检测技巧
