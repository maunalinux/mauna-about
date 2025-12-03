import os
from managers import HardwareDetector


def read_file(filepath):
    """Reads the first line of a file. Returns None if the file is not found."""
    try:
        with open(filepath) as f:
            return f.readline().strip()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    return None


def get_sys_bus_uevent():
    """
    Reads USB device information such as driver, vendor, product, and class ID
    from /sys/bus/usb/devices

    Returns:
        list: A list of dictionaries containing driver, vendor, product, and class_id
    """
    dev_path = "/sys/bus/usb/devices"
    infos = []

    if not os.path.exists(dev_path):
        return infos  # Return empty list if path doesn't exist

    for entry in os.listdir(dev_path):
        if ":" in entry:
            continue  # Skip interface subdirectories like 1-8:1.0
        if "usb" in entry:
            continue  # Skip interface subdirectories like usb1, usb2
        device_path = os.path.join(dev_path, entry)

        vendor_id = read_file(os.path.join(device_path, "idVendor"))
        product_id = read_file(os.path.join(device_path, "idProduct"))
        dev_class = read_file(os.path.join(device_path, "bDeviceClass"))
        dev_protocol = read_file(os.path.join(device_path, "bDeviceProtocol"))
        dev_subclass = read_file(os.path.join(device_path, "bDeviceSubClass"))
        busnum = read_file(os.path.join(device_path, "busnum"))
        devnum = read_file(os.path.join(device_path, "devnum"))

        product_file = os.path.join(device_path, "product")
        product = None
        if os.path.exists(product_file):
            product = read_file(product_file)

        # Construct the interface directory name (e.g., 1-8:1.0)
        iface_dir = f"{entry}:1.0"
        driver_link_path = os.path.join(device_path, iface_dir, "driver")
        modalias_id = read_file(os.path.join(device_path, iface_dir, "modalias"))

        driver = None
        if os.path.exists(driver_link_path):
            try:
                driver = os.readlink(driver_link_path).split("/")[-1]
            except OSError as e:
                print(f"Failed to read symlink: {driver_link_path} → {e}")

        # Create a fresh dictionary per device
        info = {
            "driver": driver,
            "vendor_id": vendor_id,
            "product_id": product_id,
            "modalias_id": modalias_id,
            "class_id": " ".join([dev_class, dev_protocol, dev_subclass]),
            "product": product,
            "busnum": busnum,
            "devnum": devnum,
        }

        infos.append(info)
        # print(info)  # Debug output

    return infos


def match_class_with_category(class_id):
    device_classes = {
        "e0 01 01": "bluetooth",
        "ef 01": "camera",
        "0e": "camera",
        "ff ff": "fingerprint",
        "e0 02": "wifi",
        "2c 06": "ethernet",
    }

    for key, value in device_classes.items():
        if class_id.startswith(key):
            return value
    return None


def match_driver_with_category(driver):
    device_classes = {
        "btusb": "bluetooth",
        "uvcvideo": "camera",
    }

    if driver in device_classes:
        return device_classes[driver]

    return None


def get_usb_devices():
    dev_info = get_sys_bus_uevent()

    data = {}
    for usb in dev_info:
        class_category = match_class_with_category(usb.get("class_id", ""))
        driver_category = match_driver_with_category(usb.get("driver", ""))

        if driver_category:
            category = driver_category
        elif class_category:
            category = class_category
        else:
            continue

        if category not in data:
            data[category] = []

        available_drivers = HardwareDetector.find_drivers(usb["modalias_id"])
        vendor, name = HardwareDetector.get_vendor_product_name(
            "usb", usb["vendor_id"], usb["product_id"]
        )

        vendor_upper = usb["vendor_id"].upper()
        product_upper = usb["product_id"].upper()

        if name is None or vendor is None:
            vendor_text = f"usb:v{vendor_upper}*\n ID_VENDOR_FROM_DATABASE="
            product_text = (
                f"usb:v{vendor_upper}p{product_upper}*\n ID_MODEL_FROM_DATABASE="
            )

            vendor, name = HardwareDetector.get_vendor_product_name_from_udev(
                "usb", vendor_text, product_text
            )

        if name is None:
            name = usb["product"]

        pci_id = f"{vendor_upper}:{product_upper}"

        busnum = f"{int(usb['busnum']):04}"
        devnum = f"{int(usb['devnum']):04}"
        bus_address = f"{busnum}:{devnum}"

        if not vendor:
            vendor = ""

        # Big corp renaming:
        if "INTEL" in vendor.upper():
            vendor = "Intel"

        device = {
            "name": name,
            "vendor": vendor,
            "driver": usb["driver"],
            "available_drivers": available_drivers,
            "bus": "usb",
            "pci_id": pci_id,
            "bus_address": bus_address,
            "error_logs": [],
        }

        for k in device.keys():
            if device[k] is None:
                device[k] = ""

        data[category].append(device)

    return data
