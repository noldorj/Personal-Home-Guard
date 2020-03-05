import requests

URL = "http://127.0.0.1:5000/login"

PARAMS = {'userName':'igor14', 'userPassword':'senha','userToken':'aaa'} 

r = requests.get(url = URL, params = PARAMS) 
r





