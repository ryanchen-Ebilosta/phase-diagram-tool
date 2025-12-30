import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from core_logic import calculate_phase_data # 导入逻辑

class PhaseDiagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phase Diagram Tool (Local)")
        self.root.geometry("1000x650")
        
        # 界面布局 (简化展示)
        self.input_frame = tk.Frame(self.root, padx=20, pady=20)
        self.input_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.entries = {}
        for label in ["A1", "A2", "A3", "B1", "B2", "B3"]:
            tk.Label(self.input_frame, text=label).pack()
            e = tk.Entry(self.input_frame)
            e.insert(0, "100") # 默认值
            e.pack()
            self.entries[label] = e
            
        tk.Button(self.input_frame, text="Generate Plot", command=self.plot).pack(pady=10)
        tk.Button(self.input_frame, text="Save (300 DPI)", command=self.save).pack()

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def plot(self):
        # 1. 调用核心逻辑
        vals = [float(self.entries[k].get()) for k in ["A1", "A2", "A3", "B1", "B2", "B3"]]
        res = calculate_phase_data(*vals)
        
        # 2. 绘图 (逻辑同前，调用 res['get_TA'] 等)
        self.ax.clear()
        # ... (此处省略具体的 ax.plot 代码，保持之前的逻辑)
        self.canvas.draw()

    def save(self):
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path: self.fig.savefig(path, dpi=300)

if __name__ == "__main__":
    root = tk.Tk()
    PhaseDiagramApp(root)
    root.mainloop()