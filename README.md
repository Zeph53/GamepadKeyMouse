# GAMEPADKEYMOUSE.PY
This is a Python3 script that allows the user to move the mouse cursor around with a gamepad's joystick. As well as the right and left click. Also, the ability to open an on-screen keyboard that is navigatable with the joysticks.  

Currently, the on-screen keyboard is nearly entirely functional, can use all, if not, most of the secondary symbols. Mouse cursor works but it's slightly janky still.  

ChatGPT is completely responsible for this. I primarily created this so I could sit back and do some sort of text development using my gamepad.  

## Requirements  
    Gamepad, script tested and configured ONLY using an oldschool "Playstation (DS3) Controller" connected through bluetooth.
    Debian with XFCE4
    Python3
    A whole lot of Python3 modules, SDL2 specifically, and pynput

## Usage  
#### Simply open a terminal and execute the script.  
    python3 ~/GamepadKeyMouse/gamepadkeymouse.py
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

All keys can be currently held down and it seems like all secondary symbols are functional.

## Updates
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
    Key repeat doesn't seem to work for certain keys while holding in the osk.
    It might be better to use L1 as left click in mouse mode.
    Package script as an AppImage, to include all of those dependencies. Tested - functional.
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
