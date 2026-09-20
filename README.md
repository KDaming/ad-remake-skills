# ad-remake-skills

WorkBuddy「爆款广告片复刻流水线」SKILL 矩阵 —— 从一条参考广告视频出发，端到端复刻改编为自有产品的多平台成片与封面。

沉淀自「宠儿香益生菌·红黄绿灯三幕」项目（2026-09）的完整实战踩坑链。

## 矩阵结构

```
ad-remake-hermes（总控）
 ├─ S0 逆向拆解 ──► sph-video-reverse-breakdown（需另行安装，未含在本仓库）
 ├─ S1 创意改编 ──► 总控直接执行（改编公式：留骨架 / 换血肉）
 ├─ S2 关键帧锻造 ──► ad-keyframe-forge
 ├─ S3 批量 I2VA ──► h3-prompt-writing + keyframes-batch-video（需另行安装，未含在本仓库）
 ├─ S4 分层合成 ──► subject-back-compositor（含 composite_countdown_v2.py）
 ├─ S5 节奏混音 ──► rhythm-mix-delivery
 └─ S6 分发封面 ──► cover-layout-studio
```

## 各 skill 一览

| Skill | 职责 | 核心沉淀 |
|---|---|---|
| `ad-remake-hermes` | 总控调度 | 阶段输入/输出契约、3 个用户确认门（S1 结构映射 / S2 全部定稿 / S5 成片）、断点续做、中间产物强制保留 |
| `ad-keyframe-forge` | 角色板 + 关键帧 | 六段锚定提示词、双参考图（ImageGen input_fidelity high）、倍数夸张法、巨幕投影两约束、PIL 局部克隆去水印 |
| `subject-back-compositor` | 文字/图形压主体背后 | 五级踩坑链：u2net → fill_holes → u2net/isnet 双模型并集 → 时序平滑 W=12（±12 帧逐像素 max + .npy 蒙版缓存），附可直接运行的合成脚本 |
| `rhythm-mix-delivery` | 节奏对齐 + 混音交付 | trim+setpts 变速对齐参考片切点、acrossfade BGM 无缝循环、ebur128 响度对齐 + alimiter 防削波 |
| `cover-layout-studio` | 平台封面 + 字卡 | 抖音 3:4 杂志卡 / 小红书 4:3 全幅出血两版式、文案两级制、米白描边规则、圈选迭代协议 |

## 安装

将各 skill 文件夹复制到 WorkBuddy 用户级 skill 目录：

```bash
cp -r ad-* subject-back-compositor rhythm-mix-delivery cover-layout-studio ~/.workbuddy/skills/
```

在 WorkBuddy 对话中说「复刻这条广告 + 视频链接」即可触发总控跑全流程。

## 依赖

- Python venv：`rembg`（u2net + isnet-general-use 双模型，onnx 模型走 hf-mirror 下载）、`Pillow`、`numpy`
- ffmpeg（drawtext / overlay / concat / atempo / acrossfade / ebur128 / alimiter）
- 中文字体：`C:/Windows/Fonts/NotoSansSC-VF.ttf`（思源黑体 VF，`set_variation_by_axes([700])` 加粗）
- MiniMax H3 视频生成走 TokenHub 通道（S3 阶段，凭证自备）
