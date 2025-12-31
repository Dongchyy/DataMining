# generate_health_data.py
import os
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict

# === 配置 ===
TOTAL_FILES = 5000  # 生成5000个HTML文件
DATA_DIR = os.path.join("data", "html")  # 修改为正确的路径
os.makedirs(DATA_DIR, exist_ok=True)

# === 扩展语料库 ===
foods = {
    "水果": ["蓝莓", "草莓", "覆盆子", "苹果", "香蕉", "橙子", "葡萄", "猕猴桃", "芒果", "菠萝",
             "西瓜", "哈密瓜", "樱桃", "桃子", "梨", "柚子", "柠檬", "牛油果", "榴莲", "火龙果"],
    "蔬菜": ["西兰花", "菠菜", "羽衣甘蓝", "胡萝卜", "番茄", "青椒", "黄瓜", "芹菜", "芦笋", "洋葱",
             "大蒜", "生姜", "红薯", "土豆", "南瓜", "蘑菇", "秋葵", "豆芽", "生菜", "卷心菜"],
    "谷物": ["燕麦", "藜麦", "糙米", "全麦面包", "玉米", "小米", "大麦", "黑麦", "荞麦", "薏米"],
    "蛋白质": ["三文鱼", "鸡胸肉", "鸡蛋", "豆腐", "黑豆", "扁豆", "鹰嘴豆", "金枪鱼", "虾", "牛肉",
               "猪肉", "羊肉", "鸭肉", "奶酪", "酸奶", "牛奶", "杏仁", "核桃", "花生", "腰果"],
    "饮品": ["绿茶", "红茶", "咖啡", "红酒", "豆浆", "椰子水", "姜茶", "菊花茶", "枸杞茶", "玫瑰花茶"]
}

nutrients = {
    "维生素": ["维生素A", "维生素B1", "维生素B2", "维生素B6", "维生素B12", "维生素C", "维生素D",
               "维生素E", "维生素K", "叶酸", "烟酸", "生物素"],
    "矿物质": ["钙", "铁", "锌", "镁", "钾", "钠", "磷", "硒", "铜", "锰", "碘", "氟"],
    "其他": ["蛋白质", "膳食纤维", "Omega-3脂肪酸", "抗氧化剂", "益生菌", "花青素", "类黄酮",
             "多酚", "儿茶素", "白藜芦醇", "番茄红素", "β-胡萝卜素", "叶绿素"]
}

benefits = {
    "心血管": ["降低心脏病风险", "降低血压", "降低胆固醇", "改善血液循环", "预防动脉硬化"],
    "免疫": ["增强免疫力", "抗炎作用", "抗病毒", "抗菌", "减少过敏反应"],
    "消化": ["改善肠道健康", "促进消化", "预防便秘", "平衡肠道菌群", "缓解胃痛"],
    "大脑": ["提升记忆力", "改善注意力", "预防老年痴呆", "缓解焦虑", "改善睡眠质量"],
    "代谢": ["稳定血糖", "促进新陈代谢", "帮助减肥", "增加饱腹感", "燃烧脂肪"],
    "美容": ["抗衰老", "美白皮肤", "减少皱纹", "改善头发质量", "增强指甲硬度"],
    "其他": ["增强骨骼强度", "改善视力", "保护肝脏", "排毒养颜", "缓解疲劳"]
}

# === 作者和来源列表 ===
authors = ["张医生", "李营养师", "王健康", "陈养生", "刘食疗", "赵教授", "孙专家", "周研究员"]
sources = ["健康时报", "营养学会", "医学杂志", "健康网站", "研究机构", "医院专栏", "专家讲座"]

# === 模板系统 ===
title_templates = [
    "{food}的营养价值大揭秘：{nutrient}含量惊人！",
    "为什么营养师都推荐{food}？{benefit}的功效不可忽视",
    "每天吃{food}，一个月后身体会发生这些变化",
    "{food}中的{nutrient}：{benefit}的天然来源",
    "科学研究表明：{food}能有效{benefit}",
    "{food}的正确吃法：这样吃才能{benefit}",
    "警惕！{food}的这些禁忌你一定要知道",
    "从中医角度看{food}：{benefit}的养生智慧",
    "{food} vs {food2}：哪种更{benefit}？",
    "不同人群如何食用{food}？专家给出建议"
]

