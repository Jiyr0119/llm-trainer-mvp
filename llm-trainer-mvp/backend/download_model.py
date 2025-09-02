from transformers import BertTokenizer, BertForSequenceClassification
import os

# 设置模型保存路径
model_name = 'bert-base-chinese'
model_path = '../data/models/bert-base-chinese'

# 创建目录
os.makedirs(model_path, exist_ok=True)

# 下载模型和分词器
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# 保存到本地
tokenizer.save_pretrained(model_path)
model.save_pretrained(model_path)

print(f"模型已保存到: {model_path}")