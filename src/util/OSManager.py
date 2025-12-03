import socket
import platform


class OSManager:
    os_info = None

    def __init__(self):
        self.prepare_data()

    def prepare_data(self):
        self.os_info = {}
        hostname = socket.gethostname()
        self.os_info["hostname"] = hostname.capitalize()

        os_info = platform.freedesktop_os_release()
        self.os_info["os_pretty_name"] = os_info.get("PRETTY_NAME")
        self.os_info["os_name"] = os_info.get("NAME")
        self.os_info["os_version"] = os_info.get("VERSION")
        self.os_info["os_codename"] = os_info.get("VERSION_CODENAME")

        self.os_info["kernel"] = platform.release()
        self.os_info["architecture"] = platform.machine()

    def get_info(self):
        return self.os_info
