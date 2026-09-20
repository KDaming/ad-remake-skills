#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
倒计时数字"压在主体背后"合成器 v2 —— 时序防抖版
相比 v1 的改进：
1) 支持一次运行多个 数字:帧区间（如 "3:1-54,2:55-107"）
2) 两遍处理：先为扩展区间全部帧计算 union 蒙版并缓存，
   再对每帧取 前后 W 帧蒙版的逐像素最大值（temporal max），
   消除 rembg 逐帧抖动导致的"狗白毛处数字忽隐忽现"闪烁。
用法:
  python composite_countdown_v2.py <frames_dir> <digit_dir> <spec> <out_dir> [model] [W]
  spec 例: "3:1-54,2:55-107"  (数字文件名 _digit_<n>.png)
  model: union(默认) | u2net | isnet-general-use
  W: 时序窗口半径，默认 4 (±4帧 ≈ ±0.17s @24fps)
"""
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from rembg import new_session, remove

W_IMG, H_IMG = 2176, 1440


def fill_holes(mask_l):
    """填充蒙版内部孔洞（如狗的白色脸部被误判为背景）。"""
    inv = Image.eval(mask_l, lambda v: 255 - v)
    for seed in [(0, 0), (W_IMG - 1, 0), (0, H_IMG - 1), (W_IMG - 1, H_IMG - 1)]:
        if inv.getpixel(seed) == 255:
            ImageDraw.floodfill(inv, seed, 128)
    arr = np.array(inv)
    holes = (arr == 255).astype(np.uint8) * 255
    return Image.fromarray(np.maximum(np.array(mask_l), holes), "L")


def parse_spec(spec):
    out = []
    for part in spec.split(","):
        m = re.match(r"(\w+):(\d+)-(\d+)", part.strip())
        out.append((m.group(1), int(m.group(2)), int(m.group(3))))
    return out


def main():
    frames_dir, digit_dir, spec_s, out_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    model = sys.argv[5] if len(sys.argv) > 5 else "union"
    win = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    os.makedirs(out_dir, exist_ok=True)

    ranges = parse_spec(spec_s)
    digits = {}
    for name, _, _ in ranges:
        if name not in digits:
            d = Image.open(os.path.join(digit_dir, f"_digit_{name}.png")).convert("RGBA")
            digits[name] = (d, np.array(d.split()[3]))

    if model == "union":
        sessions = [new_session("u2net"), new_session("isnet-general-use")]
    else:
        sessions = [new_session(model)]

    frames = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
    total = len(frames)

    # ---- 第一遍：为所有需要的帧（区间 ±win）计算并缓存 union 蒙版（.npy 落盘可复用）----
    need = set()
    for _, s, e in ranges:
        for i in range(max(1, s - win), min(total, e + win) + 1):
            need.add(i)
    cache_dir = os.path.join(out_dir, "_mask_cache")
    os.makedirs(cache_dir, exist_ok=True)
    raw_masks = {}
    for i in sorted(need):
        cp = os.path.join(cache_dir, f"{i:03d}.npy")
        if os.path.exists(cp):
            raw_masks[i] = np.load(cp)
            continue
        frame = Image.open(os.path.join(frames_dir, frames[i - 1])).convert("RGBA")
        masks = [np.array(remove(frame, session=s, only_mask=True)) for s in sessions]
        raw_masks[i] = np.maximum.reduce(masks)
        np.save(cp, raw_masks[i])
        if i % 10 == 0:
            print(f"mask [{i}/{max(need)}]", flush=True)

    # ---- 第二遍：时序最大 + 形态学 + 合成 ----
    digit_of = {}
    for name, s, e in ranges:
        for i in range(s, e + 1):
            digit_of[i] = name

    for i, name in enumerate(frames, start=1):
        src = os.path.join(frames_dir, name)
        dst = os.path.join(out_dir, name)
        if i not in digit_of:
            Image.open(src).convert("RGB").save(dst)
            continue
        frame = Image.open(src).convert("RGBA")
        # 时序窗口内逐像素取最大：任一邻近帧认定为主体的区域，本帧都视为主体
        lo, hi = max(1, i - win), min(total, i + win)
        stack = [raw_masks[j] for j in range(lo, hi + 1)]
        fg = Image.fromarray(np.maximum.reduce(stack), "L")
        fg = fg.filter(ImageFilter.MaxFilter(9))
        fg = fill_holes(fg)
        fg = fg.filter(ImageFilter.GaussianBlur(2))
        dimg, dalpha = digits[digit_of[i]]
        vis = ImageChops.multiply(Image.fromarray(dalpha, "L"), ImageChops.invert(fg))
        layer = Image.new("RGBA", (W_IMG, H_IMG), (0, 0, 0, 0))
        layer.paste(dimg, (0, 0), vis)
        out = frame.copy()
        out.alpha_composite(layer)
        out.convert("RGB").save(dst)
        if i % 10 == 0 or i == 1:
            print(f"composite [{i}/{total}]", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
