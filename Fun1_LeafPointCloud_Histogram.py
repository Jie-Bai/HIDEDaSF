# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 17:54:54 2025

@author: 10913
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ********************************** 1. 设置路径 **********************************
input_path = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun0_Pot_Removal\all_no_pot.csv"
output_dir = r"F:\L论文\3高光谱激光雷达边缘效应\Hidedarfe\Fun1_LeafPointCloud_Histogram"

# ********************************** 2. 确保输出目录存在 **********************************
os.makedirs(output_dir, exist_ok=True)

# ********************************** 3. 读取数据 **********************************
df = pd.read_csv(input_path)

# ********************************** 4. 波段列表 **********************************
bands = [
    '409','425','442','458','474','491','507','523','540','556',
    '572','589','605','621','637','653','670','686','703','719',
    '735','751','768','784','800','816','833','840','865','882',
    '898','914'
]

# ********************************** 5. 创建绘图窗口 **********************************
fig, axes = plt.subplots(8, 4, figsize=(20, 28))
axes = axes.flatten()

thresholds = {}

for i, band in enumerate(bands):
    ax = axes[i]
    data = df[band] * 1000  # 强度放大1000倍
    data = data[data > 0]   # 仅保留正强度值

    # ********************************** 计算直方图 **********************************
    counts, bin_edges = np.histogram(data, bins=100)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # ********************************** 找到频数第二高的 bin **********************************
    sorted_indices = np.argsort(counts)[::-1]  # 从高到低排序
    if len(sorted_indices) > 1:
        second_peak_idx = sorted_indices[1]
    else:
        second_peak_idx = sorted_indices[0]  # 如果只有一个非零bin，取它

    second_peak_value = bin_centers[second_peak_idx]

    # ********************************** 阈值 = 第二高峰强度的一半 **********************************
    threshold = second_peak_value * 0.5
    thresholds[band] = threshold

    # ********************************** 绘制直方图 **********************************
    ax.hist(data, bins=100, color='steelblue', alpha=0.7)
    ax.set_title(f"{band} nm", fontsize=10)
    ax.set_xlabel("反射强度 ×1000")
    ax.set_ylabel("点数")
    ax.grid(alpha=0.3)

    # ********************************** 绘制红线与文字 **********************************
    ax.axvline(threshold, color='red', linestyle='--', linewidth=1.5)
    ax.text(threshold, ax.get_ylim()[1]*0.85,
            f"{threshold:.3f}", color='red', fontsize=8,
            rotation=0, va='bottom', ha='center', backgroundcolor='white')

plt.suptitle("409–914 nm 各波段点云强度直方图（红线=第二高频强度的一半）", fontsize=16, y=0.92)
plt.tight_layout(rect=[0, 0, 1, 0.96])

# ********************************** 6. 保存综合直方图 **********************************
combined_path = os.path.join(output_dir, "all_band_histograms_second_peak50.png")
plt.savefig(combined_path, dpi=300, bbox_inches='tight')
plt.close()

print("✅ 已绘制综合直方图（红线=第二高频强度的一半）。")
print(f"保存路径: {combined_path}")

# ********************************** 7. 保存阈值数据 **********************************
threshold_df = pd.DataFrame.from_dict(thresholds, orient='index', columns=['50%_of_second_peak_intensity(x1000)'])
threshold_path = os.path.join(output_dir, "band_second_peak50_thresholds.csv")
threshold_df.to_csv(threshold_path)

print(f"各波段第二高峰强度及50%阈值已保存至: {threshold_path}")
