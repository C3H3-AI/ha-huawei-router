"""Support for additional sensors."""

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Callable, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .classes import DEVICE_TAG, ConnectedDevice, HuaweiInterfaceType
from .client.classes import MAC_ADDR
from .client.const import CONNECTED_VIA_ID_PRIMARY
from .const import DOMAIN
from .helpers import (
    generate_entity_id,
    generate_entity_name,
    generate_entity_unique_id,
    get_coordinator,
    get_past_moment,
)
from .options import HuaweiIntegrationOptions
from .update_coordinator import ActiveRoutersWatcher, HuaweiConnectedDevicesWatcher, HuaweiDataUpdateCoordinator

UNITS_CLIENTS: Final = "clients"

_LOGGER = logging.getLogger(__name__)

_FUNCTION_DISPLAYED_NAME_DIAGNOSTICS: Final = "诊断"
_FUNCTION_UID_DIAGNOSTICS: Final = "sensor_diagnostics"

_FUNCTION_DISPLAYED_NAME_TOTAL_CLIENTS: Final = "总客户端数"
_FUNCTION_UID_TOTAL_CLIENTS: Final = "sensor_total_clients"

_FUNCTION_DISPLAYED_NAME_CLIENTS: Final = "客户端数"
_FUNCTION_UID_CLIENTS: Final = "sensor_clients"

_FUNCTION_DISPLAYED_NAME_UPTIME: Final = "运行时间"
_FUNCTION_UID_UPTIME: Final = "sensor_uptime"

_FUNCTION_DISPLAYED_NAME_GROUPED: Final = "分组设备"
_FUNCTION_UID_GROUPED: Final = "sensor_grouped_devices"

_FUNCTION_DISPLAYED_NAME_IP: Final = "IP地址"
_FUNCTION_UID_IP: Final = "sensor_ip_address"

_FUNCTION_DISPLAYED_NAME_MAC: Final = "MAC地址"
_FUNCTION_UID_MAC: Final = "sensor_mac_address"

_FUNCTION_DISPLAYED_NAME_MODEL: Final = "型号"
_FUNCTION_UID_MODEL: Final = "sensor_model"

_FUNCTION_DISPLAYED_NAME_SERIAL_NUMBER: Final = "序列号"
_FUNCTION_UID_SERIAL_NUMBER: Final = "sensor_serial_number"

_FUNCTION_DISPLAYED_NAME_SOFTWARE_VERSION: Final = "软件版本"
_FUNCTION_UID_SOFTWARE_VERSION: Final = "sensor_software_version"

_FUNCTION_DISPLAYED_NAME_HARDWARE_VERSION: Final = "硬件版本"
_FUNCTION_UID_HARDWARE_VERSION: Final = "sensor_hardware_version"

_FUNCTION_DISPLAYED_NAME_HARMONY_VERSION: Final = "HarmonyOS版本"
_FUNCTION_UID_HARMONY_VERSION: Final = "sensor_harmony_version"

_FUNCTION_DISPLAYED_NAME_CONNECTION_TYPE: Final = "连接类型"
_FUNCTION_UID_CONNECTION_TYPE: Final = "sensor_connection_type"

_FUNCTION_DISPLAYED_NAME_SIGNAL: Final = "信号强度"
_FUNCTION_UID_SIGNAL: Final = "sensor_signal"

_FUNCTION_DISPLAYED_NAME_UPLOAD_SPEED: Final = "上传速度"
_FUNCTION_UID_UPLOAD_SPEED: Final = "sensor_upload_speed"

_FUNCTION_DISPLAYED_NAME_DOWNLOAD_SPEED: Final = "下载速度"
_FUNCTION_UID_DOWNLOAD_SPEED: Final = "sensor_download_speed"

_FUNCTION_DISPLAYED_NAME_CONNECTION_RATE: Final = "连接速率"
_FUNCTION_UID_CONNECTION_RATE: Final = "sensor_connection_rate"

_FUNCTION_DISPLAYED_NAME_FREQUENCY: Final = "WiFi频段"
_FUNCTION_UID_FREQUENCY: Final = "sensor_frequency"

_FUNCTION_DISPLAYED_NAME_DEV_BRANDS: Final = "设备厂商"
_FUNCTION_UID_DEV_BRANDS: Final = "sensor_dev_brands"

_FUNCTION_DISPLAYED_NAME_ICON_TYPE: Final = "设备类型"
_FUNCTION_UID_ICON_TYPE: Final = "sensor_icon_type"

_FUNCTION_DISPLAYED_NAME_TX_DATA: Final = "发送流量"
_FUNCTION_UID_TX_DATA: Final = "sensor_tx_data"

_FUNCTION_DISPLAYED_NAME_RX_DATA: Final = "接收流量"
_FUNCTION_UID_RX_DATA: Final = "sensor_rx_data"

_FUNCTION_DISPLAYED_NAME_PARENT_CONTROL: Final = "家长控制"
_FUNCTION_UID_PARENT_CONTROL: Final = "sensor_parent_control"

_FUNCTION_DISPLAYED_NAME_CONNECTED_VIA: Final = "连接至"
_FUNCTION_UID_CONNECTED_VIA: Final = "sensor_connected_via"

_ENTITY_DOMAIN: Final = "sensor"


# ---------------------------
#   HuaweiSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiSensorEntityDescription(SensorEntityDescription):
    """A class that describes sensor entities."""

    function_name: str | None = None
    function_uid: str | None = None
    device_mac: MAC_ADDR | None = None
    device_name: str | None = None
    name: str | None = None
    translation_placeholders: dict[str, str] | None = None


# ---------------------------
#   HuaweiUptimeSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiUptimeSensorEntityDescription(HuaweiSensorEntityDescription):
    """A class that describes sensor entities."""

    native_unit_of_measurement: str | None = None
    state_class: SensorStateClass | str | None = None
    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    device_class: str | None = SensorDeviceClass.TIMESTAMP


# ---------------------------
#   HuaweiClientsSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiClientsSensorEntityDescription(HuaweiSensorEntityDescription):
    """A class that describes clients count sensor entities."""

    native_unit_of_measurement: str | None = UNITS_CLIENTS
    state_class: SensorStateClass | str | None = SensorStateClass.MEASUREMENT
    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    suggested_display_precision: int | None = 0


# ---------------------------
#   HuaweiDiagnosticsSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiDiagnosticsSensorEntityDescription(HuaweiSensorEntityDescription):
    """A class that describes diagnostics sensor entity."""

    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC


