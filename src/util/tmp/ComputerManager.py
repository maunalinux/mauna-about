import gi
import platform

gi.require_version("GUdev", "1.0")
gi.require_version("GLib", "2.0")
from gi.repository import GUdev, GLib

from managers import DBusManager

FILTERED_WORDS = [
    "o.e.m.",
    "oem",
    "manufacturer",
    "n/a",
    "default",
    "string",
    "filled",
    "product",
    "name",
    "unknown",
]

def get_ram_size():
    client = GUdev.Client.new(["dmi"])
    device = client.query_by_sysfs_path("/sys/devices/virtual/dmi/id")

    num_ram = device.get_property_as_uint64("MEMORY_ARRAY_NUM_DEVICES")
    ram_total = 0
    for i in range(num_ram):
        ram_size = device.get_property_as_uint64(f"MEMORY_DEVICE_{i}_SIZE")
        ram_total += ram_size

    return ram_total / 1024 / 1024 / 1024  # 16.0 GB

def get_memory_info():
    memory = []
    client = GUdev.Client.new(["dmi"])
    device = client.query_by_sysfs_path("/sys/devices/virtual/dmi/id")

    num_ram = device.get_property_as_uint64("MEMORY_ARRAY_NUM_DEVICES")
    for i in range(num_ram):
        vendor = device.get_property_as_strv(f"MEMORY_DEVICE_{i}_MANUFACTURER")[0]
        size = device.get_property_as_uint64(f"MEMORY_DEVICE_{i}_SIZE") / (1024 * 1024 * 1024)
        mem_type = device.get_property_as_strv(f"MEMORY_DEVICE_{i}_TYPE")[0]
        factor = device.get_property_as_strv(f"MEMORY_DEVICE_{i}_FORM_FACTOR")[0]
        name = f"{size} GB {mem_type} {factor}"
        serial = device.get_property_as_strv(f"MEMORY_DEVICE_{i}_SERIAL_NUMBER")[0]

        mem_device = {
            "name": name,
            "vendor": vendor,
            "driver": "",
            "available_drivers": "",
            "bus": "",
            "pci_id": "",
            "bus_address": "",
            "error_logs": [],
            "serial_number": serial
        }

        for k in mem_device.keys():
            if mem_device[k] is None:
                mem_device[k] = ""

        memory.append(mem_device)

    return memory

def get_computer_info():
    computer = {}

    # Model
    model = DBusManager.read_string_in_tuple(
        "org.freedesktop.hostname1", "/org/freedesktop/hostname1", "HardwareModel", 0
    )
    if model:
        computer["model"] = model
    else:
        with open("/sys/devices/virtual/dmi/id/product_name", "r") as f:
            computer["model"] = f.readline().strip()

    # Vendor
    vendor = DBusManager.read_string_in_tuple(
        "org.freedesktop.hostname1", "/org/freedesktop/hostname1", "HardwareVendor", 0
    )
    if vendor:
        computer["vendor"] = vendor
    else:
        with open("/sys/devices/virtual/dmi/id/sys_vendor", "r") as f:
            computer["vendor"] = f.readline().strip()

    # Family
    with open("/sys/devices/virtual/dmi/id/product_family", "r") as f:
        family = f.readline().strip()

        for f in FILTERED_WORDS:
            if f.lower() in family.lower():
                family = ""
                break

        computer["family"] = family

    # Chassis
    chassis = DBusManager.read_string_in_tuple(
        "org.freedesktop.hostname1", "/org/freedesktop/hostname1", "Chassis", 0
    )
    if chassis:
        computer["chassis"] = chassis
    else:
        computer["chassis"] = ""

    # Bios Date
    with open("/sys/devices/virtual/dmi/id/bios_date", "r") as f:
        computer["bios_date"] = f.readline().strip()

    # Kernel:
    computer["kernel"] = platform.release()

    # Arch:
    computer["architecture"] = platform.machine()

    # RAM:
    computer["ram"] = f"{get_ram_size()} GB"

    # OS
    with open("/etc/os-release", "r") as f:
        name = ""
        version = ""
        codename = ""

        for line in f.readlines():
            if "NAME=" in line[0:5]:
                name = line[6:-2]
            elif "VERSION_ID=" in line:
                version = line[12:-2]

            elif "VERSION_CODENAME=" in line:
                codename = line[17:-1]

            if name and version and codename:
                break

        computer["os_name"] = name
        computer["os_version"] = version
        computer["os_codename"] = codename

    # CPU
    with open("/proc/cpuinfo", "r") as f:
        core_count = 0
        model_name = ""
        model_id = ""
        vendor = ""
        family = ""
        for line in f.readlines():
            splitted = line.split(":")
            key = splitted[0].strip()
            value = splitted[1].strip()

            if key == "siblings":
                core_count = int(value)
            elif key == "model name":
                model_name = value
            elif key == "model":
                model_id = value
            elif key == "cpu family":
                family = value
            elif key == "vendor_id":
                if "NTEL" in value.upper():
                    vendor = "Intel"
                elif "AMD" in value.upper():
                    vendor = "AMD"
                else:
                    vendor = "Unknown"

            if core_count and model_name and family and vendor and model_id:
                break

        computer["cpu_name"] = model_name
        computer["cpu_model_id"] = model_id
        computer["cpu_vendor"] = vendor
        computer["cpu_family_id"] = family
        computer["cpu_cores"] = core_count

    # Is Live USB?
    computer["live_boot"] = is_live_boot()

    return computer


def is_live_boot():
    with open("/proc/cmdline", "r") as f:
        data = f.read()

        if "boot=live" in data or "/live/vmlinuz" in data:
            return True

    return False
