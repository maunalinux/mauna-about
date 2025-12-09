import os
import subprocess
import socket
import platform

import gi
gi.require_versions({'Gdk': '3.0'})
from gi.repository import GObject, Gdk, GdkX11


operating_system_info = None


def is_wayland():
    return not isinstance(Gdk.Display.get_default(), GdkX11.X11Display)

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

    operating_system_info["desktop"] = "Unknown"
    operating_system_info["desktop_version"] = "Unknown"
    operating_system_info["display"] = "x11"
    if "XDG_CURRENT_DESKTOP" in os.environ:
        operating_system_info["desktop"] = os.environ["XDG_CURRENT_DESKTOP"]
        operating_system_info["desktop_version"] = get_desktop_version(os.environ["XDG_CURRENT_DESKTOP"])
    if is_wayland():
        operating_system_info["display"] = "wayland"

    return operating_system_info

def get_desktop_version(desktop):
    de_version_command = {"xfce": ["xfce4-session", "--version"],
                          "gnome": ["gnome-shell", "--version"],
                          "cinnamon": ["cinnamon", "--version"],
                          "mate": ["mate-about", "--version"],
                          "kde": ["plasmashell", "--version"],
                          "lxqt": ["lxqt-about", "--version"],
                          "sway": ["sway", "--version"],
                          "budgie": ["budgie-desktop", "--version"]}

    if desktop.lower() in de_version_command:
         return subprocess.run(
               de_version_command[desktop.lower()],
               shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
             ).stdout.decode().strip()
    return "Unknown"
