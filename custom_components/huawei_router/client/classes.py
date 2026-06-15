"""Huawei api classes."""



from __future__ import annotations



from datetime import datetime, time

from dataclasses import dataclass

from enum import Enum, IntEnum, StrEnum

from typing import Any, Dict, Final, Iterable, TypeAlias



VENDOR_CLASS_ID_ROUTER: Final = "router"
HUAWEI_OUI_PREFIXES: Final = [
    "00:25:9e", "00:18:82", "00:1e:10", "00:22:a1",
    "04:02:1f", "04:25:c5", "04:33:c2", "04:75:03",
    "08:19:a6", "08:63:61", "08:7a:4c", "08:e8:4f",
    "0c:37:96", "0c:45:ba", "10:1b:54", "10:44:00",
    "14:b9:68", "14:d1:1f", "18:68:cb", "18:87:96",
    "1c:8e:5c", "20:08:ed", "20:0b:c7", "20:2b:c1",
    "24:09:95", "24:1f:a0", "24:69:a5", "24:7f:3c",
    "28:31:52", "28:6e:d4", "2c:ab:00", "30:d1:7e",
    "30:f3:35", "34:00:a3", "34:29:12", "34:6a:c2",
    "34:a3:95", "38:37:8b", "38:6b:bb", "3c:47:11",
    "40:4d:8e", "40:cb:a8", "44:55:b1", "44:6a:2f",
    "48:3c:0c", "48:62:76", "4c:1f:cc", "4c:54:99",
    "50:a4:d0", "50:c7:bf", "54:25:ea", "54:89:98",
    "54:a5:1b", "58:2a:b7", "58:60:5f", "5c:4c:a9",
    "5c:7d:5e", "5c:83:bf", "60:de:44", "60:e7:01",
    "64:3e:8c", "64:4b:f0", "64:a2:f9", "68:89:c1",
    "6c:b7:49", "70:54:f5", "70:8a:09", "70:a8:e3",
    "70:cf:86", "74:59:09", "74:88:2a", "74:a2:e6",
    "78:d7:5f", "78:f5:57", "7c:10:c9", "7c:60:97",
    "80:b6:86", "80:d0:9b", "80:fb:06", "84:46:fe",
    "84:74:60", "84:a8:e4", "84:be:52", "88:53:95",
    "88:65:49", "88:89:15", "88:ce:f8", "88:e3:ab",
    "8c:0d:76", "8c:34:fd", "8c:a9:82", "90:17:c8",
    "90:78:41", "90:e2:ba", "94:04:9c", "94:23:2c",
    "94:68:3d", "94:77:1b", "94:b1:0a", "98:48:98",
    "98:5a:eb", "98:7f:6d", "98:b8:23", "98:d2:93",
    "9c:28:ef", "9c:37:f4", "9c:74:1a", "9c:a1:0a",
    "a0:08:6f", "a0:f4:50", "a4:71:74", "a4:99:47",
    "a4:c6:4f", "a8:15:4d", "a8:57:4e", "a8:68:d3",
    "a8:c8:3a", "a8:fa:d8", "a8:ff:ae", "ac:4e:91",
    "ac:61:ea", "ac:85:3d", "ac:91:48", "ac:a1:2b",
    "ac:e8:7b", "ac:f1:08", "b0:7b:25", "b0:8a:7a",
    "b0:98:2b", "b0:a2:e5", "b4:15:13", "b4:30:52",
    "b4:74:9f", "b4:75:0e", "b4:8b:19", "b4:cd:27",
    "b4:e1:0f", "b4:f1:da", "b8:2a:72", "b8:3f:d2",
    "b8:41:a4", "b8:5a:73", "b8:73:24", "b8:bc:1b",
    "b8:d5:26", "b8:e8:56", "bc:25:e0", "bc:62:0e",
    "bc:76:91", "bc:83:4d", "bc:96:99", "bc:bc:1d",
    "c0:0d:db", "c0:1a:da", "c0:2b:3e", "c0:56:e3",
    "c4:05:28", "c4:06:73", "c4:4b:22", "c4:86:e9",
    "c4:99:71", "c4:e1:7e", "c4:f2:fb", "c8:0c:a8",
    "c8:29:8b", "c8:51:95", "c8:71:f8", "c8:7e:75",
    "c8:b5:ad", "c8:bd:6d", "cc:0d:10", "cc:2f:71",
    "cc:53:b5", "cc:6e:a4", "cc:96:82", "cc:a2:35",
    "d0:22:be", "d0:29:C3", "d0:41:c9", "d0:65:ca",
    "d0:7a:b5", "d0:ab:d5", "d4:09:19", "d4:2c:0d",
    "d4:61:9d", "d4:6a:a8", "d4:6e:5c", "d4:87:d6",
    "d4:8f:fd", "d4:90:9c", "d4:96:80", "d4:9a:cd",
    "d4:a3:3d", "d4:b1:10", "d4:bf:2a", "d4:c9:ef",
    "d4:d7:d5", "d4:e1:0f", "d4:f4:5b", "d4:fb:2e",
    "d4:fe:2f", "d8:00:4d", "d8:31:34", "d8:49:0b",
    "d8:6c:63", "d8:72:a3", "d8:7d:5c", "d8:8f:76",
    "d8:96:95", "d8:b6:c7", "d8:bb:2c", "d8:c1:72",
    "d8:c7:71", "d8:d1:cb", "d8:f5:ef", "dc:35:33",
    "dc:44:b6", "dc:4f:22", "dc:51:72", "dc:53:7c",
    "dc:56:e7", "dc:71:96", "dc:89:20", "dc:8f:76",
    "dc:93:3c", "dc:9f:db", "dc:a4:ca", "dc:b4:c4",
    "dc:d2:fc", "dc:e7:1c", "dc:ef:09", "e0:06:e6",
    "e0:19:1d", "e0:24:7f", "e0:29:19", "e0:34:9d",
    "e0:40:a0", "e0:47:7c", "e0:4c:1b", "e0:4f:43",
    "e0:53:46", "e0:61:43", "e0:63:da", "e0:67:89",
    "e0:6d:87", "e0:97:96", "e0:98:6e", "e0:9f:c9",
    "e0:b5:2d", "e0:c7:67", "e0:c8:82", "e0:d7:1b",
    "e0:d9:bf", "e0:dc:ff", "e0:e1:7b", "e0:e5:cf",
    "e0:f3:79", "e0:f8:47", "e4:06:1d", "e4:26:9f",
    "e4:3a:28", "e4:3d:34", "e4:45:10", "e4:4a:39",
    "e4:5c:78", "e4:5f:01", "e4:67:d3", "e4:6c:11",
    "e4:71:85", "e4:7c:e9", "e4:81:29", "e4:8b:7a",
    "e4:8f:d2", "e4:9a:dc", "e4:9e:1a", "e4:a7:2a",
    "e4:b1:e6", "e4:b9:7e", "e4:c6:3d", "e4:c9:6d",
    "e4:d3:32", "e4:d5:3d", "e4:e0:c5", "e4:e7:08",
    "e8:04:0b", "e8:08:8b", "e8:28:45", "e8:38:70",
    "e8:3a:bc", "e8:3e:b3", "e8:41:95", "e8:46:44",
    "e8:4b:44", "e8:4d:69", "e8:57:3f", "e8:5b:39",
    "e8:5d:78", "e8:5e:be", "e8:65:d4", "e8:68:5c",
    "e8:6d:6e", "e8:6f:18", "e8:72:31", "e8:7b:d1",
    "e8:93:09", "e8:95:8c", "e8:98:e6", "e8:a2:3b",
    "e8:be:81", "e8:c3:97", "e8:cd:2d", "e8:d1:1b",
    "e8:d7:76", "e8:db:84", "e8:dc:96", "e8:e5:d6",
    "e8:e6:34", "e8:f0:ef", "e8:f1:17", "e8:f4:0b",
    "ec:08:6b", "ec:11:27", "ec:12:65", "ec:13:2d",
    "ec:1c:4e", "ec:1f:82", "ec:23:3f", "ec:29:14",
    "ec:2d:63", "ec:38:8f", "ec:3a:3d", "ec:3c:5a",
    "ec:3f:4c", "ec:4e:e3", "ec:50:55", "ec:54:81",
    "ec:5a:3b", "ec:5c:69", "ec:5d:03", "ec:5f:82",
    "ec:62:64", "ec:67:64", "ec:68:7a", "ec:6c:9f",
    "ec:74:53", "ec:7a:6b", "ec:83:50", "ec:89:f4",
    "ec:8c:70", "ec:8e:76", "ec:93:28", "ec:96:37",
    "ec:9a:74", "ec:9b:f3", "ec:9c:68", "ec:a4:40",
    "ec:a6:ea", "ec:cb:30", "ec:d0:bb", "ec:d2:d3",
    "ec:d4:3b", "ec:db:02", "ec:e0:1d", "ec:e5:28",
    "ec:e9:50", "ec:eb:8c", "ec:f0:0e", "ec:f6:63",
    "f0:43:47", "f0:4d:a2", "f0:5a:09", "f0:62:53",
    "f0:77:60", "f0:8b:ca", "f0:8c:1a", "f0:8f:6d",
    "f0:98:9d", "f0:9f:9f", "f0:b0:14", "f0:b4:29",
    "f0:bf:98", "f0:c1:76", "f0:c2:91", "f0:c3:50",
    "f0:c8:60", "f0:c9:d1", "f0:cb:a1", "f0:d1:78",
    "f0:d4:92", "f0:d7:67", "f0:d9:42", "f0:dc:e2",
    "f0:e4:4e", "f0:e7:7e", "f0:ea:8b", "f0:f3:36",
    "f4:09:d8", "f4:0b:09", "f4:1b:a1", "f4:1e:16",
    "f4:1f:74", "f4:25:18", "f4:2f:af", "f4:30:09",
    "f4:38:1f", "f4:3b:ad", "f4:3e:e0", "f4:42:8d",
    "f4:47:34", "f4:4c:33", "f4:50:5e", "f4:51:9b",
    "f4:55:9c", "f4:56:aa", "f4:57:41", "f4:58:9e",
    "f4:5a:19", "f4:5c:46", "f4:5d:71", "f4:5f:9b",
    "f4:60:10", "f4:61:41", "f4:67:f2", "f4:68:59",
    "f4:69:d5", "f4:6a:6c", "f4:6b:57", "f4:6d:04",
    "f4:6e:6b", "f4:72:31", "f4:73:71", "f4:74:81",
    "f4:75:0b", "f4:75:31", "f4:77:8a", "f4:79:60",
    "f4:7b:5e", "f4:7c:2e", "f4:7f:27", "f4:7f:72",
    "f4:81:39", "f4:82:a9", "f4:84:2e", "f4:84:68",
    "f4:85:4e", "f4:86:32", "f4:87:61", "f4:8a:19",
    "f4:8b:05", "f4:8c:50", "f4:8d:78", "f4:8e:38",
    "f4:8f:4b", "f4:90:1e", "f4:90:cb", "f4:91:36",
    "f4:93:3c", "f4:94:66", "f4:95:24", "f4:96:34",
    "f4:97:d7", "f4:98:51", "f4:99:71", "f4:9a:69",
    "f4:9c:ef", "f4:9f:4f", "f4:a5:d3", "f4:a7:39",
    "f4:a8:33", "f4:a8:4b", "f4:ab:81", "f4:ad:4d",
    "f4:b1:23", "f4:b3:28", "f4:b5:2f", "f4:b5:bb",
    "f4:b6:1a", "f4:b8:2e", "f4:ba:7d", "f4:bb:1c",
    "f4:bc:83", "f4:bd:81", "f4:bd:e5", "f4:c1:46",
    "f4:c2:3d", "f4:c2:f5", "f4:c3:27", "f4:c4:2f",
    "f4:c6:3a", "f4:c7:14", "f4:c8:01", "f4:c9:84",
    "f4:ca:e5", "f4:cf:75", "f4:d1:31", "f4:d1:8a",
    "f4:d2:35", "f4:d4:35", "f4:d6:0c", "f4:d7:34",
    "f4:d8:09", "f4:d8:52", "f4:d9:fb", "f4:da:32",
    "f4:e3:fb", "f4:e5:66", "f4:e9:70", "f4:ea:ac",
    "f4:ec:38", "f4:f1:4b", "f4:f1:9a", "f4:f2:35",
    "f4:f4:33", "f4:f5:24", "f4:f6:61", "f4:f7:32",
    "f4:f8:08", "f4:fa:e1", "f4:fc:73", "f4:fe:05",
    "f8:01:13", "f8:0b:ca", "f8:16:54", "f8:18:9c",
    "f8:19:34", "f8:1a:73", "f8:1f:f2", "f8:2a:a8",
    "f8:2d:9c", "f8:2e:df", "f8:31:7b", "f8:34:41",
    "f8:37:18", "f8:3a:21", "f8:3a:89", "f8:3b:41",
    "f8:3e:7e", "f8:40:50", "f8:42:8c", "f8:46:c1",
    "f8:4a:bf", "f8:4b:4b", "f8:4c:90", "f8:4f:57",
    "f8:51:67", "f8:53:2e", "f8:55:36", "f8:58:6b",
    "f8:5a:3a", "f8:5b:4c", "f8:5c:4a", "f8:5e:4a",
    "f8:5f:8e", "f8:61:0a", "f8:63:bc", "f8:66:14",
    "f8:67:5e", "f8:69:71", "f8:6a:12", "f8:6b:3f",
    "f8:6d:90", "f8:6f:12", "f8:70:18", "f8:72:1e",
    "f8:73:77", "f8:74:24", "f8:74:e3", "f8:75:a7",
    "f8:7b:4c", "f8:7d:3d", "f8:7e:bd", "f8:81:3a",
    "f8:82:5e", "f8:83:56", "f8:85:ce", "f8:86:71",
    "f8:87:56", "f8:88:3c", "f8:88:71", "f8:8a:3b",
    "f8:8a:dd", "f8:8b:37", "f8:8c:8a", "f8:8e:fe",
    "f8:8f:09", "f8:8f:68", "f8:90:97", "f8:91:4d",
    "f8:93:2d", "f8:93:3d", "f8:93:fb", "f8:95:b3",
    "f8:95:d4", "f8:97:47", "f8:98:b1", "f8:99:70",
    "f8:9a:9c", "f8:9b:7c", "f8:9b:95", "f8:9d:0e",
    "f8:9f:7f", "f8:9f:b0", "f8:a1:2f", "f8:a1:d6",
    "f8:a2:5e", "f8:a3:43", "f8:a4:3f", "f8:a4:48",
    "f8:a5:1c", "f8:a5:8a", "f8:a6:7e", "f8:a7:19",
    "f8:a8:1f", "f8:a9:63", "f8:ab:1f", "f8:ac:6d",
    "f8:ac:70", "f8:af:10", "f8:b0:74", "f8:b1:14",
    "f8:b1:56", "f8:b2:7c", "f8:b3:54", "f8:b5:0c",
    "f8:b5:4f", "f8:b6:26", "f8:b6:5c", "f8:b7:09",
    "f8:b8:15", "f8:b9:27", "f8:ba:43", "f8:bc:12",
    "f8:bc:61", "f8:bd:1c", "f8:bd:7e", "f8:bd:9d",
    "f8:bf:1d", "f8:c0:01", "f8:c1:90", "f8:c2:3f",
    "f8:c3:16", "f8:c4:68", "f8:c5:0d", "f8:c5:77",
    "f8:c7:5a", "f8:c8:50", "f8:c9:19", "f8:cb:6b",
    "f8:cc:18", "f8:ce:58", "f8:d0:ac", "f8:d1:11",
    "f8:d1:69", "f8:d1:93", "f8:d2:17", "f8:d3:28",
    "f8:d4:51", "f8:d5:12", "f8:d7:93", "f8:d8:60",
    "f8:da:0c", "f8:dc:be", "f8:de:20", "f8:df:15",
    "f8:e0:1c", "f8:e1:54", "f8:e2:65", "f8:e4:26",
    "f8:e5:3c", "f8:e6:24", "f8:e6:8a", "f8:e7:71",
    "f8:e8:2d", "f8:ea:10", "f8:ea:43", "f8:ea:cb",
    "f8:eb:32", "f8:ec:a0", "f8:ee:28", "f8:ee:e3",
    "f8:f0:05", "f8:f0:82", "f8:f1:0c", "f8:f1:90",
    "f8:f2:3f", "f8:f3:19", "f8:f4:28", "f8:f5:32",
    "f8:f6:63", "f8:f7:5e", "f8:f8:09", "f8:f8:23",
    "f8:f9:68", "f8:fa:3c", "f8:fb:5c", "f8:fb:ba",
    "f8:fc:af", "f8:fd:48", "f8:fe:7a", "fc:18:3c",
    "fc:19:09", "fc:19:cd", "fc:1d:59", "fc:1e:ca",
    "fc:1f:02", "fc:1f:33", "fc:21:23", "fc:22:14",
    "fc:24:4f", "fc:25:3f", "fc:26:7b", "fc:27:f2",
    "fc:29:19", "fc:2a:f1", "fc:2c:55", "fc:2e:24",
    "fc:2f:6d", "fc:31:2f", "fc:31:76", "fc:32:1d",
    "fc:33:8e", "fc:34:97", "fc:35:e1", "fc:37:47",
    "fc:37:7f", "fc:38:1f", "fc:39:4a", "fc:3a:2a",
    "fc:3c:59", "fc:3e:22", "fc:3f:c2", "fc:41:27",
    "fc:42:26", "fc:43:27", "fc:44:dd", "fc:46:1c",
    "fc:48:ef", "fc:4a:90", "fc:4c:64", "fc:4e:4f",
    "fc:4f:5c", "fc:50:81", "fc:53:5e", "fc:54:d3",
    "fc:55:84", "fc:55:a4", "fc:57:0c", "fc:57:51",
    "fc:58:53", "fc:5a:2c", "fc:5c:4c", "fc:5e:94",
    "fc:5f:67", "fc:60:6e", "fc:62:2c", "fc:63:5b",
    "fc:64:3f", "fc:65:de", "fc:66:47", "fc:66:cf",
    "fc:68:3f", "fc:69:47", "fc:6a:32", "fc:6b:4d",
    "fc:6b:53", "fc:6d:7e", "fc:6e:cd", "fc:70:3b",
    "fc:71:fa", "fc:72:4c", "fc:73:0a", "fc:74:8e",
    "fc:75:64", "fc:76:1f", "fc:77:1e", "fc:77:45",
    "fc:78:ab", "fc:79:4b", "fc:7a:6e", "fc:7b:4e",
    "fc:7c:90", "fc:7e:35", "fc:80:5a", "fc:81:12",
    "fc:83:3a", "fc:84:29", "fc:85:37", "fc:85:e0",
    "fc:87:5d", "fc:88:26", "fc:89:26", "fc:8a:73",
    "fc:8b:d1", "fc:8c:9e", "fc:8e:94", "fc:8f:51",
    "fc:8f:76", "fc:90:3c", "fc:91:34", "fc:93:25",
    "fc:94:35", "fc:94:67", "fc:95:43", "fc:96:61",
    "fc:97:27", "fc:98:51", "fc:9a:f1", "fc:9b:b1",
    "fc:9c:06", "fc:9d:3d", "fc:9e:7c", "fc:9f:15",
    "fc:9f:71", "fc:a0:23", "fc:a1:6e", "fc:a2:3d",
    "fc:a3:3f", "fc:a4:13", "fc:a5:3c", "fc:a6:1d",
    "fc:a8:1f", "fc:a9:0e", "fc:aa:55", "fc:ab:10",
    "fc:ac:4d", "fc:ae:fa", "fc:b0:3a", "fc:b0:5c",
    "fc:b1:64", "fc:b2:08", "fc:b2:36", "fc:b3:34",
    "fc:b3:77", "fc:b4:0d", "fc:b4:27", "fc:b5:5b",
    "fc:b6:47", "fc:b6:64", "fc:b7:17", "fc:b7:32",
    "fc:b8:7c", "fc:b9:99", "fc:ba:23", "fc:ba:89",
    "fc:bb:0f", "fc:bb:37", "fc:bb:9b", "fc:bc:4c",
    "fc:bd:17", "fc:bd:87", "fc:be:7a", "fc:bf:0e",
    "fc:bf:8e", "fc:c0:54", "fc:c2:6b", "fc:c3:51",
    "fc:c4:4a", "fc:c5:3c", "fc:c6:6c", "fc:c7:55",
    "fc:c8:11", "fc:ca:3a", "fc:ca:64", "fc:cb:1c",
    "fc:cc:25", "fc:cd:60", "fc:ce:11", "fc:d0:04",
    "fc:d1:0b", "fc:d2:0b", "fc:d3:8f", "fc:d4:4f",
    "fc:d5:0d", "fc:d5:68", "fc:d6:8b", "fc:d7:1f",
    "fc:d7:51", "fc:d8:60", "fc:d9:9c", "fc:db:65",
    "fc:db:ac", "fc:db:d2", "fc:dc:86", "fc:dd:32",
    "fc:de:3c", "fc:e1:0b", "fc:e1:28", "fc:e2:6a",
    "fc:e3:37", "fc:e3:5f", "fc:e4:37", "fc:e5:04",
    "fc:e6:2c", "fc:e6:63", "fc:e7:0e", "fc:e7:3a",
    "fc:e8:22", "fc:e8:6d", "fc:e9:24", "fc:e9:e5",
    "fc:ea:54", "fc:eb:63", "fc:ec:09", "fc:ed:37",
    "fc:ed:7d", "fc:ee:50", "fc:ee:c7", "fc:ef:03",
    "fc:ef:73", "fc:f0:19", "fc:f0:3b", "fc:f0:d6",
    "fc:f2:4a", "fc:f2:9a", "fc:f3:62", "fc:f4:2b",
    "fc:f5:08", "fc:f5:62", "fc:f5:c8", "fc:f6:27",
    "fc:f7:38", "fc:f7:84", "fc:f8:1e", "fc:f8:3b",
    "fc:f9:4e", "fc:f9:e2", "fc:fa:5e", "fc:fb:0c",
    "fc:fc:4d", "fc:fc:73", "fc:fd:25", "fc:fd:68",
]


