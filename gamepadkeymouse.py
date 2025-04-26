#!/usr/bin/env python3
#
## This Python 3 script allows the user to control mouse/keyboard input with a "Playstation (DS3) Controller".
## ONLY tested and configured for an old "Playstation (DS3) controller" connected through bluetooth.
## There is also a custom on-screen keyboard used with the DS3 analogue sticks.
## Button and axis assignments may not be functional for anyone besides me.
##
## The mouse input is currently controlled with the "left analogue stick (axis 0, 1)".
## Left click is "cross (button 0)". Right click is "circle (button 1)".
## 
## The on-screen keyboard can be opened by holding either "L2 (axis 4)" or "R2 (axis 5)".
## While holding "L2 (axis 4)" you can use the "left analogue stick (axis 0, 1)" to navigate the blue cursor.
## While holding "R2 (axis 5)" you can use the "right analogue stick (axis 2, 3)" to navigate the red cursor.
## You can also hold both "L2 (axis 4)" or "R2 (axis 5)" at the same time and seamlessly navigate with both.
## To select/hold with the blue cursor is "L1 (button 9)".
## To select/hold with the red cursor is "R1 (button 10)".
##
## The user can also use a real hardware mouse to click and hold items with the on-screen keyboard.
## I believe all symbols and other keys work. At least 90 percent functional now.
#
#
#
#
# GamepadKeyMouse to turn your gamepad into an effective mouse and keyboard.
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

from argparse import ArgumentParser, RawTextHelpFormatter
from sys import stdout, stderr
from time import time
from sdl2 import (
    SDL_Init, SDL_Quit, SDL_Delay, SDL_Event, SDL_NumJoysticks,
    SDL_IsGameController, SDL_GameControllerOpen, SDL_GameControllerClose,
    SDL_GameControllerEventState, SDL_PollEvent,
    SDL_ENABLE, SDL_INIT_GAMECONTROLLER,
    SDL_CONTROLLERAXISMOTION, SDL_CONTROLLERBUTTONDOWN, SDL_CONTROLLERBUTTONUP
)
from tkinter import Toplevel, Label, Button, Tk
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button as MouseButton

def print_disclaimer():
    print("""This program comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to 
redistribute it under certain conditions. """)

def print_version():
    print("""GamepadKeyMouse_0.1.91 """)

def print_help():
    print("""Control mouse and keyboard using a Playstation (DS3) controller. 

Usage: python3 "gamepadkeymouse.py" [-h] [-v]

Options:
  --help, [-h]                        Display this help menu and then exit 
  --version, [-v]                     Display the current version and then exit 

Default mouse controls: 
  Left joystick (axis 0, 1)           Cursor movement 
  Cross (button 0)                    Left click 
  Circle (button 1)                   Right click 

Default keyboard controls: 
  Hold L2/R2 (axis 4/5)               Open the on-screen keyboard 
  Left analog stick (axis 0, 1)       Blue highlight movement 
  Right analog stick (axis 2, 3)      Red highlight movement 
  L1/R1 (button 9/10)                 Key press with blue/red highlight 

GamepadKeyMouse 
Copyright (C) 2025 GitHub.com/Zeph53 
This program comes with ABSOLUTELY NO WARRANTY! 
This is free software, and you are welcome to 
redistribute it under certain conditions. 
See \"https://www.gnu.org/licenses/gpl-3.0.txt\" """)

def parse_arguments():
    parser = ArgumentParser(
        add_help=False
    )
    parser._optionals.title = "Options"
    parser.add_argument("-h", "--help", action="store_true", help="Show this message and exit. ")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information and exit. ")
    return parser.parse_args()
args = parse_arguments()

if args.help:
    print_help()
    exit(0)

if args.version:
    print_disclaimer()
    print()
    print_version()
    exit(0)

if args:
    print_disclaimer()
    print()

mouse = MouseController()
keyboard = KeyboardController()

DEADZONE = 8192
EXEMPT_AXES = {4, 5}
AXIS_STATE = {i: 0 for i in range(6)}
dx_accum = dy_accum = ver_scroll_accum = hor_scroll_accum = 0.0

MAX_SPEED = 20
FRAME_DELAY = 16

osk_window = None
menu_buttons = []

blue_x = blue_y = red_x = red_y = 0
last_move_blue = last_move_red = 0
NAV_DELAY = 0.1

pressed_blue = None
pressed_red = None
pressed_mouse = {}

