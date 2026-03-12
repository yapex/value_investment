"""测试：港股筛选毛利率 > 30% 的股票"""
import pytest
from value_investment import Scanner
from value_investment.scanner import filters


def test_hk_gross_profit_margin_filter():
    """筛选条件：最近一年毛利率 >= 30%"""
    scanner = Scanner(market="HK")
    
    print(f"\n=== 港股毛利率筛选测试 ===")
    
    # 获取港股列表
    stocks = scanner.get_stock_list()
    print(f"港股数量：{len(stocks)} 只")
    
    # 获取财务数据（毛利率）
    print("获取财务数据（毛利率）...")
    hk_codes = stocks['symbol'].tolist()
    
    financials = scanner.get_financial_data(
        stocks=hk_codes,
        fields=['gross_profit_margin'],
        years=5
    )
    
    print(f"获取到 {financials['stock_code'].nunique()} 只股票的数据")
    
    # 筛选：最近一年毛利率 >= 30%
    result = filters.latest_year(financials, field='gross_profit_margin', min_value=30)
    
    print(f"\n毛利率 >= 30% 的股票：{result['stock_code'].nunique()} 只")
    
    if not result.empty:
        print("\n符合条件的股票:")
        for code in sorted(result['stock_code'].unique()):
            margin = result.loc[result['stock_code'] == code, 'gross_profit_margin'].iloc[0]
            print(f"  - {code}: 毛利率 = {margin:.2f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