intro_templates = [
    "在众多健康食品中，{food}因其独特的营养价值备受关注。",
    "随着健康意识的提高，{food}逐渐成为餐桌上的常客。",
    "近年来研究发现，{food}对健康的益处远超我们想象。",
    "中医古籍早有记载，{food}具有{benefit}的功效。",
    "在西方营养学中，{food}被称为'超级食物'之一。"
]

content_templates = [
    "{food}富含丰富的{nutrient}，这种营养成分对于{benefit}至关重要。",
    "研究表明，每天摄入适量的{food}可以显著{benefit}。",
    "专家建议，将{food}与{other_food}搭配食用，效果更佳。",
    "需要注意的是，{food}虽然有益，但{precaution}。",
    "不同烹饪方式会影响{food}中{nutrient}的保留率。",
    "对于特定人群如{group}，食用{food}需要特别注意{point}。",
    "最新研究显示，{food}中的{nutrient}还能帮助{other_benefit}。"
]

tip_templates = [
    "建议每天食用{food}约{amount}克，以达到最佳效果。",
    "选购{food}时，应注意{selection_tip}。",
    "储存{food}的方法：{storage_tip}。",
    "最佳食用时间：{best_time}。",
    "不适合食用{food}的人群：{avoid_group}。"
]

# === 实用信息 ===
amounts = ["50-100", "100-150", "150-200", "200-250", "250-300"]
groups = ["孕妇", "儿童", "老年人", "糖尿病患者", "高血压患者", "肾病患者", "过敏体质者"]
cooking_methods = ["生吃", "蒸煮", "炖汤", "炒制", "烘焙", "榨汁", "凉拌"]
selection_tips = ["选择颜色鲜艳的", "闻起来有清香的", "表面光滑无斑点的", "手感坚实的", "产地明确的"]
storage_tips = ["冷藏保存", "避光干燥处存放", "不要清洗直接保存", "用保鲜膜包裹", "尽快食用"]
precautions = ["不宜过量食用", "某些人群需谨慎", "注意食物相克", "避免与特定药物同服", "可能引起过敏"]
points = ["适量", "咨询医生", "避免过量", "注意烹饪方式", "观察身体反应"]


# === 生成文章函数 ===
def generate_article(article_id: int) -> Dict:
    """生成一篇完整的健康文章"""

    # 随机选择食物类别和具体食物
    food_category = random.choice(list(foods.keys()))
    food = random.choice(foods[food_category])
    food2 = random.choice(foods[random.choice(list(foods.keys()))])
    while food2 == food:
        food2 = random.choice(foods[random.choice(list(foods.keys()))])

    # 随机选择营养成分
    nutrient_category = random.choice(list(nutrients.keys()))
    nutrient = random.choice(nutrients[nutrient_category])
    nutrient2 = random.choice(nutrients[random.choice(list(nutrients.keys()))])

    # 随机选择益处
    benefit_category = random.choice(list(benefits.keys()))
    benefit = random.choice(benefits[benefit_category])
    other_benefit = random.choice(benefits[random.choice(list(benefits.keys()))])

    # 随机选择其他元素
    other_food = random.choice(foods[random.choice(list(foods.keys()))])
    author = random.choice(authors)
    source = random.choice(sources)
    group = random.choice(groups)
    other_group = random.choice(groups)
    amount = random.choice(amounts)
    cooking = random.choice(cooking_methods)
    selection_tip = random.choice(selection_tips)
    storage_tip = random.choice(storage_tips)
    precaution = random.choice(precautions)
    point = random.choice(points)

    # 生成标题
    title_template = random.choice(title_templates)
    title = title_template.format(
        food=food,
        food2=food2,
        nutrient=nutrient,
        benefit=benefit
    )

    # 生成发布时间（随机在过去一年内）
    publish_date = datetime.now() - timedelta(days=random.randint(0, 365))

    # 生成正文内容
    intro = random.choice(intro_templates).format(food=food, benefit=benefit)

    # 生成3-5个内容段落
    content_paragraphs = [intro]
    for _ in range(random.randint(3, 5)):
        template = random.choice(content_templates)
        # 根据模板选择不同的参数
        if "{precaution}" in template:
            paragraph = template.format(
                food=food,
                precaution=precaution
            )
        elif "{group}" in template and "{point}" in template:
            paragraph = template.format(
                food=food,
                group=group,
                point=point
            )
        elif "{other_benefit}" in template:
            paragraph = template.format(
                food=food,
                nutrient=nutrient,
                other_benefit=other_benefit
            )
        elif "{other_food}" in template:
            paragraph = template.format(
                food=food,
                other_food=other_food
            )
        elif "{nutrient}" in template and "{benefit}" in template:
            paragraph = template.format(
                food=food,
                nutrient=nutrient,
                benefit=benefit
            )
        else:
            # 默认处理
            paragraph = template.format(
                food=food,
                nutrient=nutrient,
                benefit=benefit,
                other_food=other_food,
                precaution=precaution,
                group=group,
                point=point,
                other_benefit=other_benefit
            )
        content_paragraphs.append(paragraph)

    # 生成小贴士
    tips = []
    for _ in range(random.randint(2, 3)):
        tip_template = random.choice(tip_templates)
        if "{best_time}" in tip_template:
            tip = tip_template.format(
                food=food,
                amount=amount,
                selection_tip=selection_tip,
                storage_tip=storage_tip,
                best_time=random.choice(["早餐", "午餐前", "晚餐后", "两餐之间"]),
                avoid_group=other_group
            )
        else:
            tip = tip_template.format(
                food=food,
                amount=amount,
                selection_tip=selection_tip,
                storage_tip=storage_tip,
                avoid_group=other_group
            )
        tips.append(tip)

    # 组合完整内容
    full_content = "\n".join(content_paragraphs + ["\n小贴士："] + tips)

    # 修复：避免在f-string表达式中使用反斜杠
    # 将段落分割成列表
    paragraphs = full_content.splitlines()
    # 为每个段落添加<p>标签
    paragraph_tags = "".join(f'<p>{p}</p>' for p in paragraphs if p.strip())

    # 生成HTML结构
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="author" content="{author}">
    <meta name="source" content="{source}">
