"""端到端测试：动态 Calculator 完整流程"""
import tempfile
from pathlib import Path

import pytest

from value_investment.calculator_plugin import (
    load_calculator,
    registry,
    clear_registry,
    load_builtin_calculators,
)


@pytest.fixture(autouse=True)
def clean_registry():
    """每个测试前后清理 registry"""
    clear_registry()
    yield
    clear_registry()
    # 重新加载内置 calculators
    load_builtin_calculators()


class TestDynamicCalculatorE2E:
    """动态 Calculator 端到端测试"""

    def test_full_workflow(self):
        """完整工作流：生成脚本 -> 加载 -> 注册 -> 使用"""
        # Step 1: 模拟 skill 生成 calculator 脚本
        with tempfile.TemporaryDirectory() as tmpdir:
            calc_path = Path(tmpdir) / "calc_roic.py"
            calc_path.write_text(
                """
name = "roic"
required_fields = ["net_income", "total_equity"]

def calculate(results):
    income = results.get("net_income", {})
    equity = results.get("total_equity", {})
    return {y: income.get(y, 0) / equity.get(y, 1) for y in income}
"""
            )

            # Step 2: 加载
            calc_dict = load_calculator(str(calc_path))
            assert calc_dict["name"] == "roic"
            assert calc_dict["required_fields"] == {"net_income", "total_equity"}

            # Step 3: 注册
            
            registry.register_from_dict(calc_dict)

            # Step 4: 使用
            calculators = registry.get_all()
            roic = next((c for c in calculators if c.name == "roic"), None)
            assert roic is not None

            # 验证计算结果
            test_data = {
                "net_income": {"2023": 100},
                "total_equity": {"2023": 500},
            }
            result = roic.calculate(test_data)
            assert result["2023"] == pytest.approx(0.2)

    def test_override_builtin_with_dynamic(self):
        """测试动态 calculator 覆盖内置"""
        # Given: 创建覆盖 gross_profit 的动态 calculator
        with tempfile.TemporaryDirectory() as tmpdir:
            calc_path = Path(tmpdir) / "calc_gross_profit.py"
            calc_path.write_text(
                """
# 自定义的 gross_profit 计算（可能加了调整项）
required_fields = ["total_revenue", "operating_cost"]

def calculate(results):
    revenue = results["total_revenue"]
    cost = results["operating_cost"]
    # 这里加了一些调整逻辑
    return {y: revenue.get(y, 0) - cost.get(y, 0) * 0.99 for y in revenue}
"""
            )

            # When: 加载并注册
            calc_dict = load_calculator(str(calc_path))
            
            registry.register_from_dict(calc_dict)

            # Then: 获取 calculators 时动态的覆盖内置的
            calculators = registry.get_all()
            gross_profit = next(c for c in calculators if c.name == "gross_profit")

            # 验证使用的是动态的（不是内置的）
            assert gross_profit._source == str(calc_path)

            # 验证计算结果使用了调整逻辑
            test_data = {
                "total_revenue": {"2023": 1000},
                "operating_cost": {"2023": 600},
            }
            result = gross_profit.calculate(test_data)
            # 0.99 * 600 = 594
            assert result["2023"] == pytest.approx(406)

    def test_name_inference_from_filename(self):
        """测试从文件名推断 name"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 模拟 calc_custom_metric.py
            calc_path = Path(tmpdir) / "calc_custom_metric.py"
            calc_path.write_text(
                """
required_fields = []

def calculate(results):
    return {"2023": 42}
"""
            )

            # When
            calc_dict = load_calculator(str(calc_path))

            # Then
            assert calc_dict["name"] == "custom_metric"

    def test_multiple_calculators_same_dir(self):
        """测试加载同一目录下的多个 calculators"""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "calc_roic.py").write_text(
                """
name = "roic"
required_fields = []
def calculate(results): return {"2023": 0.2}
"""
            )
            (Path(tmpdir) / "calc_pe.py").write_text(
                """
name = "pe"
required_fields = []
def calculate(results): return {"2023": 15}
"""
            )

            # When
            
            for py_file in Path(tmpdir).glob("calc_*.py"):
                calc_dict = load_calculator(str(py_file))
                registry.register_from_dict(calc_dict)

            # Then
            calculators = registry.get_all()
            names = {c.name for c in calculators}
            assert "roic" in names
            assert "pe" in names
