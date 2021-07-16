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
#from  openvino.inference_engine import IENetwork, IEPlugin
import openvino.inference_engine.constants
from  openvino.inference_engine import IENetwork, IECore

from common import models
from common import monitors
from common.pipelines import get_user_config, AsyncPipeline
from common.images_capture import open_images_capture
from common.performance_metrics import PerformanceMetrics
from common.helpers import resolution

from argparse import ArgumentParser, SUPPRESS

from pathlib import Path
from time import perf_counter



#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)
#def main():
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log')

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.DEBUG, stream=sys.stdout)


#labels_map = ["background", "car", "person", "bike"]
labels_map = ["person", "bike", "car"] #yolo
#labels_map = ["background", "person", "car", "bike"]

#lista de boxes detectados
listRectanglesDetected = []
listObjectsTracking = []
devIces_disponiveis = []


def initOpenVino(device, model_xml, source):

    log.info(' ')
    log.info('initOpenVino::')
    # Plugin initialization for specified device and load extensions library if specified
    
    log.info(' ')
    log.info("initOpenVino:: Device   : {} ".format(device))
    log.info('initOpenVino:: Model XML: {}'.format(model_xml))
    
    log.info(' ')
    
    args = None
    detector_pipeline = None
    
    try:
        args = build_argparser().parse_args('')
    except Exception as err:
        log.error('initOpenVino:: Erro ao carregar Args: {}'.format(err))
    else:
        log.info('initOpenVino:: Args carregado')
    #args = build_argparser()

    log.info('initOpenVino:: Initializing Inference Engine...')
    try:
        ie = IECore()
    except Exception as err:
        log.error('initOpenVino:: Erro ao carregar IECore: {}'.format(err))
    else:
        log.info('initOpenVino:: IE Core carregado')

    
    try:
        args.device = device        
        args.model = model_xml
        args.architecture_type = 'yolo'
        args.input = source
        args.num_infer_requests = 2
        args.loop = True
        
        log.info('args.device               : {}'.format(args.device))
        log.info('args.model                : {}'.format(args.model))
        log.info('args.architecture_type    : {}'.format(args.architecture_type))
        log.info('args.input                : {}'.format(args.input))
        log.info('args.num_infer_requests   : {}'.format(args.num_infer_requests))
        log.info('args.loop                 : {}'.format(args.loop))
        
    except Exception as err:
        log.error('initOpenVino:: Erro setando valores no args: {}'.format(err))
    else:
        log.info('initOpenVino:: Valores inseridos no Args ok')
    
    try:
        plugin_config = get_user_config(args.device, args.num_streams, args.num_threads)
    except Exception as err:
        log.error('initOpenVino:: Error get_user_config: {}'.format(err))
    else:
        log.info('initOpenVino:: get_user_config ok')
    

    log.info('Loading network...')

    try:
    
        model = get_model(ie, args)
        
    except Exception as err:
        log.error('initOpenVino:: Erro get_model: {}'.format(err))
    else:
        log.info('initOpenVino:: get_model ok')

    try:
        detector_pipeline = AsyncPipeline(ie, model, plugin_config,
                                      device=args.device, max_num_requests=args.num_infer_requests)
    except Exception as err:    
        log.error('initOpenVino Erro detector_pipeline: {}'.format(err))
    else:
        log.info('initOpenVino:: detector_pipeline ok')
        
                                      
    log.info(' ')
    log.info("initOpenVino:: Init Openvino done")
    log.info(' ')    
    print('initOpenVino:: detector_pipeline ID: {}'.format(detector_pipeline.id_AsyncPipeline))

    return detector_pipeline, args, model


