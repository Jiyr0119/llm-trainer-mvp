# 导入必要的库
from transformers import BertTokenizer, BertForSequenceClassification  # 导入Hugging Face的BERT模型和分词器
import os  # 导入操作系统模块，用于文件和目录操作

# 设置模型保存路径
model_name = 'bert-base-chinese'  # 指定要下载的预训练模型名称（中文BERT基础模型）
model_path = '../data/models/bert-base-chinese'  # 指定模型保存的本地路径

# 创建保存模型的目录
# exist_ok=True 参数确保目录已存在时不会引发错误
os.makedirs(model_path, exist_ok=True)

# 从Hugging Face下载预训练模型和分词器
# from_pretrained方法会从Hugging Face模型仓库下载模型
tokenizer = BertTokenizer.from_pretrained(model_name)  # 下载并初始化分词器
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)  # 下载并初始化模型，设置分类标签数为2

# 将下载的模型和分词器保存到本地目录
# 这样可以避免每次都需要从网络下载
tokenizer.save_pretrained(model_path)  # 保存分词器
model.save_pretrained(model_path)  # 保存模型

# 打印保存成功的消息
print(f"模型已保存到: {model_path}")  # 输出模型保存路径