</head>
<body>
    <h1 class="rich_media_title">{title}</h1>
    <em id="publish_time">{publish_date.strftime('%Y-%m-%d %H:%M:%S')}</em>
    <div class="content">
        {paragraph_tags}
    </div>
    <div class="article_info">
        <p><strong>作者：</strong>{author}</p>
        <p><strong>来源：</strong>{source}</p>
        <p><strong>关键词：</strong>{food}, {nutrient}, {benefit}, {food_category}</p>
    </div>
</body>
</html>"""

    return {
        "id": article_id,
        "title": title,
        "food": food,
        "food_category": food_category,
        "nutrient": nutrient,
        "benefit": benefit,
        "author": author,
        "source": source,
        "publish_date": publish_date.strftime('%Y-%m-%d'),
        "content": full_content,
        "html": html_content
    }


# === 生成疾病相关文章（为了多样性） ===
def generate_disease_article(article_id: int) -> Dict:
    """生成疾病预防相关的文章"""
    diseases = ["高血压", "糖尿病", "心脏病", "肥胖症", "骨质疏松", "贫血", "痛风", "脂肪肝"]
    prevention_foods = {
        "高血压": ["香蕉", "芹菜", "菠菜", "大蒜", "燕麦"],
        "糖尿病": ["苦瓜", "黄瓜", "洋葱", "黑木耳", "全麦食品"],
        "心脏病": ["三文鱼", "坚果", "橄榄油", "蓝莓", "黑巧克力"],
        "肥胖症": ["绿茶", "苹果", "辣椒", "豆腐", "魔芋"],
        "骨质疏松": ["牛奶", "芝麻", "虾皮", "豆制品", "海带"],
        "贫血": ["红枣", "猪肝", "菠菜", "黑芝麻", "红豆"],
        "痛风": ["樱桃", "芹菜", "冬瓜", "薏米", "土豆"],
        "脂肪肝": ["枸杞", "山楂", "绿茶", "燕麦", "豆制品"]
    }

    disease = random.choice(diseases)
    food = random.choice(prevention_foods[disease])

    title = f"{disease}患者必看：{food}的预防作用"

    # 生成疾病文章内容
    paragraphs = [
        f"对于{disease}患者来说，饮食控制至关重要。",
        f"研究发现，{food}中含有多种有益成分，能够帮助{disease}患者改善症状。",
        f"专家建议，{disease}患者可以适当增加{food}的摄入量。",
        "但需要注意的是，任何食物的摄入都应适量，过量食用反而可能带来不利影响。",
        "最好在医生或营养师的指导下制定个性化的饮食计划。"
    ]

    paragraph_tags = "".join(f'<p>{p}</p>' for p in paragraphs)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<body>
    <h1 class="rich_media_title">{title}</h1>
    <em id="publish_time">{(datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')}</em>
    <div class="content">
        {paragraph_tags}
    </div>
</body>
</html>"""

    return {
        "id": article_id,
        "title": title,
        "type": "disease",
        "disease": disease,
        "food": food,
        "html": html_content
    }


