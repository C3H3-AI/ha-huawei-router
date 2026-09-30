"""Support for binary sensors."""

from dataclasses import dataclass
import logging
from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client.classes import MAC_ADDR
from .helpers import (
    generate_entity_id,
    generate_entity_name,
    generate_entity_unique_id,
    get_coordinator,
    get_past_moment,
)
from .update_coordinator import HuaweiDataUpdateCoordinator
from .utils import get_readable_rate

_LOGGER = logging.getLogger(__name__)

_FUNCTION_DISPLAYED_NAME_WAN: Final = "互联网连接"
_FUNCTION_UID_WAN: Final = "internet_connection"

_FUNCTION_DISPLAYED_NAME_NTP: Final = "NTP同步"
_FUNCTION_UID_NTP: Final = "sensor_ntp_synced"

ENTITY_DOMAIN: Final = "binary_sensor"


# ---------------------------
#   HuaweiBinarySensorEntityDescription
# ---------------------------
@dataclass
class HuaweiBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes binary sensor entities."""

    function_name: str | None = None
    function_uid: str | None = None
    device_mac: MAC_ADDR | None = None
    device_name: str | None = None
    name: str | None = None


# ---------------------------
#   HuaweiWanSensorEntityDescription
# ---------------------------
@dataclass
class HuaweiWanSensorEntityDescription(HuaweiBinarySensorEntityDescription):
    """A class that describes WAN binary sensor entity."""

    native_unit_of_measurement: str | None = None
    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    device_class: BinarySensorDeviceClass | str | None = (
        BinarySensorDeviceClass.CONNECTIVITY
    )


def _ntp_is_synced(coordinator: HuaweiDataUpdateCoordinator) -> bool | None:
    """Return whether the router clock is NTP-synchronised.

    Backed by ``api/ntwk/sntp``, verified on Q6 网线版 (WS8000-16).
    """
    status = coordinator.get_ntp_status()
    if status is None:
        return None
    return status.synchronized


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for Huawei component."""
    coordinator = get_coordinator(hass, config_entry)

    sensors = [
        HuaweiWanBinarySensor(
            coordinator,
            HuaweiWanSensorEntityDescription(
                key="wan",
                icon="mdi:web",
                name=_FUNCTION_DISPLAYED_NAME_WAN,
                device_mac=None,
                device_name=None,
                function_uid=_FUNCTION_UID_WAN,
                function_name=_FUNCTION_DISPLAYED_NAME_WAN,
            ),
        )
    ]

    # NTP 同步状态（端点已真机验证）
    if coordinator.get_ntp_status() is not None:
        sensors.append(
            HuaweiNtpBinarySensor(
                coordinator,
                HuaweiBinarySensorEntityDescription(
                    key="ntp_synced",
                    icon="mdi:clock-check",
                    name=_FUNCTION_DISPLAYED_NAME_NTP,
                    device_mac=None,
                    device_name=None,
                    function_uid=_FUNCTION_UID_NTP,
                    function_name=_FUNCTION_DISPLAYED_NAME_NTP,
                ),
            )
        )

    async_add_entities(sensors)


# ---------------------------
#   HuaweiBinarySensor
# ---------------------------
class HuaweiBinarySensor(
    CoordinatorEntity[HuaweiDataUpdateCoordinator], BinarySensorEntity
):
    entity_description: HuaweiBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiBinarySensorEntityDescription,
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
            ENTITY_DOMAIN,
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
#   HuaweiWanBinarySensor
# ---------------------------
class HuaweiWanBinarySensor(HuaweiBinarySensor):
    entity_description: HuaweiBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        description: HuaweiBinarySensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self._attr_is_on = None
        self._attr_extra_state_attributes = {}

    @callback
    def _handle_coordinator_update(self) -> None:
        wan_info = self.coordinator.get_wan_info()
        if not wan_info:
            return

        self._attr_is_on = wan_info.connected
        self._attr_extra_state_attributes["external_ip"] = wan_info.address
        self._attr_extra_state_attributes["uptime_seconds"] = wan_info.uptime
        self._attr_extra_state_attributes["connected_at"] = get_past_moment(
            wan_info.uptime
        )
        self._attr_extra_state_attributes["upload_rate_kilobytes_s"] = wan_info.upload_rate
        self._attr_extra_state_attributes["download_rate_kilobytes_s"] = wan_info.download_rate
        self._attr_extra_state_attributes["upload_rate"] = get_readable_rate(wan_info.upload_rate)
        self._attr_extra_state_attributes["download_rate"] = get_readable_rate(wan_info.download_rate)

        super()._handle_coordinator_update()


# ---------------------------
#   HuaweiNtpBinarySensor
# ---------------------------
class HuaweiNtpBinarySensor(HuaweiBinarySensor):
    """NTP synchronisation state of the router."""

    entity_description: HuaweiBinarySensorEntityDescription
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @callback
    def _handle_coordinator_update(self) -> None:
        """Pull the latest NTP state from the coordinator."""
        self._attr_is_on = _ntp_is_synced(self.coordinator)
        super()._handle_coordinator_update()

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Expose the NTP servers and raw status string."""
        status = self.coordinator.get_ntp_status()
        if status is None:
            return {}
        return {
            "status": status.status,
            "server_primary": status.server_primary,
            "server_secondary": status.server_secondary,
        }
