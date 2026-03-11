"""Test for detector module - abnormal signal detection"""
import pytest
from value_investment.analysis.detector import detect_warnings


class TestROEDetection:
    """Test ROE detection - too low or too high"""

    def test_roe_too_low(self):
        """ROE below 5% should trigger warning"""
        indicators = {
            "ROE": 3.5,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        # Should have a ROE warning
        roe_warnings = [w for w in warnings if "ROE" in str(w) or "roe" in str(w).lower()]
        assert len(roe_warnings) > 0, "Should warn about low ROE"

    def test_roe_too_high(self):
        """ROE above 30% might be abnormal (need verification)"""
        indicators = {
            "ROE": 45.0,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        # Should have a ROE warning for being too high
        roe_warnings = [w for w in warnings if "ROE" in str(w) or "roe" in str(w).lower()]
        assert len(roe_warnings) > 0, "Should warn about abnormally high ROE"

    def test_roe_normal(self):
        """Normal ROE (10-20%) should not trigger warning"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        # No ROE warning
        roe_warnings = [w for w in warnings if "ROE" in str(w) and "偏低" in str(w)]
        assert len(roe_warnings) == 0, "Normal ROE should not trigger warning"


class TestGrossMarginDetection:
    """Test gross margin abnormal detection"""

    def test_gross_margin_too_low(self):
        """Gross margin below 10% should trigger warning"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 5.0,
            "net_profit_margin": 2.0,
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        margin_warnings = [w for w in warnings if "毛利" in str(w)]
        assert len(margin_warnings) > 0, "Should warn about low gross margin"

    def test_gross_margin_declining(self):
        """If current gross margin significantly lower than historical, warn"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 20.0,
            "gross_margin_3y_avg": 35.0,  # 3-year average
            "net_profit_margin": 10.0,
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        margin_warnings = [w for w in warnings if "毛利" in str(w) and "下降" in str(w)]
        assert len(margin_warnings) > 0, "Should warn about declining gross margin"


class TestCashFlowDetection:
    """Test cash flow problem detection"""

    def test_cash_flow_negative(self):
        """Negative operating cash flow is a warning"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "cfo_to_netprofit_sum": -0.2,  # CFO / Net profit < 0
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        cf_warnings = [w for w in warnings if "现金流" in str(w) or "CFO" in str(w)]
        assert len(cf_warnings) > 0, "Should warn about negative cash flow"

    def test_cash_flow_mismatch(self):
        """CFO significantly lower than net profit is a warning"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 30.0,
            "net_profit_margin": 15.0,
            "cfo_to_netprofit_sum": 0.3,  # CFO much lower than profit
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        cf_warnings = [w for w in warnings if "现金流" in str(w)]
        assert len(cf_warnings) > 0, "Should warn about cash flow mismatch"

    def test_cash_flow_healthy(self):
        """Healthy CFO/Net profit ratio (>0.8) should not warn"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "cfo_to_netprofit_sum": 1.1,  # CFO > Net profit
            "current_ratio": 1.5,
        }
        warnings, notes = detect_warnings(indicators)
        
        cf_warnings = [w for w in warnings if "现金流" in str(w)]
        assert len(cf_warnings) == 0, "Healthy cash flow should not warn"


class TestReturnTuple:
    """Test return format"""

    def test_return_type(self):
        """Should return tuple of (warnings, notes)"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "cfo_to_netprofit_sum": 1.0,
            "current_ratio": 1.5,
        }
        result = detect_warnings(indicators)
        
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Should return 2 elements"
        assert isinstance(result[0], list), "First element should be list"
        assert isinstance(result[1], list), "Second element should be list"

    def test_empty_indicators(self):
        """Empty indicators should return empty lists"""
        indicators = {}
        warnings, notes = detect_warnings(indicators)
        
        assert warnings == []
        assert notes == []


class TestLiquidityDetection:
    """Test liquidity issue detection"""

    def test_low_current_ratio(self):
        """Current ratio below 1.0 is a warning"""
        indicators = {
            "ROE": 15.0,
            "gross_margin": 30.0,
            "net_profit_margin": 10.0,
            "current_ratio": 0.8,
        }
        warnings, notes = detect_warnings(indicators)
        
        liq_warnings = [w for w in warnings if "流动比率" in str(w) or " liquidity" in str(w).lower()]
        assert len(liq_warnings) > 0, "Should warn about low current ratio"
