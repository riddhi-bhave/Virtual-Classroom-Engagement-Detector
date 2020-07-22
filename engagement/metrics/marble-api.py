from flask import Flask                                                                            
import threading
import os                                                                                          
from main import script_start
                                                                                                    
app = Flask(__name__)                                                                              

@app.route("/ffmpeg/<parent_name>/<filename>")                                                     
def ffmpeg_convert(parent_name, filename):                                                         
    print(parent_name, filename)                                                                   
    wav_name = filename[0: filename.rindex('.')]                                                   
    cmd = "ffmpeg -i ~/files/{}/{} -ac 1 ~/files/{}/{}.wav"                                        
    os.system(cmd.format(parent_name, filename, parent_name, wav_name))                            
                                                                                                   
    return "Running FFMpeg for video file {}".format(filename)                                     
                                                                                                    
@app.route("/script/<uuid>")                                                                       
def script(uuid):                                                                                  
    print("Script started running")
    script_call = threading.Thread(target=script_start, args=(uuid,))
    script_call.start()
    return "Script for {} uuid has started running".format(uuid)            