def draw_detections(frame, detections, palette, labels, threshold, output_transform):
    size = frame.shape[:2]
    frame = output_transform.resize(frame)
    for detection in detections:
        if detection.score > threshold:
            class_id = int(detection.id)
            color = palette[class_id]
            det_label = labels[class_id] if labels and len(labels) >= class_id else '#{}'.format(class_id)
            xmin = max(int(detection.xmin), 0)
            ymin = max(int(detection.ymin), 0)
            xmax = min(int(detection.xmax), size[1])
            ymax = min(int(detection.ymax), size[0])
            xmin, ymin, xmax, ymax = output_transform.scale([xmin, ymin, xmax, ymax])
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(frame, '{} {:.1%}'.format(det_label, detection.score),
                        (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
            if isinstance(detection, models.DetectionWithLandmarks):
                for landmark in detection.landmarks:
                    landmark = output_transform.scale(landmark)
                    cv2.circle(frame, (int(landmark[0]), int(landmark[1])), 2, (0, 255, 255), 2)
    return frame


def print_raw_results(size, detections, labels, threshold):
    log.info(' Class ID | Confidence | XMIN | YMIN | XMAX | YMAX ')
    for detection in detections:
        if detection.score > threshold:
            xmin = max(int(detection.xmin), 0)
            ymin = max(int(detection.ymin), 0)
            xmax = min(int(detection.xmax), size[1])
            ymax = min(int(detection.ymax), size[0])
            class_id = int(detection.id)
            det_label = labels[class_id] if labels and len(labels) >= class_id else '#{}'.format(class_id)
            log.info('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                     .format(det_label, detection.score, xmin, ymin, xmax, ymax))


# next_frame_id_to_show = next_request_id
# next_frame_id = cur_request_id
def getListBoxDetected(detector_pipeline, next_frame_id_to_show, next_frame_id, prob_threshold, cap, source, args, model):
    
    print('getListBoxDetected')
    # print('next_frame_id:           {}'.format(next_frame_id))
    # print('next_frame_id_to_show:   {}'.format(next_frame_id_to_show))
    # print('prob_threshold:          {}'.format(prob_threshold))
    
    prob_threshold_returned, xmin, xmax, ymin, ymax, det_label, class_id, label  = 0,0, 0, 0, 0, ' ', 0, ' '

    metrics = PerformanceMetrics()
    presenter = None
    output_transform = None

    listObjectsTracking.clear()
    listRectanglesDetected.clear()
    
    cap = open_images_capture(source, True)
    
    #print('getListBoxDetected:: detector_pipeline ID: {}'.format(detector_pipeline.id_AsyncPipeline))
    
    #while True:
    if detector_pipeline.callback_exceptions:
        print('detector_pipeline rase exceptions')
        raise detector_pipeline.callback_exceptions[0]
    
    results = detector_pipeline.get_result(next_frame_id_to_show)
    
    #print('results: {}'.format(results))
    
    if results:
        #print('results')
    
        objects, frame_meta = results
        frame = frame_meta['frame']
        start_time = frame_meta['start_time']

        #objects = detections
        #print('(len(objects): {}'.format(len(objects)))
        
        if len(objects):
            #print('results:: print_raw_results')
            
            size = frame.shape[:2]
            #print_raw_results(frame.shape[:2], objects, model.labels, args.prob_threshold)
            
            for detection in objects:
                if detection.score > 0.30:
                #if detection.score > prob_threshold:
                    xmin = max(int(detection.xmin), 0)
                    ymin = max(int(detection.ymin), 0)
                    xmax = min(int(detection.xmax), size[1])
                    ymax = min(int(detection.ymax), size[0])
                    class_id = int(detection.id)
                    det_label = model.labels[class_id] if model.labels and len(model.labels) >= class_id else '#{}'.format(class_id)
                    
                    #teste para mais de um ID
                    box = (xmin, ymin, xmax, ymax, label, class_id, det_label)
                    print('det_label: {}'.format(det_label))
                    prob_threshold_returned = detection.score
                    label = det_label + ' ' + str(prob_threshold_returned) + ' %'
                    
                    if det_label is 'person' or \
                                det_label is 'cat' or \
                                det_label is 'bike' or \
                                det_label is 'car' or \
                                det_label is 'dog':
                        boxTracking = (xmin, ymin, xmax, ymax)
                        listObjectsTracking.append(boxTracking)
                        listRectanglesDetected.append(box)
        
        next_frame_id_to_show += 1                
       

    if detector_pipeline.is_ready():
        print('detector_pipeline.is_ready()')
        # Get new image/frame
        start_time = perf_counter()
        frame = cap.read()
        if frame is None:
            print('frame is None')
            if next_frame_id == 0:
                raise ValueError("Can't read an image from the input")
            #break
        if next_frame_id == 0:
            output_transform = models.OutputTransform(frame.shape[:2], args.output_resolution)
            if args.output_resolution:
                output_resolution = output_transform.new_resolution
            else:
                output_resolution = (frame.shape[1], frame.shape[0])
            
            presenter = monitors.Presenter(args.utilization_monitors, 55,
                                           (round(output_resolution[0] / 4), round(output_resolution[1] / 8)))
            #if args.output and not video_writer.open(args.output, cv2.VideoWriter_fourcc(*'MJPG'),cap.fps(), output_resolution):
                #raise RuntimeError("Can't open video writer")
        # Submit for inference
        detector_pipeline.submit_data(frame, next_frame_id, {'frame': frame, 'start_time': start_time})
        next_frame_id += 1

    else:
        # Wait for empty request
        print('Wait for empty request')
        detector_pipeline.await_any()
    
    # detector_pipeline.await_all()
    # # Process completed requests
    # for next_frame_id_to_show in range(next_frame_id_to_show, next_frame_id):
        # results = detector_pipeline.get_result(next_frame_id_to_show)
        # while results is None:
            # results = detector_pipeline.get_result(next_frame_id_to_show)
        # objects, frame_meta = results
        # frame = frame_meta['frame']
        # start_time = frame_meta['start_time']

        
        #presenter.drawGraphs(frame)
        #frame = draw_detections(frame, objects, palette, model.labels, args.prob_threshold, output_transform)
        #etrics.update(start_time, frame)

        # if video_writer.isOpened() and (args.output_limit <= 0 or next_frame_id_to_show <= args.output_limit-1):
            # video_writer.write(frame)

        # if not args.no_show:
            # cv2.imshow('Detection Results', frame)
            # key = cv2.waitKey(1)

            # ESC_KEY = 27
            # # Quit.
            # if key in {ord('q'), ord('Q'), ESC_KEY}:
                # break
            # presenter.handleKey(key)
    
    
    listReturn = [listRectanglesDetected, listObjectsTracking, prob_threshold_returned]

    return listReturn 

def get_model(ie, args):
    input_transform = models.InputTransform(args.reverse_input_channels, args.mean_values, args.scale_values)
    common_args = (ie, args.model, input_transform)
    if args.architecture_type in ('ctpn', 'yolo', 'yolov4', 'retinaface',
                                  'retinaface-pytorch') and not input_transform.is_trivial:
        raise ValueError("{} model doesn't support input transforms.".format(args.architecture_type))

    if args.architecture_type == 'ssd':
        return models.SSD(*common_args, labels=args.labels, keep_aspect_ratio_resize=args.keep_aspect_ratio)
    elif args.architecture_type == 'ctpn':
        return models.CTPN(ie, args.model, input_size=args.input_size, threshold=args.prob_threshold)
    elif args.architecture_type == 'yolo':
        return models.YOLO(ie, args.model, labels=args.labels,
                           threshold=args.prob_threshold, keep_aspect_ratio=args.keep_aspect_ratio)
    elif args.architecture_type == 'yolov4':
        return models.YoloV4(ie, args.model, labels=args.labels,
                             threshold=args.prob_threshold, keep_aspect_ratio=args.keep_aspect_ratio)
    elif args.architecture_type == 'faceboxes':
        return models.FaceBoxes(*common_args, threshold=args.prob_threshold)
    elif args.architecture_type == 'centernet':
        return models.CenterNet(*common_args, labels=args.labels, threshold=args.prob_threshold)
    elif args.architecture_type == 'retinaface':
        return models.RetinaFace(ie, args.model, threshold=args.prob_threshold)
    elif args.architecture_type == 'ultra_lightweight_face_detection':
        return models.UltraLightweightFaceDetection(*common_args, threshold=args.prob_threshold)
    elif args.architecture_type == 'retinaface-pytorch':
        return models.RetinaFacePyTorch(ie, args.model, threshold=args.prob_threshold)
    else:
        raise RuntimeError('No model type or invalid model type (-at) provided: {}'.format(args.architecture_type))


def build_argparser():
    parser = ArgumentParser(add_help=False, argument_default=SUPPRESS)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument('-m', '--model', help='Required. Path to an .xml file with a trained model.',
                      required=False, type=Path)
    args.add_argument('-at', '--architecture_type', help='Required. Specify model\' architecture type.',
                      type=str, required=False, choices=('ssd', 'yolo', 'yolov4', 'faceboxes', 'centernet', 'ctpn',
                                                        'retinaface', 'ultra_lightweight_face_detection',
                                                        'retinaface-pytorch'))
    args.add_argument('-i', '--input', required=False,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    args.add_argument('-d', '--device', default='CPU', type=str,
                      help='Optional. Specify the target device to infer on; CPU, GPU, HDDL or MYRIAD is '
                           'acceptable. The demo will look for a suitable plugin for device specified. '
                           'Default value is CPU.')

    common_model_args = parser.add_argument_group('Common model options')
    common_model_args.add_argument('--labels', help='Optional. Labels mapping file.', default=None, type=str)
    common_model_args.add_argument('-t', '--prob_threshold', default=0.5, type=float,
                                   help='Optional. Probability threshold for detections filtering.')
    common_model_args.add_argument('--keep_aspect_ratio', action='store_true', default=False,
                                   help='Optional. Keeps aspect ratio on resize.')
    common_model_args.add_argument('--input_size', default=(600, 600), type=int, nargs=2,
                                   help='Optional. The first image size used for CTPN model reshaping. '
                                        'Default: 600 600. Note that submitted images should have the same resolution, '
                                        'otherwise predictions might be incorrect.')

    infer_args = parser.add_argument_group('Inference options')
    infer_args.add_argument('-nireq', '--num_infer_requests', help='Optional. Number of infer requests',
                            default=0, type=int)
    infer_args.add_argument('-nstreams', '--num_streams',
                            help='Optional. Number of streams to use for inference on the CPU or/and GPU in throughput '
                                 'mode (for HETERO and MULTI device cases use format '
                                 '<device1>:<nstreams1>,<device2>:<nstreams2> or just <nstreams>).',
                            default='', type=str)
    infer_args.add_argument('-nthreads', '--num_threads', default=None, type=int,
                            help='Optional. Number of threads to use for inference on CPU (including HETERO cases).')

    io_args = parser.add_argument_group('Input/output options')
    io_args.add_argument('--loop', default=False, action='store_true',
                         help='Optional. Enable reading the input in a loop.')
    io_args.add_argument('-o', '--output', required=False,
                         help='Optional. Name of the output file(s) to save.')
    io_args.add_argument('-limit', '--output_limit', required=False, default=1000, type=int,
                         help='Optional. Number of frames to store in output. '
                              'If 0 is set, all frames are stored.')
    io_args.add_argument('--no_show', help="Optional. Don't show output.", action='store_true')
    io_args.add_argument('--output_resolution', default=None, type=resolution,
                          help='Optional. Specify the maximum output window resolution '
                               'in (width x height) format. Example: 1280x720. '
                               'Input frame size used by default.')
    io_args.add_argument('-u', '--utilization_monitors', default='', type=str,
                         help='Optional. List of monitors to show initially.')

    input_transform_args = parser.add_argument_group('Input transform options')
    input_transform_args.add_argument('--reverse_input_channels', default=False, action='store_true',
                                      help='Optional. Switch the input channels order from '
                                           'BGR to RGB.')
    input_transform_args.add_argument('--mean_values', default=None, type=float, nargs=3,
                                      help='Optional. Normalize input by subtracting the mean '
                                           'values per channel. Example: 255 255 255')
    input_transform_args.add_argument('--scale_values', default=None, type=float, nargs=3,
                                      help='Optional. Divide input by scale values per channel. '
                                           'Division is applied after mean values subtraction. '
                                           'Example: 255 255 255')

    debug_args = parser.add_argument_group('Debug options')
    debug_args.add_argument('-r', '--raw_output_message', help='Optional. Output inference results raw values showing.',
                            default=False, action='store_true')
    log.info('return parser ')
    log.info(' ')
    return parser
    