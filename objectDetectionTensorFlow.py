import cv2 as cv

classes = ["background", "pessoa", "bicileta", "carro", "moto", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
    "unknown", "stop sign", "parking meter", "bench", "bird", "gato", "cachorro", "horse",
    "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "unknown", "backpack",
    "umbrella", "unknown", "unknown", "handbag", "tie", "suitecase", "frisbee", "skis",
    "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "unknown", "wine glass", "cup", "fork", "knife",
    "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog",
    "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "unknown", "dining table",
    "unknown", "unknown", "toilet", "unknown", "tv", "laptop", "mouse", "remote", "keyboard",
    "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "unknown",
"book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush" ]

def objectDetection(img, idObjeto, listRectanglesDetected, detection, rows, cols, cvNet):
    box = []
    listObjectsTracking = []
    listRectanglesDetected = []

    #img = cv.imread(img)
    if img is not None:
        rows = img.shape[0]
        cols = img.shape[1]
        resized = cv.resize(img, (300,300)) 
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
