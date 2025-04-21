#!/usr/bin/env python3
#
## This Python 3 script allows the user to control mouse input with the gamepad joystick axis.
## ONLY tested and configured for an old "Playstation (DS3) controller" connected through bluetooth.
## There is also a custom on-screen keyboard to use by holding down L2.
## L2 might not be L2 for anyone else but me.
## I hardly know how to use Python so ChatGPT did 99 percent of this wizardry.
#
#
#
#
#    GamepadKeyMouse to turn your gamepad into an effective mouse and keyboard.
#    Copyright (C) 2025 GitHub.com/Zeph53
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
#
#
## Disclaimer GNU General Public License v3.0 (gpl-3.0)
print("""
This program comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it under certain conditions.
See https://www.gnu.org/licenses/gpl-3.0.html for more details.
""")

import sdl2
import tkinter as tk
import subprocess
from tkinter import Toplevel
from Xlib.display import Display
from Xlib import X
from Xlib.ext import xtest
import sys

DEADZONE = 8192
EXEMPT_AXES = {4, 5}
AXIS_STATE = {i: 0 for i in range(6)}

disp = Display()
root = disp.screen().root
g = root.get_geometry()
sw, sh = g.width, g.height

MAX_SPEED = 20
FRAME_DELAY = 16

dx_accum = 0.0
dy_accum = 0.0
scroll_accum = 0.0

osk_window = None
menu_cursor_x = 0
menu_cursor_y = 0
menu_buttons = []
MENU_SPEED = 1.5

def apply_deadzone(axis, v):
    if axis in EXEMPT_AXES:
        return v
    if abs(v) <= DEADZONE:
        return 0
    scaled = (abs(v) - DEADZONE) / (32767 - DEADZONE)
    scaled *= 32767
    return int(scaled if v > 0 else -scaled)

def send_click(btn, down):
    xtest.fake_input(disp, X.ButtonPress if down else X.ButtonRelease, btn)
    disp.sync()

def move_cursor(dx, dy):
    pos = root.query_pointer()
    nx = min(max(0, pos.root_x + dx), sw - 1)
    ny = min(max(0, pos.root_y + dy), sh - 1)
    root.warp_pointer(nx, ny)
    disp.sync()

def send_scroll(dx, dy):
    if dy != 0:
        xtest.fake_input(disp, X.ButtonPress, 4 if dy > 0 else 5)
        xtest.fake_input(disp, X.ButtonRelease, 4 if dy > 0 else 5)
    if dx != 0:
        xtest.fake_input(disp, X.ButtonPress, 6 if dx > 0 else 7)
        xtest.fake_input(disp, X.ButtonRelease, 6 if dx > 0 else 7)
    disp.sync()

def print_axis_state():
    line = " | ".join(f"A{a}:{AXIS_STATE[a]:>6}" for a in sorted(AXIS_STATE))
    sys.stdout.write("\r" + line)
    sys.stdout.flush()

