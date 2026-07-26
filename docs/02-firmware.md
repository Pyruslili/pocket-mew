# 02 · 固件

> 状态：骨架。完整可编译工程在 `firmware/mini-mew/`。

## 它做什么

1. 连 Wi‑Fi  
2. 读 FSR：超过阈值开始采样曲线，松开一次 → `POST` 一条 `touch`  
3. 读按钮：按下松开 → `POST` 一条 `button`  
4. body 示例：

```json
{
  "type": "touch",
  "peak_raw": 1234,
  "duration_ms": 420,
  "curve": [210, 400, 800, 600]
}
```

## 配置（不要提交真值）

复制示例头文件，填自己的：

```bash
cp firmware/mini-mew/include/secrets.h.example firmware/mini-mew/include/secrets.h
```

```cpp
// secrets.h.example
#pragma once
#define WIFI_SSID     "your-ssid"
#define WIFI_PASSWORD "your-password"
#define TOUCH_HOST    "touch.example.com"  // 你的 Worker 域名
#define TOUCH_PATH    "/touch"
```

`secrets.h` 已在 `.gitignore`。

## 构建

```bash
cd firmware/mini-mew
pio run -t upload
pio device monitor
```

串口看到 `已连接` 和 `POST touch ... → 2xx` 就对了。

## 调阈值

外壳、海绵、垫片都会改变 FSR raw。  
太灵敏 → 提高 `FSR_THRESHOLD`；太钝 → 降低，或改分压。

下一章：`03-worker.md`
