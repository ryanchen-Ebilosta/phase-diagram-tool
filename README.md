# Phase Diagram Tool for Metallic Systems

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](你的Streamlit链接)

This tool is designed for calculating and plotting binary phase diagrams based on thermodynamic equations. It was developed as part of a research submission to **Journal of Chemical Education(JCE)**.

## 🌟 Key Features
* **Dual Axis Display**: Shows both Weight Percent (wt%) and Mole Fraction (xB).
* **Auto-Eutectic Finder**: Automatically calculates and marks the eutectic point.
* **High-Res Export**: Supports 300 DPI exports (PNG, PDF, TIFF) for academic publication.

## 🧪 Physics Logic
The liquidus lines are calculated using the following equation:
$$T_L = \left( \frac{1}{T_m + 273.15} - \frac{R \cdot \ln(x)}{\Delta H_m \cdot 1000} \right)^{-1} - 273.15$$

## 🚀 How to Use
### 1. Web Version (Recommended)
Simply click the [Streamlit App](你的Streamlit链接) badge above to use the online version.

### 2. Local Version
1. Clone the repo: `git clone https://github.com/你的用户名/phase-diagram-tool.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`
