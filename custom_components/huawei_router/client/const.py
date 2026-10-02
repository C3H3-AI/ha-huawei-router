from typing import Final



WIFI_SECURITY_OPEN: Final = "none"

WIFI_SECURITY_ENCRYPTED: Final = "tkip"



CONNECTED_VIA_ID_PRIMARY: Final = "primary"



URL_DEVICE_INFO: Final = "api/system/deviceinfo"

URL_DEVICE_TOPOLOGY: Final = "api/device/topology"

URL_GUEST_NETWORK: Final = "api/ntwk/guest_network?type=notshowpassall"

URL_HOST_INFO: Final = "api/system/HostInfo"

URL_PORT_MAPPING: Final = "api/ntwk/portmapping"
URL_PORT_TRIGGER: Final = "api/ntwk/porttrigger"
URL_UPNP_PORT_MAPPING: Final = "api/ntwk/lan_upnp_portmapping"
URL_APPLICATION: Final = "api/app/application"
URL_REBOOT: Final = "api/service/reboot.cgi"

URL_REPEATER_INFO: Final = "api/ntwk/repeaterinfo"

URL_SWITCH_NFC: Final = "api/bsp/nfc_switch"

URL_SWITCH_WIFI_80211R: Final = "api/ntwk/WlanGuideBasic?type=notshowpassall"

URL_SWITCH_WIFI_TWT: Final = "api/ntwk/WlanGuideBasic?type=notshowpassall"

URL_TIME_CONTROL: Final = "api/ntwk/timecontrol"

URL_URL_FILTER: Final = "api/ntwk/urlfilter"

URL_TIMED_REDIAL: Final = "api/ntwk/timedredial"
URL_WAN_INFO: Final = "api/ntwk/wan?type=active"
URL_WANDETECT: Final = "api/ntwk/wandetect"

URL_WLAN_FILTER: Final = "api/ntwk/wlanfilterenhance"

# 新逆向出的 Q6 端点（均已在固件上验证返回真实数据）
URL_DHCP_STATIC_LEASE: Final = "api/ntwk/lan_ipaddressreserve"
URL_UPNP: Final = "api/ntwk/lan_upnp"
URL_IPV6_ENABLE: Final = "api/ntwk/ipv6_enable"
URL_DMZ: Final = "api/ntwk/dmz"
URL_FIREWALL: Final = "api/ntwk/firewall"
URL_REBOOT_PLAN: Final = "api/system/rebootplan"
URL_DDNS: Final = "api/ntwk/ddns"
URL_DDNS_STATUS: Final = "api/ntwk/ddnsstatus"
URL_BAND_STEERING: Final = "api/ntwk/wlandbho"
URL_SMART_CONNECT: Final = "api/ntwk/wlanintelligent"

# 设备管理（列表模式：改名 / QoS 限速 / 删除设备）
URL_CHANGE_DEVICE_NAME: Final = "api/system/changedevicename"
URL_QOS_CLASS_HOST: Final = "api/app/qosclass_host"

# ---------------------------------------------------------------------------
# Web UI 剩余端点（强类型服务用）
# ---------------------------------------------------------------------------
URL_WLAN_RADIO: Final = "api/ntwk/wlanradio"
URL_WLAN_WPS: Final = "api/ntwk/wlanwps"
URL_WPS_SWITCH: Final = "api/ntwk/wps_switch"
URL_MULTI_SSID: Final = "api/ntwk/multi_ssid"
URL_WLAN_TIMING_ACCELERATE: Final = "api/ntwk/wlanTimingAccelerate"
URL_WLAN_WIFI_SYNC: Final = "api/ntwk/wlanwifisync"

URL_LAN: Final = "api/ntwk/lan"
URL_LAN_ALL: Final = "api/ntwk/lan_all"
URL_LAN_SERVER: Final = "api/ntwk/lan_server"
URL_LAN_DEVICE_TYPE: Final = "api/ntwk/lan_devicetype"
URL_LAN_HOST: Final = "api/ntwk/lan_host"

# WiFi 射频详情（诊断页同款数据；type=1 为 2.4G，type=2 为 5G，真机已验证）
URL_WLAN_DIAG_BASIC_2G: Final = "api/system/diagnose_wlan_basic?type=1"
URL_WLAN_DIAG_BASIC_5G: Final = "api/system/diagnose_wlan_basic?type=2"

# 诊断日志收集 / 下载（真机已验证全链路，见 VERIFICATION.md）
URL_DIAGNOSTICS: Final = "api/system/diagnose_crash"
URL_DIAGNOSTICS_DOWNLOAD: Final = "api/system/diagnose_crash_resultdownload"

