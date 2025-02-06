#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os, subprocess


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "mauna-about.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/mauna-about.mo"]))
    return mo

changelog = "debian/changelog"
version = "2.0.0"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = ""
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
    ("/usr/share/applications/",
     ["top.mauna.about.desktop"]),
    ("/usr/share/mauna/mauna-about/",
     ["mauna-about.svg",
      "maunaabout.png",
      "brazil.gif",
      "icon.svg"]),
    ("/usr/share/mauna/mauna-about/src",
     ["src/cli.py",
      "src/copy_to_desktop.sh",
      "src/dump_logs.sh",
      "src/dump_system_info.sh",
      "src/get_system_info.sh",
      "src/Main.py",
      "src/MainWindow.py",
      "src/utils.py",
      "src/__version__"]),
    ("/usr/share/mauna/mauna-about/ui",
     ["ui/MainWindow.glade"]),
    ("/usr/share/mauna/mauna-about/data",
     ["data/pci.ids",
      "data/servers.txt"]),
    ("/usr/share/polkit-1/actions",
     ["top.mauna.pkexec.mauna-about.policy"]),
    ("/usr/bin/",
     ["mauna-about"]),
    ("/usr/share/icons/hicolor/scalable/apps/",
     ["mauna-about.svg",
      "mauna-about-symbolic.svg"])
] + create_mo_files()

setup(
    name="mauna-about",
    version=version,
    packages=find_packages(),
    scripts=["mauna-about"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Mauna Linux Team",
    author_email="dev@maunalinux.top",
    description="Get info about your Mauna system.",
    license="GPLv3",
    keywords="about",
    url="https://maunalinux.top",
)
