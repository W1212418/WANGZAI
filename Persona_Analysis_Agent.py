import re
import requests
import json
import pandas as pd
import streamlit as st
import numpy as np
import time
import os

# 硬编码 DeepSeek API Key
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-e4eaafa61ff349cbb93e554b64c22dcb")

# 更新 API 端点
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(text, task):
    """调用 DeepSeek API 进行账号人设分析和规划"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": "你是一名专业的账号人设规划师，负责分析账号定位、竞品差异化和受众特征。"},
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
    st.title("📢 DeepSeek 账号人设规划系统")
    
    with st.form("user_input_form"):
        account_name = st.text_input("📌 账号名称")
        industry = st.text_input("🏢 所在行业")
        core_advantages = st.text_area("💡 核心优势 (换行分隔)").split("\n")
        target_audience = st.text_area("🎯 目标人群 (请描述年龄、地区、兴趣点)")
        competitor_accounts = st.text_area("📊 竞品账号 (换行分隔)").split("\n")
        operation_goal = st.selectbox("🚀 运营目标", ["粉丝增长", "品牌曝光", "产品销售"])
        submit_button = st.form_submit_button("🔍 生成人设分析报告")
    
    if submit_button:
        if not account_name or not industry or not core_advantages or not target_audience or not competitor_accounts:
            st.error("❌ 请完整填写所有必填项")
        else:
            st.write("⏳ 正在分析账号人设，请稍候...")
            
            # 组装输入数据
            input_data = {
                "account_name": account_name,
                "industry": industry,
                "core_advantages": core_advantages,
                "target_audience": target_audience,
                "competitor_accounts": competitor_accounts,
                "operation_goal": operation_goal
            }
            
            # 账号人设分析
            analysis_response = call_deepseek_api(json.dumps(input_data, ensure_ascii=False), "账号人设分析")
            analysis_result = analysis_response.get("choices", [{}])[0].get("message", {}).get("content", "分析失败")
            st.success("✅ 账号人设分析完成")
            
            # 结果展示
            st.markdown("---")
            st.subheader("📊 账号人设分析报告")
            st.write(analysis_result)
            
            st.markdown("---")
            st.markdown("📢 全平台 @旺仔AIGC 📢")
            st.markdown("关注我，和我一起 拆解流量密码，探索 AI创作新玩法，让你的 账号精准定位，内容不再迷路！🚀")

if __name__ == "__main__":
    main()
