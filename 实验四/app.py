# app.py
import streamlit as st
import pickle
import os
import torch
import re
from sentence_transformers import SentenceTransformer, util, CrossEncoder
from transformers import AutoTokenizer, AutoModelForCausalLM

# 页面配置
st.set_page_config(page_title="专业医疗问答助手 (RAG)", layout="wide", page_icon="🩺")


# === 核心资源加载 ===
@st.cache_resource
def load_models_and_db():
    print("📥 正在加载系统资源...")

    # 1. 加载向量数据库
    db_path = "vector_db.pkl"
    if not os.path.exists(db_path):
        return None, None, None, None, None

    with open(db_path, "rb") as f:
        db_data = pickle.load(f)

    # 转换为 Tensor 加速计算
    all_vectors = torch.tensor([item["vector"] for item in db_data])

    # 2. 加载 Embedding 模型 (需与 build_db.py 保持一致)
    # 注意：如果你的数据是纯英文，建议在 build_db.py 中也换成 'BAAI/bge-base-en-v1.5' 效果更好
    # 这里保持和你之前代码一致
    embed_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

    # 3. 加载 Rerank 模型 (用于精排)
    rerank_model = CrossEncoder("BAAI/bge-reranker-base", max_length=512)

    # 4. 加载 LLM (Qwen 0.5B)
    llm_name = "Qwen/Qwen2.5-0.5B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(llm_name, trust_remote_code=True)
    llm_model = AutoModelForCausalLM.from_pretrained(llm_name, trust_remote_code=True)

    print("✅ 资源加载完成！")
    return db_data, all_vectors, embed_model, rerank_model, (tokenizer, llm_model)


# 加载资源
db_data, all_vectors, embed_model, rerank_model, llm_pkg = load_models_and_db()

# === 侧边栏设置 ===
with st.sidebar:
    st.header("⚙️ 诊断设置")
    top_k_recall = st.slider("初筛数量 (Retrieval)", 5, 50, 20)
    top_n_rank = st.slider("精排数量 (Reranking)", 1, 10, 3)
    score_threshold = st.slider("相关性阈值", -10.0, 10.0, -4.0, help="分数越高相关性越强")

    st.divider()
    if st.button("🗑️ 清空对话历史"):
        st.session_state.messages = []
        st.rerun()

# === 主界面 ===
st.title("🩺 AI 医疗助手")
st.caption("基于 RAG 技术 | 数据源：专业医学文献 | 支持中文问答")

# 检查数据库状态
if not db_data:
    st.error("❌ 数据库文件 `vector_db.pkl` 未找到！请先运行 `build_db.py`。")
    st.stop()

(tokenizer, llm_model) = llm_pkg

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === 处理用户输入 ===
query = st.chat_input("请输入医学问题（例如：皮肤癌最常见的类型是什么？）")

if query:
    # 1. 显示用户问题
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("🔍 正在检索医学知识库..."):
        # === 步骤 0: 智能查询翻译 (中文 -> 英文) ===
        # 你的数据是英文的，如果用中文去搜，效果会很差。所以先让 LLM 把问题翻译成英文。
        search_query = query
        is_chinese = any("\u4e00" <= char <= "\u9fff" for char in query)

        if is_chinese:
            # 构造翻译 Prompt
            trans_messages = [
                {"role": "system",
                 "content": "You are a professional medical translator. Translate the user's query into English directly. Do not explain."},
                {"role": "user", "content": query}
            ]
            trans_text = tokenizer.apply_chat_template(trans_messages, tokenize=False, add_generation_prompt=True)
            trans_inputs = tokenizer([trans_text], return_tensors="pt")

            # 生成翻译
            trans_ids = llm_model.generate(trans_inputs.input_ids, max_new_tokens=64, do_sample=False)
            search_query = tokenizer.batch_decode(trans_ids, skip_special_tokens=True)[0]

            # 清理输出
            if "assistant" in search_query:
                search_query = search_query.split("assistant")[-1].strip()

            # 在控制台打印翻译结果（方便调试）
            print(f"🔀 原始提问: {query}")
            print(f"🔀 检索词(英): {search_query}")

        # === 步骤 1: 向量初筛 (Retrieval) ===
        # 使用(翻译后的)英文进行搜索
        query_vec = embed_model.encode(search_query, convert_to_tensor=True, normalize_embeddings=True)
        cos_scores = util.cos_sim(query_vec, all_vectors)[0]
        top_results = torch.topk(cos_scores, k=top_k_recall)

        # 准备 Rerank 候选对
        candidate_docs = []
        candidate_indices = []

        for score, idx in zip(top_results.values, top_results.indices):
            idx = idx.item()
            doc_content = db_data[idx]['content']
            doc_title = db_data[idx]['title']
            # Cross-Encoder 输入：[English Query, English Document]
            candidate_docs.append([search_query, f"{doc_title}\n{doc_content}"])
            candidate_indices.append(idx)

        # === 步骤 2: Cross-Encoder 重排序 (Reranking) ===
        rerank_scores = rerank_model.predict(candidate_docs)

        # 组合分数与索引
        scored_candidates = list(zip(rerank_scores, candidate_indices))
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # 筛选最终 Top N
        final_refs = []
        context_str_list = []

        for score, idx in scored_candidates[:top_n_rank]:
            if score < score_threshold:
                continue

            doc = db_data[idx]
            # 保留英文原文给 LLM 阅读
            context_str_list.append(f"Source [{doc['title']}]:\n{doc['content']}")
            final_refs.append(f"{doc['title']} (Match Score: {score:.2f})")

        context_str = "\n\n".join(context_str_list)

        # === 步骤 3: 构建最终回答 Prompt ===
        if not context_str:
            prompt_content = "Please tell the user (in Chinese) that no relevant medical information was found in the database."
        else:
            # 关键：上下文是英文，但要求 LLM 用中文回答
            prompt_content = f"""You are a professional medical AI assistant.
Use the provided English medical context to answer the user's Chinese question.

=== Context / 参考文献 (English) ===
{context_str}

=== User Question / 用户问题 (Chinese) ===
{query}

=== Requirements ===
1. Answer strictly based on the Context. Do not hallucinate.
2. **Answer in Chinese (简体中文).**
3. Use professional medical tone but make it easy to understand.
4. If the context doesn't mention the answer, say "资料库中未找到相关信息".
"""

        messages = [
            {"role": "system",
             "content": "You are a helpful medical assistant. You answer in Chinese based on English evidence."},
            {"role": "user", "content": prompt_content}
        ]

        # === 步骤 4: LLM 生成 ===
        text_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer([text_input], return_tensors="pt")

        generated_ids = llm_model.generate(
            model_inputs.input_ids,
            max_new_tokens=512,
            temperature=0.3,  # 降低温度，让医学回答更严谨
            do_sample=True
        )
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        if "assistant" in response:
            ans = response.split("assistant")[-1].strip()
        else:
            ans = response

    # 3. 显示结果
    with st.chat_message("assistant"):
        st.markdown(ans)

        # 如果有翻译过程，展示一下（增加可解释性）
        if is_chinese:
            st.caption(f"ℹ️ 内部检索词: *{search_query}*")

        # 显示参考来源
        if final_refs:
            with st.expander("📚 参考医学证据"):
                for ref in final_refs:
                    st.write(f"- {ref}")
                st.divider()
                st.text("原始片段预览：")
                st.code(context_str[:500] + "...", language="text")

    st.session_state.messages.append({"role": "assistant", "content": ans})