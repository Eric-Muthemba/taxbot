import win32gui
from time import sleep
import win32con


popups = [{"title":"Generate Upload File","button_text":"&Yes"},{"title":"Microsoft Excel","button_text":"OK"}]

def callback(hwnd, _):
    if win32gui.IsWindowVisible(hwnd):
        if win32gui.GetWindowText(hwnd) in [popup["title"] for popup in popups]:
                child_handle = win32gui.FindWindowEx(hwnd, 0, "Button",[ popup["button_text"] for popup in popups if  win32gui.GetWindowText(hwnd) == popup["title"] ][0])  
                if child_handle != 0:
                    win32gui.SendMessage(child_handle, win32con.BM_CLICK, 0, 0) 
                    print("button  found")
                else:
                    print("button not found")
while True:
    win32gui.EnumWindows(callback, None)
    print("searching ...")
    sleep(1)