def is_huawei_device(mac: str | None) -> bool:
    """Check if MAC address belongs to a Huawei device."""
    if not mac:
        return False
    mac_upper = mac.upper().replace("-", ":")
    mac_prefix = mac_upper[:8]
    return mac_prefix in HUAWEI_OUI_PREFIXES



NODE_HILINK_TYPE_DEVICE: Final = "Device"

NODE_HILINK_TYPE_NONE: Final = "None"



MAC_ADDR: TypeAlias = str



KILOBYTES_PER_SECOND: TypeAlias = int





# ---------------------------

#   Feature

# ---------------------------

class Feature(StrEnum):

    NFC = "feature_nfc"

    URL_FILTER = "feature_url_filter"

    WIFI_80211R = "feature_wifi_80211r"

    WIFI_TWT = "feature_wifi_twt"

    WLAN_FILTER = "feature_wlan_filter"

    DEVICE_TOPOLOGY = "feature_device_topology"

    GUEST_NETWORK = "feature_guest_network"

    PORT_MAPPING = "feature_port_mapping"

    TIME_CONTROL = "feature_time_control"





# ---------------------------

#   Switch

# ---------------------------

class Switch(StrEnum):

    NFC = "nfc_switch"

    WIFI_80211R = "wifi_80211r_switch"

    WIFI_TWT = "wifi_twt_switch"

    WLAN_FILTER = "wlan_filter_switch"

    GUEST_NETWORK = "guest_network_switch"





