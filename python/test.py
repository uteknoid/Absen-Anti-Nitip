from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
import requests
import dlib
import numpy as np
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors


# from win32com.client import Dispatch

from gtts import gTTS
from playsound import playsound

def speak(str1):
    audio_indonesia = gTTS(text=str1, lang="id")
    audio_indonesia.save("audio.mp3")
    playsound("audio.mp3")
    os.remove("audio.mp3")

    # speak=Dispatch(("SAPI.SpVoice"))
    # vcs = speak.GetVoices()
    # speak.Voice
    # speak.SetVoice(vcs.Item(1))
    # speak.Speak(str1)

video=cv2.VideoCapture(0)
facedetect=cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
smile_detector = cv2.CascadeClassifier('data/haarcascade_smile.xml')
with open('data/names.pkl', 'rb') as w:
    LABELS=pickle.load(w)
with open('data/faces.pkl', 'rb') as f:
    FACES=pickle.load(f)

knn=KNeighborsClassifier(n_neighbors=4)
knn.fit(FACES, LABELS)

similarity = NearestNeighbors(n_neighbors=30,
                         metric='cosine',
                         algorithm='brute',
                         n_jobs=-1)
similarity.fit(FACES)



imgBackground=cv2.imread("background.png")

COL_NAMES = ['NAMA', 'WAKTU']

nama_pengabsen = ''

threshold = 0.2
eye_closed = False
kedip = 'X'
color_kedip = (0,0,255)
senyum = 'X'
color_senyum = (0,0,255)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")

def mid_line_distance(p1 ,p2, p3, p4):
    """compute the euclidean distance between the midpoints of two sets of points"""
    p5 = np.array([int((p1[0] + p2[0])/2), int((p1[1] + p2[1])/2)])
    p6 = np.array([int((p3[0] + p4[0])/2), int((p3[1] + p4[1])/2)])

    return norm(p5 - p6)

def aspect_ratio(landmarks, eye_range):
    # Get the eye coordinates
    eye = np.array(
        [np.array([landmarks.part(i).x, landmarks.part(i).y]) 
         for i in eye_range]
        )
    # compute the euclidean distances
    B = norm(eye[0] - eye[3])
    A = mid_line_distance(eye[1], eye[2], eye[5], eye[4])
    # Use the euclidean distance to compute the aspect ratio
    ear = A / B
    return ear

while True:
    ret,frame=video.read()
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces=facedetect.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=8, minSize=(50, 50), flags=cv2.CASCADE_SCALE_IMAGE)
    
    frame_crop_for_eye = cv2.resize(frame, (600, 450))
    rects = detector(gray, 0)

    for rect in rects:
        landmarks = predictor(gray, rect)

        # Use the coordinates of each eye to compute the eye aspect ratio.
        left_aspect_ratio = aspect_ratio(landmarks, range(42, 48))
        right_aspect_ratio = aspect_ratio(landmarks, range(36, 42))
        ear = (left_aspect_ratio + right_aspect_ratio) / 2.0

        if ear < threshold:
            eye_closed = True
        elif ear >= threshold and eye_closed:
            kedip = 'Berhasil'
            color_kedip = (0,255,0)
            eye_closed = False

        for n in range(36, 48):
            x = landmarks.part(n).x
            y = landmarks.part(n).y

            cv2.putText(frame, "Pejamkan Mata :", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, " {}".format(kedip), (200, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_kedip, 2)
            
    smile = smile_detector.detectMultiScale(gray,
    scaleFactor= 1.7, minNeighbors=50,
    minSize=(25, 25))
    
    for (x, y, w, h) in smile:
        if len(smile) > 0:
            senyum = 'Berhasil'
            color_senyum = (0,255,0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)
    cv2.putText(frame, "Perlihatkan Gigi :", (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, " {}".format(senyum), (200, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_senyum, 2)
    
    for (x,y,w,h) in faces:
        crop_img=frame[y:y+h, x:x+w, :]
        resized_img=cv2.resize(crop_img, (50,50), interpolation=cv2.INTER_AREA).flatten().reshape(1,-1)
        output=knn.predict(resized_img)
        nbrs = similarity.kneighbors(resized_img, 2, return_distance=False)
        ts=time.time()
        date=datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        # timestamp=datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        timestamp=date+datetime.fromtimestamp(ts).strftime(" %H:%M")
        exist=os.path.isfile("Absen/Absen_" + date + ".csv")
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 1)
        cv2.rectangle(frame,(x,y-15),(x+w,y+h),(0,128,255),2)
        cv2.rectangle(frame,(x,y+15),(x+w,y-15),(0,128,255),-1)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,128,255), 1)
        attendance=[str(output[0]), str(timestamp)]

        if nbrs[0][0] > 0:
            cv2.putText(frame, str(output[0]), (x,y+7), cv2.FONT_HERSHEY_SIMPLEX, .6, (255,255,255), 1, cv2.LINE_AA, False)
            nama_pengabsen = output[0]

        else:
            cv2.putText(frame, "UNKNOWN", (x,y+7), cv2.FONT_HERSHEY_SIMPLEX, .6, (255,255,255), 1, cv2.LINE_AA, False)
            nama_pengabsen = ''
            kedip = 'X'
            color_kedip = (0,0,255)
            senyum = 'X'
            color_senyum = (0,0,255)

        
    imgBackground[140:140 + 480, 40:40 + 640] = frame
    cv2.imshow("ABSEN ANTI NITIP v1.0",imgBackground)
    # cv2.moveWindow("ABSEN ANTI NITIP v1.0", 640, 50) 
    k=cv2.waitKey(1)
    if kedip=='Berhasil' and senyum=='Berhasil':
        if nama_pengabsen != '':

            url = 'http://localhost/abwa/input.php'
            data = {
                'nama': str(output[0]),
                'waktu': str(datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))
                }
            x = requests.post(url, data=data)
            
            if x.text == 'berhasil':
                if exist:
                    with open("Absen/Absen_" + date + ".csv", "+a", newline='') as csvfile:
                        writer=csv.writer(csvfile, delimiter=';')
                        writer.writerow(attendance)
                    csvfile.close()
                else:
                    with open("Absen/Absen_" + date + ".csv", "+a", newline='') as csvfile:
                        writer=csv.writer(csvfile, delimiter=';')
                        writer.writerow(COL_NAMES)
                        writer.writerow(attendance)
                    csvfile.close()
            
                speak('Halo '+str(output[0])+", Terimakasih Sudah Absen")
            if x.text == 'sudah':
                speak('Maaf, '+str(output[0])+" Sudah Melakukan Absen")
            if x.text == 'gagal':
                speak('Absen Gagal, Tolong Coba Lagi!')
            
            kedip = 'X'
            color_kedip = (0,0,255)
            senyum = 'X'
            color_senyum = (0,0,255)
        else:
            speak('Maaf, Anda belum terdaftar!')
            kedip = 'X'
            color_kedip = (0,0,255)
            senyum = 'X'
            color_senyum = (0,0,255)

    if k==ord('q'):
        break
video.release()
cv2.destroyAllWindows()