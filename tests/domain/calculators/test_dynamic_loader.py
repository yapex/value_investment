"""Tests for DynamicCalculatorLoader"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from value_investment.calculator_plugin import (
    CalculatorValidationError,
    load_calculator,
    load_calculators_from_dir,
)


class TestLoadCalculator:
    """测试 load_calculator 函数"""

    def test_load_valid_calculator(self):
        """测试加载有效的 calculator 脚本"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("""
name = "roic"
required_fields = ["net_income", "total_equity"]

def calculate(results):
    income = results["net_income"]
    equity = results["total_equity"]
    return {y: income[y] / equity[y] for y in income}
""")
            path = f.name

        try:
            # When
            result = load_calculator(path)

            # Then
            assert result["name"] == "roic"
            assert result["required_fields"] == {"net_income", "total_equity"}
            assert callable(result["calculate"])
            assert result["_source"] == path
        finally:
            Path(path).unlink()

    def test_infer_name_from_filename(self):
        """测试 name 从文件名推断"""
        # Given: 创建固定文件名的测试文件
        import tempfile
        import os

        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, "calc_roic.py")

        with open(path, "w") as f:
            f.write("""
required_fields = ["net_income"]

def calculate(results):
    return {}
""")

        try:
            # When
            result = load_calculator(path)

            # Then: 推断出的 name 应该是 roic（从 calc_roic.py）
            assert result["name"] == "roic"
        finally:
            Path(path).unlink()
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_explicit_name_override_filename(self):
        """测试显式 name 覆盖文件名推断"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="calc_my_roic"
        ) as f:
            f.write("""
name = "roic"  # 覆盖默认的 my_roic
required_fields = ["net_income"]

def calculate(results):
    return {}
""")
            path = f.name

        try:
            # When
            result = load_calculator(path)

            # Then
            assert result["name"] == "roic"
        finally:
            Path(path).unlink()

    def test_missing_required_fields_raises(self):
        """测试缺少 required_fields 报错"""
        # Given: 使用 calc_ 前缀的文件名
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="calc_"
        ) as f:
            f.write("""
def calculate(results):
    return {}
""")
            path = f.name

        try:
            # When/Then
            with pytest.raises(CalculatorValidationError) as exc_info:
                load_calculator(path)
            assert "required_fields" in str(exc_info.value)
        finally:
            Path(path).unlink()

    def test_missing_calculate_raises(self):
        """测试缺少 calculate 函数报错"""
        # Given: 使用 calc_ 前缀的文件名
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="calc_"
        ) as f:
            f.write("""
required_fields = ["net_income"]
""")
            path = f.name

        try:
            # When/Then
            with pytest.raises(CalculatorValidationError) as exc_info:
                load_calculator(path)
            assert "calculate" in str(exc_info.value)
        finally:
            Path(path).unlink()


class TestLoadCalculatorsFromDir:
    """测试 load_calculators_from_dir 函数"""

    def test_load_only_calc_prefix_files(self):
        """测试只加载 calc_*.py 文件"""
        # Given
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 calc_roic.py
            (Path(tmpdir) / "calc_roic.py").write_text(
                """
name = "roic"
required_fields = []

def calculate(results):
    return {}
"""
            )
            # 创建 calc_pe.py
            (Path(tmpdir) / "calc_pe.py").write_text(
                """
name = "pe"
required_fields = []

def calculate(results):
    return {}
"""
            )
            # 创建 other.py（不应被加载）
            (Path(tmpdir) / "other.py").write_text(
                """
name = "other"
required_fields = []

def calculate(results):
    return {}
"""
            )

            # When
            calculators = load_calculators_from_dir(tmpdir)

            # Then
            assert len(calculators) == 2
            names = {c["name"] for c in calculators}
            assert names == {"roic", "pe"}

    def test_invalid_file_prints_warning(self):
        """测试无效文件打印警告但不中断"""
        # Given
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "calc_valid.py").write_text(
                """
name = "valid"
required_fields = []

def calculate(results):
    return {}
"""
            )
            (Path(tmpdir) / "calc_invalid.py").write_text(
                """
# 缺少 required_fields 和 calculate
"""
            )

            # When
            calculators = load_calculators_from_dir(tmpdir)

            # Then
            assert len(calculators) == 1
            assert calculators[0]["name"] == "valid"
