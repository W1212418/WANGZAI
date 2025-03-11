import re
import aiohttp
import asyncio
import json
import pandas as pd
import numpy as np
import time
import os
import sqlite3
from datetime import datetime
from json import JSONDecodeError
import streamlit as st
import altair as alt
import requests

API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-e4eaafa61ff349cbb93e554b64c22dcb")
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

VALID_INDUSTRIES = ["美妆", "教育", "3C数码", "母婴", "美食"]

INDUSTRY_PROMPTS = {
    "美妆": "强调成分分析和使用场景",
    "教育": "集中学习效果视觉化",
    "3C数码": "关注参数对比和实测体验",
    "母婴": "注重安全性和用户体验",
    "美食": "突出口感和地域文化"
}

PLATFORM_RULES = {
    "抖音": {"时长": "15-60秒", "标题规则": "带争议点"},
    "小红书": {"笔记结构": "封面+标记点", "标题规则": "体验分享"}
}

RISK_REPLACEMENTS = {
    "最": "可能",
    "第一": "前列",
    "绝对": "建议"
}

async def compare_competitors_async(competitor_list, platform):
    data = []
    async with aiohttp.ClientSession() as session:
        tasks = [get_account_data(session, platform, comp) for comp in competitor_list]
        results = await asyncio.gather(*tasks)
        for result in results:
            data.append({
                "账号名称": result.get("昵称", "未知"),
                "平台": platform,
                "粉丝量级": result.get("粉丝数", 0),
                "内容数量": result.get("作品数", result.get("笔记数", result.get("视频数", 0)))
            })
    df = pd.DataFrame(data)
    return df

def call_deepseek_api(input_data, task, industry=""):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": f"你是一名{industry}领域账号规划师，需特别关注{INDUSTRY_PROMPTS.get(industry, '通用策略')}。"},
            {"role": "user", "content": f"{task}: {input_data}"}
        ],
        "stream": False
    })
    response = requests.post(BASE_URL, headers=headers, data=payload)
    try:
        return response.json()
    except JSONDecodeError:
        return {}

def parse_analysis_result(raw_result):
    return {
        "人设定位": raw_result.get("persona", "未找到"),
        "差异点分析": raw_result.get("differentiation", []),
        "风险提示": raw_result.get("risk", "无")
    }

def parse_topics(raw_text):
    return re.findall(r'\d+\.\s+(.*)', raw_text)

def generate_calendar(topics):
    dates = pd.date_range(start=datetime.today(), periods=len(topics))
    return pd.DataFrame({
        "日期": dates,
        "选题": topics,
        "平台": ["抖音" if i % 2 == 0 else "小红书" for i in range(len(topics))]
    })

def save_analysis_history(analysis_data):
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS histories (
                   id INTEGER PRIMARY KEY,
                   account_name TEXT,
                   industry TEXT,
                   created_at TIMESTAMP)''')
    c.execute("INSERT INTO histories (account_name, industry, created_at) VALUES (?, ?, ?)", 
              (analysis_data['account_name'], analysis_data['industry'], datetime.now()))
    conn.commit()
    conn.close()

def auto_correct(text):
    for kw, rep in RISK_REPLACEMENTS.items():
        text = text.replace(kw, rep)
    return text

def generate_platform_spec(topics, platform):
    return [f"{topic} [{PLATFORM_RULES[platform]['标题规则']}]" for topic in topics]

def streamlit_app():
    st.title("📢 DeepSeek 账号人设规划系统")
    st.markdown("## 账号基础信息")
    account_name = st.text_input("📌 账号名称")
    industry = st.selectbox("🏢 所在行业", VALID_INDUSTRIES)

    st.markdown("## 核心优势")
    core_advantages = st.text_area("💡 核心优势 (换行分隔)").split("\n")

    st.markdown("## 目标人群画像")
    target_audience = st.text_area("👥 年龄/地区/兴趣")

    st.markdown("## 竞品账号分析")
    competitor_accounts = st.text_area("竞品账号 (换行分隔)").split("\n")
    competitor_platform = st.selectbox("📲 平台", ["抖音", "小红书", "视频号"])

    st.markdown("## 运营目标")
    operation_goal = st.selectbox("🎯 目标", ["粉丝增长", "品牌曝光", "产品销售", "20个爆款选题"])

    if st.button("🔍 生成账号分析报告"):
        with st.spinner("正在分析账号人设，请稍后..."):
            input_data = {
                "account_name": account_name,
                "industry": industry,
                "core_advantages": core_advantages,
                "target_audience": target_audience,
                "competitor_accounts": competitor_accounts,
                "operation_goal": operation_goal
            }

            analysis_response = call_deepseek_api(json.dumps(input_data, ensure_ascii=False), "账号人设分析", industry)
            raw_result = analysis_response.get("choices", [{}])[0].get("message", {}).get("content", {})
            parsed_result = parse_analysis_result(raw_result)

            st.success("✅ 分析完成")
            save_analysis_history(input_data)

            st.subheader("📑 账号人设分析结果")
            st.markdown(f"**人设定位建议**: {parsed_result['人设定位']}")
            st.markdown("**差异化分析**:")
            for diff in parsed_result['差异点分析']:
                st.markdown(f"- {diff}")
            st.markdown("**⚠️ 风险提示**:")
            st.markdown(auto_correct(parsed_result['风险提示']))

            if operation_goal == "20个爆款选题":
                hot_topics_result = call_deepseek_api(parsed_result["人设定位"], "生成20个爆款选题", industry)
                raw_text = hot_topics_result.get("choices", [{}])[0].get("message", {}).get("content", "未生成选题")
                topics = parse_topics(raw_text)
                st.subheader("🔥 生成的爆款选题")
                for topic in topics:
                    st.markdown(f"- {topic}")

                calendar_df = generate_calendar(topics)
                st.dataframe(calendar_df)

                st.download_button("📅 下载 CSV 格式", calendar_df.to_csv(index=False), "content_calendar.csv")
                st.download_button("📑 下载 Excel 格式", calendar_df.to_excel(index=False), "content_calendar.xlsx")
                st.download_button("📝 下载 JSON 格式", calendar_df.to_json(orient='records', force_ascii=False), "content_calendar.json")

            competitor_df = asyncio.run(compare_competitors_async(competitor_accounts, competitor_platform))
            st.subheader("竞品账号对比分析")
            st.dataframe(competitor_df)

            chart = alt.Chart(competitor_df).mark_bar().encode(
                x='账号名称',
                y='粉丝量级',
                color='平台'
            )
            st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.markdown("📢 全平台 @旺仔AIGC")
    st.markdown("关注我，和我一起 拆解流量密码，探索 AI创作新玩法，让你的账号精准定位，内容不再迷路！🚀")

if __name__ == "__main__":
    streamlit_app()
