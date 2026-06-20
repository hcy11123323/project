"""百度搜索适配器 —— 直接执行或作为范例参考。"""


def run(keyword: str):
    """在百度搜索关键词。

    Args:
        keyword: 搜索关键词。

    流程:
        1. 导航到百度首页
        2. 在搜索框输入关键词
        3. 点击搜索按钮
        4. 等待搜索结果加载
    """
    goto("https://www.baidu.com")
    fill("#kw", keyword)           # L1 选择器: #kw → input[name='wd'] → .s_ipt
    click("#su")                   # L1 选择器: #su → input[type='submit'] → .btn-search
    wait_for_navigation()
    log(f"百度搜索完成: {keyword}")


# 选择器备选方案（注释即文档）:
# search_input: #kw → input[name='wd'] → .s_ipt
# search_button: #su → input[type='submit'] → .btn-search
