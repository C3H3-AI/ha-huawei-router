"""Huawei api extended functions."""



import asyncio

import datetime

import logging

from typing import Any, Final, Iterable, Tuple



from aiohttp import ClientResponse



from .classes import (

    MAC_ADDR,

    Action,

    Feature,

    FilterAction,

    FilterMode,

    Frequency,

    HuaweiClientDevice,

    HuaweiConnectionInfo,

    HuaweiChannelInfo,

    HuaweiDeviceCount,

    HuaweiDeviceNode,

    HuaweiEthPort,

    HuaweiFilterInfo,

    HuaweiFilterItem,

    HuaweiGuestNetworkDuration,

    HuaweiGuestNetworkItem,

    HuaweiNtpStatus,

    HuaweiProcessStatus,

    HuaweiDhcpStaticLeaseItem,

    HuaweiPortMappingItem,

    HuaweiPortTriggerItem,

    HuaweiUPnPPortMappingItem,

    HuaweiRouterInfo,

    HuaweiRsaPublicKey,

    HuaweiTimeControlItem,

    HuaweiUrlFilterInfo,

    Switch,

)

from .const import (

    URL_DEVICE_INFO,

    URL_DEVICE_TOPOLOGY,

    URL_GUEST_NETWORK,

    URL_HOST_INFO,

    URL_PORT_MAPPING,

    URL_PORT_TRIGGER,

    URL_UPNP_PORT_MAPPING,

    URL_APPLICATION,

    URL_REBOOT,

    URL_REPEATER_INFO,

    URL_SWITCH_NFC,

    URL_SWITCH_WIFI_80211R,

    URL_SWITCH_WIFI_TWT,

    URL_TIME_CONTROL,

    URL_URL_FILTER,

    URL_TIMED_REDIAL,

    URL_WANDETECT,

    URL_WLAN_FILTER,

    URL_WAN_INFO,

    URL_DHCP_STATIC_LEASE,

    URL_UPNP,

    URL_IPV6_ENABLE,

    URL_DMZ,

    URL_FIREWALL,

    URL_REBOOT_PLAN,

    URL_DDNS,

    URL_DDNS_STATUS,

    URL_BAND_STEERING,

    URL_SMART_CONNECT,

    URL_CHANGE_DEVICE_NAME,

    URL_QOS_CLASS_HOST,

    WIFI_SECURITY_ENCRYPTED,

    WIFI_SECURITY_OPEN,

    URL_WLAN_RADIO,

    URL_WLAN_WPS,

    URL_WPS_SWITCH,

    URL_MULTI_SSID,

    URL_WLAN_TIMING_ACCELERATE,

    URL_WLAN_WIFI_SYNC,

    URL_LAN,

    URL_LAN_ALL,

    URL_LAN_HOST,

    URL_LAN_SERVER,

    URL_WLAN_DIAG_BASIC_2G,

    URL_WLAN_DIAG_BASIC_5G,

    URL_DIAGNOSTICS,

    URL_DIAGNOSTICS_DEVLIST,

    URL_DIAGNOSTICS_DOWNLOAD,

    URL_WAN_LEARN_CONFIG,

    URL_WAN_DIAGNOSE,

    URL_IPV6_WAN,

    URL_IPV6_LAN,

    URL_ALG,

    URL_TUNNEL,

    URL_SWAN,

    URL_SMART_VPN,

    URL_IPTV,

    URL_MAC_FILTER,

    URL_ACCESS_AUTH,

    URL_HOMESEC_ABFA,

    URL_HOMESEC_STEALNET,

    URL_XLINK_LOCK_NET,

    URL_GUEST_NETWORK_LIMIT_RATE,

    URL_GUEST_NETWORK_REST_TIME,

    URL_NTP,

    URL_PROCESS_STATUS,

    URL_ONLINE_STATE,

    URL_ETH_NEGOTIATION,

    URL_CHANNEL_INFO,

    URL_DEVICE_COUNT,

    URL_AUTO_UPGRADE,

    URL_ONLINE_UPGRADE,

    URL_PASSWORD_RULE,

    URL_USER_ACCOUNT,

    URL_LANGUAGE,

    URL_WIFI_SCAN,

    URL_WIFI_SCAN_RESULT,

    URL_REPEATER_STATE,

    URL_REPEATER_DIAG,

    URL_REPEATER_DIAL,

    URL_NETDISK_INFO,

    URL_NETDISK_CODE,

    URL_HILINK_STATUS,

    URL_SLAVE_SETUP,

    URL_MULTI_HOST_INFO,

    URL_SYSTEM_MODE,

)

from .coreapi import (
    APICALL_ERRCAT_REQUEST,
    APICALL_ERRCODE_REQUEST,
    ApiCallError,
    HuaweiCoreApi,
    _get_response_json,
)

from .crypto import rsa_encode

from .utils import HuaweiFeaturesDetector



_STATUS_CONNECTED: Final = "Connected"





# ---------------------------

#   UnsupportedActionError

# ---------------------------

class UnsupportedActionError(Exception):

    def __init__(self, message: str) -> None:

        """Initialize."""

        super().__init__(message)

        self._message = message



    def __str__(self, *args, **kwargs) -> str:

        """Return str(self)."""

        return self._message





# ---------------------------

#   InvalidActionError

# ---------------------------

class InvalidActionError(Exception):

    def __init__(self, message: str) -> None:

        """Initialize."""

        super().__init__(message)

        self._message = message



    def __str__(self, *args, **kwargs) -> str:

        """Return str(self)."""

        return self._message





