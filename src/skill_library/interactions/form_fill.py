"""通用表单填写模板 —— 不绑定特定网站。"""


def run(url: str, fields: dict, submit_selector: str = None):
    """通用表单填写。

    Args:
        url: 表单页 URL（为 None 时不导航，假设已在表单页）。
        fields: {选择器: 值} 字典，如 {"#name": "张三", "#email": "test@example.com"}。
        submit_selector: 提交按钮选择器（为 None 时不提交）。

    流程:
        1. 导航到表单页（如果 url 不为 None）
        2. 逐个填写表单字段
        3. 点击提交按钮（如果提供了选择器）
    """
    if url:
        goto(url)

    for selector, value in fields.items():
        fill(selector, value)
        log(f"已填写: {selector} = {value}")

    if submit_selector:
        click(submit_selector)
        wait_for_navigation()
        log("表单已提交")
