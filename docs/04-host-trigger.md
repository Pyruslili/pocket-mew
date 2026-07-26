# 04 · 本机 trigger

> 状态：骨架。示例：`host/mini_cat_trigger.example.js`

## 它做什么

1. 每 N 秒 `GET /poll`  
2. 有事件 → 看冷却 / 今日次数  
3. 拼一条人类可读文案（我们叫它 Free Roam）  
4. 交给**你自己的**注入方式：脚本、webhook、socket、agent hook……

## 动作语义（可改）

| 硬件 | 我们的词 | 说明 |
|------|----------|------|
| `button` | 戳肚子 `belly_poke` | 明确按键 |
| `touch`（FSR） | 捏肉垫 `paw_pad` | 能过阈值的通常是按/捏，不是羽毛级轻抚 |

## 冷却

出门走路会误触。示例默认：

- 最小间隔：例如 10 分钟  
- 可选：每日上限  

按你的 agent 脾气改。

## 接到你的 AI

示例里 `sendTrigger(message)` 是空心的——请接到：

- 自建 inject 脚本  
- 开放的 agent webhook  
- tmux 里某 session 的提示注入  
- ……任何你用的方式  

**不要**把只属于你账号的 cookie、绝对路径、私人 hook 配置提交回这个仓库。

下一章：`05-safety.md`
