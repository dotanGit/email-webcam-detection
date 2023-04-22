import cv2    # import the OpenCV library for image and video processing
import time   # import the time module for delaying execution
import glob   # import the glob module to search for file path names
import os
from emailing import send_email   # import the send_email function from a custom module called emailing
from threading import Thread     # import the Thread class from the threading module for multi-threading

video = cv2.VideoCapture(0)   # create a video capture object for the default camera (index 0 because I only have 1 camera)
time.sleep(1)   # wait for 1 second to allow the camera to warm up

first_frame = None   # initialize the first frame to None (empty)
status_list = []   # create an empty list to store the status of each frame
count = 1   # initialize a counter for the image files to be saved

# define a function to clean the folder of all saved images
def clean_folder():
    print("clean_folder function started")
    images = glob.glob("images/*.png")   # search for all PNG image files in the images folder
    for image in images:   # iterate over each image file
        os.remove(image)   # remove the image file
    print("clean_folder function ended")

while True:
    status = 0   # initialize the status of the current frame to 0 (no movement detected)
    check, frame = video.read()   # read the next frame from the video capture object, check if it was successful (boolean), and retrieve the frame image data
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # convert the BGR color frame to grayscale, Converting the video frame to grayscale simplifies the image and helps with detecting changes in the image because less information is needed to analyze it.
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21,21), 0)   # apply a Gaussian blur with a kernel size of (21, 21) to smooth the frame and reduce noise

    if first_frame is None:   # if the first frame has not been initialized yet
        first_frame = gray_frame_gau   # store the current processed frame as the first frame

    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)   # compute the absolute difference between the first frame and the current processed frame

    thresh_frame = cv2.threshold(delta_frame, 50, 255, cv2.THRESH_BINARY)[1]   # apply a threshold to the difference frame to create a binary image where pixels with values above a certain threshold (50 in this case) are set to 255 (white), while pixels with lower values are set to 0 (black)
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)   # apply a dilation operation to the binary image to fill in gaps and smooth the edges of the regions of interest

    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   # find contours in the dilated binary image using the RETR_EXTERNAL mode, which retrieves only the outermost contours, and the CHAIN_APPROX_SIMPLE method, which compresses horizontal, vertical, and diagonal segments and leaves only their end points    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   # find contours in the dilated binary image using the RETR_EXTERNAL mode, which retrieves only the outermost contours, and the CHAIN_APPROX_SIMPLE method, which compresses horizontal, vertical, and diagonal segments and leaves only their end points

    for contour in contours:  # iterate over the contours
        if cv2.contourArea(contour) < 5000:  # if the area of the contour is smaller than 5000 pixels
            continue  # skip the contour and go to the next one
        x, y, w, h = cv2.boundingRect(contour)  # compute the bounding rectangle of the contour
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0),
                                  3)  # draw a green rectangle around the contour on the original color frame image
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}image.png",
                        frame)  # save the current frame as an image with a filename based on the count
            count += 1  # increment the count variable
            all_images = glob.glob("images/*.png")  # get a list of all image files in the "images" directory
            index = int(len(all_images) / 2)  # calculate the index of the middle image in the list
            image_with_object = all_images[
                index]  # set the variable "image_with_object" to the filename of the middle image in the list

    status_list.append(status)  # add the current status (1 or 0) to the end of the status_list
    status_list = status_list[-2:]  # keep only the last two elements in the status_list

    if status_list[0] == 1 and status_list[1] == 0:  # if the status has changed from 0 to 1 in the last two iterations
        email_thread = Thread(target=send_email, args=(
        image_with_object,))  # create a new thread to send an email with the image of the object
        email_thread.deamon = True  # set the daemon flag to True (so the thread will exit when the program exits)
        clean_thread = Thread(target=clean_folder)  # create a new thread to clean up the "images" directory
        clean_thread.deamon = True  # set the daemon flag to True

        email_thread.start()  # start the email thread

    cv2.imshow("Video", frame)  # display the current color frame with the rectangles around the contours
    key = cv2.waitKey(1)  # wait for a key to be pressed (with a 1 ms delay)

    if key == ord("q"):  # if the key pressed is "q"
        break  # exit the loop

video.release()  # release the video capture object and free up the resources used by it
clean_thread.start()  # start the thread to clean up the "images" directory
