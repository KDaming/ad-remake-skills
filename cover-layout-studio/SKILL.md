---
name: cover-layout-studio
description: |
  视频封面与章节字卡版式工坊（PIL 程序化制图）。Use when generating platform covers
  (抖音 3:4 竖版 / 小红书 4:3 横版封面) or chapter caption cards (字卡/片尾卡) from
  keyframes or video stills: 杂志卡版式（米白底+白边圆角照片卡+投影）、全幅出血版式、
  两级文案制（主标题+副标题）、米白描边压图文字、品牌色分色字、微信搜索框 CTA 绘制。
  触发词：封面、3:4、4:3、字卡、片尾卡、搜索框。由 ad-remake-hermes 在 S6 阶段调度。
agent_created: true
---

# 封面与字卡版式工坊

## 职责

关键帧/成片帧 + 文案 → 各平台封面 PNG；章节字卡与片尾卡（视频内用）。
版式写成 PIL 脚本存项目目录（如 `make_covers.py`），用户截图圈选反馈 → 改参数重跑。

## 平台规格与版式选型

| 平台 | 比例/尺寸 | 推荐版式 |
|---|---|---|
| 抖音 | 3:4，1080×1440 | **杂志卡式**：米白底 + 顶部两级标题 + 白边圆角照片卡（带投影）居中偏上 |
| 小红书 | 4:3，1440×1080 | **全幅出血式**：关键帧铺满 + 左上大标题（描边）+ 左下品牌条（可选） |

版式细节与代码模板见 `references/01-layout-patterns.md`。

## 文案规则（用户偏好沉淀）

- **两级制**：主标题（大）+ 副标题（小），不要第三层元素——用户会圈选删掉
- 压在图片上的深色文字必须加**米白 stroke（5-6px）**，否则压在深色区域（如蓝色海报）上糊掉
- 品牌色分色字（如红/黄/绿）好看但层级最低，用户说删就删，不恋战
- 字体：`C:/Windows/Fonts/NotoSansSC-VF.ttf`，`set_variation_by_axes([700])` 加粗

## 迭代协议

1. 出图 → 同时生成 50% 预览 jpg 供快速目检
2. 用户截图红框圈选 → 只改圈选元素，其他不动
3. 定稿命名：`抖音封面_3x4.png` / `小红书封面_4x3.png` 存项目根目录
4. 预览 jpg 等过程产物交付前清理

## References

- `references/01-layout-patterns.md` — 两种版式的 PIL 实现要点 + 微信搜索框 CTA 画法