# ---------------------------

#   Action

# ---------------------------

class Action(StrEnum):

    REBOOT: Final = "reboot_action"





# ---------------------------

#   Frequency

# ---------------------------

class Frequency(StrEnum):

    WIFI_2_4_GHZ = "2.4GHz"

    WIFI_5_GHZ = "5GHz"





# ---------------------------

#   FilterAction

# ---------------------------

class FilterAction(Enum):

    ADD = 0

    REMOVE = 1





# ---------------------------

#   FilterMode

# ---------------------------

class FilterMode(IntEnum):

    BLACKLIST = 0

    WHITELIST = 1





# ---------------------------

#   HuaweiGuestNetworkDuration

# ---------------------------

class HuaweiGuestNetworkDuration(IntEnum):

    FOUR_HOURS = 1

    ONE_DAY = 2

    UNLIMITED = 3





# ---------------------------

#   HuaweiRsaPublicKey

# ---------------------------

@dataclass()

class HuaweiRsaPublicKey:

    rsan: str

    rsae: str

    signature: str





# ---------------------------

#   HuaweiGuestNetworkConfig

# ---------------------------

@dataclass()

class HuaweiGuestNetworkItem:

    item_id: str

    enabled: bool

    sec_opt: str

    can_enable: bool

    pwd_score: int

    valid_time: HuaweiGuestNetworkDuration

    ssid: str

    key: str

    frequency: str

    rest_rime: int





