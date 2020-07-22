import os
from google.cloud import speech

## converts file to wav
def transcript_convert(path):
    root_path = path.split('.')[0]
    return root_path + ".wav"

## extracts transcript using google cloud
def transcript_extract(path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/home/lleonyuan/marble-api/key.json'
    client = speech.SpeechClient()
    path = path.split("/")
    operation = client.long_running_recognize(
        audio = speech.types.RecognitionAudio(uri='gs://marble-video-bucket/' + path[-2] + "/" + path[-1]),
        config=speech.types.RecognitionConfig(encoding='LINEAR16',language_code='en-US'),
    )

    response = operation.result()
    text = ""
    for result in response.results:
        text += result.alternatives[0].transcript
    return text

## runs transcript script
def transcript_run(path):
    path = transcript_convert(path)
    text = transcript_extract(path)
    return text


