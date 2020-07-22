import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
import scipy.io.wavfile
import os

## converts file to wav
def audio_convert(path):
    root_path = path.split('.')[0]
    audio = AudioSegment.from_file(path)
    audio.export(root_path + ".wav", format="wav")

    return root_path + ".wav"

## detects where there is noise in audio file
def audio_detect(path):
    rate, audio = scipy.io.wavfile.read(path)
    time = np.arange(0, float(audio.shape[0]), 1) / rate

    noise = []
    for point in range(len(audio)):
        if abs(audio[point]) > 0: ## this threshold could be varied 
            noise += [point]
    
    return noise, rate, time

## visualizes audio amplitude
def audio_viz(path):
    rate, audio = scipy.io.wavfile.read(path)
    time = np.arange(0, float(audio.shape[0]), 1) / rate

    fig = plt.figure(1)
    plt.subplot(111)
    plt.plot(time, audio, linewidth=0.1, alpha=0.7)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    root_path = path.split('.')[0]
    fig.savefig(root_path + '.jpg')

## calculates audio metrics
def audio_metrics(noise, rate, time):
    total_time = time[len(time) - 1]
    talking_sec = len(noise) / rate
    talking_pct = talking_sec / total_time
    
    return talking_sec, talking_pct

## runs audio script
def audio_run(path):
    path_ext = path.split('.')[1]
    if path_ext != '.wav':
        path = audio_convert(path)

    noise, rate, time = audio_detect(path)
    talking_sec, talking_pct = audio_metrics(noise, rate, time)
    
    return noise, rate, time, talking_sec, talking_pct



