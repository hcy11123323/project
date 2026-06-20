# 如何实现 GitHub 登录

## 适用场景
需要登录 GitHub 进行仓库操作、代码查看等。

## 模式
1. 导航到 `https://github.com/login`
2. 填写用户名 (`#login_field`)
3. 填写密码 (`#password`)
4. 点击登录按钮 (`input[name='commit']`)
5. 等待跳转到首页

## 选择器
| 元素 | 主选择器 | 备选 |
|------|---------|------|
| 用户名 | `#login_field` | `input[name='login']` |
| 密码 | `#password` | `input[name='password']` |
| 登录按钮 | `input[name='commit']` | `button[type='submit']` |

## 常见问题
- **两步验证 (2FA)**: 启用 2FA 的账号需要额外处理验证码，此脚本不覆盖
- **CAPTCHA**: GitHub 可能在异常登录时弹出验证码
- **邮箱验证**: 首次登录新设备可能需要邮箱验证

## 参考代码
→ 见 `domains/github_login.py`

## 使用方式
```python
# 方式一：直接调用适配器
from skill_library.domains.github_login import run
run("myuser", "mypassword")

# 方式二：使用控件层
smart_login("github", "myuser", "mypassword")

# 方式三：手动组合
goto("https://github.com/login")
fill("#login_field", "myuser")
fill("#password", "mypassword")
click("input[name='commit']")
wait_for_navigation()
```
