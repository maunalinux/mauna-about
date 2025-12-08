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
            "data/mauna-about.svg",
            "data/mauna-hardware-info.svg",
            "data/mauna-about-on-symbolic.svg",
            "data/mauna-about-off-symbolic.svg",
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
    author="Yusuf Düzgün",
    author_email="yusuf.duzgun@pardus.org.tr",
    description="Mauna Python GTK EXAMPLE",
    license="GPLv3",
    keywords="mauna-about, example, test",
    url="https://github.com/mauna/mauna-about",
)
