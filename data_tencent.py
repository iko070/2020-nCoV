import time, requests, json
import csv
import codecs
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=&_=%d'%int(time.time()*1000)
data = json.loads(requests.get(url = url).json()['data'])

lis = []

for m in range(len(data['areaTree'][0]['children'])):
    for n in range(len(data['areaTree'][0]['children'][m]['children'])):
        info={}
        info['country']=data['areaTree'][0]['name']#国家
        info['province']=data['areaTree'][0]['children'][m]['name']#省份  
        info['city']=data['areaTree'][0]['children'][m]['children'][n]['name']#城市   len(data['areaTree'][0]['children'][0]['children'])
        info['total_confirm']=data['areaTree'][0]['children'][m]['children'][n]['total']['confirm']
        info['total_suspect']=data['areaTree'][0]['children'][m]['children'][n]['total']['suspect']
        info['total_dead']=data['areaTree'][0]['children'][m]['children'][n]['total']['dead']
        info['total_heal']=data['areaTree'][0]['children'][m]['children'][n]['total']['heal']
        info['today_confirm']=data['areaTree'][0]['children'][m]['children'][n]['today']['confirm']
        info['today_suspect']=data['areaTree'][0]['children'][m]['children'][n]['today']['suspect']
        info['today_dead']=data['areaTree'][0]['children'][m]['children'][n]['today']['dead']
        info['today_heal']=data['areaTree'][0]['children'][m]['children'][n]['today']['heal']
        lis.append(info)

def catch_distribution():
    """抓取行政区确诊分布"""
    
    data ={}
    for item in lis:
        
        if  item['province'] not in data:
            data.update({item['province']:0})
        data[item['province']] += int(item['total_confirm'])
    
    return data

def catch_daily():
    """抓取每日确诊和死亡数据"""
    
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_cn_day_counts&callback=&_=%d'%int(time.time()*1000)
    data = json.loads(requests.get(url=url).json()['data'])
    data.sort(key=lambda x:x['date'])
    
    date_list = list() # 日期
    confirm_list = list() # 确诊
    suspect_list = list() # 疑似
    dead_list = list() # 死亡
    heal_list = list() # 治愈
    for item in data:
        month, day = item['date'].split('/')
        date_list.append(datetime.strptime('2020-%s-%s'%(month, day), '%Y-%m-%d'))
        confirm_list.append(int(item['confirm']))
        suspect_list.append(int(item['suspect']))
        dead_list.append(int(item['dead']))
        heal_list.append(int(item['heal']))
    
    return date_list, confirm_list, suspect_list, dead_list, heal_list

def plot_daily():
    """每日确诊和死亡"""
    date_list, confirm_list, suspect_list, dead_list, heal_list = catch_daily() # 获取数据
    
    plt.figure('2019-nCoV疫情统计图表', facecolor='#f4f4f4', figsize=(10, 8))
    plt.title('2019-nCoV疫情曲线', fontsize=20)
    
    plt.plot(date_list, confirm_list, label='确诊')
    plt.plot(date_list, suspect_list, label='疑似')
    plt.plot(date_list, dead_list, label='死亡')
    plt.plot(date_list, heal_list, label='治愈')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d')) # 格式化时间轴标注
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.grid(linestyle=':') # 显示网格
    plt.legend(loc='best') # 显示图例
    #plt.savefig('2019-nCoV疫情曲线.png') # 保存为文件
    plt.show()

def daily_plotly():
    date_list, confirm_list, suspect_list, dead_list, heal_list = catch_daily() # 获取数据
    
    fig = go.Figure()
    
    fig.add_trace( go.Scatter(x = date_list, y = confirm_list, name = 'Confirmed'))
    fig.add_trace(go.Scatter(x = date_list, y = suspect_list, name = 'Suspected'))
    fig.add_trace(go.Scatter(x = date_list, y = dead_list, name = 'Deaths'))
    fig.add_trace(go.Scatter(x = date_list, y = heal_list, name = 'Recovered'))
    

    fig.update_layout(title = '2020-nCoV daily plot')
    
    fig.show()

from pyecharts.charts import Map
from pyecharts import options as opts

# 省和直辖市
province_distribution = catch_distribution()

# maptype='china' 只显示全国直辖市和省级
map = Map()
map.set_global_opts(
    title_opts=opts.TitleOpts(title="20200129 casses distribution"),
    visualmap_opts=opts.VisualMapOpts(max_=3600, is_piecewise=True,
                                      pieces=[
                                        {"max": 50000, "min": 1001, "label": ">1000", "color": "#8A0808"},
                                        {"max": 1000, "min": 500, "label": "500-1000", "color": "#B40404"},
                                        {"max": 499, "min": 100, "label": "100-499", "color": "#DF0101"},
                                        {"max": 99, "min": 10, "label": "10-99", "color": "#F78181"},
                                        {"max": 9, "min": 1, "label": "1-9", "color": "#F5A9A9"},
                                        {"max": 0, "min": 0, "label": "0", "color": "#FFFFFF"},
                                        ], )  #最大数据范围，分段
    )
map.add("20200129 casses distribution", data_pair=province_distribution.items(), maptype="china", is_roam=True)
map.render('20200129 casses distribution.html')

if __name__ == '__main__':
    plot_daily()
