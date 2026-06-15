# Huawei Q6 Router — Home Assistant 自定义集成

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/C3H3-AI/ha-huawei-q6)](https://github.com/C3H3-AI/ha-huawei-q6/blob/main/LICENSE.md)

深度集成华为凌霄 Q6 系列路由器（含网线版、子母路由等 Mesh 网络），支持设备跟踪、流量监控、WiFi 管理、端口映射、时间控制等完整功能。

## 支持的设备

| 型号 | 类型 | 支持状态 |
|------|------|----------|
| 华为 Q6 网线版 (WS8000-16) | Mesh 主路由 | ✅ 已测试 |
| 华为 Q6 子路由 | Mesh 子路由 | ✅ 自动发现 |
| 华为 Q6 WiFi 版 | Mesh 主路由 | ⚠️ 理论兼容 |

> 其他华为凌霄/HiLink 路由器也可尝试使用。

---

## 功能总览

本集成提供 **8 大类实体**，全部通过配置选项控制开关：

### 1. 传感器（Sensors）

#### 全局传感器
| 实体 | 说明 |
|------|------|
| 总客户端数 | 当前连接到 Mesh 网络的活跃设备总数 |
| 客户端数 | 连接到主路由的活跃设备数 |
| 诊断 | 集成健康状态（主路由在线状态、各项计数） |
| 分组设备 | 按子路由器分组的设备列表（attribute 中含详细设备信息） |
| WAN 状态 | 互联网连接是否在线 |
| WAN IP 地址 | 公网 IPv4 地址 |
| WAN IPv6 地址 | 公网 IPv6 地址（含前缀长度） |
| WAN 下载/上传 | 当前 WAN 实时速率（Kbps） |
| UPnP 流量 | 已收/已发流量、已收/已发数据包、实时上下传速度 |
| 路由器 IP 地址 | 主路由 LAN 口 IP |
| 型号/序列号 | 路由器硬件信息 |
| 软件/硬件/HarmonyOS 版本 | 固件版本信息 |
| MAC 地址 | 主路由器 MAC 地址 |

#### 设备级传感器（每个连接设备）
| 实体 | 说明 |
|------|------|
| IP 地址 | 设备当前分配的局域网 IP |
| MAC 地址 | 设备物理地址 |
| 连接类型 | 有线/WiFi 2.4G/WiFi 5G |
| 信号强度 | WiFi 信号 dBm 值 |
| 上传/下载速度 | 设备实时上下传速率（kB/s） |
| 连接速率 | WiFi 连接速率（Mbps） |
| WiFi 频段 | 2.4GHz / 5GHz |
| 设备厂商 | 设备品牌识别 |
| 设备类型 | 设备分类（手机/PC/平板等） |
| 发送/接收流量 | 设备累计收发流量 |
| 家长控制 | 设备是否在家长控制下 |
| 连接至 | 设备连接到哪个路由器 |
| 运行时长 | 设备在线时长（时间戳+秒数） |

#### 子路由传感器（每个子路由器）
| 实体 | 说明 |
|------|------|
| 客户端数 | 该子路由下的活跃设备数 |
| 分组设备 | 该子路由下的设备列表 |
| IP 地址 / MAC 地址 | 子路由器的 IP 和 MAC |
| 运行时长 | 子路由器的运行时间 |

> **设备级传感器**支持"跳过离线设备"选项，开启后设备下线时自动清理实体。

---

### 2. 开关（Switches）

| 开关 | 说明 |
|------|------|
| **NFC** | 华为一碰连（HiConnect）的 NFC 功能开关 |
| **WiFi 802.11r** | 快速漫游（Fast Transition）开关 |
| **WiFi 6 TWT** | 目标唤醒时间（降低设备功耗）开关 |
| **访客网络** | 访客 WiFi 开关 |
| **WiFi 访问控制** | 全局 WiFi 黑白名单模式开关 |
| **设备 WiFi 访问** | 每个无线设备的上网权限开关（按设备显示） |
| **网址过滤** | 每个过滤规则的启用/禁用开关 |
| **端口映射** | 每个端口映射规则的启用/禁用开关 |
| **时间控制** | 每个上网时间控制规则的启用/禁用开关 |

---

### 3. 按键（Buttons）

| 按键 | 说明 |
|------|------|
| **重启** | 主路由重启按键 |
| **重启（子路由）** | 每个子路由的重启按键（动态创建） |

> 子路由按键在子路由上线时自动创建，下线时自动清理。

---

### 4. 二进制传感器（Binary Sensors）

| 实体 | 说明 |
|------|------|
| **互联网连接** | WAN 是否在线（绿色=连接，灰色=断开） |

---

### 5. 选择器（Selects）

| 选择器 | 说明 |
|------|------|
| **WiFi 访问控制模式** | 黑白名单切换 |
| **区域** | 设备所属区域（用于 zone 自动化） |

---

### 6. 设备追踪（Device Tracker）

开启后，每个连接设备自动出现在 Home Assistant 的设备列表中，支持：
- 显示设备当前位置
- Zone 自动化（到家/离家触发）
- 设备历史轨迹

---

### 7. 事件（Events）

| 事件 | 触发条件 |
|------|----------|
| **路由器** | 子路由上线 / 下线 |
| **设备** | 设备连接 / 断开 / 在不同路由器间移动 |

可用于自动化场景，例如"某设备连接到子路由时发送通知"。

---

### 8. 服务（Services）

通过开发者工具 → 服务调用：

| 服务 | 说明 |
|------|------|
| `huawei_router.whitelist_add` | 添加设备 MAC 到白名单 |
| `huawei_router.blacklist_add` | 添加设备 MAC 到黑名单 |
| `huawei_router.whitelist_remove` | 从白名单移除设备 |
| `huawei_router.blacklist_remove` | 从黑名单移除设备 |
| `huawei_router.guest_network_setup` | 配置访客网络（开关/SSID/时长/加密/密码） |

---

## Sonoff 设备自动关联（核心技术实现）

本集成提供**智能设备合并**功能，自动将华为路由器发现的设备与 Sonoff/eWeLink 集成的设备关联合并，实现统一设备管理。

### 功能概述

当同时安装了 **Sonoff 集成** 和 **华为路由器集成** 时：
- Sonoff 设备卡片上会同时显示 Sonoff 的开关/传感器 + 华为路由器的 WiFi 开关和设备追踪
- 避免同一物理设备在 Home Assistant 中显示为两个独立设备

### 技术实现原理

#### 1. 双数据源设计

| 数据源 | 优先级 | 获取方式 | 说明 |
|--------|--------|----------|------|
| `hass.data['sonoff']` | 高 | 运行时内存读取 | 从 Sonoff 集成实时获取 device_id → IP 映射，零 IO 开销 |
| `/config/.storage/sonoff/*.json` | 低 | 文件读取 | 回退数据源，定期缓存（20次更新周期） |

**代码实现**：[update_coordinator.py#L2662-L2759](file:///D:/ai-hub/integrations/huawei_router/custom_components/huawei_router/update_coordinator.py#L2662-L2759)

#### 2. 关联匹配流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sonoff 自动关联流程                           │
├─────────────────────────────────────────────────────────────────┤
│  1. 构建 IP → MAC 映射表                                         │
│     从华为路由器 connected_devices 获取所有在线设备的 IP 和 MAC    │
│                                                                 │
│  2. 获取 Sonoff device_id → IP 映射                              │
│     优先从 hass.data['sonoff'] 获取（实时）                       │
│     若失败则从存储文件读取（回退）                                 │
│                                                                 │
│  3. IP 桥接匹配                                                  │
│     Sonoff device_id → IP → MAC → 华为路由器设备                  │
│                                                                 │
│  4. 设备合并操作                                                 │
│     - 更新 Sonoff 设备的 connections，添加 MAC                   │
│     - 将华为路由器实体迁移到 Sonoff 设备                          │
│     - 合并 identifiers，保留华为路由器标识                        │
│     - 删除空的华为路由器设备                                      │
│     - 恢复 Sonoff 设备原始名称（防止被覆盖）                       │
└─────────────────────────────────────────────────────────────────┘
```

**代码实现**：[update_coordinator.py#L2851-L2945](file:///D:/ai-hub/integrations/huawei_router/custom_components/huawei_router/update_coordinator.py#L2851-L2945)

#### 3. 核心数据结构

```python
# hass.data["sonoff"] 结构
{
    entry_id: XRegistry,  # Sonoff 集成的注册表对象
    ...
}

# Sonoff 存储文件结构（/config/.storage/sonoff/*.json）
{
    "deviceid": "100123456789",
    "params": {
        "localip": "192.168.3.100",
        ...
    },
    ...
}
```

#### 4. 合并策略

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 更新 connections | 将 MAC 添加到 Sonoff 设备的 connections |
| 2 | 迁移实体 | 将华为路由器创建的 WiFi 开关、device_tracker 等实体迁移到 Sonoff 设备 |
| 3 | 合并 identifiers | 添加 `(huawei_router, MAC)` 到 Sonoff 设备的 identifiers |
| 4 | 删除空设备 | 删除华为路由器创建的空设备 |
| 5 | 恢复名称 | 从 Sonoff 存储文件恢复原始设备名称 |

#### 5. 性能优化

- **缓存机制**：存储文件读取结果缓存，每 20 次更新周期刷新一次
- **零 IO 优先**：优先使用 `hass.data['sonoff']` 的内存数据
- **跳过已关联**：已合并的设备不会重复处理
- **异常处理**：`suppress_update_exception` 装饰器确保关联失败不影响主流程

### 使用场景

#### 场景1：Sonoff 智能开关

用户有一个 Sonoff 智能开关，同时连接到华为路由器：
- **合并前**：两个独立设备卡片
  - Sonoff 设备：显示开关实体
  - 华为路由器设备：显示 WiFi 开关、信号强度、流量传感器
- **合并后**：一个统一设备卡片
  - 包含 Sonoff 的开关实体
  - 包含华为路由器的 WiFi 开关、信号强度、流量传感器

#### 场景2：自动化联动

结合两个集成的数据创建更智能的自动化：

```yaml
automation:
  - trigger:
      # 当设备连接到特定子路由时
      platform: event
      event_type: huawei_router.device_connected
      event_data:
        router_name: "客厅子路由"
    condition:
      # 且该设备是 Sonoff 智能插座
      condition: device
      device_id: device.sonoff_smart_plug
    action:
      - service: notify.persistent_notification
        data:
          message: "智能插座已连接到客厅路由"
```

### 配置选项

| 选项 | 默认 | 说明 |
|------|------|------|
| 自动关联设备 | ✅ | 是否启用 Sonoff 设备自动关联功能 |

> 在集成配置页面可调整此选项。

---

## 配置选项

添加集成后，点击配置可调整以下选项：

| 选项 | 默认 | 说明 |
|------|------|------|
| 数据更新间隔 | 30秒 | 轮询频率 |
| 路由器客户端传感器 | ✅ | 显示子路由客户端数、分组设备等 |
| 设备标签统计 | ✅ | 客户端传感器中的 guest/hilink/wireless/lan 分类计数 |
| 设备追踪 | ✅ | 是否创建设备追踪实体 |
| 设备区域 | ✅ | 是否启用区域选择器 |
| WiFi 访问开关 | ✅ | 是否为每个设备创建 WiFi 访问开关 |
| 网址过滤开关 | ✅ | 是否显示网址过滤开关 |
| 端口映射开关 | ✅ | 是否显示端口映射开关 |
| 时间控制开关 | ✅ | 是否显示时间控制开关 |
| 跳过离线设备 | ✅ | 离线设备的实体是否自动清理 |
| 事件实体 | ✅ | 是否启用设备连接事件 |
| 自动关联设备 | ✅ | 是否自动将 Sonoff 设备与华为路由器设备合并 |

---

## 安装

### 方法一：通过 HACS（推荐）

1. 打开 HACS → 集成
2. 点击右上角 `⋮` → `自定义存储库`
3. 添加仓库地址：`https://github.com/C3H3-AI/ha-huawei-q6`
4. 类别选择：`插件`
5. 搜索 **Huawei Q6 Router** 并安装
6. 重启 Home Assistant

### 方法二：手动安装

```bash
# 下载 custom_components/huawei_router 目录
# 放入 Home Assistant 配置目录的 custom_components/ 下
```

---

## 首次配置

1. **设置** → **设备与服务** → **添加集成**
2. 搜索 **Huawei Q6 Router**
3. 输入以下信息：
   - **主机**：`192.168.3.1`（路由器 LAN IP）
   - **用户名**：`admin`
   - **密码**：路由器后台密码
4. 点击 **提交**，完成后根据需要调整配置选项

---

## 自动化示例

### 设备连接通知

```yaml
automation:
  - trigger:
      platform: event
      event_type: huawei_router.device_connected
    action:
      - service: notify.persistent_notification
        data:
          title: "设备已连接"
          message: "{{ trigger.event.data.device_name }} 连接到网络"
```

### 访客网络定时开关

```yaml
automation:
  - trigger:
      at: "23:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.huawei_q6_router_guest_network
```

### 子路由离线告警

```yaml
automation:
  - trigger:
      platform: event
      event_type: huawei_router.router_removed
    action:
      - service: notify.persistent_notification
        data:
          title: "子路由离线"
          message: "{{ trigger.event.data.router_name }} 已离线"
```

---

## 故障排查

### 集成添加失败
- 确认路由器用户名/密码正确
- 确认 Home Assistant 可以访问路由器 IP（同一局域网）
- 检查路由器是否开启了"远程管理"或"HNC"功能

### 传感器显示"不可用"
- 检查路由器是否在线
- 查看 Home Assistant 日志中是否有认证错误
- 部分功能（如 NFC、时间控制）需要在路由器后台开启对应功能

### 子路由没有重启按键
- 子路由需要先在线，重启按键才会动态创建
- 确认数据更新间隔不要太长

---

## 更新日志

### v1.10.0
- 🐛 **修复主路由重启按键缺失**：华为 Q6 网线版主路由之前没有重启按键，现在已修复
- 🧹 **清理冗余代码**：移除注释掉的子路由 API 创建逻辑
- 🧹 **移除工具脚本**：删除开发辅助脚本
- 📦 **新增 ha_services.py**：独立服务模块

---

## 致谢

本集成基于 [vmakeev/huawei_mesh_router](https://github.com/vmakeev/huawei_mesh_router) 修改而来。

---

## 许可证

MIT License
