import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from core_logic import calculate_phase_data # 导入同样的逻辑

st.title("Online Phase Diagram Tool")

# 侧边栏输入
A1 = st.sidebar.number_input("A 分子量", 118.7)
A2 = st.sidebar.number_input("A 熔点", 231.9)
A3 = st.sidebar.number_input("A 熔化焓", 7.0)
B1 = st.sidebar.number_input("B 分子量", 207.2)
B2 = st.sidebar.number_input("B 熔点", 327.5)
B3 = st.sidebar.number_input("B 熔化焓", 4.77)

# 调用核心逻辑
res = calculate_phase_data(A1, A2, A3, B1, B2, B3)

# 绘图逻辑
fig, ax = plt.subplots()
# ... (使用 res['get_TA'] 等绘图)
st.pyplot(fig)

st.success(f"共晶点计算完成: {res['TE']:.2f} °C")