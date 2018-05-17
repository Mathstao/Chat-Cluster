#  客服对话数据聚类及热点问题挖掘  

### 一、运行环境
语言：**python3.6.3**
第三方库：**numpy, pandas, sklearn, gensim, flask, jieba, pymysql**  

### 二、数据路径说明
**./data/for_corpus/** 用来训练词向量的语料，格式为原始的客户对话数据excel



**./data/for_cluster/** 需要聚类数据，格式为原始的客户对话数据excel



**./model** 词向量模型，目前只有一个默认的w2v_model模型，维度为200



**./result** 聚类结果，每一次完整的聚类完毕后会生成3个文件，xxx为该次聚类任务的名称
* cluster_result_xxx.xls 完整的聚类结果
* cluster_stat_xxx.xls 聚类的统计结果
* trend_data_xxx.xls 各类别在每一天的数量，可用来观察趋势




**./vocab** 存放各种专门针对客服对话情景设计的词典

* stopwords.txt 分词时的使用的停用词典
* userdict.txt 分词时使用的自定义词典
* merchant.txt 商户名称
* time.txt 关于日期的词语
* negative.txt 否定词、疑问词





### 三、代码说明

#### 1. 工具函数:
* utils.py 集成了数据处理需要用到的函数




#### 2. 词向量训练：

* train_w2v_model.py 处理原始数据，得到词向量训练所需要的语料库，利用得到的语料库训练词向量（只有在需要重新训练词向量时才要运行）




#### 3. 聚类及生成摘要：

每一次的聚类及生成摘要任务可分解为（顺序如下）

* get_ori_excel.py  处理原始数据得到待聚类数据的excel表格
* cluster_first.py  Kmeans聚类
* cluster_second.py  基于关键词连接矩阵的聚类合并
* write_summary.py  根据聚类合并后的结果生成摘要
* get_trend_data.py  得到趋势图数据




#### 4. 主函数（有2个版本）

* main_func_local.py 本地实验调试版本 
* main_func_mysql.py 利用flask框架封装、将训练任务保存到MySQL数据库中的异步版本（需要与clusterAPI_startup.py配合使用）



### 四、使用方法

| 参数名称                     | 参数说明                                     |
| :----------------------- | :--------------------------------------- |
| name                     | 本次任务名称 （空或者普通的字符串，默认为空）                  |
| filter_label             | 原始数据过滤条件（空字符串或者若干个词语以"-"为分隔符组成的字符串，如 "银联-云闪付-钱包"，默认为””） |
| n_cluster_first          | K-means聚类的个数 （非负整数，默认为120）               |
| n_top_words              | 每一类别的关键词数量  （非负整数，默认为5）                  |
| threshold_cluster_second | 聚类合并的关键词重复个数阈值  （非负整数，默认为3）              |

#### 1. 本地版本

1. 确保聚类数据、词向量模型、词典完整
2. 在main_func_local.py中设置模型参数，直接运行该脚本即可。




#### 2. Flask框架版本

（注意将127.0.0.1换成服务器的ip，端口仍为5000）

1. 确保聚类数据、词向量模型、词典完整
2. 先运行 python main_func_mysql.py，开启web服务。（脚本需一直在后台挂着）
3. 在另一个CMD下运行 python clusterAPI_startup.py，其作用是每隔5秒检查是否添加了新的任务，若有，则开始新一轮的聚类。（脚本需一直在后台挂着）
4. 使用curl命令或者直接在浏览器输入url调用想要实现的接口，下面以本地测试为例。




如图，新增命名为test_3，过滤标签为云闪付和重大营销活动（其余参数默认）的聚类任务

```http://127.0.0.1:5000/cluster/train?name=test_3&filter_lable=云闪付-重大营销活动```

![pic](https://github.com/Mathstao/Chat-Cluster/blob/master/pic_for_md/1.png)

如果数据库中已存在名字为test_3的任务，则返回添加失败
![pic](https://github.com/Mathstao/Chat-Cluster/blob/master/pic_for_md/2.png)

如图为后台的训练任务数据(MySQL)，一行为一个聚类任务，记录着该次任务的参数以及开始、结束时间，另外status有3个状态，分别是to be processed（待处理），processing（处理中）以及finished（完成）。
![pic](https://github.com/Mathstao/Chat-Cluster/blob/master/pic_for_md/3.png)

在test_3任务完成后，查看其中属于2017年12月1号~2017年12月3号的结果数据，以json格式返回给前端

```127.0.0.1:5000/cluster/result/test_3/20171201-20171203```

```
json格式为[{"id":xxx,
            "summary":xxx,
            "keywords":xxx,
            "label":xxx,
            "sublabel":xxx,
            "sentence":xxx,
            "tag":xxx,
            "cutwords":xxx},
            {...},
            {...},
            ...]
```

(该结果涉及用户数据，不便展示)

删除指定的任务

```http://127.0.0.1:5000/cluster/delete/test_5```

![pic](https://github.com/Mathstao/Chat-Cluster/blob/master/pic_for_md/4.png)

### 五、项目需要补全的部分：
1. 缺少用户上传新的聚类文件的API接口
2. 缺少用户上传新的语料文件并重新训练训练词向量的API接口，目前只能在本地通过运行main_func_local.py中调用train_w2v_mode来重新训练
