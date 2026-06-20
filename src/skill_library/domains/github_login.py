"""GitHub 登录适配器 —— 直接执行或作为范例参考。"""


def run(username: str, password: str):
    """登录 GitHub。

    Args:
        username: GitHub 用户名或邮箱。
        password: GitHub 密码。

    流程:
        1. 导航到 GitHub 登录页
        2. 填写用户名
        3. 填写密码
        4. 点击登录按钮
        5. 等待跳转到首页

    注意:
        - GitHub 有两步验证，此脚本只处理第一步
        - 如果启用了 2FA，需要额外处理验证码
    """
    goto("https://github.com/login")
    fill("#login_field", username)    # 用户名输入框
    fill("#password", password)       # 密码输入框
    click("input[name='commit']")     # Sign in 按钮
    wait_for_navigation()
    log(f"GitHub 登录完成: {username}")


# 选择器备选方案:
# username_input: #login_field → input[name='login']
# password_input: #password → input[name='password']
# submit_button: input[name='commit'] → button[type='submit']