# ---------------------------

#   HuaweiFilterItem

# ---------------------------

@dataclass()

class HuaweiFilterItem:

    mac_address: MAC_ADDR

    name: str | None = None





# ---------------------------

#   HuaweiUrlFilterInfo

# ---------------------------

@dataclass()

class HuaweiUrlFilterInfo:

    filter_id: str

    url: str

    enabled: bool

    dev_manual: bool

    devices: list[HuaweiFilterItem]





# ---------------------------

#   DayOfWeek

# ---------------------------

class DayOfWeek(StrEnum):

    MONDAY = "Monday"

    TUESDAY = "Tuesday"

    WEDNESDAY = "Wednesday"

    THURSDAY = "Thursday"

    FRIDAY = "Friday"

    SATURDAY = "Saturday"

    SUNDAY = "Sunday"





# ---------------------------

#   HuaweiPortMappingItem

# ---------------------------

class HuaweiPortMappingItem:

    def __init__(

        self,

        id: str,

        name: str,

        enabled: bool,

        host_ip: str,

        host_mac: MAC_ADDR,

        host_name: str,

        application_id: str,

    ) -> None:

        self._id = id

        self._name = name

        self._enabled = enabled

        self._host_ip = host_ip

        self._host_name = host_name

        self._host_mac = host_mac

        self._application_id = application_id



    @classmethod

    def parse(cls, raw_data: dict[str, Any]) -> HuaweiPortMappingItem:

        id = raw_data.get("ID")

        if not id:

            raise ValueError("Id can not be empty")



        raw_enabled = raw_data.get("Enable")

        enabled = isinstance(raw_enabled, bool) and raw_enabled



        ip_address = raw_data.get("HostIPAddress", "")

        mac_address = raw_data.get("InternalHost", "")

        name = raw_data.get("Name", "")

        host_name = raw_data.get("HostName", "")

        application_id = raw_data.get("ApplicationID", "")



        return HuaweiPortMappingItem(

            id, name, enabled, ip_address, mac_address, host_name, application_id

        )



    @property

    def id(self) -> str:

        return self._id



    @property

    def name(self) -> str:

        return self._name



    @property

    def enabled(self) -> bool:

        return self._enabled



    @property

    def host_name(self) -> str:

        return self._host_name



    @property

    def host_ip(self) -> str:

        return self._host_ip



    @property

    def host_mac(self) -> str:

        return self._host_mac





