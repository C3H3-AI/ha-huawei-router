"""Support for services."""



from dataclasses import dataclass

from enum import StrEnum

import logging

from typing import Final



import voluptuous as vol



from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant, ServiceCall

from homeassistant.exceptions import HomeAssistantError, ServiceNotFound

import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.service import verify_domain_control



from .client.classes import (
    MAC_ADDR,
    FilterAction,
    FilterMode,
    HuaweiGuestNetworkDuration,
)
from .client.huaweiapi import InvalidActionError
from .client.const import (
    RAW_API_ENDPOINTS,
    URL_ACCESS_AUTH,
    URL_ALG,
    URL_AUTO_UPGRADE,
    URL_ETH_NEGOTIATION,
    URL_GUEST_NETWORK_LIMIT_RATE,
    URL_GUEST_NETWORK_REST_TIME,
    URL_IPTV,
    URL_IPV6_LAN,
    URL_IPV6_WAN,
    URL_LAN,
    URL_LAN_ALL,
    URL_LAN_DEVICE_TYPE,
    URL_LAN_SERVER,
    URL_MAC_FILTER,
    URL_MULTI_SSID,
    URL_NETDISK_CODE,
    URL_NETDISK_INFO,
    URL_NTP,
    URL_ONLINE_STATE,
    URL_PASSWORD_RULE,
    URL_PROCESS_STATUS,
    URL_REPEATER_DIAG,
    URL_REPEATER_STATE,
    URL_SMART_VPN,
    URL_SWAN,
    URL_SYSTEM_MODE,
    URL_TUNNEL,
    URL_USER_ACCOUNT,
    URL_WAN_DIAGNOSE,
    URL_WAN_LEARN_CONFIG,
    URL_WIFI_SCAN_RESULT,
    URL_WLAN_RADIO,
    URL_WLAN_TIMING_ACCELERATE,
    URL_WLAN_WIFI_SYNC,
    URL_WLAN_WPS,
    URL_XLINK_LOCK_NET,
)

from .const import DATA_KEY_COORDINATOR, DATA_KEY_SERVICES, DOMAIN

from .update_coordinator import HuaweiDataUpdateCoordinator



_LOGGER = logging.getLogger(__name__)



_FIELD_MAC_ADDRESS: Final = "mac_address"



_FIELD_SERIAL_NUMBER: Final = "serial_number"

_FIELD_ENABLED: Final = "enabled"

_FIELD_SSID: Final = "ssid"

_FIELD_DURATION: Final = "duration"

_FIELD_SECURITY: Final = "security"

_FIELD_PASSWORD: Final = "password"



_CV_MAC_ADDR: Final = cv.matches_regex("^([A-Fa-f0-9]{2}\\:){5}[A-Fa-f0-9]{2}$")



_WIFI_DURATION_MAP: dict[str, HuaweiGuestNetworkDuration] = {

    "four_hours": HuaweiGuestNetworkDuration.FOUR_HOURS,

    "one_day": HuaweiGuestNetworkDuration.ONE_DAY,

    "unlimited": HuaweiGuestNetworkDuration.UNLIMITED,

}



_WIFI_SECURITY_MAP: dict[str, bool] = {

    "encrypted": True,

    "open": False,

}





# ---------------------------

# ---------------------------





# ---------------------------
#   ServiceName
# ---------------------------
class ServiceName(StrEnum):
    ADD_TO_WHITELIST = "whitelist_add"
    ADD_TO_BLACKLIST = "blacklist_add"
    REMOVE_FROM_WHITELIST = "whitelist_remove"
    REMOVE_FROM_BLACKLIST = "blacklist_remove"
    GUEST_NETWORK_SETUP = "guest_network_setup"
    # 端口映射管理服务
    PORT_MAPPING_ADD = "port_mapping_add"
    PORT_MAPPING_REMOVE = "port_mapping_remove"
    PORT_MAPPING_LIST = "port_mapping_list"
    PORT_MAPPING_STATE = "port_mapping_state"
    # 端口触发服务
    PORT_TRIGGER_LIST = "port_trigger_list"
    PORT_TRIGGER_STATE = "port_trigger_state"
    PORT_TRIGGER_ADD = "port_trigger_add"
    PORT_TRIGGER_REMOVE = "port_trigger_remove"
    # UPnP 端口映射服务
    UPNP_PORT_MAPPING_LIST = "upnp_port_mapping_list"
    # WAN 重拨服务
    WAN_RECONNECT = "wan_reconnect"
    # DHCP 静态 IP 保留服务
    DHCP_STATIC_LEASE_LIST = "dhcp_static_lease_list"
    DHCP_STATIC_LEASE_ADD = "dhcp_static_lease_add"
    DHCP_STATIC_LEASE_REMOVE = "dhcp_static_lease_remove"
    DHCP_STATIC_LEASE_STATE = "dhcp_static_lease_state"
    # 路由功能开关服务
    UPNP_SET_ENABLED = "upnp_set_enabled"
    IPV6_SET_ENABLED = "ipv6_set_enabled"
    BAND_STEERING_SET_ENABLED = "band_steering_set_enabled"
    SMART_CONNECT_SET_ENABLED = "smart_connect_set_enabled"
    FIREWALL_SET_LEVEL = "firewall_set_level"
    DMZ_SET = "dmz_set"
    SCHEDULED_REBOOT_SET = "scheduled_reboot_set"
    # DDNS 动态域名服务
    DDNS_STATUS = "ddns_status"
    DDNS_SET_ENABLED = "ddns_set_enabled"
    # 设备管理服务（列表模式）
    DEVICE_SET_NAME = "device_set_name"
    DEVICE_SET_RATE_LIMIT = "device_set_rate_limit"
    DEVICE_REMOVE = "device_remove"
    # 通用 API 桥接
    API_GET = "api_get"
    API_SET = "api_set"
    # WiFi / SSID
    WIFI_RADIO_GET = "wifi_radio_get"
    WIFI_RADIO_SET_ENABLED = "wifi_radio_set_enabled"
    WLAN_WPS_GET = "wlan_wps_get"
    WPS_SET_ENABLED = "wps_set_enabled"
    MULTI_SSID_LIST = "multi_ssid_list"
    WIFI_TIMING_ACCELERATE_GET = "wifi_timing_accelerate_get"
    WIFI_TIMING_ACCELERATE_SET = "wifi_timing_accelerate_set"
    WLAN_WIFI_SYNC_GET = "wlan_wifi_sync_get"
    # LAN / DHCP
    LAN_CONFIG_GET = "lan_config_get"
    LAN_CONFIG_SET = "lan_config_set"
    LAN_ALL_GET = "lan_all_get"
    DHCP_SERVER_GET = "dhcp_server_get"
    DHCP_SERVER_SET = "dhcp_server_set"
    DEVICE_TYPE_LIST = "device_type_list"
    # WAN / IPv6 / 隧道 / VPN / IPTV
    WAN_LEARN_CONFIG_GET = "wan_learn_config_get"
    WAN_DIAGNOSE_GET = "wan_diagnose_get"
    IPV6_WAN_GET = "ipv6_wan_get"
    IPV6_WAN_SET = "ipv6_wan_set"
    IPV6_LAN_GET = "ipv6_lan_get"
    IPV6_LAN_SET = "ipv6_lan_set"
    ALG_GET = "alg_get"
    ALG_SET = "alg_set"
    TUNNEL_GET = "tunnel_get"
    TUNNEL_SET = "tunnel_set"
    SWAN_GET = "swan_get"
    SMART_VPN_GET = "smart_vpn_get"
    SMART_VPN_SET = "smart_vpn_set"
    IPTV_GET = "iptv_get"
    IPTV_SET = "iptv_set"
    # 安全 / 接入 / 防蹭网
    MAC_FILTER_LIST = "mac_filter_list"
    ACCESS_AUTH_GET = "access_auth_get"
    ACCESS_AUTH_SET = "access_auth_set"
    HOMESEC_GET = "homesec_get"
    HOMESEC_SET = "homesec_set"
    XLINK_LOCK_NET_GET = "xlink_lock_net_get"
    # 访客网络补充
    GUEST_NETWORK_LIMIT_RATE_GET = "guest_network_limit_rate_get"
    GUEST_NETWORK_LIMIT_RATE_SET = "guest_network_limit_rate_set"
    GUEST_NETWORK_REST_TIME_SET = "guest_network_rest_time_set"
    # 系统 / 时间 / 升级
    NTP_GET = "ntp_get"
    NTP_SET = "ntp_set"
    PROCESS_STATUS_GET = "process_status_get"
    ONLINE_STATE_GET = "online_state_get"
    ETH_NEGOTIATION_GET = "eth_negotiation_get"
    AUTO_UPGRADE_GET = "auto_upgrade_get"
    AUTO_UPGRADE_SET = "auto_upgrade_set"
    AUTO_UPGRADE_CHECK = "auto_upgrade_check"
    PASSWORD_RULE_GET = "password_rule_get"
    USER_ACCOUNT_GET = "user_account_get"
    SYSTEM_LANGUAGE_SET = "system_language_set"
    # 诊断 / 中继 / 存储 / 互联
    WIFI_SCAN = "wifi_scan"
    WIFI_SCAN_RESULT = "wifi_scan_result"
    REPEATER_STATE_GET = "repeater_state_get"
    REPEATER_DIAG_GET = "repeater_diag_get"
    REPEATER_DIAL_SET = "repeater_dial_set"
    NETDISK_INFO_GET = "netdisk_info_get"
    NETDISK_CODE_GET = "netdisk_code_get"
    NETDISK_CODE_SET = "netdisk_code_set"
    HILINK_STATUS_GET = "hilink_status_get"
    SLAVE_SETUP_SET = "slave_setup_set"
    MULTI_HOST_INFO_GET = "multi_host_info_get"
    SYSTEM_MODE_GET = "system_mode_get"
    WIFI_DIAG_GET = "wifi_diag_get"
    LAN_HOST_GET = "lan_host_get"
    DIAGNOSTICS_COLLECT = "diagnostics_collect"
    DIAGNOSTICS_STATUS = "diagnostics_status"
    DIAGNOSTICS_DEVLIST = "diagnostics_devlist"
    DIAGNOSTICS_DOWNLOAD = "diagnostics_download"
    WPS_PAIR_START = "wps_pair_start"
    CONFIG_EXPORT = "config_export"
    CONFIG_IMPORT = "config_import"





