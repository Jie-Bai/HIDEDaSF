# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 17:46:48 2025

@author: 10913
"""

import pandas as pd
import numpy as np
import os

# === 1. 文件路径设置 ===
input_path = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun0_Pot_Removal\all_no_pot.csv"
output_dir = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun2_RoughEdgeDetection"

os.makedirs(output_dir, exist_ok=True)

# === 2. 读取数据 ===
df = pd.read_csv(input_path)

# === 3. 波段列表 ===
bands = [
    '409','425','442','458','474','491','507','523','540','556',
    '572','589','605','621','637','653','670','686','703','719',
    '735','751','768','784','800','816','833','840','865','882',
    '898','914'
]

# === 4. 存储阈值与边缘点索引 ===
thresholds = {}
edge_indices_union = set()

# === 5. 遍历波段 ===
for band in bands:
    data = df[band] * 1000  # 强度放大1000倍
    valid_data = data[data > 0]  # 仅保留正强度值

    # === 计算直方图 ===
    counts, bin_edges = np.histogram(valid_data, bins=100)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # === 找到第二高峰 ===
    sorted_indices = np.argsort(counts)[::-1]
    if len(sorted_indices) > 1:
        second_peak_idx = sorted_indices[1]
    else:
        second_peak_idx = sorted_indices[0]

    second_peak_value = bin_centers[second_peak_idx]
    threshold = second_peak_value * 0.5
    thresholds[band] = threshold

    # === 计算边缘点 ===
    edge_mask = (data < threshold) & (data >0)
    edge_points = df.loc[edge_mask, ["X", "Y", "Z", "distance"]].copy()
    edge_points[f"wavelength_{band}_nm"] = df.loc[edge_mask, band]

    # === 保存单波段边缘点 ===
    save_path = os.path.join(output_dir, f"edge_points_{band}nm.csv")
    edge_points.to_csv(save_path, index=False)

    # === 累积边缘点索引 ===
    edge_indices_union.update(edge_points.index.tolist())

    print(f"波段 {band} nm 处理完成，阈值 = {threshold:.2f}，边缘点数 = {len(edge_points)}")

# === 6. 汇总所有波段的边缘点 ===
all_edge_points = df.loc[sorted(list(edge_indices_union))].copy()
all_edge_path = os.path.join(output_dir, "all_edge_points.csv")
all_edge_points.to_csv(all_edge_path, index=False)

print("\n✅ 已生成所有波段的边缘点云数据：")
print(f"  单波段文件保存路径：{output_dir}")
print(f"  汇总边缘点文件：{all_edge_path}")

# === 7. 保存阈值信息 ===
threshold_df = pd.DataFrame.from_dict(thresholds, orient='index', columns=['50%_of_second_peak_intensity(x1000)'])
threshold_path = os.path.join(output_dir, "band_thresholds_second_peak50.csv")
threshold_df.to_csv(threshold_path)

print(f"各波段阈值已保存至: {threshold_path}")
