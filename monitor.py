from PIL import Image, ImageChops
from pydrive.auth import GoogleAuth, ServiceAccountCredentials as Creds
from pydrive.drive import GoogleDrive
import numpy
import os
import picamera
import time

# Initialize PiCamera, set up Google Auth creds
choice = ""
threshold = 0.1
camera = picamera.PiCamera()
folder_id = "19jsoGFGGH14H0rc-jvxhGl5lrInUKEQe"
gauth = GoogleAuth()
auth = ["https://www.googleapis.com/auth/drive"]
gauth.credentials = Creds.from_json_keyfile_name("creds.json", auth)
drive = GoogleDrive(gauth)

# Uploads/removes local file (unless can't connect)
def upload(file):
    try:
        print("Uploading", file)
        location = [{"kind": "drive#fileLink", "id": folder_id}]
        drive_file = drive.CreateFile({"parents": location})
        drive_file.SetContentFile(file)
        drive_file.Upload()
        os.remove(file)
    except:
        print("Connection is offline or something's wrong with Google")

# Main program loop
while choice != "3":
    print("Welcome to Monitor")
    print("What do you want to do?")
    print("1) Monitor")
    print("2) Clear files")
    print("3) Quit")
    choice = input()

    if choice == "1":
        try:
            # Motion detection loop
            while True:
                # Start preview
                preview = camera.start_preview()
                preview.fullscreen = False
                preview.window = (0, 0, 400, 300)
                time.sleep(1)

                # Take and open two images
                print("Taking pictures")
                cap_time = time.strftime("%m-%d-%Y-%H-%M-%S")
                camera.capture("f" + cap_time + ".jpg")
                camera.capture("s" + cap_time + ".jpg")
                img1 = Image.open("f" + cap_time + ".jpg")
                img2 = Image.open("s" + cap_time + ".jpg")

                # Calculate difference between images
                print("Computing difference")
                img = ImageChops.difference(img1, img2)
                img1.close()
                img2.close()
                w, h = img.size
                a = numpy.array(img.convert("RGB")).reshape((w * h, 3))
                h, e = numpy.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)
                prob = h / numpy.sum(h)
                prob = prob[prob > 0]
                diff = -numpy.sum(prob * numpy.log2(prob))
                print(diff)

                # If difference value crosses certain threshold, record video
                if diff > threshold:
                    print("MOTION DETECTED!")
                    print("Recording video")
                    rec_time = time.strftime("%m-%d-%Y-%H-%M-%S")
                    camera.start_recording("v" + rec_time + ".h264")
                    camera.wait_recording(15)
                    camera.stop_recording()
                    upload("v" + rec_time + ".h264")
                else:
                    print("No motion detected")

                # Upload images, pause if diff value below threshold
                camera.stop_preview()
                upload("f" + cap_time + ".jpg")
                upload("s" + cap_time + ".jpg")
                if diff <= threshold:
                    time.sleep(5)

        # Go back to main program loop when interrupted
        except KeyboardInterrupt:
            camera.stop_preview()
            print("Stopping")
            time.sleep(1)

    if choice == "2":
        try:
            # List all files in Google Drive directory
            drive_file_list = drive.ListFile().GetList()
            for file in drive_file_list:
                if file["id"] != folder_id:
                    print(file["title"], file["id"])

            print("This will delete the files listed above")
            print("Are you sure you want to continue? (y/n)")
            clear_choice = input().lower()

            if clear_choice == "y":
                # Delete all files in GDrive directory
                for file in drive_file_list:
                    if file["id"] != folder_id:
                        print("Deleting " + file["title"])
                        file.Delete()
                print("Complete")
            else:
                print("Nothing will be deleted")

        # Only works if drive fetching commands work
        except:
            print("Connection is offline or something's wrong with Google")

print("Goodbye!")
input("Press enter to exit")
