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

def main():
    """Streamlit 应用主入口"""
    st.title("📢 智能内容诊断系统")
    user_input = st.text_area("请输入需要分析的文本内容：")

    if "status" not in st.session_state:
        st.session_state["status"] = [
            "内容分析",
            "优化爆款文案",
            "生成爆款标题",
            "分析最佳发布时间"
        ]

    status_list = st.session_state["status"]
    status_display = [st.empty() for _ in status_list]  # 每个状态单独一行

    if st.button("🚀 开始诊断"):
        if not user_input.strip():
            st.error("❌ 请提供输入文本。")
        else:
            for i, task in enumerate(status_list):
                # 更新当前步骤状态
                status_list[i] = f"⏳ 正在{task}，请稍候..."
                for j, display in enumerate(status_display):
                    display.write(f"**{status_list[j]}**" if "⏳" in status_list[j] else status_list[j])
                time.sleep(2)

                if i == 0:
                    score = min(len(user_input.split()) * 2, 100)
                    st.write(f"**内容爆款率**: {score:.2f}%")
                    st.progress(score / 100)
                elif i == 1:
                    optimized_response = call_deepseek_api(user_input, "请优化该文案，使其符合短视频爆款逻辑")
                    optimized_text = optimized_response.get("choices", [{}])[0].get("message", {}).get("content", "无优化建议")
                elif i == 2:
                    title_response = call_deepseek_api(user_input, "请生成符合社交传播逻辑的爆款标题")
                    title_text = title_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成标题")
                elif i == 3:
                    time_response = call_deepseek_api(user_input, "请推荐最佳发布时间")
                    time_text = time_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成发布时间")
                
                # 任务完成，更新状态
                status_list[i] = f"✅ {task}完成"
                for j, display in enumerate(status_display):
                    display.write(f"**{status_list[j]}**" if '✅' in status_list[j] else status_list[j])
                time.sleep(1)
            
            # 结果展示
            st.markdown("---")
            st.subheader("✨ 优化后的文案")
            st.text_area("优化后的爆款文案：", value=optimized_text, height=200)
            
            st.markdown("---")
            st.subheader("🚀 推荐爆款标题")
            st.write(f"### {title_text}")
            
            st.markdown("---")
            st.subheader("⏰ 推荐发布时间")
            st.write(time_text)
            
            st.markdown("---")
            st.markdown("📢 全平台 @旺仔AIGC 📢")
            st.markdown("关注我，和我一起 拆解流量密码，探索 AI创作新玩法，让你的 爆款内容精准起飞，不再迷路！🚀")

if __name__ == "__main__":
    main()
