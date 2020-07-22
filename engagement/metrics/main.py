from audio import audio_run
from transcript import transcript_run
from sentiment import sentiment_run
from video import video_run
from emotion import emotion_run, emotion_model
import json
import os
from google.cloud import firestore

def get_files(parent_uuid):
    file_list = os.listdir('/home/lleonyuan/files/{}'.format(parent_uuid))
    file_list = list(map(lambda x: os.path.join('/home/lleonyuan/files', parent_uuid, x), file_list))
    audio_files = list(filter(lambda x: x[-3:] == "wav", file_list))
    video_files = list(filter(lambda x: x[-3:] == "mp4", file_list))
    return (video_files[0], audio_files)

def script_start(parent_uuid):
    ## run audio
    video_file, audio_files = get_files(parent_uuid)
    NUM_PEOPLE = len(audio_files)
    audio_info = {}
    audio_metrics = {}
    for idx, f in enumerate(audio_files):
        noise, rate, time, talking_sec, talking_pct = audio_run(f)
        info = {idx: {'noise':noise, 'rate':rate, 'time':time}}
        audio_info.update(info)
        metrics = {idx : {'talking_sec':talking_sec, 'talking_pct':talking_pct}}
        audio_metrics.update(metrics)

    print('--- AUDIO DONE ---')

    ## run transcript
    transcript_files = []
    for idx, f in enumerate(audio_files):
        transcript_file = transcript_run(f)
        transcript_files += [transcript_file]

    print('--- TRANSCRIPT DONE ---')
    
    ## run sentiment
    sentiment_metrics = {}
    for idx, f in enumerate(transcript_files):
        sentiment_pred, sentiment_prob = sentiment_run(f)
        metrics = {idx : {'sentiment_pred':sentiment_pred, 'sentiment_prob':sentiment_prob}}
        sentiment_metrics.update(metrics)

    print('--- SENTIMENT DONE ---')

    ## run video
    video_info = {}
    video_metrics = {}
    for idx, f in enumerate(audio_files):
        noise = audio_info[idx]['noise']
        rate = audio_info[idx]['rate']
        time = audio_info[idx]['time']
        frames, video_sec, video_pct = video_run(video_file, noise, rate, time)
        info = {idx: {'frames':frames}}
        video_info.update(info)
        metrics = {idx : {'video_sec':video_sec, 'video_pct':video_pct}}
        video_metrics.update(metrics)

    print('--- VIDEO DONE ---')

    ## run emotion
    emotion_metrics = {}
    emotion_classifier = emotion_model()
    for idx in range(NUM_PEOPLE):
        frames = video_info[idx]['frames']
        emotion_freqs = emotion_run(video_file, frames, emotion_classifier)
        metrics = {idx : emotion_freqs}
        emotion_metrics.update(metrics)

    print('--- EMOTION DONE ---')

    ## create json
    print(audio_metrics)
    print(sentiment_metrics)
    print(video_metrics)
    print(emotion_metrics)

    for key in audio_metrics:
        audio_metrics[key].update(sentiment_metrics[key])
        audio_metrics[key].update(video_metrics[key])
        audio_metrics[key].update(emotion_metrics[key])

    # with open("zoom_ads.json", "w") as outfile: 
    #     json.dump(audio_metrics, outfile) 

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/home/lleonyuan/marble-api/Marble-8181cca99a94.json'
    db = firestore.Client()
    doc_ref = db.collection(u'classroom').document(parent_uuid)
    doc_ref.update({
        "state": "POPULATED",
        "data": json.loads(json.dumps(audio_metrics)),
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    print('--- JSON DONE ---') 
