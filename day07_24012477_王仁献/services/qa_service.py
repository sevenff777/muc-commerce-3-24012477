from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")

    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = "".join(question.lower().split())

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"

    if any(word in normalized for word in ["流失率", "流失"]):
        return f"总体流失率为{float(metrics['流失率']):.1%}。"

    if any(word in normalized for word in ["偏好品类", "品类", "最受欢迎", "喜欢"]):
        top_idx = category_df["用户数"].idxmax()
        top_category = category_df.loc[top_idx, "PreferedOrderCat"]
        top_users = int(category_df.loc[top_idx, "用户数"])
        return f"用户中最主要的偏好品类是{top_category}，该品类用户数为{top_users:,}人。"

    if any(word in normalized for word in ["生命周期", "风险", "阶段", "流失最高"]):
        highest_risk_row = segment_df.loc[segment_df["流失率"].idxmax()]
        return (
            f"流失率最高的生命周期阶段是{highest_risk_row['TenureGroup']}，"
            f"流失率为{highest_risk_row['流失率']:.1%}。"
        )

    if any(word in normalized for word in ["订单", "平均订单"]):
        return f"平均订单数为{float(metrics['平均订单数']):.2f}单。"

    return (
        "暂时无法回答这个问题。当前系统支持查询用户数、流失率、偏好品类、"
        "生命周期风险和平均订单数。你可以换一个更具体的提问。"
    )
