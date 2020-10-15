echo "copiando arquivos..."

xcopy "campainha.mp3" config.json regions.json -r dlModels ../deploy-win
xcopy -r openvino_deploy_package_win_2020-4 ../deploy-win/openvino

echo "gerando executavel..."

pyinstaller portao_virtual_tracking.py -y --onefile --distpath ..\deploy-win --add-data openvino_deploy_package_win_2020-4\deployment_tools\inference_engine\bin\intel64\Release\plugins.xml;. --noconfirm --hidden-import matplotlib

echo "executavel done"


