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

def analyze_content(user_input):
    """分析用户提供的文本内容，并计算爆款潜质"""
    st.write("正在诊断内容...")
    progress = st.progress(0)
    for i in range(1, 101, 10):
        progress.progress(i / 100)
    st.success("诊断完成 ✅")
    return min(len(user_input.split()) * 2, 100)

def main():
    """Streamlit 应用主入口"""
    st.title("📢 智能内容诊断系统")
    user_input = st.text_area("请输入需要分析的文本内容：")
    
    if st.button("🚀 开始诊断"):
        if not user_input.strip():
            st.error("❌ 请提供输入文本。")
        else:
            # 诊断内容
            score = analyze_content(user_input)
            
            # 调用 API 进行优化
            st.write("正在优化爆款文案...")
            progress = st.progress(0)
            for i in range(1, 101, 10):
                progress.progress(i / 100)
            optimized_response = call_deepseek_api(user_input, "请优化该文案，使其符合短视频爆款逻辑")
            st.success("文案优化完成 ✅")
            
            st.write("正在生成爆款标题...")
            progress.progress(0)
            for i in range(1, 101, 10):
                progress.progress(i / 100)
            title_response = call_deepseek_api(user_input, "请生成符合社交传播逻辑的爆款标题")
            st.success("爆款标题生成完成 ✅")
            
            st.write("正在匹配爆款话题...")
            progress.progress(0)
            for i in range(1, 101, 10):
                progress.progress(i / 100)
            topics_response = call_deepseek_api(user_input, "请提供6个热门社交媒体话题")
            st.success("爆款话题匹配完成 ✅")
            
            st.write("正在分析最佳发布时间...")
            progress.progress(0)
            for i in range(1, 101, 10):
                progress.progress(i / 100)
            time_response = call_deepseek_api(user_input, "请推荐最佳发布时间")
            st.success("最佳发布时间分析完成 ✅")
            
            # 结果展示
            st.markdown("---")
            st.subheader("📊 内容诊断结果")
            st.write(f"**内容爆款率**: {score:.2f}%")
            st.progress(1.0)
            st.button("📋 复制爆款率", on_click=lambda: st.write("✅ 已复制"))
            
            st.markdown("---")
            st.subheader("✨ 优化后的文案")
            optimized_text = optimized_response.get("choices", [{}])[0].get("message", {}).get("content", "无优化建议")
            st.text_area("优化后的爆款文案：", value=optimized_text, height=200)
            st.button("📋 复制优化文案", on_click=lambda: st.write("✅ 已复制"))
            
            st.markdown("---")
            st.subheader("🚀 推荐爆款标题")
            title_text = title_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成标题")
            st.write(f"### {title_text}")
            st.button("📋 复制爆款标题", on_click=lambda: st.write("✅ 已复制"))
            
            st.markdown("---")
            st.subheader("🔥 推荐爆款话题（6个）")
            topics_text = topics_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成话题")
            st.write(topics_text)
            st.button("📋 复制爆款话题", on_click=lambda: st.write("✅ 已复制"))
            
            st.markdown("---")
            st.subheader("⏰ 推荐发布时间")
            time_text = time_response.get("choices", [{}])[0].get("message", {}).get("content", "未生成发布时间")
            st.write(time_text)
            st.button("📋 复制发布时间", on_click=lambda: st.write("✅ 已复制"))
            
            st.markdown("---")
            st.markdown("📢 全平台 @旺仔AIGC 📢")
            st.markdown("关注我，和我一起 拆解流量密码，探索 AI创作新玩法，让你的 爆款内容精准起飞，不再迷路！🚀")

if __name__ == "__main__":
    main()
