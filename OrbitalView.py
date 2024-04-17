import csv
import logging
from datetime import datetime
import threading, queue
import multiprocessing
import socket
import time

import av
import cv2
from simple_pyspin import Camera


def save():  # saving to mp4
    while True:
        img = q.get()

        # encode the image
        frame = av.VideoFrame.from_ndarray(img, format="gray8")
        for packet in stream.encode(frame):
            container.mux(packet)

        q.task_done()


def view(displayq, exit_flag, start_flag, sock):
    while True:
        # Display the resulting frame
        if not displayq.empty():
            cv2.imshow("Video", displayq.get())

            data = "0"
            try:
                data = sock.recv(1)
            except socket.error:
                pass
            key = cv2.waitKey(1)
            # start signal is sent by either keyboard or MATLAB
            if ord("s") in (key & 0xFF, ord(data)):
                start_flag.put(True)
            # quit signal is sent by either keyboard or MATLAB
            elif ord("q") in (key & 0xFF, ord(data)):
                exit_flag.put(True)
                break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    cam = Camera()  # Acquire Camera
    cam.init()  # Initialize camera
    cam.AcquisitionMode = "Continuous"
    cam.start()  # Start recording

    # try make the frame rate 500
    cam.AcquisitionFrameRateAuto = "Off"
    cam.AcquisitionFrameRateEnabled = True
    cam.AcquisitionFrameRate = 500

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 6611))
    sock.setblocking(0)  # non-blocking, important!!!

    q = queue.Queue()  # queue for ffmpeg
    time_list = []
    displayq = multiprocessing.Queue()
    exit_flag = multiprocessing.Queue()
    start_flag = multiprocessing.Queue()

    # Python's GIL is annoying/slow, use multiprocessing to display the live view
    # this process will also take user inputs (s for start recording and q for quit)
    multiprocessing.Process(
        target=view, args=(displayq, exit_flag, start_flag, sock)
    ).start()

    n = 0
    thread_started_flag = False
    while True:
        if not exit_flag.empty():  # exit_flag is non-empty, exit
            # print(f"finish: {time.time()}")
            break
        img = cam.get_array()

        if not start_flag.empty():  # start saving to mp4
            if not thread_started_flag:
                thread_started_flag = True  # start the thread only once

                height, width = img.shape
                # the filename is up to second precision
                fn_base = datetime.today().strftime("%Y-%m-%d-%H-%M-%S.%f")
                fn = f"{fn_base}.mp4"

                container = av.open(fn, mode="w")
                stream = container.add_stream(
                    "h264_nvenc",
                    rate=25, # hard-coded frame rate
                    options={
                        "qmin": "16",
                        "qmax": "16",
                        "vsync": "0",
                    },
                )
                stream.width = width
                stream.height = height
                stream.pix_fmt = "yuv420p"

                # turn-on the thread which saves the output
                threading.Thread(target=save, daemon=True).start()

                # print(f"start: {time.time()}")
                # get a new image since the current one is out-of-date (due to time spent on spawning thread)
                img = cam.get_array()

            time_list.append(time.perf_counter())
            q.put(img)

        n = (n + 1) % 10  # display the live view at 500/10=50FPS to save CPU time
        if n == 0:
            displayq.put(img)

    logging.info("All task requests sent")

    q.join()  # block until all tasks are done

    try:
        with open(f"{fn_base}.csv", "w") as f:
            # using csv.writer method from CSV package
            write = csv.writer(f, delimiter="\n")
            write.writerow(time_list)
    except Exception as e:
        logging.error(f"Error when saving the timestamp file {fn_base}.csv!")
        logging.error(e)

    logging.info("All work completed")
    if thread_started_flag:  # recording operation used, need to close the process
        # Flush stream
        for packet in stream.encode():
            container.mux(packet)

        # Close the file
        container.close()

    cam.stop()  # Stop recording
    cam.close()  # You should explicitly clean up
    sock.close()  # close the UDP socket