# ---------------------------
#   HuaweiGroupedDevicesSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiGroupedDevicesSensorEntityDescription(HuaweiSensorEntityDescription):
    """A class that describes grouped devices sensor entity."""

    device_mac: MAC_ADDR | None = None
    device_name: str | None = None
    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    suggested_display_precision: int | None = 0


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for Huawei component."""
    coordinator = get_coordinator(hass, config_entry)

    integration_options = HuaweiIntegrationOptions(config_entry)

    sensors = [
        HuaweiUptimeSensor(
            coordinator,
            HuaweiUptimeSensorEntityDescription(
                key="uptime",
                icon="mdi:timer-outline",
                name=_FUNCTION_DISPLAYED_NAME_UPTIME,
                device_mac=None,
                device_name=None,
                function_uid=_FUNCTION_UID_UPTIME,
                function_name=_FUNCTION_DISPLAYED_NAME_UPTIME,
            ),
        ),
        HuaweiConnectedDevicesSensor(
            coordinator,
            HuaweiClientsSensorEntityDescription(
                key="total",
                icon="mdi:account-multiple",
                name=_FUNCTION_DISPLAYED_NAME_TOTAL_CLIENTS,
                device_mac=None,
                device_name=None,
                function_uid=_FUNCTION_UID_TOTAL_CLIENTS,
                function_name=_FUNCTION_DISPLAYED_NAME_TOTAL_CLIENTS,
            ),
            integration_options,
            lambda device: device.is_active,
        ),
    ]

    if integration_options.router_clients_sensors:
        sensors.append(
            HuaweiConnectedDevicesSensor(
                coordinator,
                HuaweiClientsSensorEntityDescription(
                    key="primary",
                    icon="mdi:router-wireless",
                    name=_FUNCTION_DISPLAYED_NAME_CLIENTS,
                    device_mac=None,
                    device_name=None,
                    function_uid=_FUNCTION_UID_CLIENTS,
                    function_name=_FUNCTION_DISPLAYED_NAME_CLIENTS,
                ),
                integration_options,
                lambda device: device.is_active
                and device.connected_via_id == CONNECTED_VIA_ID_PRIMARY,
            )
        )

        sensors.append(
            HuaweiDiagnosticsSensor(
                coordinator,
                HuaweiDiagnosticsSensorEntityDescription(
                    key="diagnostics",
                    icon="mdi:diagnostics",
                    name=_FUNCTION_DISPLAYED_NAME_DIAGNOSTICS,
                    device_mac=None,
                    device_name=None,
                    function_uid=_FUNCTION_UID_DIAGNOSTICS,
                    function_name=_FUNCTION_DISPLAYED_NAME_DIAGNOSTICS,
                ),
            )
        )

        sensors.append(
            HuaweiGroupedDevicesSensor(
                coordinator,
                HuaweiGroupedDevicesSensorEntityDescription(
                    key="all_devices",
                    icon="mdi:account-multiple",
                    name=_FUNCTION_DISPLAYED_NAME_GROUPED,
                    device_mac=None,
                    device_name="所有设备",
                    function_uid=_FUNCTION_UID_GROUPED,
                    function_name=_FUNCTION_DISPLAYED_NAME_GROUPED,
                ),
            )
        )

        sensors.append(
            HuaweiWanStatusSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="wan_status",
                    icon="mdi:wan",
                    name="WAN状态",
                    translation_key="wan_status",
                    function_uid="sensor_wan_status",
                    function_name="WAN状态",
                    device_mac=None,
                    device_name=None,
                ),
            )
        )

        sensors.append(
            HuaweiWanIpSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="wan_ip",
                    icon="mdi:ip-network",
                    name="WAN IP地址",
                    translation_key="wan_ip",
                    function_uid="sensor_wan_ip",
                    function_name="WAN IP地址",
                    device_mac=None,
                    device_name=None,
                ),
            )
        )

        sensors.append(
            HuaweiWanIpv6Sensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="wan_ipv6",
                    icon="mdi:ip-network",
                    name="WAN IPv6地址",
                    translation_key="wan_ipv6",
                    function_uid="sensor_wan_ipv6",
                    function_name="WAN IPv6地址",
                    device_mac=None,
                    device_name=None,
                ),
            )
        )

        # 添加主路由器的 LAN IP 传感器
        sensors.append(
            HuaweiDeviceIpSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_lan_ip",
                    icon="mdi:ip-network",
                    name="路由器 IP 地址",
                    translation_key="router_lan_ip",
                    function_uid=_FUNCTION_UID_IP,
                    function_name="路由器 IP 地址",
                    device_mac=None,
                    device_name=None,
                ),
            )
        )

        # 添加路由器信息传感器
        sensors.append(
            HuaweiRouterInfoSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_model",
                    icon="mdi:router-wireless",
                    name=_FUNCTION_DISPLAYED_NAME_MODEL,
                    function_uid=_FUNCTION_UID_MODEL,
                    function_name=_FUNCTION_DISPLAYED_NAME_MODEL,
                    device_mac=None,
                    device_name=None,
                ),
                "model",
            )
        )

        sensors.append(
            HuaweiRouterInfoSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_serial_number",
                    icon="mdi:hash",
                    name=_FUNCTION_DISPLAYED_NAME_SERIAL_NUMBER,
                    function_uid=_FUNCTION_UID_SERIAL_NUMBER,
                    function_name=_FUNCTION_DISPLAYED_NAME_SERIAL_NUMBER,
                    device_mac=None,
                    device_name=None,
                ),
                "serial_number",
            )
        )

        sensors.append(
            HuaweiRouterInfoSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_software_version",
                    icon="mdi:update",
                    name=_FUNCTION_DISPLAYED_NAME_SOFTWARE_VERSION,
                    function_uid=_FUNCTION_UID_SOFTWARE_VERSION,
                    function_name=_FUNCTION_DISPLAYED_NAME_SOFTWARE_VERSION,
                    device_mac=None,
                    device_name=None,
                ),
                "software_version",
            )
        )

        sensors.append(
            HuaweiRouterInfoSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_hardware_version",
                    icon="mdi:cpu",
                    name=_FUNCTION_DISPLAYED_NAME_HARDWARE_VERSION,
                    function_uid=_FUNCTION_UID_HARDWARE_VERSION,
                    function_name=_FUNCTION_DISPLAYED_NAME_HARDWARE_VERSION,
                    device_mac=None,
                    device_name=None,
                ),
                "hardware_version",
            )
        )

        sensors.append(
            HuaweiRouterInfoSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_harmony_version",
                    icon="mdi:os",
                    name=_FUNCTION_DISPLAYED_NAME_HARMONY_VERSION,
                    function_uid=_FUNCTION_UID_HARMONY_VERSION,
                    function_name=_FUNCTION_DISPLAYED_NAME_HARMONY_VERSION,
                    device_mac=None,
                    device_name=None,
                ),
                "harmony_version",
            )
        )
        
        # 添加 MAC 地址传感器
        sensors.append(
            HuaweiRouterInfoSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="router_mac_address",
                    icon="mdi:identifier",
                    name=_FUNCTION_DISPLAYED_NAME_MAC,
                    function_uid=_FUNCTION_UID_MAC,
                    function_name=_FUNCTION_DISPLAYED_NAME_MAC,
                    device_mac=None,
                    device_name=None,
                ),
                "mac_address",
            )
        )

        sensors.append(
            HuaweiWanSpeedSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="wan_download_speed",
                    icon="mdi:download",
                    name="WAN下载",
                    translation_key="wan_download",
                    function_uid="sensor_wan_download_speed",
                    function_name="WAN下载",
                    native_unit_of_measurement="Kbps",
                    state_class=SensorStateClass.MEASUREMENT,
                    suggested_display_precision=1,
                    device_mac=None,
                    device_name=None,
                ),
            )
        )

        sensors.append(
            HuaweiWanSpeedSensor(
                coordinator,
                HuaweiWanSensorEntityDescription(
                    key="wan_upload_speed",
                    icon="mdi:upload",
                    name="WAN上传",
                    translation_key="wan_upload",
                    function_uid="sensor_wan_upload_speed",
                    function_name="WAN上传",
                    native_unit_of_measurement="Kbps",
                    state_class=SensorStateClass.MEASUREMENT,
                    suggested_display_precision=1,
                    device_mac=None,
                    device_name=None,
                ),
            )
        )

    async_add_entities(sensors)

    watch_for_additional_routers(
        coordinator, config_entry, integration_options, async_add_entities
    )


# ---------------------------
#   watch_for_additional_routers
# ---------------------------
def watch_for_additional_routers(
    coordinator: HuaweiDataUpdateCoordinator,
    config_entry: ConfigEntry,
    integration_options: HuaweiIntegrationOptions,
    async_add_entities: AddEntitiesCallback,
):
    watcher: ActiveRoutersWatcher = ActiveRoutersWatcher(coordinator)
    skip_offline = integration_options.skip_offline_devices
    predicate = (lambda d: d.is_active and not d.is_router) if skip_offline else (lambda d: not d.is_router)
    all_watcher: HuaweiConnectedDevicesWatcher = HuaweiConnectedDevicesWatcher(
        coordinator, predicate
    )

    # 初始清理：移除离线设备的旧传感器实体
    if skip_offline:
        from homeassistant.helpers import entity_registry as er_mod
        er = er_mod.async_get(coordinator.hass)
        for mac, device in coordinator.connected_devices.items():
            if device.is_router or device.is_active:
                continue
            prefix = f"{coordinator.unique_id}_"
            for entity_entry in list(er.entities.values()):
                if entity_entry.platform == DOMAIN and mac.lower().replace(':', '_') in entity_entry.unique_id.lower():
                    er.async_remove(entity_entry.entity_id)
                    _LOGGER.debug("Cleanup offline device entity: %s", entity_entry.entity_id)

    # 为所有非路由器设备创建设备注册表条目（包括离线设备，确保 device_tracker 有关联）
    from homeassistant.helpers import device_registry as dr_mod
    dr = dr_mod.async_get(coordinator.hass)
    for mac, device in coordinator.connected_devices.items():
        if device.is_router:
            continue
        device_info = coordinator.get_device_info(mac)
        if device_info:
            dr.async_get_or_create(
                config_entry_id=config_entry.entry_id,
                **device_info,
            )
    known_client_sensors: dict[MAC_ADDR, HuaweiConnectedDevicesSensor] = {}
    known_uptime_sensors: dict[MAC_ADDR, HuaweiUptimeSensor] = {}
    known_grouped_sensors: dict[MAC_ADDR, HuaweiGroupedDevicesSensor] = {}
    known_ip_sensors: dict[MAC_ADDR, HuaweiDeviceIpSensor] = {}
    known_mac_sensors: dict[MAC_ADDR, HuaweiSensor] = {}
    known_connection_type_sensors: dict[MAC_ADDR, HuaweiDeviceConnectionTypeSensor] = {}
    known_signal_sensors: dict[MAC_ADDR, HuaweiDeviceSignalSensor] = {}
    known_upload_speed_sensors: dict[MAC_ADDR, HuaweiDeviceUploadSpeedSensor] = {}
    known_download_speed_sensors: dict[MAC_ADDR, HuaweiDeviceDownloadSpeedSensor] = {}
    known_connection_rate_sensors: dict[MAC_ADDR, HuaweiDeviceConnectionRateSensor] = {}
    known_frequency_sensors: dict[MAC_ADDR, HuaweiDeviceFrequencySensor] = {}
    known_brands_sensors: dict[MAC_ADDR, HuaweiDeviceBrandsSensor] = {}
    known_type_sensors: dict[MAC_ADDR, HuaweiDeviceTypeSensor] = {}
    known_tx_data_sensors: dict[MAC_ADDR, HuaweiDeviceTxDataSensor] = {}
    known_rx_data_sensors: dict[MAC_ADDR, HuaweiDeviceRxDataSensor] = {}
    known_parent_control_sensors: dict[MAC_ADDR, HuaweiDeviceParentControlSensor] = {}
    known_connected_via_sensors: dict[MAC_ADDR, HuaweiDeviceConnectedViaSensor] = {}

    @callback
    def on_router_added(mac: MAC_ADDR, router: ConnectedDevice) -> None:
        """When a new mesh router is detected."""
        new_entities = []
        _LOGGER.debug("on_router_added called: mac=%s, name=%s", mac, router.name)

        if integration_options.router_clients_sensors and not known_client_sensors.get(mac):
            description = HuaweiClientsSensorEntityDescription(
                key=mac,
                icon="mdi:router-wireless",
                name=_FUNCTION_DISPLAYED_NAME_CLIENTS,
                device_mac=mac,
                device_name=router.name,
                function_uid=_FUNCTION_UID_CLIENTS,
                function_name=_FUNCTION_DISPLAYED_NAME_CLIENTS,
            )
            entity = HuaweiConnectedDevicesSensor(
                coordinator,
                description,
                integration_options,
                lambda device, via_id=mac: device.is_active
                and device.connected_via_id == via_id,
            )
            known_client_sensors[mac] = entity
            new_entities.append(entity)
            _LOGGER.debug("  Added client sensor for %s", router.name)

        if not known_uptime_sensors.get(mac):
            uptime_data = coordinator.get_device_uptime(mac)
            if uptime_data is not None:
                description = HuaweiUptimeSensorEntityDescription(
                    key="uptime",
                    icon="mdi:timer-outline",
                    name=_FUNCTION_DISPLAYED_NAME_UPTIME,
                    device_mac=mac,
                    device_name=router.name,
                    function_uid=_FUNCTION_UID_UPTIME,
                    function_name=_FUNCTION_DISPLAYED_NAME_UPTIME,
                )
                entity = HuaweiUptimeSensor(coordinator, description)
                known_uptime_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added uptime sensor for %s (has uptime data)", router.name)
            else:
                _LOGGER.debug("  Skipped uptime sensor for %s (no uptime data)", router.name)

        if integration_options.router_clients_sensors and not known_grouped_sensors.get(mac):
            try:
                description = HuaweiGroupedDevicesSensorEntityDescription(
                    key=mac,
                    icon="mdi:router-wireless",
                    name=_FUNCTION_DISPLAYED_NAME_GROUPED,
                    device_mac=mac,
                    device_name=router.name,
                    function_uid=_FUNCTION_UID_GROUPED,
                    function_name=_FUNCTION_DISPLAYED_NAME_GROUPED,
                )
                entity = HuaweiGroupedDevicesSensor(coordinator, description)
                known_grouped_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added grouped sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create grouped sensor for %s: %s", router.name, ex)

        # 为子路由器添加 IP 传感器
        if not known_ip_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_ip",
                    icon="mdi:ip-network",
                    name="IP 地址",
                    translation_key="router_ip",
                    function_uid=_FUNCTION_UID_IP,
                    function_name="IP 地址",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceIpSensor(coordinator, description)
                known_ip_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added IP sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create IP sensor for %s: %s", router.name, ex)
        
        # 为子路由器添加 MAC 地址传感器
        if not known_mac_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_mac",
                    icon="mdi:identifier",
                    name="MAC 地址",
                    translation_key="router_mac",
                    function_uid=_FUNCTION_UID_MAC,
                    function_name="MAC 地址",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceMacSensor(coordinator, description)
                known_mac_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added MAC sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create MAC sensor for %s: %s", router.name, ex)
        
        # 为设备添加连接类型传感器
        if not known_connection_type_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_connection_type",
                    icon="mdi:access-point",
                    name="连接类型",
                    translation_key="connection_type",
                    function_uid=_FUNCTION_UID_CONNECTION_TYPE,
                    function_name="连接类型",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceConnectionTypeSensor(coordinator, description)
                known_connection_type_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added connection type sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create connection type sensor for %s: %s", router.name, ex)
        
        # 为设备添加信号强度传感器
        if not known_signal_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_signal",
                    icon="mdi:signal",
                    name="信号强度",
                    translation_key="signal_strength",
                    function_uid=_FUNCTION_UID_SIGNAL,
                    function_name="信号强度",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceSignalSensor(coordinator, description)
                known_signal_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added signal sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create signal sensor for %s: %s", router.name, ex)
        
        # 为设备添加上传速度传感器
        if not known_upload_speed_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_upload_speed",
                    icon="mdi:upload",
                    name="上传速度",
                    translation_key="upload_speed",
                    function_uid=_FUNCTION_UID_UPLOAD_SPEED,
                    function_name="上传速度",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceUploadSpeedSensor(coordinator, description)
                known_upload_speed_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added upload speed sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create upload speed sensor for %s: %s", router.name, ex)
        
        # 为设备添加下载速度传感器
        if not known_download_speed_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_download_speed",
                    icon="mdi:download",
                    name="下载速度",
                    translation_key="download_speed",
                    function_uid=_FUNCTION_UID_DOWNLOAD_SPEED,
                    function_name="下载速度",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceDownloadSpeedSensor(coordinator, description)
                known_download_speed_sensors[mac] = entity
                new_entities.append(entity)
                _LOGGER.debug("  Added download speed sensor for %s", router.name)
            except Exception as ex:
                _LOGGER.error("  Failed to create download speed sensor for %s: %s", router.name, ex)
        
        # 连接速率
        if not known_connection_rate_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_connection_rate",
                    icon="mdi:speedometer",
                    name="连接速率",
                    translation_key="connection_rate",
                    function_uid=_FUNCTION_UID_CONNECTION_RATE,
                    function_name="连接速率",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceConnectionRateSensor(coordinator, description)
                known_connection_rate_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create connection rate sensor: %s", ex)
        
        # WiFi频段
        if not known_frequency_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_frequency",
                    icon="mdi:radio",
                    name="WiFi频段",
                    translation_key="frequency",
                    function_uid=_FUNCTION_UID_FREQUENCY,
                    function_name="WiFi频段",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceFrequencySensor(coordinator, description)
                known_frequency_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create frequency sensor: %s", ex)
        
        # 设备厂商
        if not known_brands_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_dev_brands",
                    icon="mdi:factory",
                    name="设备厂商",
                    translation_key="dev_brands",
                    function_uid=_FUNCTION_UID_DEV_BRANDS,
                    function_name="设备厂商",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceBrandsSensor(coordinator, description)
                known_brands_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create brands sensor: %s", ex)
        
        # 设备类型
        if not known_type_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_icon_type",
                    icon="mdi:devices",
                    name="设备类型",
                    translation_key="icon_type",
                    function_uid=_FUNCTION_UID_ICON_TYPE,
                    function_name="设备类型",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceTypeSensor(coordinator, description)
                known_type_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create type sensor: %s", ex)
        
        # 发送流量
        if not known_tx_data_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_tx_data",
                    icon="mdi:upload-network",
                    name="发送流量",
                    translation_key="tx_data",
                    function_uid=_FUNCTION_UID_TX_DATA,
                    function_name="发送流量",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceTxDataSensor(coordinator, description)
                known_tx_data_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create tx data sensor: %s", ex)
        
        # 接收流量
        if not known_rx_data_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_rx_data",
                    icon="mdi:download-network",
                    name="接收流量",
                    translation_key="rx_data",
                    function_uid=_FUNCTION_UID_RX_DATA,
                    function_name="接收流量",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceRxDataSensor(coordinator, description)
                known_rx_data_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create rx data sensor: %s", ex)
        
        # 家长控制
        if not known_parent_control_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_parent_control",
                    icon="mdi:lock",
                    name="家长控制",
                    translation_key="parent_control",
                    function_uid=_FUNCTION_UID_PARENT_CONTROL,
                    function_name="家长控制",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceParentControlSensor(coordinator, description)
                known_parent_control_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create parent control sensor: %s", ex)
        
        # 连接至（路由器）
        if not known_connected_via_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_connected_via",
                    icon="mdi:router-network",
                    name="连接至",
                    translation_key="connected_via",
                    function_uid=_FUNCTION_UID_CONNECTED_VIA,
                    function_name="连接至",
                    device_mac=mac,
                    device_name=router.name,
                )
                entity = HuaweiDeviceConnectedViaSensor(coordinator, description)
                known_connected_via_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create connected via sensor: %s", ex)

        if new_entities:
            _LOGGER.debug("  Adding %d entities for router %s", len(new_entities), router.name)
            async_add_entities(new_entities)

    @callback
    def on_device_added(mac: MAC_ADDR, device: ConnectedDevice) -> None:
        """When a new non-router device is detected."""
        new_entities = []
        _LOGGER.debug("on_device_added: mac=%s, name=%s", mac, device.name)

        if not known_ip_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_ip",
                    icon="mdi:ip-network",
                    name="IP地址",
                    translation_key="ip_address",
                    function_uid=_FUNCTION_UID_IP,
                    function_name="IP地址",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceIpSensor(coordinator, description)
                known_ip_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create IP sensor for %s: %s", device.name, ex)

        if not known_mac_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_mac",
                    icon="mdi:identifier",
                    name="MAC地址",
                    translation_key="mac_address",
                    function_uid=_FUNCTION_UID_MAC,
                    function_name="MAC地址",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceMacSensor(coordinator, description)
                known_mac_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create MAC sensor for %s: %s", device.name, ex)

        if not known_connection_type_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_connection_type",
                    icon="mdi:access-point",
                    name="连接类型",
                    translation_key="connection_type",
                    function_uid=_FUNCTION_UID_CONNECTION_TYPE,
                    function_name="连接类型",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceConnectionTypeSensor(coordinator, description)
                known_connection_type_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create connection type for %s: %s", device.name, ex)

        if not known_signal_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_signal",
                    icon="mdi:signal",
                    name="信号强度",
                    translation_key="signal_strength",
                    function_uid=_FUNCTION_UID_SIGNAL,
                    function_name="信号强度",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceSignalSensor(coordinator, description)
                known_signal_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create signal for %s: %s", device.name, ex)

        if not known_upload_speed_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_upload_speed",
                    icon="mdi:upload",
                    name="上传速度",
                    translation_key="upload_speed",
                    function_uid=_FUNCTION_UID_UPLOAD_SPEED,
                    function_name="上传速度",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceUploadSpeedSensor(coordinator, description)
                known_upload_speed_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create upload speed for %s: %s", device.name, ex)

        if not known_download_speed_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_download_speed",
                    icon="mdi:download",
                    name="下载速度",
                    translation_key="download_speed",
                    function_uid=_FUNCTION_UID_DOWNLOAD_SPEED,
                    function_name="下载速度",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceDownloadSpeedSensor(coordinator, description)
                known_download_speed_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create download speed for %s: %s", device.name, ex)

        if not known_connection_rate_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_connection_rate",
                    icon="mdi:speedometer",
                    name="连接速率",
                    translation_key="connection_rate",
                    function_uid=_FUNCTION_UID_CONNECTION_RATE,
                    function_name="连接速率",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceConnectionRateSensor(coordinator, description)
                known_connection_rate_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create connection rate for %s: %s", device.name, ex)

        if not known_frequency_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_frequency",
                    icon="mdi:radio",
                    name="WiFi频段",
                    translation_key="frequency",
                    function_uid=_FUNCTION_UID_FREQUENCY,
                    function_name="WiFi频段",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceFrequencySensor(coordinator, description)
                known_frequency_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create frequency for %s: %s", device.name, ex)

        if not known_brands_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_dev_brands",
                    icon="mdi:factory",
                    name="设备厂商",
                    translation_key="dev_brands",
                    function_uid=_FUNCTION_UID_DEV_BRANDS,
                    function_name="设备厂商",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceBrandsSensor(coordinator, description)
                known_brands_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create brands for %s: %s", device.name, ex)

        if not known_type_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_icon_type",
                    icon="mdi:devices",
                    name="设备类型",
                    translation_key="icon_type",
                    function_uid=_FUNCTION_UID_ICON_TYPE,
                    function_name="设备类型",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceTypeSensor(coordinator, description)
                known_type_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create type for %s: %s", device.name, ex)

        if not known_tx_data_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_tx_data",
                    icon="mdi:upload-network",
                    name="发送流量",
                    translation_key="tx_data",
                    function_uid=_FUNCTION_UID_TX_DATA,
                    function_name="发送流量",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceTxDataSensor(coordinator, description)
                known_tx_data_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create tx data for %s: %s", device.name, ex)

        if not known_rx_data_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_rx_data",
                    icon="mdi:download-network",
                    name="接收流量",
                    translation_key="rx_data",
                    function_uid=_FUNCTION_UID_RX_DATA,
                    function_name="接收流量",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceRxDataSensor(coordinator, description)
                known_rx_data_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create rx data for %s: %s", device.name, ex)

        if not known_parent_control_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_parent_control",
                    icon="mdi:lock",
                    name="家长控制",
                    translation_key="parent_control",
                    function_uid=_FUNCTION_UID_PARENT_CONTROL,
                    function_name="家长控制",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceParentControlSensor(coordinator, description)
                known_parent_control_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create parent control for %s: %s", device.name, ex)

        if not known_connected_via_sensors.get(mac):
            try:
                description = HuaweiWanSensorEntityDescription(
                    key=f"{mac}_connected_via",
                    icon="mdi:router-network",
                    name="连接至",
                    translation_key="connected_via",
                    function_uid=_FUNCTION_UID_CONNECTED_VIA,
                    function_name="连接至",
                    device_mac=mac,
                    device_name=device.name,
                )
                entity = HuaweiDeviceConnectedViaSensor(coordinator, description)
                known_connected_via_sensors[mac] = entity
                new_entities.append(entity)
            except Exception as ex:
                _LOGGER.error("  Failed to create connected via for %s: %s", device.name, ex)

        if new_entities:
            _LOGGER.debug(
                "  Adding %d entities for device %s", len(new_entities), device.name
            )
            async_add_entities(new_entities)

    @callback
    def on_device_removed(er, mac, device):
        """Remove all sensor entities for a device that went offline."""
        sensor_dicts = [
            known_ip_sensors, known_mac_sensors, known_connection_type_sensors,
            known_signal_sensors, known_upload_speed_sensors, known_download_speed_sensors,
            known_connection_rate_sensors, known_frequency_sensors,
            known_brands_sensors, known_type_sensors,
            known_tx_data_sensors, known_rx_data_sensors,
            known_parent_control_sensors, known_connected_via_sensors,
        ]
        for d in sensor_dicts:
            entity = d.pop(mac, None)
            if entity and entity.entity_id:
                er.async_remove(entity.entity_id)

    @callback
    def coordinator_updated() -> None:
        """Update the status of the device."""
        watcher.look_for_changes(on_router_added)
        all_watcher.look_for_changes(
            on_device_added,
            on_device_removed if skip_offline else None,
        )

    config_entry.async_on_unload(coordinator.async_add_listener(coordinator_updated))
    coordinator_updated()


# ---------------------------
#   HuaweiSensor
# ---------------------------
class HuaweiSensor(CoordinatorEntity[HuaweiDataUpdateCoordinator], SensorEntity):
    entity_description: HuaweiSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = coordinator.get_device_info(description.device_mac)
        self._attr_unique_id = generate_entity_unique_id(
            coordinator, description.function_uid, description.device_mac
        )
        self.entity_id = generate_entity_id(
            coordinator,
            _ENTITY_DOMAIN,
            description.function_name,
            description.device_name,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_router_online(self.entity_description.device_mac)

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
        _LOGGER.debug("%s added to hass", self.name)


# ---------------------------
#   HuaweiUptimeSensor
# ---------------------------
class HuaweiUptimeSensor(HuaweiSensor):
    entity_description: HuaweiUptimeSensorEntityDescription
    _attr_native_value: datetime | None = None

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiUptimeSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.entity_description.device_mac is None:
            return self.coordinator.is_router_online(None)
        return self.coordinator.is_router_online(self.entity_description.device_mac) or self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        uptime_seconds = None
        router_info = self.coordinator.get_router_info(device_mac)

        if router_info and router_info.uptime:
            uptime_seconds = router_info.uptime
        elif device_mac:
            device_data = self.coordinator.get_device_uptime(device_mac)
            if device_data:
                uptime_seconds = device_data
                router_info = self.coordinator.get_router_info()

        if uptime_seconds:
            self._attr_native_value = get_past_moment(uptime_seconds)
            self._attr_extra_state_attributes["seconds"] = uptime_seconds
        else:
            self._attr_native_value = None
            self._attr_extra_state_attributes["seconds"] = None

        if device_mac:
            connected_device = self.coordinator.connected_devices.get(device_mac)
            if connected_device:
                if connected_device.ip_address:
                    self._attr_extra_state_attributes["ip_address"] = connected_device.ip_address
                self._attr_extra_state_attributes["mac_address"] = str(device_mac)
                self._attr_extra_state_attributes["device_name"] = connected_device.name
            else:
                self._attr_extra_state_attributes["ip_address"] = None
                self._attr_extra_state_attributes["mac_address"] = str(device_mac)
                self._attr_extra_state_attributes["device_name"] = device_mac

        if router_info:
            self._attr_extra_state_attributes["serial_number"] = router_info.serial_number
            self._attr_extra_state_attributes["model"] = router_info.model
            self._attr_extra_state_attributes["software_version"] = router_info.software_version

        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiConnectedDevicesSensor
# ---------------------------
class HuaweiConnectedDevicesSensor(HuaweiSensor):
    entity_description: HuaweiClientsSensorEntityDescription
    _attr_native_value: int = 0

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiClientsSensorEntityDescription,
        integration_options: HuaweiIntegrationOptions,
        devices_predicate: Callable[[ConnectedDevice], bool],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)

        self._integration_options = integration_options
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {}
        self._devices_predicate: Callable[[ConnectedDevice], bool] = devices_predicate

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.entity_description.device_mac is None:
            return self.coordinator.is_router_online(None)
        return self.coordinator.is_router_online(self.entity_description.device_mac) or self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        tags_enabled = self._integration_options.devices_tags

        total_clients: int = 0
        guest_clients: int = 0
        hilink_clients: int = 0
        wireless_clients: int = 0
        lan_clients: int = 0
        wifi_2_4_clients: int = 0
        wifi_5_clients: int = 0

        untagged_clients: int = 0
        tagged_devices: dict[DEVICE_TAG, int] = {}

        if tags_enabled:
            for tag in self.coordinator.tags_map.get_all_tags():
                tagged_devices[tag] = 0

        for device in self.coordinator.connected_devices.values():
            if not self._devices_predicate(device):
                continue

            total_clients += 1

            if device.is_guest:
                guest_clients += 1
            if device.is_hilink:
                hilink_clients += 1

            if device.interface_type == HuaweiInterfaceType.INTERFACE_LAN:
                lan_clients += 1
            elif device.interface_type == HuaweiInterfaceType.INTERFACE_2_4GHZ:
                wireless_clients += 1
                wifi_2_4_clients += 1
            elif device.interface_type == HuaweiInterfaceType.INTERFACE_5GHZ:
                wireless_clients += 1
                wifi_5_clients += 1

            if tags_enabled:
                if device.tags is None or len(device.tags) == 0:
                    untagged_clients += 1
                else:
                    for tag in device.tags:
                        if tag in tagged_devices:
                            tagged_devices[tag] += 1
                        else:
                            tagged_devices[tag] = 1

        self._attr_native_value = total_clients

        self._attr_extra_state_attributes["guest_clients"] = guest_clients
        self._attr_extra_state_attributes["hilink_clients"] = hilink_clients
        self._attr_extra_state_attributes["wireless_clients"] = wireless_clients
        self._attr_extra_state_attributes["lan_clients"] = lan_clients
        self._attr_extra_state_attributes["wifi_2_4_clients"] = wifi_2_4_clients
        self._attr_extra_state_attributes["wifi_5_clients"] = wifi_5_clients

        if tags_enabled:
            for tag, count in tagged_devices.items():
                self._attr_extra_state_attributes[f"tagged_{tag}_clients"] = count
            self._attr_extra_state_attributes[f"untagged_clients"] = untagged_clients

        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDiagnosticsSensor
# ---------------------------
class HuaweiDiagnosticsSensor(HuaweiSensor):
    """诊断传感器 - 显示集成的健康状态和统计信息"""

    entity_description: HuaweiDiagnosticsSensorEntityDescription
    _attr_native_value: str = "ok"

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiDiagnosticsSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self._attr_native_value = "ok"
        self._attr_extra_state_attributes = {}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        diagnostics = self.coordinator.diagnostics_info

        if diagnostics.get("primary_router_online"):
            self._attr_native_value = "ok"
        else:
            self._attr_native_value = "error"

        self._attr_extra_state_attributes = {
            "primary_router_online": diagnostics.get("primary_router_online", False),
            "primary_router_name": diagnostics.get("primary_router_name", "Unknown"),
            "satellite_routers_count": diagnostics.get("satellite_routers_count", 0),
            "total_connected_devices": diagnostics.get("total_connected_devices", 0),
            "active_devices": diagnostics.get("active_devices", 0),
            "wifi_2_4_ghz_devices": diagnostics.get("wifi_2_4_ghz_devices", 0),
            "wifi_5_ghz_devices": diagnostics.get("wifi_5_ghz_devices", 0),
            "lan_devices": diagnostics.get("lan_devices", 0),
            "port_mappings_count": diagnostics.get("port_mappings_count", 0),
            "url_filters_count": diagnostics.get("url_filters_count", 0),
            "time_control_items_count": diagnostics.get("time_control_items_count", 0),
            "zones_count": diagnostics.get("zones_count", 0),
        }

        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiGroupedDevicesSensor
# ---------------------------
class HuaweiGroupedDevicesSensor(HuaweiSensor):
    """分组设备列表传感器 - 显示按子路由器分组的设备"""

    entity_description: HuaweiGroupedDevicesSensorEntityDescription
    _attr_native_value: int = 0

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiGroupedDevicesSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description)
        self._device_list: list = []
        self._device_count: int = 0

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.entity_description.device_mac is None:
            return self.coordinator.is_router_online(None)
        return self.coordinator.is_router_online(self.entity_description.device_mac) or self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        devices = []
        target_mac = self.entity_description.device_mac

        for mac, device in self.coordinator.connected_devices.items():
            if target_mac is None:
                if device.is_active:
                    connected_to = device.connected_via_name or device.connected_via_id or "主路由"
                    devices.append({
                        "name": device.name,
                        "ip": device.ip_address or "",
                        "mac": device.mac,
                        "connected_to": connected_to,
                    })
            else:
                if device.connected_via_id == target_mac:
                    devices.append({
                        "name": device.name,
                        "ip": device.ip_address or "",
                        "mac": device.mac,
                        "interface": device.interface_type.value if hasattr(device.interface_type, 'value') else (str(device.interface_type) if device.interface_type else ""),
                    })

        devices.sort(key=lambda x: x.get("name", ""))
        self._device_list = devices
        self._device_count = len(devices)
        self._attr_native_value = self._device_count
        self._attr_extra_state_attributes = {
            "devices": self._device_list,
            "device_count": self._device_count,
        }
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiWanSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiWanSensorEntityDescription(SensorEntityDescription):
    function_name: str | None = None
    function_uid: str | None = None
    device_mac: MAC_ADDR | None = None
    device_name: str | None = None


# ---------------------------
#   HuaweiWanStatusSensor
# ---------------------------
class HuaweiWanStatusSensor(HuaweiSensor):
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str = "unknown"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        wan_info = self.coordinator.get_wan_info()
        if wan_info:
            self._attr_native_value = "已连接" if wan_info.connected else "已断开"
        else:
            self._attr_native_value = "未知"
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiRouterInfoSensor
# ---------------------------
class HuaweiRouterInfoSensor(HuaweiSensor):
    """路由器信息传感器 - 显示路由器型号、序列号等信息"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiWanSensorEntityDescription,
        info_type: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self._info_type = info_type

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_router_online(self.entity_description.device_mac)

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        router_info = self.coordinator.get_router_info(device_mac)
        
        if router_info:
            if self._info_type == "model":
                self._attr_native_value = router_info.model
            elif self._info_type == "serial_number":
                self._attr_native_value = router_info.serial_number
            elif self._info_type == "software_version":
                self._attr_native_value = router_info.software_version
            elif self._info_type == "hardware_version":
                self._attr_native_value = router_info.hardware_version
            elif self._info_type == "harmony_version":
                self._attr_native_value = router_info.harmony_os_version
            elif self._info_type == "mac_address":
                # 获取主路由器 MAC 地址 - 尝试多种方式
                self._attr_native_value = router_info.mac_address if router_info else None
                
                # 方式1: 从router_info获取
                if self._attr_native_value is None and router_info:
                    self._attr_native_value = router_info.mac_address
                
                # 方式2: 从连接设备中查找匹配cfg_host的设备
                if self._attr_native_value is None:
                    for mac, cd in self.coordinator._connected_devices.items():
                        if cd.ip_address == self.coordinator.cfg_host:
                            self._attr_native_value = str(mac)
                            _LOGGER.debug("Found main router MAC from connected devices: %s", self._attr_native_value)
                            break
                
                # 方式3: 如果是主路由器(无device_mac)，尝试查找is_router=True的设备
                if self._attr_native_value is None and device_mac is None:
                    for mac, cd in self.coordinator._connected_devices.items():
                        if cd.is_router:
                            self._attr_native_value = str(mac)
                            _LOGGER.debug("Found main router MAC from router devices: %s", self._attr_native_value)
                            break
                
                # 方式4: 如果还是没找到，尝试查找名称包含"router"或"网关"的设备
                if self._attr_native_value is None and device_mac is None:
                    for mac, cd in self.coordinator._connected_devices.items():
                        if cd.name and ("router" in cd.name.lower() or "网关" in cd.name or "Gateway" in cd.name):
                            self._attr_native_value = str(mac)
                            _LOGGER.debug("Found main router MAC from device name: %s (%s)", self._attr_native_value, cd.name)
                            break
                
                # 方式5: 从ARP表获取主路由器MAC
                if self._attr_native_value is None and device_mac is None:
                    self._attr_native_value = self.coordinator.get_primary_router_mac()
                    if self._attr_native_value:
                        _LOGGER.debug("Found main router MAC from ARP: %s", self._attr_native_value)
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiWanIpSensor
# ---------------------------
class HuaweiWanIpSensor(HuaweiSensor):
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        wan_info = self.coordinator.get_wan_info()
        if wan_info:
            self._attr_native_value = wan_info.address
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceIpSensor
# ---------------------------
class HuaweiDeviceIpSensor(HuaweiSensor):
    """IP地址传感器 - 显示连接设备的IP地址"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            # 普通设备或子路由器
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                self._attr_native_value = device.ip_address
            else:
                self._attr_native_value = None
        else:
            # 主路由器 - 从配置中获取主路由器的IP地址
            self._attr_native_value = self.coordinator.config_entry.data.get("host")
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceMacSensor
# ---------------------------
class HuaweiDeviceMacSensor(HuaweiSensor):
    """MAC地址传感器 - 显示连接设备的MAC地址"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            # 普通设备或子路由器
            self._attr_native_value = str(device_mac)
        else:
            # 主路由器 - 尝试多种方式获取MAC地址
            self._attr_native_value = None
            
            # 方式1: 从连接设备中查找匹配cfg_host的设备
            for mac, cd in self.coordinator._connected_devices.items():
                if cd.ip_address == self.coordinator.cfg_host:
                    self._attr_native_value = str(mac)
                    _LOGGER.debug("HuaweiDeviceMacSensor: Found main router MAC from IP match: %s", self._attr_native_value)
                    break
            
            # 方式2: 查找is_router=True的设备
            if self._attr_native_value is None:
                for mac, cd in self.coordinator._connected_devices.items():
                    if cd.is_router:
                        self._attr_native_value = str(mac)
                        _LOGGER.debug("HuaweiDeviceMacSensor: Found main router MAC from is_router: %s", self._attr_native_value)
                        break
            
            # 方式3: 查找名称包含"router"或"网关"的设备
            if self._attr_native_value is None:
                for mac, cd in self.coordinator._connected_devices.items():
                    if cd.name and ("router" in cd.name.lower() or "网关" in cd.name or "Gateway" in cd.name):
                        self._attr_native_value = str(mac)
                        _LOGGER.debug("HuaweiDeviceMacSensor: Found main router MAC from name: %s (%s)", self._attr_native_value, cd.name)
                        break
            
            # 方式4: 从ARP表获取主路由器MAC
            if self._attr_native_value is None:
                self._attr_native_value = self.coordinator.get_primary_router_mac()
                if self._attr_native_value:
                    _LOGGER.debug("HuaweiDeviceMacSensor: Found main router MAC from ARP: %s", self._attr_native_value)
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceConnectionTypeSensor
# ---------------------------
class HuaweiDeviceConnectionTypeSensor(HuaweiSensor):
    """连接类型传感器 - 显示设备的连接方式(WiFi/有线等)"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                self._attr_native_value = device.interface_type
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceSignalSensor
# ---------------------------
class HuaweiDeviceSignalSensor(HuaweiSensor):
    """信号强度传感器 - 显示设备的WiFi信号强度"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: int | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "dBm"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active and device._data.get("rssi") is not None
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                self._attr_native_value = device._data.get("rssi")
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceUploadSpeedSensor
# ---------------------------
class HuaweiDeviceUploadSpeedSensor(HuaweiSensor):
    """上传速度传感器 - 显示设备的上传速度"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: float | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "kB/s"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                self._attr_native_value = device._data.get("upload_rate_kilobytes_s")
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceDownloadSpeedSensor
# ---------------------------
class HuaweiDeviceDownloadSpeedSensor(HuaweiSensor):
    """下载速度传感器 - 显示设备的下载速度"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: float | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "kB/s"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                self._attr_native_value = device._data.get("download_rate_kilobytes_s")
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceConnectionRateSensor - WiFi连接速率(Mbps)
# ---------------------------
class HuaweiDeviceConnectionRateSensor(HuaweiSensor):
    """WiFi连接速率传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: int | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "Mbps"

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            self._attr_native_value = device._data.get("connection_rate") if device else None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceFrequencySensor - WiFi频段
# ---------------------------
class HuaweiDeviceFrequencySensor(HuaweiSensor):
    """WiFi频段传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            self._attr_native_value = device._data.get("frequency") if device else None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceBrandsSensor - 设备厂商
