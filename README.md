# Ptyxis Theme Bench

A native GTK4 / libadwaita app for designing a color theme for
[Ptyxis](https://gitlab.gnome.org/chergert/ptyxis) — the default terminal on
Ubuntu 26.04 and other recent GNOME desktops — and applying it instantly.

No copy/paste, no manual `.palette` file editing: pick colors with GTK's
native color picker (RGB and HSL sliders included), preview them live against
a sample terminal session, and click **Apply to Ptyxis** to write the theme
file and update your profile via GSettings on the spot.

## Features

- Six starting presets pulled from Ptyxis's own bundled themes (GNOME,
  Ubuntu, Solarized, Dracula, Nord, Gruvbox), each with real light *and* dark
  variants
- Full control over background, foreground, cursor, titlebar tint, and all
  16 ANSI colors, independently for light and dark mode
- Native font picker, native color picker — no custom widgets standing in
  for what the OS already does well
- Opens already reflecting whatever font and light/dark mode Ptyxis is
  currently using
- Applies directly — writes to
  `~/.local/share/org.gnome.Ptyxis/palettes/` and sets your default
  profile's GSettings, no shell commands to copy or paste

## Install

Download the latest `.deb` from
[Releases](../../releases/latest) and run:

```bash
sudo apt install ./ptyxis-theme-bench_*.deb
```

This also registers it as a normal application (search "Ptyxis Theme
Bench" in your app grid) and installs the `ptyxis-theme-bench` command.

## Build from source

```bash
git clone <this repo>
cd ptyxis-theme-bench
./packaging/build-deb.sh
sudo apt install ./ptyxis-theme-bench_*.deb
```

Requires `python3`, `python3-gi`, `gir1.2-gtk-4.0`, and `gir1.2-adw-1`
(all standard on Ubuntu 26.04).

## Why this exists

Ptyxis's own Preferences does let you change the font and its size — but its
Appearance section only offers a curated list of built-in palettes, with no
way to fine-tune an individual color, set an exact hex value, or give light
and dark mode different colors. This app fills that gap (and keeps the font
picker alongside it, since it's convenient to have both in one place) by
talking directly to the same `.palette` file format and GSettings schema
Ptyxis itself uses, rather than trying to patch its UI.

## License

MIT — see [LICENSE](LICENSE).
