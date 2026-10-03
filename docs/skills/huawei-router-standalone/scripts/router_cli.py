#!/usr/bin/env python3
"""华为路由器 LAN 控制 CLI —— 独立于 Home Assistant 集成。

只依赖 aiohttp + pycryptodome，不 import huawei_router 集成任何代码。

用法:
  python3 router_cli.py init                    # 交互生成配置文件（推荐先跑）
  python3 router_cli.py check                   # 自检本机型功能可用性
  python3 router_cli.py status
  python3 router_cli.py devices [--online]
  python3 router_cli.py wifi
  python3 router_cli.py ports
  python3 router_cli.py get <短名或路径>        # 短名查 ENDPOINTS 表
  python3 router_cli.py endpoints [关键字]      # 列出可用短名
  python3 router_cli.py exec <短名> [k=v...]    # 通用 POST
  python3 router_cli.py backup <输出路径>       # 导出配置
  python3 router_cli.py devlist                 # 列出可诊断设备（主路由+子路由）
  python3 router_cli.py diag <目录> [目标MAC]   # 收集+下载诊断日志（给MAC即采子路由）

配置（优先级：环境变量 > 配置文件 > 默认）:
  环境变量 HW_HOST / HW_USER / HW_PASS
  或配置文件 ~/.huawei-router.json（用 init 命令生成，权限 600）
"""
import asyncio, json, os, re, sys, hashlib, hmac, time
from random import randbytes

try:
    import aiohttp
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
except ImportError:
    sys.exit("缺少依赖: pip install aiohttp pycryptodome")

HOST = os.environ.get("HW_HOST", "")  # 必填：路由器管理地址，形如 http://<网关IP>
USER = os.environ.get("HW_USER", "admin")
PW = os.environ.get("HW_PASS", "")


# ---------------------------
#   配置文件支持（~/.huawei-router.json）
# ---------------------------
# 优先级：环境变量 > 配置文件 > 内置默认。
# 配置文件格式（权限建议 600，内含明文密码）：
#   {"host": "http://192.168.3.1", "user": "admin", "password": "xxx"}
# 用 `router_cli.py init` 交互式生成，避免手写。
CONFIG_PATH = os.path.expanduser(os.environ.get("HW_CONFIG", "~/.huawei-router.json"))


def _load_config() -> dict:
    """读取配置文件；不存在或损坏时返回空 dict（不报错，让环境变量兜底）。"""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


_cfg = _load_config()
HOST = HOST or str(_cfg.get("host") or "")
USER = os.environ.get("HW_USER") or str(_cfg.get("user") or "admin")
PW = PW or str(_cfg.get("password") or "")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# 前端 main.js 的 name → path 映射表（186 项，逆向自 Web UI）
ENDPOINTS = {
    "HostInfo": "system/HostInfo",
    "MultiHostInfo": "system/MultiHostInfo",
    "deviceinfo": "system/deviceinfo",
    "device_count": "system/device_count",
    "processstatus": "system/processstatus",
    "onlinestate": "system/onlinestate",
    "rebootplan": "system/rebootplan",
    "autoupgrade": "system/autoupgrade",
    "onlineupg": "system/onlineupg",
    "sntp": "ntwk/sntp",
    "lan": "ntwk/lan",
    "lan_all": "ntwk/lan_all",
    "lan_host": "ntwk/lan_host",
    "lan_server": "ntwk/lan_server",
    "lan_devicetype": "ntwk/lan_devicetype",
    "lan_ipaddressreserve": "ntwk/lan_ipaddressreserve",
    "ethnegotiation": "ntwk/ethnegotiation",
    "wlanradio": "ntwk/wlanradio",
    "multi_ssid": "ntwk/multi_ssid",
    "guest_network": "ntwk/guest_network?type=notshowpassall",
    "guest_network_limitrate": "ntwk/guest_network_limitrate",
    "wlanfilterenhance": "ntwk/wlanfilterenhance",
    "homesec_abfa": "ntwk/homesec_abfa",
    "homesec_stealnet": "ntwk/homesec_stealnet",
    "firewall": "ntwk/firewall",
    "dmz": "ntwk/dmz",
    "portmapping": "ntwk/portmapping",
    "application": "app/application",
    "applicationitems": "app/applicationitems",
    "upnp": "ntwk/lan_upnp",
    "ddns": "ntwk/ddns",
    "ddnsstatus": "ntwk/ddnsstatus",
    "ipv6_wan": "ntwk/ipv6_wan",
    "ipv6_lan": "ntwk/ipv6_lan",
    "iptv": "ntwk/iptv",
    "alg": "ntwk/alg",
    "smartvpn": "ntwk/smartvpn",
    "tunnel": "ntwk/tunnel",
    "wan": "ntwk/wan?type=active",
    "wandetect": "ntwk/wandetect",
    "wandiagnose": "ntwk/wandiagnose",
    "timedredial": "ntwk/timedredial",
    "qosclass_host": "app/qosclass_host",
    "changedevicename": "system/changedevicename",
    "topology": "device/topology",
    "hilink_status": "hilink/hilink_status",
    "slave_setup": "hilink/slave_setup",
    "repeaterstate": "ntwk/repeaterstate",
    "repeaterdiag": "ntwk/repeaterdiag",
    "wifiscan": "ntwk/wifiscan",
    "wifiscanresult": "ntwk/wifiscanresult",
    "channelinfo": "ntwk/channelinfo",
    "wlantimeaccelerate": "ntwk/wlanTimingAccelerate",
    "wlanintelligent": "ntwk/wlanintelligent",
    "wlandbho": "ntwk/wlandbho",
    "useraccount": "system/useraccount",
    "pwdrule": "system/pwdrule",
    "language": "language/lang",
    "diagnose_crash": "system/diagnose_crash",
    "diagnose_crash_devlist": "system/diagnose_crash_devlist",
    "diagnose_wlan_basic": "system/diagnose_wlan_basic?type=1",
    "wlanmode": "system/wlanmode",
}