# ---------------------------

#   HuaweiFilterItem

# ---------------------------

class HuaweiFilterInfo:

    def __init__(

        self,

        enabled: bool,

        whitelist: list[HuaweiFilterItem],

        blacklist: list[HuaweiFilterItem],

        mode: FilterMode,

    ) -> None:

        self._enabled = enabled

        self._whitelist = whitelist

        self._blacklist = blacklist

        self._mode = mode



    @classmethod

    def parse(cls, raw_data: dict[str, Any]) -> HuaweiFilterInfo:

        raw_enabled = raw_data.get("MACAddressControlEnabled")

        enabled = isinstance(raw_enabled, bool) and raw_enabled



        raw_mode = raw_data.get("MacFilterPolicy")

        if raw_mode == 0:

            mode = FilterMode.BLACKLIST

        elif raw_mode == 1:

            mode = FilterMode.WHITELIST

        else:

            raise ValueError("MacFilterPolicy must be in range [0..1]")



        def get_item(raw_item: dict[str, Any]) -> HuaweiFilterItem:

            return HuaweiFilterItem(

                name=raw_item.get("HostName"), mac_address=raw_item.get("MACAddress")

            )



        raw_whitelist = raw_data.get("WMACAddresses")

        whitelist = [get_item(item) for item in raw_whitelist]



        raw_blacklist = raw_data.get("BMACAddresses")

        blacklist = [get_item(item) for item in raw_blacklist]



        return HuaweiFilterInfo(enabled, whitelist, blacklist, mode)



    @property

    def enabled(self) -> bool:

        return self._enabled



    @property

    def mode(self) -> FilterMode:

        return self._mode



    @property

    def whitelist(self) -> Iterable[HuaweiFilterItem]:

        return self._whitelist



    @property

    def blacklist(self) -> Iterable[HuaweiFilterItem]:

        return self._blacklist