# === 生成食谱文章 ===
def generate_recipe_article(article_id: int) -> Dict:
    """生成健康食谱文章"""
    meals = ["早餐", "午餐", "晚餐", "加餐", "宵夜"]
    recipe_types = ["低卡", "高蛋白", "素食", "快手", "养生"]

    meal = random.choice(meals)
    recipe_type = random.choice(recipe_types)
    main_food = random.choice(foods[random.choice(list(foods.keys()))])
    side_food = random.choice(foods[random.choice(list(foods.keys()))])

    title = f"{meal}{recipe_type}食谱：{main_food}搭配{side_food}"

    # 生成食谱文章内容
    paragraphs = [
        f"今天为大家推荐一款适合{meal}的{recipe_type}食谱。",
        f"<strong>主要食材：</strong>{main_food}、{side_food}",
        "<strong>做法：</strong>",
        f"1. 将{main_food}清洗干净，切成适当大小",
        f"2. {side_food}处理备用",
        f"3. 用少量橄榄油翻炒{main_food}",
        f"4. 加入{side_food}和适量调味料",
        "5. 翻炒均匀即可出锅",
        f"<strong>营养提示：</strong>这款食谱富含多种营养素，适合追求健康饮食的人群。"
    ]

    paragraph_tags = "".join(f'<p>{p}</p>' for p in paragraphs)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<body>
    <h1 class="rich_media_title">{title}</h1>
    <em id="publish_time">{(datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')}</em>
    <div class="content">
        {paragraph_tags}
    </div>
</body>
</html>"""

    return {
        "id": article_id,
        "title": title,
        "type": "recipe",
        "meal": meal,
        "recipe_type": recipe_type,
        "main_food": main_food,
        "side_food": side_food,
        "html": html_content
    }


# === 主生成函数 ===
def generate_health_data(total_files: int = TOTAL_FILES):
    print(f"🚀 开始生成 {total_files} 条健康饮食数据...")
    print("=" * 50)

    stats = {
        "普通文章": 0,
        "疾病预防": 0,
        "食谱": 0
    }

    for i in range(total_files):
        try:
            # 随机选择文章类型（70%普通，15%疾病，15%食谱）
            rand_type = random.random()

            if rand_type < 0.7:
                article = generate_article(i + 1)
                stats["普通文章"] += 1
            elif rand_type < 0.85:
                article = generate_disease_article(i + 1)
                stats["疾病预防"] += 1
            else:
                article = generate_recipe_article(i + 1)
                stats["食谱"] += 1

            # 保存HTML文件
            filename = f"health_article_{i + 1:04d}.html"
            filepath = os.path.join(DATA_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(article["html"])

            # 每生成100个文件显示进度
            if (i + 1) % 100 == 0:
                print(f"✅ 已生成 {i + 1} 个文件...")

        except Exception as e:
            print(f"⚠️ 生成第{i + 1}个文件时出错: {e}")
            continue

    print("=" * 50)
    print(f"🎉 任务完成！共生成 {total_files} 个HTML文件")
    print("📊 文章类型统计：")
    for article_type, count in stats.items():
        print(f"   {article_type}: {count} 篇 ({(count / total_files) * 100:.1f}%)")
    print(f"📁 文件保存位置: {DATA_DIR}")
    print("👉 下一步：运行 preprocess.py 进行数据预处理")

    # 生成统计文件
    stats_file = os.path.join(DATA_DIR, "generation_stats.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_files": total_files,
            "stats": stats,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "food_categories": list(foods.keys()),
            "total_food_items": sum(len(items) for items in foods.values())
        }, f, ensure_ascii=False, indent=2)

    return stats


# === 生成测试用的少量数据（快速验证） ===
def generate_sample_data(sample_size: int = 100):
    """生成少量样本数据用于快速测试"""
    print(f"🧪 生成 {sample_size} 条样本数据用于测试...")
    return generate_health_data(sample_size)


if __name__ == "__main__":
    # 生成完整数据集（5000条）
    generate_health_data(5000)

    # 如果只想生成少量测试数据：
    # generate_sample_data(100)