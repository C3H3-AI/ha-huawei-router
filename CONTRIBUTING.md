# 贡献指南

感谢你愿意改进 `ha-huawei-router`。本文的规则**大部分由 CI 自动强制** ——
不是"最好这样"，而是"不这样会红"。

---

## TL;DR

```bash
git checkout main && git pull
git checkout -b fix/your-topic          # ★ 新分支，绝不从 main 直接改
# ... 改动 ...
python3 -m py_compile custom_components/huawei_router/*.py
git commit -m "fix(coreapi): 修正 Q6 固件的超时误判"
git push origin fix/your-topic
# 用仓库模板开 PR，标题 <类型>(<范围>): <描述>
```

**不要自己改 `manifest.json` 的版本号。** 版本号由维护者在发版时决定 ——
见下方「版本号谁说了算」。

---

## 分支命名

| 类型 | 分支名 | 说明 |
|---|---|---|
| 新功能 | `feat/<topic>` | 新增实体 / 服务 / 兼容型号 |
| 修 bug | `fix/<topic>` | 修正解析、超时、状态映射 |
| 重构 | `refactor/<topic>` | 不改外部行为 |
| 文档 | `docs/<topic>` | README / CONTRIBUTING |
| CI | `ci/<topic>` | workflow / 脚本 |
| 杂项 | `chore/<topic>` | 依赖、构建 |

**硬规则：PR 合并后不得继续在同一个分支上提交，也不得复用已被合并的分支。**

这条规则由 CI 强制（`pr guard` 会查该分支是否曾被已合并的 PR 使用过）。
踩过的坑：复用分支会让新提交卡在【已关闭 PR】的分支上无处可去，
只能另开一个 PR 补救，中途还容易建错分支又删掉。

---

## PR 标题格式（CI 强制，不合规直接失败）

```
<类型>(<范围>): <描述>
```

- **类型**：`feat` / `fix` / `refactor` / `docs` / `ci` / `chore` / `test` / `perf`
- **范围**：可选，小写。常用：`coreapi` / `huaweiapi` / `sensor` / `switch` /
  `config` / `services` / `translations` / `ci`
- **描述**：至少 4 个字符

CI 会按标题类型自动打 `type: <类型>` 标签，并按改动路径打 `area: <范围>`
标签 —— 这些标签决定 Release 正文的分组。

示例：

```
fix(coreapi): increase timeout and add browser headers for Q6 firmware
feat: add wan_reconnect service (PPPoE re-dial)
ci: 新增 release 流程与 PR 规范守卫
```

---

## 测试必须真的能失败

**没有失败能力的测试 = 装饰品。**

新增或修改检查逻辑（解析、兼容分支、标签规则、workflow 校验）时，
必须证明测试**真的会红**：

```bash
# 1. 在正确代码上跑 → 通过
python3 -m pytest tests/ -q

# 2. 把保护改回错误写法（注入 bug）

# 3. 确认测试确实失败 ★ 这步是关键
python3 -m pytest tests/ -q          # → 必须 failed

# 4. 恢复正确代码，再跑一遍 → 通过
```

### 本项目实测的教训

`pr_guard.py` 的 `AREA_RULES` 里曾写成：

```python
("area: brand", ("custom_components/huawei_router/brand/**")),   # ❌
```

`("x/**")` 是**字符串，不是元组**（少了尾逗号）。迭代它逐字符产出，
其中一个字符是 `'*'`，于是 `fnmatch(任意路径, '*')` **恒为真** ——
`area: brand` 标签会给**每一个** PR 都打上。

发现它靠的是**精确集合断言**：

```python
# ✅ 能发现：命中集合必须精确相等
assert set(got) == set(want)

# ❌ 发现不了：恒真
assert "area: brand" in labels
```

**结论**：断言要比较**精确集合**，不要用 `in` 做子串/成员判断就算完。

另有一条相关陷阱：**子串断言要剥掉注释**。注释里出现过的字符串会让
`assert "--verify-tag" in text` 恒为真 —— 那是假通过。

---

## 敏感信息

仓库是公开的。**绝不提交**：

- 路由器管理密码、Wi-Fi 密码
- 设备序列号、MAC 地址
- 公网 IP、DDNS 域名（如果指向你家）
- 任何 token / cookie

CI 会扫描**全部已跟踪文件**和**提交消息**（需维护者配置
`SENSITIVE_PATTERNS` secret）。提交消息是永久且公开的 ——
即使 force push 删除分支，GitHub 仍可按 SHA 直接访问该提交。

日志和截图贴到 Issue / PR 前请先打码。

---

## 版本号谁说了算

**维护者定版本号，贡献者不要自己 bump。**

| 改动 | 版本 |
|---|---|
| 仅修 bug | patch（1.12.1 → 1.12.2）|
| 向后兼容的新功能 | minor（1.12.1 → 1.13.0）|
| 破坏性变更 | major —— **先讨论** |

**常见误判**：内部重构（改 API、删兼容 shim）内部感觉"破了"，
但对用户是 minor。不要擅自升级 major。

### 发版流程（维护者视角）

```
改 manifest.json 的 version → 合并进 main
  ↓ 自动触发
1. Version Increment Check（严格递增，用 packaging.version）
2. Create ZIP
3. Create and push tag（★ 先建 tag —— GitHub 草稿不会自动建！）
4. Create draft release（--draft --verify-tag --generate-notes）
5. Verify tag exists
6. Verify release bound to tag  ★ 必须 —— tag 存在 ≠ 绑定正确
  ↓
维护者在 Releases 页面确认草稿 → Publish
```

**Release 正文由 CI 按 PR 标签自动生成**（`.github/release.yml`），
不要手写替换。正文质量 = PR 分类质量：标签打对了，正文就对。

**版本号是独立的 release PR** —— 不与功能改动混在同一个 PR 里。

---

## CI 检查项

| 检查 | 作用 | 不过怎么办 |
|---|---|---|
| `hassfest` | HA 官方结构校验 | 看报错，通常是 manifest / 翻译字段 |
| `HACS validate` | HACS 规范校验 | 通常是缺 `hacs.json` 字段或目录结构 |
| `lint & security` | 语法 / JSON / manifest / 敏感信息 | 按 `::error file=...` 定位 |
| `pr guard` | 标题格式、分支复用、自动打标签 | 改标题或换分支（见上） |

---

## 报告 > 补丁

CI 本身出错时（workflow 权限、tag 绑定失败等），正确做法是：

1. 精准诊断 —— 引用具体失败 step 和报错文本
2. 带证据 + 修复建议报告给维护者
3. 让维护者决定修 CI 还是用一次性 workaround

**不要偷偷绕开** —— 那会藏住缺陷，下次发版还会踩。

但"报告"不等于"只报告"：修 CI 缺陷本身是合法工作，只要它
① 单独一个 `ci:` PR、② 不动版本号、③ 带能真正失败的回归测试。

---

## 开发环境

```bash
# 语法自检（无需安装 HA）
python3 -m py_compile custom_components/huawei_router/*.py \
                      custom_components/huawei_router/client/*.py

# 本地跑 PR 守卫（不调 API、不退出非零）
GH_TOKEN=x REPO=c3h3-ci/ha-huawei-router REPO_OWNER=c3h3-ci PR_NUM=1 \
  HEAD_REF=fix/x TITLE="fix: 测试标题" BODY="Fixes #1" \
  python3 .github/scripts/pr_guard.py --dry-run
```

涉及实机验证的改动，请在 PR 里写明**测过哪些型号、哪些没测**。

---

## 许可

提交 PR 即表示你同意以本仓库的 [LICENSE](LICENSE) 授权你的贡献。