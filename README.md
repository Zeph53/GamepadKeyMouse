# GAMEPADKEYMOUSE.PY  
This is a Python3 script that allows the user to move the mouse cursor around with a gamepad's joystick. As well as the right and left click. Also, the ability to open an on-screen keyboard that is navigatable with the joysticks.  

Currently, the on-screen keyboard is nearly entirely functional, can use all, if not, most of the secondary symbols. Mouse cursor works but it's slightly janky still.  

ChatGPT is completely responsible for this. I primarily created this so I could sit back and do some sort of text development using my gamepad. It take a fair amount of practice to get used to, try to focus on a single highlight and use the other one for symbols, modifier keys, or things like backspace.  

## Requirements  
    Gamepad, script tested and configured ONLY using an oldschool "Playstation (DS3) Controller" connected through bluetooth.
    Debian with XFCE4, possibly any Linux OS with a DE that supports evdev now.
    Python3 and modules: tk, pysdl2, evdev, python-xlib, six, and pynput

## Installation  
### Installing the required dependencies into an interally managed environment using python3-pip  
#### Initially python3-pip must be installed in order to use pip:  
    sudo apt install python3-pip
#### Then use pip to install Tkinter, Pynput, PySDL2, and their dependencies: evdev, six, and python3-xlib:  
    pip install tk pynput pysdl2
### Installing the required dependencies into an externally managed environment using APT  
#### If installing into an interally managed environment isn't working, try to install externally:  
    sudo apt install python3-tk python3-sdl2 python3-pynput
### Installing the AppImage is as simple as it gets  
#### Simply download the latest AppImage asset file from GitHub Releases into the current directory:  
    wget $(curl -s https://api.github.com/repos/Zeph53/GamepadKeyMouse/releases/latest | grep browser_download_url | grep AppImage | cut -d '"' -f 4)
#### Then the AppImage must have execute permissions added:  
    chmod +x "gamepadkeymouse-x86_64.AppImage"
#### Here is a simple single command to download and set execute permission for the AppImage:  
    url=$(curl -s https://api.github.com/repos/Zeph53/GamepadKeyMouse/releases/latest | grep browser_download_url | grep AppImage | cut -d '"' -f 4) && wget "$url" && chmod +x "$(basename "$url")"


## Usage  
#### Simply open a terminal and execute the script:  
    python3 ~/GamepadKeyMouse/gamepadkeymouse.py
#### If you downloaded the AppImage, make sure your current directory contains it:  
    'gamepadkeymouse-x86_64.AppImage'
Debug information such as button and axis inputs will be displayed.  

#### Mouse controls  
Left analogue stick (?) (axis 0,1) to move the mouse cursor around the screen.  
Cross (?) (button 0) to left click.  
Circle (?) (button 1) to right click.  

#### On screen keyboard controls  
Hold L2? (axis 4) to bring up the on-screen keyboard as the blue highlight cursor.  
Hold R2? (axis 5) to bring up the on-screen keyboard as the red highlight cursor.  
Hold either of them at any time to activate the other highlight cursor.  

Left analogue stick? (axis 0,1) to move the blue highlight cursor.  
Right analogue stick? (axis 2,3) to move the red highlight cursor.  

L1? (button 9) to press/hold the blue highlighted key.  
R1? (button 10) to press/hold the red highlighted key.  

All/most keys can be currently held down and it seems like all secondary symbols are functional.  

## Updates  
    Improved initial license disclaimer.
    Created an entire --help menu with -h alias, also --version and -v.
    Added command options parsing.
    Added GPL3 to the AppImage.
    Altered the README.md to include information about installing dependencies and downloading the AppImage.
    Cleaned up a duplicated close_osk definition.
    Added license file and release note link for python-six library.
    Bundled the script into a standalone AppImage. Hope it works, tested working on a Debian live VM.
    Removed dependency on Xlib, and everything that depends on.
    The user can now click and hold keys on the osk with a real hardware mouse, like a real osk.
    When the two different coloured highlight selectors are on the same cell they are a mixed colour.
    Fixed a bug where a key held down would persist after the osk closes.
    Corrected right and left window scrolling with the right joystick.
    Added a complete and functional secondary red highlight on the osk menu.
    Added functional osk secondary key actions, such as uppercase letters and number row symbols.
    Edited the description in the license section of the script, includes directions.
    All python imports changed to from imports to reduce overhead.
    Resize and reorganize layout, specifically left/right shift, and space.
    Working osk button holding.
    Functional primary key presses.
    Improved navigatable multicell keys like spacebar or enter.
    Better movement from multicell keys.
    Actually select keys using gamepad button 9 (L1).
    Fixed some silly newlines in the first README.md.
    GPL3 licence compliance.
    README.md creation.

## Updates Queue  
    More than likely going to add a third green highlight for the keyboard, the directional pad and cross.
    Key repeat doesn't seem to work for certain keys while holding in the osk.
    It might be better to use L1 as left click in mouse mode.
    Keyboard media keys.
    Create a better and more informative README.md.
    On the fly SDL2 hardware remapping, for other gamepads besides a DS3.
    IDK I'll think of things later...

## Disclaimer  
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
