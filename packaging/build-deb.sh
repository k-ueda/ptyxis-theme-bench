#!/usr/bin/env bash
# Rebuilds the .deb package from source. Run from the repo root: ./packaging/build-deb.sh
set -e
cd "$(dirname "$0")/.."
BUILD=$(mktemp -d)
mkdir -p "$BUILD/DEBIAN" "$BUILD/usr/bin" "$BUILD/usr/share/ptyxis-theme-bench" \
         "$BUILD/usr/share/applications" "$BUILD/usr/share/doc/ptyxis-theme-bench"

cp terminal_theme_bench.py "$BUILD/usr/share/ptyxis-theme-bench/"
cp terminal-theme-bench.desktop "$BUILD/usr/share/applications/"
cp packaging/DEBIAN/control "$BUILD/DEBIAN/control"
cp packaging/DEBIAN/postinst "$BUILD/DEBIAN/postinst"
chmod 755 "$BUILD/DEBIAN/postinst"

cat > "$BUILD/usr/bin/terminal-theme-bench" << 'WRAP'
#!/bin/sh
exec python3 /usr/share/ptyxis-theme-bench/terminal_theme_bench.py "$@"
WRAP
chmod 755 "$BUILD/usr/bin/terminal-theme-bench"

cp LICENSE "$BUILD/usr/share/doc/ptyxis-theme-bench/copyright"
chmod -R 644 "$BUILD/usr/share/doc/ptyxis-theme-bench/copyright" \
             "$BUILD/usr/share/applications/terminal-theme-bench.desktop" \
             "$BUILD/usr/share/ptyxis-theme-bench/terminal_theme_bench.py"
find "$BUILD" -type d -exec chmod 755 {} \;

VERSION=$(grep -oP '(?<=^Version: ).*' packaging/DEBIAN/control)
dpkg-deb --build --root-owner-group "$BUILD" "ptyxis-theme-bench_${VERSION}_all.deb"
rm -rf "$BUILD"
echo "Built ptyxis-theme-bench_${VERSION}_all.deb"
