#!/usr/bin/env python3
#
## This Python 3 script allows the user to control mouse input with the gamepad joystick axis.
## ONLY tested and configured for an old "Playstation (DS3) controller" connected through bluetooth.
## There is also a custom on-screen keyboard to use by holding down L2.
## L2 might not be L2 for anyone else but me.
## GamepadKeyMouse to turn your gamepad into an effective mouse and keyboard.
#
# Copyright (C) 2025 GitHub.com/Zeph53
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


print("""
This program comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it under certain conditions.
See https://www.gnu.org/licenses/gpl-3.0.html for more details.
""")


import sys, time, sdl2, tkinter as tk 
from tkinter import Toplevel
from Xlib import X, XK
from Xlib.ext import xtest
from Xlib.display import Display
from pynput.keyboard import Controller as KeyboardController, Key


# Configuration constants
DEADZONE = 8192
EXEMPT_AXES = {4, 5}
AXIS_STATE = {i: 0 for i in range(6)}


# Display for X input
disp = Display()
root = disp.screen().root
g = root.get_geometry()
sw, sh = g.width, g.height


# Mouse settings
MAX_SPEED = 20
FRAME_DELAY = 16
dx_accum = 0.0
dy_accum = 0.0
scroll_accum = 0.0


# On-screen keyboard globals
osk_window = None
menu_buttons = []
menu_cursor_x = 0
menu_cursor_y = 0
MENU_SPEED = 1.5
NAVIGATION_DELAY = 0.1
last_move_time = 0
prev_focus = None
prev_revert = None
keyboard = KeyboardController()


# Utility functions
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
    nx = min(max(0, int(pos.root_x + dx)), sw - 1)
    ny = min(max(0, int(pos.root_y + dy)), sh - 1)
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
    print("\n")


