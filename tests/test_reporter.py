"""Tests for reporter module - generate Markdown reports from analysis results"""
import pytest
from datetime import datetime


class TestGenerateReport:
    """Test generate_report function"""

    def test_generate_report_exists(self):
        """generate_report function should exist"""
        from value_investment.analysis.reporter import generate_report
        assert callable(generate_report)

    def test_generate_report_returns_string(self):
        """generate_report should return a string"""
        from value_investment.analysis.reporter import generate_report
        
        # Mock indicators data (similar to API analyze output)
        indicators = {
            "name": "测试股票 (000001)",
            "year_range": "2020-2024",
            "summary": [
                {"label": "ROE", "value": "15.2%"},
                {"label": "ROIC", "value": "12.3%"},
                {"label": "毛利率", "value": "35.6%"},
            ],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        assert isinstance(result, str)

    def test_generate_report_contains_stock_name(self):
        """Report should contain stock name"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "腾讯控股 (00700)",
            "year_range": "2020-2024",
            "summary": [
                {"label": "ROE", "value": "25.0%"},
            ],
            "table": [],
        }
        
        result = generate_report(indicators, "00700")
        assert "腾讯控股" in result
        assert "00700" in result

    def test_generate_report_contains_year_range(self):
        """Report should contain year range"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "测试股票",
            "year_range": "2020-2024",
            "summary": [],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        assert "2020-2024" in result

    def test_generate_report_contains_summary_metrics(self):
        """Report should contain summary metrics"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "测试股票",
            "year_range": "2020-2024",
            "summary": [
                {"label": "ROE", "value": "15.2%"},
                {"label": "ROIC", "value": "12.3%"},
                {"label": "毛利率", "value": "35.6%"},
            ],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        assert "ROE" in result
        assert "15.2%" in result
        assert "ROIC" in result
        assert "12.3%" in result
        assert "毛利率" in result
        assert "35.6%" in result

    def test_generate_report_is_markdown_format(self):
        """Report should be in Markdown format"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "测试股票",
            "year_range": "2020-2024",
            "summary": [
                {"label": "ROE", "value": "15.2%"},
            ],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        # Check for Markdown formatting elements
        assert "#" in result  # Headers

    def test_generate_report_with_empty_summary(self):
        """Report should handle empty summary"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "测试股票",
            "year_range": "2020-2024",
            "summary": [],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        assert isinstance(result, str)
        assert "测试股票" in result

    def test_generate_report_with_warnings(self):
        """Report should contain warnings if present"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "测试股票",
            "year_range": "2020-2024",
            "summary": [
                {"label": "ROE", "value": "15.2%"},
            ],
            "warnings": [
                "流动比率低于1.0",
                "应收账款周转率异常",
            ],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        assert "流动比率低于1.0" in result
        assert "应收账款周转率异常" in result

    def test_generate_report_with_notes(self):
        """Report should contain notes if present"""
        from value_investment.analysis.reporter import generate_report
        
        indicators = {
            "name": "测试股票",
            "year_range": "2020-2024",
            "summary": [
                {"label": "ROE", "value": "15.2%"},
            ],
            "notes": [
                "2023年有新业务上线",
                "2024年完成并购",
            ],
            "table": [],
        }
        
        result = generate_report(indicators, "000001")
        assert "2023年有新业务上线" in result
        assert "2024年完成并购" in result

    def test_generate_report_with_table_data(self):
        """Report should contain table data if present"""
        from value_investment.analysis.reporter import generate_report
        import pandas as pd
        
        # Create sample table data
        table_data = [
            {"年份": 2024, "ROE": "15.2%", "毛利率": "35.6%"},
            {"年份": 2023, "ROE": "14.8%", "毛利率": "34.2%"},
        ]
        
        indicators = {
            "name": "测试股票",
            "year_range": "2023-2024",
            "summary": [],
            "table": pd.DataFrame(table_data),
        }
        
        result = generate_report(indicators, "000001")
        assert "2024" in result
        assert "2023" in result
        assert "ROE" in result
        assert "毛利率" in result
