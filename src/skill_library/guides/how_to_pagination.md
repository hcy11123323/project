# 如何实现通用分页翻页

## 适用场景
需要遍历多页内容（搜索结果、列表、商品等）。

## 模式
1. 获取当前页内容
2. 点击"下一页"按钮
3. 等待页面加载
4. 重复直到最后一页

## 选择器查找策略
1. **文本选择器**: `text=下一页`, `text=Next`, `text=»`
2. **Class 选择器**: `.next`, `.pagination .next`, `.page-next`
3. **Aria 选择器**: `aria-label="Next page"`
4. **视觉识别**: 用 `analyze_page()` 让 LLM 识别分页控件

## 终止条件
- "下一页"按钮不存在或不可点击
- 达到最大页数限制
- 页面内容重复（已经到最后一页）

## 常见陷阱
- 有的网站分页是**无限滚动**，不是传统翻页
- 有的网站分页是 **AJAX** 加载，URL 不变
- 有的网站"下一页"按钮在**最后一页时消失**
- 翻页太快可能触发**反爬机制**

## 参考代码
→ 见 `others/pagination.py`

## 使用方式
```python
# 使用通用模板
from skill_library.others.pagination import run
run("a.next", max_pages=10, wait_seconds=2.0)

# 手动组合
for i in range(10):
    result = click("a.next")
    if not result.get("success"):
        break
    wait(2.0)
    wait_for_navigation()
    log(f"第 {i+2} 页")
```
