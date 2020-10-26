echo "copiando arquivos..."

#xcopy "campainha.mp3" config.json regions.json -r dlModels ../deploy-win
#xcopy -r openvino_deploy_package_win_2020-4 ../deploy-win/openvino

echo "gerando executavel..."

pyinstaller portao_virtual_tracking.py --onefile -y --add-data "regions.json;." --add-data "config.json;." --add-data "campainha.mp3;." --add-data "dlModels;." --distpath ../deploy-win  --add-binary "C:\Program Files (x86)\Intel\openvino_2019.1.148\inference_engine\bin\intel64\Release;." --add-data "C:\Program Files (x86)\Intel\openvino_2019.1.148\inference_engine\bin\intel64\Release;." -p "C:\Program Files (x86)\Intel\openvino_2019.1.148\opencv;." --add-binary "C:\Program Files (x86)\Intel\openvino_2019.1.148\opencv\lib;." --hidden-import opencv --noconfirm --hidden-import matplotlib -p "C:\Users\pv\AppData\Local\Programs\Python\Python37\Lib\site-packages\matplotlib;."

echo "executavel done"

