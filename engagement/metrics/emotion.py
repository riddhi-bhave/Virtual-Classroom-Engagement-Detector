import cv2
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing import image
import numpy as np
from keras.models import load_model
from statistics import mode
from imageio import imread
from skimage.transform import resize
from scipy.io import loadmat
import pandas as pd
from random import shuffle
import os

def apply_offsets(face_coordinates, offsets):
    x, y, width, height = face_coordinates
    x_off, y_off = offsets
    return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)

def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x

def emotion_model():
    emotion_model_path = '/home/lleonyuan/marble-api/emotion_model.hdf5'
    emotion_classifier = load_model(emotion_model_path)
    return emotion_classifier

## extracts emotions from given video frames
def emotion_extract(path, frames, emotion_classifier):
    emotion_labels = {0:'angry',1:'disgust',2:'fear',3:'happy',4:'sad',5:'surprise',6:'neutral'}

    frame_window = 10
    emotion_offsets = (20, 40)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    emotion_target_size = emotion_classifier.input_shape[1:3]
    emotion_window = []

    cap = cv2.VideoCapture(path) 

    emotion_freqs = {}
    numFrames = 0.0
    
    while cap.isOpened(): # True:
        ret, bgr_image = cap.read()
        if ret == False:
            cap.release()
            break
        numFrames+=1.0
        if (numFrames in frames):
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

            faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            for face_coordinates in faces:
                x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
                gray_face = gray_image[y1:y2, x1:x2]
                try:
                    gray_face = cv2.resize(gray_face, (emotion_target_size))
                except:
                    continue

                gray_face = preprocess_input(gray_face, True)
                gray_face = np.expand_dims(gray_face, 0)
                gray_face = np.expand_dims(gray_face, -1)
                emotion_prediction = emotion_classifier.predict(gray_face)
                emotion_probability = np.max(emotion_prediction)
                emotion_label_arg = np.argmax(emotion_prediction)
                emotion_text = emotion_labels[emotion_label_arg]
                emotion_window.append(emotion_text)

                if len(emotion_window) > frame_window:
                    emotion_window.pop(0)
                try:
                    emotion_mode = mode(emotion_window)
                except:
                    continue
            
                #logging frequencies of emotions
                if(emotion_text in emotion_freqs): 
                    emotion_freqs[emotion_text] += 1.0
                else: 
                    emotion_freqs[emotion_text] = 1.0

    cap.release()
    return emotion_freqs.items()

## runs emotion script
def emotion_run(path,frames, emotion_classifier):
    print(emotion_classifier)
    emotion_freqs = emotion_extract(path, frames, emotion_classifier)
    sum_values = 0
    results = {}
    for key, value in emotion_freqs: 
        sum_values += value
    for key, value in emotion_freqs:
        emotion_pct = value / sum_values
        result = {key : emotion_pct}
        results.update(result)

    return results
