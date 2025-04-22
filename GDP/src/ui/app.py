import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os
import threading
import requests

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

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
        self.all_country_names = []  # 存储完整的国家名称列表（用于过滤）
        self.data_type_var = tk.StringVar(value="GDP")  # 默认显示GDP数据
        self.comparison_mode_var = tk.BooleanVar(value=False)  # 是否启用比较模式
        
        self.create_widgets()
        
        self.load_countries_thread = threading.Thread(target=self.load_countries)
        self.load_countries_thread.daemon = True
        self.load_countries_thread.start()
        
    def load_countries(self):
        self.status_var.set("正在加载国家列表...")
        self.progressbar.start()
        
        url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
        try:
            response = requests.get(url)
            data = response.json()
            
            if data and len(data) >= 2:
                # 按国家名称排序
                self.countries_data = sorted(data[1], key=lambda x: x['name'])
                self.country_names = [country['name'] for country in self.countries_data]
                self.all_country_names = self.country_names.copy()  # 保存完整列表
                
                # 更新下拉菜单
                self.master.after(0, self.update_country_combobox)
        except Exception as e:
            self.master.after(0, lambda: self.status_var.set(f"加载国家列表失败: {str(e)}"))
        
        self.master.after(0, self.progressbar.stop)
        
    def update_country_combobox(self):
        self.country_combobox['values'] = self.country_names
        self.country2_combobox['values'] = self.country_names
        
        if 'China' in self.country_names:
            self.country_combobox.current(self.country_names.index('China'))
            
            # 第二个默认为美国
            if 'United States' in self.country_names:
                self.country2_combobox.current(self.country_names.index('United States'))
            else:
                self.country2_combobox.current(0)
        elif len(self.country_names) > 0:
            self.country_combobox.current(0)
            if len(self.country_names) > 1:
                self.country2_combobox.current(1)
            else:
                self.country2_combobox.current(0)
                
        self.status_var.set(f"已加载 {len(self.country_names)} 个国家")
        
    def filter_countries(self, event=None, combobox=None, var=None):
        if not combobox or not var:
            return
            
        value = var.get().lower()
        if value == '':
            # 如果输入为空，显示所有国家
            combobox['values'] = self.all_country_names
        else:
            # 否则过滤国家名称
            filtered_countries = [country for country in self.all_country_names if value in country.lower()]
            combobox['values'] = filtered_countries
            
        combobox.event_generate('<Down>')
        
    def toggle_comparison_mode(self):
        comparison_mode = self.comparison_mode_var.get()
        if comparison_mode:
            self.country2_label.grid()
            self.country2_combobox.grid()
        else:
            self.country2_label.grid_remove()
            self.country2_combobox.grid_remove()
        
    def create_widgets(self):
        # 创建顶部框架用于输入
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        # 比较模式开关
        comparison_frame = ttk.Frame(self.master, padding="5")
        comparison_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.comparison_checkbox = ttk.Checkbutton(
            comparison_frame, 
            text="启用双国家比较", 
            variable=self.comparison_mode_var,
            command=self.toggle_comparison_mode
        )
        self.comparison_checkbox.pack(side=tk.LEFT, padx=10)
        
        # 国家选择区域
        country_frame = ttk.Frame(self.master, padding="5")
        country_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 第一个国家
        ttk.Label(country_frame, text="国家名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.country_var = tk.StringVar()
        self.country_combobox = ttk.Combobox(country_frame, textvariable=self.country_var, width=30)
        self.country_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.country_combobox['values'] = ["加载中..."]  # 初始状态
        self.country_combobox.current(0)
        
        self.country_combobox.bind('<KeyRelease>', lambda e: self.filter_countries(e, self.country_combobox, self.country_var))
        
        self.country2_label = ttk.Label(country_frame, text="比较国家:")
        self.country2_label.grid(row=0, column=2, padx=(20, 5), pady=5, sticky=tk.W)
        self.country2_var = tk.StringVar()
        self.country2_combobox = ttk.Combobox(country_frame, textvariable=self.country2_var, width=30)
        self.country2_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.country2_combobox['values'] = ["加载中..."]
        self.country2_combobox.current(0)

        self.country2_combobox.bind('<KeyRelease>', lambda e: self.filter_countries(e, self.country2_combobox, self.country2_var))
        
        self.country2_label.grid_remove()
        self.country2_combobox.grid_remove()
        
        year_frame = ttk.Frame(self.master, padding="5")
        year_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(year_frame, text="起始年份:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_year = ttk.Spinbox(year_frame, from_=1960, to=2023, width=10)
        self.start_year.grid(row=0, column=1, padx=5, pady=5)
        self.start_year.insert(0, "1990")
        
        ttk.Label(year_frame, text="结束年份:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.end_year = ttk.Spinbox(year_frame, from_=1960, to=2023, width=10)
        self.end_year.grid(row=0, column=3, padx=5, pady=5)
        self.end_year.insert(0, "2022")
        
        data_frame = ttk.Frame(self.master)
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(data_frame, text="数据类型:").pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Radiobutton(data_frame, text="GDP", variable=self.data_type_var, value="GDP").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Radiobutton(data_frame, text="人均GDP", variable=self.data_type_var, value="GDP_PER_CAPITA").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Radiobutton(data_frame, text="CPI", variable=self.data_type_var, value="CPI").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Radiobutton(data_frame, text="全部", variable=self.data_type_var, value="ALL").pack(side=tk.LEFT, padx=10, pady=5)
        
        self.search_button = ttk.Button(data_frame, text="查询", command=self.fetch_data)
        self.search_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.progressbar = ttk.Progressbar(self.master, orient="horizontal", length=980, mode="indeterminate")
        self.progressbar.pack(pady=5)
        
        self.chart_frame = ttk.Frame(self.master)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        

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
        
        # 获取第一个国家
        country_name = self.country_var.get()
        if country_name == "加载中...":
            messagebox.showinfo("提示", "国家列表正在加载中，请稍后再试")
            return
            
        if not self.all_country_names or country_name not in self.all_country_names:
            matching_countries = [c for c in self.all_country_names if country_name.lower() in c.lower()]
            if matching_countries:
                country_name = matching_countries[0]
                self.country_var.set(country_name)
        
        comparison_mode = self.comparison_mode_var.get()
        country2_name = None
        
        if comparison_mode:
            country2_name = self.country2_var.get()
            if not self.all_country_names or country2_name not in self.all_country_names:
                matching_countries = [c for c in self.all_country_names if country2_name.lower() in c.lower()]
                if matching_countries:
                    country2_name = matching_countries[0]
                    self.country2_var.set(country2_name)
            
        try:
            start_year = int(self.start_year.get())
            end_year = int(self.end_year.get())
        except ValueError:
            messagebox.showerror("输入错误", "年份必须是有效的数字")
            return
            
        if start_year >= end_year:
            messagebox.showerror("输入错误", "起始年份必须小于结束年份")
            return
            
        data_type = self.data_type_var.get()
        
        if comparison_mode:
            self.status_var.set(f"正在获取 {country_name} 和 {country2_name} 的数据...")
        else:
            self.status_var.set(f"正在获取 {country_name} 的数据...")
        
        self.progressbar.start()
        
        country_code = self.get_country_code(country_name)
        if not country_code:
            country_code = self.gdp_client.get_country_code(country_name)
            
        if not country_code:
            self.progressbar.stop()
            self.status_var.set("准备就绪")
            messagebox.showerror("错误", f"找不到国家: {country_name}")
            return
        
        country2_code = None
        if comparison_mode:
            country2_code = self.get_country_code(country2_name)
            if not country2_code:
                country2_code = self.gdp_client.get_country_code(country2_name)
                
            if not country2_code:
                self.progressbar.stop()
                self.status_var.set("准备就绪")
                messagebox.showerror("错误", f"找不到国家: {country2_name}")
                return
        
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        
        if data_type in ["GDP", "ALL"]:
            years1, gdp_values1 = self.gdp_client.get_gdp_data(country_code, start_year, end_year)
            
            years2, gdp_values2 = [], []
            if comparison_mode:
                years2, gdp_values2 = self.gdp_client.get_gdp_data(country2_code, start_year, end_year)
            
            if years1 and gdp_values1 or (comparison_mode and years2 and gdp_values2):
                ax1 = fig.add_subplot(111 if data_type != "ALL" else 311)
                
                if years1 and gdp_values1:
                    ax1.plot(years1, gdp_values1, 'b-', marker='o', label=f'{country_name} GDP')
                
                if comparison_mode and years2 and gdp_values2:
                    ax1.plot(years2, gdp_values2, 'r-', marker='s', label=f'{country2_name} GDP')
                
                title = f"GDP趋势 ({start_year}-{end_year})"
                if not comparison_mode:
                    title = f"{country_name} " + title
                    
                ax1.set_title(title)
                ax1.set_xlabel("年份")
                ax1.set_ylabel("GDP (美元)")
                ax1.grid(True)
                ax1.legend()
            elif data_type == "GDP":
                self.progressbar.stop()
                self.status_var.set("准备就绪")
                messagebox.showwarning("警告", f"找不到所选国家在指定年份的GDP数据")
                return
        
        if data_type in ["GDP_PER_CAPITA", "ALL"]:
            per_capita_years1, per_capita_values1 = self.gdp_client.get_gdp_per_capita_data(country_code, start_year, end_year)
            
            per_capita_years2, per_capita_values2 = [], []
            if comparison_mode:
                per_capita_years2, per_capita_values2 = self.gdp_client.get_gdp_per_capita_data(country2_code, start_year, end_year)
            
            if per_capita_years1 and per_capita_values1 or (comparison_mode and per_capita_years2 and per_capita_values2):
                ax2 = fig.add_subplot(111 if data_type != "ALL" else 312)
                
                if per_capita_years1 and per_capita_values1:
                    ax2.plot(per_capita_years1, per_capita_values1, 'g-', marker='s', label=f'{country_name} 人均GDP')
                
                if comparison_mode and per_capita_years2 and per_capita_values2:
                    ax2.plot(per_capita_years2, per_capita_values2, 'm-', marker='d', label=f'{country2_name} 人均GDP')
                
                title = f"人均GDP趋势 ({start_year}-{end_year})"
                if not comparison_mode:
                    title = f"{country_name} " + title
                    
                ax2.set_title(title)
                ax2.set_xlabel("年份")
                ax2.set_ylabel("人均GDP (美元)")
                ax2.grid(True)
                ax2.legend()
            elif data_type == "GDP_PER_CAPITA":
                self.progressbar.stop()
                self.status_var.set("准备就绪")
                messagebox.showwarning("警告", f"找不到所选国家在指定年份的人均GDP数据")
                return
        
        if data_type in ["CPI", "ALL"]:
            cpi_years1, cpi_values1 = self.gdp_client.get_cpi_data(country_code, start_year, end_year)
            
            cpi_years2, cpi_values2 = [], []
            if comparison_mode:
                cpi_years2, cpi_values2 = self.gdp_client.get_cpi_data(country2_code, start_year, end_year)
            
            if cpi_years1 and cpi_values1 or (comparison_mode and cpi_years2 and cpi_values2):
                ax3 = fig.add_subplot(111 if data_type != "ALL" else 313)
                
                if cpi_years1 and cpi_values1:
                    ax3.plot(cpi_years1, cpi_values1, 'r-', marker='^', label=f'{country_name} CPI')
                
                if comparison_mode and cpi_years2 and cpi_values2:
                    ax3.plot(cpi_years2, cpi_values2, 'c-', marker='x', label=f'{country2_name} CPI')
                
                title = f"CPI趋势 ({start_year}-{end_year})"
                if not comparison_mode:
                    title = f"{country_name} " + title
                    
                ax3.set_title(title)
                ax3.set_xlabel("年份")
                ax3.set_ylabel("CPI (%)")
                ax3.grid(True)
                ax3.legend()
            elif data_type == "CPI":
                self.progressbar.stop()
                self.status_var.set("准备就绪")
                messagebox.showwarning("警告", f"找不到所选国家在指定年份的CPI数据")
                return
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.progressbar.stop()
        if comparison_mode:
            self.status_var.set(f"显示 {country_name} 和 {country2_name} 的数据对比 ({start_year}-{end_year})")
        else:
            self.status_var.set(f"显示 {country_name} 的数据 ({start_year}-{end_year})")

def run_app():
    root = tk.Tk()
    app = GdpApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()