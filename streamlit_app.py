import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# 1. Page Configuration
st.set_page_config(page_title="Binary Phase Diagram Tool", layout="wide")

st.title("Binary Phase Diagram Analysis Tool (Academic Standard)")
st.markdown("---")

# 初始化 Session State
if 'show_metastable' not in st.session_state:
    st.session_state.show_metastable = True
if 'v_line_pos' not in st.session_state:
    st.session_state.v_line_pos = None
if 'axis_mode' not in st.session_state:
    st.session_state.axis_mode = "Weight Percent (wt%)"

# 2. Sidebar Inputs
st.sidebar.header("Input Parameters")

with st.sidebar:
    st.subheader("Component A (Left)")
    A_name = st.text_input("Name of A", "Cd")
    A1 = st.number_input("Molecular Weight (A1)", value=112.41)
    A2 = st.number_input("Melting Point °C (A2)", value=321.1)
    A3 = st.number_input("Molar Enthalpy kJ/mol (A3)", value=6.19)

    st.divider()

    st.subheader("Component B (Right)")
    B_name = st.text_input("Name of B", "Bi")
    B1 = st.number_input("Molecular Weight (B1)", value=208.98)
    B2 = st.number_input("Melting Point °C (B2)", value=271.4)
    B3 = st.number_input("Molar Enthalpy kJ/mol (B3)", value=11.3)

    st.divider()
    
    st.subheader("Interactive Tools")
    
    # 修改点 1: 添加 X 轴模式切换按钮
    if st.button("Switch X-Axis Mode"):
        if st.session_state.axis_mode == "Weight Percent (wt%)":
            st.session_state.axis_mode = "Mole Fraction (xB)"
        else:
            st.session_state.axis_mode = "Weight Percent (wt%)"
    st.caption(f"Current Priority: **{st.session_state.axis_mode}**")

    target_wt = st.number_input(f"Input Comp. (wt% {B_name})", 0.0, 100.0, 50.0)
    if st.button("Apply Vertical Line"):
        st.session_state.v_line_pos = target_wt
    
    if st.button("Toggle Extra Elements"):
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

def mole_to_wt_fraction(xB):
    return (xB*B1) / (xB*B1 + (1-xB)*A1) * 100

# Logic to run
if update_btn or 'first_run' not in st.session_state:
    st.session_state['first_run'] = False
    
    # Calculate Eutectic Point
    xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
    TE = get_TA(1 - xB_e)
    wtB_e = mole_to_wt_fraction(xB_e)

    # 4. Plotting Logic
    fig, ax1 = plt.subplots(figsize=(10, 7))

    # 数据范围定义
    wt_range_A = np.linspace(0, 95, 1000)
    wt_range_B = np.linspace(5, 100, 1000)
    
    xB_fine_A = wt_to_mole_fraction(wt_range_A)
    xB_fine_B = wt_to_mole_fraction(wt_range_B)
    
    T_liq_A = np.array([get_TA(1-x) for x in xB_fine_A])
    T_liq_B = np.array([get_TB(x) for x in xB_fine_B])

    # 绘制共晶线
    ax1.axhline(y=TE, color='black', linestyle='-', lw=1.5, label='Eutectic Line')

    # 绘制实线 (Stable)
    mask_A_stable = T_liq_A >= TE
    mask_B_stable = T_liq_B >= TE
    ax1.plot(wt_range_A[mask_A_stable], T_liq_A[mask_A_stable], 'b-', lw=2, label=f'Liquidus {A_name}')
    ax1.plot(wt_range_B[mask_B_stable], T_liq_B[mask_B_stable], 'r-', lw=2, label=f'Liquidus {B_name}')
    
    # 隐藏/显示 逻辑
    if st.session_state.show_metastable:
        ax1.plot(wt_range_A[~mask_A_stable], T_liq_A[~mask_A_stable], 'b--', lw=1.5, alpha=0.5)
        ax1.plot(wt_range_B[~mask_B_stable], T_liq_B[~mask_B_stable], 'r--', lw=1.5, alpha=0.5)

        if st.session_state.v_line_pos is not None:
            vx = st.session_state.v_line_pos
            v_xb = wt_to_mole_fraction(vx)
            v_ta, v_tb = get_TA(1 - v_xb), get_TB(v_xb)
            ax1.axvline(x=vx, color='green', linestyle=':', lw=2)
            ax1.scatter([vx, vx], [v_ta, v_tb], color='green', s=40, zorder=6)
            ax1.text(vx + 1, v_ta, f"{v_ta:.1f}°C", color='blue', fontsize=9)
            ax1.text(vx + 1, v_tb, f"{v_tb:.1f}°C", color='red', fontsize=9)

    ax1.scatter(wtB_e, TE, color='black', zorder=5)

    # 修改点 2: 在横轴两侧显示物质名称
    ax1.text(-2, TE - 15, A_name, fontweight='bold', fontsize=12, ha='center', color='blue')
    ax1.text(102, TE - 15, B_name, fontweight='bold', fontsize=12, ha='center', color='red')

    # 设置轴范围和标签 (根据切换模式)
    ax1.set_xlim(0, 100)
    all_temps = np.concatenate([T_liq_A, T_liq_B])
    ax1.set_ylim(np.min(all_temps) - 20, np.max(all_temps) + 20)
    ax1.set_ylabel("Temperature (°C)", fontweight='bold')

    # 双坐标轴逻辑调整
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())

    if st.session_state.axis_mode == "Weight Percent (wt%)":
        # 下方为主轴 wt%, 上方为辅轴 xB
        ax1.set_xlabel(f"Weight Percent of {B_name} (wt%)", fontweight='bold')
        xB_ticks = np.linspace(0, 1, 6)
        wtB_ticks = mole_to_wt_fraction(xB_ticks)
        ax2.set_xticks(wtB_ticks)
        ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
        ax2.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", color='gray')
    else:
        # 下方为主轴 xB (通过映射), 上方为辅轴 wt%
        ax1.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", fontweight='bold')
        # 修改下轴刻度：让用户看的是xB的匀称刻度
        xB_vals = np.linspace(0, 1, 6)
        ax1.set_xticks(mole_to_wt_fraction(xB_vals))
        ax1.set_xticklabels([f"{x:.1f}" for x in xB_vals])
        
        ax2.set_xlabel(f"Weight Percent of {B_name} (wt%)", color='gray')
        ax2.set_xticks([0, 20, 40, 60, 80, 100])
        ax2.set_xticklabels(["0", "20", "40", "60", "80", "100"])

    ax1.grid(True, ls=':', alpha=0.4)
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

    st.pyplot(fig)

    # 6. Results
    st.subheader("Numerical Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Eutectic Temperature", f"{TE:.2f} °C")
    c2.metric(f"Eutectic ({B_name} wt%)", f"{wtB_e:.2f} %")
    c3.metric(f"Eutectic ({B_name} xB)", f"{xB_e:.3f}")

else:
    st.info("Click 'Update Plot' to refresh the diagram.")
