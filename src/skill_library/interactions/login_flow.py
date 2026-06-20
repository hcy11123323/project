"""通用登录流程模板 —— 不绑定特定网站。"""


def run(url: str, username_selector: str, password_selector: str,
        submit_selector: str, username: str, password: str):
    """通用登录流程。

    Args:
        url: 登录页 URL。
        username_selector: 用户名输入框选择器。
        password_selector: 密码输入框选择器。
        submit_selector: 提交按钮选择器。
        username: 用户名。
        password: 密码。

    流程:
        1. 导航到登录页
        2. 填写用户名
        3. 填写密码
        4. 点击提交
        5. 等待页面跳转
    """
    goto(url)
    fill(username_selector, username)
    fill(password_selector, password)
    click(submit_selector)
    wait_for_navigation()
    log(f"登录完成: {get_url()}")
