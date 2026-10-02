---
name: huawei-router-control
description: 控制和检查华为凌霄 Q6 系列路由器（huawei_router HA 集成）。当用户要求查看路由器状态/健康、控制 WiFi（访客网络/WPS/射频）、管理连接设备（改名/限速/拉黑/黑白名单）、配置网络（端口映射/DHCP 保留/DDNS/DMZ/防火墙/UPnP）、下载诊断日志、或备份/恢复路由器配置时使用。也用于判断某个路由器功能在本机型是否可用。
---

# 华为路由器控制（huawei_router 集成）

**首要原则**：本 skill 提供**判断层**——能做/不能做/危险与否/怎么走最稳。
具体服务名和参数**不要从本文档背诵**，用 `ha_list_services` 动态发现（HA 服务注册表是唯一事实源；已注册 **102 个服务**，新增时工具自动更新）。

> 逆向/开发方向（挖端点、改集成代码）见独立的 `huawei-router-dev` skill。

---

## 一、控制路径（按优先级）

| 路径 | 适用 | 说明 |
|------|------|------|
| **1. HA 实体** | 看状态、开关 | sensor / binary_sensor / switch / device_tracker / button / event |
| **2. HA 服务** | 做动作 | `ha_call_service(domain="huawei_router", service=..., data={...})` |
| **3. 通用桥接** `api_get`/`api_set` | 白名单端点 | 83 个 `RAW_API_ENDPOINTS` 短名兜底 |

102 个服务前缀分布：`port_*`(8) `wifi_*`(7) `dhcp_*`(6) `ipv6_*`(5) `lan_*`(4) `guest_*`(4) `device_*`(4) `wan_*`(3) `diagnostics_*`(3) `auto_*`(3) `repeater_*`(3) `wps_*`(2) `config_*`(2) 等。

---

## 二、查看状态（只读）

**路由器健康**（v2.0，端点均真机验证）：

| 实体 | 实测值示例 |
|---|---|
| CPU / 内存使用率 | 0% / 46% |
| 在线设备数 / Mesh 节点数 | 97 / 5 |
| 2.4G / 5G 信道 | 1 / 44 |
| 8 个网口协商速率 | WAN 1000M；LAN2 仅 100M |
| NTP 同步状态 | on（cn.pool.ntp.org）|
| WAN 状态 / IP / IPv6 / 上下行速率 | 实时 |

**每台设备**：默认只留基础组（IP/MAC/连接类型/连接至）。要信号/速率/流量 → 集成 → 配置 → 设备传感器分组 勾选。

---

## 三、控制能力

| 类别 | 能做什么 |
|---|---|
| 设备管理 | 改名（≤64字符）、QoS 限速（100K~1G）、移除 |
| 端口映射/触发 | 增删改查 + 启停（TR-069 全套）|
| WiFi | 访客网络全套、多 SSID、WPS 开关+配对、双频优选、智能连接、定时提速、射频 |
| 网络 | DHCP 保留、LAN/DHCP、IPv6 WAN/LAN、DDNS、DMZ、防火墙、UPnP |
| 安全 | 黑白名单、防蹭网/防暴力破解、MAC 过滤 |
| 系统 | PPPoE 重拨、定时/立即重启、WiFi 扫描、中继、升级检查 |
| 诊断 | collect → status 轮询 → download（20-120 秒，实测 635 KB）|
| 配置 | `config_export`（86 KB .conf）/ `config_import`（**破坏性**）|

---

## 四、⚠️ 硬红线

### 1. session 限流（最易踩）
- 最多 **2 个并发 admin session**，超限报 `Too_Many_user`
- HA 集成常驻占 1 个 → 手动探测只剩 1 个
- 探测用 `_get_raw` 看状态码，**绝不用 `get()`**（它把 404 当未授权会自动重登录，批量探测瞬间打满）
- 循环内 `sleep(1.5)`；结束 `disconnect()`；限流后等 **2-3 分钟**

### 2. 危险操作（先确认 + 先备份）
| 操作 | 后果 |
|---|---|
| `config_import` | 覆盖全部设置 + 重启 60 秒，整屋断网。先 `config_export` |
| `device_remove` | 设备从列表消失 |
| 恢复出厂 | 集成有意未实现，不要尝试 |
| 删端口映射 | 可能级联删共享 Application（历史误删过生产 NAT 规则）|

顺序：新增 = 先建 Application → 再绑 portmapping；删除反向。**勿**逐条删 `applicationitems`（报 9003）。

### 3. 改 HA 配置必须停容器
HA 关闭时会把内存值写回覆盖修改：
```bash
docker stop <容器>; sudo python3 改文件; docker start <容器>
```

---

## 五、❌ 本机型做不到（有硬证据）

**Q6 网线版（WS8000-16，固件 6.1.0.20）实测：**

| 功能 | 证据 |
|---|---|
| 子路由单独重启 | 按钮坏；云端 `voiceReboot` 报文未解 |
| NFC | `bsp/nfc_switch` 404，`isSupportNFC=0` |
| 时间控制 | `timecontrol` 404 |
| 网址过滤 | `urlfilter` 200 但空数组 |
| 扁平端口转发 | `portforwarding` 404 |
| 访客时长 | `guest_network_resttime` 404 |
| WPS 管理 | `wps_switch`/`wlanwps` 404（硬编码 `isSupportWps=false`）|
| 抓包流/端口镜像 | `ipcapture`/`mirror` 404（死页）|
| 智能关机/硬件加速 | `poweroff`/`dps_switch` 404（`isSupportPowerKey=0`）|
| SSH/Telnet/HTTPS 远程管理 | 硬编码 `isSupportSSH/Telnet/Https: !1` |
| USB 共享（DLNA/Samba/网盘）| 需接盘，本机未接 |
| IPv6 独立开关 | `ipv6_enable` 能力位=0 |

**铁律：前端有页面 ≠ 能用**（Web UI 多机型共用代码，大量死页）。

---

## 六、常用配方

**诊断日志**（三段式异步）：
```
1. diagnostics_collect
2. 等 20-120 秒：diagnostics_status → {"state":"ExecLuaSuccess","result_ready":true}
3. diagnostics_download data={"path":"/config/www/diag.tar"} → /local/diag.tar 可访问
```

**改配置前备份**：`config_export data={"path":"/config/www/q6_backup.conf"}`

**限速**：
```
device_set_rate_limit data={"mac_address":"11:22:33:AA:BB:CC",
  "enabled":true,"upload_kbps":500,"download_kbps":2000}
```

---

## 七、相关 skill

- `huawei-router-dev` — 逆向/开发方向
- `huawei-router-external-access` — 外网访问（IPv6 直连 + DDNS-GO）
- `huawei-hilink-adapter` — 云端 HiLink（智慧生活）
