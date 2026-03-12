"""测试：使用 majority_years 筛选 100 家知名 A 股公司"""
from __future__ import annotations

import pytest
from value_investment import Scanner
from value_investment.scanner import filters

# A 股市场 100 家知名上市公司
TOP_100_A_SHARES: list[str] = [
    # 白酒/饮料
    '600519', '000858', '000568', '600809', '002304', '600702', '000799', '600779', '600197', '000721',
    # 银行
    '601398', '601288', '601939', '601166', '600036', '600000', '601009', '000001', '601818', '601998',
    # 保险/券商
    '601318', '601628', '600030', '601688', '000776',
    # 医药
    '600276', '000538', '600085', '000999', '600436', '000661', '300015', '300003', '600521', '000963',
    # 消费/食品
    '600887', '002507', '600186', '000895', '600597', '002216', '603288', '002557', '600872', '000869',
    # 家电
    '000333', '000651', '600690', '002032', '600060', '000921',
    # 汽车
    '000625', '000550', '600104', '601633', '300750', '002594',
    # 地产/建筑
    '000002', '600048', '001979', '601186', '601390', '601668', '002081',
    # 能源/化工
    '601857', '600028', '600938', '600309', '000830', '600426', '000792', '600141',
    # 科技/电子
    '002415', '000725', '601138', '002371', '600584', '002156', '600745', '000100', '600183', '002916',
    # 通信
    '000063', '600498', '601728', '600050',
    # 机械/制造
    '600031', '000157', '601369', '002158',
    # 交通运输
    '601006', '601111', '600029', '601919', '600018',
    # 公用事业
    '600900', '600795', '600011', '000543',
    # 钢铁/有色
    '600019', '000898', '601600', '600362', '000630',
    # 传媒
    '002027', '600088', '300251',
]


def test_majority_years_roe() -> None:
    """筛选条件：5 年中至少 4 年 ROE >= 15%，且平均值 >= 15%"""
    scanner = Scanner(market="A")
    
    print(f"\n测试股票数量：{len(TOP_100_A_SHARES)} 只")
    print("获取财务数据（ROE）...")
    
    financials = scanner.get_financial_data(
        stocks=TOP_100_A_SHARES,
        fields=['roe'],
        years=5
    )
    
    print(f"获取到 {financials['stock_code'].nunique()} 只股票的数据")
    
    # 筛选：5 年中至少 4 年 ROE >= 15%，且平均值 >= 15%
    result = filters.majority_years(
        financials,
        field='roe',
        min_value=15,
        years=5,
        required_years=4,
        min_avg=15
    )
    
    print(f"\n符合条件的股票：{result['stock_code'].nunique()} 只")
    
    if not result.empty:
        stocks = scanner.get_stock_list()
        
        # 转换为 list 以避免类型问题
        stock_codes: list[str] = sorted(result['stock_code'].unique().tolist())
        
        for code in stock_codes:
            stock_data = result[result['stock_code'] == code].sort_values(by='end_date')  # type: ignore[call-overload]
            name = str(stocks.loc[stocks['symbol'] == code, 'name'].iloc[0])
            
            roe_values = stock_data['roe'].tolist()
            years = stock_data['end_date'].dt.strftime('%Y').tolist()
            avg = sum(roe_values) / len(roe_values)
            
            # 统计满足条件的年份
            years_met = sum(1 for v in roe_values if v >= 15)
            
            print(f"\n{code} ({name})")
            print(f"  ROE: {dict(zip(years, [f'{v:.1f}%' for v in roe_values]))}")
            print(f"  满足条件: {years_met}/5 年，平均 {avg:.1f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
