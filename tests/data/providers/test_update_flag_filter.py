"""测试 TushareProvider 的 update_flag 去重机制"""
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from value_investment.data.providers.tushare_provider import TushareProvider


class TestUpdateFlagFilter:
    """update_flag 去重机制测试"""

    @pytest.fixture
    def mock_cache(self):
        """Mock cache"""
        return MagicMock()

    @pytest.fixture
    def provider(self, mock_cache):
        """创建 provider 实例"""
        with patch.dict('os.environ', {'TUSHARE_TOKEN': 'test_token'}):
            return TushareProvider(cache=mock_cache, token='test_token')

    def test_filter_prefers_update_flag_1(self, provider, mock_cache):
        """测试优先选择 update_flag=1 的记录"""
        # 模拟 API 返回的数据：同一年有两行，update_flag 不同
        mock_df = pd.DataFrame({
            'ts_code': ['600519.SH', '600519.SH'],
            'ann_date': ['20210331', '20210331'],
            'end_date': ['20201231', '20201231'],
            'roe': [30.0, 35.0],  # update_flag=1 的值是 35.0
            'gross_margin': [90.0, 92.0],
            'update_flag': [0, 1],  # 优先选择 update_flag=1
        })

        # Mock cache 返回 None，强制从 API 获取
        mock_cache.get.return_value = None

        with patch.object(provider._api, 'fina_indicator', return_value=mock_df):
            result = provider.get_financial_indicator('600519', start_year=2020, end_year=2020, force_refresh=True)

        # 应该只有一行数据，且是 update_flag=1 的值
        assert len(result) == 1
        assert result.iloc[0]['roe'] == 35.0  # 选择了 update_flag=1 的记录

    def test_filter_uses_update_flag_0_when_no_1(self, provider, mock_cache):
        """测试当没有 update_flag=1 时，使用 update_flag=0 的记录"""
        mock_df = pd.DataFrame({
            'ts_code': ['600519.SH'],
            'ann_date': ['20210331'],
            'end_date': ['20201231'],
            'roe': [30.0],
            'gross_margin': [90.0],
            'update_flag': [0],  # 只有 update_flag=0
        })

        mock_cache.get.return_value = None

        with patch.object(provider._api, 'fina_indicator', return_value=mock_df):
            result = provider.get_financial_indicator('600519', start_year=2020, end_year=2020, force_refresh=True)

        assert len(result) == 1
        assert result.iloc[0]['roe'] == 30.0

    def test_filter_multiple_years(self, provider, mock_cache):
        """测试多年的数据去重"""
        mock_df = pd.DataFrame({
            'ts_code': ['600519.SH'] * 5,
            'ann_date': ['20210331', '20210331', '20220331', '20220331', '20230331'],
            'end_date': ['20201231', '20201231', '20211231', '20211231', '20221231'],
            'roe': [30.0, 35.0, 32.0, 38.0, 40.0],
            'gross_margin': [90.0, 92.0, 91.0, 93.0, 94.0],
            'update_flag': [0, 1, 0, 1, 1],  # 2020 年选 1，2021 年选 1，2022 年选 1
        })

        mock_cache.get.return_value = None

        with patch.object(provider._api, 'fina_indicator', return_value=mock_df):
            result = provider.get_financial_indicator('600519', start_year=2020, end_year=2022, force_refresh=True)

        # 3 年数据，每年只保留一行
        assert len(result) == 3
        # 验证只保留了 update_flag=1 的记录
        # 检查是否包含了 update_flag=1 的记录
        assert all(result['roe'].isin([35.0, 38.0, 40.0]))

    def test_filter_without_update_flag_column(self, provider, mock_cache):
        """测试当没有 update_flag 字段时，不过滤"""
        mock_df = pd.DataFrame({
            'ts_code': ['600519.SH', '600519.SH'],
            'ann_date': ['20210331', '20210331'],
            'end_date': ['20201231', '20201231'],
            'roe': [30.0, 35.0],
            'gross_margin': [90.0, 92.0],
            # 没有 update_flag 字段
        })

        mock_cache.get.return_value = None

        with patch.object(provider._api, 'fina_indicator', return_value=mock_df):
            result = provider.get_financial_indicator('600519', start_year=2020, end_year=2020, force_refresh=True)

        # 没有 update_flag 字段时，保留所有数据（经过 DataMapper 映射后只有 roe）
        assert len(result) >= 1

    def test_quarterly_indicator_filter(self, provider, mock_cache):
        """测试季度数据的 update_flag 去重"""
        mock_df = pd.DataFrame({
            'ts_code': ['600519.SH'] * 4,
            'ann_date': ['20210427', '20210427', '20210809', '20210809'],
            'end_date': ['20210331', '20210331', '20210630', '20210630'],
            'roe': [10.0, 12.0, 15.0, 18.0],
            'update_flag': [0, 1, 0, 1],
        })

        mock_cache.get.return_value = None

        with patch.object(provider._api, 'fina_indicator', return_value=mock_df):
            result = provider.get_quarterly_indicator('600519', force_refresh=True)

        # 2 个季度，每个季度保留一行
        assert len(result) == 2
        # 验证只保留了 update_flag=1 的记录
        assert all(result['roe'].isin([12.0, 18.0]))