# 破坏性端点：exec 到这些需显式 --force
DESTRUCTIVE = {
    "restoredefcfg", "uploadconfigfile", "device_remove", "reboot",
    "reset", "restorestate", "delayreboot", "forceupg",
}


def _nonce():
    return randbytes(32).hex()


def _proof(pw, salt, iters, fn, sn):
    sp = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytearray.fromhex(salt), iters, 32)
    ck = hmac.new(b"Client Key", sp, hashlib.sha256).digest()
    sk = hashlib.sha256(ck).digest()
    cs = hmac.new(f"{fn},{sn},{sn}".encode(), sk, hashlib.sha256).digest()
    return bytes(a ^ b for a, b in zip(ck, cs)).hex()


class Router:
    def __init__(self, host=HOST, user=USER, pw=PW):
        self.host, self.user, self.pw = host.rstrip("/"), user, pw
        self.csrf = None
        self.s = None

    async def __aenter__(self):
        self.s = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True),
            headers={"User-Agent": UA, "Accept": "application/json, text/plain, */*",
                     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                     "Origin": self.host, "Referer": self.host + "/html/index.html"})
        return self

    async def __aexit__(self, *a):
        await self.logout()          # ★ 关键：释放 session，路由器只有 2 个
        if self.s:
            await self.s.close()

    def u(self, p):
        return self.host + "/" + p.lstrip("/")

    def resolve(self, name):
        """短名 → 完整路径；已是路径则原样返回。"""
        if name in ENDPOINTS:
            return "api/" + ENDPOINTS[name]
        return name if name.startswith("api/") else "api/" + name

    async def login(self):
        if not self.pw:
            raise SystemExit("请设置 HW_PASS 环境变量")
        r = await self.s.get(self.u("html/index.html"), timeout=15)
        t = await r.text()
        self.csrf = {"csrf_param": re.search(r'name="csrf_param" content="(.+?)"', t).group(1),
                     "csrf_token": re.search(r'name="csrf_token" content="(.+?)"', t).group(1)}
        fn = _nonce()
        r = await self.s.post(self.u("api/system/user_login_nonce"), timeout=15,
            json={"csrf": self.csrf, "data": {"username": self.user, "firstnonce": fn}})
        d = await r.json()
        if "servernonce" not in d:
            raise SystemExit(f"登录失败（可能已限流 Too_Many_user）: {d}")
        sn, it, salt = d["servernonce"], int(d["iterations"]), d["salt"]
        self.csrf = {"csrf_param": d.get("csrf_param", self.csrf["csrf_param"]),
                     "csrf_token": d.get("csrf_token", self.csrf["csrf_token"])}
        r = await self.s.post(self.u("api/system/user_login_proof"), timeout=15,
            json={"csrf": self.csrf,
                  "data": {"clientproof": _proof(self.pw, salt, it, fn, sn), "finalnonce": sn}})
        d = await r.json()
        self.csrf = {"csrf_param": d.get("csrf_param", self.csrf["csrf_param"]),
                     "csrf_token": d.get("csrf_token", self.csrf["csrf_token"])}
        return True

    async def logout(self):
        """显式登出，释放 session（路由器仅 2 个并发）。失败不影响退出。"""
        try:
            await self.s.post(self.u("api/system/user_logout"), timeout=5,
                              json={"csrf": self.csrf})
        except Exception:
            pass

    async def get(self, name):
        r = await self.s.get(self.u(self.resolve(name)), timeout=15)
        try:
            return await r.json()
        except Exception:
            return None

    async def post(self, name, data=None, action=None):
        dto = {"data": data or {}, "csrf": self.csrf}
        if action:
            dto["action"] = action
        r = await self.s.post(self.u(self.resolve(name)), timeout=120, json=dto)
        try:
            return await r.json()
        except Exception:
            return None

    async def download(self, path, out):
        r = await self.s.get(self.u(path), timeout=120)
        if r.status != 200:
            return {"error": f"HTTP {r.status}"}
        data = await r.read()
        with open(out, "wb") as f:
            f.write(data)
        return {"path": out, "size": len(data)}

    async def sleep(self, s=1.5):
        await asyncio.sleep(s)


