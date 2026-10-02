---
name: huawei-router-dev
description: 华为凌霄 Q6 路由器（huawei_router HA 集成）的逆向与开发方向。当要挖掘新 API 端点、逆向 Web UI 请求 payload、给集成新增功能（五件套）、排查端点是否真的可用、或理解集成代码结构时使用。含本机型已实测定性的端点清单（哪些 404 / 硬编码禁用），避免重复踩坑。
---

# 华为路由器 — 逆向与开发（huawei_router 集成）

面向**改代码 / 挖端点**的方向。
日常使用（控制、检查）→ `huawei-router-control`；无 HA 独立脚本 → `huawei-router-standalone`。

**当前基线**：仓库 `c3h3-ci/ha-huawei-router`，版本 **2.0.0**，服务 **102 个**。

---

## 一、代码结构（五件套）

改一个新功能必须同时动这些文件（缺一个会导致服务注册失败或三方不一致）：

| 文件 | 职责 |
|---|---|
| `client/const.py` | `URL_<FEATURE>` 常量 + `RAW_API_ENDPOINTS` 白名单 |
| `client/classes.py` | 数据类（解析 API 返回）、`InvalidActionError` 等异常 |
| `client/huaweiapi.py` | `HuaweiApi` 高层方法（get/set/collect/download…）|
| `services.yaml` | HA 服务 schema（name/description/fields/selector）|
| `services.py` | `ServiceName` 枚举 + `ServiceDescription` + handler `_async_<name>` + dispatch 分支 |

其他：`client/coreapi.py`（HTTP/认证/CSRF 底层）、`client/crypto.py`（SCRAM + RSA）、
`switch.py`/`sensor.py`/`button.py`/`binary_sensor.py`/`select.py`（实体平台）、
`update_coordinator.py`（轮询与数据装配）。

### 强制：三方一致性
```
ServiceName 枚举  ==  services.yaml  ==  ServiceDescription
```
现为 **102 == 102 == 102**，差集必须为空。改完跑：
```python
# 枚举 vs yaml vs 注册，三者差集应为空
```

---

## 二、逆向方法论

### 1. 静态分析（首选，零风险，不耗 session）

Web UI 是 webpack SPA，前端 JS 含全部 API 路径与调用逻辑。

```bash
# 版本号
curl -s http://<ROUTER_IP>/html/index.html | grep -o 'main.js?v=[0-9.]*[A-Za-z0-9-]*'
# 入口
curl -s "http://<ROUTER_IP>/js/main.js?v=<版本>" -o main.js
# 全部 chunk（0=common, 1=wlanauthorizeredirect，其余按 id）
curl -s "http://<ROUTER_IP>/html/js/<id>.<hash>.js" -o chunk_<id>.js
```
hash 从 main.js 的 `s.src=function(t){... "c4e0bd8e7a1df4154e9e.js"}` 取（本固件）。

从 main.js 提映射表（**186 项**）与 payload：
```python
import re
d = open('main.js', encoding='utf-8', errors='ignore').read()
# 映射: name -> "system/xxx" 等
re.findall(r'(\w+):"((?:system|ntwk|hilink|device|bsp|app|service|language)/[^"]+)"', d)
# 调用: dispatch("commonPost",{name:"xxx",data:...})
re.findall(r'dispatch\("(commonGet|commonPost|multiGets)",\{name:"(\w+)"', d)
```
URL 解析规则：`a(t) = s[t] ? "/api/"+s[t] : t` —— 查不到映射就把 name 当路径。

### 2. 只读探测定性（决定能不能做）

```
GET/POST 看真实 HTTP 状态码 → 200+有数据 = 可做；404 = 本机型无
```
- 用 `_get_raw` 看状态码，**绝不用 `core.get()`**（它把 404 当未授权会自动重登录 → 打满 session）
- 循环内 `sleep(1.5)`；结束 `disconnect()`
- 路由器**仅 2 个并发 session**；HA 集成常驻占 1 个 → 探测只剩 1 个；限流后等 2-3 分钟

### 3. ★ 铁律：前端有页面 ≠ 能用

Web UI 是**多机型共用代码**，大量页面在本固件是"死页"。
**必须真机验证**，静态分析只能给路径不能给可用性。

---

## 三、本机型已定性清单（WS8000-16 / 6.1.0.20，2026-10-02 实测）

