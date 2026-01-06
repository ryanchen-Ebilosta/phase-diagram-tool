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
    A1 = st.number_input("Molecular Weight", value=112.41)
    A2 = st.number_input("Melting Point °C", value=321.1)
    A3 = st.number_input("Molar Enthalpy kJ/mol", value=6.19)

    st.divider()

    st.subheader("Component B (Right)")
    B_name = st.text_input("Name of B", "Bi")
    B1 = st.number_input("Molecular Weight", value=208.98)
    B2 = st.number_input("Melting Point °C", value=271.4)
    B3 = st.number_input("Molar Enthalpy kJ/mol", value=11.3)

    st.divider()
    
    st.subheader("Interactive Tools")
    
    if st.button("Switch X-Axis Mode"):
        st.session_state.axis_mode = "Mole Fraction (xB)" if st.session_state.axis_mode == "Weight Percent (wt%)" else "Weight Percent (wt%)"
        st.session_state.v_line_pos = None 
    st.caption(f"Current Main Axis: **{st.session_state.axis_mode}**")

    max_val = 100.0 if "wt" in st.session_state.axis_mode else 1.0
    target_val = st.number_input(f"Input Comp. ({st.session_state.axis_mode})", 0.0, max_val, max_val/2)
    if st.button("Apply Vertical Line"):
        st.session_state.v_line_pos = target_val
    
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
    
    # 计算热力学数据
    xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
    TE = get_TA(1 - xB_e)
    wtB_e = mole_to_wt_fraction(xB_e)

    # 4. Plotting Logic
    fig, ax1 = plt.subplots(figsize=(10, 7))
    plt.subplots_adjust(bottom=0.18) # 调整底部留白

    # 确定主轴显示范围
    if st.session_state.axis_mode == "Weight Percent (wt%)":
        x_main_A = np.linspace(0, 95, 1000)
        x_main_B = np.linspace(5, 100, 1000)
        xB_for_A = wt_to_mole_fraction(x_main_A)
        xB_for_B = wt_to_mole_fraction(x_main_B)
        x_limit = (0, 100)
    else: 
        x_main_A = np.linspace(0, 0.95, 1000)
        x_main_B = np.linspace(0.05, 1, 1000)
        xB_for_A = x_main_A
        xB_for_B = x_main_B
        x_limit = (0, 1.0)

    T_liq_A = np.array([get_TA(1-x) for x in xB_for_A])
    T_liq_B = np.array([get_TB(x) for x in xB_for_B])

    # 绘制水平共晶线
    ax1.axhline(y=TE, color='black', linestyle='-', lw=1.5, label='Eutectic Line')
    
    # 绘制液相线 (Stable)
    mask_A, mask_B = T_liq_A >= TE, T_liq_B >= TE
    ax1.plot(x_main_A[mask_A], T_liq_A[mask_A], 'b-', lw=2, label=f'Liquidus {A_name}')
    ax1.plot(x_main_B[mask_B], T_liq_B[mask_B], 'r-', lw=2, label=f'Liquidus {B_name}')
    
    # 辅助元素逻辑
    if st.session_state.show_metastable:
        # 亚稳态虚线
        ax1.plot(x_main_A[~mask_A], T_liq_A[~mask_A], 'b--', lw=1.5, alpha=0.5)
        ax1.plot(x_main_B[~mask_B], T_liq_B[~mask_B], 'r--', lw=1.5, alpha=0.5)
        
        # 交互垂线和温度标注
        if st.session_state.v_line_pos is not None:
            vx = st.session_state.v_line_pos
            v_xb = vx if "xB" in st.session_state.axis_mode else wt_to_mole_fraction(vx)
            v_ta, v_tb = get_TA(1 - v_xb), get_TB(v_xb)
            ax1.axvline(x=vx, color='green', linestyle=':', lw=2)
            ax1.scatter([vx, vx], [v_ta, v_tb], color='green', s=40, zorder=6)
            ax1.text(vx, v_ta + 5, f"{v_ta:.1f}°C", color='blue', fontsize=10, ha='center')
            ax1.text(vx, v_tb + 5, f"{v_tb:.1f}°C", color='red', fontsize=10, ha='center')

    ax1.text(0, -0.10, A_name, transform=ax1.transAxes, ha='center', va='top', 
             fontsize=14, fontweight='bold', color='blue')
    ax1.text(1, -0.10, B_name, transform=ax1.transAxes, ha='center', va='top', 
             fontsize=14, fontweight='bold', color='red')

    # 设置 坐标轴
    ax1.set_xlim(x_limit)
    all_temps = np.concatenate([T_liq_A, T_liq_B])
    ax1.set_ylim(np.min(all_temps) - 20, np.max(all_temps) + 30)
    ax1.set_ylabel("Temperature (°C)", fontweight='bold', fontsize=14)
    ax1.set_xlabel(st.session_state.axis_mode, fontweight='bold', fontsize=14)

    # 辅助双轴处理
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    if st.session_state.axis_mode == "Weight Percent (wt%)":
        xB_ticks = np.linspace(0, 1, 6)
        ax2.set_xticks([mole_to_wt_fraction(x) for x in xB_ticks])
        ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
        ax2.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", color='gray', fontsize=10)
    else:
        wt_ticks = np.linspace(0, 100, 6)
        ax2.set_xticks([wt_to_mole_fraction(w) for w in wt_ticks])
        ax2.set_xticklabels([f"{int(x)}" for x in wt_ticks])
        ax2.set_xlabel(f"Weight Percent of {B_name} (wt%)", color='gray', fontsize=10)

    ax1.grid(True, ls=':', alpha=0.4)
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=3)

    st.pyplot(fig)

    # 5. Numerical Results
    st.subheader("Numerical Results")
    res_c1, res_c2, res_c3 = st.columns(3)
    res_c1.metric("Eutectic Temperature", f"{TE:.2f} °C")
    res_c2.metric(f"Eutectic ({B_name} wt%)", f"{wtB_e:.2f} %")
    res_c3.metric(f"Eutectic ({B_name} xB)", f"{xB_e:.3f}")

else:
    st.info("Click 'Update Plot' to refresh the diagram.")

