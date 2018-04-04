# -*- coding: UTF-8 -*-
from gensim.models import Word2Vec


def main(config):
    # 读取训练语料库
    with open(config["corpus_file"], 'r', encoding='utf-8') as f:
        sentences = []
        for line in f.readlines():
            sentences.append(line.strip('\n').split(' '))

    # 训练词向量模型
    print("\n正在训练词向量模型...\n")
    model = Word2Vec(sentences, size=config['w2v_dim'], window=5, min_count=5, workers=4)
    print("\n词向量模型训练成功！\n")

    # 保存词向量模型
    model.save(config["w2v_model_file"])