/**
 * pocket-mew — host-side poll → trigger example
 *
 * 1. Copy to mini_cat_trigger.js (or rename)
 * 2. Set WORKER_URL / tokens via env
 * 3. Implement sendTrigger() for YOUR agent inject path
 *
 *   WORKER_URL=https://touch.example.com/poll \
 *   WORKER_TOKEN=... \
 *   node mini_cat_trigger.example.js
 */

const WORKER_URL = process.env.WORKER_URL || "https://touch.example.com/poll";
const WORKER_TOKEN = process.env.WORKER_TOKEN || "";
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS || 3000);
const MIN_TRIGGER_INTERVAL_MS =
  Number(process.env.MIN_INTERVAL_MIN || 10) * 60 * 1000;

let lastTriggerTime = 0;
let todayDate = "";
let todayCount = 0;

function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
}

/** button → belly poke; FSR touch → paw pad (tune for your shell) */
function pickAction(event) {
  return event.type === "button" ? "belly_poke" : "paw_pad";
}

const ACTION_TEXT_DONE = {
  petting: "摸了摸你",
  belly_poke: "戳了下你肚子",
  paw_pad: "捏了下你肉垫",
};
const ACTION_TEXT_VERB = {
  petting: "撸你",
  belly_poke: "戳你肚子",
  paw_pad: "捏你肉垫",
};

function buildMessage(count, event) {
  const action = pickAction(event);
  let line;
  if (count === 1) line = `今天第1次${ACTION_TEXT_DONE[action]}`;
  else if (count <= 5) line = `今天第${count}次${ACTION_TEXT_VERB[action]}`;
  else if (count <= 9) line = `今天蹂躏个没完，${count}次了`;
  else line = `今天把 pocket-mew 薅秃了，${count}次了`;

  return {
    message: `Free Roam🐈‍⬛ pocket-mew · "${line}"`,
    action,
  };
}

/**
 * ⚠️ 换成你自己的注入。
 * 不要把私人 cookie / 绝对路径提交回公开仓库。
 */
async function sendTrigger(message) {
  // Example: webhook
  // await fetch(process.env.INJECT_WEBHOOK, {
  //   method: "POST",
  //   headers: { "content-type": "application/json" },
  //   body: JSON.stringify({ text: message }),
  // });
  console.log("[inject stub]", message);
}

async function poll() {
  try {
    const headers = {};
    if (WORKER_TOKEN) headers.authorization = `Bearer ${WORKER_TOKEN}`;
    const res = await fetch(WORKER_URL, { headers });
    const data = await res.json();
    if (!data.event) return;

    const today = todayStr();
    if (todayDate !== today) {
      todayDate = today;
      todayCount = 0;
    }

    const now = Date.now();
    if (now - lastTriggerTime < MIN_TRIGGER_INTERVAL_MS) {
      console.log("cooldown, skip");
      return;
    }

    todayCount += 1;
    lastTriggerTime = now;
    const { message, action } = buildMessage(todayCount, data.event);
    console.log(`#${todayCount} ${action}`, data.event);
    await sendTrigger(message);
  } catch (e) {
    console.error("poll error:", e.message);
  }
}

console.log("pocket-mew host trigger up");
console.log("poll:", WORKER_URL, `every ${POLL_INTERVAL_MS}ms`);
setInterval(poll, POLL_INTERVAL_MS);
poll();
