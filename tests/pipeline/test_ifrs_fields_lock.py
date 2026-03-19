"""Tests for IFRS Fields lock

验证 IFRSFields 的字段数量被锁定，禁止添加新字段。
"""

import pytest


# IFRS 标准字段的固定数量
EXPECTED_IFRS_FIELD_COUNT = 38

# 已知的派生字段列表（不应在 IFRSFields 中）
KNOWN_DERIVED_FIELDS = {
    "gross_profit",
    "operating_profit_margin",
    "inventory_turnover",
    "implied_growth",
    "free_cash_flow",
}


class TestIFRSFieldsLock:
    """IFRS 字段锁定测试"""
    
    @pytest.fixture(autouse=True)
    def cleanup_test_attrs(self):
        """每个测试后清理可能添加的测试属性"""
        yield
        # 清理测试添加的属性
        from value_investment.domain.fields import IFRSFields
        for attr in ["_TEST_LOCK_FIELD", "NEW_TEST_FIELD"]:
            if hasattr(IFRSFields, attr):
                delattr(IFRSFields, attr)

    def test_ifrs_field_count_is_locked(self):
        """IFRSFields 字段数量必须等于 38"""
        from value_investment.domain.fields import IFRSFields
        
        # 获取所有 IFRS 字段
        ifrs_attrs = [
            v for k, v in vars(IFRSFields).items() 
            if k.isupper() and not callable(v)
        ]
        
        actual_count = len(ifrs_attrs)
        
        if actual_count != EXPECTED_IFRS_FIELD_COUNT:
            extra = set(ifrs_attrs) - self._get_expected_fields()
            missing = self._get_expected_fields() - set(ifrs_attrs)
            
            error_msg = [
                f"IFRSFields 字段数量错误: 期望 {EXPECTED_IFRS_FIELD_COUNT}, 实际 {actual_count}",
            ]
            if extra:
                error_msg.append(f"  多余字段: {sorted(extra)}")
            if missing:
                error_msg.append(f"  缺失字段: {sorted(missing)}")
            
            pytest.fail("\n".join(error_msg))

    def test_no_derived_fields_in_ifrs(self):
        """IFRSFields 不应包含派生字段"""
        from value_investment.domain.fields import IFRSFields
        
        ifrs_attrs = set(
            v for k, v in vars(IFRSFields).items() 
            if k.isupper() and not callable(v)
        )
        
        derived_in_ifrs = ifrs_attrs & KNOWN_DERIVED_FIELDS
        
        if derived_in_ifrs:
            pytest.fail(
                f"IFRSFields 不应包含派生字段，发现: {sorted(derived_in_ifrs)}。"
                f"派生字段应添加到 CustomFields。"
            )

    def test_ifrs_fields_are_frozen(self):
        """IFRSFields 应该是冻结的，不允许动态添加"""
        from value_investment.domain.fields import IFRSFields
        
        # 尝试添加一个正常的字段常量名称（大写，不以下划线开头）
        try:
            # 使用 setattr 绕过静态检查来测试运行时行为
            setattr(IFRSFields, "TEST_NEW_FIELD", "test_value")
            # 如果成功，说明没有冻结
            pytest.fail(
                "IFRSFields 未被冻结！可以动态添加字段。"
                "需要使用 __slots__ 或其他机制阻止动态添加。"
            )
        except (AttributeError, TypeError) as e:
            # 预期行为：无法添加新字段
            assert "已冻结" in str(e) or "frozen" in str(e).lower()

    def _get_expected_fields(self) -> set:
        """获取期望的 IFRS 字段集合"""
        # 这个列表应该与 IFRSFields 中的字段保持同步
        # 如果字段数量不对，这个测试会失败
        return {
            # 资产负债表 (14)
            "total_assets",
            "total_liabilities", 
            "total_equity",
            "current_assets",
            "current_liabilities",
            "cash_and_equivalents",
            "inventory",
            "accounts_receivable",
            "accounts_payable",
            "fixed_assets",
            "prepayment",
            "adv_receipts",
            "contract_assets",
            "contract_liab",
            # 利润表 (4)
            "total_revenue",
            "net_profit",
            "operating_profit",
            "operating_cost",
            # 现金流量表 (4)
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "capital_expenditure",
            # 财务指标 (9)
            "roe",
            "roa",
            "gross_margin",
            "net_profit_margin",
            "current_ratio",
            "quick_ratio",
            "debt_ratio",
            "asset_turnover",
            "receivable_turnover",
            # 市场数据 (7)
            "market_cap",
            "total_shares",
            "pe_ratio",
            "pb_ratio",
            "basic_eps",
            "diluted_eps",
            "book_value_per_share",
        }
