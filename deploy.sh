#!/bin/bash

echo "copiando arquivos..."
cp portao_virtual_tracking.py pluginOpenVino.py mainForm.py utilsCore.py Utils_tracking.py -r objectTracking ../deploy2/
cp campainha.mp3 config.json regions.json -r dlModels ../deploy2
cp -r checkLicence ../deploy2
cp -r openvino ../deploy2

echo "gerando executavel..."

#pyinstaller portao_virtual_tracking.py --onefile -F -y -p openvino:. --hidden-import opencv --hidden-import matplotlib --hidden-import numpy --hidden-import scipy --hidden-import scipy._lib.messagestream --hidden-import pygame --add-data /home/igor/.local/lib/python3.6/site-packages/pygame:. --add-data openvino/deployment_tools/inference_engine/lib/intel64:. --add-data regions.json:. --add-data config.json:. --add-data campainha.mp3:. --add-data dlModels:. --add-binary /home/igor/.local/lib/python3.6/site-packages/pygame:. --add-binary openvino/opencv/lib:. --add-binary openvino/deployment_tools/inference_engine/lib/intel64:. -p openvino/opencv:. --distpath ../deploy2

pyinstaller portao_virtual_tracking.py --onefile -y -p /home/igor/.local/lib/python3.6/site-packages/matplotlib:. -p openvino:. --add-data regions.json:. --add-data config.json:. --add-data campainha.mp3:. --add-data dlModels:. --distpath ../deploy2 --add-binary /home/igor/portao-virtual/openvino/deployment_tools/inference_engine/lib/intel64:. --add-data /home/igor/portao-virtual/openvino/deployment_tools/inference_engine/lib/intel64:. -p /home/igor/portao-virtual/openvino/opencv:. --add-binary /home/igor/portao-virtual/openvino/opencv/lib:. --hidden-import opencv --add-binary /home/igor/deploy2/openvino/python/python3.6/openvino/inference_engine:. -p /home/igor/deploy2/openvino/python/python3.6/openvino/inference_engine:. -p /home/igor/intel/openvino_2020.4.287/deployment_tools/inference_engine/include:. --add-binary /home/igor/intel/openvino_2020.4.287/python/python3.7/openvino/inference_engine:. --add-data /home/igor/intel/openvino_2020.4.287/python:. --add-binary /home/igor/intel/openvino_2020.4.287/python/python3.5/openvino/inference_engine:. --hidden-import IECore --hidden-import IENetwork 


#pyinstaller portao_virtual_tracking.py --onefile -F -y -p openvino:. -p /home/igor/anaconda3/ -p checkLicence:. --add-data checkLicence:. --hidden-import matplotlib --hidden-import python-socketio --hidden-import engineio.async_aiohttp --hidden-import engineio.async_drivers.aiohttp --hidden-import socketio --hidden-import engineio.async_eventlet --hidden-import engineio.async_drivers.threading --hidden-import gevent --hidden-import geventwebsocket --hidden-import opencv --hidden-import numpy --hidden-import scipy --hidden-import scipy._lib.messagestream --hidden-import pygame --add-data /home/igor/anaconda3/envs/pv/lib/python3.6/site-packages/socketio:. --add-data /usr/local/lib/python3.6/dist-packages/pygame:. --add-data /home/igor/anaconda3/envs/pv/lib/python3.6/site-packages/engineio:. --add-data openvino/deployment_tools/inference_engine/lib/intel64:. --add-data regions.json:. --add-data config.json:. --add-data campainha.mp3:. --add-data dlModels:. -p /home/igor/anaconda3/envs/pv/lib/python3.6/site-packages/socketio:. --add-binary /home/igor/anaconda3/envs/pv/lib/python3.6/site-packages/socketio:. --add-binary /usr/local/lib/python3.6/dist-packages/pygame:. --add-binary openvino/opencv/lib:. --add-binary openvino/deployment_tools/inference_engine/lib/intel64:. -p openvino/opencv:. --distpath ../deploy2


pyinstaller portao_virtual_tracking.py --onefile -y -p /home/igor/.local/lib/python3.6/site-packages/matplotlib:. -p openvino:. --add-data regions.json:. --add-data config.json:. --add-data campainha.mp3:. --add-data dlModels:. --distpath ../deploy2 --add-binary /home/igor/portao-virtual/openvino/deployment_tools/inference_engine/lib/intel64:. --add-data /home/igor/portao-virtual/openvino/deployment_tools/inference_engine/lib/intel64:. -p /home/igor/portao-virtual/openvino/opencv:. --add-binary /home/igor/portao-virtual/openvino/opencv/lib:. --hidden-import opencv --add-binary /home/igor/deploy2/openvino/python/python3.6/openvino/inference_engine:. -p /home/igor/deploy2/openvino/python/python3.6/openvino/inference_engine:. -p /home/igor/intel/openvino_2020.4.287/deployment_tools/inference_engine/include:. --add-binary /home/igor/intel/openvino_2020.4.287/python/python3.7/openvino/inference_engine:. --add-data /home/igor/intel/openvino_2020.4.287/python:. --add-binary /home/igor/intel/openvino_2020.4.287/python/python3.5/openvino/inference_engine:. --hidden-import IECore --hidden-import IENetwork 





echo "executavel done"

#echo "apagando arquivos"
rm ../deploy2/*.py
rm -rf ../deploy2/objectTracking
rm -rf ../deploy2/checkLicence