**这些都是踩过的坑，别再重复试。**

| 端点 | 结论 | 证据 |
|---|---|---|
| `ntwk/portforwarding` | ❌ 404 | 只有 TR-069 `portmapping` 一套，无需"能力位分流" |
| `ntwk/timecontrol` | ❌ 404 | 本机型不支持 |
| `ntwk/guest_network_resttime` | ❌ 404 | 无此端点 |
| `ntwk/wps_switch` / `ntwk/wlanwps` | ❌ 404 | 前端硬编码 `isSupportWps=false` |
| `ntwk/ipcapture` / `ntwk/mirror` | ❌ 404 | mirror 页是死页（抓包流做不了）|
| `poweroff` / `powerofflist` / `dps_switch` | ❌ 404 | `isSupportPowerKey=0` |
| `sshRemoteState` / `telnetRemoteState` / `wanremoteaccess` / `remoteaccesslist` | ❌ 前端禁用 | `isSupportSSH/Telnet/Https: !1` |
| `bsp/nfc_switch` | ❌ 404 | `isSupportNFC=0` |
| `ntwk/urlfilter` | ⚠️ 200 但空数组 | 能力位=0，别误判可用 |
| `ntwk/dlna` / `app/usersamba` / `netdisk*` | ⚠️ 需 USB 盘 | 本机未接 |

**已逆向完成且可用**：
- 诊断日志：`diagnose_crash` POST `{CrashAction:InfoCollect, Mac, IsMainDev}` + `action=update`
  → 轮询 `DiagnosticsState`: `Requested → ExecLuaSuccess`（实测 18s）
  → 下载 `system/diagnose_crash_resultdownload`（624-635 KB tar）
- 配置导出：`GET system/downloadcfg`（86 KB 加密 .conf）
- 配置导入：`POST device/uploadconfigfile` multipart
  `csrf_token`(="csrf:"+param+token) / `textfield` / `configurefilename`
- WPS 三模式：`{WpsMode:"pbc"}` / `{WpsMode:"client-pin",ClientPinCode}` / `{WpsMode:"ap-pin",ApPinType}`
- WiFi 射频：`system/diagnose_wlan_basic?type=1`(2.4G) `?type=2`(5G)

---

## 四、已知代码陷阱

1. **`cv.IsFilePath` 在新版 HA 已移除** → 用 `cv.string` + 服务层路径校验
2. **`InvalidActionError` 定义在 `client/huaweiapi.py`**，不是 `client/classes.py`；`services.py` 需 `from .client.huaweiapi import InvalidActionError`
3. **新增 URL 常量要记得加进 `huaweiapi.py` 的 import 区**（漏了会 NameError，只在调用时暴露）
4. **services.yaml 的 selector 必须写成 `selector:\n  text:`**（写成裸 `text` 会解析成字符串，hassfest 报 "required key not provided at ...target"）
5. **改 `.storage/core.config_entries` 必须停容器**（HA 关闭时写回覆盖）；且改完要同步 `origin/main`
6. **session 限流**：探测脚本与 HA 集成互抢，测试时如需独占可临时 disable config entry，测完恢复

---

## 五、开发流程（必走 PR）

```
从 main 开分支 → commit → push → PR → CI(hassfest/HACS/validate/pr-guard) → 维护者合并
```
- 一个 PR 一件事；标题 `<type>: <描述>`（type: feat/fix/refactor/chore/docs/ci）
- **不自合、不擅自 bump 版本**；版本 bump 单独 PR
- 版本号语义：bug=patch / 向后兼容新功能=minor / 破坏性=major（先问）
- 详见 `ha-custom-component-contributing`（PR 模板、发版、**untagged 陷阱**）

---

## 六、发版注意（踩过）

- CI 用 `gh release create --draft --verify-tag`：**不要加 `--target`**（会导致 tag 存在也绑成 `untagged-<hash>`）
- 2.0.0 发布时就命中了这个坑，靠 `PATCH /releases/{id} {"tag_name":"v2.0.0"}` 修复
- 发布后用 `releases/tags/<tag>` 复验绑定，列表接口有最终一致性需重试

---

## 七、相关

- `huawei-router-control` — 使用方向（控制/检查）
- `huawei-router-standalone` — 独立脚本（不依赖 HA）
- `ha-custom-component-contributing` — PR/发版规范
