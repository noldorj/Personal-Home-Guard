#!/bin/bash

echo "copiando arquivos..."
cp portao_virtual_tracking.py pluginOpenVino.py mainForm.py utilsCore.py Utils_tracking.py -r objectTracking ../deploy/
cp campainha.mp3 config.json regions.json -r dlModels ../deploy
cp -r openvino ../deploy

echo "gerando executavel..."

pyinstaller portao_virtual_tracking.py -F -y -p openvino:. --hidden-import numpy --hidden-import scipy --hidden-import scipy._lib.messagestream --add-data openvino:. --add-data openvino/deployment_tools/inference_engine/lib/intel64:. --add-data /home/igor/Dropbox/deploy/regions.json:. --add-data /home/igor/Dropbox/deploy/config.json:. --add-data /home/igor/Dropbox/deploy/campainha.mp3:. --add-data /home/igor/Dropbox/deploy/dlModels:. --add-binary openvino/opencv/lib:. --add-binary openvino/deployment_tools/inference_engine/lib/intel64:. --hidden-import opencv -p openvino/opencv:. --distpath ../deploy/

echo "executavel done"

echo "apagando arquivos"
rm *.py
rm -rf objectTracking
