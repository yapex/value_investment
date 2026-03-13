"""Scanner 文本解析器

将自然语言格式的过滤条件解析为 FilterBuilder。

支持的格式：
- 单条件：{字段} {条件类型}{数值}%
- 多条件：用"且"或"和"连接

条件类型：
- 连续N年：ROE 连续5年 ≥15%
- 最近N年：ROE 最近1年 ≥20%
- N年至少M年：ROE 5年至少4年 ≥15%
- 带平均值：ROE 5年至少4年 ≥15%, 平均≥15%
"""
import re

from value_investment.scanner.pipeline import FilterBuilder


class ParseError(Exception):
    """解析错误"""
    pass


# 中文字段名到标准字段名的映射
FIELD_ALIASES = {
    # 中文 -> 标准字段名
    'roe': 'roe',
    '净资产收益率': 'roe',
    '毛利率': 'gross_profit_margin',
    'gross_profit_margin': 'gross_profit_margin',
    '净利率': 'net_profit_margin',
    'net_profit_margin': 'net_profit_margin',
    '净利润率': 'net_profit_margin',
    '负债率': 'debt_to_asset',
    'debt_to_asset': 'debt_to_asset',
    '资产负债率': 'debt_to_asset',
    '营业收入增长率': 'revenue_growth',
    'revenue_growth': 'revenue_growth',
    '营收增长率': 'revenue_growth',
    '总资产周转率': 'asset_turnover',
    'asset_turnover': 'asset_turnover',
    '存货周转率': 'inventory_turnover',
    'inventory_turnover': 'inventory_turnover',
}


def parse_filter(text: str) -> FilterBuilder:
    """解析文本为 FilterBuilder

    Args:
        text: 过滤条件文本

    Returns:
        FilterBuilder 实例

    Raises:
        ParseError: 解析失败

    Examples:
        >>> fb = parse_filter("ROE 连续5年 ≥15%")
        >>> fb = parse_filter("ROE 连续5年 ≥15% 且 毛利率 连续5年 ≥30%")
    """
    text = text.strip()

    if not text:
        raise ParseError("输入不能为空")

    # 按"且"或"和"分割多个条件
    # 先处理"且"
    if '且' in text:
        parts = text.split('且')
    elif '和' in text:
        parts = text.split('和')
    else:
        parts = [text]

    fb = FilterBuilder()

    for part in parts:
        part = part.strip()
        if not part:
            continue

        condition = _parse_condition(part)
        fb.add_filter(**condition)

    return fb


def _parse_condition(text: str) -> dict:
    """解析单个条件

    Args:
        text: 单个条件文本，如 "ROE 连续5年 ≥15%"

    Returns:
        filter 参数字典
    """
    text = text.strip()

    # 去除末尾的 %
    text = text.rstrip('%')

    # 1. 提取字段名（中文或英文）
    field_match = re.match(r'^([a-zA-Z_\u4e00-\u9fff]+)', text)
    if not field_match:
        raise ParseError(f"无法识别字段名：{text}")

    field_raw = field_match.group(1)
    field = FIELD_ALIASES.get(field_raw.lower(), field_raw.lower())

    # 剩余部分
    rest = text[field_match.end():].strip()

    # 2. 提取条件类型和年份
    # 连续N年
    consecutive_match = re.match(r'^连续(\d+)年\s*', rest)
    # 最近N年
    latest_match = re.match(r'^最近(\d+)年\s*', rest)
    # N年至少M年
    majority_match = re.match(r'^(\d+)年至少(\d+)年\s*', rest)

    if consecutive_match:
        years = int(consecutive_match.group(1))
        condition_type = 'consecutive_years'
        rest = rest[consecutive_match.end():]
    elif latest_match:
        years = int(latest_match.group(1))
        condition_type = 'latest_year'
        rest = rest[latest_match.end():]
    elif majority_match:
        years = int(majority_match.group(1))
        required_years = int(majority_match.group(2))
        condition_type = 'majority_years'
        rest = rest[majority_match.end():]
    else:
        # 默认最近1年
        years = 1
        condition_type = 'latest_year'

    # 3. 提取运算符和数值
    # ≥
    gte_match = re.match(r'^≥(\d+(?:\.\d+)?)', rest)
    # ≤
    lte_match = re.match(r'^≤(\d+(?:\.\d+)?)', rest)
    # >
    gt_match = re.match(r'^>(\d+(?:\.\d+)?)', rest)
    # <
    lt_match = re.match(r'^<(\d+(?:\.\d+)?)', rest)

    if gte_match:
        min_value = float(gte_match.group(1))
        max_value = None
        rest = rest[gte_match.end():]
    elif lte_match:
        min_value = None
        max_value = float(lte_match.group(1))
        rest = rest[lte_match.end():]
    elif gt_match:
        # > 转换为 ≥ (value + 0.001)
        min_value = float(gt_match.group(1)) + 0.001
        max_value = None
        rest = rest[gt_match.end():]
    elif lt_match:
        # < 转换为 ≤ (value - 0.001)
        min_value = None
        max_value = float(lt_match.group(1)) - 0.001
        rest = rest[lt_match.end():]
    else:
        raise ParseError(f"无法识别运算符：{text}")

    # 4. 检查是否有平均值要求
    min_avg = None
    avg_match = re.search(r',?\s*平均[≥>]=?(\d+(?:\.\d+)?)', rest)
    if avg_match:
        min_avg = float(avg_match.group(1))

    # 5. 构建结果
    result = {
        'filter_type': condition_type,
        'field': field,
        'years': years,
    }

    if min_value is not None:
        result['min_value'] = min_value
    if max_value is not None:
        result['max_value'] = max_value
    if min_avg is not None:
        result['min_avg'] = min_avg
    if condition_type == 'majority_years' and 'required_years' in locals():
        result['required_years'] = required_years

    # 重命名 key 以匹配 FilterBuilder.add_filter 的参数名
    final_result = {
        'filter_type': result.pop('filter_type'),
    }
    final_result.update(result)

    return final_result
