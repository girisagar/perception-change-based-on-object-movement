import ctypes
import action_face as action
import json
import math
import time
import autopy
import win32gui
import win32api
import win32con


# C struct redefinitions
endInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [('wVk', ctypes.c_ushort),
                ('wScan', ctypes.c_ushort),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [('uMsg', ctypes.c_ulong),
                ('wParamL', ctypes.c_short),
                ('wParamH', ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_long),
                ('dy', ctypes.c_long),
                ('mouseData', ctypes.c_ulong),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', PUL)]


class Input_I(ctypes.Union):
    _fields_ = [('ki', KeyBdInput),
                ('mi', MouseInput),
                ('hi', HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [('type', ctypes.c_ulong),
                ('ii', Input_I)]

# Actuals Functions


class FacePosition(object):

    def press_key(self, hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_key(self, hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(
            hexKeyCode, 0x48, 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def get_length(self, x1, y1, x2, y2):
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return length


    def compute_position(self, current_x, current_y, frame, area):
        self.direction = 'None'
        try:
            self.config = json.load(open('config.json', 'r'))
            self.prev_x = self.config['prevX']
            self.prev_y = self.config['prevY']
            self.config['noCnt'] = 0
        except:
            self.config['prevX'] = 0
            self.config['prevY'] = 0
        if (frame % 5 == 0):
            self.config['prevX'] = current_x
            self.config['prevY'] = current_y
            self.current_x = current_x
            self.current_y = current_y
            # self.direction =[]
            length = self.get_length(
                self.prev_x, self.prev_y, self.current_x, self.current_y)
            active_window = win32gui.GetWindowText(
                win32gui.GetForegroundWindow())

            self.direction = 'None'
            for window in self.config.get('allowed_windows'):
                if window.get('name') in active_window and window.get('works_on') == 'Face':
                    # print window.get('name') + ' found. WORKING'
                    self.direction = self.get_direction(
                        self.prev_x, self.prev_y, self.current_x, self.current_y, length, area)
                    # self.perform_action()

            json.dump(
                self.config, open('config.json', 'w'), sort_keys=True, indent=4)
            if active_window == "Travel":
                return self.direction
            else:
                # self.direction = str(self.direction)
                # print self.direction
                action.perform_action(self.config, self.direction, 'Face')
                return self.direction

        else:
            return self.direction

    def get_direction(self, x1, y1, x2, y2, length, area):
        active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if active_window == "Travel":
            x = int((1366 / 640) * x2)
            y = int((768 / 480) * y2)
            win32api.SetCursorPos((x, y))
            for x in xrange(1, 3):
                if x2 < 100:
                    direction = 'Left'
                    # autopy.key.tap(autopy.key.K_RIGHT)
                    self.press_key(0x27)  # right
                    time.sleep(0.2)
                    self.release_key(0x27)  # right
                elif x2 > 500:
                    direction = 'Right'
                    # autopy.key.tap(autopy.key.K_LEFT)
                    self.press_key(0x25)  # left
                    time.sleep(0.2)
                    self.release_key(0x25)  # left

                elif length > 8 and x1 + y1 != 0:
                    if(x2 > x1):
                        direction = 'Left'
                        # autopy.key.tap(autopy.key.K_LEFT)
                        self.press_key(0x25)  # left
                        time.sleep(0.3)
                        self.release_key(0x25)  # left
                        time.sleep(.5)
                    else:
                        direction = 'Right'
                        # call here event Left
                        # autopy.key.tap(autopy.key.K_RIGHT)
                        self.press_key(0x27)  # right
                        time.sleep(0.3)
                        self.release_key(0x27)  # right
                        time.sleep(.5)
                else:
                    direction = 'Current'
        #-----------------------------------------------------------------
                if y < 200:
                    direction = 'Down'
                    # autopy.key.tap(autopy.key.K_DOWN)
                    self.press_key(0x28)  # down
                    time.sleep(0.02)
                    self.release_key(0x28)  # down
                elif y > 550:
                    direction = 'Up'
                    # autopy.key.tap(autopy.key.K_UP)
                    self.press_key(0x26)  # up
                    time.sleep(0.02)
                    self.release_key(0x26)  # up
                elif length > 5 and x1 + y1 != 0:
                    if(y2 > y1):
                        direction = 'Up'
                        # autopy.key.tap(autopy.key.K_UP)
                        self.press_key(0x26)  # up
                        time.sleep(0.05)
                        self.release_key(0x26)  # up
                    else:
                        direction = 'Down'
                        # call here event Left
                        # autopy.key.tap(autopy.key.K_DOWN)
                        self.press_key(0x28)  # down
                        time.sleep(0.05)
                        self.release_key(0x28)  # down
                else:
                    direction = 'Current'
        # ---------------------------------------------------------------------
                try:
                    if (150000.0 / area) > 1.2:
                    # zoom out
                        # autopy.key.tap('-',autopy.key.MOD_CONTROL)
                        # autopy.key.tap(autopy.key.K_CONTROL)
                        self.press_key(0x11)  # Ctrl
                        self.press_key(0xBD)  # -

                        time.sleep(.2)
                        self.release_key(0x11)  # Ctrl
                    elif (150000.0 / area) < 0.8:
                    # zoom in
                        # autopy.key.tap('+',autopy.key.MOD_CONTROL)
                        # autopy.key.tap(autopy.key.K_SHIFT)/
                        self.press_key(0x11)  # Ctrl
                        self.press_key(0xBB)  # +

                        time.sleep(.2)
                        self.release_key(0x11)  # Ctrl
                except:
                    autopy.key.tap(autopy.key.K_SHIFT)
                return direction
        else:
            direction = 'None'
            x2 = int((1366 / 640) * x2)
            y2 = int((768 / 480) * y2)
            x1 = int((1366 / 640) * x1)
            y1 = int((768 / 480) * y1)

            if length < 25:
                direction = self.finger_gesture(area)
            elif abs(x2-x1) > 80 and x1 + y1 != 0:
                # self.config['idle'] = 0
                if(x1 > 558 and x1< 908 and x2<458):
                    direction = 'Left'
                elif (x1 > 558 and x1< 908 and x2>908):
                    direction = 'Right'
                # print direction
            else:
                direction = 'None'
            json.dump(
                self.config, open('config.json', 'w'), sort_keys=True, indent=4)
            return direction

    def finger_gesture(self, area):
        self.action = "None"
        if (150000.0 / area) > 1.6:
            self.action = 'Palm Open'
        elif (150000.0 / area) < .9:
            self.action = 'Palm Close'
        return self.action

    def perform_action(self,direction):
        action.perform_action(self.config, direction, 'Face')