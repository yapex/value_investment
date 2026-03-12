"""原型验证代码：Agent-based 股票 Scanner

验证清单：
1. 获取 A 股全市场股票代码
2. 批量获取 5 年财务数据（ROE）- 带速率限制（每分钟200次）
3. 实现复杂条件过滤：5年中4年 ROE≥15% 且平均≥15%
4. 性能测试
"""

import os
import time
from datetime import datetime

import pandas as pd
import tushare as ts


class RateLimiter:
    """速率限制器 - 限制每分钟调用次数"""

    def __init__(self, max_calls_per_minute=200):
        self.max_calls = max_calls_per_minute
        self.calls = []  # 记录每次调用的时间戳

    def wait_if_needed(self):
        """检查是否需要等待，确保不超过速率限制"""
        now = time.time()
        # 清理1分钟前的记录
        self.calls = [t for t in self.calls if now - t < 60]

        # 如果已达到限制，等待直到可以再次调用
        if len(self.calls) >= self.max_calls:
            # 计算需要等待的时间
            oldest_call = min(self.calls)
            wait_time = 60 - (now - oldest_call) + 0.1  # 多等0.1秒确保安全
            if wait_time > 0:
                print(f"  速率限制：等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
                # 重新清理
                now = time.time()
                self.calls = [t for t in self.calls if now - t < 60]

        # 记录本次调用
        self.calls.append(time.time())

    def get_status(self):
        """获取当前速率状态"""
        now = time.time()
        self.calls = [t for t in self.calls if now - t < 60]
        return {
            'calls_in_last_minute': len(self.calls),
            'remaining': self.max_calls - len(self.calls)
        }

# 设置 Tushare Token
TOKEN = os.getenv("TUSHARE_TOKEN", "")
if not TOKEN:
    print("错误：请设置 TUSHARE_TOKEN 环境变量")
    exit(1)

ts.set_token(TOKEN)
api = ts.pro_api()


def get_all_stocks():
    """获取 A 股全市场股票列表"""
    print("正在获取 A 股全市场股票列表...")
    df = api.stock_basic(
        exchange='',
        list_status='L',  # 上市
        fields='ts_code,symbol,name,area,industry,list_date'
    )
    print(f"获取到 {len(df)} 只股票")
    return df


def get_financial_indicator_batch(stock_codes, start_year=2020, end_year=2024, rate_limiter=None):
    """批量获取财务指标数据（带速率限制）

    注意：Tushare 的 fina_indicator 接口每次只能查一只股票
    使用 RateLimiter 控制每分钟调用不超过200次
    """
    if rate_limiter is None:
        rate_limiter = RateLimiter(max_calls_per_minute=200)

    print(f"正在获取 {len(stock_codes)} 只股票的财务指标 ({start_year}-{end_year})...")
    print(f"  速率限制：每分钟最多200次调用")

    all_data = []
    failed_codes = []
    start_time = time.time()

    for i, code in enumerate(stock_codes):
        if i % 50 == 0 and i > 0:
            elapsed = time.time() - start_time
            status = rate_limiter.get_status()
            print(f"  已处理 {i}/{len(stock_codes)} 只，耗时 {elapsed:.1f} 秒，剩余配额 {status['remaining']}")

        # 速率限制检查
        rate_limiter.wait_if_needed()

        try:
            df = api.fina_indicator(
                ts_code=code,
                start_date=f"{start_year}0101",
                end_date=f"{end_year}1231"
            )
            if df is not None and not df.empty:
                # 只保留年报数据（12月31日）
                annual = df[df['end_date'].astype(str).str.endswith('1231')].copy()
                if not annual.empty:
                    annual['stock_code'] = code.replace('.SH', '').replace('.SZ', '')
                    all_data.append(annual)
        except Exception as e:
            failed_codes.append((code, str(e)))

    if failed_codes:
        print(f"  失败 {len(failed_codes)} 只")

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        print(f"  成功获取 {len(result)} 条记录，涉及 {result['stock_code'].nunique()} 只股票")
        return result
    return pd.DataFrame()


def filter_roe_condition(df, min_roe=15, years=5, min_count=4, avg_min=15):
    """过滤条件：N年中至少M年 ROE≥X，且平均ROE≥Y

    Args:
        df: 财务指标 DataFrame
        min_roe: ROE 最低值（%）
        years: 考察年数
        min_count: 至少满足条件的年数
        avg_min: 平均 ROE 最低值

    Returns:
        符合条件的股票代码列表
    """
    print(f"\n过滤条件：最近{years}年中至少{min_count}年 ROE≥{min_roe}%，且平均ROE≥{avg_min}%")

    # 确保 end_date 是日期类型
    df = df.copy()
    df['end_date'] = pd.to_datetime(df['end_date'])

    # 按股票分组统计
    results = []

    for code, group in df.groupby('stock_code'):
        # 取最近 N 年
        recent = group.nlargest(years, 'end_date')

        if len(recent) < years:
            continue  # 数据不足

        roe_values = recent['roe'].astype(float)

        # 条件1：至少 M 年 ROE >= X
        count_meet = (roe_values >= min_roe).sum()

        # 条件2：平均 ROE >= Y
        avg_roe = roe_values.mean()

        if count_meet >= min_count and avg_roe >= avg_min:
            results.append({
                'stock_code': code,
                'name': recent['name'].iloc[0] if 'name' in recent.columns else '',
                'roe_count': count_meet,
                'roe_avg': round(avg_roe, 2),
                'roe_values': roe_values.tolist()
            })

    result_df = pd.DataFrame(results)
    print(f"符合条件：{len(result_df)} 只股票")
    return result_df


def main():
    """主流程 - 小规模验证（20只股票）"""
    start_time = time.time()

    # 方案1: 使用固定的小规模测试股票（包含已知的好股票如茅台）
    test_codes = [
        '600519.SH',  # 贵州茅台
        '000858.SZ',  # 五粮液
        '000333.SZ',  # 美的集团
        '000651.SZ',  # 格力电器
        '600036.SH',  # 招商银行
        '600276.SH',  # 恒瑞医药
        '600887.SH',  # 伊利股份
        '002415.SZ',  # 海康威视
        '600009.SH',  # 上海机场
        '600030.SH',  # 中信证券
        '000001.SZ',  # 平安银行
        '600000.SH',  # 浦发银行
        '601318.SH',  # 中国平安
        '601888.SH',  # 中国中免
        '600563.SH',  # 法拉电子
        '002271.SZ',  # 东方雨虹
        '600486.SH',  # 扬农化工
        '600132.SH',  # 重庆啤酒
        '000568.SZ',  # 泸州老窖
        '600809.SH',  # 山西汾酒
    ]

    print(f"测试股票数量: {len(test_codes)} 只")

    # 2. 获取财务数据（带速率限制）
    rate_limiter = RateLimiter(max_calls_per_minute=200)
    fin_df = get_financial_indicator_batch(test_codes, start_year=2020, end_year=2024, rate_limiter=rate_limiter)

    if fin_df.empty:
        print("未获取到财务数据")
        return

    # 3. 过滤条件
    result = filter_roe_condition(fin_df, min_roe=15, years=5, min_count=4, avg_min=15)

    # 4. 输出结果
    print("\n" + "="*60)
    print("筛选结果：")
    print("="*60)
    if not result.empty:
        print(result.to_string(index=False))
    else:
        print("没有符合条件的股票")

    elapsed = time.time() - start_time
    print(f"\n总耗时: {elapsed:.2f} 秒")


if __name__ == "__main__":
    main()
