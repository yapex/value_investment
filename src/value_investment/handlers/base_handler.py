"""BaseHandler with fast-reject pattern and field mapping"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from value_investment.core.types import Message


class BaseHandler(ABC):
    """Handler 基类，实现快速拒绝模式 + 字段映射

    每个 Handler 只负责特定市场和数据类型，通过快速拒绝避免无效处理。
    字段映射由 Provider 声明 FIELD_MAPPINGS，Handler 执行 _standardize()。
    """

    def __init__(
        self,
        provider,
        target_market: str,
        supported_fields: set[str],
    ):
        self._provider = provider
        self.target_market = target_market
        self._supported_fields = supported_fields

    @property
    def can_handle(self) -> set[str]:
        """该 Handler 能处理的字段集合（supported_fields ∩ provider.supported_fields）"""
        return self._supported_fields & (
            self._provider.supported_fields if self._provider else set()
        )

    def _can_handle_market(self, message: "Message") -> bool:
        """快速判断：是否处理该市场"""
        return message.market == self.target_market

    def _can_handle_fields(self, message: "Message") -> bool:
        """快速判断：是否有可处理的字段"""
        return bool(message.require & self.can_handle)

    async def handle(self, message: "Message") -> None:
        """处理消息（模板方法）"""
        # 快速拒绝：市场不匹配
        if not self._can_handle_market(message):
            return
        # 快速拒绝：无支持的字段
        if not self._can_handle_fields(message):
            return

        # 交给子类处理具体逻辑
        await self._handle_impl(message)

    @abstractmethod
    async def _handle_impl(self, message: "Message") -> None:
        """子类实现具体处理逻辑"""
        pass

    # ========================================================================
    # 字段映射方法 (Handler 层统一执行)
    # ========================================================================

    def _standardize(
        self,
        df: pd.DataFrame | None,
        statement_type: str,
    ) -> pd.DataFrame:
        """将原始字段映射为标准字段

        从 Provider 的 FIELD_MAPPINGS 获取映射规则并执行。
        静默忽略映射中存在但原始数据中不存在的字段。
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # 从 Provider 获取映射规则
        mappings = getattr(self._provider, "FIELD_MAPPINGS", {})
        mapping = mappings.get(statement_type, {})

        if not mapping:
            return df

        # 只映射实际存在的列（静默忽略缺失字段）
        rename_map = {
            native: standard
            for native, standard in mapping.items()
            if native in df.columns
        }

        if rename_map:
            return df.rename(columns=rename_map)

        return df

    def get_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取资产负债表（执行字段映射）"""
        raw_df = self._provider.fetch_raw_balance_sheet(stock_code, end_year, start_year)
        return self._standardize(raw_df, "balance_sheet")

    def get_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取利润表（执行字段映射）"""
        raw_df = self._provider.fetch_raw_income_statement(stock_code, end_year, start_year)
        return self._standardize(raw_df, "income_statement")

    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取现金流量表（执行字段映射）"""
        raw_df = self._provider.fetch_raw_cash_flow(stock_code, end_year, start_year)
        return self._standardize(raw_df, "cash_flow")
