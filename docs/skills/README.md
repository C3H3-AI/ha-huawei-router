# 配套 Skill

本目录存放与本项目配套的各方向 skill。它们是本机 AI 助手的指令文档，放在仓库里做版本化管理，便于换机器时直接取用。

## 安装到本机

```bash
cp -r docs/skills/huawei-router-<name> ~/.dsh/skills/
```

三个方向（互相独立，按需选用）：

| Skill | 方向 | 用途 |
|---|---|---|
| `huawei-router-control` | 使用 | 通过 HA 集成控制和检查路由器：看状态/健康、WiFi、设备管理、网络配置、诊断日志、配置备份 |
| `huawei-router-standalone` | 独立 | 不依赖 HA，用 `scripts/router_cli.py` 直连路由器 LAN API（含 logout、端点短名表、破坏性操作拦截）|
| `huawei-router-dev` | 逆向/开发 | 挖新端点、逆向 payload、给集成新增功能（五件套）、已实测定性的端点清单 |

## Skill 里记了什么

**不是服务清单**——服务 schema 由 Home Assistant 动态下发（当前 102+ 个），skill 只写 HA 不知道的判断层：

1. **控制路径优先级**：先看实体 → 调服务 → 兜底 `api_get`/`api_set`
2. **硬红线**：路由器 2 session 限流（探测用 `_get_raw`、间隔 1.5s、限流等 2-3 分钟）；危险操作（导入配置=覆盖+重启 60s、端口映射级联误删）；改 `.storage` 必须停容器
3. **本机型做不到清单**：16 项，每项带 404/硬编码证据（子路由重启、NFC、时间控制、WPS、抓包流、SSH 远程管理等）
4. **铁律**：前端有页面 ≠ 能用（Web UI 多机型共用代码，大量死页）

## 维护

skill 中的结论依赖真机验证。当以下情况发生时需更新：

- 固件升级（端点可用性可能变化）
- 集成新增/删除服务（数量、schema 变化）
- 换了路由器型号（机型限制清单失效）

相关：本仓库根目录的 `FEATURES.md`（功能清单）、`VERIFICATION.md`、`COVERAGE.md` 记录了验证过程与覆盖终审结果。
