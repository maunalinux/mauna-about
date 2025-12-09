import os
import gi
import requests
import json

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, Gdk

import locale
from locale import gettext as _

from util import OSManager, ComputerManager, HardwareDetector

# Translation Constants:
APPNAME = "mauna-about"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)

computerManager = None
pciManager = None
usbManager = None

HARDWARE_API_DOMAIN = "https://donanim.pardus.org.tr"
HARDWARE_API = f"{HARDWARE_API_DOMAIN}/api/v1"


class MainWindow:
    is_hardware_details_visible = False

    def __init__(self, application):
        self.computerManager = None

        # Gtk Builder
        self.builder = Gtk.Builder()

        self.load_css(os.path.dirname(os.path.abspath(__file__)) + "/../css/about.css")

        # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        # Import UI file:
        self.builder.add_from_file(
            os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
        )
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

        task = Gio.Task.new(callback=self.on_read_hardware_info_finish)
        task.run_in_thread(self.read_hardware_info)

        # Show Screen:
        self.window.show_all()

        # buttons will be visible after hardware info collected
        self.ui_hardware_info_button.hide()
        self.ui_display_report_button.hide()

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
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def define_components(self):
        def UI(str):
            return self.builder.get_object(str)

        self.ui_main_window = UI("ui_main_window")
        self.ui_main_stack = UI("ui_main_stack")
        self.ui_info_stack = UI("ui_info_stack")
        self.ui_hardware_info_button = UI("ui_hardware_info_button")
        self.ui_display_report_button = UI("ui_display_report_button")
        self.ui_copy_report_btn = UI("ui_copy_report_btn")
        self.ui_submit_report_btn = UI("ui_submit_report_btn")

        self.ui_about_dialog = UI("ui_about_dialog")
        self.ui_popover_menu = UI("ui_popover_menu")
        self.ui_notification_popover = UI("ui_notification_popover")

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

        self.ui_hardware_list_computer_revealer = UI("ui_hardware_list_computer_revealer")
        self.ui_hardware_list_computer_revealer_image = UI("ui_hardware_list_computer_revealer_image")
        self.ui_hardware_list_os_revealer = UI("ui_hardware_list_os_revealer")
        self.ui_hardware_list_os_revealer_image = UI("ui_hardware_list_os_revealer_image")
        self.ui_hardware_list_processor_revealer = UI("ui_hardware_list_processor_revealer")
        self.ui_hardware_list_processor_revealer_image = UI("ui_hardware_list_processor_revealer_image")
        self.ui_hardware_list_memory_revealer = UI("ui_hardware_list_memory_revealer")
        self.ui_hardware_list_memory_revealer_image = UI("ui_hardware_list_memory_revealer_image")
        self.ui_hardware_list_storage_revealer = UI("ui_hardware_list_storage_revealer")
        self.ui_hardware_list_storage_revealer_image = UI("ui_hardware_list_storage_revealer_image")
        self.ui_hardware_list_graphics_revealer = UI("ui_hardware_list_graphics_revealer")
        self.ui_hardware_list_graphics_revealer_image = UI("ui_hardware_list_graphics_revealer_image")
        self.ui_hardware_list_display_revealer = UI("ui_hardware_list_display_revealer")
        self.ui_hardware_list_display_revealer_image = UI("ui_hardware_list_display_revealer_image")
        self.ui_hardware_list_ethernet_revealer = UI("ui_hardware_list_ethernet_revealer")
        self.ui_hardware_list_ethernet_revealer_image = UI("ui_hardware_list_ethernet_revealer_image")
        self.ui_hardware_list_wifi_revealer = UI("ui_hardware_list_wifi_revealer")
        self.ui_hardware_list_wifi_revealer_image = UI("ui_hardware_list_wifi_revealer_image")
        self.ui_hardware_list_bluetooth_revealer = UI("ui_hardware_list_bluetooth_revealer")
        self.ui_hardware_list_bluetooth_revealer_image = UI("ui_hardware_list_bluetooth_revealer_image")
        self.ui_hardware_list_audio_revealer = UI("ui_hardware_list_audio_revealer")
        self.ui_hardware_list_audio_revealer_image = UI("ui_hardware_list_audio_revealer_image")
        self.ui_hardware_list_camera_revealer = UI("ui_hardware_list_camera_revealer")
        self.ui_hardware_list_camera_revealer_image = UI("ui_hardware_list_camera_revealer_image")
        self.ui_hardware_list_keyboard_revealer = UI("ui_hardware_list_keyboard_revealer")
        self.ui_hardware_list_keyboard_revealer_image = UI("ui_hardware_list_keyboard_revealer_image")
        self.ui_hardware_list_mouse_revealer = UI("ui_hardware_list_mouse_revealer")
        self.ui_hardware_list_mouse_revealer_image = UI("ui_hardware_list_mouse_revealer_image")
        self.ui_hardware_list_fingerprint_revealer = UI("ui_hardware_list_fingerprint_revealer")
        self.ui_hardware_list_fingerprint_revealer_image = UI("ui_hardware_list_fingerprint_revealer_image")
        self.ui_hardware_list_printer_revealer = UI("ui_hardware_list_printer_revealer")
        self.ui_hardware_list_printer_revealer_image = UI("ui_hardware_list_printer_revealer_image")

        self.ui_detail_computer_vendor_label = UI("ui_detail_computer_vendor_label")
        self.ui_detail_computer_model_label = UI("ui_detail_computer_model_label")
        self.ui_detail_computer_family_label = UI("ui_detail_computer_family_label")
        self.ui_detail_os_name_label = UI("ui_detail_os_name_label")
        self.ui_detail_os_codename_label = UI("ui_detail_os_codename_label")
        self.ui_detail_os_version_label = UI("ui_detail_os_version_label")
        self.ui_detail_os_kernel_label = UI("ui_detail_os_kernel_label")
        self.ui_detail_os_desktop_label = UI("ui_detail_os_desktop_label")
        self.ui_detail_processor_vendor_label = UI("ui_detail_processor_vendor_label")
        self.ui_detail_processor_model_label = UI("ui_detail_processor_model_label")
        self.ui_detail_processor_core_label = UI("ui_detail_processor_core_label")

        self.memory_container = UI("ui_hardware_list_memory_container")

        # Submit
        self.ui_submit_window = UI("ui_submit_window")
        # prevent destroying the window on close clicked
        self.ui_submit_window.connect("delete-event", lambda w, e: w.hide() or True)
        self.ui_submit_lbl = UI("ui_submit_lbl")

    def define_variables(self):
        return

    def control_args(self):
        if "hardware" in self.application.args.keys():
            self.is_hardware_details_visible = True

        self.ui_main_window.present()

    def read_mauna_info(self):
        mauna_info = OSManager.get_os_info()
        self.ui_hostname_label.set_text(mauna_info["hostname"])
        self.ui_mauna_label.set_text(mauna_info["os_pretty_name"])
        self.ui_kernel_label.set_text(mauna_info["kernel"])
        return

    def read_hardware_info(self, task, source_object, task_data, cancellable):
        # computer info
        self.computerManager = ComputerManager.ComputerManager()

        # Computer
        computer_info = self.computerManager.get_computer_info()
        self.ui_computer_label.set_text(computer_info["model"])
        self.ui_detail_computer_vendor_label.set_text(computer_info["vendor"])
        self.ui_detail_computer_model_label.set_text(computer_info["model"])
        self.ui_detail_computer_family_label.set_text(computer_info["family"])

        # OS
        mauna_info = OSManager.get_os_info()
        self.ui_detail_os_name_label.set_text(mauna_info["os_name"])
        self.ui_detail_os_codename_label.set_text(mauna_info["os_codename"])
        self.ui_detail_os_version_label.set_text(mauna_info["os_version"])
        self.ui_detail_os_kernel_label.set_text(mauna_info["kernel"])
        #self.ui_detail_os_desktop_label.set_text(mauna_info["wayland"])

        # CPU
        processor_info = self.computerManager.get_processor_info()
        self.ui_processor_label.set_text(processor_info["name"])
        self.ui_detail_processor_vendor_label.set_text(processor_info["vendor"])
        self.ui_detail_processor_model_label.set_text(processor_info["name"])
        self.ui_detail_processor_core_label.set_text(f"{processor_info["core_count"]} / {processor_info['thread_count']}")

        # Memory
        memory_summary = self.computerManager.get_memory_summary()
        self.ui_memory_label.set_text(memory_summary)

        memory_info = self.computerManager.get_memory_info()
        # for _index, memory in enumerate(memory_info):
        #     MEMORY_ROW_TEMPLATE_ID = "ui_hardware_list_memory_container_row"
        #     row_builder = Gtk.Builder()
        #     row_builder.add_from_string(self.memory_template_row_xml)
        #     new_row = row_builder.get_objects()[0]
        #     memory_model = f"{memory['size']}GB {memory['type']} {memory['factor']}"
        #     row_builder.get_object("ui_detail_memory_slot_label").set_text(f"#{_index + 1}")
        #     row_builder.get_object("ui_detail_memory_vendor_label").set_text(memory["vendor"])
        #     row_builder.get_object("ui_detail_memory_model_label").set_text(memory_model)
        #     self.memory_container.pack_start(new_row, False, True, 0)
        #     new_row.show_all()

        # Lazy Init PCI & USB devices information singleton
        hardware_info = HardwareDetector.get_hardware_info()

        try:
            graphics_summary = ""
            for device in hardware_info["graphics"]:
                graphics_summary += f"{device["vendor"]} {device["name"]}\n"
            self.ui_graphics_label.set_text(graphics_summary)
        except:
            pass

        try:
            ethernet_summary = ""
            for device in hardware_info["ethernet"]:
                ethernet_summary += f"{device["name"]}\n"
            self.ui_ethernet_label.set_text(ethernet_summary)
        except:
            pass

        try:
            wifi_summary = ""
            for device in hardware_info["wifi"]:
                wifi_summary += f"{device["name"]}\n"
            self.ui_wifi_label.set_text(wifi_summary)
        except:
            pass

        try:
            bluetooth_summary = ""
            for device in hardware_info["bluetooth"]:
                bluetooth_summary += f"{device["vendor"]} {device["name"]}\n"
            self.ui_bluetooth_label.set_text(bluetooth_summary)
        except:
            pass

        try:
            audio_summary = ""
            for device in hardware_info["audio"]:
                audio_summary += f"{device["vendor"]} {device["name"]}\n"
            self.ui_audio_label.set_text(audio_summary)
        except:
            pass

        task.return_boolean(True)

    # Send Hardware Report Tasks
    def send_hardware_data(self, task, source_object, task_data, cancellable):
        try:
            all_info = self.computerManager.get_all_device_info()
            response = requests.post(HARDWARE_API, json=all_info, timeout=3)

            task.return_value(response)
        except requests.Timeout as r:
            print("timeout!")
            task.return_value(r)
        except Exception as e:
            print("exception:", e)
            task.return_value(e)

    def send_hardware_data_completed(self, source, task):
        task_finished, data = task.propagate_value()

        if task_finished:
            if isinstance(data, requests.Response):
                if str(data.status_code)[0] == "2":
                    report_id = data.json()["data"]["link"]
                    url = f"{HARDWARE_API_DOMAIN}{report_id}"
                    markup = f'<a href="{url}">{report_id}</a>'

                    self.show_info_dialog(
                        title=_("Thank you for your contribution."),
                        subtitle=_("You can find your submission here:")
                        + "\n"
                        + markup,
                    )

                    self.btn_last_submission.set_uri(url)
                    self.btn_last_submission.set_visible(True)

                    self.gsettings.set_string("latest-submission-id", report_id)
                    self.is_hardware_data_submitted = True
                else:
                    message = data.json()["message"]

                    print("Response:", json.dumps(data.json(), indent=2))
                    print(data.status_code)

                    self.show_info_dialog(
                        title=_("An error occured while sending the data."),
                        subtitle=_("Returned message from the server:")
                        + f"\n{data.status_code}\n{message}",
                    )

            else:
                self.show_info_dialog(
                    title=_("Connection Failed"),
                    subtitle=_(
                        "If you are connected to the internet, then our servers have some problem."
                    ),
                )

    def show_info_dialog(self, title, subtitle, use_markup=False):
        dialog = Gtk.MessageDialog(
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_use_markup=use_markup,
            secondary_text=subtitle,
        )
        dialog.run()
        dialog.hide()

    def on_read_hardware_info_finish(self, source, task):
        self.ui_hardware_info_button.show()
        self.ui_display_report_button.show()
        self.toggle_hardware_details_pane()

    def on_menu_about_button_clicked(self, btn):
        self.ui_popover_menu.popdown()
        self.ui_about_dialog.run()
        self.ui_about_dialog.hide()

    def on_hardware_info_button_clicked(self, btn):
        self.is_hardware_details_visible = not self.is_hardware_details_visible
        self.toggle_hardware_details_pane()

    def on_display_report_button_clicked(self, btn):
        device_list = self.computerManager.get_all_device_info()
        print(json.dumps(device_list, indent=2))
        self.ui_submit_lbl.set_text(json.dumps(device_list, indent=2))
        self.ui_submit_window.show_all()

    def on_copy_report_btn_clicked(self, btn):
        clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        clipboard.set_text(self.ui_submit_lbl.get_text(), -1)
        self.ui_notification_popover.popup()

    def on_submit_report_btn_clicked(self, btn):
        task = Gio.Task.new(callback=self.send_hardware_data_completed)
        task.run_in_thread(self.send_hardware_data)

    def toggle_hardware_details_pane(self):
        if self.is_hardware_details_visible:
            self.ui_info_stack.set_visible_child_name("hardware_details")
            self.ui_hardware_info_button.set_label(_("Show Summary"))
        else:
            self.ui_info_stack.set_visible_child_name("hardware_grid")
            self.ui_hardware_info_button.set_label(_("Show Hardware Details"))

    def on_ui_hardware_list_computer_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_computer_revealer.get_reveal_child()
        self.ui_hardware_list_computer_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_computer_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_os_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_os_revealer.get_reveal_child()
        self.ui_hardware_list_os_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_os_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_processor_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_processor_revealer.get_reveal_child()
        self.ui_hardware_list_processor_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_processor_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_memory_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_memory_revealer.get_reveal_child()
        self.ui_hardware_list_memory_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_memory_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_storage_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_storage_revealer.get_reveal_child()
        self.ui_hardware_list_storage_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_storage_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_graphics_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_graphics_revealer.get_reveal_child()
        self.ui_hardware_list_graphics_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_graphics_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_display_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_display_revealer.get_reveal_child()
        self.ui_hardware_list_display_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_display_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_ethernet_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_ethernet_revealer.get_reveal_child()
        self.ui_hardware_list_ethernet_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_ethernet_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_wifi_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_wifi_revealer.get_reveal_child()
        self.ui_hardware_list_wifi_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_wifi_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_bluetooth_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_bluetooth_revealer.get_reveal_child()
        self.ui_hardware_list_bluetooth_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_bluetooth_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_audio_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_audio_revealer.get_reveal_child()
        self.ui_hardware_list_audio_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_audio_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_camera_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_camera_revealer.get_reveal_child()
        self.ui_hardware_list_camera_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_camera_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_keyboard_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_keyboard_revealer.get_reveal_child()
        self.ui_hardware_list_keyboard_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_keyboard_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_mouse_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_mouse_revealer.get_reveal_child()
        self.ui_hardware_list_mouse_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_mouse_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_fingerprint_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_fingerprint_revealer.get_reveal_child()
        self.ui_hardware_list_fingerprint_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_fingerprint_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def on_ui_hardware_list_printer_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_printer_revealer.get_reveal_child()
        self.ui_hardware_list_printer_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_printer_revealer_image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)