URL_WAN_LEARN_CONFIG: Final = "api/ntwk/wanlearnconfig?type=notshowpass"
URL_WAN_DIAGNOSE: Final = "api/ntwk/wandiagnose"
URL_IPV6_WAN: Final = "api/ntwk/ipv6_wan"
URL_IPV6_LAN: Final = "api/ntwk/ipv6_lan"
URL_ALG: Final = "api/ntwk/alg"
URL_TUNNEL: Final = "api/ntwk/tunnel"
URL_SWAN: Final = "api/ntwk/swan"
URL_SMART_VPN: Final = "api/ntwk/smartvpn"
URL_IPTV: Final = "api/ntwk/iptv"

URL_MAC_FILTER: Final = "api/ntwk/fwmacfilter"
URL_ACCESS_AUTH: Final = "api/ntwk/access_auth"
URL_HOMESEC_ABFA: Final = "api/ntwk/homesec_abfa"
URL_HOMESEC_STEALNET: Final = "api/ntwk/homesec_stealnet"
URL_XLINK_LOCK_NET: Final = "api/ntwk/xlink_lock_net"

URL_GUEST_NETWORK_LIMIT_RATE: Final = "api/ntwk/guest_network_limitrate"
URL_GUEST_NETWORK_REST_TIME: Final = "api/ntwk/guest_network_resttime"

URL_NTP: Final = "api/ntwk/sntp"
URL_PROCESS_STATUS: Final = "api/system/processstatus"
URL_ONLINE_STATE: Final = "api/system/onlinestate"
URL_ETH_NEGOTIATION: Final = "api/ntwk/ethnegotiation"
URL_CHANNEL_INFO: Final = "api/ntwk/channelinfo"
URL_DEVICE_COUNT: Final = "api/system/device_count"
URL_AUTO_UPGRADE: Final = "api/system/autoupgrade"
URL_ONLINE_UPGRADE: Final = "api/system/onlineupg"
URL_PASSWORD_RULE: Final = "api/system/pwdrule"
URL_USER_ACCOUNT: Final = "api/system/useraccount"
URL_LANGUAGE: Final = "api/language/lang"

URL_WIFI_SCAN: Final = "api/ntwk/wifiscan"
URL_WIFI_SCAN_RESULT: Final = "api/ntwk/wifiscanresult"
URL_REPEATER_STATE: Final = "api/ntwk/repeaterstate"
URL_REPEATER_DIAG: Final = "api/ntwk/repeaterdiag"
URL_REPEATER_DIAL: Final = "api/ntwk/RepeaterDial"
URL_NETDISK_INFO: Final = "api/ntwk/netdiskinfo"
URL_NETDISK_CODE: Final = "api/ntwk/netdiskcode"
URL_HILINK_STATUS: Final = "api/hilink/hilink_status"
URL_SLAVE_SETUP: Final = "api/hilink/slave_setup"
URL_MULTI_HOST_INFO: Final = "api/system/MultiHostInfo"
URL_SYSTEM_MODE: Final = "api/system/wlanmode"

