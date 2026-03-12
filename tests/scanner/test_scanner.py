"""Scanner 核心类测试"""
import pandas as pd
from unittest.mock import patch, MagicMock
from value_investment.scanner import Scanner


class TestScanner:
    """Scanner 测试类"""

    def test_scanner_initialization(self):
        """测试 Scanner 初始化"""
        scanner = Scanner(market="A")
        assert scanner.market == "A"

    def test_get_stock_list_mock(self):
        """测试获取股票列表（mock 版本）"""
        scanner = Scanner(market="A")
        
        # Mock Tushare API 响应
        mock_df = pd.DataFrame({
            'ts_code': ['600519.SH', '000001.SZ'],
            'symbol': ['600519', '000001'],
            'name': ['贵州茅台', '平安银行'],
        })
        
        with patch.object(scanner, '_api') as mock_api:
            mock_api.stock_basic.return_value = mock_df
            result = scanner.get_stock_list()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert '600519' in result['symbol'].values
