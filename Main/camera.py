import datetime
import cv2

class CameraApp(object):
    """docstring for CameraApp"""
    def __init__(self):
        super(CameraApp, self).__init__()
        self.camera = cv2.VideoCapture(2)

        self.camera.set(3, 1280)
        self.camera.set(4, 720)


    def run(self):
        while True:
            ret, img = self.camera.read()
            img = cv2.flip(img, 1)
            cv2.imshow('Camera', img)
            # cv2.setWindowProperty("Camera", cv2.WINDOW_AUTOSIZE, cv2.WND_PROP_ASPECT_RATIO)

            ch = 0xFF & cv2.waitKey(5)
            if ch == 27:
                break
            elif ch == ord('p'):
                file_name = 'image_{}_{}_{}.jpg'.format(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)

                cv2.imwrite(file_name, img)


if __name__ == '__main__':
    CameraApp().run()
