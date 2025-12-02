import os, subprocess, time
import queue
import platform

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk, GdkPixbuf

import requests

import locale
from locale import gettext as _

import socket
import fcntl
import struct
import threading
import utils

# Translation Constants:
APPNAME = "mauna-about"
TRANSLATIONS_PATH = "/usr/share/locale"
# SYSTEM_LANGUAGE = os.environ.get("LANG")

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)
# locale.setlocale(locale.LC_ALL, SYSTEM_LANGUAGE)


class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()

        # Translate things on glade:
        # self.builder.set_translation_domain(APPNAME)

        # Import UI file:
        self.builder.add_from_file(
            os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
        )
        self.builder.connect_signals(self)
        # Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect("destroy", self.onDestroy)
        self.defineComponents()

        # Show Screen:
        self.window.show_all()

        # self.stack_main.set_visible_child_name("loading")

        self.addTurkishFlag()
        self.add_gpus_to_ui()

        thread2 = threading.Thread(target=self.add_ip_to_ui)
        thread2.daemon = True
        thread2.start()


        self.readSystemInfo()

        # Set application:
        self.application = application


    # Window methods:
    def onDestroy(self, action):
        self.window.get_application().quit()

    def defineComponents(self):
        self.dialog_report_exported = self.builder.get_object("dialog_report_exported")
        self.dialog_gathering_logs = self.builder.get_object("dialog_gathering_logs")

        self.lbl_distro = self.builder.get_object("lbl_distro")
        self.lbl_distro_version = self.builder.get_object("lbl_distro_version")
        self.lbl_distro_codename = self.builder.get_object("lbl_distro_codename")

        self.lbl_user_host = self.builder.get_object("lbl_user_host")
        self.lbl_hardware = self.builder.get_object("lbl_hardware")
        self.lbl_kernel = self.builder.get_object("lbl_kernel")
        self.lbl_desktop = self.builder.get_object("lbl_desktop")
        self.lbl_cpu = self.builder.get_object("lbl_cpu")
        self.lbl_gpu = self.builder.get_object("lbl_gpu")
        self.lbl_title_gpu = self.builder.get_object("lbl_title_gpu")
        self.lbl_ram = self.builder.get_object("lbl_ram")
        self.lbl_ip_public = self.builder.get_object("lbl_ip_public")
        self.lbl_ip_local = self.builder.get_object("lbl_ip_local")

        self.img_llvm = self.builder.get_object("img_llvm")
        self.img_oem = self.builder.get_object("img_oem")

        self.img_publicip = self.builder.get_object("img_publicip")

        self.box_extra_gpu = self.builder.get_object("box_extra_gpu")

        self.popover_menu = self.builder.get_object("popover_menu")

        self.dialog_about = self.builder.get_object("dialog_about")
        self.dialog_about.set_program_name(_("Mauna About"))
        if self.dialog_about.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Mauna About"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name("pardus-about", Gtk.IconSize.LARGE_TOOLBAR)
            )
            about_headerbar.show_all()
            self.dialog_about.set_titlebar(about_headerbar)        

        self.brazil = self.builder.get_object("brazil")
        self.img_brazil = self.builder.get_object("img_brazil")

        self.img_background = self.builder.get_object("img_background")
        self.img_distro = self.builder.get_object("img_distro")

        self.lbl_distro_codename.grab_focus()

        self.public_ip = "0.0.0.0"
        self.urls = queue.Queue()
        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(
                os.path.dirname(os.path.abspath(__file__)) + "/__version__"
            ).readline()
            self.dialog_about.set_version(version)
        except:
            pass

    def addTurkishFlag(self):
        self.click_count = 0
        self.last_click_timestamp = 0
        
        pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(
            os.path.dirname(os.path.abspath(__file__)) + "/../brazil.gif"
        )

        def waving_flag(it):
            # it is iterator
            self.img_brazil.props.pixbuf = it.get_pixbuf()
            it.advance()

            GLib.timeout_add(it.get_delay_time(), waving_flag, it)

        GLib.timeout_add(0, waving_flag, pixbuf.get_iter())

    def readSystemInfo(self):
        output = subprocess.check_output(
            [os.path.dirname(os.path.abspath(__file__)) + "/get_system_info.sh"]
        ).decode("utf-8")
        lines = output.splitlines()

        self.lbl_distro.set_label(lines[0])

        def try_load_icon(icon_name):
            try:
                return Gtk.IconTheme.get_default().load_icon(
                    icon_name, 120, Gtk.IconLookupFlags(16)
                )
            except Exception as e:
                return None

        if lines[0].lower() != "pardus":
            dist_icon = "emblem-{}".format(lines[0].lower())
            with open("/etc/os-release", "r") as f:
                for fline in f.read().split("\n"):
                    if fline.startswith("LOGO="):
                        dist_icon = fline[5:]
                        break
            for name in [dist_icon, lines[0].lower(), "distributor-logo", "distro", "image-missing"]:
                pixbuf = try_load_icon(name)
                if pixbuf is not None:
                    self.img_distro.set_from_pixbuf(pixbuf)
                    break

        self.lbl_distro_version.set_label(lines[1])
        if lines[2] == "mauna":
            lines[2] = "Sirius"
            self.img_background.set_from_file(
                os.path.dirname(os.path.abspath(__file__)) + "/../maunaabout.png"
            )
        elif lines[2] == "polaris":
            lines[2] = "Polaris"
        self.lbl_distro_codename.set_label(lines[2])

        self.lbl_user_host.set_label(lines[3])
        kernel, release = utils.get_kernel()
        self.lbl_kernel.set_label(f"{kernel} {release}")

        hardware = utils.get_hardware_name()
        self.lbl_hardware.set_label(f"{hardware}")

        oem_available = os.path.isfile("/sys/firmware/acpi/tables/MSDM")
        self.img_oem.set_visible(oem_available)

        desktop_environment, desktop_environment_version = (
            utils.get_desktop_environment()
        )
        desktop_protocol = ""
        disp_name = str(type(Gdk.Display.get_default()))
        if "Wayland" in disp_name:
            desktop_protocol = "(Wayland)"
        elif "X11" in disp_name:
            desktop_protocol = "(X11)"

        self.lbl_desktop.set_label(
            f"{desktop_environment} {desktop_environment_version} {desktop_protocol}"
        )
        # if lines[7] == "0":
        #     self.lbl_cpu.set_label(lines[6])
        # else:
        #     ghz = "{:.2f}".format(float(lines[7])/1000000)
        #     self.lbl_cpu.set_label(lines[6] + " (" + ghz  + "GHz)")
        cpu, cores = utils.get_cpu()
        self.lbl_cpu.set_label("{} x{}".format(cpu, cores))

        total_ram = utils.get_ram_size()
        self.lbl_ram.set_label(f"{total_ram} GB")

    def add_gpus_to_ui(self):
        gpus = utils.get_gpu()
        if len(gpus) <= 0:
            return
        self.lbl_gpu.set_markup(
            "{} {} ({})".format(
                gpus[0]["vendor_short"], gpus[0]["device"], gpus[0]["driver"]
            )
        )
        try:
            if "llvmpipe" in gpus[0]["driver"].lower():
                llvm = True
            else:
                llvm = False
        except Exception as e:
            print("llvmpipe detect err: {}".format(e))
            llvm = False

        self.lbl_gpu.set_markup(
            "{} {} ({})".format(
                gpus[0]["vendor_short"], gpus[0]["device"], gpus[0]["driver"]
            )
        )

        self.img_llvm.set_visible(llvm)
        if len(gpus) > 1:
            self.lbl_title_gpu.set_markup("<b>GPU 1:</b>")
            self.box_extra_gpu.set_visible(True)
            count = 2
            for index, gpu in enumerate(gpus[1:]):
                box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
                gputitle = Gtk.Label.new()
                gputitle.set_selectable(True)
                gputitle.set_markup("<b>GPU {}:</b>".format(count))
                count += 1
                gpulabel = Gtk.Label.new()
                gpulabel.set_line_wrap(True)
                gpulabel.set_line_wrap_mode(Gtk.WrapMode.WORD)
                gpulabel.set_max_width_chars(55)
                gpulabel.set_selectable(True)
                gpulabel.set_markup(
                    "{} {} ({})".format(
                        gpu["vendor_short"], gpu["device"], gpu["driver"]
                    )
                )
                box.pack_start(gputitle, False, True, 0)
                box.pack_start(gpulabel, False, True, 0)

                self.box_extra_gpu.pack_start(box, False, True, 0)

            # self.box_extra_gpu.show_all()
            self.box_extra_gpu.show_all()
        else:
            self.box_extra_gpu.set_visible(False)

    def add_ip_to_ui(self):
        """async function"""
        local, public = self.get_ips()
        self.lbl_ip_public.set_text("{}".format(len(public.strip()) * "*"))
        lan = ""
        for lip in local:
            if lip[1] != "lo":
                lan += "{} ({})\n".format(lip[0], lip[1])
        lan = lan.rstrip("\n")
        GLib.idle_add(self.lbl_ip_local.set_markup, "{}".format(lan))


    def get_ip(self):
        servers = (
            open(
                os.path.dirname(os.path.abspath(__file__)) + "/../data/servers.txt", "r"
            )
            .read()
            .split("\n")
        )
        for server in servers:
            r = requests.get(server)
            if r.status_code == 200 and self.is_valid_ip(r.text):
                self.public_ip = r.text
                break
        return self.public_ip


    def is_valid_ip(self, address):
        parts = address.split(".")
        if len(parts) != 4:
            return False

        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True


    def get_ips(self):
        return utils.get_local_ip(), self.get_ip()

    # Signals:
    def on_menu_aboutapp_clicked(self, button):
        self.popover_menu.popdown()
        self.dialog_about.run()
        self.dialog_about.hide()

    def on_menu_btn_export_clicked(self, btn):
        self.popover_menu.popdown()
        self.dialog_gathering_logs.show_all()
        currentPath = os.path.dirname(os.path.abspath(__file__))

        self.finishedProcesses = 0

        def onFinished(source, condition):
            self.dialog_gathering_logs.hide()
            self.dialog_report_exported.run()
            self.dialog_report_exported.hide()

        def onLogsDumped(source, condition):
            if condition != 0:
                self.dialog_gathering_logs.hide()
                return
            pid3, _, _, _ = GLib.spawn_async(
                [currentPath + "/copy_to_desktop.sh"],
                flags=GLib.SPAWN_LEAVE_DESCRIPTORS_OPEN | GLib.SPAWN_DO_NOT_REAP_CHILD,
            )
            GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid3, onFinished)

        def onSystemInfoDumped(source, condition):
            pid2, _, _, _ = GLib.spawn_async(
                ["pkexec", currentPath + "/dump_logs.sh"],
                flags=GLib.SPAWN_SEARCH_PATH
                | GLib.SPAWN_LEAVE_DESCRIPTORS_OPEN
                | GLib.SPAWN_DO_NOT_REAP_CHILD,
            )
            GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid2, onLogsDumped)

        pid1, _, _, _ = GLib.spawn_async(
            [currentPath + "/dump_system_info.sh"],
            flags=GLib.SPAWN_LEAVE_DESCRIPTORS_OPEN | GLib.SPAWN_DO_NOT_REAP_CHILD,
        )
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid1, onSystemInfoDumped)

    def on_btn_mauna_logo_button_press_event(self, btn, event):
        timestamp = lambda: int(round(time.time() * 1000))  # milliseconds

        if event.type == Gdk.EventType._2BUTTON_PRESS:
            if timestamp() - self.last_click_timestamp < 800:
                self.click_count += 1
            else:
                self.click_count = 1

            self.last_click_timestamp = timestamp()

        if self.click_count >= 2:
            self.click_count = 0

            self.brazil.popup()

    def on_event_publicip_button_press_event(self, widget, event):
        if self.img_publicip.get_icon_name().icon_name == "view-conceal-symbolic":
            self.img_publicip.set_from_icon_name(
                "view-reveal-symbolic", Gtk.IconSize.BUTTON
            )
            self.lbl_ip_public.set_text("{}".format(len(self.public_ip) * "*"))
        else:
            self.img_publicip.set_from_icon_name(
                "view-conceal-symbolic", Gtk.IconSize.BUTTON
            )
            self.lbl_ip_public.set_text(self.public_ip)
