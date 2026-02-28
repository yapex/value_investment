"""Test for analyze method with report parameter"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


class TestAnalyzeWithReport:
    """Test analyze() method with report parameter"""

    @patch('value_investment.api.AkshareProvider')
    def test_analyze_report_false_default(self, mock_provider):
        """By default, report should be False (no report generated)"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        # Mock the provider methods to avoid actual API calls
        mock_info = pd.DataFrame([{'item': '股票名称', 'value': '测试股票'}])
        mock_provider_instance = vi._provider
        mock_provider_instance.get_stock_info = MagicMock(return_value=mock_info)
        
        # Mock financial data
        mock_financial_data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            'total_assets': [100, 90, 80],
            'net_profit': [15, 12, 10],
            'revenue': [100, 90, 80],
        })
        
        with patch.object(vi, '_prepare_data', return_value=(mock_financial_data, 1000)):
            result = vi.analyze("600519", years=3)
        
        # Without report=True, result should not contain report field
        assert "report" not in result, "Without report=True, report field should not exist"
        assert "warnings" not in result, "Without report=True, warnings field should not exist"
        assert "notes" not in result, "Without report=True, notes field should not exist"

    @patch('value_investment.api.AkshareProvider')
    def test_analyze_report_true_contains_warnings(self, mock_provider):
        """When report=True, result should contain warnings and notes"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        # Mock the provider methods
        mock_info = pd.DataFrame([{'item': '股票名称', 'value': '测试股票'}])
        mock_provider_instance = vi._provider
        mock_provider_instance.get_stock_info = MagicMock(return_value=mock_info)
        
        # Mock financial data
        mock_financial_data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            'total_assets': [100, 90, 80],
            'net_profit': [15, 12, 10],
            'revenue': [100, 90, 80],
        })
        
        with patch.object(vi, '_prepare_data', return_value=(mock_financial_data, 1000)):
            result = vi.analyze("600519", years=3, report=True)
        
        # With report=True, result should contain warnings and notes
        assert "warnings" in result, "With report=True, warnings field should exist"
        assert "notes" in result, "With report=True, notes field should exist"
        assert isinstance(result["warnings"], list), "warnings should be a list"
        assert isinstance(result["notes"], list), "notes should be a list"

    @patch('value_investment.api.AkshareProvider')
    def test_analyze_report_true_contains_report_field(self, mock_provider):
        """When report=True, result should contain Markdown report"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        # Mock the provider methods
        mock_info = pd.DataFrame([{'item': '股票名称', 'value': '测试股票'}])
        mock_provider_instance = vi._provider
        mock_provider_instance.get_stock_info = MagicMock(return_value=mock_info)
        
        # Mock financial data
        mock_financial_data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            'total_assets': [100, 90, 80],
            'net_profit': [15, 12, 10],
            'revenue': [100, 90, 80],
        })
        
        with patch.object(vi, '_prepare_data', return_value=(mock_financial_data, 1000)):
            result = vi.analyze("600519", years=3, report=True)
        
        # With report=True, result should contain report field with Markdown
        assert "report" in result, "With report=True, report field should exist"
        assert isinstance(result["report"], str), "report should be a string"
        assert len(result["report"]) > 0, "report should not be empty"
        # Report should contain key sections
        assert "测试股票" in result["report"] or "600519" in result["report"], "Report should contain stock name or code"

    @patch('value_investment.api.AkshareProvider')
    def test_analyze_report_true_calls_detector(self, mock_provider):
        """When report=True, detector.detect_warnings should be called"""
        from value_investment.api import ValueInvestment
        from value_investment.analysis import detector
        
        vi = ValueInvestment()
        
        # Mock the provider methods
        mock_info = pd.DataFrame([{'item': '股票名称', 'value': '测试股票'}])
        mock_provider_instance = vi._provider
        mock_provider_instance.get_stock_info = MagicMock(return_value=mock_info)
        
        # Mock financial data
        mock_financial_data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            'total_assets': [100, 90, 80],
            'net_profit': [15, 12, 10],
            'revenue': [100, 90, 80],
        })
        
        with patch.object(vi, '_prepare_data', return_value=(mock_financial_data, 1000)):
            with patch.object(detector, 'detect_warnings') as mock_detect:
                mock_detect.return_value = (["ROE 偏低: 3.5%"], [])
                result = vi.analyze("600519", years=3, report=True)
                
                # Verify detector was called
                mock_detect.assert_called_once()


class TestAnalyzeReportParameter:
    """Test report parameter behavior"""

    def test_report_parameter_exists(self):
        """analyze() method should accept report parameter"""
        from value_investment.api import ValueInvestment
        import inspect
        
        vi = ValueInvestment()
        sig = inspect.signature(vi.analyze)
        
        assert 'report' in sig.parameters, "analyze() should have 'report' parameter"

    def test_report_default_value_is_false(self):
        """report parameter should default to False"""
        from value_investment.api import ValueInvestment
        import inspect
        
        vi = ValueInvestment()
        sig = inspect.signature(vi.analyze)
        
        report_param = sig.parameters.get('report')
        assert report_param is not None, "report parameter should exist"
        assert report_param.default is False, "report should default to False"