def open_osk():
    global osk_window, menu_buttons, menu_cursor_x, menu_cursor_y

    if osk_window is not None:
        return

    osk_window = Toplevel()
    osk_window.title("OSK Menu")

    # Get screen width and height from the root window
    screen_width = osk_window.winfo_screenwidth()
    screen_height = osk_window.winfo_screenheight()

    # Define the desired width and height of the OSK window
    window_width = 1400
    window_height = 350

    # Calculate the position (bottom center of the screen)
    x_position = (screen_width // 2) - (window_width // 2)
    y_position = screen_height - window_height

    # Set the geometry of the window with the calculated position
    osk_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    osk_window.configure(bg="black")

    qwerty_keys = [
        ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "Empty", "Empty", "Print\nScreen", "Scroll\nLock", "Pause\nBreak"],
        ["Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty", "Empty"],
        ["~\n`", "!\n1", "@\n2", "#\n3", "$\n4", "%\n5", "^\n6", "&\n7", "*\n8", "(\n9", ")\n0", "_\n-", "+\n=", "Back\nSpace", "Empty", "Insert", "Home", "Page\nUp"],
        ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "{\n[", "}\n]", "|\n\\", "Empty", "Delete", "End", "Page\nDown"],
        ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ":\n;", "\"\n'", "Enter", "Empty", "Empty", "Empty", "Empty", "Empty"],
        ["Shift", "Z", "X", "C", "V", "B", "N", "M", "<\n,", ">\n.", "?\n/", "Shift", "Empty", "Empty", "Empty", "Empty", "Up", "Empty"],
        ["Ctrl", "Win", "Fn", "Alt", "Space", "Space", "Space", "Space", "Alt", "Fn", "Menu", "Ctrl", "Empty", "Empty", "Empty", "Left", "Down", "Right"]
    ]

    menu_buttons = []
    for i, row in enumerate(qwerty_keys):
        button_row = []
        col = 0
        while col < len(row):
            key = row[col]
            if key == "Empty":
                # Set fixed size for empty space to match buttons, ensure it's black
                spacer = tk.Label(osk_window, text="", width=6, height=2, bg="black", relief="flat")
                spacer.grid(row=i, column=col, padx=0, pady=0, sticky="nsew")
                spacer.grid_remove()  # Remove it from the focus cycle (not navigable)
                button_row.append(None)  # Use None to mark empty space, no button
                col += 1
            elif key == "Space" and col + 3 < len(row) and all(k == "Space" for k in row[col:col+4]):
                # Space bar spanning 4 columns
                btn = tk.Button(osk_window, text="Space", width=6 * 4, height=2, bg="gray", fg="white", relief="raised", font=("Arial", 12))
                btn.grid(row=i, column=col, columnspan=4, padx=3, pady=3, sticky="nsew")
                button_row.extend([btn, None, None, None])  # Extend button row with 4 columns for space
                col += 4
            elif key == "Enter":
                btn = tk.Button(osk_window, text="Enter", width=6 * 2, height=2, bg="gray", fg="white", relief="raised", font=("Arial", 12))
                btn.grid(row=i, column=col, columnspan=2, padx=3, pady=3, sticky="nsew")
                button_row.extend([btn, None])
                col += 2
            else:
                btn = tk.Button(osk_window, text=key, width=6, height=2, bg="gray", fg="white", relief="raised", font=("Arial", 12))
                btn.grid(row=i, column=col, padx=3, pady=3, sticky="nsew")
                button_row.append(btn)
                col += 1
        menu_buttons.append(button_row)

    # Ensure the grid is reconfigured after the buttons are added
    for i in range(len(qwerty_keys)):
        osk_window.grid_rowconfigure(i, weight=1, uniform="equal")
    for i in range(max(len(r) for r in menu_buttons)):
        osk_window.grid_columnconfigure(i, weight=1, uniform="equal")

    # Ensure we are not calling max() on an empty list
    if menu_buttons:
        highlight_button(0, 0)  # Highlight the first button if the menu is populated
    else:
        print("Error: Menu buttons are not populated correctly.")





def close_osk():
    global osk_window
    if osk_window:
        osk_window.destroy()
        osk_window = None

def highlight_button(x, y):
    # Ensure that the highlight is properly handled even when rows and columns are not fixed
    for i in range(len(menu_buttons)):
        for j in range(len(menu_buttons[i])):
            btn = menu_buttons[i][j]
            if btn:  # Only highlight valid buttons
                btn.configure(bg="gray")
    
    # Check if the button exists before highlighting it
    if 0 <= y < len(menu_buttons) and 0 <= x < len(menu_buttons[y]) and menu_buttons[y][x]:
        menu_buttons[y][x].configure(bg="blue")

from time import time, sleep  # Importing sleep and time from time module

# Global variable to track the last movement time
last_move_time = 0
last_move_origin = 0
NAVIGATION_DELAY = 0.075  # Delay in seconds (e.g., 200ms)

