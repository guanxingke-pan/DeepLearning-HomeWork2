import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GDPChart:
    def __init__(self, country_name, years=None, gdp_values=None, 
                 per_capita_years=None, per_capita_values=None,
                 cpi_years=None, cpi_values=None):
        self.country_name = country_name
        self.years = years
        self.gdp_values = gdp_values
        self.per_capita_years = per_capita_years
        self.per_capita_values = per_capita_values
        self.cpi_years = cpi_years
        self.cpi_values = cpi_values
    
    def plot_gdp(self):
        plt.figure(figsize=(12, 8))
        
        # GDP总量
        if self.years and self.gdp_values:
            plt.subplot(2, 1, 1)
            plt.plot(self.years, self.gdp_values, marker='o', color='blue', linewidth=2)
            plt.title(f'GDP of {self.country_name} ({min(self.years)}-{max(self.years)})')
            plt.xlabel('Year')
            plt.ylabel('GDP (current US$)')
            plt.grid(True, alpha=0.3)
            
            # 格式化y轴为十亿美元
            plt.ticklabel_format(axis='y', style='plain')
            ax = plt.gca()
            ax.get_yaxis().set_major_formatter(
                plt.FuncFormatter(lambda x, loc: f"${x/1e9:.1f}B"))
            
            plt.xticks(rotation=45)
        
        # 人均GDP
        if self.per_capita_years and self.per_capita_values:
            plt.subplot(2, 1, 2)
            plt.plot(self.per_capita_years, self.per_capita_values, marker='s', color='green', linewidth=2)
            plt.title(f'GDP per Capita of {self.country_name} ({min(self.per_capita_years)}-{max(self.per_capita_years)})')
            plt.xlabel('Year')
            plt.ylabel('GDP per Capita (current US$)')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()

    def create_figure(self):
        """创建包含GDP和人均GDP数据的图表"""
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        
        # 添加GDP子图
        if self.years and self.gdp_values:
            ax1 = fig.add_subplot(211)
            ax1.plot(self.years, self.gdp_values, 'b-', marker='o')
            ax1.set_title(f"{self.country_name} GDP趋势")
            ax1.set_xlabel("年份")
            ax1.set_ylabel("GDP (美元)")
            ax1.grid(True)
        
        # 添加人均GDP子图
        if self.per_capita_years and self.per_capita_values:
            ax2 = fig.add_subplot(212)
            ax2.plot(self.per_capita_years, self.per_capita_values, 'g-', marker='s')
            ax2.set_title(f"{self.country_name} 人均GDP趋势")
            ax2.set_xlabel("年份")
            ax2.set_ylabel("人均GDP (美元)")
            ax2.grid(True)
        
        fig.tight_layout()
        return fig
    
    def create_cpi_figure(self):
        """创建CPI数据图表"""
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        
        if self.cpi_years and self.cpi_values:
            ax = fig.add_subplot(111)
            ax.plot(self.cpi_years, self.cpi_values, 'r-', marker='^')
            ax.set_title(f"{self.country_name} 通货膨胀率(CPI)趋势")
            ax.set_xlabel("年份")
            ax.set_ylabel("通胀率 (%)")
            
            # 添加零线以便于区分正负通胀
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            
            # 为高通胀区域添加红色背景
            ax.fill_between(self.cpi_years, self.cpi_values, 0, 
                           where=[v > 5 for v in self.cpi_values],
                           color='red', alpha=0.2, label='高通胀')
            
            # 为低通胀/通缩区域添加蓝色背景
            ax.fill_between(self.cpi_years, self.cpi_values, 0,
                           where=[v < 0 for v in self.cpi_values],
                           color='blue', alpha=0.2, label='通货紧缩')
            
            ax.grid(True)
            ax.legend()
        
        return fig
    
    def create_combined_figure(self):
        """创建包含GDP、人均GDP和CPI的组合图表"""
        fig = plt.Figure(figsize=(10, 12), dpi=100)
        
        # 添加GDP子图
        if self.years and self.gdp_values:
            ax1 = fig.add_subplot(311)
            ax1.plot(self.years, self.gdp_values, 'b-', marker='o')
            ax1.set_title(f"{self.country_name} GDP趋势")
            ax1.set_xlabel("年份")
            ax1.set_ylabel("GDP (美元)")
            ax1.grid(True)
        
        # 添加人均GDP子图
        if self.per_capita_years and self.per_capita_values:
            ax2 = fig.add_subplot(312)
            ax2.plot(self.per_capita_years, self.per_capita_values, 'g-', marker='s')
            ax2.set_title(f"{self.country_name} 人均GDP趋势")
            ax2.set_xlabel("年份")
            ax2.set_ylabel("人均GDP (美元)")
            ax2.grid(True)
        
        # 添加CPI子图
        if self.cpi_years and self.cpi_values:
            ax3 = fig.add_subplot(313)
            ax3.plot(self.cpi_years, self.cpi_values, 'r-', marker='^')
            ax3.set_title(f"{self.country_name} 通货膨胀率(CPI)趋势")
            ax3.set_xlabel("年份")
            ax3.set_ylabel("通胀率 (%)")
            ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax3.grid(True)
        
        fig.tight_layout()
        return fig