# IC交易网询价助手（本机版）

## 功能
- 导入BOM（Excel列：型号、数量、年份）
- 自动打开搜索页面，按年份规则筛选供应商：优先SSCP，不足10家再补非SSCP（从上到下）
- 点击QQ图标 -> 自动点“继续唤起QQ”
- 生成询价话术一键复制
- 粘贴报价文本 -> 解析 **RMB未税 / RMB含税 / USD**
- 导出Excel（报价明细）

## 环境
- Windows 11
- Python 3.11+
- Chrome（Playwright 使用 Chromium，行为接近 Chrome）

## 安装运行
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
python main.py
```

## 重要：需要你配置选择器
由于我无法直接访问 IC交易网的 DOM，本项目把关键元素定位写在 `config.py` 中。

你需要先：
1) 用浏览器手动搜索一个型号，复制搜索结果页 URL
2) 把 `config.py` 的 `search_url_template` 调整为正确的 URL 模板（把关键词位置换成 `{pn}`）
3) 若点击不到 SSCP / QQ / 批号DC，请按 F12 在页面里复制元素 outerHTML 或 selector，微调：
- `result_row_selector`
- `vendor_cell_selector`
- `dc_cell_selector`
- `sscp_clickable_selector`
- `qq_button_selector`

调好后就能稳定跑。