# -*- coding: UTF-8 -*-

"""
Author: mathstao
Project: https://github.com/Mathstao/Chat-Cluster/
"""

import pandas as pd
import numpy as np
from collections import Counter


# 返回指定类别的各天的样本数量
def get_date_data(data, topic, date_list):
    temp = data[data["summary"] == topic]
    k = {i: 0 for i in date_list}
    for i in range(len(temp)):
        k[int(temp.iat[i, 0][:8])] += 1
    return [k[i] for i in date_list]


def main(config):
    print("\n正在得到趋势图数据...\n")
    data = pd.read_excel(config["cluster_excel_file"])
    sorted_date_list = sorted(set([int(i[:8]) for i in data["id"]]))
    n_cluster_second = len(set(data["label"]))
    labels_second = list(data["label"])
    summary_list = [data[data["label"] == i].iat[0, 1] for i in range(n_cluster_second)]
    keyword_list = [data[data["label"] == i].iat[0, 2] for i in range(n_cluster_second)]

    # 统计汇总数据
    stat = []
    for i in range(n_cluster_second):
        stat.append([i, Counter(labels_second)[i], round(float(Counter(labels_second)[i])/len(data), 3), summary_list[i], keyword_list[i]])
    stat = sorted(stat, key=lambda x:x[2], reverse=True)

    # with open(config["cluster_result_file"], 'w') as f:
    #     f.write(u"label\tnumber\tpercent\tsummary\n")
    #     for s in stat:
    #         f.write(str(s[0]) + '\t\t' + str(s[1]) + '\t\t' + str(s[2]) + '\t\t' + str(s[3]) + '\n')

    trend_data = pd.DataFrame()
    trend_data.insert(0, column="label", value=[i for i in [s[0] for s in stat]])
    trend_data.insert(1, column="number", value=[i for i in [s[1] for s in stat]])
    trend_data.insert(2, column="percent", value=[i for i in [s[2] for s in stat]])
    trend_data.insert(3, column="summary", value=[i for i in [s[3] for s in stat]])
    trend_data.insert(4, column="keywords", value=[i for i in [s[4] for s in stat]])

    # 保存各类的统计数据
    trend_data.iloc[:,:4].to_excel(config["cluster_result_file"], index=False)

    date_data = np.zeros([n_cluster_second, len(sorted_date_list)])
    for i in range(n_cluster_second):
        date_data[i, :] = get_date_data(data, stat[i][3], sorted_date_list)
    for i, s in enumerate(sorted_date_list):
        trend_data.insert(i+5, column=s, value=date_data[:, i])
    trend_data.to_excel(config["trend_data_file"], index=False)
    print("\n得到趋势图数据！\n")
