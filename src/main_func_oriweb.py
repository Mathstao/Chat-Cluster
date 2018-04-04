# -*- coding: utf-8 -*-
import sys
import time
import pandas as pd
from flask import Flask, jsonify, request, abort

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


app = Flask(__name__)

# 让jsonify返回的json串支持中文显示
app.config['JSON_AS_ASCII'] = False

# 初始化config为默认参数
PROJ_PATH = sys.path[0] + "/.."
name=""
config = dict()
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
    "cluster_excel_file": PROJ_PATH + "/result/cluster_result" + name + ".xls",
    "cluster_result_file": PROJ_PATH + "/result/cluster_stat" + name + ".xls",
    "trend_data_file": PROJ_PATH + "/trend_data" + name + ".xls"
}


# 修改参数
@app.route('/config/set', methods=['POST', 'GET'])
def set_config(n_cluster_first=120, n_top_words=5, threshold_cluster_second=3, w2v_dim=200, filter_label=None, name=''):
    global config

    # 以'POST'格式
    if request.method == 'POST':
        if not request.json:
            abort(400)
        for attr in request.json:
            if attr == "nochange":
                break
            print(attr)
            if attr == "n_cluster_first":
                n_cluster_first = request.json[attr]
            elif attr == "n_top_words":
                n_top_words = request.json[attr]
            elif attr == "threshold_cluster_second":
                threshold_cluster_second = request.json[attr]
            elif attr == "w2v_dim":
                w2v_dim = request.json[attr]
            elif attr == "filter_label":
                filter_label = request.json[attr]
            elif attr == "name":
                name = request.json[attr]
            else:
                abort(400)

    # 以GET格式
    elif request.method == 'GET':
        if not request.args.get("nochange"):
            if request.args.get("n_cluster_first"):
                n_cluster_first = int(request.args.get("n_cluster_first"))
            if request.args.get("n_top_words"):
                n_top_words = int(request.args.get("n_top_words"))
            if request.args.get("threshold_cluster_second"):
                threshold_cluster_second = int(request.args.get("threshold_cluster_second"))
            if request.args.get("w2v_dim"):
                w2v_dim = int(request.args.get("w2v_dim"))
            if request.args.get("filter_label"):
                filter_label = request.args.get("filter_label")
            if request.args.get("name"):
                name = request.args.get("name")

    config = {
        "n_cluster_first": n_cluster_first,
        "n_top_words": n_top_words,
        "threshold_cluster_second": threshold_cluster_second,
        "w2v_dim": w2v_dim,
        "filter_label": filter_label,
        "name": name,
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
    # return "配置参数设置完毕"
    return jsonify(config)


# 打印出config参数
@app.route('/config/print', methods=['GET'])
def config_json():
    if config == {}:
        return "未设置参数！"
    return jsonify(config)


# 训练词向量模型
@app.route('/w2v/train', methods=['GET'])
def train_w2v():
    w2v_config = {"DATA_FOR_CORPUS_PATH": PROJ_PATH + "/data/for_corpus",
                  "corpus_file": PROJ_PATH + "/data/corpus.txt",
                  "w2v_dim": 200}
    print("\n正在处理语料...\n")
    start = time.time()
    get_corpus.main(w2v_config)
    print("\n语料处理完毕！\n")
    print("\n正在训练词向量...\n")
    train_w2v_model.main(w2v_config)
    end = time.time()
    return "词向量训练完毕,共耗时"+str(end-start)+"秒"


# 训练聚类模型
@app.route('/cluster/train', methods=['GET'])
def cluster():
    if config == {}:
        return "未设置参数！"
    print("开始训练")
    start = time.time()
    get_ori_excel.main(config)
    cluster_first.main(config)
    cluster_second.main(config)
    write_summary.main(config)
    get_trend_data.main(config)
    end = time.time()
    return "聚类完毕, 共耗时"+str(end - start)+"秒"


# 返回全部聚类结果
@app.route('/cluster/result', methods=['GET'])
def get_cluster_result_excel():
    data = pd.read_excel(config["cluster_excel_file"], encoding='utf-8')
    return data.to_json(orient='records', force_ascii=False)


# 返回特定日期范围的聚类结果，date_range的格式应为如下格式: 20171201-20171217
@app.route('/cluster/result/<string:date_range>', methods=['GET'])
def get_spec_date_cluster_data(date_range):
    data = pd.read_excel(config["cluster_excel_file"], encoding='utf-8')
    start, end = date_range.split('-')
    start = int(start)
    end = int(end)
    idx = []
    for i in range(len(data)):
        if start <= int(data.iat[i,0].split('-')[0]) <=end:
            idx.append(i)
    return data.iloc[idx].to_json(orient='records', force_ascii=False)


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)