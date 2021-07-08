::echo "copiando arquivos..."

:: xcopy "campainha.mp3" config.json regions.json -r dlModels ../deploy-win
:: xcopy -r openvino_deploy_package_win_2020-4 ../deploy-win/openvino

echo "gerando executavel..."

:: --noconsole
:: --onefile
:: --add-data "..\deploy-win\config\openvino\inference_engine\bin\intel64\Release;."
:: -p "..\deploy-win\config\openvino\opencv;."
pyinstaller initFormConfig.py --onefile --add-data "..\deploy-win\config\openvino\deployment_tools\inference_engine\bin\intel64\Release\plugins.xml;." --hidden-import="pkg_resources.py2_warn" --hidden-import="googleapiclient" --hidden-import="apiclient" --onefile -n pv -y --add-data "pv-fb-cert.json;." --add-data "regions.json;." --add-data "campainha.mp3;." --add-data "dlModels;." --distpath ../deploy-win  --add-binary "..\deploy-win\config\openvino\deployment_tools\inference_engine\bin\intel64\Release;."  --add-binary "..\deploy-win\config\openvino\opencv\lib;." --hidden-import opencv --noconfirm --hidden-import matplotlib  
::--noconsole
:: --hidden-import firebase-admin --hidden-import google-api-core --hidden-import google-api-python-client --hidden-import google-auth --hidden-import google-auth-httplib2 --hidden-import google-auth-oauthlib --hidden-import google-cloud-core --hidden-import google-cloud-firestore 

::pyinstaller watchDog-pv.py --onefile -y --distpath ../deploy-win/config --noconfirm --noconsole -n wd
  

echo "executavel done"

