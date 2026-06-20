"""通用搜索流程模板 —— 不绑定特定网站。"""


def run(url: str, input_selector: str, submit_selector: str, keyword: str):
    """通用搜索流程。

    Args:
        url: 搜索页 URL。
        input_selector: 搜索框选择器。
        submit_selector: 搜索按钮选择器。
        keyword: 搜索关键词。

    流程:
        1. 导航到搜索页
        2. 在搜索框输入关键词
        3. 点击搜索按钮
        4. 等待结果加载
    """
    goto(url)
    fill(input_selector, keyword)
    click(submit_selector)
    wait_for_navigation()
    log(f"搜索完成: {keyword}")
