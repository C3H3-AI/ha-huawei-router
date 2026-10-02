"""Huawei Mesh Router shared constants."""



from typing import Final



from homeassistant.const import Platform



DOMAIN: Final = "huawei_router"



STORAGE_VERSION: Final = 1



DATA_KEY_COORDINATOR: Final = "coordinator"

DATA_KEY_PLATFORMS: Final = "platforms"

DATA_KEY_SERVICES: Final = "services_count"



OPT_WIFI_ACCESS_SWITCHES = "wifi_access_switches"

OPT_URL_FILTER_SWITCHES = "url_filter_switches"

OPT_PORT_MAPPING_SWITCHES = "port_mapping_switches"

OPT_ROUTER_CLIENTS_SENSORS = "router_clients_sensors"

OPT_DEVICES_TAGS = "devices_tags"

OPT_DEVICE_TRACKER = "device_tracker"

OPT_DEVICE_TRACKER_ZONES = "device_tracker_zones"

OPT_EVENT_ENTITIES = "event_entities"

OPT_TIME_CONTROL_SWITCHES = "time_control_switches"
OPT_SKIP_OFFLINE_DEVICES = "skip_offline_devices"
OPT_AUTO_ASSOCIATE_DEVICES = "auto_associate_devices"
OPT_DEVICE_SENSOR_GROUPS = "device_sensor_groups"

# 设备级传感器分组:控制每台设备生成哪些实体
DEVICE_SENSOR_GROUP_OPTIONS: Final = {
    "core": "基础(IP/MAC/连接类型/连接至)",
    "signal": "信号(信号强度/WiFi频段)",
    "speed": "实时速率(上传/下载速度)",
    "traffic": "流量统计(发送/接收/连接速率)",
    "info": "设备信息(厂商/类型/在线时长/家长控制)",
}

# 默认只启用「基础」组。
#
# 理由（2026-09-30 实测，97 台设备 / 1665 实体）：
#   - 实时速率与静态设备信息每秒级刷新，写入 states 表却几乎无回溯价值；
#   - 设备级实体随设备数线性增长，是实体膨胀的主体；
#   - 关闭后仍可在集成「配置」中按需逐组开启。
# 需要更多信息时，用户在集成配置里勾选相应分组即可。
DEFAULT_DEVICE_SENSOR_GROUPS: Final = ["core"]
MIN_SCAN_INTERVAL: Final = 10



DEFAULT_HOST: Final = "192.168.3.1"

DEFAULT_USER: Final = "admin"

DEFAULT_PORT: Final = 80

DEFAULT_SSL: Final = False

DEFAULT_PASS: Final = ""

DEFAULT_NAME: Final = "Huawei Q6 Router"

DEFAULT_VERIFY_SSL: Final = False

DEFAULT_SCAN_INTERVAL: Final = 30

DEFAULT_WIFI_ACCESS_SWITCHES: Final = True

DEFAULT_ROUTER_CLIENTS_SENSORS: Final = True

DEFAULT_DEVICES_TAGS: Final = True

DEFAULT_DEVICE_TRACKER: Final = True

DEFAULT_DEVICE_TRACKER_ZONES: Final = True

DEFAULT_URL_FILTER_SWITCHES: Final = True

DEFAULT_PORT_MAPPING_SWITCHES: Final = True

DEFAULT_EVENT_ENTITIES: Final = True

DEFAULT_TIME_CONTROL_SWITCHES: Final = True
DEFAULT_SKIP_OFFLINE_DEVICES: Final = True
DEFAULT_AUTO_ASSOCIATE_DEVICES: Final = True



ATTR_MANUFACTURER: Final = "Huawei"

PLATFORMS: Final = [

    Platform.SWITCH,

    Platform.DEVICE_TRACKER,

    Platform.SENSOR,

    Platform.BUTTON,

    Platform.BINARY_SENSOR,

    Platform.SELECT,

    Platform.EVENT,

]

