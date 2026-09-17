#!/usr/bin/env python3
"""Ptyxis Theme Bench (native) — edits Ptyxis palettes directly, no copy/paste."""
import os
import re
import copy
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, Pango, GLib

ANSI_LABELS = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]

def mk(bg, fg, cursor, tbbg, tbfg, palette):
    return {"bg": bg, "fg": fg, "cursor": cursor, "tbbg": tbbg, "tbfg": tbfg, "palette": list(palette)}

PRESETS = [
    {"name": "GNOME", "bold_is_bright": False,
     "light": mk("#FFFFFF", "#1D1D20", "#1D1D20", "#FFFFFF", "#333333",
                 ["#1D1D20","#C01C28","#26A269","#A2734C","#12488B","#A347BA","#2AA1B3","#CFCFCF",
                  "#5D5D5D","#F66151","#33D17A","#E9AD0C","#2A7BDE","#C061CB","#33C7DE","#FFFFFF"]),
     "dark": mk("#1C1C1F", "#FFFFFF", "#FFFFFF", "#2E2E32", "#FFFFFF",
                ["#241F31","#C01C28","#2EC27E","#F5C211","#1E78E4","#9841BB","#0AB9DC","#C0BFBC",
                 "#5E5C64","#ED333B","#57E389","#F8E45C","#51A1FF","#C061CB","#4FD2FD","#F6F5F4"])},
    {"name": "Ubuntu", "bold_is_bright": False,
     "light": mk("#F8F8F8", "#121212", "#121212", "#F8F8F8", "#121212",
                 ["#F2F2F2","#F93B2E","#3F7E04","#A88F00","#5B91D7","#A77DAD","#047B7D","#1B1B1B",
                  "#707070","#CE191C","#26420C","#80721B","#395E86","#80577C","#064141","#212121"]),
     "dark": mk("#300A24", "#FFFFFF", "#FFFFFF", "#300A24", "#FFFFFF",
                ["#1B1B1B","#CC1A12","#4E9A06","#C4A000","#3667A6","#7F5985","#06989A","#D5D5D5",
                 "#838383","#F93632","#8AE234","#FCE94F","#729FCF","#AD7FA8","#34E2E2","#EEEEEC"])},
    {"name": "Solarized", "bold_is_bright": False,
     "light": mk("#FDF6E3", "#657B83", "#657B83", "#FDF6E3", "#384D55",
                 ["#073642","#DC322F","#859900","#B58900","#268BD2","#D33682","#2AA198","#EEE8D5",
                  "#002B36","#CB4B16","#586E75","#657B83","#839496","#6C71C4","#93A1A1","#FDF6E3"]),
     "dark": mk("#002B36", "#839496", "#839496", "#002B36", "#B6C8CA",
                ["#073642","#DC322F","#859900","#B58900","#268BD2","#D33682","#2AA198","#EEE8D5",
                 "#002B36","#CB4B16","#586E75","#657B83","#839496","#6C71C4","#93A1A1","#FDF6E3"])},
    {"name": "Dracula", "bold_is_bright": False,
     "light": mk("#FFFFFF", "#282A36", "#282A36", "#FFFFFF", "#282A36",
                 ["#F1F2FF","#B60021","#006800","#515F00","#6946A3","#A41D74","#006274","#F8F8F2",
                  "#8393C7","#AC202F","#006803","#585E06","#6C4993","#962F7C","#006465","#595959"]),
     "dark": mk("#282A36", "#F8F8F2", "#F8F8F2", "#282A36", "#F8F8F2",
                ["#21222C","#FF5555","#50FA7B","#F1FA8C","#BD93F9","#FF79C6","#8BE9FD","#F8F8F2",
                 "#6272A4","#FF6E6E","#69FF94","#FFFFA5","#D6ACFF","#FF92DF","#A4FFFF","#FFFFFF"])},
    {"name": "Nord", "bold_is_bright": False,
     "light": mk("#E5E9F0", "#414858", "#414858", "#E5E9F0", "#414858",
                 ["#3B4251","#BF6069","#A3BE8B","#EACB8A","#81A1C1","#B48DAC","#88C0D0","#D8DEE9",
                  "#4C556A","#BF6069","#A3BE8B","#EACB8A","#81A1C1","#B48DAC","#8FBCBB","#ECEFF4"]),
     "dark": mk("#2E3440", "#D8DEE9", "#D8DEE9", "#2E3440", "#D8DEE9",
                ["#3B4252","#BF616A","#A3BE8C","#EBCB8B","#81A1C1","#B48EAD","#88C0D0","#E5E9F0",
                 "#4C566A","#BF616A","#A3BE8C","#EBCB8B","#81A1C1","#B48EAD","#8FBCBB","#ECEFF4"])},
    {"name": "Gruvbox", "bold_is_bright": False,
     "light": mk("#FBF1C7", "#3C3836", "#3C3836", "#FBF1C7", "#3C3836",
                 ["#FBF1C7","#CC241D","#98971A","#D79921","#458588","#B16286","#689D6A","#7C6F64",
                  "#928374","#9D0006","#79740E","#B57614","#076678","#8F3F71","#427B58","#3C3836"]),
     "dark": mk("#282828", "#EBDBB2", "#EBDBB2", "#282828", "#EBDBB2",
                ["#282828","#CC241D","#98971A","#D79921","#458588","#B16286","#689D6A","#A89984",
                 "#928374","#FB4934","#B8BB26","#FABD2F","#83A598","#D3869B","#8EC07C","#EBDBB2"])},
]

