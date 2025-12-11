import os
import gi
import requests
import json

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk, Gdk

import locale
from locale import gettext as _

from util import OSManager, ComputerManager, HardwareDetector, network

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

        self.control_args()

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

        self.ui_distro_id_label = UI("ui_distro_id_label")
        self.ui_distro_version_label = UI("ui_distro_version_label")
        self.ui_distro_codename_label = UI("ui_distro_codename_label")
        self.ui_username_label = UI("ui_username_label")
        self.ui_hostname_label = UI("ui_hostname_label")
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

        self.ui_hardware_list_computer_revealer = UI(
            "ui_hardware_list_computer_revealer"
        )
        self.ui_hardware_list_computer_revealer_image = UI(
            "ui_hardware_list_computer_revealer_image"
        )
        self.ui_hardware_list_os_revealer = UI("ui_hardware_list_os_revealer")
        self.ui_hardware_list_os_revealer_image = UI(
            "ui_hardware_list_os_revealer_image"
        )
        self.ui_hardware_list_processor_revealer = UI(
            "ui_hardware_list_processor_revealer"
        )
        self.ui_hardware_list_processor_revealer_image = UI(
            "ui_hardware_list_processor_revealer_image"
        )
        self.ui_hardware_list_memory_revealer = UI("ui_hardware_list_memory_revealer")
        self.ui_hardware_list_memory_revealer_image = UI(
            "ui_hardware_list_memory_revealer_image"
        )
        self.ui_hardware_list_storage_revealer = UI("ui_hardware_list_storage_revealer")
        self.ui_hardware_list_storage_revealer_image = UI(
            "ui_hardware_list_storage_revealer_image"
        )
        self.ui_hardware_list_graphics_revealer = UI(
            "ui_hardware_list_graphics_revealer"
        )
        self.ui_hardware_list_graphics_revealer_image = UI(
            "ui_hardware_list_graphics_revealer_image"
        )
        self.ui_hardware_list_display_revealer = UI("ui_hardware_list_display_revealer")
        self.ui_hardware_list_display_revealer_image = UI(
            "ui_hardware_list_display_revealer_image"
        )
        self.ui_hardware_list_ethernet_revealer = UI(
            "ui_hardware_list_ethernet_revealer"
        )
        self.ui_hardware_list_ethernet_revealer_image = UI(
            "ui_hardware_list_ethernet_revealer_image"
        )
        self.ui_hardware_list_wifi_revealer = UI("ui_hardware_list_wifi_revealer")
        self.ui_hardware_list_wifi_revealer_image = UI(
            "ui_hardware_list_wifi_revealer_image"
        )
        self.ui_hardware_list_bluetooth_revealer = UI(
            "ui_hardware_list_bluetooth_revealer"
        )
        self.ui_hardware_list_bluetooth_revealer_image = UI(
            "ui_hardware_list_bluetooth_revealer_image"
        )
        self.ui_hardware_list_audio_revealer = UI("ui_hardware_list_audio_revealer")
        self.ui_hardware_list_audio_revealer_image = UI(
            "ui_hardware_list_audio_revealer_image"
        )
        self.ui_hardware_list_camera_revealer = UI("ui_hardware_list_camera_revealer")
        self.ui_hardware_list_camera_revealer_image = UI(
            "ui_hardware_list_camera_revealer_image"
        )
        self.ui_hardware_list_keyboard_revealer = UI(
            "ui_hardware_list_keyboard_revealer"
        )
        self.ui_hardware_list_keyboard_revealer_image = UI(
            "ui_hardware_list_keyboard_revealer_image"
        )
        self.ui_hardware_list_mouse_revealer = UI("ui_hardware_list_mouse_revealer")
        self.ui_hardware_list_mouse_revealer_image = UI(
            "ui_hardware_list_mouse_revealer_image"
        )
        self.ui_hardware_list_fingerprint_revealer = UI(
            "ui_hardware_list_fingerprint_revealer"
        )
        self.ui_hardware_list_fingerprint_revealer_image = UI(
            "ui_hardware_list_fingerprint_revealer_image"
        )
        self.ui_hardware_list_printer_revealer = UI("ui_hardware_list_printer_revealer")
        self.ui_hardware_list_printer_revealer_image = UI(
            "ui_hardware_list_printer_revealer_image"
        )

        self.ui_detail_computer_vendor_label = UI("ui_detail_computer_vendor_label")
        self.ui_detail_computer_model_label = UI("ui_detail_computer_model_label")
        self.ui_detail_computer_family_label = UI("ui_detail_computer_family_label")
        self.ui_detail_processor_vendor_label = UI("ui_detail_processor_vendor_label")
        self.ui_detail_processor_model_label = UI("ui_detail_processor_model_label")
        self.ui_detail_processor_core_label = UI("ui_detail_processor_core_label")

        self.memory_container = UI("ui_hardware_list_memory_container")

        self.ui_hardware_list_memory_container = UI("ui_hardware_list_memory_container")
        self.ui_hardware_list_storage_container = UI("ui_hardware_list_storage_container")
        self.ui_hardware_list_graphics_container = UI("ui_hardware_list_graphics_container")
        self.ui_hardware_list_display_container = UI("ui_hardware_list_display_container")
        self.ui_hardware_list_ethernet_container = UI("ui_hardware_list_ethernet_container")
        self.ui_hardware_list_wifi_container = UI("ui_hardware_list_wifi_container")
        self.ui_hardware_list_bluetooth_container = UI("ui_hardware_list_bluetooth_container")
        self.ui_hardware_list_audio_container = UI("ui_hardware_list_audio_container")
        self.ui_hardware_list_camera_container = UI("ui_hardware_list_camera_container")
        self.ui_hardware_list_keyboard_container = UI("ui_hardware_list_keyboard_container")
        self.ui_hardware_list_mouse_container = UI("ui_hardware_list_mouse_container")
        self.ui_hardware_list_fingerprint_container = UI("ui_hardware_list_fingerprint_container")
        self.ui_hardware_list_printer_container = UI("ui_hardware_list_printer_container")
        self.ui_hardware_list_os_container = UI("ui_hardware_list_os_container")

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

        self.window.present()

    def read_mauna_info(self):
        mauna_info = OSManager.get_os_info()
        self.ui_distro_id_label.set_text(mauna_info["os_id"].title())
        self.ui_distro_version_label.set_text(mauna_info["os_version_id"])
        codename_map = {
            "mauna": "Sirius",
            "polaris": "Polaris",
            # "orion": "Orion",
        }
        raw_name = mauna_info.get("os_codename", "")
        display_name = codename_map.get(raw_name, raw_name)
        self.ui_distro_codename_label.set_text(f"{display_name}")
        self.ui_username_label.set_text(f"{GLib.get_user_name()}")
        self.ui_hostname_label.set_text(mauna_info["hostname"].lower())
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
        desktop_info = "{} {} ({})".format(
            mauna_info["desktop"],
            mauna_info["desktop_version"],
            mauna_info["display"],
        )
        self.ui_desktop_label.set_text(desktop_info)

        # CPU
        processor_info = self.computerManager.get_processor_info()
        self.ui_processor_label.set_text(processor_info["name"])
        self.ui_detail_processor_vendor_label.set_text(processor_info["vendor"])
        self.ui_detail_processor_model_label.set_text(processor_info["name"])
        self.ui_detail_processor_core_label.set_text(
            f"{processor_info['core_count']} / {processor_info['thread_count']}"
        )

        # Memory
        memory_summary = self.computerManager.get_memory_summary()
        # memory_summary = "32.0 GB Unknown Unknown"
        # TODO FIXME
        self.ui_memory_label.set_text(memory_summary.replace("Unknown", ""))


        # Lazy Init PCI & USB devices information singleton
        hardware_info = HardwareDetector.get_hardware_info()


        # hardware details -memory screen START
        def populate_memory_list(memory_slots):
            """Populate ui_hardware_list_memory_container using Gtk.Grid for perfect alignment."""

            container = self.ui_hardware_list_memory_container

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label(_("Slot"), bold=True), 0, 0, 1, 1)
            grid.attach(make_label(_("Vendor"), bold=True), 1, 0, 1, 1)
            grid.attach(make_label(_("Size"), bold=True), 2, 0, 1, 1)
            grid.attach(make_label(_("Type"), bold=True), 3, 0, 1, 1)
            grid.attach(make_label(_("Speed"), bold=True), 4, 0, 1, 1)

            # Empty case
            if not memory_slots:
                grid.attach(make_label(_("No memory information")), 0, 1, 5, 1)
                container.show_all()
                return

            # Data rows
            row = 1
            for index, slot in enumerate(memory_slots, start=1):
                size = slot.get("size", 0.0)
                mem_type = slot.get("type", "Unknown")
                vendor = slot.get("vendor", _("Unknown")) or _("Unknown")
                speed = slot.get("speed", "") or ""

                is_empty = (not size) or size == 0.0 or mem_type == "Unknown"

                # Slot number
                grid.attach(make_label(str(index)), 0, row, 1, 1)

                if is_empty:
                    # Show "empty" for blank slots
                    grid.attach(make_label(_("empty")), 1, row, 1, 1)
                    grid.attach(make_label(""), 2, row, 1, 1)
                    grid.attach(make_label(""), 3, row, 1, 1)
                    grid.attach(make_label(""), 4, row, 1, 1)

                else:
                    # Size formatting (16 -> "16 GB")
                    if isinstance(size, (int, float)):
                        if float(size).is_integer():
                            size_text = f"{int(size)} GB"
                        else:
                            size_text = f"{size} GB"
                    else:
                        size_text = str(size)

                    grid.attach(make_label(vendor), 1, row, 1, 1)
                    grid.attach(make_label(size_text), 2, row, 1, 1)
                    grid.attach(make_label(mem_type), 3, row, 1, 1)
                    grid.attach(make_label(speed), 4, row, 1, 1)

                row += 1

            container.show_all()

        populate_memory_list(self.computerManager.get_memory_info())
        # hardware details -memory screen END

        # hardware details -storage screen START
        def populate_storage_list(storage_list):
            """Populate ui_hardware_list_storage_container with storage device information using Gtk.Grid."""

            container = self.ui_hardware_list_storage_container

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: create left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Size", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Type", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # Filter valid storage devices
            valid_storage = [dev for dev in storage_list if dev.get("type")]

            # No valid devices
            if not valid_storage:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Add rows
            row = 1
            for device in valid_storage:
                size = device.get("size", "")
                stype = device.get("type", "")
                model = device.get("model", "")

                grid.attach(make_label(size), 0, row, 1, 1)
                grid.attach(make_label(stype), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_storage_list(hardware_info.get("storage", []))
        # hardware details -storage screen END


        # hardware details -graphics screen START
        def populate_graphics_list(graphics_list):
            """Populate ui_hardware_list_graphics_container with graphics device information using Gtk.Grid."""

            container = self.ui_hardware_list_graphics_container

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # No devices
            if not graphics_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for gpu in graphics_list:
                vendor = gpu.get("vendor", "")
                driver = gpu.get("driver", "")
                model = gpu.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_graphics_list(hardware_info.get("graphics", []))
        # hardware details -graphics screen END

        # hardware details -display screen START
        def populate_display_list(container, display_list):
            """Populate the given GTK container with display device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Resolution", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # No displays
            if not display_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for disp in display_list:
                vendor = disp.get("vendor", "")
                resolution = disp.get("resolution", "")
                model = disp.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(resolution), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_display_list(self.ui_hardware_list_display_container, hardware_info.get("display", []))
        # hardware details -display screen END

        # hardware details -ethernet screen START
        def populate_ethernet_list(container, ethernet_list):
            """Populate the given GTK container with ethernet device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # No Ethernet devices
            if not ethernet_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for eth in ethernet_list:
                vendor = eth.get("vendor", "")
                driver = eth.get("driver", "")
                model = eth.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_ethernet_list(
            self.ui_hardware_list_ethernet_container,
            hardware_info.get("ethernet", [])
        )
        # hardware details -ethernet screen START


        # hardware details -wifi screen START
        def populate_wifi_list(container, wifi_list):
            """Populate the given GTK container with WiFi device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # No WiFi adapters
            if not wifi_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Add WiFi rows
            row = 1
            for wifi in wifi_list:
                vendor = wifi.get("vendor", "")
                driver = wifi.get("driver", "")
                model = wifi.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_wifi_list(
            self.ui_hardware_list_wifi_container,
            hardware_info.get("wifi", [])
        )
        # hardware details -wifi screen END

        # hardware details -bluetooth screen START
        def populate_bluetooth_list(container, bluetooth_list):
            """Populate the given GTK container with Bluetooth device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # No Bluetooth adapters
            if not bluetooth_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Data rows
            row = 1
            for bt in bluetooth_list:
                vendor = bt.get("vendor", "")
                driver = bt.get("driver", "")
                model = bt.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_bluetooth_list(
            self.ui_hardware_list_bluetooth_container,
            hardware_info.get("bluetooth", [])
        )
        # hardware details -bluetooth screen END

        # hardware details -audio screen START
        def populate_audio_list(container, audio_list):
            """Populate the given GTK container with audio device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: create left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # Empty case
            if not audio_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for dev in audio_list:
                vendor = dev.get("vendor", "")
                driver = dev.get("driver", "")
                model = dev.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_audio_list(
            self.ui_hardware_list_audio_container,
            hardware_info.get("audio", [])
        )
        # hardware details -audio screen END


        # hardware details -camera screen START
        def populate_camera_list(container, camera_list):
            """Populate the given GTK container with camera device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: create left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Model", bold=True), 2, 0, 1, 1)

            # Empty case
            if not camera_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for dev in camera_list:
                vendor = dev.get("vendor", "")
                driver = dev.get("driver", "")
                model = dev.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(model), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_camera_list(
            self.ui_hardware_list_camera_container,
            hardware_info.get("camera", [])
        )
        # hardware details -camera screen END
        # hardware details -keyboard screen START
        def populate_keyboard_list(container, keyboard_list):
            """Populate the given GTK container with keyboard device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: create left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Name", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Connection", bold=True), 2, 0, 1, 1)

            # Empty case
            if not keyboard_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for dev in keyboard_list:
                name = dev.get("name", "")
                driver = dev.get("driver", "")
                connection = dev.get("bus", "")

                grid.attach(make_label(name), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(connection), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_keyboard_list(
            self.ui_hardware_list_keyboard_container,
            hardware_info.get("keyboard", [])
        )
        # hardware details -keyboard screen END
        # hardware details -mouse screen START
        def populate_mouse_list(container, mouse_list):
            """Populate the given GTK container with mouse device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: create left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Name", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Driver", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Connection", bold=True), 2, 0, 1, 1)

            # Empty case
            if not mouse_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 3, 1)
                container.show_all()
                return

            # Rows
            row = 1
            for dev in mouse_list:
                name = dev.get("name", "")
                driver = dev.get("driver", "")
                connection = dev.get("bus", "")

                grid.attach(make_label(name), 0, row, 1, 1)
                grid.attach(make_label(driver), 1, row, 1, 1)
                grid.attach(make_label(connection), 2, row, 1, 1)

                row += 1

            container.show_all()

        populate_mouse_list(
            self.ui_hardware_list_mouse_container,
            hardware_info.get("mouse", [])
        )
        # hardware details -mouse screen END
        # hardware details -fingerprint screen START
        def populate_fingerprint_list(container, fp_list):
            """Populate the given GTK container with fingerprint device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()

                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)

                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Vendor", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Name", bold=True), 1, 0, 1, 1)

            # Empty case
            if not fp_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 2, 1)
                container.show_all()
                return

            # Data rows
            row = 1
            for dev in fp_list:
                vendor = dev.get("vendor", "")
                name = dev.get("name", "")

                grid.attach(make_label(vendor), 0, row, 1, 1)
                grid.attach(make_label(name), 1, row, 1, 1)
                row += 1

            container.show_all()

        populate_fingerprint_list(
            self.ui_hardware_list_fingerprint_container,
            hardware_info.get("fingerprint", [])
        )
        # hardware details -fingerprint screen END

        # hardware details -printer screen START
        def populate_printer_list(container, printer_list):
            """Populate the given GTK container with printer device information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create and attach a grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)  # prevent equal column width
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: create left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row
            grid.attach(make_label("Name", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Connection", bold=True), 1, 0, 1, 1)

            # Empty case
            if not printer_list:
                grid.attach(make_label(_("Device not found")), 0, 1, 2, 1)
                container.show_all()
                return

            # Data rows
            row = 1
            for dev in printer_list:
                name = dev.get("name", "")
                connection = dev.get("bus", "")

                grid.attach(make_label(name), 0, row, 1, 1)
                grid.attach(make_label(connection), 1, row, 1, 1)

                row += 1

            container.show_all()

        populate_printer_list(
            self.ui_hardware_list_printer_container,
            hardware_info.get("printer", [])
        )
        # hardware details -printer screen END


        # hardware details -os screen START
        def populate_os_list(container, os_info):
            """Populate the given GTK container with operating system information using Gtk.Grid."""

            # Clear previous children
            for child in container.get_children():
                container.remove(child)

            # Create grid
            grid = Gtk.Grid()
            grid.set_row_spacing(6)
            grid.set_column_spacing(20)
            grid.set_column_homogeneous(False)
            grid.set_hexpand(True)

            container.pack_start(grid, True, True, 0)

            # Helper: left-aligned label
            def make_label(text, bold=False):
                text = str(text) if text is not None else ""
                label = Gtk.Label()
                if bold:
                    label.set_markup(f"<b>{text}</b>")
                else:
                    label.set_text(text)
                label.set_xalign(0.0)
                label.set_hexpand(True)
                return label

            # Header row (codename removed)
            grid.attach(make_label("Name", bold=True), 0, 0, 1, 1)
            grid.attach(make_label("Version", bold=True), 1, 0, 1, 1)
            grid.attach(make_label("Kernel", bold=True), 2, 0, 1, 1)
            grid.attach(make_label("Desktop", bold=True), 3, 0, 1, 1)
            grid.attach(make_label("Display", bold=True), 4, 0, 1, 1)

            # Empty case
            if not os_info:
                grid.attach(make_label(_("Device not found")), 0, 1, 5, 1)
                container.show_all()
                return

            # Extract OS fields (codename removed)
            name = os_info.get("os_name", "")
            version = os_info.get("os_version", "")
            kernel = os_info.get("kernel", "")
            desktop = f"{os_info.get('desktop', '')} {os_info.get('desktop_version', '')}".strip()
            display = os_info.get("display", "")

            # Row
            grid.attach(make_label(name), 0, 1, 1, 1)
            grid.attach(make_label(version), 1, 1, 1, 1)
            grid.attach(make_label(kernel), 2, 1, 1, 1)
            grid.attach(make_label(desktop), 3, 1, 1, 1)
            grid.attach(make_label(display), 4, 1, 1, 1)

            container.show_all()

        populate_os_list(self.ui_hardware_list_os_container, OSManager.get_os_info())

        # hardware details -os screen END



        def set_list_label(label, devices, fields, skip_if_type_none=False):
            """Builds text safely without trailing newline."""
            try:
                if not devices:
                    label.set_text(_("Device not found"))
                    return

                items = []

                for device in devices:
                    if skip_if_type_none and device.get("type") is None:
                        continue

                    values = []
                    for f in fields:
                        val = device.get(f)
                        if val:
                            values.append(str(val))

                    text = " ".join(values).strip()
                    if text:
                        items.append(text)

                if not items:
                    label.set_text(_("Device not found"))
                    return

                label.set_text("\n".join(items))

            except Exception as e:
                print("device summary error:", e)
                label.set_text(_("Device not found"))

        set_list_label(
            self.ui_graphics_label,
            hardware_info.get("graphics", []),
            ["vendor", "name"],
        )
        set_list_label(
            self.ui_ethernet_label, hardware_info.get("ethernet", []), ["name"]
        )
        set_list_label(self.ui_wifi_label, hardware_info.get("wifi", []), ["name"])
        set_list_label(
            self.ui_bluetooth_label,
            hardware_info.get("bluetooth", []),
            ["vendor", "name"],
        )
        set_list_label(
            self.ui_audio_label, hardware_info.get("audio", []), ["vendor", "name"]
        )

        set_list_label(
            self.ui_storage_label,
            hardware_info.get("storage", []),
            ["size", "model"],
            skip_if_type_none=True,
        )

        def set_ip_list_label(label, ip_list):
            """Formats list of (ip, iface) tuples and sets into label."""
            try:
                if not ip_list:
                    label.set_text(_("Unknown"))
                    return

                items = []
                for ip, iface in ip_list:
                    # Skip loopback
                    if iface == "lo":
                        continue

                    iface_str = str(iface) if iface else ""
                    ip_str = str(ip) if ip else ""

                    line = f"{iface_str} {ip_str}".strip()
                    if line:
                        items.append(line)

                # If everything was filtered out → not found
                if not items:
                    label.set_text(_("Unknown"))
                    return

                label.set_text("\n".join(items))

            except Exception as e:
                print("ip list error:", e)
                label.set_text(_("Unknown"))

        set_ip_list_label(self.ui_private_ip_label, network.get_local_ip())

        self.ui_public_ip_label.set_text(network.get_wan_ip())

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
        self.ui_hardware_list_computer_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_os_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_os_revealer.get_reveal_child()
        self.ui_hardware_list_os_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_os_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_processor_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_processor_revealer.get_reveal_child()
        self.ui_hardware_list_processor_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_processor_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_memory_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_memory_revealer.get_reveal_child()
        self.ui_hardware_list_memory_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_memory_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_storage_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_storage_revealer.get_reveal_child()
        self.ui_hardware_list_storage_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_storage_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_graphics_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_graphics_revealer.get_reveal_child()
        self.ui_hardware_list_graphics_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_graphics_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_display_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_display_revealer.get_reveal_child()
        self.ui_hardware_list_display_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_display_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_ethernet_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_ethernet_revealer.get_reveal_child()
        self.ui_hardware_list_ethernet_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_ethernet_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_wifi_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_wifi_revealer.get_reveal_child()
        self.ui_hardware_list_wifi_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_wifi_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_bluetooth_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_bluetooth_revealer.get_reveal_child()
        self.ui_hardware_list_bluetooth_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_bluetooth_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_audio_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_audio_revealer.get_reveal_child()
        self.ui_hardware_list_audio_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_audio_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_camera_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_camera_revealer.get_reveal_child()
        self.ui_hardware_list_camera_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_camera_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_keyboard_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_keyboard_revealer.get_reveal_child()
        self.ui_hardware_list_keyboard_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_keyboard_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_mouse_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_mouse_revealer.get_reveal_child()
        self.ui_hardware_list_mouse_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_mouse_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_fingerprint_eventbox_button_press_event(
        self, widget, event
    ):
        state = not self.ui_hardware_list_fingerprint_revealer.get_reveal_child()
        self.ui_hardware_list_fingerprint_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_fingerprint_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )

    def on_ui_hardware_list_printer_eventbox_button_press_event(self, widget, event):
        state = not self.ui_hardware_list_printer_revealer.get_reveal_child()
        self.ui_hardware_list_printer_revealer.set_reveal_child(state)
        icon = "go-up-symbolic" if state else "go-down-symbolic"
        self.ui_hardware_list_printer_revealer_image.set_from_icon_name(
            icon, Gtk.IconSize.BUTTON
        )
