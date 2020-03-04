#!/bin/bash

pyinstaller portao_virtual_tracking.py -F -y -p /home/igor/openvino:. --hidden-import numpy --hidden-import scipy --hidden-import scipy._lib.messagestream --add-data /home/igor/openvino:. --add-data /home/igor/openvino/deployment_tools/inference_engine/lib/intel64:. --add-binary /opt/intel/openvino/opencv/lib:. --add-binary /home/igor/openvino/deployment_tools/inference_engine/lib/intel64:. --hidden-import opencv -p /opt/intel/openvino/opencv/:.

cp campainha.mp3 regions.json regions.json -r dlModels ../deploy
