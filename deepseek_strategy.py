#!/usr/bin/env python3
"""
DeepSeek 淘宝投流策略分析系统
用于生成AI驱动的投放策略，支持反馈优化
"""

import os
import json
import pandas as pd
import requests
from datetime import datetime

# 配置
DEEPSEEK_API_KEY = "sk-96c514b15b454651b7d6ededda68fd6f"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DATA_PATH = "/home/michael/projects/erictsang-weather"
OUTPUT_PATH = "/home/michael/projects/erictsang-weather/deepseek_analysis"
ECOM_DATA_PATH = "/home/michael/.openclaw/media/inbound/fef2e726-9724-4944-a156-19135c0d99cd.csv"

# 确保输出目录存在
os.makedirs(OUTPUT_PATH, exist_ok=True)

def load_data():
    """加载数据"""
    # 电商数据
    ecom_df = pd.read_csv(ECOM_DATA_PATH, encoding='gbk')
    # 天气数据
    weather_df = pd.read_csv(f'{DATA_PATH}/weather_data.csv')
    # 调整ROI数据
    roi_df = pd.read_excel(f'{DATA_PATH}/调整ROI分析表.xlsx')
    return ecom_df, weather_df, roi_df

def prepare_prompt(ecom_df, weather_df, roi_df, user_requirements=None):
    """准备分析Prompt"""
    
    # 基础数据统计
    summary = {
        "总城市数": len(ecom_df),
        "总展现量": ecom_df['展现量'].sum(),
        "总花费": ecom_df['花费'].sum(),
        "总成交金额": ecom_df['总成交金额'].sum(),
        "平均ROI": ecom_df['投入产出比'].mean(),
        "高ROI城市TOP10": ecom_df.nlargest(10, '投入产出比')[['省', '市', '投入产出比', '总成交金额']].to_dict('records'),
    }
    
    # 气温数据
    temp_summary = weather_df.groupby('时间段').agg({
        '平均温度均值': ['mean', 'min', 'max']
    }).round(1).to_dict()
    
    prompt = f"""
你是淘宝投放策略专家。请根据以下数据进行分析并给出投放策略建议。

## 店铺信息
- 店铺名：爱上靓妞女童装
- 产品：ASLN女童春装（公主裙、打底衫）
- 客单价：¥180
- 预算：每日¥5000-10000
- 目标：ROI最大化 + 销售额最大化

## 数据概览
- 覆盖城市：{summary['总城市数']}个
- 总展现量：{summary['总展现量']:,.0f}
- 总花费：¥{summary['总花费']:,.0f}
- 总成交金额：¥{summary['总成交金额']:,.0f}
- 平均ROI：{summary['平均ROI']:.2f}

## 高ROI城市TOP10
{json.dumps(summary['高ROI城市TOP10'], ensure_ascii=False, indent=2)}

## 气温与转化率关系
| 气温区间 | ROI倍数 |
|----------|---------|
| ≤0°C | ×0.5 |
| 0-5°C | ×0.65 |
| 5-10°C | ×0.8 |
| 10-13°C | ×1.0 |
| 13-16°C | ×1.2 |
| 16-18°C | ×1.3 |
| 18-23°C | ×1.2 |
| >23°C | ×1.0 |

## 用户需求
{user_requirements or "无特殊需求，请给出综合最优策略"}

请给出：
1. 详细的投放策略建议
2. 重点投放城市及预算分配
3. 投放时间节奏
4. 风险提示和优化建议

请以JSON格式输出，包含以下字段：
{{
    "strategy_name": "策略名称",
    "target_cities": ["城市1", "城市2", ...],
    "budget_allocation": {{"城市": 预算}},
    "time_schedule": {{"阶段": "策略"}},
    "expected_roi": 预期ROI,
    "expected_sales": 预期销售额,
    "risks": ["风险1", "风险2"],
    "optimization_tips": ["优化建议1", "优化建议2"]
}}
"""
    return prompt

def call_deepseek(prompt):
    """调用DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的淘宝投放策略专家，擅长数据分析和ROI优化。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"API调用失败: {str(e)}"

def save_analysis(analysis_result, strategy_name, feedback=None):
    """保存分析结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存JSON
    result_data = {
        "timestamp": timestamp,
        "strategy_name": strategy_name,
        "analysis": analysis_result,
        "feedback": feedback
    }
    
    json_path = f"{OUTPUT_PATH}/strategy_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    # 保存为Markdown报告
    md_path = f"{OUTPUT_PATH}/strategy_{timestamp}.md"
    md_content = f"""# 淘宝女童装春装投放策略报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 策略名称
{strategy_name}

## 分析结果
{analysis_result}

## 用户反馈
{feedback or "无"}

---
*由DeepSeek AI生成*
"""
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return json_path, md_path

def analyze(user_requirements=None, strategy_name="DeepSeek智能策略"):
    """主分析函数"""
    print("📊 正在加载数据...")
    ecom_df, weather_df, roi_df = load_data()
    
    print("🤖 正在调用DeepSeek API...")
    prompt = prepare_prompt(ecom_df, weather_df, roi_df, user_requirements)
    result = call_deepseek(prompt)
    
    print("💾 正在保存结果...")
    json_path, md_path = save_analysis(result, strategy_name)
    
    print(f"✅ 分析完成！")
    print(f"   JSON: {json_path}")
    print(f"   MD: {md_path}")
    
    return result, json_path, md_path

def optimize_with_feedback(original_strategy, feedback):
    """基于反馈优化策略"""
    print("🔄 正在根据反馈优化策略...")
    
    prompt = f"""
你是一个专业的淘宝投放策略专家。用户对之前的策略给出了反馈，请根据反馈优化策略。

## 原始策略
{original_strategy}

## 用户反馈
{feedback}

请给出优化后的策略，仍然以JSON格式输出：
{{
    "strategy_name": "优化后的策略名称",
    "target_cities": ["城市1", "城市2", ...],
    "budget_allocation": {{"城市": 预算}},
    "time_schedule": {{"阶段": "策略"}},
    "expected_roi": 预期ROI,
    "expected_sales": 预期销售额,
    "risks": ["风险1", "风险2"],
    "optimization_tips": ["优化建议1", "优化建议2"]
}}
"""
    result = call_deepseek(prompt)
    return result

def list_strategies():
    """列出所有保存的策略"""
    files = os.listdir(OUTPUT_PATH)
    strategies = [f for f in files if f.startswith('strategy_') and f.endswith('.json')]
    return sorted(strategies, reverse=True)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "analyze":
            requirements = sys.argv[2] if len(sys.argv) > 2 else None
            analyze(requirements)
        elif sys.argv[1] == "list":
            print("📁 已保存的策略:")
            for s in list_strategies():
                print(f"  - {s}")
        elif sys.argv[1] == "optimize":
            # 需要提供原始策略和反馈
            print("请使用 Python API 调用 optimize_with_feedback()")
        else:
            print("用法: python deepseek_strategy.py [analyze|list|optimize]")
    else:
        # 默认分析
        analyze()