# ---------------------------------------------------------------------------
# 通用 API 桥接白名单（key 供 HA 服务选择，value 为路由器相对路径）
#
# 收录自 Web UI 逆向清单中所有真实的命名空间端点。已排除的条目：
#   1. 前端路由名：路径与名字完全相同、且只用 changeLang 方式（如 home、wifi、
#      nat、reboot、ipv6、login、upgrade 等），它们不是 API；
#   2. 退化为非法路径的名字（e、t、e.circlegetUrl、["useraccount"]、iptv_detect、
#      sshRemoteState、telnetRemoteState、wanremoteaccess、remoteaccesslist）；
#   3. 以 "/" 开头的绝对/遗留路径（/api/service/reboot.cgi、/api/system/poweroff
#      等），其中 reboot 已有专用实现。
# ---------------------------------------------------------------------------
RAW_API_ENDPOINTS: Final = {
    "MultiHostInfo": "api/system/MultiHostInfo",
    "RepeaterDial": "api/ntwk/RepeaterDial",
    "RepeaterDial_scram": "api/ntwk/RepeaterDial_scram",
    "WlanGuideBasic": "api/ntwk/WlanGuideBasic?type=notshowpassall",
    "access_auth": "api/ntwk/access_auth",
    "alg": "api/ntwk/alg",
    "app_wizard": "api/app/wizards",
    "applicationitems": "api/app/applicationitems",
    "autoupgrade": "api/system/autoupgrade",
    "backhaul": "api/ntwk/backhaul",
    "channelinfo": "api/ntwk/channelinfo",
    "client_heartbeat": "api/ntwk/client_heartbeat",
    "custom_report": "api/system/custom_report",
    "deviceinfo_wizard": "api/system/deviceinfo?type=wizards",
    "diagnose_button": "api/system/diagnose_button",
    "diagnose_crash": "api/system/diagnose_crash",
    "diagnose_led": "api/system/diagnose_led",
    "ethnegotiation": "api/ntwk/ethnegotiation",
    "forceupg": "api/system/forceupg",
    "forceupgcfg": "api/system/forceupgcfg",
    "forceupglater": "api/system/forceupglater",
    "fwmacfilter": "api/ntwk/fwmacfilter",
    "getmacaddress": "api/ntwk/getmacaddress",
    "guest_network": "api/ntwk/guest_network?type=notshowpassall",
    "guest_network_limitrate": "api/ntwk/guest_network_limitrate",
    "guest_network_resttime": "api/ntwk/guest_network_resttime",
    "guide": "api/system/guide",
    "heartbeat": "api/system/heartbeat",
    "hilink_status": "api/hilink/hilink_status",
    "homesec_abfa": "api/ntwk/homesec_abfa",
    "homesec_stealnet": "api/ntwk/homesec_stealnet",
    "hotaservice": "api/system/hotaservice",
    "httpdiagnose": "api/system/httpdiagnose",
    "iptv": "api/ntwk/iptv",
    "ipv6_lan": "api/ntwk/ipv6_lan",
    "ipv6_wan": "api/ntwk/ipv6_wan",
    "lan": "api/ntwk/lan",
    "lan_all": "api/ntwk/lan_all",
    "lan_server": "api/ntwk/lan_server",
    "language": "api/language/lang",
    "mirror": "api/ntwk/mirror",
    "multi_ssid": "api/ntwk/multi_ssid",
    "netdiskcode": "api/ntwk/netdiskcode",
    "netdiskguide": "api/ntwk/netdiskguide",
    "netdiskinfo": "api/ntwk/netdiskinfo",
    "onlinestate": "api/system/onlinestate",
    "onlineupg": "api/system/onlineupg",
    "plc_web_certification": "api/ntwk/plc_web_certification",
    "privacypolicy": "api/app/privacypolicy",
    "processstatus": "api/system/processstatus",
    "provcode": "api/system/provcode",
    "pwdrule": "api/system/pwdrule",
    "repeaterdiag": "api/ntwk/repeaterdiag",
    "repeaterstate": "api/ntwk/repeaterstate",
    "restorestate": "api/system/restorestate",
    "slave_setup": "api/hilink/slave_setup",
    "smartpush_autoupg": "api/app/smartpush_autoupg",
    "smartvpn": "api/ntwk/smartvpn",
    "smartvpnurl": "api/ntwk/smartvpnurl",
    "sntp": "api/ntwk/sntp",
    "swan": "api/ntwk/swan",
    "tunnel": "api/ntwk/tunnel",
    "uploadconfigfileresult": "api/device/uploadconfigfileresult",
    "user_logout": "api/system/user_logout",
    "useraccount": "api/system/useraccount",
    "userbehavior": "api/system/userbehavior",
    "wan": "api/ntwk/wan?type=active",
    "wandiagnose": "api/ntwk/wandiagnose",
    "wanlearnconfig": "api/ntwk/wanlearnconfig?type=notshowpass",
    "wanlearntrigerloopmac": "api/ntwk/wanlearntrigerloopmac",
    "wifiscan": "api/ntwk/wifiscan",
    "wifiscanresult": "api/ntwk/wifiscanresult",
    "wizard_wifi": "api/system/wizard_wifi",
    "wlan_time_switch_list": "api/ntwk/wlan_time_switch_list",
    "wlanelink": "api/ntwk/wlanelink",
    "wlanmode": "api/system/wlanmode",
    "wlanpowertimeswitch": "api/ntwk/wlanpowertimeswitch",
    "wlanradio": "api/ntwk/wlanradio",
    "wlantimeaccelerate": "api/ntwk/wlanTimingAccelerate",
    "wlanwifisync": "api/ntwk/wlanwifisync",
    "wlanwps": "api/ntwk/wlanwps",
    "wps_switch": "api/ntwk/wps_switch",
    "xlink_lock_net": "api/ntwk/xlink_lock_net",
}

