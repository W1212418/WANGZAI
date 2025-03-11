import re
import requests
import json
import pandas as pd
import streamlit as st
import numpy as np
import time
import os
import sqlite3
from datetime import datetime
from json import JSONDecodeError

# 暂时保留硬编码API KEY（安全升级后改为 st.secrets）
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-e4eaafa61ff349cbb93e554b64c22dcb")

# 更新 API 端点
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

# 抖音账号信息采集（示例代码，需调整为真实API或爬虫）
def fetch_douyin_account_info(user_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/605.1.15",
        "Cookie": "tt_webid=你的tt_webid",
    }
    api_url = f"https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={user_id}"
    try:
        response = requests.get(api_url, headers=headers)
        result = response.json()
        if result.get("user_info"):
            user_data = result["user_info"]
            return {
                "昵称": user_data.get("nickname"),
                "粉丝数": user_data.get("follower_count"),
                "作品数": user_data.get("aweme_count")
            }
        else:
            return {"error": "用户信息未获取"}
    except Exception as e:
        return {"error": str(e)}

# 小红书账号信息采集（示例代码）
def fetch_xiaohongshu_account_info(user_id):
    headers = {
        "User-Agent": "XHS/7.36.0 (iPhone; iOS 14.6; Scale/3.00)",
        "Cookie": "abtest_env=product;",
    }
    api_url = f"https://www.xiaohongshu.com/api/sns/v1/user/{user_id}"
    try:
        response = requests.get(api_url, headers=headers)
        result = response.json()
        if result.get("data"):
            user_data = result["data"]
            return {
                "昵称": user_data.get("nickname"),
                "粉丝数": user_data.get("follower_count"),
                "笔记数": user_data.get("note_count")
            }
        else:
            return {"error": "用户信息未获取"}
    except Exception as e:
        return {"error": str(e)}

# 视频号模拟数据（暂未实现真实接口）
def fetch_wechat_channels_account_info(account_name):
    return {
        "昵称": account_name,
        "粉丝数": np.random.randint(1000, 500000),
        "视频数": np.random.randint(10, 300)
    }

# 统一调用

def get_account_data(platform, account_id_or_name):
    if platform == "抖音":
        return fetch_douyin_account_info(account_id_or_name)
    elif platform == "小红书":
        return fetch_xiaohongshu_account_info(account_id_or_name)
    elif platform == "视频号":
        return fetch_wechat_channels_account_info(account_id_or_name)
    else:
        return {"error": "暂不支持的平台"}

def validate_industry(input_industry):
    if input_industry not in VALID_INDUSTRIES:
        raise ValueError(f"暂不支持该行业分类，请选择：{', '.join(VALID_INDUSTRIES)}")

def call_deepseek_api(text, task, industry=""):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = json.dumps({
        "model": "deepseek-reasoner",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": f"你是一名{industry}领域账号规划师，需特别关注{INDUSTRY_PROMPTS.get(industry, '通用策略')}。"},
            {"role": "user", "content": f"{task}: {text}"}
        ],
        "stream": False
    })
    response = requests.post(BASE_URL, headers=headers, data=payload)
    try:
        return response.json()
    except JSONDecodeError:
        st.error("API返回格式异常，请检查提示词配置")
        return {}

def parse_analysis_result(raw_result):
    return {
        "人设定位": raw_result.get("persona", "未找到"),
        "差异点分析": raw_result.get("differentiation", []),
        "风险提示": raw_result.get("risk", "无")
    }

def parse_topics(hot_topics_raw_text):
    return re.findall(r'\d+\.\s+(.*)', hot_topics_raw_text)

def compare_competitors(competitor_list, platform):
    data = []
    for comp in competitor_list:
        info = get_account_data(platform, comp)
        data.append({
            "账号名称": info.get("昵称", comp),
            "平台": platform,
            "粉丝量级": info.get("粉丝数", 0),
            "内容数量": info.get("作品数", info.get("笔记数", info.get("视频数", 0)))
        })
    df = pd.DataFrame(data)
    st.dataframe(df)
    st.bar_chart(df.set_index("账号名称")["粉丝量级"])

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

