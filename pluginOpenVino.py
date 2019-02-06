#!/usr/bin/env python
"""
 Copyright (c) 2018 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from __future__ import print_function
import sys
import os
from argparse import ArgumentParser
import cv2
import time
import logging as log
from  openvino.inference_engine import IENetwork, IEPlugin

#def main():
log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
#labels_map = ["background", "pessoa", "carro", "bicileta"]
labels_map = ["background", "carro", "pessoa", "bicileta"]

#lista de boxes detectados
listRectanglesDetected = []
listObjectsTracking = []


def initOpenVino(device, model_xml, model_bin):

    cpu_extension = 'computer_vision_sdk/deployment_tools/inference_engine/lib/ubuntu_16.04/intel64/libcpu_extension_avx2.so'

    plugin_dir = 'computer_vision_sdk/deployment_tools/inference_engine/lib/ubuntu_16.04/intel64/'


    if device == 'MYRIAD':
        log.info('loading MYRIAD plugins...')
        log.info('Model XML: {}'.format(model_xml))
        log.info('Model Bin: {}'.format(model_bin))
        #model_xml = os.getcwd() + '/dlModels/openvino/pedestrian-and-vehicle-detector-adas-0001/FP16/pedestrian-and-vehicle-detector-adas-0001.xml'
        #model_bin = os.getcwd() + '/dlModels/openvino/pedestrian-and-vehicle-detector-adas-0001/FP16/pedestrian-and-vehicle-detector-adas-0001.bin'

        #model_xml = 'computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP16/pedestrian-detection-adas-0002.xml'
        #model_bin = 'computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP16/pedestrian-detection-adas-0002.bin'

    elif device == 'CPU':
        log.info('loading CPU plugins...')
        log.info('Model XML: {}'.format(model_xml))
        log.info('Model Bin: {}'.format(model_bin))
        #model_xml = 'computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP32/pedestrian-detection-adas-0002.xml'
        #model_bin = 'computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP32/pedestrian-detection-adas-0002.bin'

        #model_bin = 'computer_vision_sdk/deployment_tools/intel_models/pedestrian-and-vehicle-detector-adas-0001/FP32/pedestrian-and-vehicle-detector-adas-0001.bin'
        #model_xml = 'computer_vision_sdk/deployment_tools/intel_models/pedestrian-and-vehicle-detector-adas-0001/FP32/pedestrian-and-vehicle-detector-adas-0001.xml'

        #model_bin = 'computer_vision_sdk/deployment_tools/intel_models/person-detection-retail-0002/FP32/person-detection-retail-0002.bin'
        #model_xml = 'computer_vision_sdk/deployment_tools/intel_models/person-detection-retail-0002/FP32/person-detection-retail-0002.xml'

        #model_bin = 'computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.bin'
        #model_xml = 'computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.xml'

        #model_bin = 'computer_vision_sdk/deployment_tools/intel_models/person-detection-retail-0013/FP32/person-detection-retail-0013.bin'
        #model_xml = 'computer_vision_sdk/deployment_tools/intel_models/person-detection-retail-0013/FP32/person-detection-retail-0013.xml'

    elif device == 'GPU':
        log.info('loading GPU plugins...')
        log.info('Model XML: {}'.format(model_xml))
        log.info('Model Bin: {}'.format(model_bin))


    # Plugin initialization for specified device and load extensions library if specified
    log.info("Initializing plugin for {} device...".format(device))

    plugin = IEPlugin(device=device, plugin_dirs=plugin_dir)

    if cpu_extension and 'CPU' in device:
        plugin.add_cpu_extension(cpu_extension)

    # Read IR
    log.info("Reading IR...")
    net = IENetwork(model=model_xml, weights=model_bin)

    if plugin.device == "CPU":
        supported_layers = plugin.get_supported_layers(net)
        not_supported_layers = [l for l in net.layers.keys() if l not in supported_layers]
        if len(not_supported_layers) != 0:
            log.error("Following layers are not supported by the plugin for specified device {}:\n {}".
                      format(plugin.device, ', '.join(not_supported_layers)))
            log.error("Please try to specify cpu extensions library path in demo's command line parameters using -l "
                      "or --cpu_extension command line argument")
            sys.exit(1)
    assert len(net.inputs.keys()) == 1, "Demo supports only single input topologies"
    assert len(net.outputs) == 1, "Demo supports only single output topologies"
    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))
    log.info("Loading IR to the plugin...")
    exec_net = plugin.load(network=net, num_requests=2)
    n, c, h, w = net.inputs[input_blob].shape
    nchw = [n,c,h,w]
    #print('nchw: {}'.format(nchw))
    del net

    log.info("Starting inference in async mode...")
    log.info("To switch between sync and async modes press Tab button")
    log.info("To stop the demo execution press Esc button")
    is_async_mode = True
    log.info("Init Openvino done")
    #print('nchw from pOpenVino.init: {}, {}, {}, {}'.format(nchw[0], nchw[1], nchw[2], nchw[3]))

    return nchw, exec_net, input_blob, out_blob


def getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold):

 # Read and pre-process input image
    #if args.input == 'cam':
    #    input_stream = 0
    #else:
    #    input_stream = args.input
    #    assert os.path.isfile(args.input), "Specified input file doesn't exist"
    #if labels:
    #    with open(labels, 'r') as f:
    #        labels_map = [x.strip() for x in f]
    #else:
    #    labels_map = None

    xmin, xmax, ymin, ymax, det_label, class_id, label  = 0, 0, 0, 0, ' ', 0, ' '

    n, c, h, w = nchw[0], nchw[1], nchw[2], nchw[3]

    cap = ipCam
    #cap = cv2.VideoCapture(input_stream)

    #ret, frame = cap.read()
    #while cap.isOpened():

    ret, next_frame = cap.read()
    if next_frame is None or ret is False:
        log.error("Error capturing next_frame")

    else:

        #while(ret is False):
        #    log.error('Error capturing next_frame - capturing again...')
        #ret, next_frame = cap.read()

        #if not ret:
        #    break


        initial_w = cap.get(3)
        initial_h = cap.get(4)
        # Main sync point:
        # in the truly Async mode we start the NEXT infer request, while waiting for the CURRENT to complete
        # in the regular mode we start the CURRENT request and immediately wait for it's completion
        #inf_start = time.time()
        in_frame = cv2.resize(next_frame, (w, h))
        in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
        in_frame = in_frame.reshape((n, c, h, w))
        exec_net.start_async(request_id=next_request_id, inputs={input_blob: in_frame})

        if exec_net.requests[cur_request_id].wait(-1) == 0:
            #inf_end = time.time()
            #det_time = inf_end - inf_start

            # Parse detection results of the current request
            res = exec_net.requests[cur_request_id].outputs[out_blob]
            #prob_threshold = 0.80
            #print('shape of res : ' + str(res.shape))
            #print('size res[0]0] : ' + str(len(res[0][0])))
            #print('size res : ' + str(res.size))
            for obj in res[0][0]:
                # Draw only objects when probability more than specified threshold
                if obj[2] > prob_threshold:
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    class_id = int(obj[1])
                    det_label = labels_map[class_id] if labels_map else str(class_id)
                    label = det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %'
                    #print('obj[2] {}'.format(obj[2]))
                    #print('Threshold: {}'.format(obj[2]))
                    #print(' ')
                    #print('class_id : ' + str(class_id))
                    # Draw box and label\class_id
                    #color = (min(class_id * 12.5, 255), min(class_id * 7, 255), min(class_id * 5, 255))
                    #color = (0,0,255)
                    #cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    #cv2.putText(frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)


            # Draw performance stats
            #inf_time_message = "Inference time: N\A for async mode" 
            #render_time_message = "OpenCV rendering time: {:.3f} ms".format(render_time * 1000)
            #async_mode_message = "Async mode is on. Processing request {}".format(cur_request_id)

            #cv2.putText(frame, inf_time_message, (15, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (200, 10, 10), 1)
            #cv2.putText(frame, render_time_message, (15, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (10, 10, 200), 1)
            #cv2.putText(frame, async_mode_message, (10, int(initial_h - 20)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (10, 10, 200), 1)

            #print('label: {}'.format(label))

            box = (xmin, ymin, xmax, ymax, label, class_id, det_label)
            #print('box from plugin: {}'.format(box))


            if det_label is 'pessoa' or \
                        det_label is 'gato' or \
                        det_label is 'carro' or \
                        det_label is 'cachorro':

                boxTracking = (xmin, ymin, xmax, ymax)
                listObjectsTracking.append(boxTracking)
                listRectanglesDetected.append(box)


    listReturn = [frame, next_frame, cur_request_id, next_request_id, listRectanglesDetected, listObjectsTracking]

    return ret, listReturn 
