import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# 1. Page Configuration
st.set_page_config(page_title="Binary Phase Diagram Tool", layout="wide")

st.title("Binary Phase Diagram Analysis Tool (Academic Standard)")
st.markdown("---")

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
    # 1) Add Update Button
    update_btn = st.sidebar.button("Update Plot", type="primary")

# 3. Core Physics Logic
def get_TA(xA):
    if xA <= 1e-9: return -273.15
    return 1 / (1 / (A2 + 273.15) - 8.314 * np.log(xA) / (A3 * 1000)) - 273.15

def get_TB(xB):
    if xB <= 1e-9: return -273.15
    return 1 / (1 / (B2 + 273.15) - 8.314 * np.log(xB) / (B3 * 1000)) - 273.15

# Logic to run only when button is clicked or at the first run
if update_btn or 'first_run' not in st.session_state:
    st.session_state['first_run'] = False
    
    # Calculate Eutectic Point
    xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
    TE = get_TA(1 - xB_e)
    wtB_e = (xB_e * B1) / (xB_e * B1 + (1 - xB_e) * A1) * 100

    # 4. Plotting Logic
    fig, ax1 = plt.subplots(figsize=(10, 7))

    wtB_fine = np.linspace(0, 100, 500)
    xB_fine = (wtB_fine/B1) / (wtB_fine/B1 + (100-wtB_fine)/A1)
    T_liq_A = np.array([get_TA(1-x) for x in xB_fine])
    T_liq_B = np.array([get_TB(x) for x in xB_fine])

    # Plot lines above Eutectic Temperature
    ax1.plot(wtB_fine[T_liq_A >= TE], T_liq_A[T_liq_A >= TE], 'b-', lw=2, label=f'Liquidous {A_name}')
    ax1.plot(wtB_fine[T_liq_B >= TE], T_liq_B[T_liq_B >= TE], 'r-', lw=2, label=f'Liquidous {B_name}')
    ax1.axhline(y=TE, color='black', linestyle='--', alpha=0.6)
    ax1.scatter(wtB_e, TE, color='black', zorder=5)

    # Annotation
    ax1.annotate(f"Eutectic: {wtB_e:.1f} wt%, {TE:.1f} °C\n$x_B$ = {xB_e:.3f}", 
                 xy=(wtB_e, TE), xytext=(wtB_e, TE+30),
                 ha='center', arrowprops=dict(arrowstyle='->'))

    ax1.set_xlim(0, 100)
    ax1.set_ylim(TE - 100, max(A2, B2) + 50)
    ax1.set_xlabel(f"Weight Percent of {B_name} (wt%)", fontweight='bold')
    ax1.set_ylabel("Temperature (°C)", fontweight='bold')

    # Dual Axis Logic
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    xB_ticks = np.linspace(0, 1, 6)
    wtB_ticks = (xB_ticks * B1) / (xB_ticks * B1 + (1 - xB_ticks) * A1) * 100
    ax2.set_xticks(wtB_ticks)
    ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
    ax2.set_xlabel(f"Mole Fraction of {B_name} ($x_B$)", fontweight='bold')

    ax1.grid(True, ls=':', alpha=0.6)
    ax1.legend()

    # 5. Display Plot
    st.pyplot(fig)

    # 6. Numerical Results Display
    st.subheader("Numerical Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Eutectic Temperature (TE)", f"{TE:.2f} °C")
    col2.metric("Eutectic wt%", f"{wtB_e:.2f} %")
    col3.metric("Eutectic Mole Frac (xB)", f"{xB_e:.3f}")
else:
    st.info("Adjust the parameters on the sidebar and click 'Update Plot' to see the results.")
