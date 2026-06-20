# 如何实现百度搜索

## 适用场景
需要在百度搜索关键词并获取搜索结果。

## 模式
1. 导航到 `https://www.baidu.com`
2. 在搜索框 (`#kw`) 输入关键词
3. 点击搜索按钮 (`#su`)
4. 等待搜索结果页加载

## 选择器
| 元素 | 主选择器 | 备选 |
|------|---------|------|
| 搜索框 | `#kw` | `input[name='wd']`, `.s_ipt` |
| 搜索按钮 | `#su` | `input[type='submit']`, `.btn-search` |

## 常见问题
- 百度有时会弹出验证码，需要视觉识别辅助
- 搜索结果页的 URL 会变化为 `www.baidu.com/s?wd=...`
- 百度首页加载较慢，建议等待时间设置长一些

## 参考代码
→ 见 `domains/baidu_search.py`

## 使用方式
```python
# 方式一：直接调用适配器
from skill_library.domains.baidu_search import run
run("Python 教程")

# 方式二：使用控件层
smart_search("baidu", "Python 教程")

# 方式三：手动组合
goto("https://www.baidu.com")
fill("#kw", "Python 教程")
click("#su")
wait_for_navigation()
```
