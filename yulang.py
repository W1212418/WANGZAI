import streamlit as st
import requests
import json
import os

# DeepSeek API配置
API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
BASE_URL = "https://api.deepseek.com/v1/chat/completions"

# 通用请求DeepSeek API函数
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
    return response.json()["choices"][0]["message"]["content"]

# 各个DeepSeek角色完整提示词
personas = {
    "品牌分析师": """商业生态解码器与品牌基因工程师，构建「战略诊断×营销预判」决策支持系统，提供品牌诊断系统、营销规划矩阵、竞争策略库、数字化工具、资产管理系统等全面服务，使用品牌体检仪、决策罗盘、声量雷达、心智图谱等专业工具，确保诊断准确率≥90%、方案通过率≥75%、ROI提升≥30%、风险预警≥95%、迭代周期≤72h。""",
    "产品分析师": """商业价值炼金师与用户需求解码器，构建「产品基因×市场势能」双螺旋模型，提供产品解构系统、卖点锻造引擎、人群画像矩阵、传播策略库等核心能力，运用用户痛点雷达、价值地图、场景模拟器、竞品拆解台等工具，确保分析准确率≥92%、卖点有效性≥85%、人群画像重合度≥80%、传播CTR提升≥40%、策略迭代周期≤48h。""",
    "品牌营销专家": """品牌价值加速器与心智占领战略家，构建「战略势能×传播裂变」双引擎系统，提供品牌战略规划、传播策略库、创意生成系统、数字作战工具、效果优化系统等服务，使用心智扫描仪、战役沙盘、创意基因库、流量引力场等工具，确保品牌认知度提升≥35%、传播ROI提升≥50%、用户口碑NPS≥60、创意产出效率≥30条/日、危机响应速度≤2小时。""",
    "渠道营销师": """渠道网络架构师与效能增长工程师，构建「渠道势能×转化效率」双轮驱动模型，提供渠道战略规划、伙伴生态系统、运营优化引擎、数据决策系统等核心能力，使用渠道沙盘、伙伴价值计算器、智能合约生成器、战情指挥台等工具，确保渠道覆盖率≥90%、渠道激活率≥75%、ROI提升≥40%、库存周转率提升≥30%、异常响应速度≤4小时。""",
    "品牌营销操盘手": """品牌增长总控官与资源整合指挥官，构建「战略穿透力×执行爆破力」双螺旋体系，实现战略解码系统、战役指挥中枢、资源熔合引擎、敏捷优化系统的综合运作，使用战略罗盘、价值飞轮、资源引力场、决策矩阵等专业工具，确保品牌资产增长率≥45%、营销战役成功率≥80%、资源利用率≥90%、策略迭代速度≤48小时、跨部门协同效率提升≥60%。"""
}

# Streamlit界面
st.title("🌟 屿浪品牌管理超级智能体 🌟")

# 用户输入模块
st.header("输入品牌与产品信息")
brand_info = st.text_area("🏢 品牌信息")
product_info = st.text_area("📦 产品信息")
brand_needs = st.text_area("📈 品牌需求")
promotion_channels = st.text_area("📡 推广渠道")

if st.button("🚀 生成完整营销方案"):
    with st.spinner("品牌分析中..."):
        brand_analysis = call_deepseek(brand_info, personas["品牌分析师"])

    with st.spinner("产品分析中..."):
        product_analysis = call_deepseek(product_info, personas["产品分析师"])

    with st.spinner("品牌需求分析中..."):
        brand_needs_analysis = call_deepseek(brand_needs, personas["品牌营销专家"])

    with st.spinner("推广渠道分析中..."):
        promotion_channels_analysis = call_deepseek(promotion_channels, personas["渠道营销师"])

    # 综合所有分析，由操盘手输出最终方案
    comprehensive_prompt = (
        f"品牌分析结果:\n{brand_analysis}\n\n"
        f"产品分析结果:\n{product_analysis}\n\n"
        f"品牌需求分析结果:\n{brand_needs_analysis}\n\n"
        f"推广渠道分析结果:\n{promotion_channels_analysis}\n\n"
        f"请根据以上所有分析，制定详细的、操盘手级别的完整营销运营方案。"
    )

    with st.spinner("综合分析生成最终营销方案..."):
        final_strategy = call_deepseek(comprehensive_prompt, personas["品牌营销操盘手"])

    # 展示最终营销方案
    st.success("🎯 完整营销方案已生成")
    st.markdown("## 📑 品牌营销操盘手最终方案")
    st.write(final_strategy)

# 页脚信息
st.markdown("---")
st.markdown("📢 屿浪品牌管理超级智能体，帮助品牌精准洞察，快速增长，实现营销闭环！🚀")
