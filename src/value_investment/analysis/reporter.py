"""Reporter module - generate Markdown reports from analysis results"""
from typing import Any

import pandas as pd


def generate_report(indicators: dict[str, Any], stock_code: str) -> str:
    """Generate Markdown format report from analysis results.
    
    Args:
        indicators: Dictionary containing analysis results with keys:
            - name: Stock name with code
            - year_range: Year range string (e.g., "2020-2024")
            - summary: List of summary metrics with label and value
            - table: DataFrame with yearly indicators (optional)
            - warnings: List of warning messages (optional)
            - notes: List of note messages (optional)
        stock_code: Stock code
    
    Returns:
        Markdown formatted report string
    """
    # Extract data from indicators dict
    name = indicators.get("name", stock_code)
    year_range = indicators.get("year_range", "")
    summary = indicators.get("summary", [])
    table = indicators.get("table")
    warnings = indicators.get("warnings", [])
    notes = indicators.get("notes", [])

    # Build Markdown report
    lines = []

    # Header
    lines.append(f"# {name}")
    lines.append("")
    lines.append(f"**股票代码:** {stock_code}")
    if year_range:
        lines.append(f"**分析期间:** {year_range}")
    lines.append("")

    # Summary section
    if summary:
        lines.append("## 关键指标摘要")
        lines.append("")
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        for item in summary:
            label = item.get("label", "")
            value = item.get("value", "")
            lines.append(f"| {label} | {value} |")
        lines.append("")

    # Table section
    if table is not None and isinstance(table, pd.DataFrame) and not table.empty:
        lines.append("## 年度数据")
        lines.append("")

        # Get column names
        columns = table.columns.tolist()

        # Build table header
        header = "| " + " | ".join(columns) + " |"
        separator = "|" + "|".join(["---" for _ in columns]) + "|"

        lines.append(header)
        lines.append(separator)

        # Add data rows
        for _, row in table.iterrows():
            row_values = [str(row.get(col, "")) for col in columns]
            lines.append("| " + " | ".join(row_values) + " |")

        lines.append("")

    # Warnings section
    if warnings:
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Notes section
    if notes:
        lines.append("## 📝 备注")
        lines.append("")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")

    return "\n".join(lines)
