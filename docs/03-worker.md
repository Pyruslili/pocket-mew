# 03 · 中继 Worker

> 状态：骨架。示例代码在 `worker/cloudflare/`。

## 为什么要中继

板子在外面，你家电脑在 NAT 后面。  
让板子只认识一个公网 HTTPS 地址；本机再去把事件「拉」回来。

## 最小 API

| 方法 | 路径 | 作用 |
|------|------|------|
| `POST` | `/touch` | 硬件上报事件，入队 |
| `GET`  | `/poll`  | 本机取走**一条**事件（取后删除或标记） |
| `GET`  | `/peek`  | 只看队列，不消费（调试 / MCP） |

## 部署提示（Cloudflare Workers）

1. 建 Worker，把 `worker/cloudflare/worker.js` 贴进去（或 wrangler 发布）  
2. 绑定 KV 或用 Durable Object / 甚至临时内存（内存重启会丢，仅适合玩）  
3. 自定义域名，打开 HTTPS  
4. 固件里 `TOUCH_HOST` 指到该域名  

**鉴权（强烈建议）**  
示例为了好读可能很裸；上线请加：

- 硬件 POST：共享 header token  
- 本机 poll：另一个 token  

token 只放环境变量，别写进公开 README 的可复制块里当真值。

下一章：`04-host-trigger.md`
