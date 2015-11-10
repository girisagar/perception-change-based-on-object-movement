import sys

sys.path.append('/usr/local/lib/python2.7/site-packages')

import json
import time
# import win32gui
from hand_tracker import *
# from face_tracker import *
import cv2


class MainClass(object):
    def __init__(self):
        super(MainClass, self).__init__()
        self.debugMode = True
        try:
            # Open the configuration file to read the settings from
            self.config = json.load(open('config.json', 'r'))
        except:
            print 'Configuration file not found.'
            exit()
        self.video_src = self.config['camera_settings'].get('source', 0)

    def run(self):
        detection_method = self.config['detection_method']
        print 'Application started'
        while True:
            try:

                hand_tracker = HandTracker(
                                        self.video_src, self.debugMode)
                hand_tracker.run()
                
                if cv2.waitKey(1) == 27:
                    # IF Esc key is pressed
                    self.exit()
                    return
#             # Continuously check for the name of the top window
#             window_name = win32gui.GetWindowText(
#                 win32gui.GetForegroundWindow())

#             for window in self.config.get('allowed_windows'):
#                 try:
#                     if window.get('name') in window_name and window.get('works_on') == detection_method:
#                         # Perform detection only when the active window is
#                         # allowed window
#                         print window.get('name') + ' found. WORKING'
#                         if detection_method == 'Hand':
#                             hand_tracker = HandTracker(
#                                 self.video_src, self.debugMode)
#                             hand_tracker.run()

#                         elif detection_method == 'Face':
#                             face_tracker = FaceTracker(
#                                 self.video_src, self.debugMode)
#                             face_tracker.run()

#                         else:
#                             print 'Something is wrong.'
#                             exit()
#                 except UnicodeDecodeError:
#                     pass
            except:
                print 'error'
#             time.sleep(5)

if __name__ == '__main__':
    try:
        main_class = MainClass()
        main_class.run()
    except KeyboardInterrupt as e:
        exit()