import glob
import os
import tempfile
from argparse import ArgumentParser
from time import sleep, time, strftime
import psutil

import cv2
import numpy as np
import pyscreenshot as ImageGrab
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

KEEP_MOVIES = 100
INACTIVE_STOP_RECORD = 10


def main():
    class TempDirException(Exception):
        def __init__(self, message):
            super(self).__init__(message)

        def message(self):
            return self.message

    class VideoDirectoryException(Exception):
        def __init__(self, message):
            super(self).__init__(message)

        def message(self):
            return self.message

    class VideoMaker(object):
        """
        Record the user activity into video .avi.
        """

        def __init__(self, video_path, tmp_picture):
            self.video_path = video_path
            self.tmp_picture = tmp_picture
            self.start = time()
            self.nbr = 0
            self.width = None
            self.height = None
            self.frames = []

        def take_screenshot(self):
            """
            Take a screenshot
            :return:
            """
            img = ImageGrab.grab(childprocess=False)

            if self.nbr == 0:
                # if it's the first screenshot, retrieve the right width and height
                self.width, self.height = img.size

            self.nbr += 1
            img.save(self.tmp_picture)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frames.append(frame)

        def stop_record(self):
            """
            Write the video
            :return:
            """
            now = time()
            elapsed = now - self.start
            # try to find the better fps
            fps = float(int(self.nbr / elapsed))
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            writer = cv2.VideoWriter(self.video_path, fourcc, fps, (self.width, self.height))

            for frame in self.frames:
                # write the video
                writer.write(frame)

            cv2.destroyAllWindows()
            writer.release()

    class ListenerEvent(object):
        """
        This class is used for event management by users.
        """
        STATUS_STOPPED = "STOPPED"
        STATUS_IN_RECORD = "IN_RECORD"
        STATUS_NEED_TO_START = "NEED_TO_START"
        STATUS_NEED_TO_STOP = "NEED_TO_STOP"
        STATUS_NEED_RESTART = "NEED_TO_RESTART"

        def __init__(self, inactive_time):
            self.last_action_time = 0
            self.status_recording = self.STATUS_STOPPED
            self.inactive_time = inactive_time
            self.nbr_screenshot = 0
            self.run()

        def run(self):
            """
            enable keyboard and mouse listener
            :return:
            """
            keyboard_listener = KeyboardListener(on_press=self.on_event, on_release=self.on_event)
            mouse_listener = MouseListener(on_move=self.on_event, on_click=self.on_event, on_scroll=self.on_event)
            keyboard_listener.deamon = True
            mouse_listener.deamon = True
            keyboard_listener.start()
            mouse_listener.start()

        def on_event(self, *args, **kwargs):
            """
            The callback used by all listener
            :param args:
            :param kwargs:
            :return:
            """
            self.last_action_time = time()

            if self.status_recording == self.STATUS_STOPPED:
                self.status_recording = self.STATUS_NEED_TO_START

        def check_status(self):
            """
            Check if it is necessary to stop the video
            :return:
            """
            if self.status_recording == self.STATUS_IN_RECORD:
                self.nbr_screenshot += 1
                now = time()
                elapsed = now - self.last_action_time

                if elapsed > self.inactive_time:
                    # if the anybody use the computer since `inactive_time`
                    self.status_recording = self.STATUS_NEED_TO_STOP
                elif self.nbr_screenshot >= 500:
                    self.nbr_screenshot = 0
                    if Utils.get_available_memory() < 10:
                        # Check if the video does not consume all the memory or it will be restarted.
                        self.status_recording = self.STATUS_NEED_RESTART

        def need_to_start(self):
            """
            Checks if it is necessary to initialize recording the video
            :return:
            """
            return self.status_recording in (self.STATUS_NEED_TO_START, self.STATUS_NEED_RESTART)

        def need_to_stop(self):
            """
            Checks if it is necessary to stop recording the video
            :return:
            """
            return self.status_recording in (self.STATUS_NEED_TO_STOP, self.STATUS_NEED_RESTART)

        def need_record(self):
            """
            Checks if it is necessary to start recording the video
            :return:
            """
            return self.status_recording == self.STATUS_IN_RECORD

        def update_status(self, status):
            """
            Update the current status if needed
            :param status:
            :return:
            """
            self.nbr_screenshot = 0
            if status == self.STATUS_IN_RECORD \
                    or (status == self.STATUS_STOPPED and self.status_recording == self.STATUS_NEED_TO_STOP):
                self.status_recording = status

    class Utils(object):
        """
        Useful helpers
        """

        def __init__(self, video_directory, nbr_videos_to_keep):
            self.video_directory = video_directory.strip()
            self.nbr_videos_to_keep = nbr_videos_to_keep
            self.temp_directory = None
            self.initialize()

        def remove_oldest(self):
            """
            Keep only the x last videos
            :return:
            """
            avi = glob.glob('%s/*.avi' % self.video_directory)
            avi.sort(key=os.path.getctime, reverse=True)

            for to_delete in avi[self.nbr_videos_to_keep:]:
                os.unlink(to_delete)

        def temp_dir(self, first=True):
            """
            Return ab available temporary directory
            :param first:
            :return:
            """
            if self.temp_directory is None:
                try:
                    self.temp_directory = tempfile.TemporaryDirectory()
                except (PermissionError, FileExistsError):
                    raise TempDirException("Unable to create temporary directory")
            if not os.path.isdir(self.temp_directory.name):
                if first:
                    return self.temp_dir(False)
                raise TempDirException("Temporary directory does not exists")

            return self.temp_directory.name

        def initialize(self):
            """
            Initialize, several checks before running
            :return:
            """
            if not os.path.isdir(self.video_directory):
                raise VideoDirectoryException("Path %s doesn't exist" % self.video_directory)

            if not os.access(self.video_directory, os.W_OK):
                raise VideoDirectoryException("Path %s isn't writable" % self.video_directory)

            self.temp_dir()
            self.remove_oldest()

        def get_tmp_picture(self):
            """
            Return a temporary path to write the screenshot
            :return:
            """
            tmp = self.temp_dir()
            return os.path.join(tmp, "out.png")

        def make_video_path(self):
            """
            Return a the path to write the video
            :return:
            """
            return os.path.join(self.video_directory, "%s.avi" % strftime("%Y%m%d-%H%M%S"))

        @staticmethod
        def get_available_memory():
            """
            Return the available memory
            :return:
            """
            return psutil.virtual_memory().percent

    class ActivityListener(object):
        def __init__(self, video_directory, nbr_videos_to_keep, inactive_times):
            self.utils = Utils(video_directory, nbr_videos_to_keep)
            self.events = ListenerEvent(inactive_times)
            self.video_maker = None
            self.run()

        def run(self):
            while True:
                sleep(0.1)

                if self.events.need_to_start():
                    self.events.update_status(ListenerEvent.STATUS_IN_RECORD)
                    self.video_maker = VideoMaker(self.utils.make_video_path(), self.utils.get_tmp_picture())

                if self.events.need_record():
                    self.video_maker.take_screenshot()
                    self.events.check_status()

                if self.events.need_to_stop():
                    self.video_maker.stop_record()
                    self.video_maker = None
                    self.events.update_status(ListenerEvent.STATUS_STOPPED)
                    self.utils.remove_oldest()

    parser = ArgumentParser(usage="usage: %(prog)s [options]")
    parser.add_argument("-o",
                        help="Directory to save the videos",
                        type=str,
                        dest="video_directory",
                        required=True)
    parser.add_argument("-k",
                        dest="nbr_videos_to_keep",
                        type=int,
                        default=KEEP_MOVIES,
                        help="max videos to keep: " + str(KEEP_MOVIES))
    parser.add_argument("-i",
                        dest="inactive_time",
                        type=int,
                        default=INACTIVE_STOP_RECORD,
                        help="stop record if inactive after x seconds: " + str(INACTIVE_STOP_RECORD))
    user_arguments = parser.parse_args()

    ActivityListener(
        user_arguments.video_directory,
        user_arguments.nbr_videos_to_keep,
        user_arguments.inactive_time
    )


if __name__ == "__main__":
    main()
