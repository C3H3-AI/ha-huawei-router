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

