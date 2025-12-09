# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 16:39:31 2025

@author: 10913
"""

import pandas as pd
import numpy as np
import os
from scipy.spatial import cKDTree

# === 1. 路径设置 ===
base_dir = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe"
input_all = os.path.join(base_dir, r"Fun0_Pot_Removal\all_no_pot.csv")
input_edge = os.path.join(base_dir, r"Fun3_RefinedEdgeDetection\SwellRefined_edge_points.csv")
output_dir = os.path.join(base_dir, r"Fun4_SphericalSpaceFiltering")
os.makedirs(output_dir, exist_ok=True)

# === 2. 读取数据 ===
all_df = pd.read_csv(input_all)
edge_df = pd.read_csv(input_edge)

# === 3. 波段列 ===
bands = [
    '409','425','442','458','474','491','507','523','540','556',
    '572','589','605','621','637','653','670','686','703','719',
    '735','751','768','784','800','816','833','840','865','882',
    '898','914'
]

# === 4. 找出非边缘点 ===
# 使用坐标(X, Y, Z)匹配（假定完全相同精度）
edge_coords = set(tuple(x) for x in edge_df[['X', 'Y', 'Z']].to_numpy())
mask_non_edge = ~all_df[['X', 'Y', 'Z']].apply(tuple, axis=1).isin(edge_coords)
#找出非边缘点
no_edge_df = all_df[mask_non_edge].copy()

# === 5. 构建 KDTree (非边缘点坐标) ===
tree = cKDTree(no_edge_df[['X', 'Y', 'Z']].values)
radius = 20  # 10 cm

# === 6. 对每个边缘点执行球空间均值校正 ===
corrected_values = []
for idx, edge_point in edge_df.iterrows():
    center = edge_point[['X', 'Y', 'Z']].values
    neighbors_idx = tree.query_ball_point(center, r=radius)

    if len(neighbors_idx) > 0:
        neighbor_vals = no_edge_df.iloc[neighbors_idx][bands]
        #print("neighbor_vals",neighbor_vals)
        mean_vals = neighbor_vals.mean(axis=0).values
    else:
        # 若邻域内没有非边缘点，则保留原值
        mean_vals = edge_point[bands].values

    corrected_values.append(mean_vals)

# === 7. 构建校正后的边缘点数据表 ===
edge_corrected_df = edge_df.copy()
edge_corrected_df.loc[:, bands] = np.array(corrected_values)

# === 8. 输出结果文件 ===
no_edge_path = os.path.join(output_dir, "allNoRefinedEdgeNoPot.csv")
edge_corrected_path = os.path.join(output_dir, "EdgeCorrectedNoLeafNoPot.csv")
all_corrected_path = os.path.join(output_dir, "EdgeCorrectedHasLeafNoPot.csv")

# 非边缘点
no_edge_df.to_csv(no_edge_path, index=False)
# 校正后的边缘点
edge_corrected_df.to_csv(edge_corrected_path, index=False)
# 合并
all_corrected_df = pd.concat([no_edge_df, edge_corrected_df], ignore_index=True)
all_corrected_df.to_csv(all_corrected_path, index=False)

print("\n✅ 球空间边缘效应校正完成！")
print(f"非边缘点输出: {no_edge_path}")
print(f"校正后边缘点输出: {edge_corrected_path}")
print(f"合并输出: {all_corrected_path}")
print(f"共校正边缘点数: {len(edge_df)}")
