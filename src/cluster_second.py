# -*- coding: UTF-8 -*-

"""
Author: mathstao
Project: https://github.com/Mathstao/Chat-Cluster/
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# data为聚类结果表格的DataFrame，topN为每一类的关键词数量，name为label/sublabel，以列表的格式返回各类的tf-idf值前topN大的词语
def get_topN_tf_idf_words(data, topN, name):
    n_class = len(set(data[name]))
    corpus = []
    for i in range(n_class):
        select_data = data[data[name] == i]
        corpus.append(" ".join([select_data.iat[i, -1] for i in range(len(select_data))]))

    # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()
    # 该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()
    # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    # 获取词袋模型中的所有词语
    word = vectorizer.get_feature_names()
    # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    weight = tfidf.toarray()

    # dicts以字典的形式记录各类中出现过的词语以及对应的tf-idf值
    dicts = {}
    for i in range(len(weight)):
        dicts[i] = []
        for j in range(len(word)):
            if weight[i][j]:
                dicts[i].append((word[j], weight[i][j]))

    # topN_word_list为最终需要返回的结果
    topN_word_list = []
    for i in range(n_class):
        temp = []
        for j in sorted(dicts[i], key=lambda x: x[1], reverse=True)[:topN]:
            temp.append(j[0])
        topN_word_list.append(temp)
    return topN_word_list


# 根据topN_tf_idf_words_list以及计算关键词连接矩阵
def get_join_matrix(n, threshold, topN_tf_idf_words_list):
    mat = np.zeros([n, n])
    for i in range(n):
        mat[i][i] = 1
        for j in range(i, n):
            if len(set(topN_tf_idf_words_list[i]) & set(topN_tf_idf_words_list[j])) >= threshold:
                mat[i][j], mat[j][i] = 1, 1
    return mat


def main(config):
    topN = config["n_top_words"]
    data = pd.read_excel(config["cluster_excel_file"])

    print("\n正在进行第二次聚类...\n")
    topN_tf_idf_words_list = get_topN_tf_idf_words(data, topN, "sublabel")
    mat = get_join_matrix(config["n_cluster_first"], config["threshold_cluster_second"], topN_tf_idf_words_list)

    # 建立（合并后）新类别与（K-means初次聚类）旧类别的对应关系
    results = []
    for i in range(config["n_cluster_first"]):
        flag = 1
        idx = list(np.where(mat[i, :]>0)[0])
        for r in range(len(results)):
            if set(idx)&set(results[r]):
                results[r].extend(idx)
                results[r] = list(set(results[r]))
                flag = 0
                break
        if flag:
            idx = list(np.where(mat[i, :]>0)[0])
            results.append(idx)
    second_to_first_dicts = {i: results[i] for i in range(len(results))}

    # 建立（K-means初次聚类）旧类别与（合并后）新类别的对应关系
    first_to_second_dicts = {}
    for i in range(len(second_to_first_dicts)):
        for j in second_to_first_dicts[i]:
            first_to_second_dicts[j] = i

    # 将聚类合并的结果写入DataFrame中，保存为excel表格
    labels_second=[]
    for i in data["sublabel"]:
        labels_second.append(first_to_second_dicts[int(i)])
    data["label"] = labels_second
    data = data.sort_values(["label"])
    data.to_excel(config["cluster_excel_file"], index=False)
    print("\n第二次聚类完成！\n")
