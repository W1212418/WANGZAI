import re
import requests
import json
import pandas as pd
import streamlit as st
import numpy as np

# 硬编码 DeepSeek API Key（⚠️ 仅用于测试，建议使用环境变量存储）
API_KEY = "sk-e4eaafa61ff349cbb93e554b64c22dcb"

# 更新 API 端点
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(text, task):
    """调用 DeepSeek API 进行内容分析和优化"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{task}: {text}"}
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

def main():
    """Streamlit 应用主入口"""
    st.title("智能内容诊断系统")
    user_input = st.text_area("请输入需要分析的文本内容：")
    
    if st.button("开始诊断"):
        if not user_input.strip():
            st.error("请提供输入文本。")
        else:
            with st.spinner("正在检测，请稍候..."):
                scores = analyze_content(user_input)
                optimized_response = call_deepseek_api(user_input, "请基于抖音短视频爆款逻辑优化该文案，并符合黄金3秒原则，按照爆款公式进行优化")
                title_response = call_deepseek_api(user_input, "请生成符合短视频爆款逻辑的爆款标题")
                topics_response = call_deepseek_api(user_input, "请提供6个与该内容相关的抖音爆款话题")
                time_response = call_deepseek_api(user_input, "请推荐适合该内容发布时间")
                
                if "error" in optimized_response:
                    st.error(optimized_response["error"])
                else:
                    st.subheader("各项指标得分")
                    for key, value in scores.items():
                        st.write(f"{key}: {value:.2f}%")
                        st.progress(value / 100)
                    
                    st.subheader("优化后的文案")
                    optimized_text = optimized_response.get("choices", [{}])[0].get("message", {}).get("content", "无优化建议")
                    st.text_area("优化后的文案：", value=optimized_text, height=200)
                    
                    st.subheader("推荐爆款标题")
                    title_text = title_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成标题")
                    st.write(title_text)
                    
                    st.subheader("推荐爆款话题（6个）")
                    topics_text = topics_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成话题")
                    st.write(topics_text)
                    
                    st.subheader("推荐发布时间")
                    time_text = time_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成发布时间")
                    st.write(time_text)
                    
                    results_df = pd.DataFrame({"评估维度": scores.keys(), "得分": scores.values()})
                    st.write(results_df)
                    
                    if st.button("导出历史记录"):
                        results_df.to_csv("diagnosis_history.csv", index=False)
                        st.success("历史记录已导出")

if __name__ == "__main__":
    main()
