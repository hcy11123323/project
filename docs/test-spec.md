# 测试规范 — 52 个任务的预期结果与验证规则

每个任务定义：任务描述 → 执行方式 → 预期结果 → 验证规则 → 判定标准

---

## 验证机制

```
任务执行后，检查以下维度：
1. URL 匹配：最终 URL 是否包含预期域名/路径
2. 页面内容：页面文本是否包含预期关键词
3. 结构化数据：提取的数据是否符合预期格式
4. 执行状态：脚本是否成功执行

判定逻辑：
- 全部通过 → PASS
- 任一失败 → FAIL
- 部分通过 → PARTIAL（记录详情）
```

---

## 1. 百度搜索

### 任务 1.1：搜索关键词

| 属性 | 值 |
|------|-----|
| 任务 | 帮我在百度搜索 Python 教程 |
| 执行 | `run_task("帮我在百度搜索 Python 教程")` |
| 预期 URL | `baidu.com/s` |
| 预期内容 | 页面包含 "Python" 和 "教程" |
| 验证规则 | `url.contains("baidu.com") && page.contains("Python")` |
| 判定 | URL 包含 baidu.com 且页面有搜索结果 |

### 任务 1.2：搜索并提取结果标题

| 属性 | 值 |
|------|-----|
| 任务 | 在百度搜索"人工智能"，返回前5条搜索结果的标题 |
| 执行 | `run_task("在百度搜索人工智能，返回前5条搜索结果的标题")` |
| 预期 URL | `baidu.com/s` |
| 预期结果 | 返回 5 个标题文本，每个标题 > 5 个字符 |
| 验证规则 | `result.output.contains_at_least(5, "title_lines")` |
| 判定 | 输出包含至少 5 行有意义的标题 |

### 任务 1.3：搜索并截图

| 属性 | 值 |
|------|-----|
| 任务 | 在百度搜索"机器学习"，截图保存结果页面 |
| 执行 | `run_task("在百度搜索机器学习，截图保存结果页面")` |
| 预期 URL | `baidu.com/s` |
| 预期结果 | 截图文件已保存 |
| 验证规则 | `result.screenshots.length > 0` |
| 判定 | 有截图文件生成 |

---

## 2. 必应中国

### 任务 2.1：搜索关键词

| 属性 | 值 |
|------|-----|
| 任务 | 在必应搜索 Python 教程 |
| 执行 | `run_task("在必应搜索 Python 教程")` |
| 预期 URL | `cn.bing.com` 或 `bing.com` |
| 预期内容 | 页面包含 "Python" |
| 验证规则 | `url.contains("bing.com") && page.contains("Python")` |
| 判定 | URL 包含 bing.com |

### 任务 2.2：搜索并提取摘要

| 属性 | 值 |
|------|-----|
| 任务 | 在必应搜索"深度学习"，返回前3条结果的标题和摘要 |
| 执行 | `run_task("在必应搜索深度学习，返回前3条结果的标题和摘要")` |
| 预期 URL | `bing.com` |
| 预期结果 | 返回至少 3 行文本，包含标题和摘要 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含至少 3 行有意义的内容 |

---

## 3. 搜狗搜索

### 任务 3.1：搜索关键词

| 属性 | 值 |
|------|-----|
| 任务 | 在搜狗搜索 Python 教程 |
| 执行 | `run_task("在搜狗搜索 Python 教程")` |
| 预期 URL | `sogou.com` |
| 预期内容 | 页面包含 "Python" |
| 验证规则 | `url.contains("sogou.com")` |
| 判定 | URL 包含 sogou.com |

### 任务 3.2：搜索微信文章

| 属性 | 值 |
|------|-----|
| 任务 | 在搜狗搜索"AI Agent"，专门搜索微信文章 |
| 执行 | `run_task("在搜狗搜索AI Agent，专门搜索微信文章")` |
| 预期 URL | `sogou.com` 且包含 `weixin` 或 `type=2` |
| 预期内容 | 页面包含 "AI" 或 "Agent" |
| 验证规则 | `url.contains("sogou.com") && url.contains("weixin")` |
| 判定 | URL 包含搜狗和微信标识 |

---

## 4. 360 搜索

### 任务 4.1：搜索关键词