def main():
    st.title("📢 DeepSeek 账号人设规划系统")
    
    if "hot_topics" not in st.session_state:
        st.session_state["hot_topics"] = None
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None
    
    with st.form("user_input_form"):
        account_name = st.text_input("📌 账号名称")
        industry = st.selectbox("🏢 所在行业", VALID_INDUSTRIES)
        core_advantages = st.text_area("💡 核心优势 (换行分隔)").split("\n")
        target_audience = st.text_area("🎯 目标人群 (请描述年龄、地区、兴趣点)")
        competitor_accounts = st.text_area("📊 竞品账号 (换行分隔)").split("\n")
        competitor_platform = st.selectbox("📲 竞品平台", ["抖音", "小红书", "视频号"])
        operation_goal = st.selectbox("🚀 运营目标", ["粉丝增长", "品牌曝光", "产品销售", "20个爆款选题"])
        submit_button = st.form_submit_button("🔍 生成人设分析报告")

    if submit_button:
        try:
            validate_industry(industry)
        except ValueError as ve:
            st.error(str(ve))
            return
        
        if len(core_advantages) > 5:
            st.warning("核心优势建议不超过5个关键点")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(1, 101, 5):
            status_text.write(f"⏳ 正在分析账号人设，请稍后 {i}%")
            progress_bar.progress(i / 100)
            time.sleep(0.1)
        
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
        st.session_state["analysis_result"] = parse_analysis_result(raw_result)
        
        status_text.write("✅ 账号人设分析完成")
        progress_bar.progress(1.0)
        
        save_analysis_history(input_data)

    if st.session_state["analysis_result"]:
        parsed_result = st.session_state["analysis_result"]
        
        st.markdown("---")
        st.subheader("📊 账号人设分析报告")
        
        with st.expander("🧠 人设定位建议"):
            st.write(parsed_result["人设定位"])
        
        with st.expander("📌 差异化分析"):
            for diff in parsed_result["差异点分析"]:
                st.write(f"- {diff}")
        
        with st.expander("⚠️ 风险提示"):
            st.warning(auto_correct(parsed_result["风险提示"]))
        
        if st.button("🔥 生成行业爆款选题"):
            with st.spinner("正在生成爆款选题，请稍候..."):
                hot_topics_result = call_deepseek_api(parsed_result["人设定位"], "生成20个爆款选题", industry)
                raw_text = hot_topics_result.get("choices", [{}])[0].get("message", {}).get("content", "未生成选题")
                st.session_state["hot_topics"] = raw_text
                st.success("✅ 爆款选题生成完成")
                st.write(st.session_state["hot_topics"])
        
        if st.session_state["hot_topics"]:
            if st.button("🔄 换一批选题"):
                with st.spinner("正在重新生成新的爆款选题，请稍候..."):
                    hot_topics_result = call_deepseek_api(parsed_result["人设定位"], "生成20个爆款选题", industry)
                    raw_text = hot_topics_result.get("choices", [{}])[0].get("message", {}).get("content", "未生成选题")
                    st.session_state["hot_topics"] = raw_text
                    st.success("✅ 新的爆款选题生成完成")
                    st.write(st.session_state["hot_topics"])
            
            topics = parse_topics(st.session_state["hot_topics"])
            platform_topics = generate_platform_spec(topics, "抖音")
            calendar_df = generate_calendar(platform_topics)
            st.dataframe(calendar_df)
            st.download_button("📅 下载内容排期表", calendar_df.to_csv(index=False), "content_calendar.csv")
        
        compare_competitors(competitor_accounts, competitor_platform)
        
        st.markdown("---")
        st.markdown("📢 全平台 @旺仔AIGC 📢")
        st.markdown("关注我，和我一起 拆解流量密码，探索 AI创作新玩法，让你的 账号精准定位，内容不再迷路！🚀")

if __name__ == "__main__":
    main()
