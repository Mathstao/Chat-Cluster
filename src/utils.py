# -*- coding: UTF-8 -*-
import re
import jieba


# 读取停用词词典，自定义词典，时间词典，疑问/否定词典
jieba.load_userdict("../vocab/userdict.txt")
userdict = [i.strip('\n') for i in open("../vocab/userdict.txt", encoding='utf-8').readlines()]
stopword = [i.strip('\n').strip('\t') for i in open("../vocab/stopwords.txt", encoding='utf-8').readlines()]
time = [i.strip('\n') for i in open("../vocab/time.txt", encoding='utf-8').readlines()]
question = [i.strip('\n') for i in open("../vocab/negative.txt", encoding='utf-8').readlines()]

# 分隔符
spliter = '，|！|!|。|？|\?|~|、| '

# 正则表达式
zhPattern = re.compile(r'[\u4e00-\u9fa5]+')
tag_pattern = '<.*?>'
url_pattern = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})"


# 去掉网址
def remove_url(s):
    # html tag
    s = re.sub(tag_pattern, "", s)
    s = re.sub(url_pattern, "", s)
    # 连续的空格替换成一个空格
    s = re.sub(r"\s +", " ", s)
    s = re.sub(r"\s　+", " ", s)
    return s

# 判断文本是否含有中文
def include_zh(text):
    if zhPattern.search(text):
        return True
    else:
        return False


# 判断该字符串是否是数字且不在停用词典中
def is_number(word):
    if "%" in word:
        return True
    try:
        float(word)
        if word in userdict:
            return False
        else:
            return True
    except ValueError:
        return False


# 是否含有时间词语
def is_time(word):
    if word == '时候':
        return False
    else:
        for t in time:
            if t in word or t == '号':
                return True
        return False


# 是否是单个英文字母
def is_single_alphabet(uchar):
    if len(uchar) > 1:
        return False
    else:
        if u'\u0041' <= uchar <= u'\u005a' or u'\u0061' <= uchar <= u'\u007a':
            return True
        else:
            return False


# 分词
def segment(x):
    temp = [i for i in jieba.cut(x) if i.strip(" ")]
    return [i for i in temp if i not in stopword and not is_number(i) and not is_time(i) and not is_single_alphabet(i)]


# 简单分词（返回jieba分词的原始结果）
def simple_segment(x):
    return [i for i in jieba.cut(x) if i.strip()]


# 判断句子是否含有否定词
def with_negative(sentence):
    for word in question:
        if word in sentence:
            return True
    return False


# 将句子列表按照分隔符再细分割一次
def split_sentence(sentences):
    temp = []
    for sen in sentences:
        temp.extend(re.split(spliter, sen))
    temp = [t for t in temp if t]
    return temp


# 得到客户说的句子列表
def chat_to_customer_sentence(chat):
    sentences = []
    sentence_segments = [i for i in str(chat).split('\r\n') if i]
    mark = 0
    for sentence in sentence_segments[:-1]:
        if mark:
            sentences.append(remove_url(sentence))
            mark = 0
        if "访客" in sentence:
            mark = 1
    return sentences


# 得到客户第一句段
def chat_to_customer_first_sentence(chat):
    chat = str(chat)
    sentences = []
    sentence_segments = [i for i in chat.split('\r\n') if i][:-1]
    mark = 0
    temp = []
    for i, sentence in enumerate(sentence_segments):
        if "客服人员" in sentence:
            mark == 0
            if temp:
                sentences.append(temp)
                temp = []
        if mark == 1:
            temp.append(remove_url(sentence))
            mark = 0
            if i != len(sentence_segments) - 1:
                if "客服人员" not in sentence_segments[i + 1] and "访客" not in sentence_segments[i + 1]:
                    mark = 1
        if "访客" in sentence:
            mark = 1
    if temp:
        sentences.append(temp)
    record = []
    for sentence in sentences:
        record.extend(sentence)
        curr_sentence = " ".join(record)
        if len(segment(curr_sentence)) >= 4 and with_negative(curr_sentence):
            return record
    return record


# 得到客户说的第一个否定窗口
def get_first_negative_window(sentences):
    for i in range(len(sentences)):
        if with_negative(sentences[i]):
            if len(segment(sentences[i])) >= 4:
                return [sentences[i]]
            else:
                sentences.insert(0, "")
                sentences.append("")
                return [s for s in sentences[i:i + 3] if s]
    return sentences


# 得到客户说的第一句话的分词列表
def chat_to_word_list_first(chat):
    chat = str(chat)
    word_segment = []
    sentence_segment = [i for i in chat.split('\r\n') if i]
    mark = 0
    end = 0
    i = 0
    while not end and i <= len(sentence_segment) - 1:
        sentence = sentence_segment[i]
        if "访客" in sentence:
            mark = 1
        elif mark:
            mark = 0
            word_segment += [word for word in segment(remove_url(sentence)) if word != ' ']
            if len(word_segment) > 5:
                end = 1
        i += 1
    return word_segment


# 得到客服和客户对话的全部分词（词向量训练的语料）
def chat_to_word_list(chat):
    word_segment = []
    sentence_segment = [i for i in str(chat).split('\r\n') if i]
    if len(sentence_segment) > 3:
        for sentence in sentence_segment[:-1]:
            if "访客" not in sentence and "客服人员说:" not in sentence:
                if "欢迎使用中国银联网络客服" not in sentence:
                    word_segment += [word for word in segment(remove_url(sentence)) if word != ' ']
        return word_segment