| 属性 | 值 |
|------|-----|
| 任务 | 在360搜索 Python 教程 |
| 执行 | `run_task("在360搜索 Python 教程")` |
| 预期 URL | `so.com` |
| 预期内容 | 页面包含 "Python" |
| 验证规则 | `url.contains("so.com")` |
| 判定 | URL 包含 so.com |

### 任务 4.2：多引擎对比

| 属性 | 值 |
|------|-----|
| 任务 | 分别在百度、必应、360搜索"Python教程"，返回三个搜索引擎的第一条结果标题 |
| 执行 | `run_task("分别在百度、必应、360搜索Python教程，返回三个搜索引擎的第一条结果标题")` |
| 预期结果 | 输出包含 3 个标题，分别来自不同搜索引擎 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含至少 3 行内容 |

---

## 5. 淘宝

### 任务 5.1：搜索商品

| 属性 | 值 |
|------|-----|
| 任务 | 在淘宝搜索"机械键盘"，返回前5个商品的名称和价格 |
| 执行 | `run_task("在淘宝搜索机械键盘，返回前5个商品的名称和价格")` |
| 预期 URL | `taobao.com` |
| 预期结果 | 返回至少 5 行商品信息，包含名称和价格 |
| 验证规则 | `result.output.lines.length >= 5 && output.contains("¥")` |
| 判定 | 输出包含商品信息和价格符号 |

### 任务 5.2：搜索并按价格排序

| 属性 | 值 |
|------|-----|
| 任务 | 在淘宝搜索"蓝牙耳机"，按价格从低到高排序，返回前3个结果 |
| 执行 | `run_task("在淘宝搜索蓝牙耳机，按价格从低到高排序，返回前3个结果")` |
| 预期 URL | `taobao.com` |
| 预期结果 | 返回 3 个商品，价格递增 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含至少 3 个商品信息 |

### 任务 5.3：搜索特定品牌

| 属性 | 值 |
|------|-----|
| 任务 | 在淘宝搜索"罗技鼠标"，返回所有搜索结果 |
| 执行 | `run_task("在淘宝搜索罗技鼠标，返回所有搜索结果")` |
| 预期 URL | `taobao.com` |
| 预期结果 | 返回商品列表 |
| 验证规则 | `result.output.length > 100` |
| 判定 | 输出包含有意义的商品信息 |

---

## 6. 京东

### 任务 6.1：搜索商品

