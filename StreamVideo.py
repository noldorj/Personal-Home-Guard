import utilsCore as utils
import threading
import datetime
import time
import cv2 as cv
#Import necessary libraries
from flask import Flask, render_template, Response
from PyQt5.QtCore import QThread
import logging as log
    
statusConfig = utils.StatusConfig()
ipCam, error = utils.camSource(statusConfig.data["camSource"])
        
RES_X = 854
RES_Y = 480

#Initialize the Flask app
appFlask = Flask(__name__) 

def gen_frames(): 

        while True:        
            conectado, frame = ipCam.read()
                
            if conectado:     
                frame = cv.resize(frame, (RES_X, RES_Y))                         
                # grab the current timestamp and draw it on the frame
                timestamp = datetime.datetime.now()
                cv.putText(frame, timestamp.strftime(
                "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                cv.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                  
                ret, buffer = cv.imencode('.jpg', frame)
                ret, buffer = cv.imencode('.jpg', frame)
                frame = buffer.tobytes()
        
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            else:
                break
      
 
@appFlask.route('/') 
def index():
    return render_template('index.html')

@appFlask.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

      
            
if __name__=="__main__":                
    
    
    log.info('StreamVideo::__init__')
    if error == '':
        appFlask.run(host='0.0.0.0', port=560, debug=True)
     
  
   
    
  

 
    
                    
            
            
            