def open_osk():
    global osk_window, menu_buttons, menu_cursor_x, menu_cursor_y, last_move_time, prev_focus, prev_revert
    reply = disp.get_input_focus()
    prev_focus = reply.focus
    prev_revert = reply.revert_to
    if osk_window is not None:
        return

    osk_window = Toplevel()
    osk_window.title("OSK Menu")
    osk_window.overrideredirect(True)
    osk_window.wm_attributes("-alpha", 0.95)
    osk_window.attributes("-topmost", True)
    osk_window.lift()
    osk_window.configure(bg="black", highlightthickness=0, bd=0)

    screen_w = osk_window.winfo_screenwidth()
    screen_h = osk_window.winfo_screenheight()
    win_w, win_h = 1400, 350
    x_pos = (screen_w // 2) - (win_w // 2)
    y_pos = screen_h - win_h
    osk_window.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")

    qwerty = [
        ["Esc","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","Empty","Empty","Print\nScreen","Scroll\nLock","Pause\nBreak"],
        ["Empty"]*18,
        ["~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6","&\n7","*\n8","(\n9",")\n0","_\n-","+\n=","Back\nSpace","Empty","Insert","Home","Page\nUp"],
        ["Tab","Q","W","E","R","T","Y","U","I","O","P","{\n[","}\n]","|\n\\","Empty","Delete","End","Page\nDown"],
        ["Caps\nLock","A","S","D","F","G","H","J","K","L",":\n;","\"\n'","Enter","Enter","Empty","Empty","Empty","Empty"],
        ["L-Shift","L-Shift","Z","X","C","V","B","N","M","<\n,",">\n.","?\n/","R-Shift","R-Shift","Empty","Empty","Up","Empty"],
        ["L-Ctrl","L-Super","Fn","L-Alt","Space","Space","Space","Space","Space","Space","R-Alt","R-Super","Menu","R-Ctrl","Empty","Left","Down","Right"]
    ]

    menu_buttons = []
    for r, row in enumerate(qwerty):
        btn_row = []
        c = 0
        while c < len(row):
            key = row[c]
            if key == "Empty":
                spacer = tk.Label(osk_window, text="", width=6, height=2, bg="black", relief="flat")
                spacer.grid(row=r, column=c, sticky="nsew")
                spacer.grid_remove()
                btn_row.append(None)
                c += 1
            elif key == "Space":
                btn = tk.Button(osk_window, text="Space", width=24, height=2,
                               bg="gray", fg="white", relief="raised", font=("Arial",12))
                btn.grid(row=r, column=c, columnspan=6, sticky="nsew")
                btn_row.extend([btn]*6)
                c += 6
            elif key in ("Enter","L-Shift","R-Shift"):
                span = 2
                btn = tk.Button(osk_window, text=key, width=12, height=2,
                               bg="gray", fg="white", relief="raised", font=("Arial",12))
                btn.grid(row=r, column=c, columnspan=span, sticky="nsew")
                btn_row.extend([btn]*span)
                c += span
            else:
                btn = tk.Button(osk_window, text=key, width=6, height=2,
                               bg="gray", fg="white", relief="raised", font=("Arial",12))
                btn.grid(row=r, column=c, sticky="nsew")
                btn_row.append(btn)
                c += 1
        menu_buttons.append(btn_row)

    for i in range(len(menu_buttons)):
        osk_window.grid_rowconfigure(i, weight=1, uniform="r")
    for j in range(max(len(r) for r in menu_buttons)):
        osk_window.grid_columnconfigure(j, weight=1, uniform="c")

    disp.set_input_focus(prev_focus, prev_revert, X.CurrentTime)
    disp.sync()
    highlight_button(menu_cursor_x, menu_cursor_y)


# Close OSK function
def close_osk():
    global osk_window, prev_focus, prev_revert, menu_cursor_x, menu_cursor_y
    if osk_window:
        menu_cursor_x, menu_cursor_y = get_cursor_position()
        disp.set_input_focus(prev_focus, prev_revert, X.CurrentTime)
        disp.sync()
        osk_window.destroy()
        osk_window = None


def get_cursor_position():
    return menu_cursor_x, menu_cursor_y


def highlight_button(x, y):
    for r, row in enumerate(menu_buttons):
        for c, btn in enumerate(row):
            if btn:
                btn.configure(bg="gray")
    if 0 <= y < len(menu_buttons) and 0 <= x < len(menu_buttons[y]):
        btn = menu_buttons[y][x]
        if btn:
            btn.configure(bg="blue")


# Navigation logic
def navigate_menu(x_axis, y_axis):
    global menu_cursor_x, menu_cursor_y, last_move_time
    now = time.time()
    if now - last_move_time < NAVIGATION_DELAY:
        return

    dx = 0
    if x_axis > 0.3:
        dx = 1
    elif x_axis < -0.3:
        dx = -1

    dy = 0
    if y_axis > 0.3:
        dy = 1
    elif y_axis < -0.3:
        dy = -1

    x0, y0 = menu_cursor_x, menu_cursor_y
    new_x, new_y = x0, y0

    def is_valid(nx, ny):
        if ny < 0 or ny >= len(menu_buttons):
            return False
        row = menu_buttons[ny]
        if nx < 0 or nx >= len(row):
            return False
        return row[nx] is not None and row[nx].cget("text") != "Empty"
    # Handle diagonal movement
    if dx != 0 and dy != 0:
        for k in range(1, 10):
            nx = x0 + k * dx
            ny = y0 + k * dy
            if is_valid(nx, ny):
                new_x, new_y = nx, ny
                break
        else:
            # if diagonal fails, check horizontal and vertical independently
            for k in range(1, 10):
                nx = x0 + k * dx
                if is_valid(nx, y0):
                    new_x = nx
                    break
            for k in range(1, 10):
                ny = y0 + k * dy
                if is_valid(x0, ny):
                    new_y = ny
                    break
    else:
        # Handle horizontal movement
        if dx != 0:
            for k in range(1, 10):
                nx = x0 + k * dx
                if is_valid(nx, y0):
                    new_x = nx
                    break
        # Handle vertical movement
        if dy != 0:
            for k in range(1, 10):
                ny = y0 + k * dy
                if is_valid(x0, ny):
                    new_y = ny
                    break
    if (new_x, new_y) != (x0, y0):
        menu_cursor_x, menu_cursor_y = new_x, new_y
        highlight_button(menu_cursor_x, menu_cursor_y)
        last_move_time = now


def press_menu_button_down():
    global prev_focus, prev_revert, pressed_osk_key
    x, y = menu_cursor_x, menu_cursor_y
    if not (0 <= y < len(menu_buttons) and 0 <= x < len(menu_buttons[y]) and menu_buttons[y][x]):
        return

    raw_label = menu_buttons[y][x]['text']
    lines = raw_label.split("\n")
    if len(lines) == 2:
        top = lines[0].strip().lower()
        bottom = lines[1].strip().lower()
        label = bottom if len(bottom) == 1 else (top + bottom)
    else:
        label = raw_label.strip().lower().replace(" ", "")

    key_map = {
        "enter": Key.enter, "space": Key.space, "tab": Key.tab,
        "backspace": Key.backspace, "esc": Key.esc, "menu": Key.menu,

        "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,

        "printscreen": Key.print_screen, "pausebreak": Key.pause,
        "insert": Key.insert, "home": Key.home, "delete": Key.delete,
        "end": Key.end, "pageup": Key.page_up, "pagedown": Key.page_down,

        "l-shift": Key.shift, "r-shift": Key.shift_r,
        "l-ctrl": Key.ctrl, "r-ctrl": Key.ctrl_r,
        "l-alt": Key.alt, "r-alt": Key.alt_r,
        "l-super": Key.cmd,"r-super": Key.cmd_r,

        "capslock": Key.caps_lock, "scrolllock": Key.scroll_lock
    }

    if label.startswith("f") and label[1:].isdigit():
        actual_key = getattr(Key, label, None)
    elif label in key_map:
        actual_key = key_map[label]
    elif len(label) == 1:
        actual_key = label
    else:
        return

    pressed_osk_key = actual_key
    keyboard.press(actual_key)
    disp.set_input_focus(prev_focus, prev_revert, X.CurrentTime)
    disp.sync()


def press_menu_button_up():
    global pressed_osk_key
    if pressed_osk_key:
        keyboard.release(pressed_osk_key)
        pressed_osk_key = None
        disp.set_input_focus(prev_focus, prev_revert, X.CurrentTime)
        disp.sync()


# Main loop
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
                    axis = evt.caxis.axis
                    v = apply_deadzone(axis, evt.caxis.value)
                    if AXIS_STATE[axis] != v:
                        AXIS_STATE[axis] = v
                        updated = True

                elif evt.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                    b = evt.cbutton.button
                    print(f"Button {b} pressed")
                    try:
                        if osk_window:
                            if b == 9:
                                press_menu_button_down()
                        else:
                            if b == 0:
                                send_click(1, True)
                            elif b == 1:
                                send_click(3, True)
                    except Exception as e:
                        print(f"Error handling button press {b}: {e}", file=sys.stderr)

                elif evt.type == sdl2.SDL_CONTROLLERBUTTONUP:
                    b = evt.cbutton.button
                    print(f"Button {b} released")
                    try:
                        if osk_window:
                            if b == 9:
                                press_menu_button_up()
                        else:
                            if b == 0:
                                send_click(1, False)
                            elif b == 1:
                                send_click(3, False)
                    except Exception as e:
                        print(f"Error handling button release {b}: {e}", file=sys.stderr)

            if AXIS_STATE[4] > 0:
                if osk_window is None:
                    open_osk()
                navigate_menu(AXIS_STATE[0]/32767, AXIS_STATE[1]/32767)
            else:
                if osk_window:
                    close_osk()
                x = AXIS_STATE[0]/32767
                y = AXIS_STATE[1]/32767
                dx_accum += x * MAX_SPEED
                dy_accum += y * MAX_SPEED
                scroll_accum += AXIS_STATE[3]/-32768
                mx, my = int(dx_accum), int(dy_accum)
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


if __name__ == "__main__":
    main()
