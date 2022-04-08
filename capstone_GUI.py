# img_viewer.py

import PySimpleGUI as sg
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os.path
import cv2
from statistics import mode
from datetime import datetime


print(tf.__version__)
model = keras.models.load_model("C:/Users/17jcs9/Desktop/Capstone/model")
f = open("demofile2.txt", "a")
# Create videofeed object:
class Videofeed:
    def __init__(self, video, room, name):
        stream = cv2.VideoCapture(video)
        frames = []
        while(stream.isOpened()):
            frameId = stream.get(1) #current frame number
            ret, frame = stream.read()
            if (ret != True):
                break
            res = cv2.resize(frame, dsize=(320, 180), interpolation=cv2.INTER_CUBIC)
            res = res.reshape(1,320,180,3)
            frames.append(res)
        stream.release()

        self.video = frames
        self.status_array = [1] * 10
        self.status = 0
        self.room = room
        self.name = name
        self.next_to_change = 0
        self.current_frame = 0

    def updateStatus(self):
        #need to define model

        #get model to predict on current frame
        
        my_list = model.predict(self.video[self.current_frame])
        #my_list = model.predict(self.video[100])
        max_index = my_list[0].argmax(axis=0)
        print(my_list)
        print(max_index)
        print(self.current_frame)
        #add prediction to proper part of sliding window array
        self.status_array[self.next_to_change] = max_index
        #update status with most likely prediction
        temp = mode(self.status_array)
        if temp == 0:
            self.status = "Getting out of bed"
        elif temp == 1:
            self.status = "In bed"
        elif temp == 2:
            if self.status !=  "Injured":
                f = open("demofile2.txt", "a")
                f.write("Report: room: " + self.room + ", Patient: "  + self.name + ", Time: " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "\n")
                f.close()
            self.status = "Injured"
        else:
            self.status = "Out of bed"
        #update counter variables, 10 can be changed if we want to change every how many frames we look at
        if self.next_to_change != 9:
            self.next_to_change = self.next_to_change + 1
        else:
            self.next_to_change = 0

        skip = 20
        if self.current_frame + skip >= len(self.video):
            self.current_frame = self.current_frame + skip - len(self.video)
        else:
            self.current_frame = self.current_frame + skip
        "1 is in bed"
        "0 is getting out of bed"
        "2 injured"
        "3 out of bed"

#define objects
feed_1 = Videofeed("Animation001.mp4", "101", "Patient 1")
feed_2 = Videofeed("Animation002.mp4", "122", "Patient 2")
feed_3 = Videofeed("Animation003.mp4", "133", "Patient 3")
feed_4 = Videofeed("Animation004.mp4", "144", "Patient 4")
feed_5 = Videofeed("Animation005.mp4", "155", "Patient 5")
data_array = [[feed_1.name, feed_1.room, feed_1.status],[feed_2.name, feed_2.room, feed_2.status], [feed_3.name, feed_3.room, feed_3.status], [feed_4.name, feed_4.room, feed_4.status], [feed_5.name, feed_5.room, feed_5.status]]
feed_order = [feed_1, feed_2, feed_3, feed_4, feed_5]
current_feed = None
# First the window layout in 2 columns

file_list_column = [
    [
        sg.Table(data_array, headings = ["Name", "Room Number", "Status"], enable_events=True, key="-TableRow-", auto_size_columns = False, max_col_width= 30, def_col_width= 15)
    ],

]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Choose a room on the left to see video feed:", key="-RightText-")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
    [sg.Button(button_text="Close", visible=False, key="-Close-")],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Patient Monitoring System", layout)

# Run the Event Loop
while True:
    event, values = window.read(timeout=1)
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".gif"))
        ]
    
    elif event == "-TableRow-":
        try:
            current_feed = values["-TableRow-"][0]
            img=feed_order[values["-TableRow-"][0]].video[feed_order[values["-TableRow-"][0]].current_frame]
            img = img.reshape(180, 320, 3)
            #print(type(img))
            img = cv2.imencode('.png', img)[1].tobytes()
            window["-IMAGE-"].update(data=img, visible = True)
            window["-RightText-"].update("Click on another room to see new feed. Click exit to close video feed.")
            window["-Close-"].update(visible=True)
        except:
            print("transition failed")

    elif event =="-Close-":
        current_feed = None
        window["-IMAGE-"].update(visible=False)
        window["-RightText-"].update("Choose a room on the left to see video feed:")
        window["-Close-"].update(visible=False)
    else:
        temp = []
        for i in feed_order:
            i.updateStatus()
            row = [i.name, i.room, i.status]
            temp.append(row)
        window["-TableRow-"].update(values = temp)
        if current_feed != None:

            img=feed_order[current_feed].video[feed_order[current_feed].current_frame]
            img = img.reshape(180, 320, 3)
            window["-IMAGE-"].update(data=cv2.imencode('.png', img)[1].tobytes())

window.close()