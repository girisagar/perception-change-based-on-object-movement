'''
    ESC   - exit
    b     - toggle back-projected probability visualization
'''
import math
import cv2
import numpy as np
from face_position import *


class FaceTracker(object):

    def __init__(self, video_src, debugMode=True):
        self.camera = cv2.VideoCapture(video_src)
        self.debugMode = debugMode
        ret, self.frame = self.camera.read()
        self.flag = False

        if self.debugMode:
            cv2.namedWindow('camshift')
            cv2.setMouseCallback('camshift', self.on_mouse)

        self.selection = None
        self.drag_start = None
        self.tracking_state = 0
        self.show_backproj = False
        self.frm = 0
        self.face_detection = True

    def detect_face(self, image):
        ''' Detect a face from the input image. Detects only the face with the largest area '''
        # Specify the trained cascade classifier
        face_cascade_name = 'haarcascades/haarcascade_frontalface_alt.xml'

        # Create a cascade classifier
        face_cascade = cv2.CascadeClassifier()

        # Load the specified classifier
        face_cascade.load(face_cascade_name)

        orig_image = image.copy()
        # Preprocess the image
        image = cv2.resize(image, (426, 320))
        image = cv2.blur(image, (10, 10))
        grayimg = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
        grayimg = cv2.equalizeHist(grayimg)

        # Run the classifiers
        faces = face_cascade.detectMultiScale(
            grayimg, 1.1, 2, 0 | cv2.cv.CV_HAAR_SCALE_IMAGE, (60, 60))

        if len(faces) != 0:            # If there are faces in the images
            # Get only the face with the biggest area
            index, area = max([(i, face[2] * face[3])
                              for i, face in enumerate(faces)])
            # Get the origin co-ordinates and the length and width till where
            # the face extends
            x, y, lx, ly = (int(j * 1.5)
                            for j in (faces[i][0], faces[i][1], faces[i][2], faces[i][3]))

            # Draw rectangles around all the faces
            cv2.rectangle(
                orig_image, (x, y), (x + lx, y + ly), cv2.cv.RGB(155, 255, 25), 2)
            cv2.imshow('Detected Face', orig_image)

            self.selection = (x, y, x + lx, x + ly)
            if self.selection is not None:
                self.tracking_state = 1
                self.face_detection = False
            else:
                self.face_detection = True
            return

    def on_mouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y])  # BUG
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.tracking_state = 0
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                h, w = self.frame.shape[:2]
                xo, yo = self.drag_start
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y]))
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y]))
                self.selection = None
                if x1 - x0 > 0 and y1 - y0 > 0:
                    self.selection = (x0, y0, x1, y1)
                    print self.selection
            else:
                self.drag_start = None
                if self.selection is not None:
                    self.tracking_state = 1

    def show_hist(self):
        bin_count = self.hist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count * bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            h = int(self.hist[i])
            cv2.rectangle(img, (i * bin_w + 2, 255), (
                (i + 1) * bin_w - 2, 255 - h), (int(180.0 * i / bin_count), 255, 255), -1)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        # cv2.imshow('hist', img)

    def run(self):
        while True:
            if (self.frm % 5 == 0):
                self.frm = 1
            else:
                self.frm = self.frm + 1
            ret, self.frame = self.camera.read()

            self.frame = cv2.flip(self.frame, 1)

            if self.face_detection:
                self.detect_face(self.frame)

            vis = self.frame.copy()
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(
                hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))

            if self.selection:
                x0, y0, x1, y1 = self.selection
                self.track_window = (x0, y0, x1 - x0, y1 - y0)
                hsv_roi = hsv[y0:y1, x0:x1]
                mask_roi = mask[y0:y1, x0:x1]
                hist = cv2.calcHist([hsv_roi], [0], mask_roi, [16], [0, 180])
                cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
                self.hist = hist.reshape(-1)
                self.show_hist()

                vis_roi = vis[y0:y1, x0:x1]
                cv2.bitwise_not(vis_roi, vis_roi)
                vis[mask == 0] = 0

            if self.tracking_state == 1:
                self.selection = None
                prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
                prob &= mask
                term_crit = (
                    cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
                track_box, self.track_window = cv2.CamShift(
                    prob, self.track_window, term_crit)
                centroid_x = int(track_box[0][0])
                centroid_y = int(track_box[0][1])
                track_box_area = math.pi * \
                    (track_box[1][0]) * (track_box[1][1])
                # print track_box_area
                cv2.circle(vis, (centroid_x, centroid_y), 5, (0, 255, 0), -1)
                self.direction = FacePosition().compute_position(
                    centroid_x, centroid_y, self.frm, track_box_area)
                if self.show_backproj:
                    vis[:] = prob[..., np.newaxis]
                try:
                    cv2.ellipse(vis, track_box, (0, 0, 255), 2)
                except:
                    print track_box
            if self.debugMode:
                cv2.imshow('camshift', vis)
                # print vis
                ch = 0xFF & cv2.waitKey(5)
                if ch == 27:
                    # IF Esc key is pressed
                    self.exit()
                    return
                if ch == ord('b'):
                    self.show_backproj = not self.show_backproj
        cv2.destroyAllWindows()

    def exit(self):
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    print __doc__
    FaceTracker(video_src, True).run()
