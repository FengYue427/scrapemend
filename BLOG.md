# 发布文章（中英双版）

> 用途：dev.to / Hacker News / Reddit r/webscraping 发英文版；掘金 / V2EX 发中文版。
> 原则：讲痛点、讲取舍、给真实数据，不吹。文末才出现安装引导。
> 文内 token 数字来自真实 DeepSeek 运行（Run1=178, 缓存=0, 改版后 Run3=190），发布前如重跑请替换为最新真实值。

---

## English version

### Title options (pick one)

- Why your scraper breaks every time a site is redesigned — and how to make it heal itself
- I got tired of rewriting scrapers after every redesign, so I made selectors repair themselves
- Show HN: scrapemend — self-healing web scraping that repairs itself when sites change

### Body

Every scraper I've ever written died the same death. Not with an error — with
silence. The site shipped a redesign, my CSS selectors matched nothing, and the
script kept running and returning empty fields. I'd notice days later when the
data looked wrong.

The usual fixes all have a catch:

- **Hand-written selectors** are free and fast, but every redesign means a
  manual rewrite. The maintenance never ends.
- **Cloud "AI scraping" services** are robust, but they're expensive, they send
  the pages you're scraping through someone else's servers, and they run a model
  call on *every single request* — your bill scales with your crawl.

I wanted the robustness of the AI approach without paying for it on every page.
So I built [scrapemend](https://github.com/FengYue427/scrapemend) around one
idea: **treat a broken selector as a cache miss, not a crash.**

#### How it works

You describe *what* you want in plain language — no selectors:

```python
from scrapemend import Scraper, Schema

schema = (
    Schema("product")
    .add("title", "the product name")
    .add("price", "the product price with currency")
)

scraper = Scraper()
result = scraper.extract("https://shop.example/p/1", schema)
print(result["title"], result["price"])
```

Under the hood:

```
extract(url, schema)
      │
      ├─ cached selectors exist? ──► apply them
      │                               ├─ all fields matched ──► return (free)
      │                               └─ some field missed ──┐
      │                                                      ▼
      └─ no cache ─────────────────────────────────► LLM heals selectors
                                                      apply, cache, return
```

The LLM only runs when selectors are missing or have stopped matching. In the
steady state, extraction is just parsing — zero tokens. You pay the model
exactly when a site actually changes, and the repaired selectors are cached so
the next run is free again.

#### Does it actually survive a redesign?

Here's a real run against two versions of the same page — same `Schema`, no code
changes:

```
Run 1 — first visit, no cache        -> HEALED,     178 tokens
Run 2 — same markup again            -> CACHE HIT,     0 tokens
Run 3 — site redesigned (new markup) -> HEALED,     190 tokens
```

Run 2 is the whole point: once selectors are known, you're not paying anything.
Run 3 is the other half: when the markup changed and the cached selectors broke,
it repaired itself and still returned the right data.

Before the LLM ever sees a page, the HTML is condensed — scripts, styles, and
noise attributes are stripped, keeping only structure and `class`/`id`. On a
typical bloated page that cut the prompt by over 90%, which keeps healing cheap.

#### Try it

```bash
pip install scrapemend
```

It ships with an offline stub so the pipeline runs with no API key, and
provider adapters for OpenAI and DeepSeek when you want real healing. DeepSeek
in particular makes healing almost free.

Code and docs: https://github.com/FengYue427/scrapemend

It's early (`0.0.1`) and I'd genuinely like feedback on where it breaks. If
you've ever lost a day to a silent scraper, I'd love to know whether this
approach holds up on the sites you work with.

---

## 中文版

### 标题备选（选一个）

- 为什么你的爬虫总在网站改版后悄悄崩掉，以及怎么让它自己修好
- 我受够了每次网站改版就重写爬虫，于是让选择器学会了自愈
- 一个会自我修复的爬虫库：网站改版也不怕

### 正文

我写过的每一个爬虫，都是以同一种方式"死"的——不是报错，而是**沉默**。网站改了版，
CSS 选择器一个都匹配不上，脚本照常运行、照常返回空字段。往往过了好几天，我才在数据
不对劲的时候发现它早就废了。

常见的几种做法都有各自的坑：

- **手写选择器**：免费、快，但每次网站改版都得手动重写，维护成本没有尽头。
- **云端"AI 抓取"服务**：够健壮，但贵，而且要把你抓的页面发到别人的服务器上，还会
  **每一次请求都调一次大模型**——账单随着抓取量一起涨。

我想要 AI 方案的健壮性，但不想为每一个页面都付钱。于是我做了
[scrapemend](https://github.com/FengYue427/scrapemend)，核心就一句话：
**把"选择器失效"当成一次缓存未命中，而不是一次崩溃。**

#### 它怎么工作

你只用自然语言描述**你要什么**，不写选择器：

```python
from scrapemend import Scraper, Schema

schema = (
    Schema("product")
    .add("title", "商品名称")
    .add("price", "含货币符号的商品价格")
)

scraper = Scraper()
result = scraper.extract("https://shop.example/p/1", schema)
print(result["title"], result["price"])
```

内部逻辑：

```
extract(url, schema)
      │
      ├─ 有缓存的选择器？ ──► 直接套用
      │                        ├─ 全部字段命中 ──► 返回（零成本）
      │                        └─ 有字段没命中 ──┐
      │                                          ▼
      └─ 没有缓存 ───────────────────────► LLM 重新生成选择器
                                            套用、写回缓存、返回
```

LLM 只在选择器缺失或失效时才被调用。稳定运行时，提取就是纯解析——**零 token**。
只有当网站真的改版时你才付一次模型的钱，而且修好的选择器会被缓存，下一次又回到免费。

#### 它真的扛得住改版吗？

下面是对同一个页面两个版本的真实运行——**同一个 `Schema`，一行代码没改**：

```
Run 1 — 首次访问，无缓存       -> 自愈，     178 tokens
Run 2 — 相同页面再访问         -> 命中缓存，   0 tokens
Run 3 — 网站改版（新结构）     -> 自愈，     190 tokens
```

Run 2 才是重点：选择器一旦学会，之后就不再花钱。Run 3 是另一半：当结构变了、
缓存的选择器失效，它自己修好了，而且照样返回了正确的数据。

在 LLM 看到页面之前，HTML 会先被"瘦身"——删掉 script、style 和噪音属性，只保留
结构和 `class`/`id`。在一个典型的臃肿页面上，这一步把 prompt 削掉了 90% 以上，
自愈因此一直很便宜。

#### 试一下

```bash
pip install scrapemend
```

它自带一个离线桩，没有 API key 也能把整条流程跑通；需要真实自愈时，内置了 OpenAI
和 DeepSeek 两个适配器。尤其是 DeepSeek，便宜到自愈成本几乎可以忽略。

代码和文档：https://github.com/FengYue427/scrapemend

项目还很早（`0.0.1`），我很想知道它在什么场景下会崩。如果你也曾因为一个"悄悄失效"
的爬虫浪费过一整天，欢迎告诉我，这个思路在你实际抓的网站上扛不扛得住。
```
