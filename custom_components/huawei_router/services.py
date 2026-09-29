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

