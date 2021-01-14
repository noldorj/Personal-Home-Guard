echo "copiando arquivos..."

:: xcopy "campainha.mp3" config.json regions.json -r dlModels ../deploy-win
:: xcopy -r openvino_deploy_package_win_2020-4 ../deploy-win/openvino

echo "gerando executavel..."

:: --noconsole

pyinstaller initFormConfig.py  --noconsole -n pv --onefile -y --add-data "regions.json;." --add-data "config.json;." --add-data "campainha.mp3;." --add-data "dlModels;." --distpath ../deploy-win  --add-binary "C:\Program Files (x86)\Intel\openvino_2019.1.148\inference_engine\bin\intel64\Release;." --add-data "C:\Program Files (x86)\Intel\openvino_2019.1.148\inference_engine\bin\intel64\Release;." -p "C:\Program Files (x86)\Intel\openvino_2019.1.148\opencv;." --add-binary "C:\Program Files (x86)\Intel\openvino_2019.1.148\opencv\lib;." --hidden-import opencv --noconfirm --hidden-import matplotlib

pyinstaller watchDog-pv.py --onefile -y --distpath ../deploy-win/config --noconfirm --noconsole -n wd
  

echo "executavel done"

