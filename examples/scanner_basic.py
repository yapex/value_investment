"""基础示例：使用 Scanner 筛选股票

运行前请设置环境变量:
    export TUSHARE_TOKEN="your_token"

运行:
    uv run python examples/scanner_basic.py
"""
from value_investment import Scanner, filters


def main():
    print("=" * 60)
    print("基础股票筛选示例")
    print("=" * 60)

    # 初始化
    scanner = Scanner(market="A")

    # 获取股票列表（取前 20 只测试）
    print("\n1. 获取股票列表...")
    stocks = scanner.get_stock_list()
    test_stocks = stocks['symbol'].head(20).tolist()
    print(f"   测试股票：{len(test_stocks)} 只")

    # 获取财务数据
    print("\n2. 获取财务数据（ROE）...")
    financials = scanner.get_financial_data(
        stocks=test_stocks,
        fields=['roe'],
        years=5
    )
    print(f"   获取到 {financials['stock_code'].nunique()} 只股票的数据")

    # 筛选：连续 5 年 ROE >= 15%
    print("\n3. 筛选：连续 5 年 ROE >= 15%...")
    result = filters.consecutive_years(
        financials,
        field='roe',
        min_value=15,
        years=5
    )

    # 显示结果
    print(f"\n4. 结果：{result['stock_code'].nunique()} 只股票符合条件")

    if not result.empty:
        # 合并股票名称
        result_named = result.merge(
            stocks[['symbol', 'name']],
            left_on='stock_code',
            right_on='symbol'
        )
        print("\n   符合条件的股票:")
        for code in result_named['stock_code'].unique():
            name = result_named[result_named['stock_code'] == code]['name'].iloc[0]
            roe_values = result_named[result_named['stock_code'] == code]['roe'].tolist()
            print(f"   - {code} ({name}): ROE = {roe_values}")

    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