@dataclass

class ServiceDescription:

    name: str

    schema: vol.Schema





SERVICES = [

    ServiceDescription(

        schema=vol.Schema({vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR}),

        name=ServiceName.ADD_TO_WHITELIST,

    ),

    ServiceDescription(

        schema=vol.Schema({vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR}),

        name=ServiceName.REMOVE_FROM_WHITELIST,

    ),

    ServiceDescription(

        schema=vol.Schema({vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR}),

        name=ServiceName.ADD_TO_BLACKLIST,

    ),

    ServiceDescription(

        schema=vol.Schema({vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR}),

        name=ServiceName.REMOVE_FROM_BLACKLIST,

    ),

    ServiceDescription(

        name=ServiceName.GUEST_NETWORK_SETUP,

        schema=vol.Schema(

            {

                vol.Required(_FIELD_SERIAL_NUMBER): vol.Coerce(str),

                vol.Required(_FIELD_ENABLED): vol.Coerce(bool),

                vol.Required(_FIELD_SSID): vol.Coerce(str),

                vol.Required(_FIELD_DURATION): vol.In(list(_WIFI_DURATION_MAP.keys())),

                vol.Required(_FIELD_SECURITY): vol.In(list(_WIFI_SECURITY_MAP.keys())),

                vol.Required(_FIELD_PASSWORD): vol.All(
                    vol.Coerce(str), vol.Length(min=8)
                ),
            }
        ),
    ),
    # 端口映射管理服务
    ServiceDescription(
        name=ServiceName.PORT_MAPPING_ADD,
        schema=vol.Schema(
            {
                vol.Required("internal_host"): vol.Coerce(str),
                vol.Required("internal_port"): vol.Coerce(int),
                vol.Required("external_port"): vol.Coerce(int),
                vol.Required("protocol"): vol.In(["TCP", "UDP"]),
                vol.Optional("description"): vol.Coerce(str),
                vol.Optional("enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.PORT_MAPPING_REMOVE,
        schema=vol.Schema(
            {
                vol.Required("external_port"): vol.Coerce(int),
                vol.Required("protocol"): vol.In(["TCP", "UDP"]),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.PORT_MAPPING_LIST,
        schema=vol.Schema({}),
    ),
    ServiceDescription(
        name=ServiceName.PORT_MAPPING_STATE,
        schema=vol.Schema(
            {
                vol.Required("port_mapping_id"): vol.Coerce(str),
                vol.Required("enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.PORT_TRIGGER_LIST,
        schema=vol.Schema({}),
    ),
    ServiceDescription(
        name=ServiceName.PORT_TRIGGER_STATE,
        schema=vol.Schema(
            {
                vol.Required("port_trigger_id"): vol.Coerce(str),
                vol.Required("enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.PORT_TRIGGER_ADD,
        schema=vol.Schema(
            {
                vol.Required("name"): vol.Coerce(str),
                vol.Required("application_id"): vol.Coerce(str),
                vol.Optional("enabled", default=False): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.PORT_TRIGGER_REMOVE,
        schema=vol.Schema(
            {
                vol.Required("port_trigger_id"): vol.Coerce(str),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.UPNP_PORT_MAPPING_LIST,
        schema=vol.Schema({}),
    ),
    ServiceDescription(
        name=ServiceName.WAN_RECONNECT,
        schema=vol.Schema({}),
    ),
    ServiceDescription(
        name=ServiceName.DHCP_STATIC_LEASE_LIST,
        schema=vol.Schema({}),
    ),
    ServiceDescription(
        name=ServiceName.DHCP_STATIC_LEASE_ADD,
        schema=vol.Schema(
            {
                vol.Required("ip_address"): vol.Coerce(str),
                vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR,
                vol.Optional("enabled", default=True): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.DHCP_STATIC_LEASE_REMOVE,
        schema=vol.Schema({vol.Required("lease_id"): vol.Coerce(str)}),
    ),
    ServiceDescription(
        name=ServiceName.DHCP_STATIC_LEASE_STATE,
        schema=vol.Schema(
            {
                vol.Required("lease_id"): vol.Coerce(str),
                vol.Required("enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.UPNP_SET_ENABLED,
        schema=vol.Schema({vol.Required("enabled"): vol.Coerce(bool)}),
    ),
    ServiceDescription(
        name=ServiceName.IPV6_SET_ENABLED,
        schema=vol.Schema({vol.Required("enabled"): vol.Coerce(bool)}),
    ),
    ServiceDescription(
        name=ServiceName.BAND_STEERING_SET_ENABLED,
        schema=vol.Schema({vol.Required("enabled"): vol.Coerce(bool)}),
    ),
    ServiceDescription(
        name=ServiceName.SMART_CONNECT_SET_ENABLED,
        schema=vol.Schema({vol.Required("enabled"): vol.Coerce(bool)}),
    ),
    ServiceDescription(
        name=ServiceName.FIREWALL_SET_LEVEL,
        schema=vol.Schema({vol.Required("level"): vol.Coerce(str)}),
    ),
    ServiceDescription(
        name=ServiceName.DMZ_SET,
        schema=vol.Schema(
            {
                vol.Required("enabled"): vol.Coerce(bool),
                vol.Optional("ip_address"): vol.Coerce(str),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.SCHEDULED_REBOOT_SET,
        schema=vol.Schema(
            {
                vol.Required("enabled"): vol.Coerce(bool),
                vol.Optional("reboot_time"): vol.Coerce(str),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.DDNS_STATUS,
        schema=vol.Schema({}),
    ),
    ServiceDescription(
        name=ServiceName.DDNS_SET_ENABLED,
        schema=vol.Schema({vol.Required("enabled"): vol.Coerce(bool)}),
    ),
    ServiceDescription(
        name=ServiceName.DEVICE_SET_NAME,
        schema=vol.Schema(
            {
                vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR,
                vol.Required("name"): vol.Coerce(str),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.DEVICE_SET_RATE_LIMIT,
        schema=vol.Schema(
            {
                vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR,
                vol.Optional("enabled"): vol.Coerce(bool),
                vol.Optional("upload_kbps"): vol.Coerce(int),
                vol.Optional("download_kbps"): vol.Coerce(int),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.DEVICE_REMOVE,
        schema=vol.Schema({vol.Required(_FIELD_MAC_ADDRESS): _CV_MAC_ADDR}),
    ),
    # 通用 API 桥接
    ServiceDescription(
        name=ServiceName.API_GET,
        schema=vol.Schema(
            {vol.Required("endpoint"): vol.In(list(RAW_API_ENDPOINTS.keys()))}
        ),
    ),
    ServiceDescription(
        name=ServiceName.API_SET,
        schema=vol.Schema(
            {
                vol.Required("endpoint"): vol.In(list(RAW_API_ENDPOINTS.keys())),
                vol.Required("data"): dict,
                vol.Optional("action"): vol.In(
                    ["create", "update", "delete", "SendSettings", "check"]
                ),
            }
        ),
    ),
    # WiFi / SSID
    ServiceDescription(name=ServiceName.WIFI_RADIO_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.WIFI_RADIO_SET_ENABLED,
        schema=vol.Schema(
            {
                vol.Required("frequency"): vol.In(["2.4G", "5G"]),
                vol.Required("enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(name=ServiceName.WLAN_WPS_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.WPS_SET_ENABLED,
        schema=vol.Schema({vol.Required("enabled"): vol.Coerce(bool)}),
    ),
    ServiceDescription(name=ServiceName.MULTI_SSID_LIST, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.WIFI_TIMING_ACCELERATE_GET, schema=vol.Schema({})
    ),
    ServiceDescription(
        name=ServiceName.WIFI_TIMING_ACCELERATE_SET,
        schema=vol.Schema(
            {
                vol.Required("enabled"): vol.Coerce(bool),
                vol.Optional("data"): dict,
            }
        ),
    ),
    ServiceDescription(name=ServiceName.WLAN_WIFI_SYNC_GET, schema=vol.Schema({})),
    # LAN / DHCP
    ServiceDescription(name=ServiceName.LAN_CONFIG_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.LAN_CONFIG_SET,
        schema=vol.Schema(
            {
                vol.Optional("ip_address"): vol.Coerce(str),
                vol.Optional("netmask"): vol.Coerce(str),
                vol.Optional("dhcp_enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(name=ServiceName.LAN_ALL_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.DHCP_SERVER_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.DHCP_SERVER_SET,
        schema=vol.Schema(
            {
                vol.Optional("start_ip"): vol.Coerce(str),
                vol.Optional("end_ip"): vol.Coerce(str),
                vol.Optional("lease_time"): vol.Coerce(int),
                vol.Optional("enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(name=ServiceName.DEVICE_TYPE_LIST, schema=vol.Schema({})),
    # WAN / IPv6 / 隧道 / VPN / IPTV
    ServiceDescription(name=ServiceName.WAN_LEARN_CONFIG_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.WAN_DIAGNOSE_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.IPV6_WAN_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.IPV6_WAN_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.IPV6_LAN_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.IPV6_LAN_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.ALG_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.ALG_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.TUNNEL_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.TUNNEL_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.SWAN_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.SMART_VPN_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.SMART_VPN_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.IPTV_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.IPTV_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    # 安全 / 接入 / 防蹭网
    ServiceDescription(name=ServiceName.MAC_FILTER_LIST, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.ACCESS_AUTH_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.ACCESS_AUTH_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.HOMESEC_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.HOMESEC_SET,
        schema=vol.Schema(
            {
                vol.Optional("abfa_enabled"): vol.Coerce(bool),
                vol.Optional("stealnet_enabled"): vol.Coerce(bool),
            }
        ),
    ),
    ServiceDescription(name=ServiceName.XLINK_LOCK_NET_GET, schema=vol.Schema({})),
    # 访客网络补充
    ServiceDescription(
        name=ServiceName.GUEST_NETWORK_LIMIT_RATE_GET, schema=vol.Schema({})
    ),
    ServiceDescription(
        name=ServiceName.GUEST_NETWORK_LIMIT_RATE_SET,
        schema=vol.Schema(
            {
                vol.Required("enabled"): vol.Coerce(bool),
                vol.Optional("peak_rate"): vol.Coerce(int),
                vol.Optional("down_peak_rate"): vol.Coerce(int),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.GUEST_NETWORK_REST_TIME_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    # 系统 / 时间 / 升级
    ServiceDescription(name=ServiceName.NTP_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.NTP_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.PROCESS_STATUS_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.ONLINE_STATE_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.ETH_NEGOTIATION_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.AUTO_UPGRADE_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.AUTO_UPGRADE_SET,
        schema=vol.Schema(
            {
                vol.Required("enabled"): vol.Coerce(bool),
                vol.Optional("start_time"): vol.Coerce(str),
                vol.Optional("end_time"): vol.Coerce(str),
            }
        ),
    ),
    ServiceDescription(name=ServiceName.AUTO_UPGRADE_CHECK, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.PASSWORD_RULE_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.USER_ACCOUNT_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.SYSTEM_LANGUAGE_SET,
        schema=vol.Schema({vol.Required("language"): vol.Coerce(str)}),
    ),
    # 诊断 / 中继 / 存储 / 互联
    ServiceDescription(name=ServiceName.WIFI_SCAN, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.WIFI_SCAN_RESULT, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.REPEATER_STATE_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.REPEATER_DIAG_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.REPEATER_DIAL_SET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.NETDISK_INFO_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.NETDISK_CODE_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.NETDISK_CODE_SET,
        schema=vol.Schema({vol.Required("data"): dict}),
    ),
    ServiceDescription(name=ServiceName.HILINK_STATUS_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.SLAVE_SETUP_SET,
        schema=vol.Schema({vol.Required("allow"): vol.Coerce(bool)}),
    ),
    ServiceDescription(name=ServiceName.MULTI_HOST_INFO_GET, schema=vol.Schema({})),
    ServiceDescription(name=ServiceName.SYSTEM_MODE_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.WIFI_DIAG_GET,
        schema=vol.Schema(
            {
                vol.Optional("band", default="both"): vol.In(["2.4G", "5G", "both"]),
            }
        ),
    ),
    ServiceDescription(name=ServiceName.LAN_HOST_GET, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.DIAGNOSTICS_COLLECT,
        schema=vol.Schema({vol.Optional("mac_address"): _CV_MAC_ADDR}),
    ),
    ServiceDescription(name=ServiceName.DIAGNOSTICS_STATUS, schema=vol.Schema({})),
    ServiceDescription(
        name=ServiceName.DIAGNOSTICS_DEVLIST, schema=vol.Schema({})
    ),
    ServiceDescription(
        name=ServiceName.DIAGNOSTICS_DOWNLOAD,
        schema=vol.Schema({vol.Required("path"): cv.string}),
    ),
    ServiceDescription(
        name=ServiceName.WPS_PAIR_START,
        schema=vol.Schema(
            {
                vol.Required("mode"): vol.In(["pbc", "client-pin", "ap-pin"]),
                vol.Optional("pin"): cv.string,
                vol.Optional("ap_pin_type", default="default"): vol.In(
                    ["default", "random"]
                ),
            }
        ),
    ),
    ServiceDescription(
        name=ServiceName.CONFIG_EXPORT,
        schema=vol.Schema({vol.Required("path"): cv.string}),
    ),
    ServiceDescription(
        name=ServiceName.CONFIG_IMPORT,
        schema=vol.Schema(
            {
                vol.Required("path"): cv.string,
                vol.Optional("wait_restart", default=False): vol.Coerce(bool),
            }
        ),
    ),
]





# ---------------------------

#   _find_coordinator

# ---------------------------

def _find_coordinator(

    hass: HomeAssistant, device_mac: MAC_ADDR

) -> HuaweiDataUpdateCoordinator | None:

    _LOGGER.debug("Looking for coordinators with device '%s'", device_mac)

    for key, item in hass.data[DOMAIN].items():

        if key == DATA_KEY_SERVICES:

            continue

        coordinator = item.get(DATA_KEY_COORDINATOR)

        if not coordinator or not isinstance(coordinator, HuaweiDataUpdateCoordinator):

            continue

        for mac, _ in coordinator.connected_devices.items():

            if mac == device_mac:

                _LOGGER.debug(

                    "Found coordinator %s for '%s'", coordinator.name, device_mac

                )

                return coordinator





# ---------------------------

#   _find_coordinator_serial

# ---------------------------

def _find_coordinator_serial(

    hass: HomeAssistant, serial_number: str

) -> HuaweiDataUpdateCoordinator | None:

    _LOGGER.debug("Looking for coordinators with serial number '%s'", str)

    for key, item in hass.data[DOMAIN].items():

        if key == DATA_KEY_SERVICES:

            continue

        coordinator = item.get(DATA_KEY_COORDINATOR)

        if not coordinator or not isinstance(coordinator, HuaweiDataUpdateCoordinator):

            continue

        if coordinator.primary_router_serial_number == serial_number.upper():

            _LOGGER.debug(

                "Found coordinator %s with serial number '%s'",

                coordinator.name,

                serial_number,

            )

            return coordinator





# ---------------------------

#   _async_add_to_whitelist

# ---------------------------

async def _async_add_to_whitelist(hass: HomeAssistant, service: ServiceCall):

    """Service to add device to whitelist."""

    device_mac = service.data[_FIELD_MAC_ADDRESS].upper()

    coordinator = _find_coordinator(hass, device_mac)

    if not coordinator:

        raise HomeAssistantError(

            f"Can not find coordinator for mac address '{device_mac}'"

        )



    _LOGGER.debug(

        "Service '%s' called for device mac '%s' with %s",

        service.service,

        device_mac,

        coordinator.name,

    )

    try:

        success = await coordinator.primary_router_api.apply_wlan_filter(

            FilterMode.WHITELIST, FilterAction.ADD, device_mac

        )

    except Exception as ex:

        raise HomeAssistantError(str(ex))



    if not success:

        raise HomeAssistantError("Can not add item to whitelist")





# ---------------------------

#   _async_add_to_blacklist

# ---------------------------

async def _async_add_to_blacklist(hass: HomeAssistant, service: ServiceCall):

    """Service to add device to whitelist."""

    device_mac = service.data[_FIELD_MAC_ADDRESS].upper()

    coordinator = _find_coordinator(hass, device_mac)

    if not coordinator:

        raise HomeAssistantError(

            f"Can not find coordinator for mac address '{device_mac}'"

        )



    _LOGGER.debug(

        "Service '%s' called for device mac '%s' with %s",

        service.service,

        device_mac,

        coordinator.name,

    )

    try:

        success = await coordinator.primary_router_api.apply_wlan_filter(

            FilterMode.BLACKLIST, FilterAction.ADD, device_mac

        )

    except Exception as ex:

        raise HomeAssistantError(str(ex))



    if not success:

        raise HomeAssistantError("Can not add item to blacklist")





# ---------------------------

#   _async_remove_from_whitelist

# ---------------------------

async def _async_remove_from_whitelist(hass: HomeAssistant, service: ServiceCall):

    """Service to remove device from whitelist."""

    device_mac = service.data[_FIELD_MAC_ADDRESS].upper()

    coordinator = _find_coordinator(hass, device_mac)

    if not coordinator:

        raise HomeAssistantError(

            f"Can not find coordinator for mac address '{device_mac}'"

        )



    _LOGGER.debug(

        "Service '%s' called for device mac '%s' with %s",

        service.service,

        device_mac,

        coordinator.name,

    )



    try:

        success = await coordinator.primary_router_api.apply_wlan_filter(

            FilterMode.WHITELIST, FilterAction.REMOVE, device_mac

        )

    except Exception as ex:

        raise HomeAssistantError(str(ex))



    if not success:

        raise HomeAssistantError("Can not remove item from whitelist")





# ---------------------------

#   _async_remove_from_blacklist

# ---------------------------

async def _async_remove_from_blacklist(hass: HomeAssistant, service: ServiceCall):

    """Service to remove device from whitelist."""

    device_mac = service.data[_FIELD_MAC_ADDRESS].upper()

    coordinator = _find_coordinator(hass, device_mac)

    if not coordinator:

        raise HomeAssistantError(

            f"Can not find coordinator for mac address '{device_mac}'"

        )



    _LOGGER.debug(

        "Service '%s' called for device mac '%s' with %s",

        service.service,

        device_mac,

        coordinator.name,

    )

    try:

        success = await coordinator.primary_router_api.apply_wlan_filter(

            FilterMode.BLACKLIST, FilterAction.REMOVE, device_mac

        )

    except Exception as ex:

        raise HomeAssistantError(str(ex))



    if not success:

        raise HomeAssistantError("Can not remove item from blacklist")





# ---------------------------

#   _async_setup_guest_network

# ---------------------------

async def _async_setup_guest_network(hass: HomeAssistant, service: ServiceCall):

    """Service to set port poe settings."""

    serial_number = service.data[_FIELD_SERIAL_NUMBER]



    coordinator = _find_coordinator_serial(hass, serial_number)

    if not coordinator:

        raise HomeAssistantError(

            f"Can not find coordinator with primary router's serial number '{serial_number}'"

        )



    _LOGGER.debug(

        "Service '%s' called for serial number '%s' with name %s",

        service.service,

        serial_number,

        coordinator.name,

    )



    try:

        enabled: bool = service.data[_FIELD_ENABLED]

        ssid: str = service.data[_FIELD_SSID]

        duration: HuaweiGuestNetworkDuration = _WIFI_DURATION_MAP[

            service.data[_FIELD_DURATION]

        ]

        secured: bool = _WIFI_SECURITY_MAP[service.data[_FIELD_SECURITY]]

        password: str | None = service.data[_FIELD_PASSWORD]



        await coordinator.primary_router_api.set_guest_network_state(

            enabled, ssid, duration, secured, password

        )

    except Exception as ex:
        raise HomeAssistantError(str(ex))


# ---------------------------
#   _async_port_mapping_add
# ---------------------------
async def _async_port_mapping_add(hass: HomeAssistant, service: ServiceCall):
    """Service to add port mapping (Q6: two-step Application + mapping)."""
    data = service.data
    name = data["name"]
    mac_address = data["mac_address"]
    host_ip = data["host_ip"]
    protocol = data.get("protocol", "TCP")
    external_port = str(data["external_port"])
    internal_port = str(data.get("internal_port", data["external_port"]))
    enabled = data.get("enabled", True)
    host_name = data.get("host_name", "")

    _LOGGER.debug(
        "Service '%s' called: name=%s, mac=%s, ip=%s, proto=%s, ext=%s, int=%s",
        service.service, name, mac_address, host_ip, protocol,
        external_port, internal_port,
    )

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        success = await coordinator.primary_router_api.add_port_mapping(
            name=name,
            mac_address=mac_address,
            host_ip=host_ip,
            protocol=protocol,
            external_port=external_port,
            internal_port=internal_port,
            enabled=enabled,
            host_name=host_name,
        )
        if not success:
            raise HomeAssistantError("Router rejected the add (check logs)")

        _LOGGER.info("Port mapping added: %s (%s)", name, host_ip)

    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"Error adding port mapping: {ex}")


# ---------------------------
#   _async_port_mapping_remove
# ---------------------------
async def _async_port_mapping_remove(hass: HomeAssistant, service: ServiceCall):
    """Service to remove port mapping by port_mapping_id."""
    data = service.data
    mapping_id = data.get("port_mapping_id", "")

    _LOGGER.debug(
        "Service '%s' called: port_mapping_id=%s",
        service.service, mapping_id,
    )

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        success = await coordinator.primary_router_api.remove_port_mapping(mapping_id)
        if not success:
            raise HomeAssistantError("Router rejected the remove (check logs)")

        _LOGGER.info("Port mapping removed: %s", mapping_id)

    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"Error removing port mapping: {ex}")


# ---------------------------
#   _async_port_mapping_list
# ---------------------------
async def _async_port_mapping_list(hass: HomeAssistant, service: ServiceCall):
    """Service to list port mappings."""
    _LOGGER.debug("Service '%s' called", service.service)

    # 查找任意一个coordinator
    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    # 返回端口映射列表
    mappings = []
    for mapping in await coordinator.primary_router_api.get_port_mappings():
        mappings.append({
            "id": mapping.id,
            "name": mapping.name,
            "enabled": mapping.enabled,
            "host_ip": mapping.host_ip,
            "host_name": mapping.host_name,
        })

    _LOGGER.info("Port mappings listed: %d mappings found", len(mappings))
    return mappings


# ---------------------------
#   _async_port_mapping_state
# ---------------------------
async def _async_port_mapping_state(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable a port mapping."""
    port_mapping_id = service.data["port_mapping_id"]
    enabled = service.data["enabled"]

    _LOGGER.info(
        "Service '%s' called: port_mapping_id=%s, enabled=%s",
        service.service, port_mapping_id, enabled,
    )

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        await coordinator.primary_router_api.set_port_mapping_state(
            port_mapping_id, enabled
        )
        _LOGGER.info("Port mapping %s set to enabled=%s", port_mapping_id, enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting port mapping state: {ex}")


# ---------------------------
#   _async_port_trigger_list
# ---------------------------
async def _async_port_trigger_list(hass: HomeAssistant, service: ServiceCall):
    """Service to list port trigger rules."""
    _LOGGER.debug("Service '%s' called", service.service)

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        triggers = []
        for t in await coordinator.primary_router_api.get_port_triggers():
            triggers.append({
                "id": t.id,
                "name": t.name,
                "enabled": t.enabled,
            })
        _LOGGER.info("Port triggers listed: %d found", len(triggers))
        return triggers
    except Exception as ex:
        raise HomeAssistantError(f"Error listing port triggers: {ex}")


# ---------------------------
#   _async_port_trigger_state
# ---------------------------
async def _async_port_trigger_state(hass: HomeAssistant, service: ServiceCall):
    """Service to enable or disable a port trigger rule."""
    data = service.data
    trigger_id = data["port_trigger_id"]
    enabled = data["enabled"]

    _LOGGER.debug(
        "Service '%s' called: port_trigger_id=%s, enabled=%s",
        service.service, trigger_id, enabled,
    )

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        await coordinator.primary_router_api.set_port_trigger_state(trigger_id, enabled)
        _LOGGER.info("Port trigger %s -> enabled=%s", trigger_id, enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error toggling port trigger: {ex}")


# ---------------------------
#   _async_port_trigger_add
# ---------------------------
async def _async_port_trigger_add(hass: HomeAssistant, service: ServiceCall):
    """Service to add a new port trigger rule."""
    data = service.data
    name = data["name"]
    application_id = data["application_id"]
    enabled = data.get("enabled", False)

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        success = await coordinator.primary_router_api.add_port_trigger(
            name, application_id, enabled
        )
        if not success:
            raise HomeAssistantError("Router rejected add (need valid ApplicationID)")
        _LOGGER.info("Port trigger added: %s", name)
    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"Error adding port trigger: {ex}")


# ---------------------------
#   _async_port_trigger_remove
# ---------------------------
async def _async_port_trigger_remove(hass: HomeAssistant, service: ServiceCall):
    """Service to remove a port trigger rule."""
    trigger_id = service.data["port_trigger_id"]

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        success = await coordinator.primary_router_api.remove_port_trigger(trigger_id)
        if not success:
            raise HomeAssistantError("Router rejected remove (check logs)")
        _LOGGER.info("Port trigger removed: %s", trigger_id)
    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"Error removing port trigger: {ex}")


# ---------------------------
#   _async_upnp_port_mapping_list
# ---------------------------
async def _async_upnp_port_mapping_list(hass: HomeAssistant, service: ServiceCall):
    """Service to list UPnP port mapping rules."""
    _LOGGER.debug("Service '%s' called", service.service)

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        mappings = []
        for m in await coordinator.primary_router_api.get_upnp_port_mappings():
            mappings.append({
                "external_port": m.external_port,
                "internal_port": m.internal_port,
                "internal_client": m.internal_client,
                "protocol": m.protocol,
                "enabled": m.enabled,
                "description": m.description,
            })
        _LOGGER.info("UPnP port mappings listed: %d found", len(mappings))
        return mappings
    except Exception as ex:
        raise HomeAssistantError(f"Error listing UPnP port mappings: {ex}")


# ---------------------------
#   _async_wan_reconnect
# ---------------------------
async def _async_wan_reconnect(hass: HomeAssistant, service: ServiceCall):
    """Service to trigger a PPPoE WAN disconnect + reconnect cycle."""
    _LOGGER.info("Service '%s' called - initiating WAN reconnect", service.service)

    coordinator = None
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            break

    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")

    try:
        from .client.classes import Action

        await coordinator.primary_router_api.execute_action(Action.WAN_RECONNECT)
        _LOGGER.info("WAN reconnect cycle completed successfully")

    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"WAN reconnect failed: {ex}") from ex


# ---------------------------
#   _find_any_coordinator
# ---------------------------
def _find_any_coordinator(hass: HomeAssistant) -> HuaweiDataUpdateCoordinator | None:
    """Return the first Huawei router coordinator, or None."""
    for key, item in hass.data[DOMAIN].items():
        if key == DATA_KEY_SERVICES:
            continue
        coordinator = item.get(DATA_KEY_COORDINATOR)
        if coordinator and isinstance(coordinator, HuaweiDataUpdateCoordinator):
            return coordinator
    return None


# ---------------------------
#   _async_dhcp_static_lease_list
# ---------------------------
async def _async_dhcp_static_lease_list(hass: HomeAssistant, service: ServiceCall):
    """Service to list DHCP static lease (MAC-IP binding) entries."""
    _LOGGER.debug("Service '%s' called", service.service)
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        leases = []
        for lease in await coordinator.primary_router_api.get_dhcp_static_leases():
            leases.append({
                "id": lease.id,
                "ip_address": lease.ip_address,
                "mac_address": lease.mac_address,
                "enabled": lease.enabled,
            })
        _LOGGER.info("DHCP static leases listed: %d found", len(leases))
        return leases
    except Exception as ex:
        raise HomeAssistantError(f"Error listing DHCP static leases: {ex}")


# ---------------------------
#   _async_dhcp_static_lease_add
# ---------------------------
async def _async_dhcp_static_lease_add(hass: HomeAssistant, service: ServiceCall):
    """Service to add a DHCP static lease."""
    ip_address = service.data["ip_address"]
    mac_address = service.data[_FIELD_MAC_ADDRESS]
    enabled = service.data.get("enabled", True)
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        success = await coordinator.primary_router_api.add_dhcp_static_lease(
            ip_address, mac_address, enabled
        )
        if not success:
            raise HomeAssistantError("Router rejected the add (check logs)")
        _LOGGER.info("DHCP static lease added: %s -> %s", mac_address, ip_address)
    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"Error adding DHCP static lease: {ex}")


# ---------------------------
#   _async_dhcp_static_lease_remove
# ---------------------------
async def _async_dhcp_static_lease_remove(hass: HomeAssistant, service: ServiceCall):
    """Service to remove a DHCP static lease."""
    lease_id = service.data["lease_id"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        success = await coordinator.primary_router_api.remove_dhcp_static_lease(lease_id)
        if not success:
            raise HomeAssistantError("Router rejected the remove (check logs)")
        _LOGGER.info("DHCP static lease removed: %s", lease_id)
    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"Error removing DHCP static lease: {ex}")


# ---------------------------
#   _async_dhcp_static_lease_state
# ---------------------------
async def _async_dhcp_static_lease_state(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable a DHCP static lease."""
    lease_id = service.data["lease_id"]
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_dhcp_static_lease_state(lease_id, enabled)
        _LOGGER.info("DHCP static lease %s -> enabled=%s", lease_id, enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error toggling DHCP static lease: {ex}")


# ---------------------------
#   _async_upnp_set_enabled
# ---------------------------
async def _async_upnp_set_enabled(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable UPnP."""
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_upnp_enabled(enabled)
        _LOGGER.info("UPnP set to enabled=%s", enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting UPnP state: {ex}")


# ---------------------------
#   _async_ipv6_set_enabled
# ---------------------------
async def _async_ipv6_set_enabled(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable IPv6."""
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_ipv6_enabled(enabled)
        _LOGGER.info("IPv6 set to enabled=%s", enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting IPv6 state: {ex}")


# ---------------------------
#   _async_band_steering_set_enabled
# ---------------------------
async def _async_band_steering_set_enabled(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable 双频优选 (band steering)."""
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_band_steering_enabled(enabled)
        _LOGGER.info("Band steering set to enabled=%s", enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting band steering: {ex}")


# ---------------------------
#   _async_smart_connect_set_enabled
# ---------------------------
async def _async_smart_connect_set_enabled(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable 智能连接 (smart connect)."""
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_smart_connect_enabled(enabled)
        _LOGGER.info("Smart connect set to enabled=%s", enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting smart connect: {ex}")


# ---------------------------
#   _async_firewall_set_level
# ---------------------------
async def _async_firewall_set_level(hass: HomeAssistant, service: ServiceCall):
    """Service to set firewall level."""
    level = service.data["level"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_firewall_level(level)
        _LOGGER.info("Firewall level set to %s", level)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting firewall level: {ex}")


# ---------------------------
#   _async_dmz_set
# ---------------------------
async def _async_dmz_set(hass: HomeAssistant, service: ServiceCall):
    """Service to configure DMZ host."""
    enabled = service.data["enabled"]
    ip_address = service.data.get("ip_address", "")
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_dmz(enabled, ip_address)
        _LOGGER.info("DMZ set: enabled=%s, ip=%s", enabled, ip_address)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting DMZ: {ex}")


# ---------------------------
#   _async_scheduled_reboot_set
# ---------------------------
async def _async_scheduled_reboot_set(hass: HomeAssistant, service: ServiceCall):
    """Service to configure scheduled reboot."""
    enabled = service.data["enabled"]
    reboot_time = service.data.get("reboot_time", "")
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_scheduled_reboot(enabled, reboot_time)
        _LOGGER.info("Scheduled reboot set: enabled=%s, time=%s", enabled, reboot_time)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting scheduled reboot: {ex}")


# ---------------------------
#   _async_ddns_status
# ---------------------------
async def _async_ddns_status(hass: HomeAssistant, service: ServiceCall):
    """Service to return DDNS status."""
    _LOGGER.debug("Service '%s' called", service.service)
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.get_ddns_status()
    except Exception as ex:
        raise HomeAssistantError(f"Error getting DDNS status: {ex}")


# ---------------------------
#   _async_ddns_set_enabled
# ---------------------------
async def _async_ddns_set_enabled(hass: HomeAssistant, service: ServiceCall):
    """Service to enable/disable DDNS."""
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_ddns_enabled(enabled)
        _LOGGER.info("DDNS set to enabled=%s", enabled)
    except Exception as ex:
        raise HomeAssistantError(f"Error setting DDNS state: {ex}")


# ---------------------------
#   _async_device_set_name
# ---------------------------
async def _async_device_set_name(hass: HomeAssistant, service: ServiceCall):
    """Service to rename a connected device."""
    mac_address = service.data[_FIELD_MAC_ADDRESS]
    name = service.data["name"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_device_name(mac_address, name)
        _LOGGER.info("Device %s renamed to %s", mac_address, name)
    except Exception as ex:
        raise HomeAssistantError(f"Error renaming device: {ex}")


# ---------------------------
#   _async_device_set_rate_limit
# ---------------------------
async def _async_device_set_rate_limit(hass: HomeAssistant, service: ServiceCall):
    """Service to set per-device QoS rate limit."""
    mac_address = service.data[_FIELD_MAC_ADDRESS]
    enabled = service.data.get("enabled")
    upload_kbps = service.data.get("upload_kbps")
    download_kbps = service.data.get("download_kbps")
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_device_rate_limit(
            mac_address,
            enabled=enabled,
            upload_kbps=upload_kbps,
            download_kbps=download_kbps,
        )
        _LOGGER.info(
            "Device %s rate limit set: enabled=%s, up=%s, down=%s",
            mac_address,
            enabled,
            upload_kbps,
            download_kbps,
        )
    except Exception as ex:
        raise HomeAssistantError(f"Error setting device rate limit: {ex}")


# ---------------------------
#   _async_device_remove
# ---------------------------
async def _async_device_remove(hass: HomeAssistant, service: ServiceCall):
    """Service to remove a known device entry."""
    mac_address = service.data[_FIELD_MAC_ADDRESS]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.remove_device(mac_address)
        _LOGGER.info("Device removed: %s", mac_address)
    except Exception as ex:
        raise HomeAssistantError(f"Error removing device: {ex}")


# ---------------------------
#   Web UI 剩余端点：通用读写助手
# ---------------------------
async def _async_read_config(
    hass: HomeAssistant, service: ServiceCall, path: str, label: str
):
    """GET 指定配置端点并返回原始 JSON（dict / list）。"""
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        _LOGGER.debug("Service '%s' called: GET %s", service.service, path)
        return await coordinator.primary_router_api.get_config(path)
    except Exception as ex:
        raise HomeAssistantError(f"{label}: {ex}")


async def _async_update_config(
    hass: HomeAssistant, service: ServiceCall, path: str, updates: dict, label: str
):
    """GET 完整对象 → 覆盖 updates → POST。"""
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        _LOGGER.debug(
            "Service '%s' called: update %s %s", service.service, path, updates
        )
        await coordinator.primary_router_api.update_config(
            path, updates, action="update"
        )
        _LOGGER.info("%s: %s", label, updates)
    except Exception as ex:
        raise HomeAssistantError(f"{label}: {ex}")


# ---------------------------
#   _async_api_get / _async_api_set（通用 API 桥接）
# ---------------------------
async def _async_api_get(hass: HomeAssistant, service: ServiceCall):
    """对白名单端点执行原始 GET，返回 {"status": ..., "data": ...}。"""
    endpoint = service.data["endpoint"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.get_endpoint_config(
            RAW_API_ENDPOINTS[endpoint]
        )
    except Exception as ex:
        raise HomeAssistantError(f"Error reading endpoint {endpoint}: {ex}")


async def _async_api_set(hass: HomeAssistant, service: ServiceCall):
    """对白名单端点执行原始 POST（可选 action）。"""
    endpoint = service.data["endpoint"]
    path = RAW_API_ENDPOINTS.get(endpoint)
    if not path:
        raise HomeAssistantError(f"Unknown API endpoint: {endpoint}")
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.set_endpoint_config(
            path, service.data["data"], service.data.get("action")
        )
    except Exception as ex:
        raise HomeAssistantError(f"Error writing endpoint {endpoint}: {ex}")


# ---------------------------
#   WiFi / SSID
# ---------------------------
async def _async_wifi_radio_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_WLAN_RADIO, "获取射频配置失败")


async def _async_wifi_radio_set_enabled(hass: HomeAssistant, service: ServiceCall):
    frequency = service.data["frequency"]
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_wifi_radio_enabled(frequency, enabled)
        _LOGGER.info("WiFi radio %s -> enabled=%s", frequency, enabled)
    except Exception as ex:
        raise HomeAssistantError(f"设置射频开关失败: {ex}")


async def _async_wlan_wps_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_WLAN_WPS, "获取 WPS 配置失败")


async def _async_wps_set_enabled(hass: HomeAssistant, service: ServiceCall):
    enabled = service.data["enabled"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_wps_enabled(enabled)
        _LOGGER.info("WPS set to enabled=%s", enabled)
    except Exception as ex:
        raise HomeAssistantError(f"设置 WPS 开关失败: {ex}")


async def _async_multi_ssid_list(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_MULTI_SSID, "获取多 SSID 列表失败")


async def _async_wifi_timing_accelerate_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_WLAN_TIMING_ACCELERATE, "获取 WiFi 加速配置失败"
    )


async def _async_wifi_timing_accelerate_set(hass: HomeAssistant, service: ServiceCall):
    updates: dict = {"Enable": service.data["enabled"]}
    updates.update(service.data.get("data") or {})
    await _async_update_config(
        hass, service, URL_WLAN_TIMING_ACCELERATE, updates, "设置 WiFi 加速失败"
    )


async def _async_wlan_wifi_sync_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_WLAN_WIFI_SYNC, "获取 WiFi 同步配置失败"
    )


# ---------------------------
#   LAN / DHCP
# ---------------------------
async def _async_lan_config_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_LAN, "获取 LAN 配置失败")


async def _async_lan_config_set(hass: HomeAssistant, service: ServiceCall):
    updates: dict = {}
    if "ip_address" in service.data:
        updates["IPAddress"] = service.data["ip_address"]
    if "netmask" in service.data:
        updates["SubnetMask"] = service.data["netmask"]
    if "dhcp_enabled" in service.data:
        updates["EnableDhcp"] = service.data["dhcp_enabled"]
    await _async_update_config(hass, service, URL_LAN, updates, "设置 LAN 配置失败")


async def _async_lan_all_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_LAN_ALL, "获取 LAN 完整配置失败")


async def _async_dhcp_server_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_LAN_SERVER, "获取 DHCP 服务配置失败")


async def _async_dhcp_server_set(hass: HomeAssistant, service: ServiceCall):
    updates: dict = {}
    if "start_ip" in service.data:
        updates["StartIPAddress"] = service.data["start_ip"]
    if "end_ip" in service.data:
        updates["EndIPAddress"] = service.data["end_ip"]
    if "lease_time" in service.data:
        updates["LeaseTime"] = service.data["lease_time"]
    if "enabled" in service.data:
        updates["Enable"] = service.data["enabled"]
    await _async_update_config(
        hass, service, URL_LAN_SERVER, updates, "设置 DHCP 服务失败"
    )


async def _async_device_type_list(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_LAN_DEVICE_TYPE, "获取设备类型列表失败"
    )


# ---------------------------
#   WAN / IPv6 / 隧道 / VPN / IPTV
# ---------------------------
async def _async_wan_learn_config_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_WAN_LEARN_CONFIG, "获取 WAN 学习配置失败"
    )


async def _async_wan_diagnose_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_WAN_DIAGNOSE, "获取 WAN 诊断信息失败"
    )


async def _async_ipv6_wan_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_IPV6_WAN, "获取 IPv6 WAN 配置失败")


async def _async_ipv6_wan_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_IPV6_WAN, service.data["data"], "设置 IPv6 WAN 配置失败"
    )


async def _async_ipv6_lan_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_IPV6_LAN, "获取 IPv6 LAN 配置失败")


async def _async_ipv6_lan_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_IPV6_LAN, service.data["data"], "设置 IPv6 LAN 配置失败"
    )


async def _async_alg_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_ALG, "获取 ALG 配置失败")


async def _async_alg_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(hass, service, URL_ALG, service.data["data"], "设置 ALG 失败")


async def _async_tunnel_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_TUNNEL, "获取隧道配置失败")


async def _async_tunnel_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_TUNNEL, service.data["data"], "设置隧道配置失败"
    )


async def _async_swan_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_SWAN, "获取 SWAN 配置失败")


async def _async_smart_vpn_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_SMART_VPN, "获取 Smart VPN 配置失败")


async def _async_smart_vpn_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_SMART_VPN, service.data["data"], "设置 Smart VPN 配置失败"
    )


async def _async_iptv_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_IPTV, "获取 IPTV 配置失败")


async def _async_iptv_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_IPTV, service.data["data"], "设置 IPTV 配置失败"
    )


# ---------------------------
#   安全 / 接入 / 防蹭网
# ---------------------------
async def _async_mac_filter_list(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_MAC_FILTER, "获取 MAC 过滤列表失败")


async def _async_access_auth_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_ACCESS_AUTH, "获取接入认证配置失败")


async def _async_access_auth_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_ACCESS_AUTH, service.data["data"], "设置接入认证失败"
    )


async def _async_homesec_get(hass: HomeAssistant, service: ServiceCall):
    """合并返回家庭安全（防暴力破解 + 防蹭网）配置。"""
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.get_homesec()
    except Exception as ex:
        raise HomeAssistantError(f"获取家庭安全配置失败: {ex}")


async def _async_homesec_set(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_homesec(
            abfa_enabled=service.data.get("abfa_enabled"),
            stealnet_enabled=service.data.get("stealnet_enabled"),
        )
        _LOGGER.info("家庭安全已更新: %s", dict(service.data))
    except Exception as ex:
        raise HomeAssistantError(f"设置家庭安全失败: {ex}")


async def _async_xlink_lock_net_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_XLINK_LOCK_NET, "获取防蹭网配置失败"
    )


# ---------------------------
#   访客网络补充
# ---------------------------
async def _async_guest_network_limit_rate_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(
        hass, service, URL_GUEST_NETWORK_LIMIT_RATE, "获取访客网络限速配置失败"
    )


async def _async_guest_network_limit_rate_set(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_guest_network_limit_rate(
            enabled=service.data["enabled"],
            peak_rate=service.data.get("peak_rate"),
            down_peak_rate=service.data.get("down_peak_rate"),
        )
        _LOGGER.info("访客网络限速已更新: %s", dict(service.data))
    except Exception as ex:
        raise HomeAssistantError(f"设置访客网络限速失败: {ex}")


async def _async_guest_network_rest_time_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass,
        service,
        URL_GUEST_NETWORK_REST_TIME,
        service.data["data"],
        "设置访客网络休息时间失败",
    )


# ---------------------------
#   系统 / 时间 / 升级
# ---------------------------
async def _async_ntp_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_NTP, "获取 NTP 配置失败")


async def _async_ntp_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(hass, service, URL_NTP, service.data["data"], "设置 NTP 失败")


async def _async_process_status_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_PROCESS_STATUS, "获取进程状态失败")


async def _async_online_state_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_ONLINE_STATE, "获取在线状态失败")


async def _async_eth_negotiation_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_ETH_NEGOTIATION, "获取网口协商配置失败")


async def _async_auto_upgrade_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_AUTO_UPGRADE, "获取自动升级配置失败")


async def _async_auto_upgrade_set(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_auto_upgrade(
            enabled=service.data["enabled"],
            start_time=service.data.get("start_time"),
            end_time=service.data.get("end_time"),
        )
        _LOGGER.info("自动升级已更新: %s", dict(service.data))
    except Exception as ex:
        raise HomeAssistantError(f"设置自动升级失败: {ex}")


async def _async_auto_upgrade_check(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.check_auto_upgrade()
    except Exception as ex:
        raise HomeAssistantError(f"触发在线升级检查失败: {ex}")


async def _async_password_rule_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_PASSWORD_RULE, "获取密码规则失败")


async def _async_user_account_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_USER_ACCOUNT, "获取用户账号信息失败")


async def _async_system_language_set(hass: HomeAssistant, service: ServiceCall):
    language = service.data["language"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_language(language)
        _LOGGER.info("系统语言已设置为 %s", language)
    except Exception as ex:
        raise HomeAssistantError(f"设置系统语言失败: {ex}")


# ---------------------------
#   诊断 / 中继 / 存储 / 互联
# ---------------------------
async def _async_wifi_scan(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.trigger_wifi_scan()
    except Exception as ex:
        raise HomeAssistantError(f"触发 WiFi 扫描失败: {ex}")


async def _async_wifi_scan_result(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_WIFI_SCAN_RESULT, "获取 WiFi 扫描结果失败")


async def _async_repeater_state_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_REPEATER_STATE, "获取中继状态失败")


async def _async_repeater_diag_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_REPEATER_DIAG, "获取中继诊断失败")


async def _async_repeater_dial_set(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_repeater_dial()
        _LOGGER.info("中继拨号已触发")
    except Exception as ex:
        raise HomeAssistantError(f"中继拨号失败: {ex}")


async def _async_netdisk_info_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_NETDISK_INFO, "获取网络存储信息失败")


async def _async_netdisk_code_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_NETDISK_CODE, "获取网络存储码失败")


async def _async_netdisk_code_set(hass: HomeAssistant, service: ServiceCall):
    await _async_update_config(
        hass, service, URL_NETDISK_CODE, service.data["data"], "设置网络存储码失败"
    )


async def _async_hilink_status_get(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.get_hilink_status()
    except Exception as ex:
        raise HomeAssistantError(f"获取 HiLink 状态失败: {ex}")


async def _async_slave_setup_set(hass: HomeAssistant, service: ServiceCall):
    allow = service.data["allow"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.set_slave_setup(allow)
        _LOGGER.info("HiLink 组网允许状态已设置为 %s", allow)
    except Exception as ex:
        raise HomeAssistantError(f"设置 HiLink 组网失败: {ex}")


async def _async_multi_host_info_get(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.get_multi_host_info()
    except Exception as ex:
        raise HomeAssistantError(f"获取多主机信息失败: {ex}")


async def _async_system_mode_get(hass: HomeAssistant, service: ServiceCall):
    return await _async_read_config(hass, service, URL_SYSTEM_MODE, "获取系统模式失败")


# ---------------------------
#   WiFi 射频详情 / LAN host / 诊断日志 / WPS 配对（最后一缺口）
# ---------------------------
async def _async_wifi_diag_get(hass: HomeAssistant, service: ServiceCall):
    """Return full radio parameters for one or both bands (真机已验证)."""
    band = service.data.get("band", "both")
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    result: dict = {}
    try:
        if band in ("2.4G", "both"):
            result["2.4G"] = await coordinator.primary_router_api.get_wlan_diag_basic("2.4G")
        if band in ("5G", "both"):
            result["5G"] = await coordinator.primary_router_api.get_wlan_diag_basic("5G")
    except Exception as ex:
        raise HomeAssistantError(f"获取 WiFi 射频详情失败: {ex}")
    return result


async def _async_lan_host_get(hass: HomeAssistant, service: ServiceCall):
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.get_lan_host()
    except Exception as ex:
        raise HomeAssistantError(f"获取 LAN host 配置失败: {ex}")


async def _async_diagnostics_collect(hass: HomeAssistant, service: ServiceCall):
    """Start diagnostics collection (async; poll diagnostics_status)."""
    mac = service.data.get("mac_address")
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.diagnostics_collect_start(mac)
        _LOGGER.info("Diagnostics collection started (mac=%s)", mac or "primary")
    except Exception as ex:
        raise HomeAssistantError(f"触发诊断收集失败: {ex}")


async def _async_diagnostics_status(hass: HomeAssistant, service: ServiceCall):
    """Return current collection state; result_ready=True when downloadable."""
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        state = await coordinator.primary_router_api.get_diagnostics_state()
    except Exception as ex:
        raise HomeAssistantError(f"查询诊断状态失败: {ex}")
    if not isinstance(state, dict):
        return {"raw": state}
    return {
        "state": state.get("DiagnosticsState"),
        "result_ready": state.get("ResultState") is True
        or state.get("ResultState") == 1,
    }


async def _async_diagnostics_devlist(hass: HomeAssistant, service: ServiceCall):
    """List devices that can be diagnosed (main router + satellite routers).

    返回的 MAC 可直接用于 diagnostics_collect 的 mac_address 参数，
    从而采集指定子路由（而非主路由）的诊断日志。真机验证：6 条。
    """
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        devices = await coordinator.primary_router_api.get_diagnostics_devlist()
    except Exception as ex:
        raise HomeAssistantError(f"获取可诊断设备列表失败: {ex}")
    return {
        "devices": [
            {
                "name": d.get("DeviceName"),
                "mac_address": d.get("MACAddress"),
                "is_main": d.get("IsMainDevice") is True,
                "url": d.get("URL"),
            }
            for d in devices
        ]
    }


async def _async_diagnostics_download(hass: HomeAssistant, service: ServiceCall):
    """Download the diagnostics package into the HA config directory."""
    path = service.data["path"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.diagnostics_download(path)
    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"下载诊断日志失败: {ex}")


async def _async_wps_pair_start(hass: HomeAssistant, service: ServiceCall):
    """Trigger a WPS pairing session (pbc / client-pin / ap-pin).

    ⚠️ 底层端点在 Q6 网线版上 404（前端硬编码 isSupportWps=false 的同源问题）。
    端点缺失时给出明确错误而不是裸 traceback。
    """
    mode = service.data["mode"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        await coordinator.primary_router_api.wps_pair_start(
            mode,
            pin=service.data.get("pin"),
            ap_pin_type=service.data.get("ap_pin_type", "default"),
        )
        _LOGGER.info("WPS pairing started: mode=%s", mode)
    except InvalidActionError:
        raise
    except Exception as ex:
        msg = str(ex)
        if "404" in msg:
            raise HomeAssistantError(
                "本机型未开放 WPS 管理端点（HTTP 404）——该功能在此固件上不可用"
            )
        raise HomeAssistantError(f"触发 WPS 配对失败: {ex}")


async def _async_config_export(hass: HomeAssistant, service: ServiceCall):
    """Export the router configuration backup to a local file (真机验证 ✅)."""
    path = service.data["path"]
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.config_export(path)
    except Exception as ex:
        raise HomeAssistantError(f"导出配置失败: {ex}")


async def _async_config_import(hass: HomeAssistant, service: ServiceCall):
    """⚠️ 破坏性：上传配置备份，路由器覆盖全部设置并重启。"""
    path = service.data["path"]
    wait_restart = service.data.get("wait_restart", False)
    coordinator = _find_any_coordinator(hass)
    if not coordinator:
        raise HomeAssistantError("Can not find any Huawei router coordinator")
    try:
        return await coordinator.primary_router_api.config_import(
            path, wait_restart=wait_restart
        )
    except HomeAssistantError:
        raise
    except Exception as ex:
        raise HomeAssistantError(f"导入配置失败: {ex}")


# ---------------------------
#   _change_instances_count
# ---------------------------
def _change_instances_count(hass: HomeAssistant, delta: int) -> int:

    current_count = hass.data.setdefault(DOMAIN, {}).setdefault(DATA_KEY_SERVICES, 0)

    result = current_count + delta

    hass.data[DOMAIN][DATA_KEY_SERVICES] = result

    return result





async def async_setup_services(hass: HomeAssistant, config_entry: ConfigEntry) -> None:

    """Set up the Huawei Router services."""

    active_instances = _change_instances_count(hass, 1)

    if active_instances > 1:

        _LOGGER.debug(

            "%s active instances has already been registered, skipping",

            active_instances - 1,

        )

        return



    try:
        _service_decorator = verify_domain_control(DOMAIN)
    except TypeError:  # HA < 2026.x requires hass
        _service_decorator = verify_domain_control(hass, DOMAIN)

    @_service_decorator

    async def async_call_service(service: ServiceCall) -> None:

        service_name = service.service



        if service_name == ServiceName.ADD_TO_WHITELIST:

            await _async_add_to_whitelist(hass, service)



        elif service_name == ServiceName.ADD_TO_BLACKLIST:

            await _async_add_to_blacklist(hass, service)



        elif service_name == ServiceName.REMOVE_FROM_WHITELIST:

            await _async_remove_from_whitelist(hass, service)



        elif service_name == ServiceName.REMOVE_FROM_BLACKLIST:

            await _async_remove_from_blacklist(hass, service)



        elif service_name == ServiceName.GUEST_NETWORK_SETUP:
            await _async_setup_guest_network(hass, service)

        elif service_name == ServiceName.PORT_MAPPING_ADD:
            await _async_port_mapping_add(hass, service)

        elif service_name == ServiceName.PORT_MAPPING_REMOVE:
            await _async_port_mapping_remove(hass, service)

        elif service_name == ServiceName.PORT_MAPPING_LIST:
            return await _async_port_mapping_list(hass, service)

        elif service_name == ServiceName.PORT_MAPPING_STATE:
            await _async_port_mapping_state(hass, service)

        elif service_name == ServiceName.PORT_TRIGGER_LIST:
            return await _async_port_trigger_list(hass, service)

        elif service_name == ServiceName.PORT_TRIGGER_STATE:
            await _async_port_trigger_state(hass, service)

        elif service_name == ServiceName.PORT_TRIGGER_ADD:
            await _async_port_trigger_add(hass, service)

        elif service_name == ServiceName.PORT_TRIGGER_REMOVE:
            await _async_port_trigger_remove(hass, service)

        elif service_name == ServiceName.UPNP_PORT_MAPPING_LIST:
            return await _async_upnp_port_mapping_list(hass, service)

        elif service_name == ServiceName.WAN_RECONNECT:
            await _async_wan_reconnect(hass, service)

        elif service_name == ServiceName.DHCP_STATIC_LEASE_LIST:
            return await _async_dhcp_static_lease_list(hass, service)

        elif service_name == ServiceName.DHCP_STATIC_LEASE_ADD:
            await _async_dhcp_static_lease_add(hass, service)

        elif service_name == ServiceName.DHCP_STATIC_LEASE_REMOVE:
            await _async_dhcp_static_lease_remove(hass, service)

        elif service_name == ServiceName.DHCP_STATIC_LEASE_STATE:
            await _async_dhcp_static_lease_state(hass, service)

        elif service_name == ServiceName.UPNP_SET_ENABLED:
            await _async_upnp_set_enabled(hass, service)

        elif service_name == ServiceName.IPV6_SET_ENABLED:
            await _async_ipv6_set_enabled(hass, service)

        elif service_name == ServiceName.BAND_STEERING_SET_ENABLED:
            await _async_band_steering_set_enabled(hass, service)

        elif service_name == ServiceName.SMART_CONNECT_SET_ENABLED:
            await _async_smart_connect_set_enabled(hass, service)

        elif service_name == ServiceName.FIREWALL_SET_LEVEL:
            await _async_firewall_set_level(hass, service)

        elif service_name == ServiceName.DMZ_SET:
            await _async_dmz_set(hass, service)

        elif service_name == ServiceName.SCHEDULED_REBOOT_SET:
            await _async_scheduled_reboot_set(hass, service)

        elif service_name == ServiceName.DDNS_STATUS:
            return await _async_ddns_status(hass, service)

        elif service_name == ServiceName.DDNS_SET_ENABLED:
            await _async_ddns_set_enabled(hass, service)

        elif service_name == ServiceName.DEVICE_SET_NAME:
            await _async_device_set_name(hass, service)

        elif service_name == ServiceName.DEVICE_SET_RATE_LIMIT:
            await _async_device_set_rate_limit(hass, service)

        elif service_name == ServiceName.DEVICE_REMOVE:
            await _async_device_remove(hass, service)

        elif service_name == ServiceName.API_GET:
            return await _async_api_get(hass, service)

        elif service_name == ServiceName.API_SET:
            return await _async_api_set(hass, service)

        elif service_name == ServiceName.WIFI_RADIO_GET:
            return await _async_wifi_radio_get(hass, service)

        elif service_name == ServiceName.WIFI_RADIO_SET_ENABLED:
            await _async_wifi_radio_set_enabled(hass, service)

        elif service_name == ServiceName.WLAN_WPS_GET:
            return await _async_wlan_wps_get(hass, service)

        elif service_name == ServiceName.WPS_SET_ENABLED:
            await _async_wps_set_enabled(hass, service)

        elif service_name == ServiceName.MULTI_SSID_LIST:
            return await _async_multi_ssid_list(hass, service)

        elif service_name == ServiceName.WIFI_TIMING_ACCELERATE_GET:
            return await _async_wifi_timing_accelerate_get(hass, service)

        elif service_name == ServiceName.WIFI_TIMING_ACCELERATE_SET:
            await _async_wifi_timing_accelerate_set(hass, service)

        elif service_name == ServiceName.WLAN_WIFI_SYNC_GET:
            return await _async_wlan_wifi_sync_get(hass, service)

        elif service_name == ServiceName.LAN_CONFIG_GET:
            return await _async_lan_config_get(hass, service)

        elif service_name == ServiceName.LAN_CONFIG_SET:
            await _async_lan_config_set(hass, service)

        elif service_name == ServiceName.LAN_ALL_GET:
            return await _async_lan_all_get(hass, service)

        elif service_name == ServiceName.DHCP_SERVER_GET:
            return await _async_dhcp_server_get(hass, service)

        elif service_name == ServiceName.DHCP_SERVER_SET:
            await _async_dhcp_server_set(hass, service)

        elif service_name == ServiceName.DEVICE_TYPE_LIST:
            return await _async_device_type_list(hass, service)

        elif service_name == ServiceName.WAN_LEARN_CONFIG_GET:
            return await _async_wan_learn_config_get(hass, service)

        elif service_name == ServiceName.WAN_DIAGNOSE_GET:
            return await _async_wan_diagnose_get(hass, service)

        elif service_name == ServiceName.IPV6_WAN_GET:
            return await _async_ipv6_wan_get(hass, service)

        elif service_name == ServiceName.IPV6_WAN_SET:
            await _async_ipv6_wan_set(hass, service)

        elif service_name == ServiceName.IPV6_LAN_GET:
            return await _async_ipv6_lan_get(hass, service)

        elif service_name == ServiceName.IPV6_LAN_SET:
            await _async_ipv6_lan_set(hass, service)

        elif service_name == ServiceName.ALG_GET:
            return await _async_alg_get(hass, service)

        elif service_name == ServiceName.ALG_SET:
            await _async_alg_set(hass, service)

        elif service_name == ServiceName.TUNNEL_GET:
            return await _async_tunnel_get(hass, service)

        elif service_name == ServiceName.TUNNEL_SET:
            await _async_tunnel_set(hass, service)

        elif service_name == ServiceName.SWAN_GET:
            return await _async_swan_get(hass, service)

        elif service_name == ServiceName.SMART_VPN_GET:
            return await _async_smart_vpn_get(hass, service)

        elif service_name == ServiceName.SMART_VPN_SET:
            await _async_smart_vpn_set(hass, service)

        elif service_name == ServiceName.IPTV_GET:
            return await _async_iptv_get(hass, service)

        elif service_name == ServiceName.IPTV_SET:
            await _async_iptv_set(hass, service)

        elif service_name == ServiceName.MAC_FILTER_LIST:
            return await _async_mac_filter_list(hass, service)

        elif service_name == ServiceName.ACCESS_AUTH_GET:
            return await _async_access_auth_get(hass, service)

        elif service_name == ServiceName.ACCESS_AUTH_SET:
            await _async_access_auth_set(hass, service)

        elif service_name == ServiceName.HOMESEC_GET:
            return await _async_homesec_get(hass, service)

        elif service_name == ServiceName.HOMESEC_SET:
            await _async_homesec_set(hass, service)

        elif service_name == ServiceName.XLINK_LOCK_NET_GET:
            return await _async_xlink_lock_net_get(hass, service)

        elif service_name == ServiceName.GUEST_NETWORK_LIMIT_RATE_GET:
            return await _async_guest_network_limit_rate_get(hass, service)

        elif service_name == ServiceName.GUEST_NETWORK_LIMIT_RATE_SET:
            await _async_guest_network_limit_rate_set(hass, service)

        elif service_name == ServiceName.GUEST_NETWORK_REST_TIME_SET:
            await _async_guest_network_rest_time_set(hass, service)

        elif service_name == ServiceName.NTP_GET:
            return await _async_ntp_get(hass, service)

        elif service_name == ServiceName.NTP_SET:
            await _async_ntp_set(hass, service)

        elif service_name == ServiceName.PROCESS_STATUS_GET:
            return await _async_process_status_get(hass, service)

        elif service_name == ServiceName.ONLINE_STATE_GET:
            return await _async_online_state_get(hass, service)

        elif service_name == ServiceName.ETH_NEGOTIATION_GET:
            return await _async_eth_negotiation_get(hass, service)

        elif service_name == ServiceName.AUTO_UPGRADE_GET:
            return await _async_auto_upgrade_get(hass, service)

        elif service_name == ServiceName.AUTO_UPGRADE_SET:
            await _async_auto_upgrade_set(hass, service)

        elif service_name == ServiceName.AUTO_UPGRADE_CHECK:
            return await _async_auto_upgrade_check(hass, service)

        elif service_name == ServiceName.PASSWORD_RULE_GET:
            return await _async_password_rule_get(hass, service)

        elif service_name == ServiceName.USER_ACCOUNT_GET:
            return await _async_user_account_get(hass, service)

        elif service_name == ServiceName.SYSTEM_LANGUAGE_SET:
            await _async_system_language_set(hass, service)

        elif service_name == ServiceName.WIFI_SCAN:
            return await _async_wifi_scan(hass, service)

        elif service_name == ServiceName.WIFI_SCAN_RESULT:
            return await _async_wifi_scan_result(hass, service)

        elif service_name == ServiceName.REPEATER_STATE_GET:
            return await _async_repeater_state_get(hass, service)

        elif service_name == ServiceName.REPEATER_DIAG_GET:
            return await _async_repeater_diag_get(hass, service)

        elif service_name == ServiceName.REPEATER_DIAL_SET:
            await _async_repeater_dial_set(hass, service)

        elif service_name == ServiceName.NETDISK_INFO_GET:
            return await _async_netdisk_info_get(hass, service)

        elif service_name == ServiceName.NETDISK_CODE_GET:
            return await _async_netdisk_code_get(hass, service)

        elif service_name == ServiceName.NETDISK_CODE_SET:
            await _async_netdisk_code_set(hass, service)

        elif service_name == ServiceName.HILINK_STATUS_GET:
            return await _async_hilink_status_get(hass, service)

        elif service_name == ServiceName.SLAVE_SETUP_SET:
            await _async_slave_setup_set(hass, service)

        elif service_name == ServiceName.MULTI_HOST_INFO_GET:
            return await _async_multi_host_info_get(hass, service)

        elif service_name == ServiceName.SYSTEM_MODE_GET:
            return await _async_system_mode_get(hass, service)

        elif service_name == ServiceName.WIFI_DIAG_GET:
            return await _async_wifi_diag_get(hass, service)

        elif service_name == ServiceName.LAN_HOST_GET:
            return await _async_lan_host_get(hass, service)

        elif service_name == ServiceName.DIAGNOSTICS_COLLECT:
            await _async_diagnostics_collect(hass, service)

        elif service_name == ServiceName.DIAGNOSTICS_STATUS:
            return await _async_diagnostics_status(hass, service)

        elif service_name == ServiceName.DIAGNOSTICS_DEVLIST:
            return await _async_diagnostics_devlist(hass, service)

        elif service_name == ServiceName.DIAGNOSTICS_DOWNLOAD:
            return await _async_diagnostics_download(hass, service)

        elif service_name == ServiceName.WPS_PAIR_START:
            await _async_wps_pair_start(hass, service)

        elif service_name == ServiceName.CONFIG_EXPORT:
            return await _async_config_export(hass, service)

        elif service_name == ServiceName.CONFIG_IMPORT:
            return await _async_config_import(hass, service)

        else:

            raise ServiceNotFound(DOMAIN, service_name)



    for item in SERVICES:

        hass.services.async_register(

            domain=DOMAIN,

            service=item.name,

            service_func=async_call_service,

            schema=item.schema,

        )





async def async_unload_services(hass: HomeAssistant, config_entry: ConfigEntry):

    """Unload services."""

    active_instances = _change_instances_count(hass, -1)

    if active_instances > 0:

        _LOGGER.debug("%s active instances remaining, skipping", active_instances)

        return



    hass.data[DOMAIN].pop(DATA_KEY_SERVICES)

    for service in SERVICES:

        hass.services.async_remove(domain=DOMAIN, service=service.name)

