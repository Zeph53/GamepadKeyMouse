#!/bin/bash

if [ "$#" -lt 1 ] || [ "$#" -gt 1 ]; then
  echo "Usage: $0 path/to/script.py" >&2
  exit 1
fi

export pdir="$(dirname $(readlink -f "$0"))"
export appname="$(basename "$1" | awk -F '.py' '{print $1}')"
appnameext="$(basename "$1")"
venvdir="$pdir/$appname.venv"
export imagedir="$pdir/$appname"
imagetool="$pdir/appimagetool-*.AppImage"

while [[ -d "$venvdir" ]]; do
  printf "removing venv \n"
  rm -r "$venvdir"
  sleep 0.2
done

while [[ -d "$imagedir" ]]; do
  printf "removing imagedir \n"
  rm -r "$imagedir"
  sleep 0.2
done

if [[ ! -d "$venvdir" ]]; then
  printf "building python venv \n"
  if [[ $(python3 -m venv --copies "$venvdir"; echo $?) -eq 0 ]]; then
    source "$venvdir/bin/activate"
    #pip install evdev python-xlib six pynput pysdl2
    pip install tk pynput pysdl2
  fi
fi

mkdir -p \
  "$imagedir" \
  "$imagedir/usr" \
  "$imagedir/usr/share" \
  "$imagedir/usr/share/licenses" \
  "$imagedir/usr/share/applications" \
  "$imagedir/usr/share/icons/zeph53" \
  "$imagedir/usr/lib" \
  "$imagedir/usr/lib/x86_64-linux-gnu"

cp -a -r -f "/usr/lib/python3.13" "$imagedir/usr/lib/"
cp -r -f "$venvdir/"* "$imagedir/usr"

cp -f "/usr/lib/x86_64-linux-gnu/libtk8.6.so" "$imagedir/usr/lib/x86_64-linux-gnu/"
cp -f "/usr/lib/x86_64-linux-gnu/libtk8.6.so.0" "$imagedir/usr/lib/x86_64-linux-gnu/"

cp -f "/usr/lib/x86_64-linux-gnu/libtcl8.6.so" "$imagedir/usr/lib/x86_64-linux-gnu/"
cp -f "/usr/lib/x86_64-linux-gnu/libtcl8.6.so.0" "$imagedir/usr/lib/x86_64-linux-gnu/"

cp -a -r -f "/usr/share/tcltk/"* "$imagedir/usr/lib/"

bash -i -c "$pdir/generatelicenses.bash"

while [[ ! -e "$imagedir/usr/bin/$appnameext" ]]; do
  printf "copying source script \n"
  cp "$pdir/$appnameext" "$imagedir/usr/bin/$appnameext"
  sleep 0.2
done

if [[ -e "$imagedir/usr/bin/$appnameext"  ]];then
  ln -s "$imagedir/usr/bin/$appnameext" "$imagedir/usr/bin/$appname"
fi

if [[ ! -f "$imagedir/usr/share/applications/$appname.desktop" ]] ;then
  if touch "$imagedir/usr/share/applications/$appname.desktop"; then
    printf '%s\n' \
      "[Desktop Entry]" \
      "Type=Application" \
      "Name=$appname" \
      "Exec=/usr/bin/python3.13 /usr/bin/$appname" \
      "Icon=/usr/share/icons/zeph53/$appname" \
      "Categories=Utility" \
    > "$imagedir/usr/share/applications/$appname.desktop"
  fi
  sleep 0.2
  if [[ -f "$imagedir/usr/share/applications/$appname.desktop" ]]; then
    ln -s "$imagedir/usr/share/applications/$appname.desktop" "$imagedir/$appname.desktop"
  fi
fi

if [[ ! -f "$imagedir/AppRun" ]] ;then
  if touch "$imagedir/AppRun"; then
    printf '%s\n' \
      '#!/bin/bash' \
      'HERE="$(dirname "$(readlink -f "$0")")"' \
      'export PATH="$HERE/usr/bin:$PATH"' \
      'export PYTHONHOME="$HERE/usr"' \
      'export PYTHONPATH="$HERE/usr/lib/python3.13/site-packages"' \
      'export LD_LIBRARY_PATH="$HERE/usr/lib:$HERE/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"' \
      'export PYSDL2_DLL_PATH="$HERE/usr/lib/"' \
      'exec "$HERE/usr/bin/python3" "$HERE/usr/bin/$(ls "$HERE/usr/bin" | grep -E "\.py$")" "$@"' \
    > "$imagedir/AppRun"
  fi
  sleep 0.2
fi

convert -size 128x128 xc:#0000FF "$imagedir/usr/share/icons/zeph53/$appname.png"
ln -f -s "$imagedir/usr/share/icons/zeph53/$appname.png" "$imagedir/.DirIcon"

chmod -f -R +x "$imagedir"

ARCH=x86_64 $imagetool "$imagedir" "$pdir/$appname-x86_64.AppImage"
