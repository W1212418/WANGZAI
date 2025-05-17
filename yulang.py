import streamlit as st
import requests
import json
import os

# DeepSeek API配置
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-38a62f45bd574dafb3d96237b0c8d71a")
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

# 通用请求DeepSeek API函数（增加错误处理）
def call_deepseek(prompt, persona):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": persona},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    result = response.json()

    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"]
    else:
        error_message = result.get('error', {}).get('message', '未知错误，请检查API或参数。')
        st.error(f"DeepSeek API 调用失败: {error_message}")
        return f"调用失败: {error_message}"

# 各个DeepSeek角色完整提示词（专业严谨）
personas = {
    "品牌分析师": "商业生态解码器与品牌基因工程师，提供战略诊断、营销预判、品牌诊断、营销规划、竞争策略等严谨且精准的品牌增长建议。",
    "产品分析师": "商业价值分析师与市场需求解读专家，提供产品定位、市场适配度、竞争优势、用户需求等详细精准的产品战略分析。",
    "品牌营销专家": "战略品牌增长顾问与传播策划师，提供品牌定位、用户心智分析、品牌战略规划及高效传播策略。",
    "渠道营销师": "渠道网络构建师与营销效率优化师，提供渠道策略、市场覆盖规划、伙伴生态建设及渠道运营优化策略。",
    "品牌营销操盘手": "整体品牌营销操盘手，统筹战略规划、营销执行、资源整合及阶段性目标达成，提供切实可行、严谨且专业的商业落地方案。"
}

# Streamlit界面
st.title("屿浪品牌管理超级智能体")

# 用户输入模块
st.header("输入品牌与产品信息")
brand_info = st.text_area("品牌信息")
product_info = st.text_area("产品信息")
brand_needs = st.text_area("品牌需求")
promotion_channels = st.text_area("推广渠道")

if st.button("生成营销方案"):
    with st.spinner("品牌分析中..."):
        brand_analysis = call_deepseek(brand_info, personas["品牌分析师"])

    with st.spinner("产品分析中..."):
        product_analysis = call_deepseek(product_info, personas["产品分析师"])

    with st.spinner("品牌需求分析中..."):
        brand_needs_analysis = call_deepseek(brand_needs, personas["品牌营销专家"])

    with st.spinner("推广渠道分析中..."):
        promotion_channels_analysis = call_deepseek(promotion_channels, personas["渠道营销师"])

    # 严谨且专业的综合方案
    comprehensive_prompt = (
        f"品牌分析:\n{brand_analysis}\n\n"
        f"产品分析:\n{product_analysis}\n\n"
        f"品牌需求分析:\n{brand_needs_analysis}\n\n"
        f"推广渠道分析:\n{promotion_channels_analysis}\n\n"
        "基于以上信息，请提供一个严谨且专业的营销方案，明确各个阶段的具体目标与实施措施，确保方案切实可行，能够实际落地执行，避免使用夸张修饰词语。"
    )

    with st.spinner("生成严谨专业的营销方案..."):
        final_strategy = call_deepseek(comprehensive_prompt, personas["品牌营销操盘手"])

    # 展示严谨且专业的最终营销方案
    st.success("营销方案已生成")
    st.markdown("### 品牌营销操盘手完整方案")
    st.write(final_strategy)

# 页脚信息
st.markdown("---")
st.markdown("屿浪品牌管理超级智能体，帮助品牌精准洞察，制定可执行的专业营销方案。");
