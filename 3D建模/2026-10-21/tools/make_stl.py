#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ELDERCHAT 老智系統 — 可列印 STL 產生器
只用 numpy + trimesh（+ manifold3d 做布林），不依賴 CAD 套件。
所有實體以「2D 凸多邊形沿 Y 軸擠出」+ 布林差集建構，逐一驗證水密性。

座標：x = 寬, y = 高（列印 Z）, z = 深
輸出：<out>/01_主機殼.stl ... 05_底座.stl
"""
import json
import math
import os
import sys

import numpy as np
import trimesh


# ---------------------------------------------------------------- 2D 輪廓
def rounded_rect(w, d, r, seg=10):
    """回傳 (N,2) 的圓角矩形輪廓（x, z），中心在原點，逆時針。"""
    r = min(r, w / 2 - 1e-6, d / 2 - 1e-6)
    hw, hd = w / 2 - r, d / 2 - r
    pts = []
    corners = [(hw, hd, 0.0), (-hw, hd, 90.0), (-hw, -hd, 180.0), (hw, -hd, 270.0)]
    for cx, cz, a0 in corners:
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    # 保證逆時針（用有號面積判斷）
    area = 0.0
    n = len(pts)
    for i in range(n):
        x1, z1 = pts[i]
        x2, z2 = pts[(i + 1) % n]
        area += x1 * z2 - x2 * z1
    if area < 0:
        pts.reverse()
    return np.array(pts, dtype=float)


def circle(r, seg=64):
    """(N,2) 圓形輪廓（x, z），逆時針。"""
    pts = [(r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg))
           for i in range(seg)]
    return np.array(pts, dtype=float)


def rect(w, d, cx=0.0, cz=0.0):
    hw, hd = w / 2.0, d / 2.0
    return np.array([[cx - hw, cz - hd], [cx + hw, cz - hd],
                     [cx + hw, cz + hd], [cx - hw, cz + hd]], dtype=float)


# ---------------------------------------------------------------- 擠出
def prism(poly2d, y0, y1, cx=0.0, cz=0.0):
    """凸多邊形沿 +Y 擠出成封閉實體。"""
    p = np.asarray(poly2d, dtype=float) + np.array([cx, cz])
    n = len(p)
    v = np.vstack([np.column_stack([p[:, 0], np.full(n, y0), p[:, 1]]),
                   np.column_stack([p[:, 0], np.full(n, y1), p[:, 1]])])
    f = []
    for i in range(n):
        j = (i + 1) % n
        f.append([i, j, n + j])
        f.append([i, n + j, n + i])
    for i in range(1, n - 1):          # 凸多邊形 → 扇形三角化即可
        f.append([0, i + 1, i])        # 下蓋（法線 -Y）
        f.append([n, n + i, n + i + 1])  # 上蓋（法線 +Y）
    m = trimesh.Trimesh(vertices=v, faces=np.array(f), process=True)
    m.fix_normals()
    return m


def cyl(r, y0, y1, cx=0.0, cz=0.0, seg=64):
    return prism(circle(r, seg), y0, y1, cx=cx, cz=cz)


def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def diff(a, b):
    out = trimesh.boolean.difference([a, b], engine="manifold")
    if isinstance(out, (list, tuple)):
        out = trimesh.util.concatenate(out)
    out.merge_vertices()
    out.fix_normals()
    return out


# ---------------------------------------------------------------- 零件
def main_shell():
    """200×150×95 外殼，壁厚 2.5，R8，底部開口（頂板 2.5）"""
    outer = prism(rounded_rect(200, 150, 8), 0.0, 95.0)
    cavity = prism(rounded_rect(195, 145, 5.5), -1.0, 92.5)
    return diff(outer, cavity)


def front_frame():
    """165×105×6 前框，中間開 154×86 視窗，外角 R5"""
    outer = prism(rounded_rect(165, 105, 5), 0.0, 6.0)
    win = prism(rounded_rect(154, 86, 2.5), -1.0, 7.0)
    return diff(outer, win)


def button_seat():
    """Ø66×20 按鈕座，內孔 Ø60.4（60mm 按鈕用），底部留 2mm 法蘭環"""
    outer = cyl(33.0, 0.0, 20.0)
    bore = cyl(30.2, 2.0, 21.0)   # 從 y=2 起鑽 → 底部保留 2mm 擋環
    return diff(outer, bore)


def mic_seat():
    """22×17×6 麥克風座，內腔 20×15 深 4.5（底板 1.5），頂部開放"""
    outer = box(-11, 11, 0, 6, -8.5, 8.5)
    cav = box(-10, 10, 1.5, 7, -7.5, 7.5)
    seat = diff(outer, cav)
    # 音孔 Ø1.2（MEMS 進音孔）
    hole = cyl(0.6, -1.0, 2.5, cx=0.0, cz=0.0, seg=24)
    return diff(seat, hole)


def base_plate():
    """200×150×8 底座，底面 4 個 Ø12.3×3 防滑墊凹槽（位於 ±80,±52）"""
    plate = prism(rounded_rect(200, 150, 8), 0.0, 8.0)
    for sx in (-1, 1):
        for sz in (-1, 1):
            pocket = cyl(6.15, -1.0, 3.0, cx=80.0 * sx, cz=52.0 * sz, seg=48)
            plate = diff(plate, pocket)
    return plate


PARTS = [
    ("01_主機殼.stl", main_shell, (200.0, 95.0, 150.0), "200×150×95 壁厚2.5 R8 底部開口"),
    ("02_前框.stl", front_frame, (165.0, 6.0, 105.0), "165×105×6 視窗154×86"),
    ("03_緊急按鈕座.stl", button_seat, (66.0, 20.0, 66.0), "Ø66×20 內孔Ø60.4"),
    ("04_麥克風座.stl", mic_seat, (22.0, 6.0, 17.0), "22×17×6 內腔20×15"),
    ("05_底座.stl", base_plate, (200.0, 8.0, 150.0), "200×150×8 4×Ø12.3凹槽"),
]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    report = []
    for name, fn, spec, note in PARTS:
        m = fn()
        m.merge_vertices()
        # 體積為負 → 反向（保險）
        if m.volume < 0:
            m.invert()
        ext = m.bounding_box.extents  # x, y, z
        path = os.path.join(out, name)
        m.export(path)
        # 讀回驗證
        rb = trimesh.load(path, process=True)
        rb_ext = rb.bounding_box.extents
        rec = {
            "file": name,
            "bytes": os.path.getsize(path),
            "verts": int(len(rb.vertices)),
            "faces": int(len(rb.faces)),
            "watertight": bool(rb.is_watertight),
            "winding": bool(rb.is_winding_consistent),
            "volume_mm3": round(float(rb.volume), 1),
            "bbox_mm": [round(float(v), 2) for v in rb_ext],
            "spec_mm": [round(float(v), 2) for v in spec],
            "bbox_err_mm": [round(abs(float(a) - float(b)), 3) for a, b in zip(rb_ext, spec)],
            "euler": int(rb.euler_number),
            "note": note,
        }
        report.append(rec)
        print(json.dumps(rec, ensure_ascii=False))
    with open(os.path.join(out, "_stl_report.json"), "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
