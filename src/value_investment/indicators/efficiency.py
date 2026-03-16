"""Efficiency indicators: Payable Turnover, Expense Ratio, Fee Rate, etc."""

import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class WorkingCapitalIndicator(BaseIndicator):
    """Working Capital = 应收账款 + 预付款项 + 存货 + 合同资产 - (应付账款 + 预收款项 + 合同负债)

    反映企业运营资金占用情况，越低说明对上下游议价能力越强
    """

    name = "working_capital"
    description = "Working Capital (流动资金 = 应收+预付+存货+合同资产 - 应付-预收-合同负债)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 流动资产部分
        ar_col = self._find_column(data, ['accounts_receivable', 'ACCOUNTS_RECE'])
        prepay_col = self._find_column(data, ['prepayment', 'PREPAYMENT'])
        inv_col = self._find_column(data, ['inventory', 'INVENTORY'])
        ca_col = self._find_column(data, ['contract_assets', 'CONTRACT_ASSETS'])

        # 流动负债部分
        ap_col = self._find_column(data, ['accounts_payable', 'ACCOUNTS_PAYABLE'])
        adv_col = self._find_column(data, ['adv_receipts', 'ADV_RECEIPTS'])
        cl_col = self._find_column(data, ['contract_liab', 'CONTRACT_LIAB'])

        # 计算各项（缺失则为0）
        ar = data[ar_col] if ar_col else pd.Series(0, index=data.index)
        prepay = data[prepay_col] if prepay_col else pd.Series(0, index=data.index)
        inv = data[inv_col] if inv_col else pd.Series(0, index=data.index)
        ca = data[ca_col] if ca_col else pd.Series(0, index=data.index)

        ap = data[ap_col] if ap_col else pd.Series(0, index=data.index)
        adv = data[adv_col] if adv_col else pd.Series(0, index=data.index)
        cl = data[cl_col] if cl_col else pd.Series(0, index=data.index)

        # 计算流动资金
        wc = (ar + prepay + inv + ca) - (ap + adv + cl)

        return IndicatorResult(
            value=float(wc.mean()) if len(wc) > 0 else 0.0,
            unit="元",
            description="Working Capital (流动资金)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=wc.tolist() if len(wc) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['accounts_receivable', 'prepayment', 'inventory', 'contract_assets',
                'accounts_payable', 'adv_receipts', 'contract_liab']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class WCToRevenueIndicator(BaseIndicator):
    """WC to Revenue Ratio = Working Capital / Operating Revenue

    反映1元收入占用的流动资金，越低说明运营效率越高
    """

    name = "wc_to_revenue"
    description = "WC to Revenue Ratio (1元收入占用流动资金)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 先计算 WC
        ar_col = self._find_column(data, ['accounts_receivable', 'ACCOUNTS_RECE'])
        prepay_col = self._find_column(data, ['prepayment', 'PREPAYMENT'])
        inv_col = self._find_column(data, ['inventory', 'INVENTORY'])
        ca_col = self._find_column(data, ['contract_assets', 'CONTRACT_ASSETS'])
        ap_col = self._find_column(data, ['accounts_payable', 'ACCOUNTS_PAYABLE'])
        adv_col = self._find_column(data, ['adv_receipts', 'ADV_RECEIPTS'])
        cl_col = self._find_column(data, ['contract_liab', 'CONTRACT_LIAB'])
        revenue_col = self._find_column(data, ['operating_revenue', 'OPERATE_INCOME', 'TOTAL_OPERATE_INCOME', 'total_revenue'])

        # 计算 WC
        ar = data[ar_col] if ar_col else pd.Series(0, index=data.index)
        prepay = data[prepay_col] if prepay_col else pd.Series(0, index=data.index)
        inv = data[inv_col] if inv_col else pd.Series(0, index=data.index)
        ca = data[ca_col] if ca_col else pd.Series(0, index=data.index)
        ap = data[ap_col] if ap_col else pd.Series(0, index=data.index)
        adv = data[adv_col] if adv_col else pd.Series(0, index=data.index)
        cl = data[cl_col] if cl_col else pd.Series(0, index=data.index)

        wc = (ar + prepay + inv + ca) - (ap + adv + cl)

        # 获取营业收入
        revenue = data[revenue_col] if revenue_col else pd.Series([1], index=data.index)

        # 计算比率
        ratio = wc / revenue.replace(0, 1)

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="ratio",
            description="WC to Revenue Ratio (1元收入占用流动资金)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['accounts_receivable', 'prepayment', 'inventory', 'contract_assets',
                'accounts_payable', 'adv_receipts', 'contract_liab', 'operating_revenue']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class RevenuePerEmployeeIndicator(BaseIndicator):
    """Revenue per Employee = Operating Revenue / Employee Count

    反映人均产出效率。注意：员工人数需要从外部数据源获取（如tushare公司基本信息接口）。

    数据来源参考：
    - tushare: stock_company接口的employee字段
    - 同花顺/东方财富F10公司概况
    - 年报附注"公司员工情况"
    """

    name = "revenue_per_employee"
    description = "Revenue per Employee (人均收入，需要员工人数外部数据)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        revenue_col = self._find_column(data, ['operating_revenue', 'OPERATE_INCOME', 'TOTAL_OPERATE_INCOME', 'total_revenue'])

        # 尝试从 kwargs 获取员工人数
        employee_count = kwargs.get('employee_count', None)

        if employee_count is None:
            # 尝试从数据列中获取
            emp_col = self._find_column(data, ['employee_count', 'EMPLOYEE_COUNT'])
            if emp_col:
                employee_count = data[emp_col].iloc[0]

        revenue = data[revenue_col] if revenue_col else pd.Series([0], index=data.index)

        if employee_count is None or employee_count == 0:
            # 返回提示信息
            return IndicatorResult(
                value=0.0,
                unit="元/人",
                description="Revenue per Employee (需要员工人数数据 - 可从tushare或web搜索获取)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[0.0] * len(revenue)
            )

        # 计算人均收入
        ratio = revenue / employee_count

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="元/人",
            description=f"Revenue per Employee (员工数: {employee_count})",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_revenue']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None

