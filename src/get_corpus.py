# -*- coding: UTF-8 -*-

"""
Author: mathstao
Project: https://github.com/Mathstao/Chat-Cluster/
"""

import pandas as pd
import os
import utils


def main(config):
    # 读取在 DATA_FOR_CORPUS_PATH 目录下的全部xls格式文件
    file_names = os.listdir(config["DATA_FOR_CORPUS_PATH"])
    chat = []
    for file in file_names:
        if ".xls" in file:
            print(file)
            data = pd.read_excel(config["DATA_FOR_CORPUS_PATH"] + "/" + file)
            chat += list(data['对话内容'])

    # 得到训练语料
    fin = open(config["corpus_file"], 'w', encoding='utf-8')
    for t in range(len(chat)):
        word_segment = []
        curr_chat = str.lower(str(chat[t]))
        sentence_segment = [i for i in curr_chat.split('\r\n') if i]
        if len(sentence_segment) > 3:
            for sentence in sentence_segment[:-1]:
                if "访客" not in sentence and "客服人员说:" not in sentence:
                    if "欢迎使用中国银联网络客服" not in sentence:
                        word_segment += [word for word in utils.segment(utils.remove_url(sentence)) if word !=' ']
        if word_segment:
            fin.write(' '.join(word_segment) + '\n')
    fin.close()

