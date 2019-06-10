# Pymonitor
Motion detection with just a PiCamera

This uses PyDrive, Image/ImageChops, Numpy, and (of course) PiCamera to detect motion and upload images/videos to a Google Drive directory specified by the variable "folder_id".

You should have a credentials file set up with the Google Drive API, unless if you just want to save files locally.

## How it works
The program takes two images, and calculates the difference between those images, simulating a motion sensor. If the difference value is above a certain threshold, the program will record a video (h264). If the difference is below the threshold, the program will wait for a short period of time before starting over (rather than just immediately). No matter what, images will always be saved periodically.
