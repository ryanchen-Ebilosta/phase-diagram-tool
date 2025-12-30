import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- 1. 页面基本设置 ---
st.set_page_config(page_title="二元相图交互演示")
st.title("固态不互溶二元体系 - 自动绘图工具")
st.sidebar.header("调整物理参数")

# --- 2. 侧边栏输入参数 (模拟液相线公式 T = Tm - m*x) ---
# Tm 是纯金属熔点，m 是下降斜率
tm_a = st.sidebar.slider("金属 A 的熔点 (°C)", 500, 1500, 1000)
slope_a = st.sidebar.slider("A 侧液相线下降斜率", 1, 20, 10)

tm_b = st.sidebar.slider("金属 B 的熔点 (°C)", 500, 1500, 800)
slope_b = st.sidebar.slider("B 侧液相线下降斜率", 1, 20, 8)

# --- 3. 核心数学计算 ---
# x 轴代表组元 B 的含量 (0 到 1)
x_range = np.linspace(0, 1, 500)

# 计算两条液相线
# A侧：T = Tm_A - slope_A * (x*100)
line_a = tm_a - slope_a * (x_range * 100)
# B侧：T = Tm_B - slope_B * ((1-x)*100)
line_b = tm_b - slope_b * ((1 - x_range) * 100)

# 寻找两条线的交点（共晶点）
# 原理：寻找两条线高度差绝对值最小的点
diff = np.abs(line_a - line_b)
idx = np.argmin(diff)
x_e = x_range[idx] # 共晶成分
t_e = line_a[idx]  # 共晶温度

# --- 4. 绘图部分 ---
fig, ax = plt.subplots(figsize=(8, 6))

# 画 A 侧液相线 (到交点为止)
ax.plot(x_range[:idx+1], line_a[:idx+1], color='blue', linewidth=2, label='Liquidus A')
# 画 B 侧液相线 (从交点开始)
ax.plot(x_range[idx:], line_b[idx:], color='red', linewidth=2, label='Liquidus B')

# 【关键点】画经过交点的水平线 (共晶线)
ax.axhline(y=t_e, color='black', linestyle='--', linewidth=1.5, label=f'Eutectic Line (T={t_e:.1f}°C)')

# 标注交点
ax.scatter(x_e, t_e, color='black', s=50, zorder=5)
ax.text(x_e, t_e + 20, f' Eutectic Point\n ({x_e*100:.1f}%, {t_e:.1f}°C)', fontsize=10)

# 图表装饰
ax.set_xlim(0, 1)
ax.set_ylim(400, 1600)
ax.set_xlabel("Composition of B (mol fraction)")
ax.set_ylabel("Temperature (°C)")
ax.legend()
ax.grid(alpha=0.3)

# --- 5. 在小程序中显示 ---
st.pyplot(fig)

st.info(f"理论分析：当前共晶成分为 {x_e*100:.2f}% B，共晶温度为 {t_e:.2f} °C。")