def _cmd_init() -> None:
    """交互式生成配置文件（避免手写 JSON、避免密码进 shell 历史）。"""
    import getpass

    print(f"配置将写入: {CONFIG_PATH}")
    if os.path.exists(CONFIG_PATH):
        print("  （已存在，将被覆盖）")
    cur = _load_config()
    default_host = cur.get("host") or "http://192.168.3.1"
    default_user = cur.get("user") or "admin"

    host = input(f"路由器地址 [{default_host}]: ").strip() or default_host
    if not host.startswith(("http://", "https://")):
        host = "http://" + host
    user = input(f"用户名 [{default_user}]: ").strip() or default_user
    # getpass 不回显，且不写入 shell 历史
    pw = getpass.getpass("密码（输入时不显示）: ")
    if not pw:
        sys.exit("密码不能为空")

    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump({"host": host, "user": user, "password": pw}, fh,
                  ensure_ascii=False, indent=2)
    os.chmod(CONFIG_PATH, 0o600)     # 含明文密码，收紧权限
    print(f"✅ 已写入 {CONFIG_PATH}（权限 600）")
    print("   之后直接运行命令即可，无需再设环境变量")


async def _cmd_check(r: "Router") -> None:
    """自检本机型的功能可用性（真机探测，不依赖硬编码清单）。

    每一项用只读 GET 看真实 HTTP 状态码：
      200 + 有数据 = 可用；200 + 空数组 = 端点存在但无数据；404 = 本机型无。
    探测间隔 1.5s，避免打满路由器 2-session 限额。
    """
    # (标签, 端点, 该功能"可用"的判定)
    groups = [
        ("核心", [
            ("设备信息", "deviceinfo"),
            ("设备列表", "HostInfo"),
            ("CPU/内存", "processstatus"),
            ("设备计数", "device_count"),
            ("NTP", "sntp"),
        ]),
        ("WiFi", [
            ("2.4G 射频", "system/diagnose_wlan_basic?type=1"),
            ("5G 射频", "system/diagnose_wlan_basic?type=2"),
            ("WiFi 射频配置", "wlanradio"),
            ("访客网络", "guest_network"),
            ("信道信息", "channelinfo"),
        ]),
        ("网络", [
            ("LAN", "lan"),
            ("LAN host", "lan_host"),
            ("DHCP 服务器", "lan_server"),
            ("网口速率", "ethnegotiation"),
            ("端口映射", "portmapping"),
            ("防火墙", "firewall"),
            ("DMZ", "dmz"),
            ("DDNS", "ddns"),
            ("IPv6 WAN", "ipv6_wan"),
            ("UPnP", "upnp"),
            ("IPTV", "iptv"),
        ]),
        ("安全/组网", [
            ("WiFi 过滤", "wlanfilterenhance"),
            ("防暴力破解", "homesec_abfa"),
            ("防蹭网", "homesec_stealnet"),
            ("HiLink 组网", "hilink_status"),
            ("中继状态", "repeaterstate"),
        ]),
        ("诊断", [
            ("诊断设备列表", "diagnose_crash_devlist"),
            ("诊断状态", "diagnose_crash"),
        ]),
    ]
    # 已知不支持（对照用）：探测这些应返回 404
    known_unsupported = [
        ("NFC", "bsp/nfc_switch"),
        ("时间控制", "ntwk/timecontrol"),
        ("网址过滤", "ntwk/urlfilter"),
        ("端口转发(扁平)", "ntwk/portforwarding"),
        ("WPS", "ntwk/wps_switch"),
        ("端口镜像", "ntwk/mirror"),
        ("多 SSID", "ntwk/multi_ssid"),
        ("硬件加速", "dps_switch"),
    ]

    async def probe(name: str, ep: str) -> tuple[str, str]:
        try:
            d = await r.get(ep)
        except Exception as ex:  # noqa: BLE001
            return name, f"❌ 异常 {type(ex).__name__}"
        await r.sleep(1.5)
        if d is None:
            return name, "❌ 404 / 无响应"
        if isinstance(d, list) and not d:
            return name, "⚠️  200 但空"
        return name, "✅ 可用"

    print("路由器功能自检（真机探测）\n")
    for title, items in groups:
        print(f"【{title}】")
        for name, ep in items:
            n, verdict = await probe(name, ep)
            print(f"  {n:16s} {verdict}")
        print()

    print("【本机型已知不支持（对照，预期 404）】")
    unexpected = []
    for name, ep in known_unsupported:
        n, verdict = await probe(name, ep)
        # 若这里返回 200 有数据，说明固件变了，需要更新 skill
        if verdict == "✅ 可用":
            unexpected.append(n)
        print(f"  {n:16s} {verdict}")
    if unexpected:
        print(f"\n⚠️  以下功能实测可用，与文档记录的『不支持』不符 —— "
              f"固件可能已升级，请更新 skill：{', '.join(unexpected)}")
    else:
        print("\n✅ 与文档记录一致（这些功能在本机型确实不可用）")