# ---------------------------
class HuaweiDeviceBrandsSensor(HuaweiSensor):
    """设备厂商传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            self._attr_native_value = device._data.get("dev_brands") if device else None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceTypeSensor - 设备类型
# ---------------------------
class HuaweiDeviceTypeSensor(HuaweiSensor):
    """设备类型传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            self._attr_native_value = device._data.get("icon_type") if device else None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceTxDataSensor - 发送流量
# ---------------------------
class HuaweiDeviceTxDataSensor(HuaweiSensor):
    """发送流量传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                kb = device._data.get("tx_kbytes")
                self._attr_native_value = f"{int(kb) / 1024:.1f} MB" if kb else "0 MB"
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceRxDataSensor - 接收流量
# ---------------------------
class HuaweiDeviceRxDataSensor(HuaweiSensor):
    """接收流量传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                kb = device._data.get("rx_kbytes")
                self._attr_native_value = f"{int(kb) / 1024:.1f} MB" if kb else "0 MB"
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceParentControlSensor - 家长控制
# ---------------------------
class HuaweiDeviceParentControlSensor(HuaweiSensor):
    """家长控制传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: bool | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            self._attr_native_value = device._data.get("parent_control") if device else None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiDeviceConnectedViaSensor - 连接至哪个路由器
# ---------------------------
class HuaweiDeviceConnectedViaSensor(HuaweiSensor):
    """连接至路由器传感器"""
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            return device is not None and device.is_active
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        device_mac = self.entity_description.device_mac
        if device_mac:
            device = self.coordinator.connected_devices.get(device_mac)
            if device:
                self._attr_native_value = device.connected_via_name or "主路由"
            else:
                self._attr_native_value = None
        else:
            self._attr_native_value = None
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiWanIpv6Sensor
# ---------------------------
class HuaweiWanIpv6Sensor(HuaweiSensor):
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: str | None = None
    _attr_extra_state_attributes: dict = {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        wan_info = self.coordinator.get_wan_info()
        if wan_info:
            ipv6 = wan_info.ipv6_address
            if ipv6 and "/" in ipv6:
                parts = ipv6.split("/")
                self._attr_extra_state_attributes["prefix_length"] = parts[1]
                ipv6 = parts[0]
            else:
                self._attr_extra_state_attributes.pop("prefix_length", None)
            self._attr_native_value = ipv6
        else:
            self._attr_native_value = None
            self._attr_extra_state_attributes.pop("prefix_length", None)
        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiWanSpeedSensor
# ---------------------------
class HuaweiWanSpeedSensor(HuaweiSensor):
    entity_description: HuaweiWanSensorEntityDescription
    _attr_native_value: float = 0.0

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_router_online(None)

    @callback
    def _handle_coordinator_update(self) -> None:
        wan_info = self.coordinator.get_wan_info()
        if wan_info:
            if "download" in self.entity_description.key:
                self._attr_native_value = float(wan_info.download_rate)
            else:
                self._attr_native_value = float(wan_info.upload_rate)
        else:
            self._attr_native_value = 0.0
        super()._handle_coordinator_update()


