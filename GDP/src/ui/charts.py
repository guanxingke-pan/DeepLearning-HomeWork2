import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GDPChart:
    def __init__(self, country_name, years, gdp_values, per_capita_years=None, per_capita_values=None):
        self.country_name = country_name
        self.years = years
        self.gdp_values = gdp_values
        self.per_capita_years = per_capita_years
        self.per_capita_values = per_capita_values

    def plot_gdp(self):
        plt.figure(figsize=(12, 8))
        
        # GDP总量
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
        """创建图表而不显示，用于嵌入到GUI中"""
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # GDP图表
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(self.years, self.gdp_values, marker='o', color='blue', linewidth=2)
        ax1.set_title(f'GDP of {self.country_name} ({min(self.years)}-{max(self.years)})')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('GDP (current US$)')
        ax1.grid(True, alpha=0.3)
        
        # 格式化y轴为十亿美元
        ax1.ticklabel_format(axis='y', style='plain')
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, loc: f"${x/1e9:.1f}B"))
        
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)
        
        # 人均GDP图表
        if self.per_capita_years and self.per_capita_values:
            ax2 = fig.add_subplot(2, 1, 2)
            ax2.plot(self.per_capita_years, self.per_capita_values, marker='s', color='green', linewidth=2)
            ax2.set_title(f'GDP per Capita of {self.country_name} ({min(self.per_capita_years)}-{max(self.per_capita_years)})')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('GDP per Capita (current US$)')
            ax2.grid(True, alpha=0.3)
            
            for tick in ax2.get_xticklabels():
                tick.set_rotation(45)
        
        fig.tight_layout()
        return fig