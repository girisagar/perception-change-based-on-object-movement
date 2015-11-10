import json
import math
import re
# import autopy
# import win32gui
import action

class HandPosition(object):

    def __init__(self):
        pass

    def get_length(self, x1, y1, x2, y2):
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return length

    def get_direction(self, x1, y1, x2, y2, length, fingers):
        if length < 25 and self.config['idle'] > 0:
            # print self.config['idle']
            if self.config['idle'] > 3:
                direction = self.finger_gesture(fingers)
            else:
                self.config['idle'] += 1
        elif length > 150 and x1 + y1 != 0:
            self.config['idle'] = 0
            if(x2 > x1):
                direction = 'Right'
            else:
                direction = 'Left'
            # print direction
        else:
            direction = 'None'
        json.dump(
            self.config, open('config.json', 'w'), sort_keys=True, indent=4)
        return direction

    def compute_position(self, current_x, current_y, frame, fingers):

        self.direction = 'None'
        try:
            self.config = json.load(open('config.json', 'r'))
            self.prev_x = self.config['prevX']
            self.prev_y = self.config['prevY']
            self.config['noCnt'] = 0
        except:
            self.config['prevX'] = 0
            self.config['prevY'] = 0

        if (frame % 10 == 0):
            # Do something every 10 frames
            self.config['prevX'] = current_x
            self.config['prevY'] = current_y
            self.current_x = current_x
            self.current_y = current_y

            json.dump(
                self.config, open('config.json', 'w'), sort_keys=True, indent=4)

            # self.direction =[]
            length = self.get_length(
                self.prev_x, self.prev_y, self.current_x, self.current_y)
            self.direction = self.get_direction(
                self.prev_x, self.prev_y, self.current_x, self.current_y, length, fingers)

            # Do something based on the hand movement direction
            self.perform_action()

            return self.direction
        else:
            return self.direction

    def finger_gesture(self, fingers):
        if fingers > 3:
            self.action = 'Palm Open'
        else:
            self.action = 'Palm Close'
        return self.action

    def perform_action(self):
        action.perform_action(self.config, self.direction, 'Hand')