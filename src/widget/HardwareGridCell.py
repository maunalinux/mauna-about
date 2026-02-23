import gi

gi.require_version("Gtk", "3.0")
from locale import gettext as _

from gi.repository import Gtk


class HardwareGridCell(Gtk.Box):
    def __init__(self, icon_name, title, name):
        super().__init__()

        self.get_style_context().add_class("card")
        self.get_style_context().add_class("p-7")

        # Icon
        box = Gtk.Box(spacing=7, halign="start", valign="center")
        icon_img = Gtk.Image(icon_name=icon_name, pixel_size=42)

        # Title + Name
        name_box = Gtk.Box(
            orientation="vertical", spacing=3, valign="center", halign="start"
        )
        title_lbl = Gtk.Label(label=f"{_(title)}", halign="start")
        name_lbl = Gtk.Label(
            label=f"<b>{_(name)}</b>",
            halign="start",
            use_markup=True,
            ellipsize="end",
            selectable=True,
        )
        name_box.add(title_lbl)
        name_box.add(name_lbl)

        box.add(icon_img)
        box.add(name_box)

        self.add(box)
