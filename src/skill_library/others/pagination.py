"""通用分页翻页模板 —— 不绑定特定网站。"""


def run(next_button_selector: str, max_pages: int = 10, wait_seconds: float = 2.0):
    """通用分页翻页。

    Args:
        next_button_selector: "下一页"按钮选择器。
        max_pages: 最大翻页数。
        wait_seconds: 每次翻页后等待秒数。

    流程:
        1. 检查"下一页"按钮是否存在
        2. 点击按钮
        3. 等待页面加载
        4. 重复直到达到最大页数或按钮消失

    使用示例:
        # 翻 5 页，每页等待 3 秒
        pagination.run("a.next", max_pages=5, wait_seconds=3.0)
    """
    for page_num in range(1, max_pages + 1):
        log(f"正在处理第 {page_num} 页")

        # 检查下一页按钮是否存在
        result = click(next_button_selector)
        if not result.get("success"):
            log(f"第 {page_num} 页: 下一页按钮不存在或不可点击，停止翻页")
            break

        wait(wait_seconds)
        wait_for_navigation()
        log(f"已翻到第 {page_num + 1} 页")

    log("分页完成")
