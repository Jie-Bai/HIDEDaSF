# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 13:30:07 2025

@author: 10913
"""

import pandas as pd
import os

# === 1. 设置路径 ===
input_path = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\original_data\all-CloudPreprocessing.csv"
output_path = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun0_Pot_Removal\all_no_pot.csv"

# === 2. 读取 CSV 数据 ===
df = pd.read_csv(input_path)

# === 3. 去除花盆区域点云 ===
# 花盆空间范围: -20<=X<=10, -20<=Y<=20, 480<=Z<=510
mask_pot = (df["X"] >= -20) & (df["X"] <= 12) & \
           (df["Y"] >= -20) & (df["Y"] <= 20) & \
           (df["Z"] >= 480) & (df["Z"] <= 530)

# 保留不在花盆范围内的点云
df_filtered = df[~mask_pot].copy()

# === 4. 保存结果 ===
df_filtered.to_csv(output_path, index=False)

print(f"处理完成！已去除花盆区域点云。")
print(f"原始点数: {len(df)}, 去除后剩余点数: {len(df_filtered)}")
print(f"已保存至: {output_path}")
