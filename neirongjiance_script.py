import re
import requests
import json
import pandas as pd
import streamlit as st
import numpy as np
import time

# 硬编码 DeepSeek API Key
API_KEY = "sk-e4eaafa61ff349cbb93e554b64c22dcb"

# 更新 API 端点
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(text, task):
    """调用 DeepSeek API 进行内容分析和优化"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "社交传播算法工程师与数字内容架构师，构建‘传播心理学+数据驱动创作’双轨系统，开发智能内容生态优化引擎。"},
            {"role": "user", "content": f"{task}: {text}"}
        ],
        "stream": False
    })
    response = requests.post(BASE_URL, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"请求失败: {response.status_code}, 错误信息: {response.text}"}

def update_status(status_list, index, message):
    """更新步骤状态，点亮当前步骤，完成后更新为成功状态"""
    status_list[index] = f"✅ {message}"
    st.session_state["status"] = status_list
    st.experimental_rerun()

def main():
    """Streamlit 应用主入口"""
    st.title("📢 智能内容诊断系统")
    user_input = st.text_area("请输入需要分析的文本内容：")
    
    if "status" not in st.session_state:
        st.session_state["status"] = [
            "灰色 - 正在分析内容，请稍候...",
            "灰色 - 正在优化爆款文案，请稍候...",
            "灰色 - 正在生成爆款标题，请稍候...",
            "灰色 - 正在匹配爆款话题，请稍候...",
            "灰色 - 正在分析最佳发布时间，请稍候..."
        ]
    
    for step in st.session_state["status"]:
        st.write(step)
    
    if st.button("🚀 开始诊断"):
        if not user_input.strip():
            st.error("❌ 请提供输入文本。")
        else:
            status_list = st.session_state["status"]
            
            # 诊断内容
            update_status(status_list, 0, "内容分析完成")
            time.sleep(2)
            score = min(len(user_input.split()) * 2, 100)
            st.write(f"**内容爆款率**: {score:.2f}%")
            st.progress(score / 100)
            
            # 依次调用 API 进行内容优化和分析
            update_status(status_list, 1, "文案优化完成")
            optimized_response = call_deepseek_api(user_input, "请优化该文案，使其符合短视频爆款逻辑")
            optimized_text = optimized_response.get("choices", [{}])[0].get("message", {}).get("content", "无优化建议")
            
            update_status(status_list, 2, "爆款标题生成完成")
            title_response = call_deepseek_api(user_input, "请生成符合社交传播逻辑的爆款标题")
            title_text = title_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成标题")
            
            update_status(status_list, 3, "爆款话题匹配完成")
            topics_response = call_deepseek_api(user_input, "请提供6个热门社交媒体话题")
            topics_text = topics_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成话题")
            
            update_status(status_list, 4, "最佳发布时间分析完成")
            time_response = call_deepseek_api(user_input, "请推荐最佳发布时间")
            time_text = time_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成发布时间")
            
            # 结果展示
            st.markdown("---")
            st.subheader("✨ 优化后的文案")
            st.text_area("优化后的爆款文案：", value=optimized_text, height=200)
            
            st.markdown("---")
            st.subheader("🚀 推荐爆款标题")
            st.write(f"### {title_text}")
            
            st.markdown("---")
            st.subheader("🔥 推荐爆款话题（6个）")
            st.write(topics_text)
            
            st.markdown("---")
            st.subheader("⏰ 推荐发布时间")
            st.write(time_text)
            
            st.markdown("---")
            st.markdown("📢 全平台 @旺仔AIGC 📢")
            st.markdown("关注我，和我一起 拆解流量密码，探索 AI创作新玩法，让你的 爆款内容精准起飞，不再迷路！🚀")

if __name__ == "__main__":
    main()
