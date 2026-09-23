import streamlit as st
import numpy as np
import pandas as pd
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

# 加载 database.xlsx 数据
@st.cache_data
def load_database():
    try:
        df = pd.read_excel("database.xlsx")
        # 清理 Name 列字符串两端的空格，确保匹配精准
        if 'Name' in df.columns:
            df['Name'] = df['Name'].astype(str).str.strip()
        return df
    except Exception as e:
        return None

df_db = load_database()

# 2. Sidebar Inputs (Compact Layout)
st.sidebar.header("Parameters & Controls")

if df_db is not None and 'Name' in df_db.columns:
    comp_names = df_db['Name'].dropna().tolist()
    
    # 侧边栏：组件 A 选择（一级分类）
    st.sidebar.subheader("Component A (Left)")
    default_a_idx = comp_names.index("Cd") if "Cd" in comp_names else 0
    A_name = st.sidebar.selectbox("Select A", comp_names, index=default_a_idx, key="sel_A")
    
    # 获取组件 A 所在的行
    matched_a = df_db[df_db['Name'] == A_name]
    if not matched_a.empty:
        row_a = matched_a.iloc[0]
    else:
        row_a = df_db.iloc[0]
        
    # 读取组件 A 的第 2, 3, 4 列数据 (index 1, 2, 3)
    A1 = float(row_a.iloc[1]) if pd.notna(row_a.iloc[1]) else 1.0
    A2 = float(row_a.iloc[2]) if pd.notna(row_a.iloc[2]) else 0.0
    A3 = float(row_a.iloc[3]) if pd.notna(row_a.iloc[3]) else 0.0
    
    col_a1, col_a2, col_a3 = st.sidebar.columns(3)
    with col_a1:
        st.number_input("MW", value=A1, disabled=True)
    with col_a2:
        st.number_input("MP (°C)", value=A2, disabled=True)
    with col_a3:
        st.number_input("Enthalpy", value=A3, disabled=True)

    st.sidebar.divider()

    # ---------------------------------------------------------
    # 侧边栏：组件 B 选择（二级分类）
    # ---------------------------------------------------------
    st.sidebar.subheader("Component B (Right)")
    
    # 1）初始化列表
    matches = []
    
    # 2）根据 A_name 已定位到 row_a
    if row_a is not None:
        # 3）在该行中，把第 5 列到第 8 列（Python 索引 4 到 7，即 Excel 的 E 到 H 列）依次读入列表，空单元格不计入
        for col_idx in range(4, min(8, len(df_db.columns))):
            val = row_a.iloc[col_idx]
            if pd.notna(val):
                clean_val = str(val).strip()
                if clean_val and clean_val.lower() != 'nan' and clean_val not in matches:
                    matches.append(clean_val)
                    
    # 4）列表中的所有化合物就是 B 的下拉菜单
    if not matches:
        matches = ["无可用匹配"]
        
    B_name = st.sidebar.selectbox("Select B (Match)", matches, key="sel_B")
    
    # 获取组件 B 的第 2, 3, 4 列数据（优化匹配逻辑，忽略大小写与空格）
    row_b_df = df_db[df_db['Name'].str.lower() == B_name.strip().lower()]
    if not row_b_df.empty:
        row_b = row_b_df.iloc[0]
        B1 = float(row_b.iloc[1]) if pd.notna(row_b.iloc[1]) else 1.0
        B2 = float(row_b.iloc[2]) if pd.notna(row_b.iloc[2]) else 0.0
        B3 = float(row_b.iloc[3]) if pd.notna(row_b.iloc[3]) else 0.0
    else:
        B1, B2, B3 = 208.98, 271.4, 11.3
        
    col_b1, col_b2, col_b3 = st.sidebar.columns(3)
    with col_b1:
        st.number_input("MW ", value=B1, disabled=True)
    with col_b2:
        st.number_input("MP (°C) ", value=B2, disabled=True)
    with col_b3:
        st.number_input("Enthalpy ", value=B3, disabled=True)

else:
    st.sidebar.error("未找到 'database.xlsx' 或表格缺少 'Name' 列，请检查文件！")
    A_name, B_name = "Cd", "Bi"
    A1, A2, A3 = 112.41, 321.1, 6.19
    B1, B2, B3 = 208.98, 271.4, 11.3

st.sidebar.divider()

# 侧边栏：交互辅助工具（紧凑排版）
st.sidebar.subheader("Interactive Tools")
if st.sidebar.button("Switch X-Axis Mode"):
    st.session_state.axis_mode = "Mole Fraction (xB)" if st.session_state.axis_mode == "Weight Percent (wt%)" else "Weight Percent (wt%)"
    st.session_state.v_line_pos = None 

max_val = 100.0 if "wt" in st.session_state.axis_mode else 1.0
target_val = st.sidebar.number_input(f"Input Comp. ({st.session_state.axis_mode})", 0.0, max_val, max_val/2)
if st.sidebar.button("Apply Vertical Line"):
    st.session_state.v_line_pos = target_val

if st.sidebar.button("Toggle Metastable Lines"):
    st.session_state.show_metastable = not st.session_state.show_metastable

# 3. Core Physics Logic
def get_TA(xA):
    if xA <= 1e-9 or A3 == 0: return -273.15
    return 1 / (1 / (A2 + 273.15) - 8.314 * np.log(xA) / (A3 * 1000)) - 273.15

def get_TB(xB):
    if xB <= 1e-9 or B3 == 0: return -273.15
    return 1 / (1 / (B2 + 273.15) - 8.314 * np.log(xB) / (B3 * 1000)) - 273.15

def wt_to_mole_fraction(wtB):
    if A1 == 0 or B1 == 0: return 0
    return (wtB/B1) / (wtB/B1 + (100-wtB)/A1)

def mole_to_wt_fraction(xB):
    if A1 == 0 or B1 == 0: return 0
    return (xB*B1) / (xB*B1 + (1-xB)*A1) * 100

# 计算热力学数据
if B_name != "无可用匹配" and A3 > 0 and B3 > 0:
    try:
        xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
        TE = get_TA(1 - xB_e)
        wtB_e = mole_to_wt_fraction(xB_e)
    except Exception:
        xB_e, TE, wtB_e = 0.5, 0.0, 50.0

    # 4. Plotting Logic (自动响应更新)
    fig, ax1 = plt.subplots(figsize=(10, 6.5))
    plt.subplots_adjust(bottom=0.18)

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
        ax1.plot(x_main_A[~mask_A], T_liq_A[~mask_A], 'b--', lw=1.5, alpha=0.5)
        ax1.plot(x_main_B[~mask_B], T_liq_B[~mask_B], 'r--', lw=1.5, alpha=0.5)
        
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
    st.warning("请选择有效的组分及匹配项。")
