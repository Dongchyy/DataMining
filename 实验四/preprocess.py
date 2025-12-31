# preprocess.py (新版：处理医疗JSON数据)
import os
import json
from tqdm import tqdm

# 输入文件：你保存的新数据集
INPUT_FILE = os.path.join("data", "medical_data.json")
# 输出文件：构建向量库所需的中间格式
OUTPUT_FILE = os.path.join("data", "processed_data.json")


def process_data():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误：未找到 {INPUT_FILE}，请先将数据集保存为该文件。")
        return

    print(f"📥 正在读取 {INPUT_FILE} ...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    processed_data = []

    print(f"🧹 开始处理 {len(raw_data)} 条数据...")

    for item in tqdm(raw_data):
        # 1. 提取字段
        # 使用 'question' 作为标题，这样检索时匹配度更高
        title = item.get('question', '未知问题')

        # 2. 构造用于检索和回答的内容块 (Content)
        # 将问题、答案和证据组合在一起，提供完整的上下文给 LLM
        answer = item.get('answer', '')
        evidence = item.get('evidence', '')

        # 组合成一个清晰的文本块
        content = f"问题：{title}\n答案：{answer}\n医学证据：{evidence}"

        # 3. 构造 build_db.py 需要的字典格式
        processed_data.append({
            "source": item.get('source', 'Medical DB'),  # 来源
            "id": item.get('id', ''),
            "title": title,  # 标题（用于展示引用）
            "publish_time": "2025",  # 数据集未提供时间，给个默认值
            "content": content  # 核心文本（用于向量化）
        })

    # 保存处理后的数据
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 数据预处理完成！共 {len(processed_data)} 条。")
    print(f"📁 已保存至 {OUTPUT_FILE}")
    print("👉 下一步：运行 build_db.py 构建向量库")


if __name__ == "__main__":
    process_data()