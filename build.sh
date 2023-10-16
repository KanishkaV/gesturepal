pip install -r requirements.txt
pyinstaller --onefile --add-data="gesture_model.h5:." --add-data="config/:config/" --hidden-import "mediapipe"  --name GesturePal App.py