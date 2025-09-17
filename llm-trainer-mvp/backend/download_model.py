# 导入必要的库
from transformers import AutoTokenizer, AutoModelForCausalLM  # 导入Hugging Face的自动模型和分词器
import os  # 导入操作系统模块，用于文件和目录操作
import argparse  # 导入参数解析模块，用于处理命令行参数
import torch  # 导入PyTorch

# 可用模型配置
AVAILABLE_MODELS = {
    'qwen-1.5-0.5b': {
        'model_name': 'Qwen/Qwen1.5-0.5B-Chat',
        'description': 'Qwen 1.5 0.5B Chat模型，适合轻量级对话应用'
    },
    'qwen-1.5-1.8b': {
        'model_name': 'Qwen/Qwen1.5-1.8B-Chat',
        'description': 'Qwen 1.5 1.8B Chat模型，适合一般对话任务'
    },
    'deepseek-1.5b': {
        'model_name': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B',
        'description': 'DeepSeek Coder 1.3B指令模型，适合代码生成'
    },
    'deepseek-6.7b': {
        'model_name': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B',
        'description': 'DeepSeek Coder 6.7B指令模型，适合复杂代码生成'
    }
}

def download_model(model_key):
    """下载并保存指定的模型"""
    if model_key not in AVAILABLE_MODELS:
        print(f"错误：未知的模型 '{model_key}'")
        print(f"可用的模型: {', '.join(AVAILABLE_MODELS.keys())}")
        return
    
    model_info = AVAILABLE_MODELS[model_key]
    model_name = model_info['model_name']
    model_path = f'../data/models/{model_key}'
    
    print(f"开始下载模型: {model_name}")
    print(f"描述: {model_info['description']}")
    
    # 创建保存模型的目录
    os.makedirs(model_path, exist_ok=True)
    
    # 设置下载参数，使用4位精度以减小模型大小
    torch_dtype = torch.float16  # 使用半精度浮点数
    
    try:
        # 下载分词器
        print("下载分词器...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        # 下载模型
        print("下载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        # 保存模型和分词器
        print("保存模型和分词器到本地...")
        tokenizer.save_pretrained(model_path)
        model.save_pretrained(model_path)
        
        print(f"模型已成功保存到: {model_path}")
    except Exception as e:
        print(f"下载模型时出错: {str(e)}")

def list_models():
    """列出所有可用的模型"""
    print("可用的模型:")
    for key, info in AVAILABLE_MODELS.items():
        print(f"  - {key}: {info['description']}")

def main():
    """主函数，处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='下载和保存语言模型')
    parser.add_argument('--model', type=str, help='要下载的模型名称')
    parser.add_argument('--list', action='store_true', help='列出所有可用的模型')
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
    elif args.model:
        download_model(args.model)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()