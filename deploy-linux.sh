::echo "copiando arquivos..."

:: xcopy "campainha.mp3" config.json regions.json -r dlModels ../deploy-win
:: xcopy -r openvino_deploy_package_win_2020-4 ../deploy-win/openvino_linux

echo "gerando executavel..."

:: --noconsole
:: --onefile
:: --add-data "..\deploy-win/config/openvino_linux/inference_engine/bin/intel64/Release;."
:: -p "..\deploy-win/config/openvino_linux/opencv;."

pyinstaller initFormConfig.py --noconsole --onefile --hidden-import="pkg_resources.py2_warn" --hidden-import="googleapiclient" --hidden-import="apiclient" --onefile -n pv -y --distpath ../deploy-linux --add-binary="../deploy-win/config/openvino_linux/openvino_2021/opencv/lib:lib" --add-binary="../deploy-win/config/openvino_linux/openvino_2021/opencv/bin:lib" --paths "../deploy-win/config/openvino_linux/openvino_2021/python/python3/cv2/python-3" --hidden-import opencv --noconfirm 

::--hidden-import matplotlib
:: --hidden-import firebase-admin --hidden-import google-api-core --hidden-import google-api-python-client --hidden-import google-auth --hidden-import google-auth-httplib2 --hidden-import google-auth-oauthlib --hidden-import google-cloud-core --hidden-import google-cloud-firestore 

::pyinstaller watchDog-pv.py --onefile -y --distpath ../deploy-win/config --noconfirm --noconsole -n wd
  

echo "executavel done"