# ---------------------------

#   HuaweiRouterInfo

# ---------------------------

@dataclass
class HuaweiRouterInfo:
    name: str
    model: str
    serial_number: str
    hardware_version: str
    software_version: str
    harmony_os_version: str
    uptime: int
    mac_address: str | None = None





# ---------------------------

#   HuaweiConnectionInfo

# ---------------------------

@dataclass
class HuaweiConnectionInfo:
    uptime: int
    connected: bool
    address: str | None
    ipv6_address: str | None
    upload_rate: KILOBYTES_PER_SECOND
    download_rate: KILOBYTES_PER_SECOND





# ---------------------------

#   HuaweiClientDevice

# ---------------------------

class HuaweiClientDevice:

    def __init__(self, device_data: Dict) -> None:

        """Initialize."""

        self._data: Dict = device_data



    def get_raw_value(self, property_name: str) -> Any | None:

        """Return the raw value from api response."""

        return self._data.get(property_name)



    @property

    def mac_address(self) -> MAC_ADDR | None:

        """Return the mac address of the device."""

        return self._data.get("MACAddress")



    @property

    def is_active(self) -> bool:

        """Return true when device is connected to network."""

        value = self._data.get("Active")

        return isinstance(value, bool) and value



    @property

    def rssi(self) -> int | None:

        """Return signal strength."""

        value = self._data.get("rssi")

        return value if isinstance(value, int) else None



    @property
    def is_hilink(self) -> bool:
        """Return true when device is hilink or Huawei device."""
        value = self._data.get("HiLinkDevice")
        if isinstance(value, bool) and value:
            return True
        actual_name = self._data.get("ActualName", "")
        host_name = self._data.get("HostName", "")
        combined_name = (actual_name + host_name).lower()
        if any(pattern in combined_name for pattern in ["huawei", "hilink", "华为", "ws8000", "ws8500", "q6"]):
            return True
        if is_huawei_device(self._data.get("MACAddress")):
            return True
        return False



    @property

    def is_guest(self) -> bool:

        """Return true when device is guest."""

        value = self._data.get("IsGuest")

        return isinstance(value, bool) and value



    @property
    def is_router(self) -> bool:
        """Return true when device is a mesh router (HiLink or Huawei)."""
        if self.is_hilink and self._data.get("VendorClassID") == VENDOR_CLASS_ID_ROUTER:
            return True
        actual_name = self._data.get("ActualName", "")
        host_name = self._data.get("HostName", "")
        combined_name = (actual_name + host_name).lower()
        phone_patterns = ["p60", "p70", "p80", "p90", "mate ", "nova ", "honor ", "pixel", "iphone", "ipad", "galaxy", "redmi", "xiaomi ", "oppo ", "vivo ", "pad", "phone"]
        if any(pattern in combined_name for pattern in phone_patterns):
            return False
        router_patterns = ["ws-", "ws8000", "ws8500", "q6", "凌霄", "ax3", "ax6", "ax3pro", "tc7102", "tc7206"]
        if any(pattern in combined_name for pattern in router_patterns):
            return True
        return False



    @property

    def actual_name(self) -> str | None:

        """Return the name of the device."""

        return self._data.get("ActualName")



    @property

    def host_name(self) -> str | None:

        """Return the host name of the device."""

        return self._data.get("HostName")



    @property

    def ip_address(self) -> str | None:

        """Return the ip address of the device."""

        return self._data.get("IPAddress")



    @property

    def interface_type(self) -> str | None:

        """Return the connection interface type."""

        return self._data.get("InterfaceType")



    @property

    def upload_rate(self) -> KILOBYTES_PER_SECOND:

        """Return the upload rate in kilobytes per second."""

        return self._data.get("UpRate", 0)



    @property
    def download_rate(self) -> KILOBYTES_PER_SECOND:
        """Return the download rate in kilobytes per second."""
        return self._data.get("DownRate", 0)

    @property
    def uptime(self) -> int | None:
        """Return the uptime in seconds if available."""
        value = self._data.get("UpTime")
        return value if isinstance(value, int) else None


