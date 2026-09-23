import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import fsolve
import streamlit as st

# ==================== 1. 页面基本配置 ====================
st.set_page_config(
    page_title='二元相图计算与实验比对系统', page_icon='🔬', layout='wide'
)

st.title('🔬 二元相图理论计算与实验数据比对系统')
st.markdown(
    '基于热力学模型（理想/正规溶液）计算二元共晶体系理论相图，并支持一键联查 FACT-Web 权威实验数据库。'
)


# ==================== 2. 加载数据库（带缓存） ====================
@st.cache_data
def load_databases():
  # 加载理论计算参数数据库
  df_main = pd.read_excel('database.xlsx')
  # 加载实验相图链接数据库
  df_link = pd.read_excel('diagram_link.xlsx')
  return df_main, df_link


try:
  df, link_df = load_databases()
except Exception as e:
  st.error(
      f'❌ 加载 Excel 文件失败，请检查文件是否存在于 GitHub 根目录！错误信息: {e}'
  )
  st.stop()


# ==================== 3. 定义双向匹配查找函数 ====================
def get_fact_url(comp_a, comp_b, link_df):
  """支持顺序无关（A-B 与 B-A 互换）匹配链接的查找函数"""
  name1 = f'{comp_a}-{comp_b}'
  name2 = f'{comp_b}-{comp_a}'
  matched = link_df[link_df['Names'].isin([name1, name2])]
  if not matched.empty:
    return matched.iloc[0]['Ref_URL']
  return None


# ==================== 4. 侧边栏：系统参数与组分选择 ====================
st.sidebar.header('⚙️ 体系参数设置')

# 检查 database.xlsx 中是否有 'Name' 列
if 'Name' not in df.columns:
  st.error("错误：'database.xlsx' 表格中缺少 'Name' 列！")
  st.stop()

component_list = df['Name'].dropna().unique().tolist()

if len(component_list) < 2:
  st.error("'database.xlsx' 中的有效组分少于 2 个，无法构成二元体系。")
  st.stop()

# 下拉菜单选择组分 A 和 组分 B
comp_a = st.sidebar.selectbox('选择组分 A', component_list, index=0)
comp_b = st.sidebar.selectbox(
    '选择组分 B', component_list, index=1 if len(component_list) > 1 else 0
)

if comp_a == comp_b:
  st.sidebar.warning('⚠️ 组分 A 和组分 B 不能相同，请选择不同的组分。')

# 模型选择
model_type = st.sidebar.radio(
    '选择热力学模型', ['理想溶液模型 (Ideal Solution)', '正规溶液模型 (Regular Solution)']
)


# ==================== 5. 主界面：左右分栏布局 ====================
st.markdown('---')
col_plot, col_control = st.columns([2, 1])

# --- 左侧：理论计算与相图绘制 ---
with col_plot:
  st.subheader(f'📈 {comp_a} - {comp_b} 理论相图计算结果')

  # 提取当前组分在表格中的对应行数据（若有熔点等参数可在此处提取）
  row_a = df[df['Name'] == comp_a]
  row_b = df[df['Name'] == comp_b]

  # 绘制相图核心逻辑 (可替换为您原有的详细计算与 fsolve 代码)
  fig, ax = plt.subplots(figsize=(8, 6))

  x = np.linspace(0, 1, 100)
  # 模拟示意液相线计算（实际会调用您的热力学公式）
  T_a = 1000.0  # 默认值或从 row_a 读取
  T_b = 800.0  # 默认值或从 row_b 读取
  T_liquidus_A = T_a - 200 * x
  T_liquidus_B = T_b - 150 * (1 - x)

  ax.plot(x, T_liquidus_A, label=f'{comp_a} 液相线', color='blue', linewidth=2)
  ax.plot(
      x, T_liquidus_B, label=f'{comp_b} 液相线', color='orange', linewidth=2
  )
  ax.set_xlabel('组分 B 摩尔分数 ($x_B$)', fontsize=12)
  ax.set_ylabel('温度 ($K$)', fontsize=12)
  ax.set_title(
      f'{comp_a} - {comp_b} 二元共晶相图 ({model_type})', fontsize=14
  )
  ax.legend()
  ax.grid(True, linestyle='--', alpha=0.6)

  st.pyplot(fig)

# --- 右侧：实验相图互动调阅栏 ---
with col_control:
  st.subheader('🔍 实验对照与文献库')

  st.markdown(
      '通过下方按钮，您可以直接跳转至国际权威热力学数据库（FACT-Web）调阅该二元体系的**标准评定实验相图**，与左侧理论计算结果进行交叉比对。'
  )

  st.markdown('---')

  # 调用双向匹配函数查找链接
  fact_url = get_fact_url(comp_a, comp_b, link_df)

  if fact_url:
    st.success(f'✅ 已成功匹配 **{comp_a} - {comp_b}** 实验相图！')
    # 核心新增功能：打开外部实验相图网页的互动按钮
    st.link_button(
        f'🌐 在 FACT-Web 中打开标准相图',
        fact_url,
        use_container_width=True,
    )
  else:
    st.warning(
        f'💡 提示：当前本地评定数据库中暂未收录 **{comp_a} - {comp_b}**'
        ' 的直接对照链接。'
    )

  st.markdown('---')
  st.markdown('**当前仿真状态摘要**：')
  st.info(
      f'- **当前体系**: `{comp_a}` — `{comp_b}`\n- **计算模型**: `{model_type}`'
  )
