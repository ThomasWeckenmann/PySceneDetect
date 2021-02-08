# -*- coding: utf-8 -*-
#

""" ``scenedetect.bbox_video_stream`` Module.

    This module contains the BboxVideoStream class that sets up a video stream 
    and allows the user to select a recatangle / bounding box (coordinates 
    stored in a list of int in format: [ul-x, ul-y, lr-x, lr-y]) by mouse 
    clicking upper left and lower right coordinates of the desired bounding box 
    within the video frame.
    
    The bbox ccordinates are saved to a .bbox text_file and can then be used to 
    crop a cv2 frame.
"""

# Standard Library Imports
import logging
import os
import sys

# Third-Party Library Imports
import click
import cv2


class BboxVideoStream(object):
    """ BboxVideoStream: base class that sets up a video stream and allows the 
    user to select a recatangle / bounding box. """
    
    def __init__(self, video_file):
        """ BboxVideoStream Constructor Method (__init__).

        Arguments:
            video_file (str): Absolute path to video file.

        Raises:
            VideoOpenFailure: Video could not be opened.
        """
        self.cap = cv2.VideoCapture(video_file)
        self.output_file = os.path.splitext(video_file)[0] + ".bbox"
        self.basename = os.path.basename(video_file) 
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.bbox = []
        if (self.cap.isOpened()== False):
          raise VideoOpenFailure("Error opening the video file.")
          return
        else:
          self.frame = self.cap.read()[1]
          self.clean_frame = None
          self.height = self.frame.shape[0]

    def mouse_callback(self, event, x, y, flags, params):
        """ Callback method that sets bbox (rect) coordinates on an image. """
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.bbox) == 4:
                del self.bbox[:]
                self.frame = self.clean_frame
                cv2.imshow(self.basename, self.frame)
            self.bbox.extend([x, y])
            if len(self.bbox) == 2:
                cv2.circle(self.frame, tuple(self.bbox), 2, (0,255,0), 2)
                cv2.imshow(self.basename, self.frame)
            elif len(self.bbox) == 4:
                self._add_bbox_overlay()
                cv2.imshow(self.basename, self.frame)
                self._check_and_fix_bbox()
                self._save_bbox()

    def _add_bbox_overlay(self):
        """ Adds a rectangle overlay with the bbox coordinates to the frame. """
        cv2.rectangle(self.frame, 
                      tuple(self.bbox[:2]), tuple(self.bbox[2:]), 
                      (0,255,0), 2)

    def _add_text_overlay(self, text, y_pos):
        """ Adds a text overlay to the cv2 frame. """
        cv2.putText(self.frame, text, (30, y_pos), self.font, 1, (0, 255, 0), 2, 
                    cv2.LINE_AA)

    def _check_and_fix_bbox(self):
        """ Makes sure that bbox has this format: [ul-x, ul-y, lr-x, lr-y]."""
        if self.bbox[0] > self.bbox[2]:
            self.bbox[0], self.bbox[2] = self.bbox[2], self.bbox[0]
        if self.bbox[1] > self.bbox[3]:
            self.bbox[1], self.bbox[3] = self.bbox[3], self.bbox[1]

    def _save_bbox(self):
        """ Saves bbox to textfile. """
        with open(self.output_file, "w") as text_file:
            text_file.write(str(self.bbox))
            logging.info('Bounding Box: %s saved to %s', str(self.bbox), 
                         self.output_file)

    def play(self):
        """ Plays video and lets user define the bbox after pressing any key."""
        while(self.cap.isOpened()):
          status, self.frame = self.cap.read()
          info_text = "Press any key to pause video. Press q to exit."
          self._add_text_overlay(info_text, int(self.height/2))
          if status:
            if len(self.bbox) == 4:
                self.clean_frame = self.frame.copy()
                self._add_bbox_overlay()
            cv2.imshow(self.basename, self.frame)
            key = cv2.waitKey(1)
            if key == ord("q"):
                break
            elif key > -1:
                info_text = ("Set Bounding Box by clicking Upper Left & Lower"
                             "Right.")
                self._add_text_overlay(info_text, int(self.height/2-50))
                cv2.imshow(self.basename, self.frame)
                cv2.setMouseCallback(self.basename, self.mouse_callback)
                cv2.waitKey(0)
          else:
            break
        self.cap.release()
        cv2.destroyAllWindows()
