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
OPT_DEVICE_MAC_SENSORS = "device_mac_sensors"
OPT_FAST_SENSOR_WRITE_DIVISOR = "fast_sensor_write_divisor"
OPT_ACCESS_SWITCH_RETENTION_DAYS = "access_switch_retention_days"

# 配置入口结构版本（async_migrate_entry 链与之对齐）。
# v8: 引入 device_mac_sensors 选项；存量入口迁移时显式写 True 保持原行为，
#     新建入口由 config_flow 直接以 v8 创建（走默认 False）。
CONFIG_VERSION: Final = 8

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

# MAC 地址传感器：静态值且与设备注册表/tracker 属性重复，新装默认不建。
# 存量入口经 async_migrate_entry 显式写 True，升级不悄悄删实体。
DEFAULT_DEVICE_MAC_SENSORS: Final = False

# 易变量传感器（WAN 上/下行、CPU/内存、连接速率、收发流量）对外发布频率
# = scan_interval × N。默认 4（30s 轮询 → 约 2min 发布一次），1 = 原行为。
DEFAULT_FAST_SENSOR_WRITE_DIVISOR: Final = 4
MIN_FAST_SENSOR_WRITE_DIVISOR: Final = 1
MAX_FAST_SENSOR_WRITE_DIVISOR: Final = 60

# 设备离网超过 N 天后清理其 tracker/开关/传感器实体；0 = 不清理。
# 设备再次上线时实体会自动重建，device entry 与区域归属保留。
DEFAULT_ACCESS_SWITCH_RETENTION_DAYS: Final = 0

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

