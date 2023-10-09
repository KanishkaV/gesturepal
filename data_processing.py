import mediapipe as mp
import cv2
from tensorflow.keras.models import load_model
from constants import DATASET_FRAME_LENGTH
import numpy as np
from datetime import datetime, timedelta

class Processor:
    def __init__(self,parent):
        self.parent=parent
        self.mp_hand = mp.solutions.hands
        self.hand_tracking=None
        self.drawing_util=mp.solutions.drawing_utils
        model_path = self.parent.resource_path("gesture_model.h5")
        self.model=load_model(model_path)
        self.last_pred=datetime.now()
    
    def detect_hand_pose(self,frame):
        if(self.hand_tracking==None):
            return
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        frame.flags.writeable=False
        results=self.hand_tracking.process(frame)
        frame.flags.writeable=True
        frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        return results
    
    def start_hand_tracking(self):
        self.hand_tracking=self.mp_hand.Hands( static_image_mode=False,model_complexity=1,min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    def stop_hand_tracking(self):
        self.hand_tracking.close()
        self.hand_tracking=null
        
    def draw_gesture(self,image,gesture_results):
        
        if gesture_results.multi_hand_landmarks:
            for landmark in gesture_results.multi_hand_landmarks:
                self.drawing_util.draw_landmarks(image, landmark, self.mp_hand.HAND_CONNECTIONS)

    def extract_hand_keypoints(self,results):
        lh=np.empty((0))
        rh=np.empty((0))
        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks)<2:
                if results.multi_handedness[0].classification[0].index==1:
                    lh=np.zeros(21*3)
                    rh=self.get_points_of_hand(results.multi_hand_landmarks[0])
                else:
                    rh=np.zeros(21*3)
                    lh=self.get_points_of_hand(results.multi_hand_landmarks[0])
            else:
                lh=self.get_points_of_hand(results.multi_hand_landmarks[0])
                rh=self.get_points_of_hand(results.multi_hand_landmarks[1])
        else:
            return np.zeros(126)               
        return np.concatenate([lh,rh])                
        # if(results.multi_hand_landmarks):
        #     x=0
        #     for l in results.multi_hand_landmarks:
        #         print(len(l.landmark))
        #         x+=1
        #     print(x)
        # if(results.multi_handedness):
        #     for hand in results.multi_handedness:
        #         print(hand.classification[0].index)
        # if(results.multi_hand_world_landmarks):
        #     x=0
        #     print(len(results.multi_hand_world_landmarks))
        #     for l in results.multi_hand_world_landmarks:
        #         print(len(l.landmark))
        #         x+=1
        #     print(x)
        # print("-------------------")
        # data = np.empty((0))
        # 'multi_hand_landmarks', 'multi_hand_world_landmarks', 'multi_handedness'
        # if results.pose_landmarks:
        #     for landmark in results.pose_landmarks.landmark:
        #             data=np.append(data,np.array([landmark.x,landmark.y,landmark.z,landmark.visibility]).flatten())
        # else:
        #     data=np.append(data,np.zeros(33*4))

        # if results.right_hand_landmarks:
        #     for landmark in results.right_hand_landmarks.landmark:
        #             data=np.append(data,np.array([landmark.x,landmark.y,landmark.z]).flatten())
        # else:
        #     data=np.append(data,np.zeros(21*3))
            
        # if results.left_hand_landmarks:
        #     for landmark in results.left_hand_landmarks.landmark:
        #             data=np.append(data,np.array([landmark.x,landmark.y,landmark.z]).flatten())
        # else:
        #     data=np.append(data,np.zeros(21*3))
            

        # landmark_size = 258
        # while len(data) < landmark_size:
        #     data.append(0)
        # return data
    def get_points_of_hand(self,landmarks):
        data=np.empty((0))
        for landmark in landmarks.landmark:
            data=np.concatenate([data,[landmark.x,landmark.y,landmark.z]])
        return data
    
    def train_model(self,gesture):
        print("train")
        
    def predict(self,data):
        # return
        y=np.expand_dims(np.array(data), axis=0)
        print(y.shape)
        x=self.model.predict(y,verbose=0)
        # # print(data)
       
        res=np.argmax(x)
        accuracy=x[0][res]
        current_time=datetime.now()
        if current_time-self.last_pred>=timedelta(seconds=5):
        
            if(accuracy>0.86):
                self.parent.save_data("dtest/dtest.json",y.tolist())
                print(accuracy)
                print(res)
                print(self.parent.gestures[res])
                print("-------------")
                self.last_pred=datetime.now()
        

        