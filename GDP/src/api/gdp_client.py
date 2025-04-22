import requests
import json
from datetime import datetime

class GdpClient:
    """处理与World Bank API的通信，获取GDP和其他经济数据"""
    
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2/"
        
    def get_country_code(self, country_name):
        """获取国家代码"""
        url = f"{self.base_url}country?format=json&per_page=300"
        response = requests.get(url)
        data = response.json()
        
        if not data or len(data) < 2:
            return None
            
        countries = data[1]
        for country in countries:
            if country_name.lower() in country['name'].lower():
                return country['id']
        return None
    
    def get_gdp_data(self, country_code, start_year=1990, end_year=2022):
        """获取指定国家在给定年份范围内的GDP数据"""
        indicator = "NY.GDP.MKTP.CD"  # GDP (current US$)
        url = f"{self.base_url}country/{country_code}/indicator/{indicator}?format=json&date={start_year}:{end_year}&per_page=100"
        
        response = requests.get(url)
        data = response.json()
        
        if not data or len(data) < 2:
            return [], []
            
        # 数据排序（因为API返回的是倒序）
        data_points = data[1]
        data_points.sort(key=lambda x: x['date'])
        
        years = []
        values = []
        
        for point in data_points:
            if point['value'] is not None:
                years.append(int(point['date']))
                values.append(float(point['value']))
                
        return years, values
    
    def get_gdp_per_capita_data(self, country_code, start_year=1990, end_year=2022):
        """获取指定国家在给定年份范围内的人均GDP数据"""
        indicator = "NY.GDP.PCAP.CD"  # GDP per capita (current US$)
        url = f"{self.base_url}country/{country_code}/indicator/{indicator}?format=json&date={start_year}:{end_year}&per_page=100"
        
        response = requests.get(url)
        data = response.json()
        
        if not data or len(data) < 2:
            return [], []
            
        data_points = data[1]
        data_points.sort(key=lambda x: x['date'])
        
        years = []
        values = []
        
        for point in data_points:
            if point['value'] is not None:
                years.append(int(point['date']))
                values.append(float(point['value']))
                
        return years, values

    def get_cpi_data(self, country_code, start_year, end_year):
 
        # CPI指标代码: FP.CPI.TOTL.ZG (消费者价格指数，年度百分比变化)
        indicator = "FP.CPI.TOTL.ZG"
        
        url = f"{self.base_url}/country/{country_code}/indicator/{indicator}?format=json&date={start_year}:{end_year}&per_page=100"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if not data or len(data) < 2 or not data[1]:
                return [], []
                
            years = []
            cpi_values = []
            
            for item in reversed(data[1]):
                if item['value'] is not None:
                    years.append(int(item['date']))
                    cpi_values.append(float(item['value']))
                    
            return years, cpi_values
            
        except Exception as e:
            print(f"获取CPI数据出错: {str(e)}")
            return [], []