# 如何实现通用搜索

## 适用场景
需要在任意网站实现搜索功能，没有现成的站点适配器。

## 模式
1. 导航到搜索页
2. 定位搜索输入框
3. 输入关键词
4. 点击搜索按钮（或按 Enter）
5. 等待搜索结果加载

## 选择器查找策略
1. **常见 ID**: `#search`, `#query`, `#q`, `#keyword`
2. **Name 选择器**: `input[name='q']`, `input[name='search']`
3. **Role 选择器**: `role=searchbox`
4. **Placeholder**: `input[placeholder*='搜索']`, `input[placeholder*='Search']`
5. **视觉识别**: 用 `analyze_page()` 让 LLM 识别

## 常见陷阱
- 有的网站搜索框是 `<textarea>` 而非 `<input>`
- 有的网站按 Enter 提交，没有搜索按钮
- 有的网站搜索是 AJAX 异步加载，不跳转页面
- 有的网站搜索框在页面顶部固定，需要先滚动到可见区域

## 参考代码
→ 见 `interactions/search_flow.py`

## 使用方式
```python
# 使用通用模板
from skill_library.interactions.search_flow import run
run("https://example.com", "#search", "#search-btn", "Python")

# 使用控件层
smart_search("example", "Python",
             input_field="search_input",
             submit_field="search_button")

# 手动组合
goto("https://example.com")
fill("#search", "Python")
click("#search-btn")
wait_for_navigation()
```
