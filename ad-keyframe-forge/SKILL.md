---
name: ad-keyframe-forge
description: |
  广告片角色板与关键帧锻造（ImageGen 静帧生产）。Use when producing character sheets
  (角色板) or shot keyframes (关键帧) for an ad remake: 双参考图合成（角色板+产品图/工服图）、
  巨幕产品投影、动物/物体极致夸张比例、视线方向控制、自然肤质/裸妆/暖光氛围修正、
  右下角 AI 水印去除（PIL 局部克隆）、防穿模构图。触发词：角色板、关键帧、定稿、
  生成5个镜头、产品投影上墙、狗要更大、去水印。由 ad-remake-hermes 在 S2 阶段调度。
agent_created: true
---

# 广告关键帧锻造

## 职责

把 Hermes S1 的角色设定与分幕表，变成用户逐帧确认的 `V<n>_<名>_定稿.png`。
流程：角色板（1 张，先确认）→ 逐镜关键帧（N 张，逐张确认）→ 定稿命名归档。

## 生产流程

1. **角色板先行**：工服/服装参考图 + 形象描述 → 生成 1 张角色板；用户确认后才做关键帧，后续所有关键帧以它为参考图锁定形象。
2. **逐镜生成**：每镜 = 双参考图（角色板 + 当幕产品 PNG/道具图）+ 镜头提示词 → 出图 → 用户反馈 → 迭代（`_v1/_v2…`）→ 批准后改名 `_定稿`。
3. **提示词结构**：参照 `references/01-prompt-formulas.md` 的锚定写法。
4. **去水印**：出图右下角 AI 水印用 `references/02-watermark-and-fixes.md` 的 PIL 局部克隆法，**禁止**生成式 erase（会毁掉包装/文字细节）。

## 核心经验（迭代踩坑沉淀）

- **比例夸张要说倍数**："大一点的狗"无效；写"马一样大、20 倍体型、女孩只到狗膝盖"才到位。
- **巨幕产品投影**：写 "giant product poster projection on the wall, flat, no light spill, does not occlude foreground subjects"——无光影、不挡前景两个约束缺一不可。
- **视线控制**：显式写 "looking at the dog, not at the camera"。
- **真人感**：初版塑料感重时追加"自然皮肤肌理、裸妆、波浪蓬松长发、柔和暖光、温馨氛围"。
- **防穿模**：构图提示词预留"主体居中偏左、右下角留大片干净地面"，给去水印克隆留出干净采样源。
- **静帧即首帧**：关键帧就是 I2VA 首帧，画面里不想动的东西（投影、灯状态）必须在静帧里画对——视频模型修不动。

## 交付契约

- 尺寸与后续视频一致（如 1536×1024 / 3:2），PNG。
- 命名：`keyframes/V<n>_<镜头名>_定稿.png`；中间版本保留 `_v1~_vN` 至项目交付。
- 全部镜头定稿 = S2 完成信号，报 Hermes 进 S3。

## References

- `references/01-prompt-formulas.md` — 角色板/关键帧提示词公式与实例
- `references/02-watermark-and-fixes.md` — 去水印与常见缺陷修复 playbook
