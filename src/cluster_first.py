# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import gensim
import utils
import time
from sklearn.cluster import KMeans

# not_count = ['银联钱包','闪付','云闪付','app','钱包']

# 输入一个句子分词后的词语列表，返回平均词向量
def get_mean_vec(word_lists, model, w2v_dim):
    vec = np.zeros(w2v_dim)
    count = 0
    select_word = []
    for word in word_lists:
        # if word in model.wv.vocab and word not in not_count:
        if word in model.wv.vocab:
            vec += model.wv.__getitem__(word)
            select_word.append(word)
            count += 1
    if count:
        return vec/count, select_word
    else:
        return vec, select_word


def main(config):
    print("\n正在进行第一次聚类...\n")

    # 读取词向量模型
    model = gensim.models.Word2Vec.load(config["w2v_model_file"])

    # 读取数据
    data = pd.read_excel(config["cluster_excel_file"])

    # 得到句子平均词向量
    w2v_dim = model.vector_size
    print("词向量模型的维度为",w2v_dim)

    # 样本的特征矩阵，一列为一个样本
    feature = np.zeros([len(data), w2v_dim])
    split_word = []
    for i in range(len(data)):
        word_list = utils.segment(data.iat[i,5])
        feature[i,:], select_word = get_mean_vec(word_list, model, w2v_dim)
        split_word.append(' '.join(select_word))

    # 只保留分词不为空的数据
    bool_idx = [True if split_word[i] else False for i in range(len(split_word))]
    num_idx = [i for i in range(len(split_word)) if split_word[i]]
    data = data[bool_idx]
    split_word = np.array(split_word)[num_idx]
    feature = feature[num_idx, :]

    # 利用sk-learn中的K-means函数进行聚类
    y_pred = KMeans(n_clusters=config["n_cluster_first"]).fit_predict(feature)
    data["sublabel"]=y_pred
    data["cutwords"]=split_word
    data = data.sort_values(["sublabel"])

    # 保存数据
    data.to_excel(config["cluster_excel_file"], index=False)
    print("\n第一次聚类完成！\n")
