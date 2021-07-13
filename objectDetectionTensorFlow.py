import cv2 as cv

# classes = ["background", "pessoa", "bicileta", "carro", "moto", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
    # "unknown", "stop sign", "parking meter", "bench", "bird", "gato", "cachorro", "horse",
    # "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "unknown", "backpack",
    # "umbrella", "unknown", "unknown", "handbag", "tie", "suitecase", "frisbee", "skis",
    # "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    # "surfboard", "tennis racket", "bottle", "unknown", "wine glass", "cup", "fork", "knife",
    # "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog",
    # "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "unknown", "dining table",
    # "unknown", "unknown", "toilet", "unknown", "tv", "laptop", "mouse", "remote", "keyboard",
    # "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "unknown",
# "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush" ]

class_names = []
with open("config/classes.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

def objectDetectionYolo(frame, cvNet):
    #box = []
    listObjectsTracking = []
    listRectanglesDetected = []
        
    model = cv.dnn_DetectionModel(cvNet)
    model.setInputParams(size=(512, 512), scale=1/255, swapRB=True)
    
    CONFIDENCE_THRESHOLD = 0.2
    NMS_THRESHOLD = 0.4

    #frame = ipCam.imread(img)
    
    if frame is not None:
                
        rows = frame.shape[0]
        cols = frame.shape[1] 
        #initial_w = ipCam.get(3)
        #initial_h = ipCam.get(4)
        
        # print(' ')
        # print('initial_w: {}'.format(initial_w))
        # print('initial_h: {}'.format(initial_h))
        # print(' ')        
        
        # print(' ')
        # print('rows: {}'.format(rows))
        # print('cols: {}'.format(cols))
        # print(' ')
        
        #resized = cv.resize(img, (416,416)) 
        
        if cvNet is not None:
            
            #frame = cv.resize(frame, (rows, cols)) 
            
            classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
            
            for (classid, score, box) in zip(classes, scores, boxes):                

                if score > 0.20:
                
                    # left = box[0] * int((rows / 416)) 
                    # top = box[1] * int((cols / 416)) 
                    # right = box[2] * int((rows / 416)) 
                    # bottom = box[3] * int((cols / 416))

                    left = box[0] 
                    top = box[1] 
                    right = box[2] + box[0]
                    bottom = box[3] + box[1]
                    
                    # print(' ')
                    # print('left: {}'.format(left))
                    # print('top: {}'.format(top))
                    # print('right: {}'.format(right))
                    # print('bottom: {}'.format(bottom))
                    # print(' ')
                    
                    # left = box[0] * cols
                    # top = box[1] * rows
                    #right = box[2] * cols
                    #bottom = box[3] * rows
                    
                    # print(' ')
                    # print('left: {}'.format(left))
                    # print('top: {}'.format(top))
                    # print('right: {}'.format(right))
                    # print('bottom: {}'.format(bottom))
                    # print(' ')

                    idx = classid[0] #indice da classe identificada
                    #label = "{}: {:.2f}%".format(classes[idx],score*100)
                    score[0] = score[0] * 100
                    label = "%s : %f" % (class_names[classid[0]], score[0])
                    
                    classe = class_names[classid[0]]
                    #print('type classe: {}'.format(type(classe)))
                    
                    # print('label: {}'.format(label))
                    # print('classe: {}'.format(classe))
                    # print('score: {}'.format(score[0]))

                    
                    boxR = (left, top, right, bottom, label, idx, classe, score[0])
                    #boxR = (box, label, idx, classe, score[0])                                       
                    #print('detected score: {:f}'.format(score))
                    

                    if classe == "person" or \
                        classe == "bicycle" or \
                        classe == "car" or \
                        classe == "motorcycle":

                            #print('classe detectada: {}'.format(class_names[idx]))
                            boxTracking = (left, top, right, bottom)
                            #boxTracking = box

                            #print('box: {}'.format(box))
                            #print('boxR: {}'.format(boxR))
                            
                            listObjectsTracking.append(boxTracking)
                            listRectanglesDetected.append(boxR)


    return listRectanglesDetected, listObjectsTracking
        
     


def objectDetection(img, idObjeto, listRectanglesDetected, detection, rows, cols, cvNet):
    box = []
    listObjectsTracking = []
    listRectanglesDetected = []

    #img = cv.imread(img)
    if img is not None:
        rows = img.shape[0]
        cols = img.shape[1]
        resized = cv.resize(img, (300,300)) 
        
        if cvNet is not None:
            cvNet.setInput(cv.dnn.blobFromImage(resized, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
            cvOut = cvNet.forward()

            for detection in cvOut[0,0,:,:]:

                score = float(detection[2])

                if score > 0.35:

                    left = int(detection[3] * cols)
                    top = int(detection[4] * rows)
                    right = int(detection[5] * cols)
                    bottom = int(detection[6] * rows)

                    idx = int(detection[1]) #indice da classe identificada
                    label = "{}: {:.2f}%".format(classes[idx],score*100)
                    classe = classes[idx]

                    box = (left, top, right, bottom, label, idx, classe)
                    
                    #print('detected score: {:f}'.format(score))


                    if  classes[idx] is 'pessoa'   or \
                        classes[idx] is 'gato'     or \
                        classes[idx] is 'cachorro' or \
                        classes[idx] is 'carro'    or \
                        classes[idx] is 'moto': 


                        #print('classe detectada: {}'.format(classes[idx]))
                        boxTracking = (left, top, right, bottom)

                        listObjectsTracking.append(boxTracking)

                        listRectanglesDetected.append(box)


    return listRectanglesDetected, listObjectsTracking
