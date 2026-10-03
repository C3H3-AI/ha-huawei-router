---
name: huawei-router-standalone
description: 不依赖 Home Assistant / huawei_router 集成，直连华为凌霄 Q6 路由器的 LAN HTTP API 做检查和控制的独立脚本。当环境里没有 HA、HA 集成不可用、或需要在 HA 之外（如宿主机、临时排查）直接操作路由器时使用。提供 router_cli.py（含 logout、端点短名表、破坏性操作拦截、配置备份、诊断日志下载）。
---

# 华为路由器 — 独立直连（不依赖 HA 集成）

**独立路径**：绕开 Home Assistant 和 `huawei_router` 集成，直接用路由器 LAN HTTP API。

- 日常通过 HA 集成控制 → `huawei-router-control`
- **本 skill** → 无 HA / 集成挂了 / 宿主机直接排查 / 一次性脚本

脚本：`scripts/router_cli.py`（**全部命令真机验证通过**）。

---

## 一、运行

```bash
pip install aiohttp pycryptodome

export HW_HOST="http://<ROUTER_IP>"   # 默认
export HW_USER="admin"                # 默认
export HW_PASS="<管理密码>"            # 必填
```

| 命令 | 作用 | 实测 |
|---|---|---|
| `status` | 型号/固件/HarmonyOS/运行时间/CPU/内存/在线设备/Mesh节点 | ✅ |
| `devices [--online]` | 设备列表（MAC/IP/名称，标注子路由、离线）| ✅ 152 条 |
| `wifi` | 2.4G/5G 信道、带宽、SSID、加密、功率 | ✅ |
| `ports` | 各网口速率与连接状态 | ✅ 发现 LAN2/IPTV 未连接 |
| `endpoints [关键字]` | 列出可用端点短名（内置 186 项映射表）| ✅ |
| `get <短名/路径>` | 任意端点只读 GET | ✅ |
| `exec <短名> [k=v]` | 通用 POST（破坏性需 `--force`）| ✅ |
| `backup <路径>` | 导出配置 .conf | ✅ 86 KB |
| `devlist` | 列出可诊断设备（主路由 + 各子路由，含 MAC）| ✅ 6 台 |
| `diag <目录> [目标MAC]` | 收集+下载诊断日志；**给 MAC 即采集该子路由** | ✅ 12-18 秒 / 620-624 KB |

### ★ 子路由日志可采集（实测确认 —— 唯一能拿到子路由内部信息的通道）

Q6 网线版子路由**没有独立管理界面**（无法单独登录、无 api 端点、不能单独重启），
但**主路由可以代收子路由的诊断日志**：

```bash
python3 router_cli.py devlist                        # 拿到子路由 MAC
python3 router_cli.py diag /tmp 88:81:B9:67:87:4A    # 采集该子路由日志
```

对照实验证实两者是**不同设备**的日志（不是同一份重复下载）：

| 证据 | 主路由包 | 子路由包 |
|---|---|---|
| md5 | `1fc5fc71…` | `c4296885…`（不同）|
| syslog 最新时间 | `2026-10-03 08:22:22` | `2026-10-02 23:35:36`（滞后）|
| 含本次采集动作 | 8 行 | **0 行** |
| 特有内容 | 用户操作记录 | `1970-01-01` / `2023-03-21` 未同步时钟、`DAD_LOG: dev eth0 collision` |

---

## 二、认证协议（逆向已验证）

三步 SCRAM 风格：

1. `GET /html/index.html` → 正则取 `csrf_param` / `csrf_token`
2. `POST api/system/user_login_nonce`
   `{"csrf":{...},"data":{"username":...,"firstnonce":<32字节hex>}}`
   → 返回 `servernonce` / `iterations` / `salt`
3. `POST api/system/user_login_proof`
   `{"csrf":{...},"data":{"clientproof":...,"finalnonce":servernonce}}`

**clientproof**：
```
salted = pbkdf2_hmac("sha256", pw, bytes.fromhex(salt), iterations, 32)
ck = HMAC(b"Client Key", salted).digest()
sk = sha256(ck).digest()
cs = HMAC(f"{fn},{sn},{sn}".encode(), sk).digest()
proof = bytes(a^b for a,b in zip(ck,cs)).hex()
```

**必需 header**（缺了被拒绝）：
```
User-Agent: Mozilla/5.0 ... Chrome/131.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
Origin: http://<ROUTER_IP>
Referer: http://<ROUTER_IP>/html/index.html
```
`CookieJar(unsafe=True)`（路由器用 IP 而非域名）。

---

## 三、请求格式

```
GET  /api/<路径>
POST /api/<路径>  {"data":{...}, "csrf":{...}}   # 写操作常需 "action":"update"
```

短名解析：脚本内置 `ENDPOINTS` 表（186 项，逆向自前端 main.js），
`get wlanradio` 会自动解析成 `api/ntwk/wlanradio`。用 `endpoints` 查有哪些短名。

---

## 四、⚠️ 红线

1. **★ 必须 logout**：路由器**仅 2 个并发 session**。脚本用 `async with` 退出时自动
   `POST api/system/user_logout`。**别绕过上下文管理器**，否则 session 占着直到超时，
   下次登录报 `Too_Many_user`
2. HA 集成常驻占 1 个 → 独立脚本只剩 1 个；限流后等 **2-3 分钟**
3. 探测用 raw 请求看状态码，**不要自动重登录**（瞬间打满）
4. 循环间隔 `sleep(1.5)`
5. **破坏性操作需 `--force`**：`restoredefcfg`(恢复出厂)、`uploadconfigfile`(导入配置=
   覆盖+重启60秒)、`device_remove`、`reboot`、`forceupg`。先 `backup` 再动
6. 独立脚本**不更新 HA 实体**——只是旁路操作

---

## 五、端点速查

**可用**：`deviceinfo` `HostInfo` `processstatus` `device_count` `onlinestate`
`diagnose_wlan_basic?type=1/2` `ethnegotiation` `lan` `lan_all` `lan_host`
`wlanradio` `multi_ssid` `guest_network` `wlanfilterenhance` `homesec_abfa/stcalnet`
`firewall` `dmz` `portmapping` `application` `upnp` `ddns` `ipv6_wan/lan` `iptv`
`alg` `smartvpn` `wan` `wandetect` `timedredial` `qosclass_host` `changedevicename`
`topology` `hilink_status` `repeaterstate` `wifiscan` `channelinfo` `sntp`
`diagnose_crash`(+`_devlist`) `downloadcfg`(导出) `useraccount` `pwdrule`

**404（别浪费时间）**：`bsp/nfc_switch` `ntwk/timecontrol` `ntwk/portforwarding`
`ntwk/wps_switch` `ntwk/wlanwps` `ntwk/ipcapture` `ntwk/mirror` `poweroff`
`powerofflist` `dps_switch` `sshRemoteState` `telnetRemoteState` `wanremoteaccess`
`remoteaccesslist`

---

## 六、复用 Router 类

```python
from router_cli import Router

async with Router() as r:            # 退出时自动 logout
    await r.login()
    d = await r.get("deviceinfo")              # 支持短名
    await r.sleep()                             # 请求间隔
    await r.post("qosclass_host", {...}, action="update")
    await r.download("api/system/downloadcfg", "/tmp/b.conf")
```

---

## 七、相关

- `huawei-router-control` — HA 集成路径（日常推荐）
- `huawei-router-dev` — 逆向/开发方向
