import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

import locale
from locale import gettext as _

from util import MaunaInfoManager, ComputerManager

import threading

# Translation Constants:
APPNAME = "mauna-about"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)

maunaInfoManager = MaunaInfoManager.MaunaInfoManager()
computerManager = None
pciManager = None
usbManager = None

class MainWindow:
    is_hardware_loaded = False
    is_hardware_details_visible = False

    def __init__(self, application):
        self.computerManager = None
        self.Application = application

        # Gtk Builder
        self.builder = Gtk.Builder()

        self.load_css(os.path.dirname(os.path.abspath(__file__)) + "/../css/about.css")

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Import UI file:
        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Window
        self.window = self.builder.get_object("ui_main_window")
        self.window.set_application(application)

        # Set application:
        self.application = application

        # Global Definitions:
        self.define_components()
        self.define_variables()

        self.read_mauna_info()

        self.ui_main_window.set_title(_("About Mauna"))

        thread = threading.Thread(target=self.read_hardware_info)
        thread.daemon = True
        thread.start()

        # Show Screen:
        self.window.show_all()

    @staticmethod
    def load_css(css_file_path):
        css_provider = Gtk.CssProvider()

        try:
            css_provider.load_from_path(css_file_path)
        except GLib.Error as e:
            print(f"Error loading CSS file '{css_file_path}': {e}")
            return

        screen = Gdk.Screen.get_default()

        Gtk.StyleContext.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def define_components(self):
        def UI(str):
            return self.builder.get_object(str)

        self.ui_main_window = UI("ui_main_window")
        self.ui_main_stack = UI("ui_main_stack")
        self.ui_info_stack = UI("ui_info_stack")
        self.ui_hardware_info_button = UI("ui_hardware_info_button")
        self.ui_display_report_button = UI("ui_display_report_button")
        self.ui_send_report_button = UI("ui_send_report_button")
        self.ui_copy_report_link_button = UI("ui_copy_report_link_button")
        self.ui_close_hardware_info_button = UI("ui_close_hardware_info_button")

        self.ui_about_dialog = UI("ui_about_dialog")
        self.ui_popover_menu = UI("ui_popover_menu")

        self.ui_hostname_label = UI("ui_hostname_label")
        self.ui_mauna_label = UI("ui_mauna_label")
        self.ui_kernel_label = UI("ui_kernel_label")
        self.ui_computer_label = UI("ui_computer_label")
        self.ui_processor_label = UI("ui_processor_label")
        self.ui_memory_label = UI("ui_memory_label")
        self.ui_storage_label = UI("ui_storage_label")
        self.ui_graphics_label = UI("ui_graphics_label")
        self.ui_desktop_label = UI("ui_desktop_label")
        self.ui_wifi_label = UI("ui_wifi_label")
        self.ui_ethernet_label = UI("ui_ethernet_label")
        self.ui_bluetooth_label = UI("ui_bluetooth_label")
        self.ui_audio_label = UI("ui_audio_label")
        self.ui_private_ip_label = UI("ui_private_ip_label")
        self.ui_public_ip_label = UI("ui_public_ip_label")

    def define_variables(self):
        return

    def control_args(self):
        if "hardware" in self.Application.args.keys():
            self.is_hardware_details_visible = True

        self.ui_main_window.present()

    def read_mauna_info(self):
        mauna_info = maunaInfoManager.get_info()
        self.ui_hostname_label.set_text(mauna_info["hostname"])
        self.ui_mauna_label.set_text(mauna_info["mauna"])
        self.ui_kernel_label.set_text(mauna_info["kernel"])
        return

    def read_hardware_info(self):
        # computer info
        self.computerManager = ComputerManager.ComputerManager()
        computer_info = self.computerManager.get_computer_info()
        self.ui_computer_label.set_text(computer_info["model"])
        self.ui_processor_label.set_text(computer_info["cpu_name"])

        memory_summary = self.computerManager.get_memory_summary()
        self.ui_memory_label.set_text(memory_summary)

        # pci info


        # usb info
        # self.usbManager = UsbManager.UsbManager()
        self.is_hardware_loaded = True
        self.toggle_hardware_details_pane()

        return

    def on_menu_about_button_clicked(self, btn):
        self.ui_popover_menu.popdown()
        self.ui_about_dialog.run()
        self.ui_about_dialog.hide()

    def on_hardware_info_button_clicked(self, btn):
        #GLib.idle_add(self.ui_main_stack.set_visible_child_name, "page_hardware_info")
        GLib.idle_add(self.ui_info_stack.set_visible_child_name, "hardware_details")

    def on_close_hardware_info_button(self, btn):
        GLib.idle_add(self.ui_main_stack.set_visible_child_name, "page_info_box")

    def toggle_hardware_details_pane(self):
        if self.is_hardware_details_visible:
            GLib.idle_add(self.ui_info_stack.set_visible_child_name, "hardware_details")
        else:
            GLib.idle_add(self.ui_info_stack.set_visible_child_name, "hardware_grid")
