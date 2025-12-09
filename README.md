# HIDEDaSF
# HIDEDaSF: a detection and correction framework for edge effect on hyperspectral intensity data for novel hyperspectral LiDAR remote sensor
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
HIDEDaSF is a new integrated edge effect detection and correction framework for hyperspectral LiDAR system, incorporating histogram of intensity distribution, edge detection, and spherical spatial filtering (HIDEDaSF) This framework addresses the intensity loss and spectral distortion caused by partial laser footprint illumination at leaf boundaries, enabling more accurate retrieval of vegetation intensity and spectral parameters from HSL data.

The methodology is detailed in the research paper:  
*Bai, J., Niu, Z., Zhu, J., et al. (2025). HIDEDaSF: a detection and correction framework for edge effect on hyperspectral intensity data for novel hyperspectral LiDAR remote sensor. Remote Sensing of Environment.*

## Workflow
The framework consists of **5 core modules** that process raw HSL point cloud data sequentially:
1. **Pot Region Removal** (Fun0_Pot_Removal.py): Eliminate non-vegetation background to focus on leaf point clouds.
2. **Band Intensity Histogram Generation** (Fun1_LeafPointCloud_Histogram.py): Calculate intensity thresholds for edge detection using second-peak statistics across 32 HSL bands (409–914 nm).
3. **Rough Edge Detection** (Fun2_RoughEdgeDetection.py): Extract candidate edge points by thresholding intensity values for each spectral band.
4. **Refined Edge Extraction** (Fun3_RefinedEdgeDetection.py): Filter false edge points via grid projection, convolution-based neighborhood analysis, and morphological dilation.
5. **Spherical Spatial Filtering** (Fun4_SphericalSpaceFiltering.py): Correct edge point intensities using the mean value of neighboring non-edge points within a spherical neighborhood.

## Installation
### Dependencies
The code requires the following Python libraries:
```bash
pip install pandas numpy matplotlib scipy
```

### Data Preparation
1. Raw HSL point cloud data should be formatted as a CSV file with columns:  
   `X, Y, Z, distance, 409, 425, ..., 914` (3D coordinates + distance + 32 spectral band intensities)
2. Update the `input_path` and `output_path` variables in each script to match your local data directory.

## Usage
Run the scripts in **sequential order** (from Fun0 to Fun4):
### 1. Remove Pot Region
```python
python Fun0_Pot_Removal.py
```
- **Function**: Filters out points within the predefined 3D bounding box of the flowerpot (`-20≤X≤12, -20≤Y≤20, 480≤Z≤530`).
- **Output**: `all_no_pot.csv` (vegetation-only point cloud).

### 2. Generate Band Intensity Histograms
```python
python Fun1_LeafPointCloud_Histogram.py
```
- **Function**: Plots intensity histograms for all 32 bands, calculates edge thresholds (50% of the second peak intensity), and saves thresholds to a CSV file.
- **Outputs**: 
  - `all_band_histograms_second_peak50.png` (combined histogram plot)
  - `band_second_peak50_thresholds.csv` (threshold values per band)

### 3. Detect Rough Edge Points
```python
python Fun2_RoughEdgeDetection.py
```
- **Function**: Identifies edge points for each band by thresholding and merges results across all bands to form a rough edge point set.
- **Outputs**:
  - Per-band edge point CSVs (`edge_points_XXXnm.csv`)
  - `all_edge_points.csv` (merged rough edge points)
  - `band_thresholds_second_peak50.csv` (threshold log)

### 4. Extract Refined Edges
```python
python Fun3_RefinedEdgeDetection.py
```
- **Function**: 
  1. Projects rough edges into a 0.45 cm resolution grid
  2. Uses a 4×4 convolution kernel to retain valid edges (≥4 neighboring edge pixels)
  3. Performs morphological dilation to refine edge boundaries
  4. Generates non-edge point cloud by excluding refined edges
- **Outputs**:
  - `rough_edge_projection.png` / `SwellRefined_edge_projection_045cm.png` (edge projection plots)
  - `SwellRefined_edge_points.csv` (final refined edge points)
  - `allNoRefinedEdgeNoPot.csv` (non-edge vegetation points)

### 5. Correct Edge Intensities
```python
python Fun4_SphericalSpaceFiltering.py
```
- **Function**: Corrects edge point intensities using the mean of non-edge points within a 20 mm spherical radius (adjustable via `radius` parameter).
- **Outputs**:
  - `allNoRefinedEdgeNoPot.csv` (non-edge points, unchanged)
  - `EdgeCorrectedNoLeafNoPot.csv` (corrected edge points)
  - `EdgeCorrectedHasLeafNoPot.csv` (merged corrected + non-edge points)

## Performance Metrics
After correction, the framework achieves:
- **22.68% reduction** in intensity standard deviation (σ) of edge regions
- **28.30% reduction** in coefficient of variation (CV)
- Mean ratio of CV (corrected/raw) = 0.7288 (all < 1, confirming correction effectiveness)

## Directory Structure
```
HIDEDaSF/
├── Fun0_Pot_Removal.py
├── Fun1_LeafPointCloud_Histogram.py
├── Fun2_RoughEdgeDetection.py
├── Fun3_RefinedEdgeDetection.py
├── Fun4_SphericalSpaceFiltering.py
├── README.md
└── data/
    ├── original_data/          # Raw input data
    ├── Fun0_Pot_Removal/       # Output of Fun0
    ├── Fun1_LeafPointCloud_Histogram/  # Output of Fun1
    ├── Fun2_RoughEdgeDetection/        # Output of Fun2
    ├── Fun3_RefinedEdgeDetection/      # Output of Fun3
    └── Fun4_SphericalSpaceFiltering/   # Output of Fun4
```


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For questions or issues, contact Jie Bai at `baijie@uestc.edu.cn`.
