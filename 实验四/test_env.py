# test_env.py
import sys
import os

print("=" * 50)
print("PyCharm环境配置测试")
print("=" * 50)

# 1. 检查Python解释器
print(f"1. Python解释器路径: {sys.executable}")
print(f"2. Python版本: {sys.version[:10]}")

# 2. 修复：正确检查是否在conda环境
if "envs" in sys.executable and "rag_system" in sys.executable:
    print("3. ✅ 正在使用conda rag_system环境")
else:
    print("3. ❌ 未使用正确的conda环境")

# 3. 检查关键包
packages = [
    ("torch", "PyTorch"),
    ("transformers", "Transformers"),
    ("streamlit", "Streamlit"),
    ("sentence_transformers", "Sentence-Transformers"),
    ("pymilvus", "PyMilvus"),
    ("bs4", "BeautifulSoup4"),
    ("tqdm", "Tqdm"),
    ("huggingface_hub", "HuggingFace Hub"),
    ("accelerate", "Accelerate"),
    ("numpy", "NumPy")
]

print("\n4. 包导入测试:")
all_success = True
for import_name, display_name in packages:
    try:
        if import_name == "sentence_transformers":
            from sentence_transformers import SentenceTransformer
        elif import_name == "bs4":
            import bs4
        else:
            exec(f"import {import_name}")

        if import_name == "torch":
            import torch

            print(f"   ✅ {display_name}: {torch.__version__} (CUDA: {torch.cuda.is_available()})")
        elif import_name == "transformers":
            import transformers

            print(f"   ✅ {display_name}: {transformers.__version__}")
        elif import_name == "streamlit":
            import streamlit

            print(f"   ✅ {display_name}: {streamlit.__version__}")
        else:
            print(f"   ✅ {display_name}: 已安装")
    except Exception as e:
        print(f"   ❌ {display_name}: {str(e)[:50]}")
        all_success = False

print("\n" + "=" * 50)
if all_success:
    print("🎉 所有测试通过！环境配置正确。")
else:
    print("⚠️  有部分包未安装，请安装缺失的包。")
print("=" * 50)