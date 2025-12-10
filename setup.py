#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is template/test
#

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs(
                "{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True
            )
            mo_file = "{}/{}/LC_MESSAGES/{}".format(
                podir, po.split(".po")[0], "mauna-about.mo"
            )
            msgfmt_cmd = "msgfmt {} -o {}".format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(
                (
                    "/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                    ["po/" + po.split(".po")[0] + "/LC_MESSAGES/mauna-about.mo"],
                )
            )
    return mo


changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = "0.0.0"
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
    ("/usr/bin", ["mauna-about"]),
    ("/usr/share/applications", ["data/top.mauna.python-gtk.desktop"]),
    ("/usr/share/mauna/mauna-about/ui", ["ui/MainWindow.glade"]),
    (
        "/usr/share/mauna/mauna-about/src",
        [
            "src/Main.py",
            "src/MainWindow.py",
            "src/UserSettings.py",
            "src/Actions.py",
            "src/__version__",
        ],
    ),
    (
        "/usr/share/mauna/mauna-about/data",
        [
            "data/style.css",
            "data/top.mauna.python-gtk-autostart.desktop",
            "data/mauna-about.svg",
            "data/mauna-about-on-symbolic.svg",
            "data/mauna-about-off-symbolic.svg",
        ],
    ),
    (
        "/usr/share/icons/hicolor/scalable/apps/",
        [
            "data/assets/mauna-about.svg",
            "data/assets/mauna-about-symbolic.svg",
            "data/assets/mauna-hardware-info.svg",
            "data/assets/mauna-about-audio.svg",
            "data/assets/mauna-about-bluetooth.svg",
            "data/assets/mauna-about-camera.svg",
            "data/assets/mauna-about-computer.svg",
            "data/assets/mauna-about-desktop.svg",
            "data/assets/mauna-about-ethernet.svg",
            "data/assets/mauna-about-fingerprint.svg",
            "data/assets/mauna-about-graphics.svg",
            "data/assets/mauna-about-keyboard.svg",
            "data/assets/mauna-about-memory.svg",
            "data/assets/mauna-about-monitor.svg",
            "data/assets/mauna-about-mouse.svg",
            "data/assets/mauna-about-printer.svg",
            "data/assets/mauna-about-processor.svg",
            "data/assets/mauna-about-publicip.svg",
            "data/assets/mauna-about-storage.svg",
            "data/assets/mauna-about-touchpad.svg",
            "data/assets/mauna-about-wifi.svg",
            "data/assets/mauna-about-bios.svg",
            "data/assets/mauna-about-main.svg",
            "data/assets/mauna-about-network-card.svg"
        ],
    ),
] + create_mo_files()

setup(
    name="mauna-about",
    version=version,
    packages=find_packages(),
    scripts=["mauna-about"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Mehmet Zahid Berktas",
    author_email="mehmet.berktas@tubitak.gov.tr",
    description="Mauna About Application",
    license="GPLv3",
    keywords="mauna-about, mauna-hardware-info",
    url="https://github.com/mauna/mauna-about",
)
