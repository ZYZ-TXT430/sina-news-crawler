# 新浪新闻首页爬虫（Scrapy 反反爬虫机制研究）

基于 **Scrapy** 实现的新浪新闻首页内容抓取项目，内置多种反反爬虫策略，用于研究主流新闻网站的反爬机制与应对方案。抓取结果同时输出 **JSON** 与 **CSV** 两种格式。

> ⚠️ **免责声明**：本项目仅用于学习与技术研究，请遵守目标网站的 `robots.txt` 及相关法律法规，勿将抓取数据用于商业用途或非法目的。

## 功能特性

- 🕷️ 基于 Scrapy 异步框架，支持并发抓取
- 🔀 **随机 User-Agent**：内置 8 个主流浏览器 UA，每次请求随机切换
- ⏱️ **随机请求延迟**：基于 `DOWNLOAD_DELAY + RANDOMIZE_DOWNLOAD_DELAY` 及每请求 `download_delay` 双重随机化，降低访问频率特征
- 🌐 **代理扩展**：预留 Proxy 中间件，可在 `settings.py` 中配置代理池
- 🔁 **智能重试**：对 403/404/5xx 等状态码自动重试（最多 3 次）
- 🗃️ **HTTP 缓存**：开启 1 小时缓存，避免重复请求
- 📄 **双格式输出**：每次运行自动生成带时间戳的 JSON + CSV 文件
- 🏷️ **自动分类**：新闻自动映射为国内/国际/财经/体育等 10 个分类

## 目录结构

```
sina-news-crawler/
├── sina_news_crawler/           # Scrapy 工程
│   ├── spiders/
│   │   └── sina_spider.py       # 主爬虫（解析新浪新闻首页）
│   ├── items.py                 # 数据模型定义
│   ├── middlewares.py           # 反反爬虫中间件（随机UA/延迟/代理/重试）
│   ├── pipelines.py             # 数据管道（JSON + CSV 双输出）
│   └── settings.py              # 全局配置
├── scrapy.cfg                   # Scrapy 部署配置
├── tests/                       # 单元测试
│   └── test_sina_spider.py
├── docs/                        # 研究报告文档
├── requirements.txt             # 依赖清单
└── README.md
```

## 环境要求

- Python 3.9+
- Scrapy 2.11+

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 运行爬虫

```bash
# 在项目根目录执行
scrapy crawl sina
```

### 输出说明

运行完成后，数据保存在 `sina_news_data/` 目录，命名格式为 `sina_news_YYYYMMDD_HHMMSS.json/.csv`。

| 字段 | 说明 |
|------|------|
| title | 新闻标题 |
| url | 新闻链接 |
| summary | 新闻摘要（可能为空） |
| source | 新闻来源 |
| publish_time | 发布时间（可能为空） |
| crawl_time | 抓取时间 |
| category | 分类（headline/rolling/domestic/international/finance/sports/entertainment/tech/military/education/health/culture/other） |

### 运行测试

```bash
python -m pytest tests/ -v
```

## 反反爬虫策略说明

| 策略 | 实现位置 | 说明 |
|------|----------|------|
| 随机 User-Agent | `middlewares.py` → `RandomUserAgentMiddleware` | 从 `USER_AGENTS` 池随机选择 |
| 随机延迟 | `settings.py` + `RandomDelayMiddleware` | Scrapy 原生随机延迟 + 每请求独立延迟 |
| 代理池 | `middlewares.py` → `ProxyMiddleware` | 在 `settings.py` 的 `PROXIES` 中填入代理即可启用 |
| 状态码重试 | `middlewares.py` → `CustomRetryMiddleware` | 对 403/404/5xx 自动重试，最多 3 次 |
| HTTP 缓存 | `settings.py` | `HTTPCACHE_ENABLED = True`，缓存 1 小时 |

## 常见问题

- **抓不到数据**：新浪首页 DOM 结构可能更新，请检查 `sina_spider.py` 中的 XPath 选择器。
- **被反爬拦截（403）**：适当增大 `DOWNLOAD_DELAY`，或配置代理池 `PROXIES`。
- **并发过高被封**：降低 `CONCURRENT_REQUESTS` 与 `CONCURRENT_REQUESTS_PER_DOMAIN`。

## 研究文档

详见 [docs/](./docs/) 目录中的研究报告：

- 《Scrapy反反爬虫机制研究_新浪新闻网站首页内容抓取》
- 《Scrapy反反爬虫机制研究_新浪新闻网站首页内容抓取_A4版》
- 《Scrapy反反爬虫机制研究_新浪新闻网站首页内容抓取_完整版》
