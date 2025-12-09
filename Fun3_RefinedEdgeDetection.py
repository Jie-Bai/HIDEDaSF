# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 18:03:05 2025

@author: 10913
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import convolve
from scipy.ndimage import binary_dilation

resolution = 0.45  # 0.45 cm
edgeThresholdNumber = 4
windowLength = 4
# ********************************** 1. 路径设置 **********************************
input_path = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun2_RoughEdgeDetection\all_edge_points.csv"
noPotPath = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun0_Pot_Removal\all_no_pot.csv"
output_dir = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun3_RefinedEdgeDetection"
os.makedirs(output_dir, exist_ok=True)

# ********************************** 2. 读取数据 **********************************
df = pd.read_csv(input_path)
df2 = pd.read_csv(noPotPath) 
# ********************************** 3. 参数设置 **********************************
resolution = resolution
bands = [
    '409','425','442','458','474','491','507','523','540','556',
    '572','589','605','621','637','653','670','686','703','719',
    '735','751','768','784','800','816','833','840','865','882',
    '898','914'
]

# ********************************** 4. 构建投影网格 **********************************
x_min, x_max = df['X'].min(), df['X'].max()
y_min, y_max = df['Y'].min(), df['Y'].max()
x_bins = int(np.ceil((x_max - x_min) / resolution))
y_bins = int(np.ceil((y_max - y_min) / resolution))

print(f"投影网格大小: {x_bins} × {y_bins}")

# ********************************** 5. 建立投影图像与映射表 **********************************
projection = np.zeros((y_bins, x_bins), dtype=np.uint8)
cell_to_points = {}

for idx, row in df.iterrows():
    x_idx = int((row['X'] - x_min) / resolution)
    y_idx = int((row['Y'] - y_min) / resolution)
    if 0 <= x_idx < x_bins and 0 <= y_idx < y_bins:
        projection[y_idx, x_idx] = 1
        cell_to_points.setdefault((y_idx, x_idx), []).append(idx)

# ********************************** 6. 保存粗边缘投影图 **********************************
plt.figure(figsize=(10, 8))
plt.imshow(projection, cmap='gray', origin='lower')
plt.title("rough projection (1=on, 0=none)")
plt.savefig(os.path.join(output_dir, "rough_edge_projection.png"), dpi=300, bbox_inches='tight')
plt.close()

# ********************************** 7. 窗口卷积检测 **********************************
kernel = np.ones((windowLength, windowLength), dtype=int)
neighbor_sum = convolve(projection, kernel, mode='constant', cval=0)

# 符合条件（邻域内像元≥一定数量）保留
refined_mask = (neighbor_sum >= edgeThresholdNumber) & (projection == 1)

# ********************************** 形态学膨胀（可调） **********************************
dilate_iters = 1  # 膨胀迭代次数，>1 会更粗

# 选一：4-邻域（十字形核，扩张更克制）
'''structure_4 = np.array([[0,1,0],
                        [1,1,1],
                        [0,1,0]], dtype=bool)
'''
# 选二：8-邻域（3x3 全1核，扩张更明显）
structure_8 = np.ones((3,3), dtype=bool)

# 使用4-邻域（想更粗就换成 structure_8）
refined_mask = binary_dilation(refined_mask, structure=structure_8, iterations=dilate_iters)


# refined_mask = binary_dilation(...)

# ********************************** A. 用同一网格把去盆点云映射进来，找出膨胀后为1的像元内的所有点 **********************************
swell_indices = []
for idx, row in df2.iterrows():
    x_idx = int((row['X'] - x_min) / resolution)   # 注意：这里的 resolution 仍是 0.45 cm
    y_idx = int((row['Y'] - y_min) / resolution)
    if 0 <= x_idx < x_bins and 0 <= y_idx < y_bins:
        if refined_mask[y_idx, x_idx]:
            swell_indices.append(idx)

# ********************************** B. 导出“膨胀精边缘”的真实点（来自去盆点云）**********************************
swell_refined_df = df2.loc[swell_indices, ['X','Y','Z','distance'] + bands]
swell_refined_csv = os.path.join(output_dir, "SwellRefined_edge_points.csv")
swell_refined_df.to_csv(swell_refined_csv, index=False)
print(f"✅ 膨胀后精边缘点导出：{swell_refined_csv}（共 {len(swell_refined_df)} 点）")

# ********************************** C. 以 0.45 cm 分辨率输出该集合的投影图（沿用同一网格范围）**********************************
proj_swell = np.zeros((y_bins, x_bins), dtype=np.uint8)
for idx, row in swell_refined_df.iterrows():
    x_idx = int((row['X'] - x_min) / resolution)
    y_idx = int((row['Y'] - y_min) / resolution)
    if 0 <= x_idx < x_bins and 0 <= y_idx < y_bins:
        proj_swell[y_idx, x_idx] = 1

plt.figure(figsize=(10, 8))
plt.imshow(proj_swell, cmap='gray', origin='lower')
plt.title("SwellRefined edge projection 0.45 cm (1=on, 0=none)")
plt.savefig(os.path.join(output_dir, "SwellRefined_edge_projection_045cm.png"), dpi=300, bbox_inches='tight')
plt.close()


print(f"\n✅ 精边缘检测完成！")
print(f"粗边缘图像: {os.path.join(output_dir, 'rough_edge_projection.png')}")
print(f"精边缘图像: {os.path.join(output_dir, 'refined_edge_projection.png')}")



base_dir = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe"
all_path   = os.path.join(base_dir, r"Fun0_Pot_Removal\all_no_pot.csv")
edge_path  = os.path.join(base_dir, r"Fun3_RefinedEdgeDetection\SwellRefined_edge_points.csv")
out_path   = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun3_RefinedEdgeDetection\allNoRefinedEdgeNoPot.csv"

# 读取
df_all  = pd.read_csv(all_path)
df_edge = pd.read_csv(edge_path)

# 用 X,Y,Z 精确匹配，左连接打标签
merged = df_all.merge(
    df_edge[['X','Y','Z']],  # 只需坐标列
    on=['X','Y','Z'],
    how='left',
    indicator=True
)

# 保留在 all_no_pot 中但不在 refined_edge_points 中的点
df_out = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])

# 保存
df_out.to_csv(out_path, index=False)

print("✅ 已生成非边缘去盆点云：", out_path)
print(f"原始去盆点数：{len(df_all)}")
print(f"精边缘点数：{len(df_edge)}")
print(f"剔除后剩余点数：{len(df_out)}")
