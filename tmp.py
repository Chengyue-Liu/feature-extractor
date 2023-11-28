import random
from collections import Counter
from math import log10

import matplotlib.pyplot as plt


def plot_line_chart_from_list(data):
    counter = Counter(data)
    total = len(data)
    points = [(num, round((count / total) * 100, 2)) for num, count in counter.items()]

    # 将点按 x 坐标排序
    points.sort(key=lambda x: x[0])

    # 提取 x 和 y 坐标
    x_values, y_values = zip(*points)

    x_values = map(log10, x_values)
    # 绘制折线图
    plt.plot(x_values, y_values, label='折线图')

    # 添加标签和标题
    plt.title('折线图')
    plt.xlabel('X坐标')
    plt.ylabel('Y坐标')

    # 显示图例
    plt.legend()

    # 显示图形
    plt.show()


# 示例数据，格式为 [(x1, y1), (x2, y2), ...]
data = [0] * 230
data.extend([random.randint(0, 10) for i in range(2700)])
data.extend([random.randint(11, 100) for i in range(2000)])
data.extend([random.randint(101, 500) for i in range(5000)])
data.extend([random.randint(501, 1000) for i in range(5000)])
data.extend([random.randint(1001, 3000) for i in range(5000)])
data.extend([random.randint(3000, 30000) for i in range(3000)])
# data.extend([random.randint(30001, 300000) for i in range(300)])

plot_line_chart_from_list(data)
