# build_db.py
import json
import os
import pickle
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

DATA_PATH = os.path.join("data", "processed_data.json")
DB_PATH = "vector_db.pkl"
# 向量模型 (Bi-Encoder)
MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def build_database():
    if not os.path.exists(DATA_PATH):
        print("❌ 错误：请先运行 preprocess.py")
        return

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 正在加载嵌入模型 {MODEL_NAME} ...")
    # normalize_embeddings=True 对余弦相似度检索很重要
    model = SentenceTransformer(MODEL_NAME)

    db_data = []
    print(f"🚀 开始生成向量 (共 {len(data)} 条切片)...")

    # 批量处理可以稍微快一点，但为了进度条显示，我们这里还是逐条或小批量
    # 构造 "Instruct: ... Query: ..." 格式对于 BGE 模型有加成，但这里是存库，直接存内容即可
    # 也可以将标题加入向量计算增加语义

    texts_to_encode = [f"{item['title']}：{item['content']}" for item in data]

    # 批量编码
    embeddings = model.encode(texts_to_encode, normalize_embeddings=True, show_progress_bar=True)

    for i, item in enumerate(data):
        db_data.append({
            "vector": embeddings[i],  # numpy array
            "content": item['content'],
            "title": item['title'],
            "source": item['source'],
            "publish_time": item.get('publish_time', '')
        })

    with open(DB_PATH, 'wb') as f:
        pickle.dump(db_data, f)
    print(f"✅ 数据库构建完成！已保存至 {DB_PATH}")


if __name__ == "__main__":
    build_database()