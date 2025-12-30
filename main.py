import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import fsolve
import os

# 设置支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

class PhaseDiagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("二元金属相图分析工具 - CEJ投稿专用版")
        self.root.geometry("1200x750")

        # --- 左侧输入和控制栏 ---
        self.input_frame = tk.Frame(self.root, width=320, padx=20, pady=20, bg="#f5f5f5")
        self.input_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.inputs = {}
        self.create_input_fields()

        # 按钮区
        self.btn_draw = tk.Button(self.input_frame, text="1. 生成/更新相图", command=self.update_plot, 
                                  bg="#2c3e50", fg="white", font=('Arial', 11, 'bold'), pady=8)
        self.btn_draw.pack(fill=tk.X, pady=(20, 10))

        self.btn_save = tk.Button(self.input_frame, text="2. 保存高清图片 (300 DPI)", command=self.save_plot, 
                                  bg="#27ae60", fg="white", font=('Arial', 11, 'bold'), pady=8)
        self.btn_save.pack(fill=tk.X, pady=5)

        tk.Label(self.input_frame, text="* 自动保存格式支持: .png, .pdf, .tiff", bg="#f5f5f5", fg="gray").pack()

        # --- 右侧绘图区 ---
        self.plot_frame = tk.Frame(self.root, bg="white")
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 初始化Matplotlib画布
        self.fig, self.ax1 = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax2 = None # 顶部轴引用

    def create_input_fields(self):
        """创建输入表单"""
        fields = [
            ("组分 A 名称", "Sn"), ("A 分子量 (A1)", "118.7"), ("A 熔点 ℃ (A2)", "231.9"), ("A 摩尔熔化焓 kJ/mol (A3)", "7.0"),
            ("", ""), 
            ("组分 B 名称", "Pb"), ("B 分子量 (B1)", "207.2"), ("B 熔点 ℃ (B2)", "327.5"), ("B 摩尔熔化焓 kJ/mol (B3)", "4.77")
        ]
        
        for label_text, default_val in fields:
            if not label_text:
                tk.Frame(self.input_frame, height=15, bg="#f5f5f5").pack()
                continue
            lbl = tk.Label(self.input_frame, text=label_text, bg="#f5f5f5", font=('Arial', 10))
            lbl.pack(anchor=tk.W)
            entry = tk.Entry(self.input_frame, font=('Arial', 10))
            entry.insert(0, default_val)
            entry.pack(fill=tk.X, pady=2)
            self.inputs[label_text] = entry

    def calculate_logic(self):
        """核心计算逻辑"""
        try:
            A1, A2, A3 = float(self.inputs["A 分子量 (A1)"].get()), float(self.inputs["A 熔点 ℃ (A2)"].get()), float(self.inputs["A 摩尔熔化焓 kJ/mol (A3)"].get())
            B1, B2, B3 = float(self.inputs["B 分子量 (B1)"].get()), float(self.inputs["B 熔点 ℃ (B2)"].get()), float(self.inputs["B 摩尔熔化焓 kJ/mol (B3)"].get())
            A_name, B_name = self.inputs["组分 A 名称"].get(), self.inputs["组分 B 名称"].get()

            def get_TA(xA):
                if xA <= 1e-9: return -273.15
                return 1 / (1 / (A2 + 273.15) - 8.314 * np.log(xA) / (A3 * 1000)) - 273.15

            def get_TB(xB):
                if xB <= 1e-9: return -273.15
                return 1 / (1 / (B2 + 273.15) - 8.314 * np.log(xB) / (B3 * 1000)) - 273.15

            xB_e = fsolve(lambda xb: get_TA(1-xb) - get_TB(xb), 0.5)[0]
            TE = get_TA(1 - xB_e)
            wtB_e = (xB_e * B1) / (xB_e * B1 + (1 - xB_e) * A1) * 100

            return locals()
        except Exception as e:
            messagebox.showerror("错误", "请输入有效的数值！")
            return None

    def update_plot(self):
        d = self.calculate_logic()
        if not d: return

        self.ax1.clear()
        wtB = np.linspace(0, 100, 500)
        xB = (wtB/d['B1']) / (wtB/d['B1'] + (100-wtB)/d['A1'])
        
        T_A = np.array([d['get_TA'](1-x) for x in xB])
        T_B = np.array([d['get_TB'](x) for x in xB])

        # 绘图曲线
        self.ax1.plot(wtB[T_A >= d['TE']], T_A[T_A >= d['TE']], 'b-', lw=2, label=f'Liquidous {d["A_name"]}')
        self.ax1.plot(wtB[T_B >= d['TE']], T_B[T_B >= d['TE']], 'r-', lw=2, label=f'Liquidous {d["B_name"]}')
        self.ax1.axhline(y=d['TE'], color='black', lw=1.5, ls='--')
        self.ax1.scatter(d['wtB_e'], d['TE'], color='black', zorder=5)

        # 标注
        self.ax1.annotate(f"E: {d['wtB_e']:.1f} wt%, {d['TE']:.1f} °C\n$x_B$ = {d['xB_e']:.3f}", 
                         xy=(d['wtB_e'], d['TE']), xytext=(d['wtB_e'], d['TE']+30),
                         ha='center', arrowprops=dict(arrowstyle='->'), fontsize=10)

        # 坐标轴设置
        self.ax1.set_xlim(0, 100)
        self.ax1.set_ylim(d['TE'] - 100, max(d['A2'], d['B2']) + 50)
        self.ax1.set_xlabel(f"Weight Percent of {d['B_name']} (wt%)", fontweight='bold')
        self.ax1.set_ylabel("Temperature (°C)", fontweight='bold')

        # 处理双轴
        if self.ax2: self.ax2.remove()
        self.ax2 = self.ax1.twiny()
        self.ax2.set_xlim(self.ax1.get_xlim())
        xB_ticks = np.linspace(0, 1, 6)
        wtB_ticks = (xB_ticks * d['B1']) / (xB_ticks * d['B1'] + (1 - xB_ticks) * d['A1']) * 100
        self.ax2.set_xticks(wtB_ticks)
        self.ax2.set_xticklabels([f"{x:.1f}" for x in xB_ticks])
        self.ax2.set_xlabel(f"Mole Fraction of {d['B_name']} ($x_B$)", fontweight='bold')

        self.ax1.grid(True, ls=':', alpha=0.6)
        self.ax1.legend(frameon=False)
        self.fig.tight_layout()
        self.canvas.draw()

    def save_plot(self):
        """保存高清图片"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("TIFF files", "*.tiff"), ("All files", "*.*")],
            initialfile=f"Phase_Diagram_{self.inputs['组分 A 名称'].get()}_{self.inputs['组分 B 名称'].get()}"
        )
        if file_path:
            # 关键：设置 dpi=300 以上以满足期刊要求
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("保存成功", f"相图已成功保存至:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhaseDiagramApp(root)
    root.mainloop()