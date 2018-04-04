# -*- coding: UTF-8 -*-
import os
import pandas as pd
import utils


def main(config):
    print("\n正在处理原始数据并得到excel表格...\n")

    # 读取在 DATA_FOR_CLUSTER_PATH 目录下的全部xls格式文件
    file_names = os.listdir(config["DATA_FOR_CLUSTER_PATH"])
    data = pd.DataFrame()
    for file in file_names:
        if "xls" in file:
            print(file)
            temp_df = pd.read_excel(config["DATA_FOR_CLUSTER_PATH"] + '/' + file, encoding='utf-8')
            name = file[-12:-4]
            temp_df.insert(loc=0, column='序号', value=[name + "-" + str(i+1) for i in range(len(temp_df))])
            data = pd.concat([data,temp_df])
    data = data.reset_index(drop=True)

    # 根据filter_label选择性对原数据进行过滤
    if config["filter_label"]:
        filter_label = [f.strip(" ") for f in config["filter_label"].split("-")]
    else:
        filter_label = []
    idx = []
    # 不需要过滤
    if not filter_label:
        for i in range(len(data)):
            catalog =  str(data.loc[i,"对话分类"])
            if "客户主动离开" not in catalog:
                idx.append(i)
        data = data.iloc[idx]
        data = data.reset_index(drop=True)
    # 需要过滤
    else:
        for i in range(len(data)):
            catalog = str(data.loc[i, "对话分类"])
            if "客户主动离开" not in catalog:
                flag = 0
                for label in config["filter_label"]:
                    if label in catalog:
                        flag =1
                        break
                if flag:
                    idx.append(i)
        data = data.iloc[idx]
        data = data.reset_index(drop=True)

    # 得到每一个样本的第一个否定窗口
    sentences_for_segment = []
    for i in range(len(data)):
        first = utils.chat_to_customer_first_sentence(data.iat[i, 14])
        first_split = utils.split_sentence(first)
        negative = utils.get_first_negative_window(first_split)
        #################################################
        # if len(utils.segment(" ".join(negative)))>=3: #
        #################################################
        if len("".join(negative)) >= 7:
            sentences_for_segment.append(" ".join(negative))
        else:
            sentences_for_segment.append(" ".join(first))

    # 需要保存的数据框
    to_save = pd.DataFrame()
    to_save.insert(loc=0, column="id", value=data["序号"])
    to_save.insert(loc=1, column="summary", value=None)
    to_save.insert(loc=2, column="keywords", value=None)
    to_save.insert(loc=3, column="label", value=None)
    to_save.insert(loc=4, column="sublabel", value=None)
    to_save.insert(loc=5, column="sentence", value=sentences_for_segment)
    to_save.insert(loc=6, column="tag", value=None)
    to_save.insert(loc=7, column="cutwords", value=None)

    # 只保留句子不为空，长度不小于5且包含中文的样本
    idx = [True if len(to_save.iat[i, 5]) >= 5 and utils.include_zh(to_save.iat[i, 5]) and not pd.isnull(data.iat[i, 5])
           else False for i in range(len(to_save))]
    to_save = to_save[idx]

    # 将处理完毕的数据保存为excel表格
    ew = pd.ExcelWriter(config["cluster_excel_file"], encoding='utf-8')
    to_save.to_excel(ew, index=False)
    ew.save()
    print("\n得到待聚类的excel数据！\n")