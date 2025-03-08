import re
import requests
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 硬编码 DeepSeek API Key（⚠️ 仅用于测试，建议使用环境变量存储）
API_KEY = "sk-e4eaafa61ff349cbb93e554b64c22dcb"

# 更新 API 端点
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(text):
    """调用 DeepSeek API 进行内容分析"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": text}
        ],
        "stream": False
    })
    response = requests.post(BASE_URL, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"请求失败: {response.status_code}, 错误信息: {response.text}"}

def analyze_content(user_input):
    """分析用户提供的文本内容，并根据关键评估维度进行诊断"""
    evaluation_criteria = {
        "文案能力": {"pattern": ["文案", "营销", "推广"], "weight": 1.0, "guidance": "加强文案吸引力，结合故事化表达或痛点共鸣，提高用户关注度。"},
        "工具掌握度": {"pattern": ["DeepSeek", "AI工具", "数据分析"], "weight": 0.9, "guidance": "提升AI工具的熟练度，合理使用数据分析工具优化内容策略。"},
        "路径可行性": {"pattern": ["行业", "竞争", "市场"], "weight": 0.8, "guidance": "关注市场趋势，分析行业竞争格局，选择最优路径提升变现效率。"},
        "客单价定位": {"pattern": ["定价", "消费", "承受力"], "weight": 0.7, "guidance": "优化定价策略，确保符合目标用户消费能力，同时提高产品价值感。"},
        "政策合规性": {"pattern": ["平台规则", "违禁词", "政策"], "weight": 0.6, "guidance": "确保内容符合平台合规要求，避免敏感词汇，减少违规风险。"}
    }
    
    scores = {}
    guidance_notes = {}
    for key, value in evaluation_criteria.items():
        count = sum([len(re.findall(pattern, user_input, re.IGNORECASE)) for pattern in value["pattern"]])
        scores[key] = min(count * value["weight"] * 10, 100)
        guidance_notes[key] = value["guidance"]
    
    return scores, guidance_notes

def visualize_results(scores):
    """将评估结果可视化"""
    labels = list(scores.keys())
    values = list(scores.values())
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    values += values[:1]
    angles += angles[:1]
    
    ax.fill(angles, values, color='b', alpha=0.3)
    ax.plot(angles, values, color='b', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    
    plt.title("内容诊断雷达图")
    st.pyplot(fig)

def main():
    """Streamlit 应用主入口"""
    st.title("智能内容诊断系统")
    user_input = st.text_area("请输入需要分析的文本内容：")
    
    if st.button("开始诊断"):
        if not user_input.strip():
            st.error("请提供输入文本。")
        else:
            deepseek_response = call_deepseek_api(user_input)
            scores, guidance_notes = analyze_content(user_input)
            
            if "error" in deepseek_response:
                st.error(deepseek_response["error"])
            else:
                visualize_results(scores)
                
                results_df = pd.DataFrame({"评估维度": scores.keys(), "得分": scores.values(), "优化建议": guidance_notes.values()})
                st.write(results_df)
                
                if st.button("导出历史记录"):
                    results_df.to_csv("diagnosis_history.csv", index=False)
                    st.success("历史记录已导出")

if __name__ == "__main__":
    main()
