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
labels_map = ["background", "car", "person", "bike"]
#labels_map = ["background", "person", "car", "bike"]

#lista de boxes detectados
listRectanglesDetected = []
listObjectsTracking = []


def initOpenVino(device, model_xml, model_bin, cpu_extension, plugin_dir):

    #cpu_extension = '/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_avx2.so'

    #plugin_dir = '/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64'
    log.info('CPU Extension    : {}'.format(cpu_extension))
    log.info('Plugin Diretorio : {}'.format(plugin_dir))
    log.info(' ')

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

    try: 
        plugin = IEPlugin(device=device, plugin_dirs=plugin_dir)
    except e:
        log.critical('IEPlugin error: {}'.format(e))
    else:
        log.info('Plugin {} carregado'.format(device))

    if cpu_extension and 'CPU' in device:

        plugin.add_cpu_extension(cpu_extension)
        log.info('CPU Estension carregado')
    else:
        log.critical('Erro adicionando CPU_Extension')

    # Read IR
    log.info("Reading IR...")
    try:
        log.info('Carregando IENetwork') 
        net = IENetwork(model=model_xml, weights=model_bin)

    except Exception as e:

        log.critical('IENetwork error: {}'.format(e))

    else:
        log.info('IENetwork carregada')

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
    del net

    is_async_mode = True
    log.info("Init Openvino done")

    return nchw, exec_net, input_blob, out_blob


def getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold):


    prob_threshold_returned, xmin, xmax, ymin, ymax, det_label, class_id, label  = 0,0, 0, 0, 0, ' ', 0, ' '

    listObjectsTracking.clear()
    listRectanglesDetected.clear()

    n, c, h, w = nchw[0], nchw[1], nchw[2], nchw[3]

    cap = ipCam

    ret, next_frame = cap.read()
    if next_frame is None or ret is False:
        log.error("Error capturing next_frame")

    else:

        initial_w = cap.get(3)
        initial_h = cap.get(4)
        in_frame = cv2.resize(next_frame, (w, h))
        in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
        in_frame = in_frame.reshape((n, c, h, w))
        exec_net.start_async(request_id=next_request_id, inputs={input_blob: in_frame})

        if exec_net.requests[cur_request_id].wait(-1) == 0:

            # Parse detection results of the current request
            res = exec_net.requests[cur_request_id].outputs[out_blob]

            for obj in res[0][0]:
                # Draw only objects when probability more than specified threshold
                if obj[2] > prob_threshold:
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    class_id = int(obj[1])
                    det_label = labels_map[class_id] if labels_map else str(class_id)
                    prob_threshold_returned = round(obj[2] * 100, 1)
                    label = det_label + ' ' + str(prob_threshold_returned) + ' %'

                    #teste para mais de um ID
                    box = (xmin, ymin, xmax, ymax, label, class_id, det_label)
                    if det_label is 'person' or \
                                det_label is 'cat' or \
                                det_label is 'car' or \
                                det_label is 'dog':
                        boxTracking = (xmin, ymin, xmax, ymax)
                        listObjectsTracking.append(boxTracking)
                        listRectanglesDetected.append(box)



            #if det_label is 'person' or \
            #            det_label is 'cat' or \
            #            det_label is 'car' or \
            #            det_label is 'dog':

                #boxTracking = (xmin, ymin, xmax, ymax)
                #listObjectsTracking.append(boxTracking)
                #listRectanglesDetected.append(box)

    listReturn = [frame, next_frame, cur_request_id, next_request_id, listRectanglesDetected, listObjectsTracking, prob_threshold_returned]

    return ret, listReturn 
