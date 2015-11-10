'''
This module contains some common routines used by other samples.
'''

import cv2


def draw_str(dst, xxx_todo_changeme, s):
    (x, y) = xxx_todo_changeme
    cv2.putText(dst, s, (x + 1, y + 1), cv2.FONT_HERSHEY_PLAIN,
                1.0, (0, 0, 0), thickness=2, lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN,
                1.0, (255, 255, 255), lineType=cv2.CV_AA)
