"""Workflow / 流程守卫测试。

背景
----
本仓库此前的发布是纯手工的：改版本号 → 打 tag → 在 GitHub UI 建 Release。
踩过的坑都写进了 CONTRIBUTING，但**规则只是文档，不是机制**。

这里把关键性质固化成测试，防止以后被改坏。每条断言都对应一个真实事故：

  · `--target` 会让 tag 存在也照样绑成 `untagged-<hash>`（HACS 收不到更新）
  · 草稿 Release 不会自动建 tag
  · release.yml 漏掉某个 type: 标签 → 该 PR 掉进"其他"兜底分组
  · AREA_RULES 写成 `("x/**")` 而非 `("x/**",)` 是字符串 →
    迭代逐字符产出，`'*'` 让 fnmatch 恒真 → 标签给每个 PR 都打上

**没有失败能力的测试 = 装饰品。** 每条断言的写法都确保能真的红：

  · 命令行断言用 `_cmd_lines()` 剥掉注释（注释里出现过同名字符串，
    直接 `in` 会恒真 —— 假通过）
  · area 匹配用**精确集合比较**，不用 `in`
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WF_DIR = ROOT / ".github/workflows"
DRAFT = WF_DIR / "draft-release.yml"
GUARD_WF = WF_DIR / "pr-guard.yml"
VALIDATE = WF_DIR / "validate.yml"
RELEASE_RL = ROOT / ".github/release.yml"
GUARD_PY = ROOT / ".github/scripts/pr_guard.py"
DOMAIN = "huawei_router"


def _yaml():
    return pytest.importorskip("yaml")


def _load(path: Path, name: str):
    """按文件路径加载模块（不依赖包结构）。"""
    assert path.exists(), f"{path} 不存在"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _wf(path: Path) -> dict:
    assert path.exists(), f"{path.name} 不存在"
    return _yaml().safe_load(path.read_text(encoding="utf-8"))


def _steps(path: Path, job: str | None = None) -> list[dict]:
    wf = _wf(path)
    jobs = wf["jobs"]
    return jobs[job]["steps"] if job else [s for j in jobs.values() for s in j["steps"]]


def _run_text(path: Path, job: str | None = None) -> str:
    return "\n".join(s.get("run", "") for s in _steps(path, job))


def _cmd_lines(path: Path, job: str | None = None) -> list[str]:
    """只取**真实命令行**，剥掉注释行。

    ★ 关键：注释里也会出现 `gh release create` / `--target` 这类字符串，
    直接对全文做 `in` 断言会恒为真 —— 那是假通过。
    """
    out = []
    for ln in _run_text(path, job).splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def _cmd_text(path: Path, job: str | None = None) -> str:
    return "\n".join(_cmd_lines(path, job))


# ═══════════════════════════════════════════════════════════════════════════
#  draft-release.yml —— 触发条件与结构
# ═══════════════════════════════════════════════════════════════════════════

class TestDraftReleaseStructure:
    def test_exists_and_is_valid_yaml(self):
        wf = _wf(DRAFT)
        assert wf["name"] == "Auto Release Draft"
        assert wf["permissions"]["contents"] == "write"

    def test_triggers_on_main_manifest_push(self):
        wf = _wf(DRAFT)
        on = wf.get("on") or wf.get(True)
        push = on["push"]
        assert "main" in str(push["branches"])
        # 必须盯着本集成的 manifest，且加 workflow_dispatch 兜底
        assert any(f"{DOMAIN}/manifest.json" in p for p in push["paths"])
        assert "workflow_dispatch" in on

    def test_fetch_depth_zero(self):
        """浅克隆会让版本比较和 generate-notes 都失效。"""
        wf = _wf(DRAFT)
        checkout = wf["jobs"]["build-and-draft"]["steps"][0]
        assert checkout["with"]["fetch-depth"] == 0


# ═══════════════════════════════════════════════════════════════════════════
#  版本号比较
# ═══════════════════════════════════════════════════════════════════════════

class TestVersionCheck:
    def test_uses_packaging_not_string_compare(self):
        """字符串比较会判错 "1.12.10" < "1.12.9"。"""
        txt = _run_text(DRAFT)
        assert "from packaging import version" in txt
        assert "version.parse" in txt

    def test_compares_against_latest_tag(self):
        txt = _run_text(DRAFT)
        assert 'git tag -l "v*"' in txt
        assert "compare_result=skip" in txt

    def test_reads_the_right_manifest(self):
        assert f"custom_components/{DOMAIN}/manifest.json" in _run_text(DRAFT)

    def test_sets_prerelease_flag(self):
        assert "is_prerelease=true" in _run_text(DRAFT)


# ═══════════════════════════════════════════════════════════════════════════
#  tag 必须先于草稿 Release 创建（坑 2）
# ═══════════════════════════════════════════════════════════════════════════

class TestTagCreatedBeforeDraft:
    def _names(self) -> list[str]:
        return [s.get("name", "") for s in _steps(DRAFT)]

    def test_tag_step_before_release_step(self):
        names = " | ".join(self._names())
        assert names.index("Create and push tag") < names.index("Create draft release")

    def test_pushes_the_tag(self):
        txt = _run_text(DRAFT)
        assert 'git tag "$TAG"' in txt
        assert 'git push origin "$TAG"' in txt

    def test_tag_step_is_idempotent(self):
        """重跑不能因 tag 已存在而失败。"""
        assert 'git rev-parse "$TAG"' in _run_text(DRAFT)


# ═══════════════════════════════════════════════════════════════════════════
#  ★ 核心：Release 必须真的绑在 tag 上（坑 3，ha-lixiang v1.2.4 事故）
# ═══════════════════════════════════════════════════════════════════════════

class TestReleaseTagBinding:
    def _create_cmd(self) -> list[str]:
        """只取 `gh release create` 起的那段**命令行**（行首才是命令）。"""
        lines = _cmd_lines(DRAFT)
        for i, ln in enumerate(lines):
            if ln.startswith("gh release create"):
                return lines[i:i + 10]
        raise AssertionError("找不到 gh release create 命令行")

    def test_no_target_flag(self):
        """带上 --target，tag 明明存在也可能绑成 untagged-<hash>。"""
        seg = "\n".join(self._create_cmd())
        assert "--target" not in seg, (
            "--target 会让 Release 绑成 untagged-<hash> 占位符 —— "
            "HACS 靠 release.tag_name 解析版本，绑错 = 用户收不到更新且零报错"
        )

    def test_uses_verify_tag(self):
        """--verify-tag：tag 远程不可见时直接失败，而不是静默建坏草稿。"""
        seg = "\n".join(self._create_cmd())
        assert "--verify-tag" in seg

    def test_is_draft_with_generated_notes(self):
        seg = "\n".join(self._create_cmd())
        assert "--draft" in seg
        assert "--generate-notes" in seg

    def test_has_binding_verification_step(self):
        """tag 存在 ≠ 绑定正确。必须单独校验绑定。"""
        names = [s.get("name", "") for s in _steps(DRAFT)]
        assert any("bound to tag" in n.lower() for n in names), (
            "缺少绑定校验步骤 —— tag 存在不代表 Release 绑在它上面"
        )

    def test_binding_check_avoids_tags_endpoint(self):
        """GET /releases/tags/{tag} 对草稿返回 404 —— 用它校验会永远误判未绑定。"""
        txt = _run_text(DRAFT)
        assert "/releases/tags/" not in txt

    def test_binding_check_retries_list_api(self):
        """GET /releases 列表是最终一致性的（实测 3 次丢 1 次）→ 必须重试。"""
        txt = _run_text(DRAFT)
        assert "for _ in 1 2 3 4 5" in txt
        assert "sleep 3" in txt
        assert "releases?per_page=" in txt

    def test_untagged_detection_uses_prefix_not_name(self):
        """startswith("v1.12.1") 会误匹配 v1.12.10 —— 必须认 untagged- 前缀。"""
        txt = _run_text(DRAFT)
        assert 'startswith("untagged-")' in txt

    def test_can_repair_a_broken_binding(self):
        """发现绑错时能 PATCH 修回来，而不是只报错。"""
        txt = _run_text(DRAFT)
        assert "-X PATCH" in txt
        assert 'tag_name="$TAG"' in txt

    def test_verify_tag_exists_step(self):
        txt = _run_text(DRAFT)
        assert "ls-remote" in txt


# ═══════════════════════════════════════════════════════════════════════════
#  ZIP 产物
# ═══════════════════════════════════════════════════════════════════════════

class TestZIPArtifact:
    def test_zips_the_component_dir(self):
        txt = _run_text(DRAFT)
        assert f"cd custom_components/{DOMAIN}" in txt
        assert "zip -r" in txt

    def test_artifact_name_matches_component(self):
        """HACS 要按集成域名拿到 zip。"""
        assert f"{DOMAIN}.zip" in _run_text(DRAFT)


# ═══════════════════════════════════════════════════════════════════════════
#  release.yml —— 覆盖 pr-guard 的全部类型
# ═══════════════════════════════════════════════════════════════════════════

class TestReleaseConfig:
    def _cats(self) -> list[dict]:
        return _yaml().safe_load(RELEASE_RL.read_text(encoding="utf-8"))["changelog"]["categories"]

    def test_exists_and_valid(self):
        assert RELEASE_RL.exists()
        assert len(self._cats()) >= 8

    def test_categories_cover_all_pr_guard_types(self):
        """漏掉的类型会让那些 PR 掉进"其他"兜底分组。"""
        guard = _load(GUARD_PY, "pg_cover")
        labels = {l for c in self._cats() for l in c["labels"] if l != "*"}
        missing = {f"type: {t}" for t in guard.TYPES} - labels
        assert not missing, f"release.yml 缺少这些分类标签: {sorted(missing)}"

    def test_wildcard_is_last(self):
        """兜底 '*' 放前面会吞掉后面所有分类。"""
        cats = self._cats()
        assert cats[-1]["labels"] == ["*"]
        for c in cats[:-1]:
            assert "*" not in c["labels"]


# ═══════════════════════════════════════════════════════════════════════════
#  pr_guard.py —— 守卫逻辑
# ═══════════════════════════════════════════════════════════════════════════

class TestGuardTitleFormat:
    @pytest.fixture(scope="class")
    @classmethod
    def guard(cls):
        return _load(GUARD_PY, "pg_title")

    @pytest.mark.parametrize("title", [
        "feat: add wan_reconnect service",
        "fix(coreapi): increase timeout for Q6 firmware",
        "ci: 新增 PR 守卫",
        "docs: 补充型号兼容表",
        "perf(api): cache the session token",
        "refactor: 拆出 client 层",
        "chore: bump dev deps",
        "test: 覆盖绑定校验",
    ])
    def test_accepts_conventional(self, guard, title):
        assert guard.TITLE_RE.match(title)

    @pytest.mark.parametrize("title", [
        "修改了一些东西",
        "Update readme",
        "feat 缺少冒号",
        "feat: 短",          # 描述 < 4 字符
        "unknown: 类型不对",
        "",
    ])
    def test_rejects_non_conventional(self, guard, title):
        assert not guard.TITLE_RE.match(title or "")

    def test_types_match_contributing_table(self, guard):
        assert set(guard.TYPES) == {
            "feat", "fix", "refactor", "docs", "ci", "chore", "test", "perf"}

    def test_main_returns_nonzero_on_bad_title(self, guard, monkeypatch, capsys):
        """守卫必须真的能拦下 —— 不能恒返回 0。"""
        monkeypatch.setenv("TITLE", "随便写点什么")
        monkeypatch.setenv("HEAD_REF", "x")
        monkeypatch.setenv("PR_NUM", "1")
        monkeypatch.setenv("REPO", "o/r")
        monkeypatch.setattr(sys, "argv", ["pr_guard.py", "--dry-run"])
        assert guard.main() == 0          # dry-run 不失败
        monkeypatch.setattr(sys, "argv", ["pr_guard.py"])
        assert guard.main() != 0, "坏标题竟然放行了 —— 守卫是装饰品"


class TestGuardAreaRules:
    @pytest.fixture(scope="class")
    @classmethod
    def guard(cls):
        return _load(GUARD_PY, "pg_area")

    def test_every_rule_is_a_tuple(self, guard):
        """★ 写成 ("x/**") 是【字符串】不是元组 —— 迭代逐字符产出，
        其中 '*' 让 fnmatch(任意路径,'*') 恒真 → 标签给每个 PR 都打上。
        单元素元组必须有尾逗号。"""
        for label, pats in guard.AREA_RULES:
            assert isinstance(pats, tuple), (
                f"{label} 的 patterns 是 {type(pats).__name__} 而非 tuple —— "
                f"漏了尾逗号，会导致该标签命中所有路径"
            )

    def test_no_rule_matches_everything(self, guard):
        """变异测试：拿一个中立探针，任何规则都不该无差别命中。"""
        probe = "some/entirely/unrelated/file.txt"
        hits = [l for l, p in guard.AREA_RULES if guard._match_any(probe, p)]
        assert hits == [], f"这些规则命中了无关路径（规则写得太宽）: {hits}"

    @pytest.mark.parametrize("path,expected", [
        (f"custom_components/{DOMAIN}/client/coreapi.py", "area: api"),
        (f"custom_components/{DOMAIN}/sensor.py", "area: platforms"),
        (f"custom_components/{DOMAIN}/switch.py", "area: platforms"),
        (f"custom_components/{DOMAIN}/config_flow.py", "area: config"),
        (f"custom_components/{DOMAIN}/ha_services.py", "area: services"),
        (f"custom_components/{DOMAIN}/services.yaml", "area: services"),
        (f"custom_components/{DOMAIN}/manifest.json", "area: core"),
        (f"custom_components/{DOMAIN}/__init__.py", "area: core"),
        (f"custom_components/{DOMAIN}/translations/en.json", "area: translations"),
        (f"custom_components/{DOMAIN}/brand/icon.png", "area: brand"),
        (".github/workflows/validate.yml", "area: ci"),
        ("README.md", "area: docs"),
        ("CONTRIBUTING.md", "area: docs"),
    ])
    def test_matches_real_repo_paths(self, guard, path, expected):
        """用仓库里真实存在的路径做精确断言。"""
        got = [l for l, p in guard.AREA_RULES if guard._match_any(path, p)]
        assert got == [expected], f"{path} → {got}，期望 [{expected}]"

    def test_dir_glob_does_not_match_prefix_sibling(self, guard):
        """`brand/**` 不能匹配 `branding/` 这种前缀兄弟目录。"""
        assert not guard._match_any(
            f"custom_components/{DOMAIN}/branding/x.png",
            (f"custom_components/{DOMAIN}/brand/**",))

    def test_all_referenced_rule_files_exist(self, guard):
        """规则里引用的具体文件必须真实存在（否则规则是死的）。"""
        missing = []
        for _label, pats in guard.AREA_RULES:
            for p in pats:
                if p.endswith("/**") or "*" in p:
                    continue
                if not (ROOT / p).exists():
                    missing.append(p)
        assert not missing, f"AREA_RULES 引用了不存在的文件: {missing}"


class TestGuardIssueLink:
    @pytest.fixture(scope="class")
    @classmethod
    def guard(cls):
        return _load(GUARD_PY, "pg_issue")

    @pytest.mark.parametrize("text", [
        "Fixes #12", "fix #3", "Closes #9", "closed #9",
        "Resolves #4", "Refs #7", "fixes: #21",
    ])
    def test_detects(self, guard, text):
        assert guard.ISSUE_RE.search(text)

    @pytest.mark.parametrize("text", ["no issue here", "#12", "issue 12", ""])
    def test_ignores(self, guard, text):
        assert not guard.ISSUE_RE.search(text or "")


class TestGuardWorkflow:
    def test_workflow_valid_and_wired(self):
        wf = _wf(GUARD_WF)
        steps = wf["jobs"]["guard"]["steps"]
        runs = " ".join(s.get("run", "") for s in steps)
        assert ".github/scripts/pr_guard.py" in runs

    def test_has_label_permission(self):
        perms = _wf(GUARD_WF)["permissions"]
        assert perms.get("pull-requests") == "write"

    def test_triggers_include_synchronize(self):
        on = _wf(GUARD_WF).get("on") or _wf(GUARD_WF).get(True)
        types = on["pull_request"]["types"]
        assert "synchronize" in types
        assert "edited" in types      # 改了标题要重跑

    def test_sparse_checkout_fetches_the_script(self):
        """sparse-checkout 没写对 → 脚本不在工作区 → workflow 直接失败。"""
        wf = _wf(GUARD_WF)
        with_ = wf["jobs"]["guard"]["steps"][0].get("with", {})
        assert with_.get("sparse-checkout") == ".github/scripts"

    def test_referenced_script_exists(self):
        assert GUARD_PY.exists()
        assert ".github/scripts/pr_guard.py" in _run_text(GUARD_WF)

    def test_gitignore_does_not_swallow_guard_script(self):
        """★ .gitignore 里的 `scripts/` 会连 `.github/scripts/` 一起吞掉 ——
        没有否定规则，守卫脚本永远不会被提交，workflow 静默失效。"""
        import subprocess
        r = subprocess.run(
            ["git", "check-ignore", "--no-index", "-q", ".github/scripts/pr_guard.py"],
            cwd=ROOT, capture_output=True)
        assert r.returncode != 0, (
            ".github/scripts/pr_guard.py 被 .gitignore 忽略了 —— "
            "需要在 scripts/ 之后加 `!.github/scripts/` 例外"
        )


# ═══════════════════════════════════════════════════════════════════════════
#  validate.yml
# ═══════════════════════════════════════════════════════════════════════════

class TestValidateWorkflow:
    def test_valid_and_has_expected_jobs(self):
        wf = _wf(VALIDATE)
        assert {"hassfest", "hacs", "lint"} <= set(wf["jobs"])

    def test_python_compile_covers_subpackages(self):
        """只写 `*.py` 会漏掉 client/ 子包 → 语法错误漏检。"""
        txt = _run_text(VALIDATE, "lint")
        assert "find custom_components" in txt
        assert "*.py" in txt
        assert "py_compile" in txt

    def test_manifest_check_uses_right_domain(self):
        txt = _run_text(VALIDATE, "lint")
        assert f'!= "{DOMAIN}"' in txt, "domain 校验写错了"

    def test_sensitive_scan_env_is_wired(self):
        """★ 变量引用过但从未映射 secret → 扫描自诞生起就是空操作。"""
        wf = _wf(VALIDATE)
        lint = wf["jobs"]["lint"]
        assert "SENSITIVE_PATTERNS" in lint.get("env", {}), (
            "job env 没有映射 SENSITIVE_PATTERNS —— 扫描会永远跳过"
        )

    def test_sensitive_scan_is_fail_closed_on_bad_json(self):
        txt = _run_text(VALIDATE, "lint")
        assert "不是合法 JSON" in txt

    def test_sensitive_scan_checks_commit_messages(self):
        """文件内容扫描看不见提交消息 —— 必须单独扫。"""
        txt = _run_text(VALIDATE, "lint")
        assert "--format=%B" in txt, "缺少提交消息扫描"

    def test_sensitive_scan_fails_closed_on_rev_list_error(self):
        txt = _run_text(VALIDATE, "lint")
        assert "rev-list 失败" in txt
        assert "未取到任何提交" in txt

    def test_fetch_depth_zero_for_commit_scan(self):
        wf = _wf(VALIDATE)
        checkout = wf["jobs"]["lint"]["steps"][0]
        assert checkout["with"]["fetch-depth"] == 0


# ═══════════════════════════════════════════════════════════════════════════
#  文档产物
# ═══════════════════════════════════════════════════════════════════════════

class TestProcessDocs:
    def test_pr_template_has_required_sections(self):
        t = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        for section in ["变更类型", "关联 Issue", "变更原因", "具体改动",
                        "验证方法", "检查清单", "破坏性变更"]:
            assert section in t, f"PR 模板缺少「{section}」节"
        for t_ in ("feat", "fix", "refactor", "docs", "ci", "chore", "test", "perf"):
            assert f"`{t_}`" in t, f"PR 模板缺少类型 `{t_}`"

    def test_contributing_documents_branch_reuse(self):
        c = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        assert "分支" in c
        # 必须说明「不得复用已合并分支」这条硬规则
        assert "复用" in c

    def test_contributing_says_maintainer_owns_version(self):
        c = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        assert "版本号" in c
        assert "维护者" in c

    def test_contributing_documents_mutation_testing(self):
        c = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        assert "变异测试" in c or "真的能失败" in c

    def test_manifest_version_is_semver_not_behind_latest_tag(self):
        """★ 版本号是维护者的活，CI PR 不该动它 —— 但这条断言不能写死某个数字，
        否则维护者自己发版时会把测试弄红。
        改成检查**持久成立的不变量**：manifest 版本必须合法，且不小于最新 tag。"""
        import json
        import subprocess
        raw = json.loads((ROOT / f"custom_components/{DOMAIN}/manifest.json")
                         .read_text(encoding="utf-8"))["version"]
        assert re.fullmatch(r"\d+\.\d+\.\d+([.-]?(a|b|rc|beta|alpha)\d*)?", raw), \
            f"manifest 版本不是合法 semver: {raw}"

        tags = subprocess.run(["git", "tag", "-l", "v*", "--sort=-v:refname"],
                              cwd=ROOT, capture_output=True, text=True).stdout.split()
        if not tags:
            pytest.skip("仓库还没有 tag")
        packaging = pytest.importorskip("packaging.version")
        newest = packaging.Version(tags[0].lstrip("v"))
        cur = packaging.Version(raw)
        assert cur >= newest, (
            f"manifest 版本 {cur} 落后于最新 tag {newest} —— "
            f"版本号只增不减，可能是回退了"
        )