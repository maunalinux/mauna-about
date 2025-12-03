import socket
import platform

class MaunaInfoManager:
    mauna_info = None

    def __init__(self):
        self.prepare_data()

    def prepare_data(self):
        self.mauna_info = {}
        hostname = socket.gethostname()
        self.mauna_info["hostname"] = hostname.capitalize()

        os_info = platform.freedesktop_os_release()
        self.mauna_info["mauna"] = os_info.get("PRETTY_NAME")
        self.mauna_info["os_name"] = os_info.get("NAME")
        self.mauna_info["os_version"] = os_info.get("VERSION")
        self.mauna_info["os_codename"] = os_info.get("VERSION_CODENAME")

        self.mauna_info["kernel"] = platform.release()
        self.mauna_info["architecture"] = platform.machine()

    def get_info(self):
        return self.mauna_info
