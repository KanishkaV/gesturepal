import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os
import sys
from table import Table
from data_processing import Processor
import json
import pyautogui
import subprocess
from constants import GESTURE_DATA_DIRECTORY,DATASET_FRAME_LENGTH
from datetime import datetime
from collections import deque
from ttkthemes import ThemedTk

class App:
    def __init__(self, root):
        self.root = root
        # 'clam', 'alt', 'default', 'classic'
        # self.style = ttk.Style(root)
        # print(self.style.theme_names())
        # self.style.theme_use("alt")
        self.root.title("Gesture Pal")
        self.root.geometry("630x700")
        
        self.selected_tab="Configurations"
        self.frames=0
        self.frame_sequence_data={}
        self.train_data_count=0
        self.selected_gesture=None
        self.frame_queue = deque(maxlen=DATASET_FRAME_LENGTH)
        self.training=False

        self.device_selector_label = tk.Label(root, text="Select Video Device:",anchor="w")
        self.device_selector_label.grid(row=0,column=0,pady=10)
        self.device_selector = ttk.Combobox(root, values=detect_video_devices(),state="readonly")
        self.device_selector.grid(row=0,column=1,pady=10)
        self.device_selector.current(0)
        self.device_button = tk.Button(root, text="Switch Device", command=self.switch_device,anchor="e",fg="#FFFFFF",bg="#3A2AEE")
        self.device_button.grid(row=0,column=2,pady=10)
        
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=1,columnspan=3,pady=10)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Configurations")
        self.notebook.add(self.tab2, text="Train")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.root.bind("<space>", self.on_space_pressed)

   
        self.countdown_value = None

        self.gestures =  App.read_gestures_from_json()
        self.new_gestures =  App.list_new_gestures()
        
        self.processor=Processor(self)
   
        self.setup_tab1()
     
        self.setup_tab2()

  
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1920)  
        self.cap.set(4, 1080)  
        self.capture_video()
        
        

    def setup_tab1(self):
        self.table = Table(self.tab1, ["Item A", "Item B", "sh File", "Item D"], self.gestures)

        next_row = self.tab1.grid_size()[1]

        # self.win_key_btn = tk.Button(self.tab1, text="Press Windows Key", command=self.press_win_key)
        # self.win_key_btn.grid(row=next_row, column=0, pady=10, sticky=tk.W+tk.E) 

       
        # self.shell_script_btn = tk.Button(self.tab1, text="Run Shell Script", command=self.run_shell_script)
        # self.shell_script_btn.grid(row=next_row+1, column=0, pady=10, sticky=tk.W+tk.E) 

    def press_win_key(self):
        pyautogui.hotkey('alt','tab') 

    def run_shell_script(self):
        script_path = "test.sh" 
        subprocess.run(["bash", script_path])

    

    def setup_tab2(self):


        self.device_selector_label = tk.Label(self.tab2, text="Gesture :",anchor="w")
        self.device_selector_label.grid(row=0,column=0,pady=10)
        self.gesture_selector = ttk.Combobox(self.tab2, values=list(set(self.gestures + self.new_gestures)),state="readonly")
        self.gesture_selector.grid(row=0,column=1,pady=10)
        self.data_count_label= tk.Label(self.tab2, text="")
        self.data_count_label.grid(row=0,column=2,pady=10)
        self.train_button=tk.Button(self.tab2,text="Train",command=self.train_model,fg="#FFFFFF",state=tk.DISABLED)
        self.train_button.grid(row=0,column=3,pady=10)
        
        self.gesture_selector.bind("<<ComboboxSelected>>", self.on_gesture_selected)
        self.gesture_selector.bind('<space>', self.on_space_pressed)
         
        self.entry = tk.Entry(self.tab2)
        self.entry.grid(row=1,column=0,columnspan=2,pady=10)

        self.add_btn = tk.Button(self.tab2, text="Add new Gesture", command=self.add_item,fg="#FFFFFF",bg="#3A2AEE")
        self.add_btn.grid(row=1,column=2,columnspan=2,pady=10)

        self.video_label = tk.Label(self.tab2)
        self.video_label.grid(row=2,columnspan=4,pady=10)

    def read_gestures_from_json(filename="config/gesture.json"):
        if not os.path.exists(filename):
            return []

        with open(filename, "r") as infile:
            return json.load(infile)

    def list_new_gestures(directory=GESTURE_DATA_DIRECTORY):
        if not os.path.exists(directory):
            return []

        return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]


    def switch_device(self):
        selected_value = self.device_selector.get()
        device_number = int(selected_value.split(":")[0].split()[-1])
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(device_number)
        self.cap.set(3, 1920)
        self.cap.set(4, 1080) 


    def on_space_pressed(self, event):
        if self.selected_gesture and self.countdown_value is None:
            self.countdown_value = 4
            self.decrease_countdown()

    def decrease_countdown(self):
        if self.countdown_value > 0:
            self.countdown_value -= 1
            self.root.after(1000, self.decrease_countdown) 
        else:
            self.countdown_value = None 

    def add_item(self):
        item = self.entry.get()
        if item and item not in self.gesture_selector['values']:
            self.gesture_selector['values'] = (*self.gesture_selector['values'], item)
        

            os.makedirs(os.path.join(GESTURE_DATA_DIRECTORY, item), exist_ok=True)
        
        self.entry.delete(0, tk.END)

    def capture_video(self):
        if(self.processor.hand_tracking==None):
            self.processor.start_hand_tracking()
        ret, frame = self.cap.read()
        if ret:
           
            frame=cv2.flip(frame,1)
            gesture=self.processor.detect_hand_pose(frame)
            key_points=self.processor.extract_hand_keypoints(gesture)
            self.frame_queue.append(key_points.tolist())
            
            if self.selected_tab == "Train":
                self.processor.draw_gesture(frame,gesture)
                self.update_video(frame)
                if self.frames>0:
                    self.frames-=1
                elif self.training==True:
                    self.save_data(f"{GESTURE_DATA_DIRECTORY}/{self.selected_gesture}/{self.train_data_count+1}.json",list(self.frame_queue))
                    self.update_no_of_datasets()
                    self.training=False     
            else:
                if len(self.frame_queue)==DATASET_FRAME_LENGTH:
                    if(self.frames==0):
                        self.processor.predict(list(self.frame_queue))
                        self.frames=8
                    else:
                        self.frames-=1
                        
        self.root.after(1, self.capture_video)
    
    def update_video(self,frame):      
        if self.frames==0:
            if not self.selected_gesture:
                cv2.putText(frame, "Select a gesture", 
                                (int(frame.shape[1]/2 - 180), int(frame.shape[0]*3/7)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 5)
            elif  self.countdown_value==None:
                cv2.putText(frame, "Press space to", 
                                (int(frame.shape[1]/2 - 180), int(frame.shape[0]*3/7)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 5)
                cv2.putText(frame, " start recording", 
                                (int(frame.shape[1]/2 - 200), int(frame.shape[0]*4/7)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 5)
            elif self.countdown_value==0:
                cv2.putText(frame, "Start", 
                                (int(frame.shape[1]/2 - 100), int(frame.shape[0]/2)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
                
                self.frames=DATASET_FRAME_LENGTH
                self.training=True
            else :
                cv2.putText(frame, str(self.countdown_value), 
                                (int(frame.shape[1]/2 - 50), int(frame.shape[0]/2)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
        
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.video_label.config(image=photo)
        self.video_label.image = photo
        
    def on_tab_changed(self, event):
        self.selected_tab = self.notebook.tab(self.notebook.select(), "text")
        self.reset_frame_sequence()
        self.frames=0
        
        
    def save_data(self,path,data):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, "w") as outfile:
            json.dump(data, outfile)
            
    def reset_frame_sequence(self):
        self.frame_sequence_data.clear()

    def on_gesture_selected(self,event):
        self.selected_gesture = self.gesture_selector.get()
        self.update_no_of_datasets()
        
    def update_no_of_datasets(self):
        try:
            self.train_data_count=len(os.listdir(f"{GESTURE_DATA_DIRECTORY}/{self.selected_gesture}/"))
        except FileNotFoundError:
            self.train_data_count=0
            
        self.data_count_label.config(text=f"No of data available : {self.train_data_count}")
        self.update_train_button_status()
        
    def train_model(self):
        self.processor.train_model(self.selected_gesture)
        
    def update_train_button_status(self):
        if self.train_data_count>=15:
            self.train_button.config(state=tk.NORMAL)
        else:
            self.train_button.config(state=tk.DISABLED)
    def resource_path(self,relative_path):
        try:
                base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    
def detect_video_devices():
    devices = []
    for i in range(10): 
        video_device_path = f"/dev/video{i}"
        sys_info_path = f"/sys/class/video4linux/video{i}/name"
        if os.path.exists(video_device_path):
            device_name = f"Device {i}"
            if os.path.exists(sys_info_path):
                with open(sys_info_path, 'r') as f:
                    device_name = f.read().strip()
            devices.append(f"Device {i}: {device_name}")
    return devices

# root = tk.Tk()
root=ThemedTk(theme="breeze")
app = App(root)
root.mainloop()
