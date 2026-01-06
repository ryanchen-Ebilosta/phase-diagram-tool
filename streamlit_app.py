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
    
    st.subheader("Interactive Tools")
    target_wt = st.number_input(f"Input Composition (wt% {B_name})", 0.0, 100.0, 50.0)
    if st.button("Apply Vertical Line"):
        st.session_state.v_line_pos = target_wt
    
    # 修改逻辑：点击此按钮将同时控制虚线和交点辅助线的可见性
    if st.button("Toggle Extra Elements (Dashed/Markers)"):
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

    # --- 数据范围设置 ---
    # 修改点 1: 分别定义 A 和 B 的数据范围
    wt_range_A = np.linspace(0, 95, 1000)
    wt_range_B = np.linspace(5, 100, 1000)
    
    xB_fine_A = wt_to_mole_fraction(wt_range_A)
    xB_fine_B = wt_to_mole_fraction(wt_range_B)
    
    T_liq_A = np.array([get_TA(1-x) for x in xB_fine_A])
    T_liq_B = np.array([get_TB(x) for x in xB_fine_B])

    # 绘制共晶线
    ax1.axhline(y=TE, color='black', linestyle='-', lw=1.5, label='Eutectic Line')

    # 绘制实线部分 (Stable: T >= TE)
    mask_A_stable = T_liq_A >= TE
    mask_B_stable = T_liq_B >= TE
    
    ax1.plot(wt_range_A[mask_A_stable], T_liq_A[mask_A_stable], 'b-', lw=2, label=f'Liquidus {A_name}')
    ax1.plot(wt_range_B[mask_B_stable], T_liq_B[mask_B_stable], 'r-', lw=2, label=f'Liquidus {B_name}')
    
    # 修改点 2: 只有在 show_metastable 为 True 时才绘制虚线、垂线和交点数值
    if st.session_state.show_metastable:
        # 绘制虚线部分 (Metastable: T < TE)
        ax1.plot(wt_range_A[~mask_A_stable], T_liq_A[~mask_A_stable], 'b--', lw=1.5, alpha=0.5)
        ax1.plot(wt_range_B[~mask_B_stable], T_liq_B[~mask_B_stable], 'r--', lw=1.5, alpha=0.5)

        # 绘制垂直参考线及交点标注
        if st.session_state.v_line_pos is not None:
            vx = st.session_state.v_line_pos
            v_xb = wt_to_mole_fraction(vx)
            v_ta = get_TA(1 - v_xb)
            v_tb = get_TB(v_xb)
            
            ax1.axvline(x=vx, color='green', linestyle=':', lw=2, label=f'Marker at {vx}wt%')
            ax1.scatter([vx, vx], [v_ta, v_tb], color='green', s=50, zorder=6)
            
            # 在图上标注交点温度
            ax1.text(vx + 1, v_ta, f"{v_ta:.1f}°C", color='blue', fontsize=9, fontweight='bold')
            ax1.text(vx + 1, v_tb, f"{v_tb:.1f}°C", color='red', fontsize=9, fontweight='bold')

    ax1.scatter(wtB_e, TE, color='black', zorder=5)
    ax1.annotate(f"Eutectic: {wtB_e:.1f} wt%, {TE:.1f} °C", 
                 xy=(wtB_e, TE), xytext=(wtB_e, TE + 25),
                 ha='center', arrowprops=dict(arrowstyle='->'))

    # 设置显示范围
    all_temps = np.concatenate([T_liq_A, T_liq_B])
    ax1.set_xlim(0, 100) # 修改点 1: x轴显示范围 0-100
    ax1.set_ylim(np.min(all_temps) - 20, np.max(all_temps) + 20)
    
    ax1.set_xlabel(f"Weight Percent of {B_name} (wt%)", fontweight='bold')
    ax1.set_ylabel("Temperature (°C)", fontweight='bold')

    # Dual Axis (Mole Fraction)
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    xB_ticks = np.linspace(0, 1, 6)
    wtB_ticks = (xB_ticks * B1) / (xB_ticks * B1 + (1 - xB_ticks) * A1) * 100
    ax2.set_xticks(wtB_ticks)
    ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
    ax2.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", fontweight='bold')

    ax1.grid(True, ls=':', alpha=0.4)
    ax1.legend(loc='best', fontsize='small')

    st.pyplot(fig)

    # 6. Results
    st.subheader("Numerical Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Eutectic Temperature", f"{TE:.2f} °C")
    c2.metric("Eutectic Composition (wt%)", f"{wtB_e:.2f} %")
    
    # 结果面板也根据显示状态同步
    if st.session_state.v_line_pos and st.session_state.show_metastable:
        curr_x = st.session_state.v_line_pos
        curr_xb = wt_to_mole_fraction(curr_x)
        st.info(f"Marker Info ({curr_x} wt%): Liquidus {A_name} = {get_TA(1-curr_xb):.2f}°C | Liquidus {B_name} = {get_TB(curr_xb):.2f}°C")

else:
    st.info("Click 'Update Plot' to apply changes.")
