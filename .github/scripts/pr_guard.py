#!/usr/bin/env python3
"""PR 规范守卫 —— 把 CONTRIBUTING 里"靠人记得"的规则变成机器强制。

为什么需要它（ha-lixiang 2026-09-28 实测教训）
----------------------------------------------
CONTRIBUTING 早就写了「PR 合并后不得继续在同一个分支上提交」，还附了检查命令 ——
但**没有任何机制拦人**。结果同一次会话里，同一个分支被 PR #5 和 PR #7 先后使用：

    PR #5 合并后又往同一分支提交
      → 新提交卡在【已关闭 PR】的分支上，无处可去
      → 只能再开一个 PR 补救（中途还建错分支又删掉）

规则写了、案例也有，仍然违反 —— 因为规则只是文档，不是机制。

检查项
------
  ① 【失败】head 分支是否曾被合并过（复用已合并分支）
  ② 【失败】PR 标题是否符合 Conventional Commits
  ③ 【警告】是否关联 Issue（Fixes/Closes/Refs #N）
  ④ 按标题类型自动打 `type: <类型>` 标签
  ⑤ 按改动路径自动打 `area: <范围>` 标签

本地自测
--------
    GH_TOKEN=x REPO=o/r PR_NUM=1 HEAD_REF=feat/x REPO_OWNER=o \
        TITLE="feat: 测试" BODY="Fixes #1" python3 .github/scripts/pr_guard.py --dry-run

`--dry-run` 只打印不调 API、不退出非零，用于本地验证逻辑。
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")

#: 允许的标题类型（与 CONTRIBUTING「分支命名」表保持一致）
TYPES = ("feat", "fix", "refactor", "docs", "ci", "chore", "test", "perf")

TITLE_RE = re.compile(r"^(?P<type>" + "|".join(TYPES) + r")(\([a-z0-9_-]+\))?: .{4,}$")

ISSUE_RE = re.compile(
    r"\b(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?|refs?)\s*:?\s*#\d+",
    re.IGNORECASE,
)


def api(path: str, token: str, method: str = "GET", payload: dict | None = None):
    url = path if path.startswith("http") else f"{API}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        body = resp.read()
        return json.loads(body) if body else {}


def _gha(level: str, msg: str) -> None:
    """GitHub Actions 注解（本地运行时降级为普通输出）。"""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::{level}::{msg}")
    else:
        print(f"[{level}] {msg}")


def check_branch_not_reused(repo: str, owner: str, head: str, pr_num: int,
                           token: str, dry: bool) -> bool:
    """① 该分支是否已被【其它】已合并的 PR 用过。"""
    print(f"① 分支复用检查：{head}（本 PR #{pr_num}）")
    if dry:
        print("   [dry-run] 跳过 API 查询")
        return True
    try:
        prs = api(f"/repos/{repo}/pulls?head={owner}:{head}&state=closed&per_page=100", token)
    except Exception as err:  # noqa: BLE001
        _gha("warning", f"无法查询分支历史 PR（{err}），跳过该检查")
        return True

    reused = [
        p for p in prs
        if p.get("merged_at") and p.get("number") != pr_num
    ]
    if not reused:
        print("   ✅ 未复用已合并分支")
        return True

    lines = [f"#{p['number']} {p.get('title', '')[:50]} (merged {p['merged_at'][:10]})"
             for p in reused]
    _gha("error", f"❌ 分支 '{head}' 已被合并过的 PR 使用过 —— CONTRIBUTING 禁止复用已合并分支")
    print("\n已合并的 PR：")
    for ln in lines:
        print(f"    {ln}")
    print(
        "\n为什么禁止：\n"
        "  · PR 的 diff 会带上历史提交，review 变难\n"
        "  · 实测：复用分支会让新提交卡在【已关闭 PR】的分支上，\n"
        "    只能另开 PR 补救（ha-lixiang PR #5 → PR #7 就是这么来的）\n"
        "\n正确做法：\n"
        "  git checkout main && git pull\n"
        "  git checkout -b <新分支名>\n"
    )
    return False


def check_title(title: str) -> bool:
    """② 标题格式。"""
    print(f"② 标题格式检查：{title}")
    m = TITLE_RE.match(title or "")
    if m:
        print("   ✅ 格式正确")
        return True
    _gha("error", f"❌ PR 标题不符合 Conventional Commits：{title}")
    print(
        "\n要求：<类型>(<范围>): <描述>\n"
        f"  类型：{' / '.join(TYPES)}\n"
        "  范围：可选，小写（如 coreapi / sensor / ci）\n"
        "  描述：至少 4 个字符\n"
        "\n示例：\n"
        "  fix(coreapi): increase timeout for Q6 firmware\n"
        "  ci: 新增 PR 规范守卫\n"
    )
    return False


def check_issue_link(title: str, body: str) -> bool:
    """③ Issue 关联（仅警告）。"""
    print("③ Issue 关联检查")
    if ISSUE_RE.search(f"{title}\n{body or ''}"):
        print("   ✅ 已关联 Issue")
        return True
    _gha("warning", "未关联 Issue —— 若本次改动对应某个 Issue，请写 Fixes #N")
    print("   （仅警告，不阻断。关联后 Issue 关闭时会自动留痕。）")
    return True


def apply_type_label(repo: str, pr_num: int, title: str, token: str, dry: bool) -> None:
    """④ 按标题类型打标签。"""
    m = TITLE_RE.match(title or "")
    if not m:
        print("④ 标题不合规，跳过打标签")
        return
    label = f"type: {m.group('type')}"
    print(f"④ 打标签：{label}")
    if dry:
        print("   [dry-run] 跳过 API 调用")
        return
    _apply_labels(repo, pr_num, [label], token)


#: 改动路径 → area 标签（让 reviewer 一眼看出动了哪一层）
#: ★ 本仓库的层级划分对应 custom_components/huawei_router/ 的实际结构
AREA_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("area: ci",           (".github/**", "hacs.json")),
    ("area: docs",         ("README.md", "CONTRIBUTING.md")),
    ("area: translations", ("custom_components/huawei_router/translations/**",)),
    # ★ 单元素元组必须有尾逗号！写成 ("x/**") 是【字符串】不是元组，
    #   迭代它会逐字符产出，其中一个字符是 '*' → fnmatch(任意路径, '*') 恒为真
    #   → 这个标签会给【每个】PR 都打上。实测踩过。
    ("area: brand",        ("custom_components/huawei_router/brand/**",)),
    ("area: api",          ("custom_components/huawei_router/client/**",)),
    ("area: platforms",    ("custom_components/huawei_router/sensor.py",
                            "custom_components/huawei_router/binary_sensor.py",
                            "custom_components/huawei_router/switch.py",
                            "custom_components/huawei_router/button.py",
                            "custom_components/huawei_router/select.py",
                            "custom_components/huawei_router/device_tracker.py",
                            "custom_components/huawei_router/event.py")),
    ("area: config",       ("custom_components/huawei_router/config_flow.py",
                            "custom_components/huawei_router/options.py")),
    ("area: services",     ("custom_components/huawei_router/services.py",
                            "custom_components/huawei_router/ha_services.py",
                            "custom_components/huawei_router/services.yaml")),
    ("area: core",         ("custom_components/huawei_router/__init__.py",
                            "custom_components/huawei_router/update_coordinator.py",
                            "custom_components/huawei_router/const.py",
                            "custom_components/huawei_router/helpers.py",
                            "custom_components/huawei_router/classes.py",
                            "custom_components/huawei_router/utils.py",
                            "custom_components/huawei_router/manifest.json")),
)


def _match_any(path: str, patterns: tuple[str, ...]) -> bool:
    """支持 `dir/**` 前缀与 fnmatch 通配的路径匹配。"""
    import fnmatch
    for pat in patterns:
        if pat.endswith("/**"):
            if path.startswith(pat[:-3] + "/"):
                return True
        elif fnmatch.fnmatch(path, pat):
            return True
    return False


def apply_area_labels(repo: str, pr_num: int, token: str, dry: bool) -> None:
    """⑤ 按改动路径打 area 标签。"""
    if dry:
        print("⑤ area 标签：[dry-run] 跳过")
        return
    try:
        files = api(f"/repos/{repo}/pulls/{pr_num}/files?per_page=100", token)
    except Exception as err:  # noqa: BLE001
        _gha("warning", f"无法取改动文件列表（{err}），跳过 area 标签")
        return

    paths = [f.get("filename", "") for f in files]
    labels = [label for label, pats in AREA_RULES
              if any(_match_any(p, pats) for p in paths)]
    print(f"⑤ area 标签：{len(paths)} 个文件 → {labels or '无匹配'}")
    if labels:
        _apply_labels(repo, pr_num, labels, token)


def _apply_labels(repo: str, pr_num: int, labels: list[str], token: str) -> None:
    """幂等地创建并附加标签（422 = 标签已存在，忽略）。"""
    for label in labels:
        try:
            try:
                api(f"/repos/{repo}/labels", token, "POST",
                    {"name": label, "color": "ededed"})
            except urllib.error.HTTPError as err:
                if err.code != 422:
                    raise
            api(f"/repos/{repo}/issues/{pr_num}/labels", token, "POST",
                {"labels": [label]})
        except Exception as err:  # noqa: BLE001
            _gha("warning", f"打标签 '{label}' 失败（不影响合并）：{err}")
    print(f"   ✅ 已打标签: {', '.join(labels)}")


def main() -> int:
    dry = "--dry-run" in sys.argv
    env = os.environ
    repo = env.get("REPO", "owner/repo")
    owner = env.get("REPO_OWNER", repo.split("/")[0])
    pr_num = int(env.get("PR_NUM") or 0)
    head = env.get("HEAD_REF", "")
    title = env.get("TITLE", "")
    body = env.get("BODY", "")
    token = env.get("GH_TOKEN", "")

    print("=" * 60)
    print("  PR 规范守卫")
    print("=" * 60)

    ok = True
    ok &= check_branch_not_reused(repo, owner, head, pr_num, token, dry)
    print()
    ok &= check_title(title)
    print()
    check_issue_link(title, body)
    print()
    apply_type_label(repo, pr_num, title, token, dry)
    print()
    apply_area_labels(repo, pr_num, token, dry)

    print("=" * 60)
    if ok:
        print("  ✅ 守卫通过")
    else:
        print("  ❌ 守卫未通过 —— 见上方 ::error:: 说明")
    print("=" * 60)
    return 0 if (ok or dry) else 1


if __name__ == "__main__":
    raise SystemExit(main())