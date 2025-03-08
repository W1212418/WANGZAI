import re
import requests
import json
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
        "文案能力": {"pattern": ["文案", "营销", "推广"], "weight": 1.0},
        "工具掌握度": {"pattern": ["DeepSeek", "AI工具", "数据分析"], "weight": 0.9},
        "路径可行性": {"pattern": ["行业", "竞争", "市场"], "weight": 0.8},
        "客单价定位": {"pattern": ["定价", "消费", "承受力"], "weight": 0.7},
        "政策合规性": {"pattern": ["平台规则", "违禁词", "政策"], "weight": 0.6}
    }
    
    scores = {}
    for key, value in evaluation_criteria.items():
        count = sum([len(re.findall(pattern, user_input, re.IGNORECASE)) for pattern in value["pattern"]])
        scores[key] = min(count * value["weight"] * 10, 100)
    
    scores["爆款潜质"] = np.mean(list(scores.values()))  # 计算爆款潜质
    return scores

def visualize_results(scores):
    """使用 Matplotlib 生成五角形雷达图"""
    labels = list(scores.keys())
    values = list(scores.values())
    values += values[:1]  # 形成闭合图形
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='b', alpha=0.3)
    ax.plot(angles, values, color='b', linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    
    st.pyplot(fig)

def main():
    """Streamlit 应用主入口"""
    st.title("智能内容诊断系统")
    user_input = st.text_area("请输入需要分析的文本内容：")
    
    if st.button("开始诊断"):
        if not user_input.strip():
            st.error("请提供输入文本。")
        else:
            with st.spinner("正在检测，请稍候..."):
                deepseek_response = call_deepseek_api(user_input)
                scores = analyze_content(user_input)
                
                if "error" in deepseek_response:
                    st.error(deepseek_response["error"])
                else:
                    visualize_results(scores)
                    
                    st.subheader("爆款潜质分析")
                    st.progress(scores["爆款潜质"] / 100)
                    st.write(f"爆款潜质: {scores['爆款潜质']:.2f}%")
                    
                    st.subheader("优化后的文案建议")
                    st.text_area("请修改文案后粘贴到此处进行优化", value=user_input, height=200)
                    
                    results_df = pd.DataFrame({"评估维度": scores.keys(), "得分": scores.values()})
                    st.write(results_df)
                    
                    if st.button("导出历史记录"):
                        results_df.to_csv("diagnosis_history.csv", index=False)
                        st.success("历史记录已导出")

if __name__ == "__main__":
    main()
