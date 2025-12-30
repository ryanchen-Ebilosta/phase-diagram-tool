import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# 1. 页面配置
st.set_page_config(page_title="Binary Phase Diagram Tool", layout="wide")

st.title("二元金属相图在线分析工具 (CEJ Standard)")
st.markdown("---")

# 2. 侧边栏输入 (替代 Tkinter 的 Entry)
st.sidebar.header("输入参数")

with st.sidebar:
    st.subheader("组分 A")
    A_name = st.text_input("A 名称", "Sn")
    A1 = st.number_input("A 分子量 (A1)", value=118.7)
    A2 = st.number_input("A 熔点 ℃ (A2)", value=231.9)
    A3 = st.number_input("A 摩尔熔化焓 kJ/mol (A3)", value=7.0)

    st.divider()

    st.subheader("组分 B")
    B_name = st.text_input("B 名称", "Pb")
    B1 = st.number_input("B 分子量 (B1)", value=207.2)
    B2 = st.number_input("B 熔点 ℃ (B2)", value=327.5)
    B3 = st.number_input("B 摩尔熔化焓 kJ/mol (B3)", value=4.77)

# 3. 核心物理计算逻辑 (与 main.py 一致)
def get_TA(xA):
    if xA <= 1e-9: return -273.15
    return 1 / (1 / (A2 + 273.15) - 8.314 * np.log(xA) / (A3 * 1000)) - 273.15

def get_TB(xB):
    if xB <= 1e-9: return -273.15
    return 1 / (1 / (B2 + 273.15) - 8.314 * np.log(xB) / (B3 * 1000)) - 273.15

# 计算共晶点
xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
TE = get_TA(1 - xB_e)
wtB_e = (xB_e * B1) / (xB_e * B1 + (1 - xB_e) * A1) * 100

# 4. 绘图逻辑 (使用 Matplotlib)
fig, ax1 = plt.subplots(figsize=(10, 7))

wtB_fine = np.linspace(0, 100, 500)
xB_fine = (wtB_fine/B1) / (wtB_fine/B1 + (100-wtB_fine)/A1)
T_liq_A = np.array([get_TA(1-x) for x in xB_fine])
T_liq_B = np.array([get_TB(x) for x in xB_fine])

ax1.plot(wtB_fine[T_liq_A >= TE], T_liq_A[T_liq_A >= TE], 'b-', lw=2, label=f'Liquidous {A_name}')
ax1.plot(wtB_fine[T_liq_B >= TE], T_liq_B[T_liq_B >= TE], 'r-', lw=2, label=f'Liquidous {B_name}')
ax1.axhline(y=TE, color='black', linestyle='--', alpha=0.6)
ax1.scatter(wtB_e, TE, color='black', zorder=5)

# 标注坐标
ax1.annotate(f"E: {wtB_e:.1f} wt%, {TE:.1f} °C\n$x_B$ = {xB_e:.3f}", 
             xy=(wtB_e, TE), xytext=(wtB_e, TE+30),
             ha='center', arrowprops=dict(arrowstyle='->'))

ax1.set_xlim(0, 100)
ax1.set_ylim(TE - 100, max(A2, B2) + 50)
ax1.set_xlabel(f"Weight Percent of {B_name} (wt%)", fontweight='bold')
ax1.set_ylabel("Temperature (°C)", fontweight='bold')

# 双轴逻辑
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
xB_ticks = np.linspace(0, 1, 6)
wtB_ticks = (xB_ticks * B1) / (xB_ticks * B1 + (1 - xB_ticks) * A1) * 100
ax2.set_xticks(wtB_ticks)
ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
ax2.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", fontweight='bold')

ax1.grid(True, ls=':', alpha=0.6)
ax1.legend()

# 5. 在网页上显示图片 (替代 plt.show())
st.pyplot(fig)

# 6. 数据结果展示
col1, col2, col3 = st.columns(3)
col1.metric("共晶温度 TE", f"{TE:.2f} °C")
col2.metric("共晶点 wt%", f"{wtB_e:.2f} %")
col3.metric("共晶点 xB", f"{xB_e:.3f}")