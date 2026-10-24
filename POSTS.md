# 社区短帖文案（Reddit / Hacker News / QQ 群）

> 和 BLOG.md（长文）分开用。短帖的规则：**低姿态、讲痛点、求反馈、绝不推销。**
> 社区极度反感广告腔和新号硬广；用「我被这个坑过，做了个东西，想听听你们的场景」的姿态。
> 发帖前把 token 数字（178 / 0 / 190）换成最新一次真实运行的值。
>
> ⚠️ Reddit 对代理 IP 风控严格，可能登录受阻。若打不通就跳过，不要硬耗——
> 国内（掘金 / V2EX / QQ 群）+ dev.to + Hacker News 已足够覆盖。

---

## 1. Hacker News — Show HN

**提交方式**：HN 的 "Show HN" 用法是 title + URL。URL 填 GitHub 仓库。
正文留空或极简，真正的说明放进你自己发的**第一条评论**。

### Title

```
Show HN: Scrapemend – a scraper that repairs its own selectors when sites change
```

### URL

```
https://github.com/FengYue427/scrapemend
```

### First comment（发布后立刻自己贴在评论区）

```
Author here. Every scraper I wrote died the same way: not with an error, but
silently — a site shipped a redesign, my CSS selectors matched nothing, and the
script kept returning empty fields until I noticed days later.

Hand-written selectors are free but break on every redesign. Cloud "AI scraping"
services are robust but pricey and call a model on every request.

Scrapemend tries the middle path: treat a broken selector as a cache miss, not a
crash. Cached selectors run with zero LLM cost; the model is only called when a
field stops matching, and the repaired selectors are cached so the next run is
free again.

A real run against two versions of the same page, same schema, no code changes:
  - first visit (no cache): healed, 178 tokens
  - same markup again:      cache hit, 0 tokens
  - after a redesign:       healed, 190 tokens

Before the model sees a page the HTML is condensed (scripts/styles/noise attrs
stripped) — on a bloated page that cut the prompt ~90%, which keeps healing cheap.
It ships an offline stub (runs with no API key) plus OpenAI and DeepSeek adapters.

It's early (0.0.1) and I'd genuinely like to know where it breaks on real sites.
MIT. Feedback welcome.
```

**发布后**：盯着评论区，24 小时内回每一条。有人质疑就老实回答、有人提 bug 就谢谢并记下。
HN 吃「作者真诚、技术扎实」，不吃「防御/嘴硬」。

---

## 2. Reddit — r/webscraping

**注意**：先看该版规则（有的版块禁止自我推广或要求标 flair）。用 "I built ..." 的分享/求反馈姿态。
标题讲痛点，不要堆产品名。

### Title

```
I got tired of scrapers silently dying after every redesign, so I made the selectors heal themselves
```

### Body

```
Like everyone here, my scrapers never crash on a redesign — they just quietly
return empty fields until I notice the data is wrong days later.

I wanted the robustness of the "LLM reads the page" approach without paying a
model call on every single request. So I built a small library around one idea:
a broken selector is a cache miss, not a crash.

How it works:
- You describe the fields in plain language (no selectors).
- Cached selectors run first — pure parsing, zero LLM cost.
- Only when a field stops matching does an LLM re-derive the selectors, which
  then get cached. So you pay the model exactly when a site actually changes.

Real run, same schema on two versions of a page, no code change:
first visit → healed (178 tokens), same page again → cache hit (0 tokens),
after a redesign → healed again (190 tokens).

HTML is condensed before the model sees it (scripts/styles/noise attrs stripped),
which cut a bloated page's prompt by ~90%.

It's open source (MIT), early days, has an offline stub so it runs without an API
key, and adapters for OpenAI and DeepSeek.

Mostly I want to know: does this approach hold up on the messy sites you actually
scrape? Where would it fall over? Repo: https://github.com/FengYue427/scrapemend
```

**发布后**：r/webscraping 的人很懂技术，会问尖锐问题（反爬、JS 渲染、动态 class、速率限制）。
老实承认当前边界（比如还没做 JS 渲染），把它们记成 roadmap。真诚 > 完美。

---

## 3. 备选英文社区（dev.to 的讨论区 / Lobsters）

如果 Reddit 打不通，Lobsters 可用（需邀请码）；或在 dev.to 文章里主动引导评论。
用 Reddit 那版 Body 稍微精简即可，姿态一致。

---

## 4. QQ 群 / 微信技术群短文案（国内，最快反馈）

**用法**：进 Python / 爬虫 / 开源相关的群，别刷屏，挑合适时机发一条。姿态是「分享 + 求试用」，不是打广告。

```
分享个我自己写的开源小库 scrapemend，解决一个老痛点：爬虫最烦的不是报错，是网站
改版后选择器悄悄失效、脚本照跑却返回空值，过几天才发现。

思路是「选择器失效 = 缓存未命中，而不是崩溃」：平时用缓存的选择器跑，零大模型开销；
只有某个字段匹配不上了，才调一次 LLM 重新生成选择器并缓存起来，下次又免费。相当于
只在网站真改版时才花一次钱。内置离线桩（没 key 也能跑通流程），接了 OpenAI 和
DeepSeek，DeepSeek 便宜到自愈几乎不要钱。

还很早期，就想找人试试在真实网站上扛不扛得住、哪里会崩。
pip install scrapemend
仓库：https://github.com/FengYue427/scrapemend
```

**发布后**：群里反馈往往最直接（「我那个站就这样」「你这个和 XX 有啥区别」）。
这些是最真实的需求信号，收集下来。

---

## 发布节奏建议（Reddit 打不通也不影响）

1. 先发 **掘金**（BLOG.md 中文版）+ **几个 QQ 群**（本文第 4 条）——无障碍、母语、反馈最快。
2. 再发 **dev.to**（BLOG.md 英文版）——国外主入口，长期吃搜索。
3. 然后 **Show HN**（本文第 1 条）——国外爆发点，选美西时间早上发。
4. **Reddit** 能登上就发（第 2 条），登不上直接跳过，不耗。
5. 每发一处，等反馈、回评论、把真实问题记成 roadmap，再发下一处。
```
