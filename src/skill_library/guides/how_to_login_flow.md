# 如何实现通用登录

## 适用场景
需要在任意网站实现登录功能，没有现成的站点适配器。

## 模式
1. 导航到登录页
2. 定位用户名输入框
3. 填写用户名
4. 定位密码输入框
5. 填写密码
6. 定位登录按钮
7. 点击登录
8. 等待页面跳转确认登录成功

## 选择器查找策略
按优先级尝试：
1. **ID 选择器**: `#login`, `#username`, `#password` — 最稳定
2. **Name 选择器**: `input[name='username']`, `input[name='password']`
3. **Type 选择器**: `input[type='password']` — 密码框通用
4. **文本选择器**: `text=登录`, `text=Sign in` — 按钮通用
5. **视觉识别**: 用 `analyze_page()` 让 LLM 识别

## 常见陷阱
- 有的网站用 **email** 而非 username
- 有的网站用 **手机号** 登录
- 登录后可能跳转到不同页面（首页、仪表盘、原页面）
- 有的网站有"记住我"复选框，需要额外处理
- 有的网站登录按钮是 `<a>` 而非 `<button>`

## 参考代码
→ 见 `others/login_flow.py`

## 使用方式
```python
# 使用控件层（推荐）
smart_login("example", "admin", "1234",
            username_field="email",
            password_field="password",
            submit_field="login_btn")

# 使用通用模板
from skill_library.others.login_flow import run
run("https://example.com/login",
    "#email", "#password", "#login-btn",
    "admin", "1234")

# 手动组合
goto("https://example.com/login")
fill("#email", "admin")
fill("#password", "1234")
click("#login-btn")
wait_for_navigation()
```