class PayableTurnoverIndicator(BaseIndicator):
    """Payable Turnover = Operating Cost / Accounts Payable"""

    name = "payable_turnover"
    description = "Payable Turnover (Operating Cost / Accounts Payable)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        cost_col = self._find_column(data, ['operating_cost'])
        ap_col = self._find_column(data, ['accounts_payable'])

        cost = data[cost_col] if cost_col else pd.Series(0, index=data.index)
        ap = data[ap_col] if ap_col else pd.Series([1], index=data.index)

        turnover = cost / ap.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Payable Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_cost', 'accounts_payable']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class ExpenseRatioIndicator(BaseIndicator):
    """Expense Ratio = (Operating Cost + Sales Expense + Management Expense + Financial Expense) / Operating Income"""

    name = "expense_ratio"
    description = "Expense Ratio ((Operating Cost + Sales/Management/Financial Expense) / Operating Income)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Total expenses = operating_cost + sales_expense + management_expense + financial_expense
        cost_col = self._find_column(data, ['operating_cost'])
        sales_exp_col = self._find_column(data, ['sales_expense'])
        mgmt_exp_col = self._find_column(data, ['management_expense'])
        fin_exp_col = self._find_column(data, ['financial_expense'])
        income_col = self._find_column(data, ['operating_income', 'total_revenue'])

        # Get expenses (default to 0 if not available)
        operating_cost = data[cost_col] if cost_col else pd.Series(0, index=data.index)
        sales_expense = data[sales_exp_col] if sales_exp_col else pd.Series(0, index=data.index)
        mgmt_expense = data[mgmt_exp_col] if mgmt_exp_col else pd.Series(0, index=data.index)
        fin_expense = data[fin_exp_col] if fin_exp_col else pd.Series(0, index=data.index)

        # Total expenses
        total_expense = operating_cost + sales_expense + mgmt_expense + fin_expense

        # Get income
        income = data[income_col] if income_col else pd.Series([1], index=data.index)

        # Calculate ratio (as percentage)
        expense_ratio = (total_expense / income.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(expense_ratio.mean()) if len(expense_ratio) > 0 else 0.0,
            unit="%",
            description="Expense Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=expense_ratio.tolist() if len(expense_ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_cost', 'operating_income', 'sales_expense', 'management_expense', 'financial_expense']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FeeRateIndicator(BaseIndicator):
    """Fee Rate = (Sales Expense + Management Expense + Financial Expense) / Operating Income"""

    name = "fee_rate"
    description = "Fee Rate ((Sales/Management/Financial Expense) / Operating Income)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Fee rate = (sales_expense + management_expense + financial_expense) / operating_income
        sales_exp_col = self._find_column(data, ['sales_expense'])
        mgmt_exp_col = self._find_column(data, ['management_expense'])
        fin_exp_col = self._find_column(data, ['financial_expense'])
        income_col = self._find_column(data, ['operating_income', 'total_revenue'])

        # Get fee expenses (default to 0 if not available)
        sales_expense = data[sales_exp_col] if sales_exp_col else pd.Series(0, index=data.index)
        mgmt_expense = data[mgmt_exp_col] if mgmt_exp_col else pd.Series(0, index=data.index)
        fin_expense = data[fin_exp_col] if fin_exp_col else pd.Series(0, index=data.index)

        # Total fee expenses
        total_fee = sales_expense + mgmt_expense + fin_expense

        # Get income
        income = data[income_col] if income_col else pd.Series([1], index=data.index)

        # Calculate ratio (as percentage)
        fee_rate = (total_fee / income.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(fee_rate.mean()) if len(fee_rate) > 0 else 0.0,
            unit="%",
            description="Fee Rate",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=fee_rate.tolist() if len(fee_rate) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_income', 'sales_expense', 'management_expense', 'financial_expense']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FixedAssetTurnoverIndicator(BaseIndicator):
    """Fixed Asset Turnover = Operating Income / Fixed Assets"""

    name = "fixed_asset_turnover"
    description = "Fixed Asset Turnover (Operating Income / Fixed Assets)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        income_col = self._find_column(data, ['operating_income'])
        fa_col = self._find_column(data, ['fixed_assets'])

        income = data[income_col] if income_col else pd.Series(0, index=data.index)
        fixed_assets = data[fa_col] if fa_col else pd.Series([1], index=data.index)

        turnover = income / fixed_assets.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Fixed Asset Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_income', 'fixed_assets']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FeeToGrossProfitRatioIndicator(BaseIndicator):
    """Fee to Gross Profit Ratio = 三费 / 毛利润

    Formula: (sales_expense + management_expense + financial_expense) / (operating_income - operating_cost)
    Thresholds: <50%优秀, >70%无关注价值

    From 手把手教你读财报: 如果费用占毛利润比例在50%以内，算是优秀的公司；
    如果在30%-70%区域，但仍是有一定优势的公司；如果超过70%，通常关注的价值不大
    """

    name = "fee_to_gross_profit_ratio"
    description = "Fee to Gross Profit Ratio (三费/毛利润)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get expense columns
        sales_exp_col = self._find_column(data, ['sales_expense'])
        mgmt_exp_col = self._find_column(data, ['management_expense'])
        fin_exp_col = self._find_column(data, ['financial_expense'])

        # Get income and cost columns
        income_col = self._find_column(data, ['operating_income', 'total_revenue'])
        cost_col = self._find_column(data, ['operating_cost'])

        # Get expenses (default to 0 if not available)
        sales_expense = data[sales_exp_col] if sales_exp_col else pd.Series(0, index=data.index)
        mgmt_expense = data[mgmt_exp_col] if mgmt_exp_col else pd.Series(0, index=data.index)
        fin_expense = data[fin_exp_col] if fin_exp_col else pd.Series(0, index=data.index)

        # Total three fees (三费)
        total_fee = sales_expense + mgmt_expense + fin_expense

        # Get income and cost
        income = data[income_col] if income_col else pd.Series(0, index=data.index)
        cost = data[cost_col] if cost_col else pd.Series(0, index=data.index)

        # Calculate gross profit (毛利润)
        gross_profit = income - cost

        # Calculate ratio (as percentage), handle division by zero
        # If gross profit is 0 or negative, return 0
        ratio = pd.Series(0.0, index=data.index)
        valid_mask = gross_profit > 0
        ratio[valid_mask] = (total_fee[valid_mask] / gross_profit[valid_mask]) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="Fee to Gross Profit Ratio (费用占毛利润比)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_income', 'operating_cost', 'sales_expense', 'management_expense', 'financial_expense']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class AccountsReceivableRatioIndicator(BaseIndicator):
    """Accounts Receivable to Revenue Ratio = 应收账款 / 营业收入

    Formula: accounts_receivable / operating_income
    Threshold: >30%需警惕

    From 手把手教你读财报: 应收账款占营业收入的比例较大，且有大部分（如超过三成）是一年以上的应收款，需警惕
    """

    name = "accounts_receivable_ratio"
    description = "Accounts Receivable to Revenue Ratio (应收账款/营业收入)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get columns
        ar_col = self._find_column(data, ['accounts_receivable'])
        income_col = self._find_column(data, ['operating_income', 'total_revenue'])

        # Get accounts receivable and revenue
        accounts_receivable = data[ar_col] if ar_col else pd.Series(0, index=data.index)
        income = data[income_col] if income_col else pd.Series([1], index=data.index)

        # Calculate ratio (as percentage), handle division by zero
        ratio = pd.Series(0.0, index=data.index)
        valid_mask = income != 0
        ratio[valid_mask] = (accounts_receivable[valid_mask] / income[valid_mask].abs()) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="Accounts Receivable to Revenue Ratio (应收账款占比)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['accounts_receivable', 'operating_income']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class ProductionAssetRatioIndicator(BaseIndicator):
    """Production Asset Ratio = 生产资产 / 总资产

    Formula: (fixed_assets + construction_in_progress + project_materials) / total_assets
    Note: In strict definition, land (part of intangible assets) should be included,
    but typically not separated in financial data.

    From 手把手教你读财报: 生产资产占总资产的比例，占比大称为"重资产公司"，占比小称为"轻资产公司"
    """

    name = "production_asset_ratio"
    description = "Production Asset Ratio (生产资产/总资产)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get columns
        fixed_col = self._find_column(data, ['fixed_assets'])
        cip_col = self._find_column(data, ['construction_in_progress'])
        material_col = self._find_column(data, ['project_materials'])
        total_col = self._find_column(data, ['total_assets'])

        # Get values (default to 0 if not available)
        fixed_assets = data[fixed_col] if fixed_col else pd.Series(0, index=data.index)
        construction = data[cip_col] if cip_col else pd.Series(0, index=data.index)
        materials = data[material_col] if material_col else pd.Series(0, index=data.index)
        total_assets = data[total_col] if total_col else pd.Series([1], index=data.index)

        # Calculate production assets
        production_assets = fixed_assets + construction + materials

        # Calculate ratio (as percentage), handle division by zero
        ratio = pd.Series(0.0, index=data.index)
        valid_mask = total_assets != 0
        ratio[valid_mask] = (production_assets[valid_mask] / total_assets[valid_mask].abs()) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="Production Asset Ratio (生产资产占比)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['fixed_assets', 'construction_in_progress', 'project_materials', 'total_assets']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class ReturnOnProductionAssetsIndicator(BaseIndicator):
    """Return on Production Assets = 税前利润 / 生产资产

    Formula: total_profit / (fixed_assets + construction_in_progress + project_materials)

    From 手把手教你读财报: 用"税前利润总额÷生产资产"，得出的比值如果显著高于
    社会平均资本回报率（银行借款标准利率的两倍左右），则属于优秀公司，是其竞争力的体现
    """

    name = "return_on_production_assets"
    description = "Return on Production Assets (税前利润/生产资产)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get profit column
        profit_col = self._find_column(data, ['total_profit', 'profit_before_tax'])

        # Get production asset columns
        fixed_col = self._find_column(data, ['fixed_assets'])
        cip_col = self._find_column(data, ['construction_in_progress'])
        material_col = self._find_column(data, ['project_materials'])

        # Get values (default to 0 if not available)
        total_profit = data[profit_col] if profit_col else pd.Series(0, index=data.index)
        fixed_assets = data[fixed_col] if fixed_col else pd.Series(0, index=data.index)
        construction = data[cip_col] if cip_col else pd.Series(0, index=data.index)
        materials = data[material_col] if material_col else pd.Series(0, index=data.index)

        # Calculate production assets
        production_assets = fixed_assets + construction + materials

        # Calculate return (as percentage), handle division by zero
        ratio = pd.Series(0.0, index=data.index)
        valid_mask = production_assets > 0
        ratio[valid_mask] = (total_profit[valid_mask] / production_assets[valid_mask]) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="Return on Production Assets (税前利润/生产资产)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['total_profit', 'fixed_assets', 'construction_in_progress', 'project_materials']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class ReceivablesToAssetsRatioIndicator(BaseIndicator):
    """Receivables to Total Assets Ratio = 应收类科目 / 总资产

    Formula: (accounts_receivable + notes_receivable + other_receivables) / total_assets
    Note: Bank acceptances (银票) typically not available separately in financial data

    From 手把手教你读财报: 所有带"应收"两个字的科目总和，减去银票金额，
    看其占总资产比例是否过大，一般超过三成已经算严重，过半显然有问题
    """

    name = "receivables_to_assets_ratio"
    description = "Receivables to Total Assets Ratio (应收类科目/总资产)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get receivable columns
        ar_col = self._find_column(data, ['accounts_receivable'])
        notes_col = self._find_column(data, ['notes_receivable'])
        other_col = self._find_column(data, ['other_receivables', 'other_receivable'])
        total_col = self._find_column(data, ['total_assets'])

        # Get values (default to 0 if not available)
        accounts_receivable = data[ar_col] if ar_col else pd.Series(0, index=data.index)
        notes_receivable = data[notes_col] if notes_col else pd.Series(0, index=data.index)
        other_receivables = data[other_col] if other_col else pd.Series(0, index=data.index)
        total_assets = data[total_col] if total_col else pd.Series([1], index=data.index)

        # Calculate total receivables (应收类科目)
        total_receivables = accounts_receivable + notes_receivable + other_receivables

        # Calculate ratio (as percentage), handle division by zero
        ratio = pd.Series(0.0, index=data.index)
        valid_mask = total_assets != 0
        ratio[valid_mask] = (total_receivables[valid_mask] / total_assets[valid_mask].abs()) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="Receivables to Total Assets Ratio (应收类科目占比)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['accounts_receivable', 'notes_receivable', 'other_receivables', 'total_assets']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FixedAssetToRevenueIndicator(BaseIndicator):
    """Fixed Asset to Revenue = 一元营收需要固定资产

    Formula: (fixed_assets + construction_in_progress) / total_revenue
    From 手把手教你读财报: 用（固定资产净额+在建工程）除以营业收入，
    看企业生产每元营收需要投入多少固定资产

    This indicator measures asset efficiency - how much fixed asset investment
    is needed to generate one unit of revenue.
    """

    name = "fixed_asset_to_revenue"
    description = "一元营收需要固定资产 ((固定资产+在建工程)/营业收入)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get fixed asset columns (support multiple field names)
        fixed_col = self._find_column(data, ['fixed_assets'])
        # construction_in_progress for HK, cip for A-share
        cip_col = self._find_column(data, ['construction_in_progress', 'cip'])
        # Get revenue column
        revenue_col = self._find_column(data, ['total_revenue', 'operating_income', 'revenue'])

        # Get values (default to 0 if not available)
        fixed_assets = data[fixed_col] if fixed_col else pd.Series(0, index=data.index)
        construction = data[cip_col] if cip_col else pd.Series(0, index=data.index)
        revenue = data[revenue_col] if revenue_col else pd.Series([1], index=data.index)

        # Calculate total fixed assets (固定资产 + 在建工程)
        total_fixed = fixed_assets + construction

        # Calculate ratio, handle division by zero
        ratio = pd.Series(0.0, index=data.index)
        valid_mask = (revenue != 0) & (revenue.notna())
        ratio[valid_mask] = total_fixed[valid_mask] / revenue[valid_mask].abs()

        # Get years and sort by year descending to get most recent value
        years = data['year'].tolist() if 'year' in data.columns else []
        values = ratio.tolist() if len(ratio) > 0 else []

        # Find most recent year's value
        if years and values:
            # Sort by year descending and get the first (most recent) value
            year_value_pairs = sorted(zip(years, values), key=lambda x: x[0], reverse=True)
            most_recent_value = year_value_pairs[0][1] if year_value_pairs else 0.0
        else:
            most_recent_value = 0.0

        return IndicatorResult(
            value=float(most_recent_value),
            unit="ratio",
            description="一元营收需要固定资产 ((固定资产+在建工程)/营业收入)",
            years=years,
            values=values
        )

    def get_required_fields(self) -> list[str]:
        return ['fixed_assets', 'construction_in_progress', 'total_revenue']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
