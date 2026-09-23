import os
import pandas as pd

def match_compounds_with_pic(base_folder):
    pic_dir = os.path.join(base_folder, "pic")
    
    if not os.path.exists(pic_dir):
        print(f"错误：目录 {pic_dir} 不存在！")
        return
        
    # 严格按照第二张图片中给出的化合物顺序建立列表
    compound_list = [
        "Ag", "As", "Au", "Bi", "Cd", "CeCl3", "CsBr", "CsF", "Ge", 
        "KBr", "KCl", "KF", "LaCl3", "LiBr", "LiCl", "LiF", "LiNO3", 
        "MgCl2", "MgF2", "NaBr", "NaCl", "NaF", "NaI", "PbCl2", 
        "RbBr", "RbF", "Sb", "Si", "SrF2", "Zn"
    ]
    
    # 用于存储每个化合物对应的所有配对组分
    pair_map = {comp: set() for comp in compound_list}
    
    print(f"正在扫描目录: {pic_dir} 并提取配对关系...")
    file_list = os.listdir(pic_dir)
    
    for filename in file_list:
        file_path = os.path.join(pic_dir, filename)
        if os.path.isfile(file_path):
            # 去掉后缀名（如 .png）
            name_no_ext, _ = os.path.splitext(filename)
            # 按 "-" 拆分文件名中的各个组分
            parts = [p.strip() for p in name_no_ext.split('-') if p.strip()]
            
            # 如果文件名包含两个或以上组分（如二元系 A-B）
            if len(parts) >= 2:
                for i, p1 in enumerate(parts):
                    if p1 in pair_map:
                        for j, p2 in enumerate(parts):
                            if i != j:
                                pair_map[p1].add(p2)
                                
    # 将结果整理为行数据，计算最大配对列数以对齐表格
    rows = []
    max_pairs = 0
    
    for comp in compound_list:
        # 排序以保持整洁
        pairs = sorted(list(pair_map[comp]))
        row = [comp] + pairs
        rows.append(row)
        if len(pairs) > max_pairs:
            max_pairs = len(pairs)
            
    # 动态构建列名（主化合物列 + 各个配对列）
    columns = ["化合物"] + [f"配对化合物{i+1}" for i in range(max_pairs)]
    
    # 补齐每一行的长度，确保转换为 DataFrame 时列数一致
    padded_rows = []
    for row in rows:
        while len(row) < len(columns):
            row.append("")
        padded_rows.append(row)
        
    df = pd.DataFrame(padded_rows, columns=columns)
    
    # 导出到 Excel
    output_excel_path = os.path.join(base_folder, "compound_pairs_matched.xlsx")
    df.to_excel(output_excel_path, index=False, engine='openpyxl')
    
    print(f"处理完成！表格已成功生成。")
    print(f"保存路径：\n{output_excel_path}")

if __name__ == "__main__":
    target_folder = r"D:\Phase-Figs"
    match_compounds_with_pic(target_folder)
