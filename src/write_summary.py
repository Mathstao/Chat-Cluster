# -*- coding: UTF-8 -*-

"""
Author: mathstao
Project: https://github.com/Mathstao/Chat-Cluster/
"""

import re
import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# 需要用到的正则表达式
number_pattern = '\d{4,}'
xuci_words = '啊|阿|吖|呢|了|吗|呢'
greet_words = 'nihao|你好|您好|请问'


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


# 用于drop_duplicate_str函数中，返回字符串的全部长度的子串
def slice_window(one_str, w):
    res_list = []
    for i in range(0, len(one_str) - w + 1):
        res_list.append(one_str[i:i + w])
    return res_list


# 对字符串的过长重复子串进行去重
def drop_duplicate_str(one_str):
    if one_str:
        all_sub = []
        for i in range(1, len(one_str) + 1):
            all_sub += slice_window(one_str, i)
        res_dict = {}
        for one in all_sub:
            if one in res_dict:
                res_dict[one] += 1
            else:
                res_dict[one] = 1
        threshold = max(res_dict.values())
        sorted_list = sorted(res_dict.items(), key=lambda e: e[1], reverse=True)
        tmp_list = [one for one in sorted_list if one[1] >= threshold]
        tmp_list = sorted(tmp_list, key=lambda x: len(x[0]), reverse=True)
        if len(tmp_list[0][0]) > 0.4 * len(one_str):
            return tmp_list[0][0]
        else:
            return one_str
    else:
        return one_str

# 去掉过长的数字（一般是手机号码，证件号等无意义的数字）
def drop_long_number_mark(summary):
    new_summary = summary
    splits = summary.split(" ")
    for s in splits:
        search = re.search(string=s, pattern=number_pattern)
        if search:
            if len(search.group()) > 0.5 * len(s):
                new_summary = new_summary.replace(s, "")
            else:
                seg = jieba.lcut(s)
                for i in seg:
                    if re.search(string=i, pattern=number_pattern):
                        new_summary = new_summary.replace(i, "")
    return new_summary


# 精简摘要
def simplify_summary(temp_key_words, summary):
    # 只保留包含关键词的句子分块
    splits = summary.split(" ")
    temp = []
    for i in splits:
        flag = 0
        for j in temp_key_words:
            if j in i:
                flag = 1
                break
        if flag:
            temp.append(i)
    # 去重
    temp2 = []
    for i in range(len(temp)):
        flag = 1
        for j in range(len(temp)):
            if j != i and temp[i] in temp[j] and temp[i] != temp[j]:
                flag = 0
                break
        if flag:
            temp2.append(temp[i])
    summary = " ".join(temp2)

    # 进一步精简
    summary = summary.lower()
    summary = summary.replace("不了", "_protect_")
    summary = re.sub(xuci_words, '', summary)
    summary = re.sub(greet_words, '', summary)
    summary = summary.replace("_protect_", "不了")
    summary = drop_duplicate_str(summary)
    summary = drop_long_number_mark(summary)
    return summary


# 获取指定类别的摘要
def get_summary(data, label, topN_word, name):
    select_data = data[data[name] == label]
    dicts = {}
    for i in range(len(select_data)):
        splits = select_data.iat[i, -1].split(" ")
        if topN_word[0] in splits and len(simplify_summary(topN_word, select_data.iat[i, 5])) > 7:
            curr_mark = 0
            for s in splits:
                if s in topN_word:
                    curr_mark += 1
            mark_one = curr_mark / len(splits)
            mark_two = len("".join(select_data.iat[i, -1]).split(" ")) / len(select_data.iat[i, 5].replace(" ", ""))
            dicts[select_data.iat[i, 5]] = (mark_one, mark_two)
    if dicts!={}:
        key_list = list(dicts.keys())
        summary = key_list[0]
        for i in key_list[1:]:
            best = dicts[summary]
            curr = dicts[i]
            if curr[0] > best[0] or (curr[0] == best[0] and curr[1] > best[1]):
                summary = i
        return simplify_summary(topN_word, summary)
    else:
        return "无法生成摘要"


def main(config):
    topN = config["n_top_words"]
    data = pd.read_excel(config["cluster_excel_file"])
    # common_words = ['银联钱包','银联','云闪付','app','App','APP','手机号码','手机号','身份证','号码']
    #common_words = [u'银联钱包', u'银联', u'云闪付', u'app', u'App', u'APP']
    #not_count_words = [u'成功', u'失败', u'显示', u'活动']
    n_cluster_second = len(set(data["label"]))

    print("\n正在写入摘要...\n")

    topN_word_lists = get_topN_tf_idf_words(data, topN, "label")
    summary_list = [get_summary(data, i, topN_word_lists[i], "label") for i in range(n_cluster_second)]
    summaries = []
    keywords = []
    for i in data["label"]:
        summaries.append(summary_list[i])
        keywords.append(" ".join(topN_word_lists[i]))
    data["summary"] = summaries
    data["keywords"] = keywords
    data.to_excel(config["cluster_excel_file"], index=False)
    print("\n写入摘要完成！\n")
