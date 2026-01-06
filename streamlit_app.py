import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# 1. Page Configuration
st.set_page_config(page_title="Binary Phase Diagram Tool", layout="wide")

st.title("Binary Phase Diagram Analysis Tool (Academic Standard)")
st.markdown("---")

# 初始化 Session State 用于存储交互状态
if 'show_metastable' not in st.session_state:
    st.session_state.show_metastable = True
if 'v_line_pos' not in st.session_state:
    st.session_state.v_line_pos = None

# 2. Sidebar Inputs
st.sidebar.header("Input Parameters")

with st.sidebar:
    st.subheader("Component A")
    A_name = st.text_input("Name of A", "Cd")
    A1 = st.number_input("Molecular Weight (A1)", value=112.41)
    A2 = st.number_input("Melting Point °C (A2)", value=321.1)
    A3 = st.number_input("Molar Enthalpy kJ/mol (A3)", value=6.19)

    st.divider()

    st.subheader("Component B")
    B_name = st.text_input("Name of B", "Bi")
    B1 = st.number_input("Molecular Weight (B1)", value=208.98)
    B2 = st.number_input("Melting Point °C (B2)", value=271.4)
    B3 = st.number_input("Molar Enthalpy kJ/mol (B3)", value=11.3)

    st.divider()
    
    # 修改点 2 & 3: 交互功能
    st.subheader("Interactive Tools")
    target_wt = st.number_input(f"Input Composition (wt% {B_name})", 0.0, 100.0, 50.0)
    if st.button("Apply Vertical Line"):
        st.session_state.v_line_pos = target_wt
    
    if st.button("Toggle Metastable Lines (Dashed)"):
        st.session_state.show_metastable = not st.session_state.show_metastable

    st.divider()
    update_btn = st.sidebar.button("Update Plot", type="primary")

# 3. Core Physics Logic
def get_TA(xA):
    if xA <= 1e-9: return -273.15
    return 1 / (1 / (A2 + 273.15) - 8.314 * np.log(xA) / (A3 * 1000)) - 273.15

def get_TB(xB):
    if xB <= 1e-9: return -273.15
    return 1 / (1 / (B2 + 273.15) - 8.314 * np.log(xB) / (B3 * 1000)) - 273.15

def wt_to_mole_fraction(wtB):
    return (wtB/B1) / (wtB/B1 + (100-wtB)/A1)

# Logic to run
if update_btn or 'first_run' not in st.session_state:
    st.session_state['first_run'] = False
    
    # Calculate Eutectic Point
    xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
    TE = get_TA(1 - xB_e)
    wtB_e = (xB_e * B1) / (xB_e * B1 + (1 - xB_e) * A1) * 100

    # 4. Plotting Logic
    fig, ax1 = plt.subplots(figsize=(10, 7))

    # 修改点 1: x轴范围设为 5 到 100
    wtB_fine = np.linspace(5, 100, 1000)
    xB_fine = wt_to_mole_fraction(wtB_fine)
    
    T_liq_A = np.array([get_TA(1-x) for x in xB_fine])
    T_liq_B = np.array([get_TB(x) for x in xB_fine])

    # 绘制三相线
    ax1.axhline(y=TE, color='black', linestyle='-', lw=1.5, label='Eutectic Line')

    # 绘制实线 (Stable)
    ax1.plot(wtB_fine[T_liq_A >= TE], T_liq_A[T_liq_A >= TE], 'b-', lw=2, label=f'Liquidus {A_name}')
    ax1.plot(wtB_fine[T_liq_B >= TE], T_liq_B[T_liq_B >= TE], 'r-', lw=2, label=f'Liquidus {B_name}')
    
    # 修改点 3: 根据状态显示/隐藏虚线
    if st.session_state.show_metastable:
        ax1.plot(wtB_fine[T_liq_A < TE], T_liq_A[T_liq_A < TE], 'b--', lw=1.5, alpha=0.5)
        ax1.plot(wtB_fine[T_liq_B < TE], T_liq_B[T_liq_B < TE], 'r--', lw=1.5, alpha=0.5)

    # 修改点 2: 垂直线及交点逻辑
    if st.session_state.v_line_pos is not None:
        vx = st.session_state.v_line_pos
        v_xb = wt_to_mole_fraction(vx)
        v_ta = get_TA(1 - v_xb)
        v_tb = get_TB(v_xb)
        
        ax1.axvline(x=vx, color='green', linestyle=':', lw=2, label=f'Marker at {vx}wt%')
        ax1.scatter([vx, vx], [v_ta, v_tb], color='green', s=50, zorder=6)
        
        # 在图上标注交点温度
        ax1.text(vx+1, v_ta, f"{v_ta:.1f}°C", color='blue', fontweight='bold')
        ax1.text(vx+1, v_tb, f"{v_tb:.1f}°C", color='red', fontweight='bold')

    ax1.scatter(wtB_e, TE, color='black', zorder=5)

    # 纵轴显示范围
    all_temps = np.concatenate([T_liq_A, T_liq_B])
    ax1.set_xlim(5, 100)
    ax1.set_ylim(np.min(all_temps) - 20, np.max(all_temps) + 20)
    
    ax1.set_xlabel(f"Weight Percent of {B_name} (wt%)", fontweight='bold')
    ax1.set_ylabel("Temperature (°C)", fontweight='bold')

    # Dual Axis
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    xB_ticks = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
    wtB_ticks = (xB_ticks * B1) / (xB_ticks * B1 + (1 - xB_ticks) * A1) * 100
    ax2.set_xticks(wtB_ticks)
    ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
    ax2.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", fontweight='bold')

    ax1.grid(True, ls=':', alpha=0.4)
    ax1.legend(loc='best', fontsize='small')

    # 5. Display Plot
    st.pyplot(fig)

    # 6. Results
    st.subheader("Numerical Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Eutectic Temperature", f"{TE:.2f} °C")
    c2.metric("Eutectic Composition (wt%)", f"{wtB_e:.2f} %")
    if st.session_state.v_line_pos:
        st.info(f"Marker at {st.session_state.v_line_pos} wt%: Liquidus A = {get_TA(1-wt_to_mole_fraction(st.session_state.v_line_pos)):.2f}°C, Liquidus B = {get_TB(wt_to_mole_fraction(st.session_state.v_line_pos)):.2f}°C")

else:
    st.info("Click 'Update Plot' to generate the diagram.")