# ---------------------------
#   HuaweiClientDevice

# ---------------------------

class HuaweiDeviceNode:

    def __init__(self, mac: MAC_ADDR, hilink_type: str | None):

        """Initialize."""

        self._mac = mac

        self._hilink_type = hilink_type

        self._connected_devices: list[HuaweiDeviceNode] = []



    @property

    def mac_address(self) -> MAC_ADDR:

        """Return the mac address of the device."""

        return self._mac



    @property

    def hilink_type(self) -> str:

        """Return the hilink type of the device."""

        return self._hilink_type



    @property

    def connected_devices(self) -> Iterable[HuaweiDeviceNode]:

        """Return the nodes that are connected to the device."""

        return self._connected_devices



    def add_device(self, device: HuaweiDeviceNode) -> None:

        """Add connected node to the device."""

        self._connected_devices.append(device)





# ---------------------------

#   HuaweiTimeAccessItem

# ---------------------------

class HuaweiTimeControlItemDay:

    def __init__(

        self, day_of_week: DayOfWeek, is_enabled: bool, start: time, end: time

    ):

        """Initialize."""

        self._day_of_week = day_of_week

        self._is_enabled = is_enabled

        self._start = start

        self._end = end



    @property

    def day_of_week(self) -> DayOfWeek:

        """Return the day of week."""

        return self._day_of_week



    @property

    def is_enabled(self) -> bool:

        """Return the state of the day."""

        return self._is_enabled



    @property

    def start(self) -> time:

        """Return the start time at this day."""

        return self._start



    @property

    def end(self) -> time:

        """Return the end time at this day."""

        return self._end





