import json
import numpy as np
import cv2
import common
# import win32gui
from ConvexHull import *


class HandTracker(object):

    def __init__(self, video_src, debugMode=True):
        self.do_work = False        # To perform or not perform the recognition
        self.direction = 0
        self.debugMode = debugMode
        self.fingers = 0
        self.frame = 0
        self.camera = cv2.VideoCapture(video_src)

        self.camera.set(3, 640)
        self.camera.set(4, 480)

        self.posPre = 0
        self.Data = {
            "angles less 90": 0,
            "cursor": (0, 0),
            "hulls": 0,
            "defects": 0,
            "fingers": 0,
            "fingers history": [0],
            "area": 0,
        }

        self.lastData = self.Data

        try:
            # Open the configuration file to read the settings from
            config_file = open("config.json", "r")
            self.config = json.load(config_file)
        except:
            print "Configuration file not found."
            exit()

        self.convex_hull = ConvexHull()

        if self.debugMode:
            cv2.namedWindow("Filters")
            cv2.createTrackbar("erode", "Filters", self.config[
                               "erode"], 255, self.erode)
            cv2.createTrackbar("dilate", "Filters", self.config[
                               "dilate"], 255, self.dilate)
            cv2.createTrackbar("smooth", "Filters", self.config[
                               "smooth"], 255, self.smooth)
            cv2.createTrackbar("upper", "Filters", self.config[
                               "upper"], 255, self.onChange_upper)
            cv2.createTrackbar("lower", "Filters", self.config[
                               "lower"], 255, self.onChange_lower)

    def erode(self, value):
        self.config["erode"] = value + 1
        json.dump(self.config, open(
            "config.json", "w"), sort_keys=True, indent=4)

    def dilate(self, value):
        self.config["dilate"] = value + 1
        json.dump(self.config, open(
            "config.json", "w"), sort_keys=True, indent=4)

    def smooth(self, value):
        self.config["smooth"] = value + 1
        json.dump(self.config, open(
            "config.json", "w"), sort_keys=True, indent=4)

    def onChange_upper(self, value):
        self.config["upper"] = value
        json.dump(self.config, open(
            "config.json", "w"), sort_keys=True, indent=4)

    def onChange_lower(self, value):
        self.config["lower"] = value
        json.dump(self.config, open(
            "config.json", "w"), sort_keys=True, indent=4)

    def filter_skin(self, im):
        """Apply the filter skin."""
        UPPER = np.array([self.config["upper"], self.config[
                         "filterUpS"], self.config["filterUpV"]], np.uint8)
        LOWER = np.array([self.config["lower"], self.config[
                         "filterDownS"], self.config["filterDownV"]], np.uint8)
        hsv_im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        # Remove all the region except the skin
        filter_im = cv2.inRange(hsv_im, LOWER, UPPER)
        return filter_im

    def run(self):
        while True:
            if (self.frame % 10 == 0):
                # Do something every 10 frames only
                # window_name = win32gui.GetWindowText(
                #     win32gui.GetForegroundWindow())
                self.frame = 1

                # Check if current window is in the list of allowed windows or
                # not
                if self.debugMode:
                    self.do_work = True
                else:
                    self.do_work = False
                    # self.do_work = any(window.get(
                    #     'name') in window_name for window in self.config.get('allowed_windows'))
            else:
                self.frame = self.frame + 1

            # print window_name + '=>' + str(self.do_work)
            ret, im = self.camera.read()
            im = cv2.flip(im, 1)    # Flip the image to make it as a mirror

            # print self.do_work
            if self.do_work:
                # Perform image processing on only the window that are allowed
                # print window_name
                self.im_orig = im.copy()
                self.imNoFilters = im.copy()

                # Smoothing to reduce noise
                # Uses Normalized Box Filter
                # Simplest of all! Each output pixel is the mean of its kernel neighbors (all
                # of them contribute with equal weights)
                im = cv2.blur(im, (self.config[
                              "smooth"], self.config["smooth"]))
                im_blur = im.copy()
                filter_ = self.filter_skin(im)
                im_skin = filter_.copy()
                filter_ = cv2.erode(filter_,
                                    cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.config["erode"], self.config["erode"])))
                im_erode = filter_.copy()
                filter_ = cv2.dilate(filter_,
                                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.config["dilate"], self.config["dilate"])))
                dilated = filter_.copy()

                try:
                    # print 'here'
                    vis, self.fingers, self.direction = self.convex_hull.draw_convex(
                        filter_, self.im_orig, self.frame)

                    ch = 0xFF & cv2.waitKey(5)
                    if ch == ord(' '):
                        cv2.imwrite('images/im_orig.jpg', self.imNoFilters)
                        cv2.imwrite('images/im_blur.jpg', im_blur)
                        cv2.imwrite('images/im_skin.jpg', im_skin)
                        cv2.imwrite('images/im_erode.jpg', im_erode)
                        cv2.imwrite('images/im_dilated.jpg', dilated)
                        cv2.imwrite('images/im_final.jpg', vis)
                        print 'Images saved to disk.'
                except Exception, e:
                    # dilated = self.im_orig
                    # print 'Error => ', e
                    vis = self.im_orig
            else:
                # NO image processing required
                vis = im

            if self.debugMode:
                common.draw_str(vis, (
                    20, 50), 'No of fingers: ' + str(self.fingers))
                common.draw_str(vis, (
                    20, 80), 'Movement of contour:' + str(self.direction))
                cv2.imshow('dilated', dilated)
                cv2.imshow('image', vis)

                if cv2.waitKey(1) == 27:
                    # IF Esc key is pressed
                    self.exit()
                    return

    def exit(self):
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    tracing = HandTracker(video_src, True)
    tracing.run()
