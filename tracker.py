#!/usr/bin/env python3
"""
3个月盈利提升跟踪系统
自动记录和跟踪投放效果
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

TRACKING_FILE = "/home/michael/projects/erictsang-weather/progress_tracker.json"
GOAL_FILE = "/home/michael/projects/erictsang-weather/3个月盈利提升计划.md"

# 初始基线数据
BASELINE = {
    "start_date": "2026-02-16",
    "target_date": "2026-05-16",
    "baseline": {
        "total_sales": 22514750,
        "total_cost": 3327720,
        "avg_roi": 6.77,
        "daily_sales": 750492
    },
    "target": {
        "roi": 12.0,
        "improvement": "77%"
    }
}

def init_tracker():
    """初始化跟踪器"""
    if not os.path.exists(TRACKING_FILE):
        data = {
            "baseline": BASELINE,
            "weekly_progress": [],
            "optimizations": [],
            "milestones": []
        }
        save_tracker(data)
        return data
    return load_tracker()

def load_tracker():
    """加载跟踪数据"""
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tracker(data):
    """保存跟踪数据"""
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_weekly_progress(week_num, strategy, actual_roi, actual_sales, notes=""):
    """记录每周进度"""
    data = load_tracker()
    
    progress = {
        "week": week_num,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "strategy": strategy,
        "actual_roi": actual_roi,
        "actual_sales": actual_sales,
        "roi_improvement": round((actual_roi - BASELINE['baseline']['avg_roi']) / BASELINE['baseline']['avg_roi'] * 100, 1),
        "notes": notes
    }
    
    data['weekly_progress'].append(progress)
    save_tracker(data)
    
    # 检查里程碑
    check_milestones(actual_roi)
    
    return progress

def add_optimization(problem, solution, effect):
    """记录优化措施"""
    data = load_tracker()
    
    opt = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "problem": problem,
        "solution": solution,
        "effect": effect
    }
    
    data['optimizations'].append(opt)
    save_tracker(data)
    return opt

def check_milestones(current_roi):
    """检查里程碑达成"""
    data = load_tracker()
    milestones = [
        (2, 8.0, "第2周：ROI提升至8.0"),
        (4, 10.0, "第4周：ROI提升至10.0"),
        (8, 12.0, "第8周：ROI提升至12.0"),
        (12, 12.0, "第12周：ROI稳定12.0+")
    ]
    
    week = len(data['weekly_progress'])
    
    for target_week, target_roi, message in milestones:
        if week == target_week and current_roi >= target_roi:
            data['milestones'].append({
                "week": target_week,
                "achieved": True,
                "roi": current_roi,
                "message": message,
                "date": datetime.now().strftime("%Y-%m-%d")
            })
            save_tracker(data)
            print(f"🎉 达成里程碑：{message}")

def get_progress_report():
    """生成进度报告"""
    data = load_tracker()
    
    if not data['weekly_progress']:
        return "暂无进度数据"
    
    latest = data['weekly_progress'][-1]
    baseline = BASELINE['baseline']['avg_roi']
    
    report = f"""
📊 3个月盈利提升进度报告
========================

🎯 目标：3个月内ROI从 {baseline} 提升至 12.0

📈 当前进度（第{latest['week']}周）
   - 当前ROI：{latest['actual_roi']}
   - 提升幅度：+{latest['roi_improvement']}%
   - 策略：{latest['strategy']}

📅 周度数据：
"""
    for p in data['weekly_progress']:
        report += f"   第{p['week']}周: ROI={p['actual_roi']}, 销售额=¥{p['actual_sales']:,.0f}\n"
    
    if data['optimizations']:
        report += "\n🔧 优化记录：\n"
        for opt in data['optimizations']:
            report += f"   - {opt['date']}: {opt['problem']} → {opt['solution']} (效果: {opt['effect']})\n"
    
    return report

def select_strategy(strategy_name, cities, budget):
    """确认策略选择"""
    data = load_tracker()
    data['selected_strategy'] = {
        "name": strategy_name,
        "cities": cities,
        "budget": budget,
        "selected_date": datetime.now().strftime("%Y-%m-%d")
    }
    save_tracker(data)
    
    print(f"✅ 已选择策略: {strategy_name}")
    print(f"   重点城市: {', '.join(cities[:5])}...")
    print(f"   预算: ¥{budget:,}/天")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            init_tracker()
            print("✅ 跟踪器已初始化")
        elif sys.argv[1] == "report":
            print(get_progress_report())
        elif sys.argv[1] == "select" and len(sys.argv) > 3:
            strategy = sys.argv[2]
            budget = int(sys.argv[3])
            # 简化处理
            select_strategy(strategy, [], budget)
        else:
            print("用法: python tracker.py [init|report|select]")
    else:
        init_tracker()
        print(get_progress_report())
