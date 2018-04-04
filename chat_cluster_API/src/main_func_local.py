# -*- coding: utf-8 -*-
import sys
import time

# 该部分为程序的分步脚本：
# 1. get_corpus: 处理原始数据，得到词向量训练所需要的语料库
# 2. train_w2v_model: 利用上一步得到的语料库训练词向量
# 3. get_ori_excel: 处理原始数据得到待聚类数据的excel表格
# 4. cluster_first: Kmeans聚类
# 5. cluster_second: 基于关键词连接矩阵的聚类合并
# 6. write_summary: 根据聚类合并后的结果生成摘要
# 7. get_trend_data: 得到趋势图数据
import get_corpus
import train_w2v_model
import get_ori_excel
import cluster_first
import cluster_second
import write_summary
import get_trend_data


# 项目路径
PROJ_PATH = sys.path[0] + "/.."


# 设置config参数
name = ""
config = {
    "n_cluster_first": 120,
    "n_top_words": 5,
    "threshold_cluster_second": 3,
    "filter_label": None,
    "name": name,

    "w2v_dim": 200,
    "PROJ_PATH": PROJ_PATH,
    "DATA_PATH": PROJ_PATH + "/data",
    "DATA_FOR_CORPUS_PATH": PROJ_PATH + "/data/for_corpus",
    "DATA_FOR_CLUSTER_PATH": PROJ_PATH + "/data/for_cluster",
    "MODEL_PATH": PROJ_PATH + "/model",
    "RESULT_PATH": PROJ_PATH + "/result",
    "corpus_file": PROJ_PATH + "/data/corpus.txt",
    "w2v_model_file": PROJ_PATH + "/model/w2v_model",
    "cluster_excel_file": PROJ_PATH + "/result/cluster_result" + "_" + name + ".xls",
    "cluster_result_file": PROJ_PATH + "/result/cluster_stat" + "_" + name + ".xls",
    "trend_data_file": PROJ_PATH + "/result/trend_data" + "_" + name + ".xls"
}


# 训练词向量
def train_w2v():
    print("\n正在处理语料...\n")
    start = time.time()
    get_corpus.main(config)
    print("\n语料处理完毕！\n")
    print("\n正在训练词向量...\n")
    train_w2v_model.main(config)
    end = time.time()
    return "词向量训练完毕,共耗时"+str(end-start)+"秒"


# 聚类
def cluster():
    get_ori_excel.main(config)
    cluster_first.main(config)
    cluster_second.main(config)
    write_summary.main(config)
    get_trend_data.main(config)
    return "聚类完毕"


if __name__ == '__main__':
    train_w2v()
    # cluster()