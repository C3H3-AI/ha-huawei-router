"""Huawei router buttons."""

from abc import ABC
import asyncio
import logging
from typing import Final

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .classes import ConnectedDevice
from .client.classes import MAC_ADDR, Action
from .helpers import (
    generate_entity_id,
    generate_entity_unique_id,
    get_coordinator,
)
from .update_coordinator import ActiveRoutersWatcher, HuaweiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

_FUNCTION_DISPLAYED_NAME_REBOOT: Final = "重启"
_FUNCTION_UID_REBOOT: Final = "button_reboot"

ENTITY_DOMAIN: Final = "button"


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
) -> None:
    """Set up buttons for Huawei Router component."""
    coordinator = get_coordinator(hass, config_entry)

    # 主路由不在 connected_devices 中，需要直接创建重启按键
    primary_button = HuaweiRebootButton(coordinator, None)
    async_add_entities([primary_button])

    # 子路由通过 ActiveRoutersWatcher 动态创建重启按键
    _watch_for_satellite_routers(coordinator, config_entry, async_add_entities)


def _watch_for_satellite_routers(
    coordinator, config_entry, async_add_entities
) -> None:
    """监听子路由上线，动态创建重启按键。"""
    watcher: ActiveRoutersWatcher = ActiveRoutersWatcher(coordinator)
    known_buttons: dict[MAC_ADDR, HuaweiButton] = {}

    @callback
    def on_router_added(mac: MAC_ADDR, router: ConnectedDevice) -> None:
        if not known_buttons.get(mac):
            entity = HuaweiRebootButton(coordinator, router)
            async_add_entities([entity])
            known_buttons[mac] = entity

    @callback
    def coordinator_updated() -> None:
        watcher.look_for_changes(on_router_added)

    config_entry.async_on_unload(coordinator.async_add_listener(coordinator_updated))
    coordinator_updated()


class HuaweiButton(CoordinatorEntity[HuaweiDataUpdateCoordinator], ButtonEntity, ABC):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        action: Action,
        device_mac: MAC_ADDR | None,
    ) -> None:
        super().__init__(coordinator)
        self._action: Action = action
        self._device_mac: MAC_ADDR = device_mac
        self._attr_device_info = coordinator.get_device_info(device_mac)

    @property
    def available(self) -> bool:
        return self.coordinator.is_router_online(self._device_mac)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._handle_coordinator_update()
        if self._device_mac:
            _LOGGER.debug("Button %s (%s) added to hass", self._action, self._device_mac)
        else:
            _LOGGER.debug("Primary router button %s added to hass", self._action)

    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()

    async def async_press(self) -> None:
        await self.coordinator.execute_action(self._action, self._device_mac)

    def press(self) -> None:
        return asyncio.run_coroutine_threadsafe(
            self.async_press(), self.hass.loop
        ).result()


class HuaweiRebootButton(HuaweiButton):
    def __init__(
        self,
        coordinator: HuaweiDataUpdateCoordinator,
        device: ConnectedDevice | None,
    ) -> None:
        super().__init__(coordinator, Action.REBOOT, device.mac if device else None)
        self._attr_device_class = ButtonDeviceClass.RESTART
        self._attr_name = _FUNCTION_DISPLAYED_NAME_REBOOT
        self.entity_id = generate_entity_id(
            coordinator,
            ENTITY_DOMAIN,
            _FUNCTION_DISPLAYED_NAME_REBOOT,
            device.name if device else None,
        )
        self._attr_unique_id = generate_entity_unique_id(
            coordinator, _FUNCTION_UID_REBOOT, device.mac if device else None
        )
        self._attr_icon = "mdi:restart"
