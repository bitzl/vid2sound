from queue import Queue
from threading import Thread

import cv2
import numpy as np


def video2array(path, transform):
    cap = cv2.VideoCapture(path)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('Number of frames:', length)

    result = np.zeros(length)

    for i in range(length):
        ret, frame = cap.read()
        if not ret:
            print('Interrupted at frame', i)
            break
        result[i] = transform(frame)

    cap.release()
    return result


class VideoStream:
    def __init__(self, path, queue_size=128):
        self.capture = cv2.VideoCapture(path)
        self.length = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.stopped = False
        self.queue = Queue(maxsize=queue_size)

        t = Thread(target=self.update, name='vid2sound video decoding')
        t.daemon = True
        t.start()

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        while True:
            if self.stopped:
                raise StopIteration()
            try:
                yield self.queue.get(timeout=0.5)  # Wait one second if queue is empty
            except:
                raise StopIteration()

    def update(self):
        while True:
            got_frame, frame = self.capture.read()
            if not got_frame:
                self.stopped = True
                self.capture.release()
                print('Stopping, no more frames')
                return
            self.queue.put(frame)


def video2array_async(path, transform):
    stream = VideoStream(path)
    print('Number of frames:', stream.length)
    result = np.zeros(stream.length)
    for i, frame in enumerate(stream):
        result[i] = transform(frame)
    return result