class HuaweiApi:

    def __init__(

        self,

        host: str,

        port: int,

        use_ssl: bool,

        user: str,

        password: str,

        verify_ssl: bool,

    ) -> None:

        """Initialize."""

        self._core_api = HuaweiCoreApi(host, port, use_ssl, user, password, verify_ssl)

        self._is_features_updated = False

        self._logger = logging.getLogger(f"{__name__} ({host})")

        self._features = HuaweiFeaturesDetector(self._core_api, self._logger)

        self._logger.debug("New instance of HuaweiApi created")



    async def authenticate(self) -> None:

        """Perform authentication."""

        await self._core_api.authenticate()



    async def disconnect(self) -> None:

        """Disconnect from api."""

        await self._core_api.disconnect()



    async def _ensure_features_updated(self):

        if not self._is_features_updated:

            self._logger.debug("Updating available features")

            await self._features.update()

            self._is_features_updated = True

            self._logger.debug("Available features updated")



    @property

    def router_url(self) -> str:

        """URL address of the router."""

        return self._core_api.router_url



    async def is_feature_available(self, feature: Feature) -> bool:

        """Return true if specified feature is known and available."""

        await self._ensure_features_updated()

        return self._features.is_available(feature)



    @staticmethod

    def _router_data_check_authorized(

        response: ClientResponse, result: dict[str, Any]

    ) -> bool:

        if response.status == 404:

            return False

        if result is None or result.get("EmuiVersion", "-") == "-":

            return False

        return True



    @staticmethod

    def _wan_info_check_authorized(

        response: ClientResponse, result: dict[str, Any]

    ) -> bool:

        if response.status == 404:

            return False

        if result is None or result.get("ExternalIPAddress", "-") == "-":

            return False

        return True



    async def get_router_info(self) -> HuaweiRouterInfo:

        """Return the router information."""

        data = await self._core_api.get(

            URL_DEVICE_INFO, check_authorized=HuaweiApi._router_data_check_authorized

        )



        return HuaweiRouterInfo(
            name=data.get("FriendlyName"),
            model=data.get("custinfo", {}).get("CustDeviceName"),
            serial_number=data.get("SerialNumber"),
            software_version=data.get("SoftwareVersion"),
            hardware_version=data.get("HardwareVersion"),
            harmony_os_version=data.get("HarmonyOSVersion"),
            uptime=data.get("UpTime"),
            mac_address=data.get("MACAddress"),
        )



    async def get_wan_connection_info(self) -> HuaweiConnectionInfo:
        data = await self._core_api.get(
            URL_WANDETECT, check_authorized=HuaweiApi._wan_info_check_authorized
        )
        rate_data = await self._core_api.get(URL_WAN_INFO)

        return HuaweiConnectionInfo(
            uptime=data.get("Uptime", 0),
            connected=data.get("Status") == _STATUS_CONNECTED,
            address=data.get("ExternalIPAddress"),
            ipv6_address=data.get("ExternalIPv6Address") or data.get("IPv6Address"),
            upload_rate=rate_data.get("UpBandwidth", 0),
            download_rate=rate_data.get("DownBandwidth", 0),
        )

    # ---------------------------
    #   健康监控（均已真机验证）
    # ---------------------------

    async def get_process_status(self) -> HuaweiProcessStatus | None:
        """Return aggregate CPU / memory usage.

        Verified on Q6 网线版: the endpoint returns a list; the ``Total``
        entry carries the aggregate percentages.
        """
        data = await self._core_api.get(URL_PROCESS_STATUS)
        if not isinstance(data, list):
            return None
        for item in data:
            if isinstance(item, dict) and item.get("Name") == "Total":
                return HuaweiProcessStatus(
                    cpu_usage=int(item.get("CpuUsage", 0) or 0),
                    mem_usage=int(item.get("MemUsage", 0) or 0),
                )
        return None

    async def get_device_count(self) -> HuaweiDeviceCount | None:
        """Return connected-device counters."""
        data = await self._core_api.get(URL_DEVICE_COUNT)
        if not isinstance(data, dict):
            return None
        return HuaweiDeviceCount(
            hilink_devices=int(data.get("HiLinkDevNum", 0) or 0),
            active_devices=int(data.get("ActiveDeviceNumbers", 0) or 0),
            lan_active=int(data.get("LanActiveNumber", 0) or 0),
            user_number=int(data.get("UserNumber", 0) or 0),
        )

    async def get_ntp_status(self) -> HuaweiNtpStatus | None:
        """Return NTP synchronisation state."""
        data = await self._core_api.get(URL_NTP)
        if not isinstance(data, dict):
            return None
        return HuaweiNtpStatus(
            synchronized=bool(data.get("SntpIsSynchronizedStatus", False)),
            status=data.get("Status"),
            server_primary=data.get("NTPServer1"),
            server_secondary=data.get("NTPServer2"),
        )

    async def get_channel_info(self) -> HuaweiChannelInfo:
        """Return the current channel of each WiFi band.

        Verified payload: ``WifiStatus[].ChannelInfo[]``, where every entry
        carries an explicit ``FrequencyBand`` ("2.4GHz" / "5GHz") and a
        ``Channel``. The band label is authoritative — do not infer the band
        from the channel number. One entry is reported per mesh node, so the
        first node that reports a band wins (the whole mesh is single-channel).
        """
        data = await self._core_api.get(URL_CHANNEL_INFO)
        result = HuaweiChannelInfo()
        if not isinstance(data, dict):
            return result
        for node in data.get("WifiStatus", []) or []:
            for ch in (node or {}).get("ChannelInfo", []) or []:
                channel = ch.get("Channel")
                band = str(ch.get("FrequencyBand", ""))
                if not channel:
                    continue
                if band == "2.4GHz" and result.channel_2g is None:
                    result.channel_2g = int(channel)
                elif band == "5GHz" and result.channel_5g is None:
                    result.channel_5g = int(channel)
        return result

    async def get_eth_ports(self) -> Iterable[HuaweiEthPort]:
        """Return every physical Ethernet port with its negotiated speed."""
        data = await self._core_api.get(URL_ETH_NEGOTIATION)
        if not isinstance(data, dict):
            return []
        return [
            HuaweiEthPort(
                port_name=str(item.get("PortName", "?")),
                speed=int(item.get("Speed", 0) or 0),
                status=int(item.get("Status", 0) or 0),
            )
            for item in data.get("ethintflist", []) or []
            if isinstance(item, dict)
        ]



    async def get_switch_state(self, switch: Switch) -> bool:

        """Return the specified switch state."""

        await self._ensure_features_updated()



        if switch == Switch.NFC and self._features.is_available(Feature.NFC):

            data = await self._core_api.get(URL_SWITCH_NFC)

            return data.get("nfcSwitch") == 1



        elif switch == Switch.WIFI_80211R and self._features.is_available(

            Feature.WIFI_80211R

        ):

            data = await self._core_api.get(URL_SWITCH_WIFI_80211R)

            setting_value = data.get("WifiConfig", [{}])[0].get("Dot11REnable")

            return isinstance(setting_value, bool) and setting_value



        elif switch == Switch.WIFI_TWT and self._features.is_available(

            Feature.WIFI_TWT

        ):

            data = await self._core_api.get(URL_SWITCH_WIFI_TWT)

            setting_value = data.get("WifiConfig", [{}])[0].get("TWTEnable")

            return isinstance(setting_value, bool) and setting_value



        elif switch == Switch.WLAN_FILTER and self._features.is_available(

            Feature.WLAN_FILTER

        ):

            _, data = await self.get_wlan_filter_info()

            return data.enabled



        elif switch == Switch.GUEST_NETWORK and self._features.is_available(

            Feature.GUEST_NETWORK

        ):

            data_2g, data_5g = await self.get_guest_network_info()

            return (data_2g is not None and data_2g.enabled) or (

                data_5g is not None and data_5g.enabled

            )



        else:

            raise UnsupportedActionError(f"Unsupported switch: {switch}")



    async def set_switch_state(self, switch: Switch, state: bool) -> None:

        """Set the specified switch state."""

        await self._ensure_features_updated()



        if switch == Switch.NFC and self._features.is_available(Feature.NFC):

            await self._core_api.post(URL_SWITCH_NFC, {"nfcSwitch": 1 if state else 0})



        elif switch == Switch.WIFI_80211R and self._features.is_available(

            Feature.WIFI_80211R

        ):

            await self._core_api.post(

                URL_SWITCH_WIFI_80211R,

                {"Dot11REnable": state},

                extra_data={"action": "11rSetting"},

            )



        elif switch == Switch.WIFI_TWT and self._features.is_available(

            Feature.WIFI_TWT

        ):

            await self._core_api.post(

                URL_SWITCH_WIFI_TWT,

                {"TWTEnable": state},

                extra_data={"action": "TWTSetting"},

            )



        elif switch == Switch.WLAN_FILTER and self._features.is_available(

            Feature.WLAN_FILTER

        ):

            await self._set_wlan_filter_enabled(state)



        elif switch == Switch.GUEST_NETWORK and self._features.is_available(

            Feature.GUEST_NETWORK

        ):

            await self._set_guest_network_enabled(state)



        else:

            raise UnsupportedActionError(f"Unsupported switch: {switch}")



    async def get_known_devices(self) -> Iterable[HuaweiClientDevice]:

        """Return the known devices."""

        return [

            HuaweiClientDevice(item) for item in await self._core_api.get(URL_HOST_INFO)

        ]



    @staticmethod

    def _get_device(node: dict[str, Any]) -> HuaweiDeviceNode:

        device = HuaweiDeviceNode(node.get("MACAddress"), node.get("HiLinkType"))

        connected_devices = node.get("ConnectedDevices", [])

        for connected_device in connected_devices:

            inner_node = HuaweiApi._get_device(connected_device)

            device.add_device(inner_node)

        return device



    async def get_devices_topology(self) -> Iterable[HuaweiDeviceNode]:

        """Return the topology of the devices."""

        return [

            self._get_device(item)

            for item in await self._core_api.get(URL_DEVICE_TOPOLOGY)

        ]



    async def execute_action(self, action: Action) -> None:

        """Execute specified action."""

        if action == Action.REBOOT:

            await self._core_api.post(URL_REBOOT, {})

        elif action == Action.WAN_RECONNECT:

            await self.wan_reconnect()

        else:

            raise UnsupportedActionError(f"Unsupported action name: {action}")



    async def wan_reconnect(self) -> None:

        """Perform a PPPoE WAN disconnect + reconnect cycle.

        Uses the Huawei TimedRedial API (POST /api/ntwk/timedredial) which
        triggers a WAN re-dial at the specified time. We set the time to
        1 minute from now so the re-dial fires almost immediately.

        Verified on WS8000 series (Q6) firmware 6.1.0.20(V7R2).
        """

        # 1. Save current timedredial config so we can restore it later
        original_config = {}
        try:
            original_config = await self._core_api.get(URL_TIMED_REDIAL)
            self._logger.debug(
                "Saved original timedredial config: %s", original_config
            )
        except Exception as exc:
            self._logger.warning(
                "Could not read original timedredial config: %s", exc
            )

        # 2. Build re-dial time: now + 60 seconds (24h "HH:MM" format)
        trigger_time = (
            datetime.datetime.now() + datetime.timedelta(seconds=60)
        ).strftime("%H:%M")

        self._logger.info(
            "Triggering WAN reconnect via timedredial at %s", trigger_time
        )

        # 3. Enable timedredial with our trigger time
        await self._core_api.post(
            URL_TIMED_REDIAL,
            {"Enable": True, "RedialTime": trigger_time},
        )

        self._logger.info(
            "TimedRedial enabled at %s — waiting up to 120s for WAN to drop and re-dial...",
            trigger_time,
        )

        # 4. Wait for the re-dial to complete (give it up to 2 minutes)
        for _ in range(24):
            await asyncio.sleep(5)
            try:
                wan = await self._core_api.get(URL_WAN_INFO)
                status = wan.get("ConnectionStatus", "")
                uptime = wan.get("Uptime", 0)
                if status == "Connected" and isinstance(uptime, (int, float)) and uptime < 300:
                    self._logger.info(
                        "WAN reconnect confirmed! Status=%s, Uptime=%ss (< 5min)",
                        status,
                        uptime,
                    )
                    break
            except Exception as exc:
                self._logger.debug("While waiting for reconnect: %s", exc)

        # 5. Restore original timedredial config so we don't leave it enabled
        try:
            if original_config:
                await self._core_api.post(URL_TIMED_REDIAL, original_config)
                self._logger.info(
                    "Restored original timedredial config: %s", original_config
                )
            else:
                # Best-effort: just disable it
                await self._core_api.post(
                    URL_TIMED_REDIAL, {"Enable": False, "RedialTime": "04:00"}
                )
                self._logger.info("Disabled timedredial (no original config saved)")
        except Exception as exc:
            self._logger.warning(
                "Could not restore timedredial config: %s — please verify manually",
                exc,
            )

        self._logger.info("WAN reconnect cycle completed")



    async def apply_wlan_filter(

        self,

        filter_mode: FilterMode,

        filter_action: FilterAction,

        device_mac: MAC_ADDR,

        device_name: str | None = None,

    ) -> bool:

        """Apply filter to the device."""



        def verify_state(target_state: dict[str, Any]) -> bool:

            enabled = target_state.get("MACAddressControlEnabled")

            verification_result = isinstance(enabled, bool) and enabled

            if not verification_result:

                self._logger.warning("WLAN Filtering is not enabled")

            return verification_result



        state_2g, state_5g = await self._get_filter_states()



        if state_2g is None:

            self._logger.debug("Can not find actual 2.4GHz filter state")

            return False



        if state_5g is None:

            self._logger.debug("Can not find actual 5GHz filter state")

            return False



        if not verify_state(state_2g) or not verify_state(state_5g):

            self._logger.debug("Verification failed")

            return False



        need_action_2g, whitelist_2g, blacklist_2g = await self._process_access_lists(

            state_2g, filter_mode, filter_action, device_mac, device_name

        )

        if whitelist_2g is None or blacklist_2g is None or need_action_2g is None:

            self._logger.debug("Processing 2.4GHz filter failed")

            return False



        need_action_5g, whitelist_5g, blacklist_5g = await self._process_access_lists(

            state_5g, filter_mode, filter_action, device_mac, device_name

        )

        if whitelist_5g is None or blacklist_5g is None or need_action_5g is None:

            self._logger.debug("Processing 5GHz filter failed")

            return False



        if not need_action_2g and not need_action_5g:

            return True



        command = {

            "config2g": {

                "MACAddressControlEnabled": True,

                "WMacFilters": whitelist_2g,

                "ID": state_2g.get("ID"),

                "MacFilterPolicy": state_2g.get("MacFilterPolicy"),

                "BMacFilters": blacklist_2g,

                "FrequencyBand": state_2g.get("FrequencyBand"),

            },

            "config5g": {

                "MACAddressControlEnabled": True,

                "WMacFilters": whitelist_5g,

                "ID": state_5g.get("ID"),

                "MacFilterPolicy": state_5g.get("MacFilterPolicy"),

                "BMacFilters": blacklist_5g,

                "FrequencyBand": state_5g.get("FrequencyBand"),

            },

        }



        await self._core_api.post(URL_WLAN_FILTER, command)

        return True



    async def _set_wlan_filter_enabled(self, value: bool) -> bool:

        """Enable or disable wlan filtering."""



        state_2g, state_5g = await self._get_filter_states()



        if state_2g is None:

            self._logger.debug("Can not find actual 2.4GHz filter state")

            return False



        if state_5g is None:

            self._logger.debug("Can not find actual 5GHz filter state")

            return False



        current_value_2g = state_2g.get("MACAddressControlEnabled")

        current_value_2g = isinstance(current_value_2g, bool) and current_value_2g



        current_value_5g = state_5g.get("MACAddressControlEnabled")

        current_value_5g = isinstance(current_value_5g, bool) and current_value_5g



        current_state = current_value_2g and current_value_5g



        if current_state == value:

            return True



        command = {

            "config2g": {

                "MACAddressControlEnabled": value,

                "WMacFilters": state_2g.get("WMACAddresses"),

                "ID": state_2g.get("ID"),

                "MacFilterPolicy": state_2g.get("MacFilterPolicy"),

                "BMacFilters": state_2g.get("BMACAddresses"),

                "FrequencyBand": state_2g.get("FrequencyBand"),

            },

            "config5g": {

                "MACAddressControlEnabled": value,

                "WMacFilters": state_5g.get("WMACAddresses"),

                "ID": state_5g.get("ID"),

                "MacFilterPolicy": state_5g.get("MacFilterPolicy"),

                "BMacFilters": state_5g.get("BMACAddresses"),

                "FrequencyBand": state_5g.get("FrequencyBand"),

            },

        }



        await self._core_api.post(URL_WLAN_FILTER, command)

        return True



    async def set_wlan_filter_mode(self, value: FilterMode) -> bool:

        """Enable or disable wlan filtering."""



        state_2g, state_5g = await self._get_filter_states()



        if state_2g is None:

            self._logger.debug("Can not find actual 2.4GHz filter state")

            return False



        if state_5g is None:

            self._logger.debug("Can not find actual 5GHz filter state")

            return False



        current_state = state_5g.get("MacFilterPolicy")



        if current_state == value.value:

            return True



        command = {

            "config2g": {

                "MACAddressControlEnabled": state_2g.get("MACAddressControlEnabled"),

                "WMacFilters": state_2g.get("WMACAddresses"),

                "ID": state_2g.get("ID"),

                "MacFilterPolicy": value.value,

                "BMacFilters": state_2g.get("BMACAddresses"),

                "FrequencyBand": state_2g.get("FrequencyBand"),

            },

            "config5g": {

                "MACAddressControlEnabled": state_5g.get("MACAddressControlEnabled"),

                "WMacFilters": state_5g.get("WMACAddresses"),

                "ID": state_5g.get("ID"),

                "MacFilterPolicy": value.value,

                "BMacFilters": state_5g.get("BMACAddresses"),

                "FrequencyBand": state_5g.get("FrequencyBand"),

            },

        }



        await self._core_api.post(URL_WLAN_FILTER, command)

        return True



    async def get_wlan_filter_info(self) -> Tuple[HuaweiFilterInfo, HuaweiFilterInfo]:

        state_2g, state_5g = await self._get_filter_states()

        info_2g = HuaweiFilterInfo.parse(state_2g)

        info_5g = HuaweiFilterInfo.parse(state_5g)

        return info_2g, info_5g



    async def _get_filter_states(self):

        actual_states = await self._core_api.get(URL_WLAN_FILTER)

        state_2g = None

        state_5g = None

        for state in actual_states:

            frequency = state.get("FrequencyBand")

            if frequency == Frequency.WIFI_2_4_GHZ:

                state_2g = state

            elif frequency == Frequency.WIFI_5_GHZ:

                state_5g = state

        return state_2g, state_5g



    async def apply_url_filter_info(self, url_filter_info: HuaweiUrlFilterInfo) -> None:

        actual = await self.get_url_filter_info()

        existing_item = next(

            (item for item in actual if item.filter_id == url_filter_info.filter_id),

            None,

        )



        action: str = "update" if existing_item is not None else "create"



        data: dict[str, Any] = {

            "Devices": [

                {"MACAddress": device.mac_address} for device in url_filter_info.devices

            ],

            "DeviceNames": [

                {"HostName": device.name} for device in url_filter_info.devices

            ],

            "DevManual": url_filter_info.dev_manual,

            "URL": url_filter_info.url,

            "Status": 2 if url_filter_info.enabled else 0,

            "ID": url_filter_info.filter_id,

        }



        await self._core_api.post(URL_URL_FILTER, data, extra_data={"action": action})



    async def _process_access_lists(

        self,

        state: dict[str, Any],

        filter_mode: FilterMode,

        filter_action: FilterAction,

        device_mac: MAC_ADDR,

        device_name: str | None,

    ) -> Tuple[bool | None, dict[str, Any] | None, dict[str, Any] | None]:

        """Return (need_action, whitelist, blacklist)"""

        whitelist = state.get("WMACAddresses")

        blacklist = state.get("BMACAddresses")



        if whitelist is None:

            self._logger.debug("Can not find whitelist")

            return None, None, None



        if blacklist is None:

            self._logger.debug("Can not find blacklist")

            return None, None, None



        async def get_access_list_item() -> dict[str, Any]:

            if device_name:

                return {"MACAddress": device_mac, "HostName": device_name}

            # search for HostName if no item popped and no name provided

            known_devices = await self.get_known_devices()

            for device in known_devices:

                if device.mac_address == device_mac:

                    return {"MACAddress": device_mac, "HostName": device.actual_name}

            self._logger.debug("Can not find known device '%s'", device_mac)

            return {

                "MACAddress": device_mac,

                "HostName": f"Unknown device {device_mac}",

            }



        # | FilterAction | FilterMode |    WL    |   BL   |

        # |--------------|------------|----------|--------|

        # | ADD          | WHITELIST  |   Add    | Remove |

        # | ADD          | BLACKLIST  |  Remove  |  Add   |

        # | REMOVE       | WHITELIST  |  Remove  |  None  |

        # | REMOVE       | BLACKLIST  |   None   | Remove |



        whitelist_index: int | None = None

        blacklist_index: int | None = None



        for index in range(len(whitelist)):

            if device_mac == whitelist[index].get("MACAddress"):

                whitelist_index = index

                self._logger.debug(

                    "Device '%s' found at %s whitelist",

                    device_mac,

                    state.get("FrequencyBand"),

                )

                break



        for index in range(len(blacklist)):

            if device_mac == blacklist[index].get("MACAddress"):

                blacklist_index = index

                self._logger.debug(

                    "Device '%s' found at %s blacklist",

                    device_mac,

                    state.get("FrequencyBand"),

                )

                break



        if filter_action == FilterAction.REMOVE:

            if filter_mode == FilterMode.BLACKLIST:

                if blacklist_index is None:

                    self._logger.debug(

                        "Can not find device '%s' to remove from blacklist", device_mac

                    )

                    return False, whitelist, blacklist

                del blacklist[blacklist_index]

                return True, whitelist, blacklist

            elif filter_mode == FilterMode.WHITELIST:

                if whitelist_index is None:

                    self._logger.debug(

                        "Can not find device '%s' to remove from whitelist", device_mac

                    )

                    return False, whitelist, blacklist

                del whitelist[whitelist_index]

                return True, whitelist, blacklist

            else:

                raise InvalidActionError(f"Unknown FilterMode: {filter_mode}")



        elif filter_action == FilterAction.ADD:

            item_to_add = None



            if filter_mode == FilterMode.BLACKLIST:

                if whitelist_index is not None:

                    item_to_add = whitelist.pop(whitelist_index)

                if blacklist_index is not None:

                    self._logger.debug(

                        "Device '%s' already in the %s blacklist",

                        device_mac,

                        state.get("FrequencyBand"),

                    )

                    return False, whitelist, blacklist

                else:

                    blacklist.append(item_to_add or await get_access_list_item())

                    return True, whitelist, blacklist



            if filter_mode == FilterMode.WHITELIST:

                if blacklist_index is not None:

                    item_to_add = blacklist.pop(blacklist_index)

                if whitelist_index is not None:

                    self._logger.debug(

                        "Device '%s' already in the %s whitelist",

                        device_mac,

                        state.get("FrequencyBand"),

                    )

                    return False, whitelist, blacklist

                else:

                    whitelist.append(item_to_add or await get_access_list_item())

                    return True, whitelist, blacklist

            else:

                raise InvalidActionError(f"Unknown FilterMode: {filter_mode}")



        else:

            raise InvalidActionError(f"Unknown FilterAction: {filter_action}")



    async def get_is_repeater(self) -> bool:

        data = await self._core_api.get(URL_REPEATER_INFO)



        if data is None:

            return False



        repeater_enable = data.get("RepeaterEnable", False)



        return isinstance(repeater_enable, bool) and repeater_enable



    @staticmethod

    def _to_url_filter_info(data: dict[str, Any]) -> HuaweiUrlFilterInfo:

        result = HuaweiUrlFilterInfo(

            filter_id=data["ID"],

            url=data["URL"],

            enabled=data.get("Status", -1) == 2,

            dev_manual=data.get("DevManual") is True,

            devices=[

                HuaweiFilterItem(item[0].get("MACAddress"), item[1].get("HostName"))

                for item in zip(data["Devices"], data["DeviceNames"])

            ],

        )



        return result



    async def get_url_filter_info(self) -> Iterable[HuaweiUrlFilterInfo]:

        data = await self._core_api.get(URL_URL_FILTER)

        return [self._to_url_filter_info(item) for item in data]



    @staticmethod

    def _to_huawei_guest_network_item(source: dict[str, Any]):

        return HuaweiGuestNetworkItem(

            item_id=source["ID"],

            enabled=source["EnableFrequency"] is True,

            sec_opt=source["SecOpt"],

            can_enable=source["CanEnableFrequency"] is True,

            pwd_score=source["PwdScore"],

            valid_time=HuaweiGuestNetworkDuration(source["ValidTime"]),

            ssid=source["WifiSsid"],

            key=source["WpaPreSharedKey"],

            frequency=source["FrequencyBand"],

            rest_rime=source["RestTime"],

        )



    async def get_guest_network_info(

        self,

    ) -> Tuple[HuaweiGuestNetworkItem, HuaweiGuestNetworkItem]:

        data = await self._core_api.get(URL_GUEST_NETWORK)

        item_2g = None

        item_5g = None



        for item in data:

            if item.get("FrequencyBand") == Frequency.WIFI_2_4_GHZ:

                item_2g = item

            elif item.get("FrequencyBand") == Frequency.WIFI_5_GHZ:

                item_5g = item



        result_2g = None if not item_2g else self._to_huawei_guest_network_item(item_2g)

        result_5g = None if not item_5g else self._to_huawei_guest_network_item(item_5g)

        return result_2g, result_5g



    @staticmethod

    def _to_guest_wifi_config(

        current_item: HuaweiGuestNetworkItem,

        rsa_key: HuaweiRsaPublicKey,

        enabled: bool,

        ssid: str,

        duration: HuaweiGuestNetworkDuration,

        secure: bool,

        password: str | None,

    ) -> dict[str, Any]:

        if secure and not password:

            raise InvalidActionError("Password must be specified")



        return {

            "ID": current_item.item_id,

            "Enable": enabled and current_item.can_enable,

            "WifiSsid": ssid,

            "ValidTime": duration.value,

            "SecOpt": WIFI_SECURITY_OPEN if not secure else WIFI_SECURITY_ENCRYPTED,

            "WpaPreSharedKey": rsa_encode(password, rsa_key),

        }



    async def set_guest_network_state(

        self,

        enabled: bool,

        ssid: str,

        duration: HuaweiGuestNetworkDuration,

        secure: bool,

        password: str | None,

    ) -> None:

        rsa_key = self._core_api.rsa_key

        if not rsa_key:

            raise InvalidActionError("Can not obtain RSA public key")



        actual_2g, actual_5g = await self.get_guest_network_info()



        config2g = self._to_guest_wifi_config(

            actual_2g, rsa_key, enabled, ssid, duration, secure, password

        )

        config5g = self._to_guest_wifi_config(

            actual_5g, rsa_key, enabled, ssid, duration, secure, password

        )



        data = {"config5g": config5g, "config2g": config2g}



        await self._core_api.post(

            URL_GUEST_NETWORK,

            data,

            headers={"Content-Type": "application/json;charset=UTF-8;enp"},

        )



    async def get_port_mappings(

        self,

    ) -> Iterable[HuaweiPortMappingItem]:

        return [

            HuaweiPortMappingItem.parse(item)

            for item in await self._core_api.get(URL_PORT_MAPPING)

        ]



    async def set_port_mapping_state(self, port_mapping_id: str, enabled: bool) -> None:

        port_mappings = await self._core_api.get(URL_PORT_MAPPING)

        target = next(

            (item for item in port_mappings if item.get("ID") == port_mapping_id)

        )



        if not target:

            raise InvalidActionError(f"Unknown port mapping: {port_mapping_id}")



        target["Enable"] = enabled



        await self._core_api.post(

            URL_PORT_MAPPING, target, extra_data={"action": "update"}

        )



    async def add_port_mapping(
        self,
        name: str,
        mac_address: str,
        host_ip: str,
        protocol: str,
        external_port: str,
        internal_port: str,
        enabled: bool = True,
        host_name: str = "",
    ) -> bool:
        """Add a port mapping rule on Q6.

        Q6 requires a two-step flow (traced from the Web UI):
          1. POST /api/app/application  action=create — create the Application
             object that carries the protocol + port range (ItemList) and get
             back a fresh ApplicationID.
          2. POST /api/ntwk/portmapping action=create — bind that ApplicationID
             to the rule name / MAC / IP.
        """
        try:
            app_name = f"{name}_pm"
            app_payload = {
                "ID": "",
                "Name": app_name,
                "ObjAcc": 65535,
                "EnablePortmapping": True,
                "EnablePorttrigger": False,
                "EnableQos": False,
                "EnableFilter": False,
                "ItemList": [
                    {
                        "ID": "",
                        "Protocol": protocol,
                        "ExternalPort": external_port,
                        "ExternalPortEnd": external_port,
                        "InternalPort": internal_port,
                        "InternalPortEnd": internal_port,
                        "index": 1,
                    }
                ],
            }
            await self._core_api.post(
                URL_APPLICATION, app_payload, extra_data={"action": "create"}
            )

            application_id = await self._find_application_id(app_name)
            if not application_id:
                self._logger.warning("Application '%s' not found after create", app_name)
                return False

            mapping_payload = {
                "ID": "",
                "ApplicationID": application_id,
                "Name": name,
                "Enable": enabled,
                "HostName": host_name,
                "HostIPAddress": host_ip,
                "InternalHost": mac_address,
            }
            await self._core_api.post(
                URL_PORT_MAPPING, mapping_payload, extra_data={"action": "create"}
            )
            return True
        except Exception as ex:
            self._logger.warning("Failed to add port mapping: %s", ex)
            return False

    async def _find_application_id(self, name: str) -> str | None:
        """Return the ID of the Application with the given name, or None."""
        applications = self._coerce_list(await self._core_api.get(URL_APPLICATION))
        for application in applications:
            if application.get("Name") == name:
                return application.get("ID")
        return None

    async def remove_port_mapping(self, port_mapping_id: str) -> bool:
        """Remove a port mapping rule on Q6.

        Two-step teardown (verified against the router):
          1. POST /api/ntwk/portmapping action=delete — remove the rule.
          2. POST /api/app/application action=delete — remove the Application;
             the router cascades and removes its content items automatically.
        """
        try:
            mappings = self._coerce_list(await self._core_api.get(URL_PORT_MAPPING))
            target = next(
                (mapping for mapping in mappings if mapping.get("ID") == port_mapping_id),
                None,
            )
            if not target:
                self._logger.warning("Unknown port mapping: %s", port_mapping_id)
                return False
            application_id = target.get("ApplicationID", "")

            await self._core_api.post(
                URL_PORT_MAPPING, target, extra_data={"action": "delete"}
            )

            if application_id:
                await self._delete_application(application_id)

            return True
        except Exception as ex:
            self._logger.warning("Failed to remove port mapping: %s", ex)
            return False

    async def _delete_application(self, application_id: str) -> None:
        """Delete an Application object (the router cascades its content items)."""
        applications = self._coerce_list(await self._core_api.get(URL_APPLICATION))
        target_app = next(
            (application for application in applications if application.get("ID") == application_id),
            None,
        )
        if target_app:
            await self._core_api.post(
                URL_APPLICATION, target_app, extra_data={"action": "delete"}
            )

    @staticmethod
    def _coerce_list(data) -> list:
        """Normalize a list endpoint response (some wrap in a dict)."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "result", "items", "ItemList"):
                value = data.get(key)
                if isinstance(value, list):
                    return value
        return []



    async def set_port_trigger_state(
        self, port_trigger_id: str, enabled: bool
    ) -> None:
        """Enable or disable a port trigger rule.

        Fetches the current rule, toggles Enable, and posts back with action=update.
        Verified working on Huawei Q6 (action=update).
        """
        port_triggers = await self._core_api.get(URL_PORT_TRIGGER)

        target = next(
            (item for item in port_triggers if item.get("ID") == port_trigger_id),
            None,
        )

        if not target:
            raise InvalidActionError(f"Unknown port trigger: {port_trigger_id}")

        target["Enable"] = enabled

        await self._core_api.post(
            URL_PORT_TRIGGER, target, extra_data={"action": "update"}
        )



    async def add_port_trigger(
        self, name: str, application_id: str, enabled: bool = False
    ) -> bool:
        """Add a new port trigger rule.

        Q6 router uses TR-069 style:
          {"Name": "...", "Enable": bool, "ApplicationID": "InternetGatewayDevice.Services.X_Application.N."}
        action MUST be "create" (not "add") per Q6 逆向测试.
        """
        try:
            payload = {
                "Name": name,
                "Enable": enabled,
                "ApplicationID": application_id,
            }
            await self._core_api.post(
                URL_PORT_TRIGGER, payload, extra_data={"action": "create"}
            )
            return True
        except Exception:
            return False



    async def remove_port_trigger(self, port_trigger_id: str) -> bool:
        """Remove a port trigger rule by its ID.

        action MUST be "delete" (not "remove") per Q6 逆向测试.
        """
        try:
            # 先 get 完整对象，delete 时路由器需要完整 payload
            triggers = await self._core_api.get(URL_PORT_TRIGGER)
            target = next(
                (item for item in triggers if item.get("ID") == port_trigger_id),
                None,
            )
            if not target:
                return False

            await self._core_api.post(
                URL_PORT_TRIGGER, target, extra_data={"action": "delete"}
            )
            return True
        except Exception:
            return False



    async def get_port_triggers(self) -> Iterable[HuaweiPortTriggerItem]:
        """Get all port trigger rules."""
        return [
            HuaweiPortTriggerItem.parse(item)
            for item in await self._core_api.get(URL_PORT_TRIGGER)
        ]



    async def get_upnp_port_mappings(self) -> Iterable[HuaweiUPnPPortMappingItem]:
        """Get all UPnP port mapping rules."""
        data = await self._core_api.get(URL_UPNP_PORT_MAPPING)
        if isinstance(data, list):
            return [HuaweiUPnPPortMappingItem.parse(item) for item in data]
        return []



    async def _set_guest_network_enabled(self, enabled: bool) -> None:

        actual_2g, actual_5g = await self.get_guest_network_info()



        actual_enabled = (actual_2g is not None and actual_2g.enabled) or (

            actual_5g is not None and actual_5g.enabled

        )



        if actual_enabled == enabled:

            return



        primary_item = None



        for item in await self.get_guest_network_info():

            if item.can_enable:

                primary_item = item

                break



        if not primary_item:

            raise InvalidActionError("No one frequency can be enabled")



        await self.set_guest_network_state(

            enabled=enabled,

            ssid=primary_item.ssid,

            duration=primary_item.valid_time,

            secure=primary_item.sec_opt != WIFI_SECURITY_OPEN,

            password=primary_item.key,

        )



    async def get_time_control_items(self) -> Iterable[HuaweiTimeControlItem]:

        data = await self._core_api.get(URL_TIME_CONTROL)

        return [HuaweiTimeControlItem(item) for item in data]



    async def set_time_control_item_state(

        self, time_control_item_id: str, enabled: bool

    ) -> None:

        time_control_items = await self._core_api.get(URL_TIME_CONTROL)

        target = next(

            (

                item

                for item in time_control_items

                if item.get("ID") == time_control_item_id

            )

        )



        if not target:

            raise InvalidActionError(

                f"Unknown time control item: {time_control_item_id}"

            )



        target["Enable"] = enabled



        await self._core_api.post(

            URL_TIME_CONTROL, target, extra_data={"action": "update"}

        )

    # ---------------------------
    #   DHCP 静态 IP 保留（MAC-IP 绑定）
    # ---------------------------

    async def get_dhcp_static_leases(self) -> Iterable[HuaweiDhcpStaticLeaseItem]:
        """Get all DHCP static lease (MAC binding) entries."""
        return [
            HuaweiDhcpStaticLeaseItem.parse(item)
            for item in self._coerce_list(await self._core_api.get(URL_DHCP_STATIC_LEASE))
        ]

    async def add_dhcp_static_lease(
        self, ip_address: str, mac_address: str, enabled: bool = True
    ) -> bool:
        """Add a DHCP static lease (reserve IP for a MAC)."""
        try:
            payload = {
                "ID": "",
                "Yiaddr": ip_address,
                "Chaddr": mac_address.upper(),
                "Enable": enabled,
            }
            await self._core_api.post(
                URL_DHCP_STATIC_LEASE, payload, extra_data={"action": "create"}
            )
            return True
        except Exception as ex:
            self._logger.warning("Failed to add DHCP static lease: %s", ex)
            return False

    async def remove_dhcp_static_lease(self, lease_id: str) -> bool:
        """Remove a DHCP static lease by its ID."""
        try:
            leases = self._coerce_list(await self._core_api.get(URL_DHCP_STATIC_LEASE))
            target = next((x for x in leases if x.get("ID") == lease_id), None)
            if not target:
                self._logger.warning("Unknown DHCP static lease: %s", lease_id)
                return False
            await self._core_api.post(
                URL_DHCP_STATIC_LEASE, target, extra_data={"action": "delete"}
            )
            return True
        except Exception as ex:
            self._logger.warning("Failed to remove DHCP static lease: %s", ex)
            return False

    async def set_dhcp_static_lease_state(self, lease_id: str, enabled: bool) -> None:
        """Enable or disable a DHCP static lease."""
        leases = self._coerce_list(await self._core_api.get(URL_DHCP_STATIC_LEASE))
        target = next((x for x in leases if x.get("ID") == lease_id), None)
        if not target:
            raise InvalidActionError(f"Unknown DHCP static lease: {lease_id}")
        target["Enable"] = enabled
        await self._core_api.post(
            URL_DHCP_STATIC_LEASE, target, extra_data={"action": "update"}
        )

    # ---------------------------
    #   UPnP 总开关
    # ---------------------------

    async def set_upnp_enabled(self, enabled: bool) -> None:
        cfg = await self._core_api.get(URL_UPNP)
        cfg["enable"] = enabled
        await self._core_api.post(URL_UPNP, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   IPv6 开关
    # ---------------------------

    async def set_ipv6_enabled(self, enabled: bool) -> None:
        cfg = await self._core_api.get(URL_IPV6_ENABLE)
        cfg["Enable"] = 1 if enabled else 0
        await self._core_api.post(URL_IPV6_ENABLE, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   双频优选
    # ---------------------------

    async def set_band_steering_enabled(self, enabled: bool) -> None:
        cfg = await self._core_api.get(URL_BAND_STEERING)
        cfg["DbhoEnable"] = enabled
        await self._core_api.post(URL_BAND_STEERING, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   智能连接（多频合一）
    # ---------------------------

    async def set_smart_connect_enabled(self, enabled: bool) -> None:
        cfg = await self._core_api.get(URL_SMART_CONNECT)
        cfg["enable"] = enabled
        cfg["ntwksyncEnable"] = enabled
        await self._core_api.post(URL_SMART_CONNECT, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   防火墙等级
    # ---------------------------

    async def set_firewall_level(self, level: str) -> None:
        cfg = await self._core_api.get(URL_FIREWALL)
        cfg["SetLevel"] = level
        await self._core_api.post(URL_FIREWALL, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   DMZ 主机
    # ---------------------------

    async def set_dmz(self, enabled: bool, ip_address: str) -> None:
        cfg = await self._core_api.get(URL_DMZ)
        cfg["Enable"] = enabled
        if ip_address:
            cfg["IPAddress"] = ip_address
        await self._core_api.post(URL_DMZ, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   定时重启
    # ---------------------------

    async def set_scheduled_reboot(self, enabled: bool, reboot_time: str) -> None:
        cfg = await self._core_api.get(URL_REBOOT_PLAN)
        cfg["Enable"] = enabled
        if reboot_time:
            cfg["RebootTime"] = reboot_time
        await self._core_api.post(URL_REBOOT_PLAN, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   DDNS 动态域名
    # ---------------------------

    async def get_ddns_status(self) -> dict:
        """Return combined DDNS config and sync status."""
        ddns = await self._core_api.get(URL_DDNS)
        status = await self._core_api.get(URL_DDNS_STATUS)
        result = dict(ddns) if isinstance(ddns, dict) else {}
        if isinstance(status, dict):
            result["Status"] = status.get("Status", result.get("Status", ""))
            result["ConnectType"] = status.get("ConnectType", "")
        # Password 回传是被掩码的，屏蔽掉以免脏写
        result.pop("Password", None)
        return result

    async def set_ddns_enabled(self, enabled: bool) -> None:
        cfg = await self._core_api.get(URL_DDNS)
        cfg["Enable"] = enabled
        cfg.pop("Password", None)
        await self._core_api.post(URL_DDNS, cfg, extra_data={"action": "update"})

    # ---------------------------
    #   设备管理（列表模式：改名 / 限速 / 删除）
    # ---------------------------

    async def _find_host_info(self, mac_address: str) -> dict:
        """Locate a HostInfo entry by MAC address."""
        host_info = self._coerce_list(await self._core_api.get(URL_HOST_INFO))
        mac = str(mac_address).upper()
        target = next(
            (
                x
                for x in host_info
                if str(x.get("MACAddress", "")).upper() == mac
            ),
            None,
        )
        if not target:
            raise InvalidActionError(f"Unknown device MAC: {mac_address}")
        return target

    async def set_device_name(self, mac_address: str, name: str) -> None:
        """Rename a connected device.

        逆向自 Web UI devicesList.postName：
            POST api/system/changedevicename
            body: {"action":"update","data":[{"ActualName":<name>,"ID":<HostInfo[].ID>}]}
        Web UI 将名称截断到 64 字符。
        """
        target = await self._find_host_info(mac_address)
        payload = [{"ActualName": name[:64], "ID": target.get("ID")}]
        await self._core_api.post(
            URL_CHANGE_DEVICE_NAME, payload, extra_data={"action": "update"}
        )

    async def set_device_rate_limit(
        self,
        mac_address: str,
        enabled: bool | None = None,
        upload_kbps: int | None = None,
        download_kbps: int | None = None,
    ) -> None:
        """Set per-device QoS rate limit.

        逆向自 Web UI devicesList.postRate：
            POST api/app/qosclass_host，body 为完整的 HostInfo 条目对象（无 action）。
        相关字段：
            DeviceDownRateEnable   QoS 总开关
            DeviceMaxUpLoadRate    上行限速 (Kbps)
            DeviceMaxDownLoadRate  下行限速 (Kbps)
        Web UI 允许范围 100 ~ 1000000 Kbps。
        """
        target = await self._find_host_info(mac_address)
        if enabled is not None:
            target["DeviceDownRateEnable"] = enabled
        if upload_kbps is not None:
            target["DeviceMaxUpLoadRate"] = int(upload_kbps)
        if download_kbps is not None:
            target["DeviceMaxDownLoadRate"] = int(download_kbps)
        await self._core_api.post(URL_QOS_CLASS_HOST, target)

    async def remove_device(self, mac_address: str) -> None:
        """Delete a known device entry.

        逆向自 Web UI devicesList.delDevice：
            POST api/system/HostInfo
            body: {"action":"delete","data":{"ID":<HostInfo[].ID>}}
        """
        target = await self._find_host_info(mac_address)
        await self._core_api.post(
            URL_HOST_INFO, {"ID": target.get("ID")}, extra_data={"action": "delete"}
        )

    # ---------------------------
    #   通用 API 桥接（Web UI 剩余端点）
    # ---------------------------

    async def get_endpoint_config(self, path: str) -> Any:
        """对指定端点执行原始 GET，返回 {"status": <int>, "data": <json|None>}。

        刻意绕开 HuaweiCoreApi.get()：后者把 404 当作未授权并触发重新登录，
        批量探测未知端点时会打满路由器仅有的 2 个 admin session。
        """
        await self._core_api._ensure_initialized()
        response = await self._core_api._get_raw(path)
        data = await _get_response_json(response)
        return {"status": response.status, "data": data}

    async def set_endpoint_config(
        self, path: str, data: dict, action: str | None = None
    ) -> Any:
        """对指定端点执行原始 POST，data 作为顶层 data，action 可选。

        与 get_config 同理：端点在本机型不存在时（404）转成可读的
        `UnsupportedActionError`，避免底层 `ApiCallError` 直接抛给用户。
        """
        try:
            return await self._core_api.post(
                path, data, extra_data=({"action": action} if action else None)
            )
        except ApiCallError as ex:
            if "404" in str(ex):
                raise UnsupportedActionError(
                    f"本机型不支持该功能（端点 {path} 返回 404）"
                ) from ex
            raise

    async def get_config(self, path: str) -> Any:
        """GET 配置端点，返回解析后的 JSON（dict / list）。

        端点在本机型不存在时（HTTP 404）转成 `UnsupportedActionError` 并附可读说明
        —— 否则调用方只看到底层 `ApiCallError`，无法区分「本机型无此功能」与
        「参数写错了」。

        这层兜底覆盖全部走 get_config 的强类型服务。Web UI 是多机型共用代码，
        大量端点只在部分固件实现（实测 `multi_ssid` / `wps_switch` / `wlanwps`
        在 Q6 网线版均为 404）。
        """
        try:
            return await self._core_api.get(path)
        except ApiCallError as ex:
            if "404" in str(ex):
                raise UnsupportedActionError(
                    f"本机型不支持该功能（端点 {path} 返回 404）"
                ) from ex
            raise

    async def update_config(
        self, path: str, updates: dict[str, Any], action: str | None = "update"
    ) -> dict[str, Any]:
        """GET 完整对象 → 覆盖 updates 中的字段 → POST。

        GET 返回的不是 dict，或用户提供的字段在对象中不存在时抛
        InvalidActionError，避免把错误的 payload 写进路由器。
        """
        config = await self._core_api.get(path)
        if not isinstance(config, dict):
            raise InvalidActionError(
                f"端点 {path} 未返回配置对象，当前固件可能不支持该功能"
            )
        missing = [key for key in updates if key not in config]
        if missing:
            raise InvalidActionError(
                f"字段 {missing} 不在 {path} 的返回中，可用字段：{sorted(config.keys())}"
            )
        config.update(updates)
        await self._core_api.post(
            path, config, extra_data=({"action": action} if action else None)
        )
        return config

    # ---------------------------
    #   WiFi / SSID
    # ---------------------------

    async def set_wifi_radio_enabled(self, frequency: str, enabled: bool) -> None:
        """按频段开关 WiFi 射频。

        wlanradio 返回射频列表；按 FrequencyBand 匹配目标频段，改动其中
        首个含 "Enable" 的字段后整体回写该射频对象（字段名由 GET 返回推断）。
        """
        radios = self._coerce_list(await self._core_api.get(URL_WLAN_RADIO))
        if not radios:
            raise InvalidActionError(
                f"端点 {URL_WLAN_RADIO} 未返回射频列表，当前固件可能不支持该功能"
            )
        target = next(
            (
                item
                for item in radios
                if frequency.lower() in str(item.get("FrequencyBand", "")).lower()
            ),
            None,
        )
        if target is None:
            available = [item.get("FrequencyBand") for item in radios]
            raise InvalidActionError(
                f"未找到频段 {frequency} 的射频配置，可用频段：{available}"
            )
        enable_key = next((key for key in target if "enable" in key.lower()), None)
        if enable_key is None:
            raise InvalidActionError(
                f"未找到射频使能字段，可用字段：{sorted(target.keys())}"
            )
        target[enable_key] = enabled
        await self._core_api.post(URL_WLAN_RADIO, target)

    async def set_wps_enabled(self, enabled: bool) -> None:
        """开关 WPS（字段名 WpsEnable 已由逆向确认）。

        ⚠️ 本端点在 Q6 网线版（WS8000-16, 6.1.0.20）真机 404 —— 该机型未开放
        WPS 管理端点。此处把 404 转成可读的 UnsupportedActionError，
        让用户看到「本机型不支持」而不是底层错误。
        """
        try:
            await self._core_api.post(URL_WPS_SWITCH, {"WpsEnable": enabled})
        except ApiCallError as ex:
            if "404" in str(ex):
                raise UnsupportedActionError(
                    "本机型不支持该功能（WPS 管理端点返回 404）"
                ) from ex
            raise

    async def wps_pair_start(
        self,
        mode: str,
        pin: str | None = None,
        ap_pin_type: str = "default",
    ) -> None:
        """Trigger a WPS pairing session (frontend chunk 54, three modes).

        Verified payload shapes from Web UI wps page:
          - PBC:         {"WpsMode": "pbc"}
          - Client PIN:  {"WpsMode": "client-pin", "ClientPinCode": "<pin>"}
          - AP PIN:      {"WpsMode": "ap-pin", "ApPinType": "default"|"random"}

        ⚠️ Underlying endpoint is 404 on Q6 网线版 — callers must guard.
        """
        if mode == "pbc":
            payload: dict[str, Any] = {"WpsMode": "pbc"}
        elif mode == "client-pin":
            if not pin:
                raise InvalidActionError("client-pin mode requires a PIN")
            payload = {"WpsMode": "client-pin", "ClientPinCode": pin}
        elif mode == "ap-pin":
            payload = {
                "WpsMode": "ap-pin",
                "ApPinType": ap_pin_type if ap_pin_type in ("default", "random") else "default",
            }
        else:
            raise InvalidActionError(
                f"Unknown WPS mode: {mode} (expected pbc / client-pin / ap-pin)"
            )
        try:
            await self._core_api.post(URL_WLAN_WPS, payload)
        except ApiCallError as ex:
            if "404" in str(ex):
                raise UnsupportedActionError(
                    "本机型不支持该功能（WPS 端点返回 404）"
                ) from ex
            raise

    # ---------------------------
    #   WiFi 射频详情（diagnose_wlan_basic，真机已验证）
    # ---------------------------

    async def get_wlan_diag_basic(self, band: str) -> dict[str, Any]:
        """Return full radio parameters for one band ("2.4G" or "5G").

        Verified payload (Q6 网线版): Bandwidth / Channel / SSID / BSSID /
        RegulatoryDomain / MaxBitRate / BeaconType / WPAEncryptionModes /
        IEEE11iEncryptionModes / X_WlanStandard / TransmitPower /
        AutoChannelEnable / Enable ...
        """
        if band == "2.4G":
            url: Final = URL_WLAN_DIAG_BASIC_2G
        elif band == "5G":
            url = URL_WLAN_DIAG_BASIC_5G
        else:
            raise InvalidActionError(f"Unknown band: {band} (expected 2.4G / 5G)")
        return await self._core_api.get(url)

    async def get_lan_host(self) -> dict[str, Any]:
        """Return LAN host configuration (domain / gateway MAC / IP / mask)."""
        return await self._core_api.get(URL_LAN_HOST)

    # ---------------------------
    #   诊断日志（diagnose_crash，真机已验证全链路）
    # ---------------------------

    async def get_diagnostics_state(self) -> dict[str, Any]:
        """Return current diagnostics collection state.

        Verified fields: DiagnosticsState ("Requested" → "ExecLuaSuccess" /
        "ErrorExecLuaFailed" / "ErrorNoDiagnoseResult") and ResultState.
        """
        return await self._core_api.get(URL_DIAGNOSTICS)

    async def get_diagnostics_devlist(self) -> list[dict[str, Any]]:
        """Return the devices that can be diagnosed (main router + satellites).

        Verified against a real Q6 网线版: returns 6 entries, each with
        ``DeviceName`` / ``MACAddress`` / ``URL`` / ``IsMainDevice`` /
        ``IsSupportNtwkCrash``. Use the MAC of the target device when calling
        ``diagnostics_collect_start`` — this is how you collect a satellite
        router's log rather than the main router's.
        """
        data = await self._core_api.get(URL_DIAGNOSTICS_DEVLIST)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        return []

    async def diagnostics_collect_start(self, mac_address: str | None = None) -> dict[str, Any]:
        """Start a diagnostics log collection.

        Reverse-engineered from Web UI diagnose page (chunk 24):
          POST diagnose_crash {"CrashAction":"InfoCollect","Mac":..,"IsMainDev":..}
          extra_data action=update. Collection takes ~20-120s; poll
          get_diagnostics_state() until DiagnosticsState == ExecLuaSuccess.
        """
        if mac_address is None:
            data = await self._core_api.get(URL_DEVICE_INFO)
            mac_address = data.get("MACAddress") or data.get("SerialNumber")
        payload = {
            "CrashAction": "InfoCollect",
            "Mac": mac_address,
            "IsMainDev": True,
        }
        return await self._core_api.post(
            URL_DIAGNOSTICS, payload, extra_data={"action": "update"}
        )

    async def diagnostics_download(self, file_path: str) -> dict[str, Any]:
        """Download the collected diagnostics package to a local file.

        Verified against a real Q6 网线版: the endpoint returns
        ``application/octet-stream`` (a log archive whose first member is
        ``var/syslog``). Uses the live authenticated session (cookies) via
        ``_get_raw`` — no separate login, so it cannot trip the router's
        2-session rate limit.

        Returns {"path": ..., "size": ...}.
        """
        import os

        if not file_path or os.path.isdir(file_path):
            raise InvalidActionError(
                f"diagnostics_download 需要一个完整文件路径（含文件名），收到: {file_path}"
            )
        parent = os.path.dirname(os.path.abspath(file_path))
        if parent and not os.path.isdir(parent):
            raise InvalidActionError(f"目标目录不存在: {parent}")

        response = await self._core_api._get_raw(URL_DIAGNOSTICS_DOWNLOAD)
        if response.status != 200:
            raise ApiCallError(
                f"下载诊断日志失败，HTTP {response.status}（是否尚未完成收集？）",
                APICALL_ERRCODE_REQUEST,
                APICALL_ERRCAT_REQUEST,
            )
        total = 0
        with open(file_path, "wb") as fh:
            while chunk := await response.content.read(65536):
                fh.write(chunk)
                total += len(chunk)
        return {"path": file_path, "size": total}

    # ---------------------------
    #   配置导出 / 导入（reset 页，真机已验证导出）
    # ---------------------------

    async def config_export(self, file_path: str) -> dict[str, Any]:
        """Download the router configuration backup to a local file.

        Verified against a real Q6 网线版: GET ``/api/system/downloadcfg``
        returns ``application/octet-stream`` with
        ``Content-Disposition: attachment; filename=downloadconfigfile<ts>.conf``.
        The payload is an encrypted binary blob (~86 KB on this unit) — it is
        the exact file the Web UI "导出配置" saves and the only format
        ``config_import`` accepts. Uses the live authenticated session.
        """
        import os

        if not file_path or os.path.isdir(file_path):
            raise InvalidActionError(
                f"config_export 需要一个完整文件路径（含文件名），收到: {file_path}"
            )
        parent = os.path.dirname(os.path.abspath(file_path))
        if parent and not os.path.isdir(parent):
            raise InvalidActionError(f"目标目录不存在: {parent}")

        response = await self._core_api._get_raw("api/system/downloadcfg")
        if response.status != 200:
            raise ApiCallError(
                f"导出配置失败，HTTP {response.status}",
                APICALL_ERRCODE_REQUEST,
                APICALL_ERRCAT_REQUEST,
            )
        disposition = response.headers.get("Content-Disposition", "")
        data = await response.read()
        with open(file_path, "wb") as fh:
            fh.write(data)
        return {
            "path": file_path,
            "size": len(data),
            "server_filename": (
                disposition.split("filename=")[-1].strip('"') if disposition else None
            ),
        }

    async def config_import(
        self, file_path: str, wait_restart: bool = False
    ) -> dict[str, Any]:
        """Upload a previously exported ``.conf`` backup to the router.

        ⚠️⚠️ 破坏性操作：路由器会用该配置覆盖当前全部设置并自动重启（约 60 秒），
        期间整屋断网。前端强制 .conf 扩展名。

        Reverse-engineered from Web UI reset page (chunk 34) + common Upload
        component (chunk 0):
          POST /api/device/uploadconfigfile  multipart/form-data
            csrf_token        = "csrf:" + csrf_param + csrf_token
            textfield         = 文件名
            configurefilename = 文件二进制
        Optional polling: GET device/uploadconfigfileresult → {uploadFail: 0|1}.
        """
        import os

        if not file_path or not os.path.isfile(file_path):
            raise InvalidActionError(f"配置文件不存在: {file_path}")
        if not file_path.lower().endswith(".conf"):
            raise InvalidActionError("配置文件必须是 .conf（与 Web UI 导出格式一致）")

        # multipart 组装：csrf_token 字段是 "csrf:" + param + token 拼接
        csrf = self._core_api._active_csrf or {}
        csrf_value = (
            "csrf:" + str(csrf.get("csrf_param", "")) + str(csrf.get("csrf_token", ""))
        )
        form = aiohttp.FormData()
        form.add_field("csrf_token", csrf_value)
        form.add_field("textfield", os.path.basename(file_path))
        form.add_field(
            "configurefilename",
            open(file_path, "rb"),
            filename=os.path.basename(file_path),
            content_type="application/octet-stream",
        )

        import logging

        logging.getLogger(__name__).warning(
            "配置导入已发起（%s）——路由器将覆盖全部设置并重启，约 60 秒",
            file_path,
        )
        # multipart POST 需绕过 core 的 JSON dto 封装，直接用已认证 session
        await self._core_api._ensure_initialized()
        response = await self._core_api._session.post(
            url=self._core_api._get_url("api/device/uploadconfigfile"),
            data=form,
            verify_ssl=self._core_api._verify_ssl,
            timeout=600,
        )
        result = await _get_response_json(response)
        out: dict[str, Any] = {"errcode": result.get("errcode") if result else None}
        if wait_restart:
            # 前端提交后 60 秒跳转首页；这里轮询设备可达
            await asyncio.sleep(10)
            for _ in range(60):
                await asyncio.sleep(5)
                try:
                    r = await self._core_api._get_raw("api/system/deviceinfo")
                    if r.status == 200:
                        out["router_back"] = True
                        break
                except Exception:  # noqa: BLE001 - 重启期间不可达属预期
                    continue
            else:
                out["router_back"] = False
        return out

    # ---------------------------
    #   家庭安全（防暴力破解 + 防蹭网）
    # ---------------------------

    async def get_homesec(self) -> dict[str, Any]:
        """合并返回防暴力破解与防蹭网配置。"""
        abfa = await self._core_api.get(URL_HOMESEC_ABFA)
        stealnet = await self._core_api.get(URL_HOMESEC_STEALNET)
        return {"abfa": abfa, "stealnet": stealnet}

    async def set_homesec(
        self,
        abfa_enabled: bool | None = None,
        stealnet_enabled: bool | None = None,
    ) -> None:
        """分别设置家庭安全的两个子功能的开关。"""
        if abfa_enabled is not None:
            await self.update_config(
                URL_HOMESEC_ABFA, {"Enable": abfa_enabled}, action="update"
            )
        if stealnet_enabled is not None:
            await self.update_config(
                URL_HOMESEC_STEALNET, {"Enable": stealnet_enabled}, action="update"
            )

    # ---------------------------
    #   访客网络补充（限速 / 休息时间）
    # ---------------------------

    async def set_guest_network_limit_rate(
        self,
        enabled: bool,
        peak_rate: int | None = None,
        down_peak_rate: int | None = None,
    ) -> None:
        """设置访客网络限速（字段名 Enable/PeakRate/X_DownPeakRate 来自逆向）。"""
        updates: dict[str, Any] = {"Enable": enabled}
        if peak_rate is not None:
            updates["PeakRate"] = int(peak_rate)
        if down_peak_rate is not None:
            updates["X_DownPeakRate"] = int(down_peak_rate)
        await self.update_config(URL_GUEST_NETWORK_LIMIT_RATE, updates, action="update")

    # ---------------------------
    #   系统时间 / 自动升级 / 语言
    # ---------------------------

    async def set_auto_upgrade(
        self,
        enabled: bool,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> None:
        """设置自动升级（字段名 Enable/StartTime/EndTime 来自逆向）。"""
        updates: dict[str, Any] = {"Enable": enabled}
        if start_time is not None:
            updates["StartTime"] = start_time
        if end_time is not None:
            updates["EndTime"] = end_time
        await self.update_config(URL_AUTO_UPGRADE, updates, action="update")

    async def check_auto_upgrade(self) -> Any:
        """触发一次在线升级检查（action=check 已由逆向确认）。"""
        return await self.set_endpoint_config(URL_ONLINE_UPGRADE, {}, action="check")

    async def set_language(self, language: str) -> None:
        """切换系统语言（字段名 Language 为推断值，待真机验证）。"""
        await self._core_api.post(URL_LANGUAGE, {"Language": language})

    # ---------------------------
    #   诊断 / 中继 / 互联
    # ---------------------------

    async def trigger_wifi_scan(self) -> Any:
        """触发一次周边 WiFi 扫描。"""
        return await self.set_endpoint_config(URL_WIFI_SCAN, {})

    async def set_repeater_dial(self) -> None:
        """触发中继拨号（action=update 已由逆向确认）。"""
        await self.set_endpoint_config(URL_REPEATER_DIAL, {}, action="update")

    async def set_slave_setup(self, allow: bool) -> None:
        """设置是否允许被其他设备组网（字段名 hilink_allow 已由逆向确认）。"""
        await self._core_api.post(URL_SLAVE_SETUP, {"hilink_allow": allow})

    async def get_hilink_status(self) -> Any:
        """hilink_status 为 POST 型查询接口。"""
        return await self.set_endpoint_config(URL_HILINK_STATUS, {})

    async def get_multi_host_info(self) -> Any:
        """MultiHostInfo 为 POST 型查询接口。"""
        return await self.set_endpoint_config(URL_MULTI_HOST_INFO, {})