CORE_ROWS = [("bg", "Background"), ("fg", "Foreground"), ("cursor", "Cursor"),
             ("tbbg", "Titlebar background"), ("tbfg", "Titlebar text")]

PALETTES_DIR = os.path.expanduser("~/.local/share/org.gnome.Ptyxis/palettes")


def hex_to_rgba(h):
    rgba = Gdk.RGBA()
    rgba.parse(h)
    return rgba


def rgba_to_hex(rgba):
    r = round(rgba.red * 255)
    g = round(rgba.green * 255)
    b = round(rgba.blue * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    r = max(0, min(255, round(r)))
    g = max(0, min(255, round(g)))
    b = max(0, min(255, round(b)))
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_hsl(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return round(h * 360), round(s * 100), round(l * 100)


def hsl_to_rgb(h, s, l):
    h, s, l = h / 360, s / 100, l / 100
    if s == 0:
        r = g = b = l
    else:
        def hue2rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1 / 6: return p + (q - p) * 6 * t
            if t < 1 / 2: return q
            if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
            return p
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1 / 3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1 / 3)
    return round(r * 255), round(g * 255), round(b * 255)


def normalize_hex(v):
    v = v.strip()
    if not v.startswith("#"):
        v = "#" + v
    if re.fullmatch(r"#[0-9a-fA-F]{6}", v):
        return v.upper()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        return "#" + "".join(c * 2 for c in v[1:]).upper()
    return None


def fresh_state(preset):
    return {
        "name": "My " + preset["name"],
        "adaptive": True,
        "bold_is_bright": preset["bold_is_bright"],
        "use_system_font": True,
        "font_desc": "Monospace 11",
        "light": copy.deepcopy(preset["light"]),
        "dark": copy.deepcopy(preset["dark"]),
    }


class ThemeBenchWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Ptyxis Theme Bench", default_width=1320, default_height=860)

        self.state = fresh_state(PRESETS[2])  # start on Solarized
        self.editing_variant = "dark"
        self.core_buttons = {}
        self.ansi_buttons = []
        self.active_target = {"kind": "core", "key": "bg"}
        self._ft_syncing = False

        # Reflect whatever font Ptyxis is actually using right now, not a hardcoded guess.
        try:
            top_settings = Gio.Settings.new("org.gnome.Ptyxis")
            self.state["use_system_font"] = top_settings.get_boolean("use-system-font")
            current_font = top_settings.get_string("font-name")
            if current_font:
                self.state["font_desc"] = current_font
        except Exception:
            pass

        # Open editing on whichever variant Ptyxis is actually displaying right now.
        try:
            style = top_settings.get_string("interface-style")
            if style == "dark":
                self.editing_variant = "dark"
            elif style == "light":
                self.editing_variant = "light"
            else:  # "system" — resolve against the desktop's own light/dark choice
                scheme = Gio.Settings.new("org.gnome.desktop.interface").get_string("color-scheme")
                self.editing_variant = "dark" if scheme == "prefer-dark" else "light"
        except Exception:
            pass

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        title = Adw.WindowTitle(title="Ptyxis Theme Bench", subtitle="edits Ptyxis directly — nothing to copy/paste")
        header.set_title_widget(title)

        self.apply_btn = Gtk.Button(label="Apply to Ptyxis")
        self.apply_btn.add_css_class("suggested-action")
        self.apply_btn.connect("clicked", self.on_apply)
        header.pack_end(self.apply_btn)

        toolbar.add_top_bar(header)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, position=460, vexpand=True, hexpand=True)
        paned.set_shrink_start_child(False)
        paned.set_shrink_end_child(False)
        paned.set_resize_start_child(False)
        paned.set_resize_end_child(True)
        sidebar = self.build_sidebar()
        sidebar.set_size_request(420, -1)
        main = self.build_main()
        main.set_size_request(420, -1)
        paned.set_start_child(sidebar)
        paned.set_end_child(main)
        toolbar.set_content(paned)

        self.set_content(toolbar)

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), self.css_provider,
                                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.ft_css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), self.ft_css_provider,
                                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.refresh_all()

    # ---------- sidebar ----------
    def build_sidebar(self):
        scroller = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin_top=16, margin_bottom=16,
                       margin_start=16, margin_end=16)
        scroller.set_child(box)

        # Presets
        box.append(self.section_label("Presets"))
        preset_flow = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, max_children_per_line=3,
                                   column_spacing=6, row_spacing=6)
        for p in PRESETS:
            btn = Gtk.Button(label=p["name"])
            btn.connect("clicked", lambda _b, preset=p: self.load_preset(preset))
            preset_flow.append(btn)
        box.append(preset_flow)

        # Fine-tune (RGB / HSL sliders for whichever swatch was last focused)
        box.append(self.section_label("Fine-tune"))
        self.ft_hint = Gtk.Label(label="click any swatch below", halign=Gtk.Align.START,
                                  css_classes=["caption", "dim-label"])
        box.append(self.ft_hint)

        preview_row = Gtk.Box(spacing=10, margin_top=4, margin_bottom=6)
        self.ft_swatch = Gtk.Frame(width_request=44, height_request=44, valign=Gtk.Align.CENTER)
        self.ft_swatch.set_name("ftSwatch")
        self.ft_hex_entry = Gtk.Entry(hexpand=True, valign=Gtk.Align.CENTER)
        self.ft_hex_entry.connect("activate", self.on_ft_hex_activate)
        preview_row.append(self.ft_swatch)
        preview_row.append(self.ft_hex_entry)
        box.append(preview_row)

        self.rgb_sliders = {}
        rgb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        for label, key in [("R", "r"), ("G", "g"), ("B", "b")]:
            row = Gtk.Box(spacing=8)
            row.append(Gtk.Label(label=label, width_chars=1, css_classes=["caption"]))
            scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
            scale.set_range(0, 255)
            scale.set_draw_value(False)
            scale.set_name(f"ftScale{key.upper()}")
            val_label = Gtk.Label(label="0", width_chars=3, css_classes=["caption", "numeric"])
            scale.connect("value-changed", self.on_rgb_slider_changed)
            row.append(scale)
            row.append(val_label)
            rgb_box.append(row)
            self.rgb_sliders[key] = (scale, val_label)
        box.append(rgb_box)

        self.hsl_sliders = {}
        hsl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin_top=8)
        for label, key, maxv in [("H", "h", 360), ("S", "s", 100), ("L", "l", 100)]:
            row = Gtk.Box(spacing=8)
            row.append(Gtk.Label(label=label, width_chars=1, css_classes=["caption"]))
            scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
            scale.set_range(0, maxv)
            scale.set_draw_value(False)
            scale.set_name(f"ftScale{key.upper()}")
            val_label = Gtk.Label(label="0", width_chars=4, css_classes=["caption", "numeric"])
            scale.connect("value-changed", self.on_hsl_slider_changed)
            row.append(scale)
            row.append(val_label)
            hsl_box.append(row)
            self.hsl_sliders[key] = (scale, val_label)
        box.append(hsl_box)

        # Theme name
        box.append(self.section_label("Theme name"))
        self.name_entry = Gtk.Entry(text=self.state["name"])
        self.name_entry.connect("changed", self.on_name_changed)
        box.append(self.name_entry)

        # Adaptive switch
        adaptive_row = Adw.ActionRow(title="Different colors for light &amp; dark")
        self.adaptive_switch = Gtk.Switch(valign=Gtk.Align.CENTER, active=True)
        self.adaptive_switch.connect("notify::active", self.on_adaptive_toggled)
        adaptive_row.add_suffix(self.adaptive_switch)
        group = Adw.PreferencesGroup()
        group.add(adaptive_row)
        box.append(group)

        # Variant toggle
        self.variant_box = Gtk.Box(spacing=0, css_classes=["linked"], halign=Gtk.Align.START)
        self.light_toggle = Gtk.ToggleButton(label="Light")
        self.dark_toggle = Gtk.ToggleButton(label="Dark", active=True, group=self.light_toggle)
        self.light_toggle.connect("toggled", self.on_variant_toggled)
        self.variant_box.append(self.light_toggle)
        self.variant_box.append(self.dark_toggle)
        box.append(self.variant_box)

        # Core colors
        box.append(self.section_label("Core colors"))
        core_group = Adw.PreferencesGroup()
        for key, label in CORE_ROWS:
            row = Adw.ActionRow(title=label)
            btn = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog(with_alpha=False), valign=Gtk.Align.CENTER)
            btn.connect("notify::rgba", self.on_core_color_changed, key)
            self.add_focus_target(btn, {"kind": "core", "key": key})
            self.core_buttons[key] = btn
            row.add_suffix(btn)
            core_group.add(row)
        box.append(core_group)

        bold_row = Adw.ActionRow(title="Bold text uses the bright color variant")
        self.bold_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.bold_switch.connect("notify::active", self.on_bold_toggled)
        bold_row.add_suffix(self.bold_switch)
        bold_group = Adw.PreferencesGroup()
        bold_group.add(bold_row)
        box.append(bold_group)

        # ANSI palette
        box.append(self.section_label("ANSI palette"))
        grid = Gtk.Grid(row_spacing=4, column_spacing=4)
        for col, label in enumerate(ANSI_LABELS):
            l = Gtk.Label(label=label, css_classes=["caption"])
            grid.attach(l, col + 1, 0, 1, 1)
        for row_idx, row_name in enumerate(["Normal", "Bright"]):
            grid.attach(Gtk.Label(label=row_name, css_classes=["caption"], halign=Gtk.Align.START), 0, row_idx + 1, 1, 1)
            for col in range(8):
                idx = row_idx * 8 + col
                btn = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog(with_alpha=False))
                btn.set_size_request(34, 28)
                btn.connect("notify::rgba", self.on_ansi_color_changed, idx)
                self.add_focus_target(btn, {"kind": "ansi", "idx": idx})
                self.ansi_buttons.append(btn)
                grid.attach(btn, col + 1, row_idx + 1, 1, 1)
        box.append(grid)

        # Font
        box.append(self.section_label("Font"))
        font_use_row = Adw.ActionRow(title="Use system font")
        self.font_switch = Gtk.Switch(valign=Gtk.Align.CENTER, active=True)
        self.font_switch.connect("notify::active", self.on_font_switch_toggled)
        font_use_row.add_suffix(self.font_switch)
        font_group = Adw.PreferencesGroup()
        font_group.add(font_use_row)

        font_row = Adw.ActionRow(title="Custom font")
        self.font_btn = Gtk.FontDialogButton(dialog=Gtk.FontDialog(), valign=Gtk.Align.CENTER, sensitive=False)
        self.font_btn.set_font_desc(Pango.FontDescription.from_string(self.state["font_desc"]))
        self.font_btn.connect("notify::font-desc", self.on_font_changed)
        font_row.add_suffix(self.font_btn)
        font_group.add(font_row)
        box.append(font_group)

        self.status_label = Gtk.Label(label="", wrap=True, css_classes=["caption"], margin_top=8)
        box.append(self.status_label)

        return scroller

    def section_label(self, text):
        l = Gtk.Label(label=text, halign=Gtk.Align.START, css_classes=["heading"])
        return l

    # ---------- main / preview ----------
    def build_main(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=16, margin_bottom=16,
                       margin_start=16, margin_end=16)

        frame = Gtk.Frame(css_classes=["card"])
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.title_label = Gtk.Label(label="user@ubuntu — ~/projects/site", halign=Gtk.Align.START,
                                      margin_start=10, margin_top=6, margin_bottom=6)
        self.title_label.set_name("ttbTitlebar")
        inner.append(self.title_label)

        self.preview = Gtk.TextView(editable=False, cursor_visible=False, monospace=True, vexpand=True,
                                     top_margin=14, bottom_margin=14, left_margin=16, right_margin=16,
                                     wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.preview.set_name("ttbPreview")
        inner.append(self.preview)
        frame.set_child(inner)
        box.append(frame)

        buf = self.preview.get_buffer()
        self.preview_tags = {
            "user": buf.create_tag("user", weight=Pango.Weight.BOLD),
            "path": buf.create_tag("path", weight=Pango.Weight.BOLD),
            "dim": buf.create_tag("dim"),
            "dir": buf.create_tag("dir", weight=Pango.Weight.BOLD),
            "exe": buf.create_tag("exe", weight=Pango.Weight.BOLD),
            "archive": buf.create_tag("archive", weight=Pango.Weight.BOLD),
            "add": buf.create_tag("add"),
            "del": buf.create_tag("del"),
            "warn": buf.create_tag("warn", weight=Pango.Weight.BOLD),
        }

        note = Gtk.Label(
            label="This writes a real .palette file to ~/.local/share/org.gnome.Ptyxis/palettes/ and updates "
                  "your default profile's GSettings directly — open a new Ptyxis window to see it.",
            wrap=True, halign=Gtk.Align.START, css_classes=["caption", "dim-label"])
        box.append(note)

        return box

    # ---------- state <-> UI ----------
    def active_data(self):
        return self.state[self.editing_variant] if self.state["adaptive"] else self.state["light"]

    def load_preset(self, preset):
        self.state = fresh_state(preset)
        self.refresh_all()

    def on_name_changed(self, entry):
        self.state["name"] = entry.get_text()

    def on_adaptive_toggled(self, switch, _pspec):
        self.state["adaptive"] = switch.get_active()
        if not self.state["adaptive"]:
            self.state["dark"] = copy.deepcopy(self.state["light"])
        self.variant_box.set_sensitive(self.state["adaptive"])
        self.refresh_all()

    def on_variant_toggled(self, _btn):
        self.editing_variant = "light" if self.light_toggle.get_active() else "dark"
        self.refresh_all()

    def on_core_color_changed(self, btn, _pspec, key):
        self.active_data()[key] = rgba_to_hex(btn.get_rgba())
        self.update_fine_tune()
        self.refresh_preview()

    def on_ansi_color_changed(self, btn, _pspec, idx):
        self.active_data()["palette"][idx] = rgba_to_hex(btn.get_rgba())
        self.update_fine_tune()
        self.refresh_preview()

    # ---------- fine-tune (RGB / HSL sliders) ----------
    def add_focus_target(self, widget, target):
        controller = Gtk.EventControllerFocus()
        controller.connect("enter", lambda _c, t=target: self.select_target(t))
        widget.add_controller(controller)

    def get_hex_for(self, target):
        d = self.active_data()
        return d[target["key"]] if target["kind"] == "core" else d["palette"][target["idx"]]

    def set_hex_for(self, target, hexval):
        d = self.active_data()
        if target["kind"] == "core":
            d[target["key"]] = hexval
        else:
            d["palette"][target["idx"]] = hexval

    def target_label(self, target):
        if target["kind"] == "core":
            return dict(CORE_ROWS)[target["key"]]
        bright = target["idx"] >= 8
        return ("Bright " if bright else "") + ANSI_LABELS[target["idx"] % 8] + f" · Color{target['idx']}"

    def select_target(self, target):
        self.active_target = target
        self.update_fine_tune()

    def sync_button_for_target(self, target, hexval):
        if target["kind"] == "core":
            self.core_buttons[target["key"]].set_rgba(hex_to_rgba(hexval))
        else:
            self.ansi_buttons[target["idx"]].set_rgba(hex_to_rgba(hexval))

    def update_fine_tune(self):
        hexval = self.get_hex_for(self.active_target)
        r, g, b = hex_to_rgb(hexval)
        h, s, l = rgb_to_hsl(r, g, b)

        self.ft_hint.set_label("editing: " + self.target_label(self.active_target))
        self.ft_hex_entry.set_text(hexval)

        self._ft_syncing = True
        self.rgb_sliders["r"][0].set_value(r); self.rgb_sliders["r"][1].set_label(str(r))
        self.rgb_sliders["g"][0].set_value(g); self.rgb_sliders["g"][1].set_label(str(g))
        self.rgb_sliders["b"][0].set_value(b); self.rgb_sliders["b"][1].set_label(str(b))
        self.hsl_sliders["h"][0].set_value(h); self.hsl_sliders["h"][1].set_label(f"{h}°")
        self.hsl_sliders["s"][0].set_value(s); self.hsl_sliders["s"][1].set_label(f"{s}%")
        self.hsl_sliders["l"][0].set_value(l); self.hsl_sliders["l"][1].set_label(f"{l}%")
        self._ft_syncing = False

        css = f"""
        frame#ftSwatch {{ background-color: {hexval}; }}
        scale#ftScaleR trough {{ background-image: linear-gradient(to right, {rgb_to_hex(0,g,b)}, {rgb_to_hex(255,g,b)}); }}
        scale#ftScaleG trough {{ background-image: linear-gradient(to right, {rgb_to_hex(r,0,b)}, {rgb_to_hex(r,255,b)}); }}
        scale#ftScaleB trough {{ background-image: linear-gradient(to right, {rgb_to_hex(r,g,0)}, {rgb_to_hex(r,g,255)}); }}
        scale#ftScaleH trough {{ background-image: linear-gradient(to right, hsl(0,{s}%,{l}%), hsl(60,{s}%,{l}%), hsl(120,{s}%,{l}%), hsl(180,{s}%,{l}%), hsl(240,{s}%,{l}%), hsl(300,{s}%,{l}%), hsl(360,{s}%,{l}%)); }}
        scale#ftScaleS trough {{ background-image: linear-gradient(to right, hsl({h},0%,{l}%), hsl({h},100%,{l}%)); }}
        scale#ftScaleL trough {{ background-image: linear-gradient(to right, #000000, hsl({h},{s}%,50%), #ffffff); }}
        """
        self.ft_css_provider.load_from_string(css)

    def on_rgb_slider_changed(self, _scale):
        if self._ft_syncing:
            return
        r = round(self.rgb_sliders["r"][0].get_value())
        g = round(self.rgb_sliders["g"][0].get_value())
        b = round(self.rgb_sliders["b"][0].get_value())
        hexval = rgb_to_hex(r, g, b)
        self.set_hex_for(self.active_target, hexval)
        self.sync_button_for_target(self.active_target, hexval)
        self.update_fine_tune()
        self.refresh_preview()

    def on_hsl_slider_changed(self, _scale):
        if self._ft_syncing:
            return
        h = self.hsl_sliders["h"][0].get_value()
        s = self.hsl_sliders["s"][0].get_value()
        l = self.hsl_sliders["l"][0].get_value()
        r, g, b = hsl_to_rgb(h, s, l)
        hexval = rgb_to_hex(r, g, b)
        self.set_hex_for(self.active_target, hexval)
        self.sync_button_for_target(self.active_target, hexval)
        self.update_fine_tune()
        self.refresh_preview()

    def on_ft_hex_activate(self, entry):
        hexval = normalize_hex(entry.get_text())
        if hexval:
            self.set_hex_for(self.active_target, hexval)
            self.sync_button_for_target(self.active_target, hexval)
            self.update_fine_tune()
            self.refresh_preview()

    def on_bold_toggled(self, switch, _pspec):
        self.state["bold_is_bright"] = switch.get_active()
        self.refresh_preview()

    def on_font_switch_toggled(self, switch, _pspec):
        self.state["use_system_font"] = switch.get_active()
        self.font_btn.set_sensitive(not switch.get_active())

    def on_font_changed(self, btn, _pspec):
        desc = btn.get_font_desc()
        if desc:
            self.state["font_desc"] = desc.to_string()
        self.refresh_preview()

    def refresh_all(self):
        self.name_entry.set_text(self.state["name"])
        self.adaptive_switch.set_active(self.state["adaptive"])
        self.variant_box.set_sensitive(self.state["adaptive"])
        self.dark_toggle.set_active(self.editing_variant == "dark")
        self.light_toggle.set_active(self.editing_variant == "light")
        self.bold_switch.set_active(self.state["bold_is_bright"])
        self.font_switch.set_active(self.state["use_system_font"])
        self.font_btn.set_sensitive(not self.state["use_system_font"])

        d = self.active_data()
        for key, btn in self.core_buttons.items():
            btn.set_rgba(hex_to_rgba(d[key]))
        for idx, btn in enumerate(self.ansi_buttons):
            btn.set_rgba(hex_to_rgba(d["palette"][idx]))

        self.update_fine_tune()
        self.refresh_preview()

    # ---------- preview ----------
    def refresh_preview(self):
        d = self.active_data()
        p = d["palette"]
        bright = self.state["bold_is_bright"]

        def eff(i):
            return p[8 + i] if bright else p[i]

        if self.state["use_system_font"]:
            font_family, font_size = "Monospace", 11
        else:
            desc = Pango.FontDescription.from_string(self.state["font_desc"])
            font_family = desc.get_family() or "Monospace"
            raw_size = desc.get_size()
            font_size = (raw_size / Pango.SCALE) if raw_size else 11

        css = f"""
        textview#ttbPreview text {{ background-color: {d['bg']}; color: {d['fg']}; caret-color: {d['cursor']}; }}
        textview#ttbPreview {{ background-color: {d['bg']}; font-family: "{font_family}"; font-size: {font_size}pt; }}
        label#ttbTitlebar {{ background-color: {d['tbbg']}; color: {d['tbfg']}; padding: 4px 10px; }}
        """
        self.css_provider.load_from_string(css)

        buf = self.preview.get_buffer()
        buf.set_text("")
        tags = self.preview_tags
        tags["user"].set_property("foreground", eff(2))
        tags["path"].set_property("foreground", eff(4))
        tags["dim"].set_property("foreground", d["fg"])
        tags["dir"].set_property("foreground", eff(4))
        tags["exe"].set_property("foreground", eff(2))
        tags["archive"].set_property("foreground", eff(1))
        tags["add"].set_property("foreground", p[2])
        tags["del"].set_property("foreground", p[1])
        tags["warn"].set_property("foreground", eff(3))

        def insert(text, tag=None):
            end = buf.get_end_iter()
            if tag:
                buf.insert_with_tags(end, text, tags[tag])
            else:
                buf.insert(end, text)

        insert("user@ubuntu", "user"); insert(":", "dim"); insert("~/projects/site", "path"); insert("$ ls -la\n", "dim")
        insert("drwxr-xr-x  4 user user  4096 Sep 17 09:14 ", "dim"); insert("src\n", "dir")
        insert("-rwxr-xr-x  1 user user  8840 Sep 16 22:47 ", "dim"); insert("build.sh\n", "exe")
        insert("-rw-r--r--  1 user user 40211 Sep 10 14:03 ", "dim"); insert("release-v1.2.tar.gz\n\n", "archive")
        insert("user@ubuntu", "user"); insert(":", "dim"); insert("~/projects/site", "path"); insert("$ git diff --stat\n", "dim")
        insert("+  set_palette(profile, custom_palette);\n", "add")
        insert("-  set_palette(profile, DEFAULT_PALETTE);\n\n", "del")
        insert("user@ubuntu", "user"); insert(":", "dim"); insert("~/projects/site", "path"); insert("$ ./build.sh\n", "dim")
        insert("warning:", "warn"); insert(" 2 unused variables\n", "dim")


    # ---------- apply ----------
    def color_lines(self, d):
        lines = [f"Foreground={d['fg']}", f"Background={d['bg']}",
                 f"TitlebarBackground={d['tbbg']}", f"TitlebarForeground={d['tbfg']}",
                 f"Cursor={d['cursor']}"]
        lines += [f"Color{i}={c}" for i, c in enumerate(d["palette"])]
        return lines

    def on_apply(self, _btn):
        try:
            name = (self.state["name"] or "My Terminal Theme").strip()
            safe_name = name.replace("/", "").replace("\\", "") or "My Terminal Theme"

            os.makedirs(PALETTES_DIR, exist_ok=True)
            path = os.path.join(PALETTES_DIR, f"{safe_name}.palette")

            lines = ["[Palette]", f"Name={safe_name}"]
            if self.state["adaptive"]:
                lines.append("Primary=true")
                lines.append("")
                lines.append("[Light]")
                lines += self.color_lines(self.state["light"])
                lines.append("")
                lines.append("[Dark]")
                lines += self.color_lines(self.state["dark"])
            else:
                lines += self.color_lines(self.state["light"])

            with open(path, "w") as f:
                f.write("\n".join(lines) + "\n")

            top = Gio.Settings.new("org.gnome.Ptyxis")
            uuid = top.get_string("default-profile-uuid")
            profile_path = f"/org/gnome/Ptyxis/Profiles/{uuid}/"
            profile = Gio.Settings.new_with_path("org.gnome.Ptyxis.Profile", profile_path)
            profile.set_string("palette", safe_name)
            profile.set_boolean("bold-is-bright", self.state["bold_is_bright"])

            top.set_boolean("use-system-font", self.state["use_system_font"])
            if not self.state["use_system_font"]:
                top.set_string("font-name", self.state["font_desc"])

            self.status_label.set_label(f"Applied “{safe_name}” — open a new Ptyxis window to see it.")
        except Exception as e:
            self.status_label.set_label(f"Failed to apply: {e}")


class ThemeBenchApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.ueda.PtyxisThemeBench")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = ThemeBenchWindow(self)
        win.present()


if __name__ == "__main__":
    ThemeBenchApp().run(None)