async def cmd_endpoints(args):
    kw = args[0] if args else None
    for k in sorted(ENDPOINTS):
        if kw and kw.lower() not in k.lower() and kw.lower() not in ENDPOINTS[k].lower():
            continue
        print(f"  {k:32s} {ENDPOINTS[k]}")


async def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd = argv[0]

    # init 不需要连路由器，放在 HOST 校验之前
    if cmd == "init":
        _cmd_init()
        return

    if not HOST:
        sys.exit(
            f"未配置路由器地址。请任选其一：\n"
            f"  1) 运行 `{os.path.basename(sys.argv[0])} init` 生成配置文件 {CONFIG_PATH}\n"
            f"  2) 设置环境变量 HW_HOST（形如 http://<网关IP>）"
        )
    if not PW:
        sys.exit(
            f"未配置密码。请任选其一：\n"
            f"  1) 运行 `{os.path.basename(sys.argv[0])} init`\n"
            f"  2) 设置环境变量 HW_PASS"
        )
    rest = argv[1:]
    force = "--force" in rest
    rest = [a for a in rest if a != "--force"]

    async with Router() as r:
        await r.login()

        if cmd == "endpoints":
            await cmd_endpoints(rest)

        elif cmd == "status":
            d = await r.get("deviceinfo")
            await r.sleep()
            ps = await r.get("processstatus")
            await r.sleep()
            dc = await r.get("device_count")
            tot = next((x for x in ps if x.get("Name") == "Total"), {})
            print(json.dumps({
                "型号": d.get("custinfo", {}).get("CustDeviceName"),
                "固件": d.get("SoftwareVersion"),
                "HarmonyOS": d.get("HarmonyOSVersion"),
                "运行时间_秒": d.get("UpTime"),
                "CPU%": tot.get("CpuUsage"), "内存%": tot.get("MemUsage"),
                "在线设备": dc.get("ActiveDeviceNumbers"),
                "Mesh节点": dc.get("HiLinkDevNum"),
            }, ensure_ascii=False, indent=2))

        elif cmd == "devices":
            d = await r.get("HostInfo")
            only_online = "--online" in " ".join(rest)
            for h in d:
                if only_online and not h.get("Active"):
                    continue
                tag = "[子路由]" if h.get("IsSlave") else "[离线] " if not h.get("Active") else "       "
                print(f"  {h.get('MACAddress')}  {str(h.get('IPAddress')):15s} {tag} "
                      f"{h.get('ActualName') or h.get('HostName')}")

        elif cmd == "wifi":
            for band, ep in (("2.4G", "system/diagnose_wlan_basic?type=1"),
                             ("5G", "system/diagnose_wlan_basic?type=2")):
                w = await r.get(ep)
                print(f"  {band}: 信道={w.get('Channel')} 带宽={w.get('Bandwidth')} "
                      f"SSID={w.get('SSID')} 加密={w.get('BeaconType')} 功率={w.get('TransmitPower')}%")
                await r.sleep()

        elif cmd == "ports":
            d = await r.get("ethnegotiation")
            for p in d.get("ethintflist", []):
                sp, st = p.get("Speed"), p.get("Status")
                print(f"  {p.get('PortName'):6s} {sp} Mbps  "
                      f"{'已连接' if st == 1 else '未连接'}")

        elif cmd == "get":
            print(json.dumps(await r.get(rest[0]), ensure_ascii=False, indent=2)[:4000])

        elif cmd == "exec":
            name = rest[0]
            if name in DESTRUCTIVE and not force:
                print(f"⛔ '{name}' 是破坏性操作。确认请加 --force\n"
                      f"   （路由器仅 2 session，误操作影响整网）")
                return
            kv = {}
            for a in rest[1:]:
                if "=" in a:
                    k, v = a.split("=", 1)
                    kv[k] = v.lower() in ("true", "1") if v.lower() in ("true", "false", "1", "0") else v
            print(json.dumps(await r.post(name, kv), ensure_ascii=False))

        elif cmd == "backup":
            out = rest[0] if rest else "/tmp/q6_backup.conf"
            print(json.dumps(await r.download("api/system/downloadcfg", out), ensure_ascii=False))

        elif cmd == "check":
            # 自检：把"本机型不支持清单"变成可执行验证（真机探测而非硬编码）
            await _cmd_check(r)

        elif cmd == "devlist":
            devs = await r.get("diagnose_crash_devlist")
            print(f"可诊断设备 {len(devs)} 台：")
            for d in devs:
                tag = "★主路由" if d.get("IsMainDevice") else " 子路由"
                print(f"  {tag}  {str(d.get('DeviceName'))[:26]:28s} "
                      f"{d.get('MACAddress')}  {d.get('URL')}")

        elif cmd == "diag":
            # diag [输出目录] [目标MAC] —— 给 MAC 即采集该子路由日志
            outdir = rest[0] if rest else "/tmp"
            target_mac = rest[1] if len(rest) > 1 else None
            devlist = await r.get("diagnose_crash_devlist")
            if target_mac:
                dev = next((x for x in devlist
                            if str(x.get("MACAddress", "")).upper() == target_mac.upper()), None)
                if not dev:
                    print(f"⛔ 设备列表中找不到 MAC: {target_mac}")
                    print("   可用设备（先跑 devlist 查看）:")
                    for x in devlist:
                        print(f"     {x.get('MACAddress')}  {x.get('DeviceName')}")
                    return
            else:
                dev = next((x for x in devlist if x.get("IsMainDevice")), None)
            mac = dev["MACAddress"] if dev else None
            is_main = bool(dev.get("IsMainDevice")) if dev else True
            print(f"目标: {dev.get('DeviceName') if dev else '?'} ({mac})"
                  f"{'  [主路由]' if is_main else '  [子路由]'}")
            res = await r.post("diagnose_crash", {"CrashAction": "InfoCollect",
                                                  "Mac": mac, "IsMainDev": is_main},
                               action="update")
            print("触发收集:", res.get("errcode") if isinstance(res, dict) else res)
            s = None
            for i in range(40):
                await r.sleep(2)
                st = await r.get("diagnose_crash")
                s = st.get("DiagnosticsState")
                if s in ("ExecLuaSuccess", "ErrorExecLuaFailed", "ErrorNoDiagnoseResult"):
                    print(f"[{i*2}s] {s}")
                    break
            if s == "ExecLuaSuccess":
                name = "huawei_diag.tar" if is_main else f"huawei_diag_{mac.replace(':', '')}.tar"
                out = os.path.join(outdir, name)
                print(json.dumps(await r.download("api/system/diagnose_crash_resultdownload", out),
                                 ensure_ascii=False))
            else:
                print("收集未成功，状态:", s)
        else:
            print(__doc__)

asyncio.run(main())