# ---------------------------

#   HuaweiTimeAccessItem

# ---------------------------

class HuaweiTimeControlItem:

    def __init__(self, data: Dict):

        """Initialize."""

        self._data = data

        self._days: dict[DayOfWeek, HuaweiTimeControlItemDay] = {}



        for day_of_week in DayOfWeek:



            enabled_value = self._data.get(f"{day_of_week.value}enable")

            is_enabled: bool = isinstance(enabled_value, bool) and enabled_value



            start_value = self._data.get(f"{day_of_week.value}From", "00:00")

            start: time = datetime.strptime(start_value, "%H:%M").time()



            end_value = self._data.get(f"{day_of_week.value}To", "00:00")

            end: time = datetime.strptime(end_value, "%H:%M").time()



            day: HuaweiTimeControlItemDay = HuaweiTimeControlItemDay(

                day_of_week, is_enabled, start, end

            )



            self._days[day_of_week] = day



    @property

    def id(self) -> str:

        """Return the state of the item."""

        return self._data.get("ID")



    @property

    def name(self) -> str:

        """Return the name of the item."""

        device_names = [

            item.get("HostName", "device") for item in self._data.get("DeviceNames", [])

        ]

        days = [

            active_day.day_of_week.value

            for active_day in filter(lambda x: x.is_enabled, self._days.values())

        ]



        device_names_str = (

            "for " + ", ".join(device_names)

            if len(device_names) > 0

            else "for some devices"

        )



        if len(days) == 7:

            days_str = "for every day"

        elif days == ["Saturday", "Sunday"]:

            days_str = "on weekends"

        elif days == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:

            days_str = "on working days"

        else:

            days_str = "on " + ", ".join(days)



        return f"Time limit rule {device_names_str} {days_str}"



    @property

    def enabled(self) -> bool:

        """Return the state of the item."""

        value = self._data.get("Enable")

        return isinstance(value, bool) and value



    @property

    def devices_mac(self) -> Iterable[MAC_ADDR]:

        """Return the state of the item."""

        return [device.get("MACAddress", "no_mac_addr") for device in self._data.get("Devices", [])]



    @property

    def days(self) -> dict[DayOfWeek, HuaweiTimeControlItemDay]:

        """Return the schedule for each day."""

        return self._days



    def update(self, source: HuaweiTimeControlItem) -> None:

        self._data = source._data

        self._days = source._days



    def set_enabled(self, enabled: bool) -> None:

        self._data["Enable"] = enabled