| 属性 | 值 |
|------|-----|
| 任务 | 在京东搜索"机械键盘"，返回前5个商品的名称和价格 |
| 执行 | `run_task("在京东搜索机械键盘，返回前5个商品的名称和价格")` |
| 预期 URL | `jd.com` |
| 预期结果 | 返回至少 5 行商品信息 |
| 验证规则 | `url.contains("jd.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含 jd.com 且输出包含商品信息 |

### 任务 6.2：搜索并提取评价

| 属性 | 值 |
|------|-----|
| 任务 | 在京东搜索"iPhone 15"，进入第一个商品页面，提取商品评价数量和评分 |
| 执行 | `run_task("在京东搜索iPhone 15，进入第一个商品页面，提取商品评价数量和评分")` |
| 预期 URL | `jd.com` |
| 预期结果 | 输出包含评价数量和评分信息 |
| 验证规则 | `output.contains("评价") \|\| output.contains("好评")` |
| 判定 | 输出包含评价相关信息 |

### 任务 6.3：多平台价格对比

| 属性 | 值 |
|------|-----|
| 任务 | 在京东和淘宝分别搜索"蓝牙耳机"，对比两边的价格 |
| 执行 | `run_task("在京东和淘宝分别搜索蓝牙耳机，对比两边的价格")` |
| 预期结果 | 输出包含两个平台的价格信息 |
| 验证规则 | `output.contains("京东") && output.contains("淘宝")` |
| 判定 | 输出包含两个平台的价格对比 |

---

## 7. 拼多多

### 任务 7.1：搜索商品

| 属性 | 值 |
|------|-----|
| 任务 | 在拼多多搜索"手机壳"，返回前5个商品的名称和价格 |
| 执行 | `run_task("在拼多多搜索手机壳，返回前5个商品的名称和价格")` |
| 预期 URL | `pinduoduo.com` 或 `yangkeduo.com` |
| 预期结果 | 返回至少 5 行商品信息 |
| 验证规则 | `result.output.lines.length >= 5` |
| 判定 | 输出包含商品信息 |

### 任务 7.2：搜索低价商品

| 属性 | 值 |
|------|-----|
| 任务 | 在拼多多搜索"数据线"，找到最便宜的3个商品 |
| 执行 | `run_task("在拼多多搜索数据线，找到最便宜的3个商品")` |
| 预期 URL | `pinduoduo.com` |
| 预期结果 | 返回 3 个商品，价格较低 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含至少 3 个商品信息 |

---

## 8. 当当网

### 任务 8.1：搜索书籍

| 属性 | 值 |
|------|-----|
| 任务 | 在当当网搜索"Python编程"，返回前5本书的名称和价格 |
| 执行 | `run_task("在当当网搜索Python编程，返回前5本书的名称和价格")` |
| 预期 URL | `dangdang.com` |
| 预期结果 | 返回至少 5 行书籍信息 |
| 验证规则 | `url.contains("dangdang.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含 dangdang.com 且输出包含书籍信息 |

### 任务 8.2：搜索特定作者

| 属性 | 值 |
|------|-----|
| 任务 | 在当当网搜索"刘慈欣"，返回所有相关书籍 |
| 执行 | `run_task("在当当网搜索刘慈欣，返回所有相关书籍")` |
| 预期 URL | `dangdang.com` |
| 预期结果 | 返回书籍列表，包含 "刘慈欣" |
| 验证规则 | `output.contains("刘慈欣")` |
| 判定 | 输出包含作者名 |

### 任务 8.3：搜索并提取评分

| 属性 | 值 |
|------|-----|
| 任务 | 在当当网搜索"三体"，返回书籍的评分和评价数量 |
| 执行 | `run_task("在当当网搜索三体，返回书籍的评分和评价数量")` |
| 预期 URL | `dangdang.com` |
| 预期结果 | 输出包含评分信息 |
| 验证规则 | `output.contains("三体") \|\| output.contains("评分")` |
| 判定 | 输出包含书籍名称或评分信息 |

---

## 9. 微博

### 任务 9.1：查看热搜

| 属性 | 值 |
|------|-----|
| 任务 | 打开微博热搜榜，返回前10条热搜话题 |
| 执行 | `run_task("打开微博热搜榜，返回前10条热搜话题")` |
| 预期 URL | `weibo.com` 或 `s.weibo.com` |
| 预期结果 | 返回至少 10 行热搜话题 |
| 验证规则 | `url.contains("weibo.com") && result.output.lines.length >= 10` |
| 判定 | URL 包含 weibo.com 且输出包含热搜列表 |

### 任务 9.2：搜索话题

| 属性 | 值 |
|------|-----|
| 任务 | 在微博搜索"人工智能"，返回前5条相关微博的标题 |
| 执行 | `run_task("在微博搜索人工智能，返回前5条相关微博的标题")` |
| 预期 URL | `weibo.com` |
| 预期结果 | 返回至少 5 行微博内容 |
| 验证规则 | `result.output.lines.length >= 5` |
| 判定 | 输出包含至少 5 行内容 |

### 任务 9.3：搜索用户

| 属性 | 值 |
|------|-----|
| 任务 | 在微博搜索"人民日报"，返回该用户的主页链接 |
| 执行 | `run_task("在微博搜索人民日报，返回该用户的主页链接")` |
| 预期 URL | `weibo.com` |
| 预期结果 | 输出包含用户主页链接 |
| 验证规则 | `output.contains("weibo.com") && output.contains("人民日报")` |
| 判定 | 输出包含微博链接和用户名 |

---

## 10. 知乎

### 任务 10.1：搜索问题

| 属性 | 值 |
|------|-----|
| 任务 | 在知乎搜索"Python怎么学"，返回前3个问题的标题 |
| 执行 | `run_task("在知乎搜索Python怎么学，返回前3个问题的标题")` |
| 预期 URL | `zhihu.com` |
| 预期结果 | 返回至少 3 行问题标题 |
| 验证规则 | `url.contains("zhihu.com") && result.output.lines.length >= 3` |
| 判定 | URL 包含 zhihu.com 且输出包含问题标题 |

### 任务 10.2：搜索并提取回答

| 属性 | 值 |
|------|-----|
| 任务 | 在知乎搜索"人工智能"，进入第一个问题，提取最高赞回答的前200字 |
| 执行 | `run_task("在知乎搜索人工智能，进入第一个问题，提取最高赞回答的前200字")` |
| 预期 URL | `zhihu.com` |
| 预期结果 | 输出包含回答内容，长度 > 50 字 |
| 验证规则 | `output.length > 50` |
| 判定 | 输出包含有意义的回答内容 |

### 任务 10.3：搜索特定话题

| 属性 | 值 |
|------|-----|
| 任务 | 在知乎搜索"机器学习入门"，返回相关问题和回答数量 |
| 执行 | `run_task("在知乎搜索机器学习入门，返回相关问题和回答数量")` |
| 预期 URL | `zhihu.com` |
| 预期结果 | 输出包含问题列表 |
| 验证规则 | `output.contains("机器学习")` |
| 判定 | 输出包含搜索关键词 |

---

## 11. 豆瓣

### 任务 11.1：搜索电影

| 属性 | 值 |
|------|-----|
| 任务 | 在豆瓣搜索"肖申克的救赎"，返回电影的评分和评价人数 |
| 执行 | `run_task("在豆瓣搜索肖申克的救赎，返回电影的评分和评价人数")` |
| 预期 URL | `douban.com` |
| 预期结果 | 输出包含评分信息 |
| 验证规则 | `output.contains("肖申克") \|\| output.contains("评分")` |
| 判定 | 输出包含电影名或评分 |

### 任务 11.2：搜索书籍

| 属性 | 值 |
|------|-----|
| 任务 | 在豆瓣搜索"三体"，返回书籍的评分和简介 |
| 执行 | `run_task("在豆瓣搜索三体，返回书籍的评分和简介")` |
| 预期 URL | `douban.com` |
| 预期结果 | 输出包含书籍信息 |
| 验证规则 | `output.contains("三体")` |
| 判定 | 输出包含书名 |

### 任务 11.3：搜索并提取影评

| 属性 | 值 |
|------|-----|
| 任务 | 在豆瓣搜索"流浪地球"，返回前3条热评的作者和内容摘要 |
| 执行 | `run_task("在豆瓣搜索流浪地球，返回前3条热评的作者和内容摘要")` |
| 预期 URL | `douban.com` |
| 预期结果 | 返回至少 3 行评论内容 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含评论内容 |

---

## 12. B站

### 任务 12.1：搜索视频

| 属性 | 值 |
|------|-----|
| 任务 | 在B站搜索"Python教程"，返回前5个视频的标题和播放量 |
| 执行 | `run_task("在B站搜索Python教程，返回前5个视频的标题和播放量")` |
| 预期 URL | `bilibili.com` |
| 预期结果 | 返回至少 5 行视频信息 |
| 验证规则 | `url.contains("bilibili.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含 bilibili.com 且输出包含视频信息 |

### 任务 12.2：搜索并提取UP主信息

| 属性 | 值 |
|------|-----|
| 任务 | 在B站搜索"何同学"，返回该UP主的粉丝数和代表作 |
| 执行 | `run_task("在B站搜索何同学，返回该UP主的粉丝数和代表作")` |
| 预期 URL | `bilibili.com` |
| 预期结果 | 输出包含UP主信息 |
| 验证规则 | `output.contains("何同学") \|\| output.contains("粉丝")` |
| 判定 | 输出包含UP主名或粉丝信息 |

### 任务 12.3：搜索特定分区

| 属性 | 值 |
|------|-----|
| 任务 | 在B站搜索"机器学习"，只看知识区的结果，返回前3个视频 |
| 执行 | `run_task("在B站搜索机器学习，只看知识区的结果，返回前3个视频")` |
| 预期 URL | `bilibili.com` |
| 预期结果 | 返回至少 3 行视频信息 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含至少 3 个视频信息 |

---

## 13. 今日头条

### 任务 13.1：搜索新闻

| 属性 | 值 |
|------|-----|
| 任务 | 在今日头条搜索"人工智能"，返回前5条新闻的标题和来源 |
| 执行 | `run_task("在今日头条搜索人工智能，返回前5条新闻的标题和来源")` |
| 预期 URL | `toutiao.com` |
| 预期结果 | 返回至少 5 行新闻标题 |
| 验证规则 | `url.contains("toutiao.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含 toutiao.com 且输出包含新闻标题 |

### 任务 13.2：搜索热点

| 属性 | 值 |
|------|-----|
| 任务 | 打开今日头条，返回当前的热点新闻前10条 |
| 执行 | `run_task("打开今日头条，返回当前的热点新闻前10条")` |
| 预期 URL | `toutiao.com` |
| 预期结果 | 返回至少 10 行热点新闻 |
| 验证规则 | `result.output.lines.length >= 10` |
| 判定 | 输出包含至少 10 条新闻 |

---

## 14. CSDN

### 任务 14.1：搜索技术文章

| 属性 | 值 |
|------|-----|
| 任务 | 在CSDN搜索"Python爬虫"，返回前5篇文章的标题和作者 |
| 执行 | `run_task("在CSDN搜索Python爬虫，返回前5篇文章的标题和作者")` |
| 预期 URL | `csdn.net` |
| 预期结果 | 返回至少 5 行文章信息 |
| 验证规则 | `url.contains("csdn.net") && result.output.lines.length >= 5` |
| 判定 | URL 包含 csdn.net 且输出包含文章信息 |

### 任务 14.2：搜索并提取代码

| 属性 | 值 |
|------|-----|
| 任务 | 在CSDN搜索"Python requests用法"，进入第一篇文章，提取代码示例 |
| 执行 | `run_task("在CSDN搜索Python requests用法，进入第一篇文章，提取代码示例")` |
| 预期 URL | `csdn.net` |
| 预期结果 | 输出包含代码片段 |
| 验证规则 | `output.contains("import") \|\| output.contains("def ") \|\| output.contains("requests")` |
| 判定 | 输出包含 Python 代码特征 |

### 任务 14.3：搜索特定标签

| 属性 | 值 |
|------|-----|
| 任务 | 在CSDN搜索"机器学习"，返回阅读量最高的3篇文章 |
| 执行 | `run_task("在CSDN搜索机器学习，返回阅读量最高的3篇文章")` |
| 预期 URL | `csdn.net` |
| 预期结果 | 返回至少 3 行文章信息 |
| 验证规则 | `result.output.lines.length >= 3` |
| 判定 | 输出包含至少 3 篇文章信息 |

---

## 15. Gitee

### 任务 15.1：搜索仓库

| 属性 | 值 |
|------|-----|
| 任务 | 在Gitee搜索"Python"，返回前5个仓库的名称、Stars和描述 |
| 执行 | `run_task("在Gitee搜索Python，返回前5个仓库的名称、Stars和描述")` |
| 预期 URL | `gitee.com` |
| 预期结果 | 返回至少 5 行仓库信息 |
| 验证规则 | `url.contains("gitee.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含 gitee.com 且输出包含仓库信息 |

### 任务 15.2：搜索热门项目

| 属性 | 值 |
|------|-----|
| 任务 | 在Gitee找到当前最热门的10个Python项目 |
| 执行 | `run_task("在Gitee找到当前最热门的10个Python项目")` |
| 预期 URL | `gitee.com` |
| 预期结果 | 返回至少 10 行项目信息 |
| 验证规则 | `result.output.lines.length >= 10` |
| 判定 | 输出包含至少 10 个项目信息 |

### 任务 15.3：搜索特定语言

| 属性 | 值 |
|------|-----|
| 任务 | 在Gitee搜索"machine-learning"，只看Python语言的项目 |
| 执行 | `run_task("在Gitee搜索machine-learning，只看Python语言的项目")` |
| 预期 URL | `gitee.com` |
| 预期结果 | 返回 Python 项目列表 |
| 验证规则 | `output.contains("Python") \|\| output.contains("python")` |
| 判定 | 输出包含 Python 相关信息 |

---

## 16. 百度百科

### 任务 16.1：查询词条

| 属性 | 值 |
|------|-----|
| 任务 | 在百度百科查询"人工智能"，返回词条的简介（前200字） |
| 执行 | `run_task("在百度百科查询人工智能，返回词条的简介")` |
| 预期 URL | `baike.baidu.com` |
| 预期结果 | 输出包含 "人工智能" 的简介，长度 > 50 字 |
| 验证规则 | `url.contains("baike.baidu.com") && output.contains("人工智能")` |
| 判定 | URL 包含百科域名且输出包含词条名 |

### 任务 16.2：查询并提取信息

| 属性 | 值 |
|------|-----|
| 任务 | 在百度百科查询"Python"，返回创建时间、创始人、最新版本等信息 |
| 执行 | `run_task("在百度百科查询Python，返回创建时间、创始人、最新版本等信息")` |
| 预期 URL | `baike.baidu.com` |
| 预期结果 | 输出包含 Python 相关信息 |
| 验证规则 | `output.contains("Python") && output.length > 100` |
| 判定 | 输出包含有意义的内容 |

### 任务 16.3：查询多个词条

| 属性 | 值 |
|------|-----|
| 任务 | 分别在百度百科查询"机器学习"、"深度学习"、"神经网络"，返回各自的简介 |
| 执行 | `run_task("分别在百度百科查询机器学习、深度学习、神经网络，返回各自的简介")` |
| 预期结果 | 输出包含 3 个词条的简介 |
| 验证规则 | `output.contains("机器学习") && output.contains("深度学习") && output.contains("神经网络")` |
| 判定 | 输出包含所有 3 个词条名 |

---

## 17. 百度文库

### 任务 17.1：搜索文档

| 属性 | 值 |
|------|-----|
| 任务 | 在百度文库搜索"Python教程"，返回前5个文档的标题和页数 |
| 执行 | `run_task("在百度文库搜索Python教程，返回前5个文档的标题和页数")` |
| 预期 URL | `wenku.baidu.com` |
| 预期结果 | 返回至少 5 行文档信息 |
| 验证规则 | `url.contains("wenku.baidu.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含文库域名且输出包含文档信息 |

### 任务 17.2：搜索特定类型

| 属性 | 值 |
|------|-----|
| 任务 | 在百度文库搜索"年终总结"，只看PPT类型的结果 |
| 执行 | `run_task("在百度文库搜索年终总结，只看PPT类型的结果")` |
| 预期 URL | `wenku.baidu.com` |
| 预期结果 | 返回 PPT 类型文档列表 |
| 验证规则 | `output.contains("PPT") \|\| output.contains("ppt")` |
| 判定 | 输出包含 PPT 相关信息 |

---

## 18. QQ邮箱

### 任务 18.1：查看收件箱

| 属性 | 值 |
|------|-----|
| 任务 | 登录QQ邮箱，返回最近5封邮件的发件人和主题 |
| 执行 | `run_task("登录QQ邮箱，返回最近5封邮件的发件人和主题")` |
| 预期 URL | `mail.qq.com` |
| 预期结果 | 返回至少 5 行邮件信息 |
| 验证规则 | `url.contains("mail.qq.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含QQ邮箱域名且输出包含邮件信息 |

### 任务 18.2：搜索邮件

| 属性 | 值 |
|------|-----|
| 任务 | 在QQ邮箱搜索"工作"，返回相关邮件的标题和日期 |
| 执行 | `run_task("在QQ邮箱搜索工作，返回相关邮件的标题和日期")` |
| 预期 URL | `mail.qq.com` |
| 预期结果 | 返回邮件列表 |
| 验证规则 | `output.contains("工作") \|\| output.length > 50` |
| 判定 | 输出包含搜索关键词或邮件信息 |

### 任务 18.3：统计未读邮件

| 属性 | 值 |
|------|-----|
| 任务 | 登录QQ邮箱，返回未读邮件的数量 |
| 执行 | `run_task("登录QQ邮箱，返回未读邮件的数量")` |
| 预期 URL | `mail.qq.com` |
| 预期结果 | 输出包含数字 |
| 验证规则 | `any(char.isdigit() for char in output)` |
| 判定 | 输出包含数字（未读数量） |

---

## 19. 163邮箱

### 任务 19.1：查看收件箱

| 属性 | 值 |
|------|-----|
| 任务 | 登录163邮箱，返回最近5封邮件的发件人和主题 |
| 执行 | `run_task("登录163邮箱，返回最近5封邮件的发件人和主题")` |
| 预期 URL | `mail.163.com` |
| 预期结果 | 返回至少 5 行邮件信息 |
| 验证规则 | `url.contains("mail.163.com") && result.output.lines.length >= 5` |
| 判定 | URL 包含163邮箱域名且输出包含邮件信息 |

### 任务 19.2：搜索邮件

| 属性 | 值 |
|------|-----|
| 任务 | 在163邮箱搜索"会议"，返回相关邮件的标题和日期 |
| 执行 | `run_task("在163邮箱搜索会议，返回相关邮件的标题和日期")` |
| 预期 URL | `mail.163.com` |
| 预期结果 | 返回邮件列表 |
| 验证规则 | `output.contains("会议") \|\| output.length > 50` |
| 判定 | 输出包含搜索关键词或邮件信息 |

---

## 20. 天气网

### 任务 20.1：查询天气

| 属性 | 值 |
|------|-----|
| 任务 | 查询北京今天的天气，返回温度、天气状况、风力 |
| 执行 | `run_task("查询北京今天的天气，返回温度、天气状况、风力")` |
| 预期 URL | `weather.com.cn` |
| 预期结果 | 输出包含温度数字和天气描述 |
| 验证规则 | `output.contains("北京") && any(c.isdigit() for c in output)` |
| 判定 | 输出包含城市名和温度数字 |

### 任务 20.2：查询未来一周天气

| 属性 | 值 |
|------|-----|
| 任务 | 查询上海未来一周的天气预报 |
| 执行 | `run_task("查询上海未来一周的天气预报")` |
| 预期 URL | `weather.com.cn` |
| 预期结果 | 输出包含多天天气信息 |
| 验证规则 | `output.contains("上海") && output.length > 100` |
| 判定 | 输出包含城市名和天气信息 |

### 任务 20.3：对比城市天气

| 属性 | 值 |
|------|-----|
| 任务 | 对比北京和上海今天的温度，哪个更热 |
| 执行 | `run_task("对比北京和上海今天的温度，哪个更热")` |
| 预期结果 | 输出包含两个城市的温度对比 |
| 验证规则 | `output.contains("北京") && output.contains("上海")` |
| 判定 | 输出包含两个城市名 |

---

## 验证函数设计

```python
def verify_result(task_result, expected):
    """验证任务执行结果。

    Args:
        task_result: AgentTaskResult 对象
        expected: 预期结果字典

    Returns:
        dict: {passed: bool, checks: list, details: str}
    """
    checks = []

    # 1. 检查执行状态
    if not task_result.success:
        checks.append({"name": "execution", "passed": False, "detail": "任务执行失败"})

    # 2. 检查 URL
    if "url_contains" in expected:
        url_ok = expected["url_contains"] in task_result.final_url
        checks.append({"name": "url", "passed": url_ok, "detail": f"URL: {task_result.final_url}"})

    # 3. 检查输出内容
    if "output_contains" in expected:
        for keyword in expected["output_contains"]:
            content_ok = keyword in task_result.output
            checks.append({"name": f"content_{keyword}", "passed": content_ok, "detail": f"包含: {keyword}"})

    # 4. 检查输出长度
    if "output_min_length" in expected:
        length_ok = len(task_result.output) >= expected["output_min_length"]
        checks.append({"name": "output_length", "passed": length_ok, "detail": f"长度: {len(task_result.output)}"})

    # 5. 检查输出行数
    if "output_min_lines" in expected:
        lines = [l for l in task_result.output.split("\n") if l.strip()]
        lines_ok = len(lines) >= expected["output_min_lines"]
        checks.append({"name": "output_lines", "passed": lines_ok, "detail": f"行数: {len(lines)}"})

    # 汇总
    all_passed = all(c["passed"] for c in checks)
    return {"passed": all_passed, "checks": checks}
```

---

## 测试执行流程

```
1. 读取任务列表
2. 对每个任务：
   a. 执行 run_task(task_description)
   b. 获取执行结果
   c. 对照预期结果验证
   d. 记录 PASS/FAIL
3. 生成测试报告
```

## 测试报告格式

```
=== 测试报告 ===

任务 1.1: 帮我在百度搜索 Python 教程
  执行: PASS
  URL: PASS (baidu.com/s)
  内容: PASS (包含 Python)
  判定: ✅ PASS

任务 1.2: 在必应搜索"深度学习"，返回前3条结果的标题和摘要
  执行: PASS
  URL: PASS (bing.com)
  内容: FAIL (输出为空)
  判定: ❌ FAIL

=== 统计 ===
通过: 45/52
失败: 7/52
通过率: 86.5%
```
