import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os
import threading
import requests
# 添加父目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.gdp_client import GdpClient
from ui.charts import GDPChart

class GdpApp:
    def __init__(self, master):
        self.master = master
        self.master.title("GDP Analyzer")
        self.master.geometry("1000x800")
        self.master.configure(bg="#f0f0f0")
        
        self.gdp_client = GdpClient()
        self.countries_data = []  # 存储国家数据
        self.country_names = []   # 存储国家名称
        
        # 创建界面基本元素
        self.create_widgets()
        
        # 在单独的线程中加载国家列表，避免界面卡顿
        self.load_countries_thread = threading.Thread(target=self.load_countries)
        self.load_countries_thread.daemon = True
        self.load_countries_thread.start()
        
    def load_countries(self):
        """加载国家列表"""
        self.status_var.set("正在加载国家列表...")
        self.progressbar.start()
        
        url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
        try:
            response = self.gdp_client.base_url.replace("/v2/", "")  # 这里使用一个技巧来获取基本URL
            response = requests.get(url)
            data = response.json()
            
            if data and len(data) >= 2:
                # 按国家名称排序
                self.countries_data = sorted(data[1], key=lambda x: x['name'])
                self.country_names = [country['name'] for country in self.countries_data]
                
                # 更新下拉菜单
                self.master.after(0, self.update_country_combobox)
        except Exception as e:
            self.master.after(0, lambda: self.status_var.set(f"加载国家列表失败: {str(e)}"))
        
        self.master.after(0, self.progressbar.stop)
        
    def update_country_combobox(self):
        """更新国家下拉菜单"""
        self.country_combobox['values'] = self.country_names
        if 'China' in self.country_names:
            self.country_combobox.current(self.country_names.index('China'))
        elif len(self.country_names) > 0:
            self.country_combobox.current(0)
        self.status_var.set(f"已加载 {len(self.country_names)} 个国家")
        
    def create_widgets(self):
        # 创建顶部框架用于输入
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        # 国家下拉菜单
        ttk.Label(input_frame, text="国家名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.country_var = tk.StringVar()
        self.country_combobox = ttk.Combobox(input_frame, textvariable=self.country_var, width=30)
        self.country_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.country_combobox['values'] = ["加载中..."]  # 初始状态
        self.country_combobox.current(0)
        
        # 年份范围
        ttk.Label(input_frame, text="起始年份:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.start_year = ttk.Spinbox(input_frame, from_=1960, to=2023, width=10)
        self.start_year.grid(row=0, column=3, padx=5, pady=5)
        self.start_year.insert(0, "1990")
        
        ttk.Label(input_frame, text="结束年份:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.end_year = ttk.Spinbox(input_frame, from_=1960, to=2023, width=10)
        self.end_year.grid(row=0, column=5, padx=5, pady=5)
        self.end_year.insert(0, "2022")
        
        # 搜索按钮
        self.search_button = ttk.Button(input_frame, text="查询", command=self.fetch_data)
        self.search_button.grid(row=0, column=6, padx=10, pady=5)
        
        # 进度条
        self.progressbar = ttk.Progressbar(self.master, orient="horizontal", length=980, mode="indeterminate")
        self.progressbar.pack(pady=5)
        
        # 创建图表框架
        self.chart_frame = ttk.Frame(self.master)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        self.statusbar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def get_country_code(self, country_name):
        for country in self.countries_data:
            if country['name'] == country_name:
                return country['id']
        return None
        
    def fetch_data(self):
        # 清除现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        country_name = self.country_var.get()
        if country_name == "加载中...":
            messagebox.showinfo("提示", "国家列表正在加载中，请稍后再试")
            return
            
        try:
            start_year = int(self.start_year.get())
            end_year = int(self.end_year.get())
        except ValueError:
            messagebox.showerror("输入错误", "年份必须是有效的数字")
            return
            
        if start_year >= end_year:
            messagebox.showerror("输入错误", "起始年份必须小于结束年份")
            return
            
        self.status_var.set(f"正在获取 {country_name} 的GDP数据...")
        self.progressbar.start()
        
        # 获取国家代码
        country_code = self.get_country_code(country_name)
        if not country_code:
            # 如果从缓存中找不到，尝试通过API查询
            country_code = self.gdp_client.get_country_code(country_name)
            
        if not country_code:
            self.progressbar.stop()
            self.status_var.set("准备就绪")
            messagebox.showerror("错误", f"找不到国家: {country_name}")
            return
            
        # 获取GDP数据
        years, gdp_values = self.gdp_client.get_gdp_data(country_code, start_year, end_year)
        
        # 获取人均GDP数据
        per_capita_years, per_capita_values = self.gdp_client.get_gdp_per_capita_data(country_code, start_year, end_year)
        
        if not years or not gdp_values:
            self.progressbar.stop()
            self.status_var.set("准备就绪")
            messagebox.showwarning("警告", f"找不到 {country_name} 在指定年份的GDP数据")
            return
            
        # 创建并显示图表
        chart = GDPChart(country_name, years, gdp_values, per_capita_years, per_capita_values)
        figure = chart.create_figure()
        
        canvas = FigureCanvasTkAgg(figure, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.progressbar.stop()
        self.status_var.set(f"显示 {country_name} 的GDP数据 ({start_year}-{end_year})")

def run_app():
    import requests
    
    root = tk.Tk()
    app = GdpApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()