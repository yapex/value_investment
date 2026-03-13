"""测试 Scanner 文本解析器"""
import pytest

from value_investment.scanner.pipeline import FilterBuilder


class TestTextParser:
    """文本解析器测试"""

    def test_parse_single_condition_consecutive(self):
        """测试解析单条件 - 连续N年"""
        from value_investment.scanner.parser import parse_filter

        fb = parse_filter("ROE 连续5年 ≥15%")

        assert len(fb) == 1
        config = fb.to_config()
        assert config[0]['type'] == 'consecutive_years'
        assert config[0]['params']['field'] == 'roe'
        assert config[0]['params']['min_value'] == 15
        assert config[0]['params']['years'] == 5

    def test_parse_single_condition_latest(self):
        """测试解析单条件 - 最近1年"""
        from value_investment.scanner.parser import parse_filter

        fb = parse_filter("ROE 最近1年 ≥20%")

        assert len(fb) == 1
        config = fb.to_config()
        assert config[0]['type'] == 'latest_year'
        assert config[0]['params']['field'] == 'roe'
        assert config[0]['params']['min_value'] == 20

    def test_parse_single_condition_majority(self):
        """测试解析单条件 - 多数年份"""
        from value_investment.scanner.parser import parse_filter

        fb = parse_filter("ROE 5年至少4年 ≥15%")

        assert len(fb) == 1
        config = fb.to_config()
        assert config[0]['type'] == 'majority_years'
        assert config[0]['params']['field'] == 'roe'
        assert config[0]['params']['min_value'] == 15
        assert config[0]['params']['years'] == 5
        assert config[0]['params']['required_years'] == 4

    def test_parse_single_condition_with_avg(self):
        """测试解析单条件 - 带平均值要求"""
        from value_investment.scanner.parser import parse_filter

        fb = parse_filter("ROE 5年至少4年 ≥15%, 平均≥15%")

        assert len(fb) == 1
        config = fb.to_config()
        assert config[0]['params']['min_avg'] == 15

    def test_parse_multiple_conditions_and(self):
        """测试解析多条件 - 且 (AND)"""
        from value_investment.scanner.parser import parse_filter

        fb = parse_filter("ROE 连续5年 ≥15% 且 毛利率 连续5年 ≥30%")

        assert len(fb) == 2
        config = fb.to_config()

        # 第一个条件
        assert config[0]['type'] == 'consecutive_years'
        assert config[0]['params']['field'] == 'roe'
        assert config[0]['params']['min_value'] == 15

        # 第二个条件
        assert config[1]['type'] == 'consecutive_years'
        assert config[1]['params']['field'] == 'gross_profit_margin'
        assert config[1]['params']['min_value'] == 30

    def test_parse_chinese_field_names(self):
        """测试中文字段名映射"""
        from value_investment.scanner.parser import parse_filter

        # 毛利率
        fb = parse_filter("毛利率 连续5年 ≥30%")
        assert fb.to_config()[0]['params']['field'] == 'gross_profit_margin'

        # 净利率
        fb = parse_filter("净利率 最近1年 ≥10%")
        assert fb.to_config()[0]['params']['field'] == 'net_profit_margin'

        # 负债率
        fb = parse_filter("负债率 最近1年 ≤60%")
        assert fb.to_config()[0]['params']['field'] == 'debt_to_asset'

    def test_parse_different_operators(self):
        """测试不同运算符"""
        from value_investment.scanner.parser import parse_filter

        # ≥ 大于等于
        fb = parse_filter("ROE 连续5年 ≥15%")
        assert fb.to_config()[0]['params']['min_value'] == 15

        # ≤ 小于等于
        fb = parse_filter("负债率 最近1年 ≤60%")
        assert fb.to_config()[0]['params']['max_value'] == 60

    def test_parse_invalid_format(self):
        """测试无效格式"""
        from value_investment.scanner.parser import parse_filter, ParseError

        with pytest.raises(ParseError):
            parse_filter("这是无效的格式")

    def test_parse_empty_string(self):
        """测试空字符串"""
        from value_investment.scanner.parser import parse_filter, ParseError

        with pytest.raises(ParseError):
            parse_filter("")
