# 如何实现通用表单填写

## 适用场景
需要填写任意网站的表单（注册、设置、提交信息等）。

## 模式
1. 导航到表单页
2. 逐个定位表单字段
3. 填写每个字段
4. 处理特殊字段（下拉框、复选框、单选框）
5. 点击提交按钮
6. 等待提交结果

## 字段类型处理

### 文本输入
```python
fill("#name", "张三")
fill("#email", "test@example.com")
fill("#phone", "13800138000")
```

### 下拉框
```python
# 方式一：直接选择
click("#country")           # 点击下拉框
click("text=中国")          # 点击选项

# 方式二：Playwright select
page.select_option("#country", "CN")
```

### 复选框 / 单选框
```python
click("#agree")             # 勾选复选框
click("input[value='male']") # 选择单选框
```

### 文件上传
```python
# 需要用 Playwright 原生 API
page.set_input_files("#avatar", "path/to/file.jpg")
```

## 常见陷阱
- 表单字段可能有**前端验证**，填写后需要触发 change 事件
- 有的字段需要**先点击激活**才能输入
- 提交按钮可能在**表单外部**（浮动按钮、底部固定）
- 提交后可能有**确认弹窗**需要处理

## 参考代码
→ 见 `interactions/form_fill.py`

## 使用方式
```python
# 使用通用模板
from skill_library.interactions.form_fill import run
run("https://example.com/register", {
    "#name": "张三",
    "#email": "test@example.com",
    "#password": "secure123",
}, submit_selector="#register-btn")

# 使用控件层
smart_fill_form("example", {
    "name": "张三",
    "email": "test@example.com",
})
```
