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

def getListBoxDetected(ipCam, device='CPU'):

    log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
    #model_xml = args.model

    cpu_extension = '/home/igor/intel/computer_vision_sdk/deployment_tools/inference_engine/lib/ubuntu_16.04/intel64/libcpu_extension_avx2.so'

    plugin_dir = '/home/igor/intel/computer_vision_sdk/deployment_tools/inference_engine/lib/ubuntu_16.04/intel64/'


    if device == 'MYRIAD': 
        log.info('loading MYRIAD plugins...')
        #model_xml = os.getcwd() + '/dlModels/openvino/pedestrian-and-vehicle-detector-adas-0001/FP16/pedestrian-and-vehicle-detector-adas-0001.xml'
        #model_bin = os.getcwd() + '/dlModels/openvino/pedestrian-and-vehicle-detector-adas-0001/FP16/pedestrian-and-vehicle-detector-adas-0001.bin'

        model_xml = '/home/igor/intel/computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP16/pedestrian-detection-adas-0002.xml'

        model_bin = '/home/igor/intel/computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP16/pedestrian-detection-adas-0002.bin'

    else:
        log.info('loading CPU plugins...')
        #model_xml = '/home/igor/intel/computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP32/pedestrian-detection-adas-0002.xml'

        #model_bin = '/home/igor/intel/computer_vision_sdk/deployment_tools/intel_models/pedestrian-detection-adas-0002/FP32/pedestrian-detection-adas-0002.bin'

        model_bin = '/home/igor/intel/computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.bin'

        model_xml = '/home/igor/intel/computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.xml'


    #model_bin = os.path.splitext(model_xml)[0] + ".bin"

    #labels = 'voc_labels.txt' #TODO parametro para labels
    labels_map = ["background", "pessoa", "carro", "bicileta"]
    

    # Plugin initialization for specified device and load extensions library if specified
    log.info("Initializing plugin for {} device...".format(device))

    plugin = IEPlugin(device=device, plugin_dirs=plugin_dir)

    if cpu_extension and 'CPU' in device:
        plugin.add_cpu_extension(cpu_extension)

    # Read IR
    log.info("Reading IR...")
    net = IENetwork.from_ir(model=model_xml, weights=model_bin)

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

 # Read and pre-process input image
    n, c, h, w = net.inputs[input_blob].shape
    del net
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

    cap = ipCam
    #cap = cv2.VideoCapture(input_stream)

    cur_request_id = 0
    next_request_id = 1

    log.info("Starting inference in async mode...")
    log.info("To switch between sync and async modes press Tab button")
    log.info("To stop the demo execution press Esc button")
    is_async_mode = True
    render_time = 0
    ret, frame = cap.read()
    while cap.isOpened():

        if is_async_mode:
            ret, next_frame = cap.read()
        else:
            ret, frame = cap.read()
        if not ret:
            break
        initial_w = cap.get(3)
        initial_h = cap.get(4)
        # Main sync point:
        # in the truly Async mode we start the NEXT infer request, while waiting for the CURRENT to complete
        # in the regular mode we start the CURRENT request and immediately wait for it's completion
        inf_start = time.time()
        if is_async_mode:
            in_frame = cv2.resize(next_frame, (w, h))
            in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
            in_frame = in_frame.reshape((n, c, h, w))
            exec_net.start_async(request_id=next_request_id, inputs={input_blob: in_frame})
        else:
            in_frame = cv2.resize(frame, (w, h))
            in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
            in_frame = in_frame.reshape((n, c, h, w))
            exec_net.start_async(request_id=cur_request_id, inputs={input_blob: in_frame})

        if exec_net.requests[cur_request_id].wait(-1) == 0:
            inf_end = time.time()
            det_time = inf_end - inf_start

            # Parse detection results of the current request
            res = exec_net.requests[cur_request_id].outputs[out_blob]
            prob_threshold = 0.35
            #print('shape of res : ' + str(res.shape))
            #print('size res[0]0] : ' + str(len(res[0][0])))
            #print('size res : ' + str(res.size))
            for obj in res[0][0]:
                #log.info('Threshold: {}'.format(obj[2]))
                # Draw only objects when probability more than specified threshold
                if obj[2] > prob_threshold:
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    class_id = int(obj[1])
                    #print(' ')
                    #print('class_id : ' + str(class_id))
                    # Draw box and label\class_id
                    #color = (min(class_id * 12.5, 255), min(class_id * 7, 255), min(class_id * 5, 255))
                    color = (0,0,255)
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    det_label = labels_map[class_id] if labels_map else str(class_id)
                    cv2.putText(frame, det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)

            # Draw performance stats
            inf_time_message = "Inference time: N\A for async mode" if is_async_mode else \
                "Inference time: {:.3f} ms".format(det_time * 1000)
            render_time_message = "OpenCV rendering time: {:.3f} ms".format(render_time * 1000)
            async_mode_message = "Async mode is on. Processing request {}".format(cur_request_id) if is_async_mode else \
                "Async mode is off. Processing request {}".format(cur_request_id)

            cv2.putText(frame, inf_time_message, (15, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (200, 10, 10), 1)
            cv2.putText(frame, render_time_message, (15, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (10, 10, 200), 1)
            cv2.putText(frame, async_mode_message, (10, int(initial_h - 20)), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (10, 10, 200), 1)

        #
        render_start = time.time()
        cv2.imshow("Detection Results", frame)
        render_end = time.time()
        render_time = render_end - render_start

        if is_async_mode:
            cur_request_id, next_request_id = next_request_id, cur_request_id
            frame = next_frame

        key = cv2.waitKey(1)
        if key == 27:
            break
        if (9 == key):
            is_async_mode = not is_async_mode
            log.info("Switched to {} mode".format("async" if is_async_mode else "sync"))

    cv2.destroyAllWindows()
    del exec_net
    del plugin


#if __name__ == '__main__':
#    sys.exit(main() or 0)
