import numpy as np
from scipy.optimize import fsolve

def calculate_phase_data(A1, A2, A3, B1, B2, B3):
    """
    输入: 分子量(1), 熔点(2), 熔化焓(3)
    返回: 计算函数和关键点坐标
    """
    # 液相线方程 TA
    def get_TA(xA):
        if xA <= 1e-9: return -273.15
        return 1 / (1 / (A2 + 273.15) - 8.314 * np.log(xA) / (A3 * 1000)) - 273.15

    # 液相线方程 TB
    def get_TB(xB):
        if xB <= 1e-9: return -273.15
        return 1 / (1 / (B2 + 273.15) - 8.314 * np.log(xB) / (B3 * 1000)) - 273.15

    # 求解共晶点 (TA = TB)
    xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
    TE = get_TA(1 - xB_e)
    
    # 换算质量百分数 wt%
    wtB_e = (xB_e * B1) / (xB_e * B1 + (1 - xB_e) * A1) * 100
    
    return {
        "get_TA": get_TA,
        "get_TB": get_TB,
        "xB_e": xB_e,
        "TE": TE,
        "wtB_e": wtB_e
    }