import socket
import platform

operating_system_info = None


def get_os_info():
    global operating_system_info
    if operating_system_info:
        return operating_system_info

    operating_system_info = {}

    hostname = socket.gethostname()
    operating_system_info["hostname"] = hostname.capitalize()

    os_info = platform.freedesktop_os_release()
    operating_system_info["os_pretty_name"] = os_info.get("PRETTY_NAME")
    operating_system_info["os_name"] = os_info.get("NAME")
    operating_system_info["os_version"] = os_info.get("VERSION")
    operating_system_info["os_codename"] = os_info.get("VERSION_CODENAME")
    operating_system_info["kernel"] = platform.release()
    operating_system_info["architecture"] = platform.machine()

    return operating_system_info