def navigate_menu(x_axis, y_axis):
    global menu_cursor_x, menu_cursor_y, last_move_time, last_move_origin

    current_time = time()
    if current_time - last_move_time < NAVIGATION_DELAY:
        return

    dx = int(x_axis * MENU_SPEED) if abs(x_axis) > 0.3 else 0
    dy = int(y_axis * MENU_SPEED) if abs(y_axis) > 0.3 else 0

    new_x = menu_cursor_x
    new_y = menu_cursor_y

    # Track origin of movement to handle return behavior (only necessary for special keys)
    origin_x = menu_cursor_x
    origin_y = menu_cursor_y

    # If we're entering a multi-cell key like Space or Enter, track the exact origin cell
    if menu_buttons[origin_y][origin_x] and menu_buttons[origin_y][origin_x].cget("text") in ("Space", "Enter"):
        last_move_origin = (origin_x, origin_y)

    # Handle horizontal movement (left/right)
    if dx != 0:
        tx = new_x
        while True:
            tx += dx
            if tx < 0 or tx >= len(menu_buttons[new_y]):
                break
            btn = menu_buttons[new_y][tx]
            if btn and btn.cget("text") != "Empty":  # Ensure button is not "Empty"
                new_x = tx
                break

    # Handle vertical movement (up/down)
    if dy != 0:
        ty = new_y
        while True:
            ty += dy
            if ty < 0 or ty >= len(menu_buttons):
                break
            row = menu_buttons[ty]
            if new_x < len(row):
                btn = row[new_x]
                if btn and btn.cget("text") != "Empty":  # Button must be valid
                    new_y = ty
                    break
                elif btn is None:
                    # Check for multi-column buttons like Space or Enter
                    for offset in range(-3, 1):  # range(-3, 1) to check left and right columns
                        cx = new_x + offset
                        if 0 <= cx < len(row):
                            check_btn = row[cx]
                            if check_btn and check_btn.cget("text") in ("Enter", "Space"):
                                new_y = ty
                                new_x = cx
                                break
                    else:
                        continue
                    break

        # Special case: when moving up to multi-column buttons like Enter/Space, return to the original position
        if dy < 0 and menu_buttons[new_y][new_x] is not None and menu_buttons[new_y][new_x].cget("text") in ("Enter", "Space"):
            # Ensure we return to the origin cell inside the multi-column button
            if last_move_origin and (origin_y != new_y or origin_x != new_x):
                new_y, new_x = last_move_origin

    # Ensure the new position is within bounds
    if 0 <= new_y < len(menu_buttons) and 0 <= new_x < len(menu_buttons[new_y]):
        menu_cursor_x = new_x
        menu_cursor_y = new_y
        highlight_button(menu_cursor_x, menu_cursor_y)
        last_move_time = current_time






def press_menu_button():
    btn = menu_buttons[menu_cursor_y][menu_cursor_x]
    if btn:  # Only press valid buttons
        char = btn["text"]
        subprocess.Popen(["xdotool", "type", char])

def main():
    global dx_accum, dy_accum, scroll_accum

    sdl2.SDL_Init(sdl2.SDL_INIT_GAMECONTROLLER)
    controller = None
    for i in range(sdl2.SDL_NumJoysticks()):
        if sdl2.SDL_IsGameController(i):
            controller = sdl2.SDL_GameControllerOpen(i)
            break
    if not controller:
        print("No controller found")
        return

    sdl2.SDL_GameControllerEventState(sdl2.SDL_ENABLE)
    evt = sdl2.SDL_Event()

    root_tk = tk.Tk()
    root_tk.withdraw()

    print("Monitoring PS3 gamepad input (Press Ctrl+C to quit)")
    print_axis_state()

    try:
        while True:
            updated = False
            while sdl2.SDL_PollEvent(evt):
                if evt.type == sdl2.SDL_CONTROLLERAXISMOTION:
                    a = evt.caxis.axis
                    v = apply_deadzone(a, evt.caxis.value)
                    if AXIS_STATE[a] != v:
                        AXIS_STATE[a] = v
                        updated = True
                elif evt.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                    b = evt.cbutton.button
                    print(f"\n[BUTTON DOWN] {b}")
                    if b == 0: send_click(1, True)
                    elif b == 1: send_click(3, True)
                    elif b == 2 and osk_window: press_menu_button()
                elif evt.type == sdl2.SDL_CONTROLLERBUTTONUP:
                    b = evt.cbutton.button
                    print(f"\n[BUTTON UP] {b}")
                    if b == 0: send_click(1, False)
                    elif b == 1: send_click(3, False)

            if AXIS_STATE[4] > 0:
                if osk_window is None:
                    open_osk()
                navigate_menu(AXIS_STATE[0] / 32767.0, AXIS_STATE[1] / 32767.0)
            else:
                if osk_window:
                    close_osk()
                x = AXIS_STATE[0] / 32767.0
                y = AXIS_STATE[1] / 32767.0
                dx_accum += x * MAX_SPEED
                dy_accum += y * MAX_SPEED

                scroll_accum += AXIS_STATE[3] / -32768.0

                mx = int(dx_accum)
                my = int(dy_accum)
                dx_accum -= mx
                dy_accum -= my

                if scroll_accum >= 0.5:
                    send_scroll(0, 1)
                    scroll_accum -= 1
                elif scroll_accum <= -0.5:
                    send_scroll(0, -1)
                    scroll_accum += 1

                if mx or my:
                    move_cursor(mx, my)
                    updated = True

            if updated:
                print_axis_state()

            sdl2.SDL_Delay(FRAME_DELAY)
            root_tk.update()

    except KeyboardInterrupt:
        pass
    finally:
        if controller:
            sdl2.SDL_GameControllerClose(controller)
        sdl2.SDL_Quit()
        print("""\n""")

if __name__ == "__main__":
    main()
