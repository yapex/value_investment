# LSP 配置指南

本文档说明如何配置语言服务器 (Pylance/Pyright) 使用 uv 虚拟环境。

## 自动配置

项目已包含以下配置文件：

- `.vscode/settings.json` - VS Code 设置
- `pyrightconfig.json` - Pyright 类型检查配置

## VS Code 配置

### 1. 安装扩展

确保安装以下扩展：
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Ruff** (charliermarsh.ruff) - 可选，用于代码格式化

### 2. 选择解释器

1. 打开命令面板：`Cmd+Shift+P` (Mac) 或 `Ctrl+Shift+P` (Windows/Linux)
2. 输入：`Python: Select Interpreter`
3. 选择：`.venv/bin/python` 或显示为 `Python 3.14.x ('.venv': venv)`

### 3. 验证配置

打开任意 Python 文件，检查底部状态栏是否显示：
```
Python 3.14.x ('.venv': venv)
```

## Pyright 配置

`pyrightconfig.json` 已配置：

```json
{
    "venvPath": ".",
    "venv": ".venv",
    "extraPaths": ["src"],
    "typeCheckingMode": "basic"
}
```

这会告诉 Pyright：
- 使用 `.venv` 虚拟环境
- 将 `src` 添加到导入路径
- 使用基础类型检查模式

## 常见问题

### 问题：仍然显示 "Import could not be resolved"

**解决方案 1**：重新加载窗口
1. `Cmd+Shift+P` → `Developer: Reload Window`

**解决方案 2**：手动指定 Python 路径
在 `.vscode/settings.json` 中添加：
```json
{
    "python.analysis.extraPaths": ["src"],
    "python.autoComplete.extraPaths": ["src"]
}
```

**解决方案 3**：重建虚拟环境
```bash
uv sync --reinstall
```

### 问题：pytest 导入无法解析

这是正常的，因为 pytest 只在测试运行时加载。可以忽略这些警告，或在 `pyrightconfig.json` 中添加：

```json
{
    "ignore": ["tests/**"]
}
```

### 问题：运行时导入无法解析

对于动态导入（如 `from value_investment.api import IndicatorNotFoundError`），
Pyright 可能无法静态分析。这是误报，代码实际运行正常。

可以在代码中添加类型忽略注释：
```python
from value_investment.api import IndicatorNotFoundError  # type: ignore[import-not-found]
```

## 其他编辑器

### Neovim + pyright

在 `lspconfig` 配置中：

```lua
require('lspconfig').pyright.setup({
    settings = {
        python = {
            analysis = {
                extraPaths = {"src"},
            },
        },
    },
})
```

### PyCharm

1. `Preferences` → `Project` → `Python Interpreter`
2. 点击齿轮图标 → `Add`
3. 选择 `Existing Environment`
4. 选择 `.venv/bin/python`

## 验证配置

运行以下命令验证虚拟环境配置：

```bash
# 检查 Python 路径
which python  # 应该指向 .venv/bin/python

# 检查导入
uv run python -c "from value_investment.api import ValueInvestment; print('OK')"

# 运行测试
uv run pytest tests/test_business_exceptions.py -v
```

## 参考链接

- [Pyright 配置文档](https://github.com/microsoft/pyright/blob/main/docs/configuration.md)
- [VS Code Python 配置](https://code.visualstudio.com/docs/python/environments)
- [uv 文档](https://docs.astral.sh/uv/)
