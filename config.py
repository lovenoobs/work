from dataclasses import dataclass

@dataclass
class AppConfig:
    # 是否显示浏览器窗口（调试时建议 False 改成 True；本字段配合 UI 的“无头模式”勾选）
    headless: bool = False

    # IC交易网搜索 URL 模板（需要你根据实际网站改成正确的搜索入口）
    # 做法：手动搜索一次，把结果页URL贴过来，把关键词部分替换成 {pn}
    search_url_template: str = "https://www.ic.net.cn/search?keys={pn}"

    # 结果列表“行容器”选择器（需要按实际 DOM 调整）
    result_row_selector: str = "tr"

    # 行内：可点击 SSCP 图标选择器（你说 SSCP 可点击）
    sscp_clickable_selector: str = "a:has-text('SSCP'), span:has-text('SSCP'), img[alt*='SSCP']"

    # 行内：DC/批号所在的选择器（截图表头“批号”列）
    dc_cell_selector: str = "td:nth-child(4)"  # 需要按表格实际列位置调整

    # 行内：供应商名称选择器（截图左侧供应商列）
    vendor_cell_selector: str = "td:nth-child(1)"  # 需要调整

    # 行内：QQ按钮选择器（右侧QQ图标）
    qq_button_selector: str = "a:has(img), a:has-text('QQ')"  # 需要调整成更准确的

    # 弹窗“继续唤起QQ”按钮（你确认文案固定）
    continue_wakeup_selector: str = "text=继续唤起QQ"

    # 每个料号最多询价供应商数
    top_n: int = 10