prev_focus = prev_revert = None

def apply_deadzone(axis, v):
    if axis in EXEMPT_AXES:
        return v
    if abs(v) <= DEADZONE:
        return 0
    scaled = (abs(v) - DEADZONE) / (32767 - DEADZONE) * 32767
    return int(scaled if v > 0 else -scaled)

def send_click(btn, down):
    if btn == 1:
        if down:
            mouse.press(MouseButton.left)
        else:
            mouse.release(MouseButton.left)
    elif btn == 3:
        if down:
            mouse.press(MouseButton.right)
        else:
            mouse.release(MouseButton.right)

def move_cursor(dx, dy):
    mouse.move(int(dx), int(dy))

def send_scroll(dx, dy):
    if dx:
        mouse.scroll(int(dx), 0)
    if dy:
        mouse.scroll(0, int(dy))

def print_axis_state():
    line = " | ".join(f"A{a}:{AXIS_STATE[a]:>6}" for a in sorted(AXIS_STATE))
    stdout.write("\r" + line)
    stdout.flush()

def set_focus(window):
    window.focus_force()
    window.lift()

def open_osk():
    global osk_window, menu_buttons
    if osk_window:
        return

    osk_window = Toplevel()
    osk_window.overrideredirect(True)
    osk_window.wm_attributes("-alpha", 0.95)
    osk_window.configure(bg="black", highlightthickness=0, bd=0)
    win_w, win_h = 1400, 350
    x_pos = (osk_window.winfo_screenwidth() // 2) - (win_w // 2)
    y_pos = osk_window.winfo_screenheight() - win_h
    osk_window.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")
    set_focus(osk_window)

    qwerty = [
        ["Esc","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","Empty","Empty","Print\nScreen","Scroll\nLock","Pause\nBreak"],
        ["Empty"]*18,
        ["~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6","&\n7","*\n8","(\n9"," )\n0","_\n-","+\n=","Back\nSpace","Empty","Insert","Home","Page\nUp"],
        ["Tab","Q","W","E","R","T","Y","U","I","O","P","{\n[","}\n]","|\n\\","Empty","Delete","End","Page\nDown"],
        ["Caps\nLock","A","S","D","F","G","H","J","K","L",":\n;","\"\n\'","Enter","Enter","Empty","Empty","Empty","Empty"],
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
                spacer = Label(osk_window, text="", width=6, height=2, bg="black")
                spacer.grid(row=r, column=c)
                spacer.grid_remove()
                btn_row.append(None)
                c += 1
            elif key == "Space":
                btn = Button(osk_window, text="Space", width=24, height=2, bg="gray", fg="white", relief="raised", font=("Arial", 12))
                btn.grid(row=r, column=c, columnspan=6, sticky="nsew")
                btn_row += [btn]*6
                c += 6
            elif key in ("Enter","L-Shift","R-Shift"):
                span = 2
                btn = Button(osk_window, text=key, width=12, height=2, bg="gray", fg="white", relief="raised", font=("Arial", 12))
                btn.grid(row=r, column=c, columnspan=span, sticky="nsew")
                btn_row += [btn]*span
                c += span
            else:
                btn = Button(osk_window, text=key, width=6, height=2, bg="gray", fg="white", relief="raised", font=("Arial", 12))
                btn.grid(row=r, column=c, sticky="nsew")
                btn_row.append(btn)
                c += 1
        menu_buttons.append(btn_row)

    for y, row in enumerate(menu_buttons):
        for x, btn in enumerate(row):
            if btn:
                btn.bind("<ButtonPress-1>", lambda e, x=x, y=y: on_mouse_press(e, x, y))
                btn.bind("<ButtonRelease-1>", lambda e, x=x, y=y: on_mouse_release(e, x, y))

    for i in range(len(menu_buttons)):
        osk_window.grid_rowconfigure(i, weight=1, uniform="r")
    for j in range(max(len(r) for r in menu_buttons)):
        osk_window.grid_columnconfigure(j, weight=1, uniform="c")

def close_osk():
    global osk_window, prev_focus, prev_revert, pressed_blue, pressed_red, pressed_mouse
    if not osk_window:
        return
    # release any held OSK gamepad buttons
    if pressed_blue:
        release_button(pressed_blue)
        pressed_blue = None
    if pressed_red:
        release_button(pressed_red)
        pressed_red = None
    # release any held OSK mouse buttons
    for data in list(pressed_mouse.values()):
        if data:
            release_button(data)
    pressed_mouse.clear()
    osk_window.destroy()
    osk_window = None

def highlight_all():
    for r, row in enumerate(menu_buttons):
        for c, btn in enumerate(row):
            if btn:
                btn.configure(bg="gray")  # Default color for all buttons

    if osk_window:
        blue_open = AXIS_STATE[4] > 0
        red_open = AXIS_STATE[5] > 0
        x, y = None, None  # Initialize x, y to None
        color = None  # Ensure color is reset

        # Handle blue and red cursor states
        if blue_open or red_open:
            # If both cursors are active, handle them separately
            if blue_open:
                color = "blue"
                x, y = blue_x, blue_y
                # Ensure blue cursor highlight is set
                if 0 <= y < len(menu_buttons) and 0 <= x < len(menu_buttons[y]):
                    btn = menu_buttons[y][x]
                    if btn:
                        btn.configure(bg=color)

            if red_open:
                color = "red"
                x, y = red_x, red_y
                # Ensure red cursor highlight is set
                if 0 <= y < len(menu_buttons) and 0 <= x < len(menu_buttons[y]):
                    btn = menu_buttons[y][x]
                    if btn:
                        btn.configure(bg=color)

            # Check if both cursors are on the same cell
            if blue_open and red_open and blue_x == red_x and blue_y == red_y:
                # Set the cell to purple if both cursors are in the same position
                btn = menu_buttons[blue_y][blue_x]
                if btn:
                    btn.configure(bg="purple")

def navigate(x, y, cur_x, cur_y, last_move):
    now = time()
    if now - last_move < NAV_DELAY:
        return cur_x, cur_y, last_move
    dx = 1 if x>0.3 else -1 if x<-0.3 else 0
    dy = 1 if y>0.3 else -1 if y<-0.3 else 0
    nx, ny = cur_x, cur_y
    def valid(ix, iy):
        return 0<=iy<len(menu_buttons) and 0<=ix<len(menu_buttons[iy]) and menu_buttons[iy][ix]
    if dx and dy:
        for k in range(1,10):
            if valid(cur_x+dx*k, cur_y+dy*k):
                nx, ny = cur_x+dx*k, cur_y+dy*k
                break
    else:
        if dx:
            for k in range(1,10):
                if valid(cur_x+dx*k, cur_y):
                    nx = cur_x+dx*k
                    break
        if dy:
            for k in range(1,10):
                if valid(cur_x, cur_y+dy*k):
                    ny = cur_y+dy*k
                    break
    if (nx,ny)!=(cur_x,cur_y):
        last_move = now
    return nx, ny, last_move

def press_button(cur_x, cur_y):
    raw = menu_buttons[cur_y][cur_x]['text']
    lines = raw.split("\n")
    label = (lines[1].lower() if len(lines)==2 and len(lines[1].strip())==1 else raw.lower().replace("\n","").replace(" ",""))
    key_map = {
        "enter":Key.enter,"space":Key.space,"tab":Key.tab,"backspace":Key.backspace,
        "esc":Key.esc,"menu":Key.menu,"up":Key.up,"down":Key.down,"left":Key.left,"right":Key.right,
        "printscreen":Key.print_screen,"pausebreak":Key.pause,"insert":Key.insert,"home":Key.home,
        "delete":Key.delete,"end":Key.end,"pageup":Key.page_up,"pagedown":Key.page_down,
        "l-shift":Key.shift,"r-shift":Key.shift_r,"l-ctrl":Key.ctrl,"r-ctrl":Key.ctrl_r,
        "l-alt":Key.alt,"r-alt":Key.alt_r,"l-super":Key.cmd,"r-super":Key.cmd_r,
        "capslock":Key.caps_lock,"scrolllock":Key.scroll_lock
    }

    actual = getattr(Key, label, None) if label.startswith("f") and label[1:].isdigit() else key_map.get(label, label if len(label) == 1 else None)
    if actual:
        keyboard.press(actual)
        menu_buttons[cur_y][cur_x].configure(relief="sunken")
        return (actual, cur_x, cur_y)
    return (None, None, None)

def release_button(button_data):
    actual, cur_x, cur_y = button_data
    if actual:
        keyboard.release(actual)
    if actual is not None and 0<=cur_y<len(menu_buttons) and 0<=cur_x<len(menu_buttons[cur_y]):
        menu_buttons[cur_y][cur_x].configure(relief="raised")

def on_mouse_press(event, x, y):
    pressed_mouse[(x,y)] = press_button(x, y)

def on_mouse_release(event, x, y):
    data = pressed_mouse.pop((x,y), None)
    if data:
        release_button(data)

def main():
    global dx_accum, dy_accum, ver_scroll_accum, hor_scroll_accum
    global blue_x, blue_y, red_x, red_y, last_move_blue, last_move_red
    global pressed_blue, pressed_red
    SDL_Init(SDL_INIT_GAMECONTROLLER)
    controller = None
    for i in range(SDL_NumJoysticks()):
        if SDL_IsGameController(i):
            controller = SDL_GameControllerOpen(i)
            break
    if not controller:
        print("No controller found")
        return
    SDL_GameControllerEventState(SDL_ENABLE)
    evt = SDL_Event()
    root_Tk = Tk()
    root_Tk.withdraw()
    print("Monitoring PS3 gamepad input (Press Ctrl+C to quit)")
    print_axis_state()
    try:
        while True:
            updated = False
            while SDL_PollEvent(evt):
                if evt.type == SDL_CONTROLLERAXISMOTION:
                    a = evt.caxis.axis
                    v = apply_deadzone(a, evt.caxis.value)
                    if AXIS_STATE[a] != v:
                        AXIS_STATE[a] = v
                        updated = True
                elif evt.type == SDL_CONTROLLERBUTTONDOWN:
                    b = evt.cbutton.button
                    print(f"\nButton {b} DOWN")
                    if osk_window:
                        if b == 9 and AXIS_STATE[4] > 0:
                            pressed_blue = press_button(blue_x, blue_y)
                        elif b == 10 and AXIS_STATE[5] > 0:
                            pressed_red = press_button(red_x, red_y)
                    else:
                        if b == 0:
                            send_click(1, True)
                        elif b == 1:
                            send_click(3, True)
                elif evt.type == SDL_CONTROLLERBUTTONUP:
                    b = evt.cbutton.button
                    print(f"\nButton {b} UP")
                    if osk_window:
                        if b == 9 and pressed_blue:
                            release_button(pressed_blue)
                            pressed_blue = None
                        elif b == 10 and pressed_red:
                            release_button(pressed_red)
                            pressed_red = None
                    else:
                        if b == 0:
                            send_click(1, False)
                        elif b == 1:
                            send_click(3, False)

            blue_open = AXIS_STATE[4] > 0
            red_open = AXIS_STATE[5] > 0
            if blue_open or red_open:
                open_osk()
                if blue_open:
                    blue_x, blue_y, last_move_blue = navigate(
                        AXIS_STATE[0]/32767, AXIS_STATE[1]/32767,
                        blue_x, blue_y, last_move_blue
                    )
                if red_open:
                    red_x, red_y, last_move_red = navigate(
                        AXIS_STATE[2]/32767, AXIS_STATE[3]/32768,
                        red_x, red_y, last_move_red
                    )
                highlight_all()
            else:
                if osk_window:
                    close_osk()
                x = AXIS_STATE[0]/32767
                y = AXIS_STATE[1]/32767
                dx_accum += x * MAX_SPEED
                dy_accum += y * MAX_SPEED
                ver_scroll_accum += AXIS_STATE[3] / -32768
                hor_scroll_accum += AXIS_STATE[2] / -32767
                mx, my = int(dx_accum), int(dy_accum)
                dx_accum -= mx
                dy_accum -= my
                if ver_scroll_accum >= 0.5:
                    send_scroll(0, 1)
                    ver_scroll_accum -= 1
                elif ver_scroll_accum <= -0.5:
                    send_scroll(0, -1)
                    ver_scroll_accum += 1
                if hor_scroll_accum >= 0.5:
                    send_scroll(-1, 0)
                    hor_scroll_accum -= 1
                elif hor_scroll_accum <= -0.5:
                    send_scroll(1, 0)
                    hor_scroll_accum += 1
                if mx or my:
                    move_cursor(mx, my)
                    updated = True

            if updated:
                print_axis_state()
            SDL_Delay(FRAME_DELAY)
            root_Tk.update()
    except KeyboardInterrupt:
        print()
        pass
    finally:
        if controller:
            SDL_GameControllerClose(controller)
        SDL_Quit()

if __name__ == "__main__":
    main()
