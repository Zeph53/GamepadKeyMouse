# GAMEPADKEYMOUSE.PY
This is a Python3 script that allows the user to move the mouse cursor around with a gamepad's joystick. As well as the right and left click. Also, the ability to open an on-screen keyboard that is navigatable with the joystick.  

Currently, the on-screen keyboard is nearly entirely functional, can't use the secondary symbols yet. Mouse cursor works but it's slightly janky still.  

ChatGPT is completely responsible for this. I primarily created this so I could sit back and do some sort of text development using my gamepad.  

## Requirements  
    Gamepad, script tested and configured ONLY using an oldschool "Playstation (DS3) Controller" connected through bluetooth.
    Debian with XFCE4
    Python3
    A whole lot of Python3 modules, SDL2 specifically, and pynput
    IDK I'll figure it all out later...

## Usage  
Simply open a terminal and execute the script.  
Debug information such as button and axis inputs will be displayed.  

#### Mouse controls
Left analogue stick (?) (axis 0,1) to move the mouse cursor around the screen.  
Cross (?) (button 0) to left click.  
Circle (?) (button 1) to right click.

#### On screen keyboard controls
Hold L2 (?) (axis 4) to bring up the on-screen keyboard.  
Left analogue stick (?) (axis 0,1) to navigate the on-screen keyboard.  
L1 (?) (button 9) to select or hold a key.  

All keys seem to have functional primary actions. However the secondary actions, such as symbols, do not work yet.

## Updates
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
    Key repeat doesn't seem to work while holding a key in the osk.
    It might be better to use L1 as left click in mouse mode.
    Package script as an AppImage, to include all of those dependencies. Tested - functional.
    Use right stick and R1 for secondary highlight selection with the OSK open.
    Keyboard media keys.
    Create a better and more informative README.md.
    Informative GPL3 comliance within script.
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
