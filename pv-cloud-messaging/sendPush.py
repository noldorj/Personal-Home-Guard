import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import datetime

cred = credentials.Certificate("pvalarmes-3f7ee-firebase-adminsdk-slpxb-4563d30a50.json")
firebase_admin.initialize_app(cred)


# This registration token comes from the client FCM SDKs.
#registration_token = " eyJhbGciOiJSUzI1NiIsImtpZCI6IjJjOGUyYjI5NmM2ZjMyODRlYzMwYjg4NjVkNzI5M2U2MjdmYTJiOGYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcHZhbGFybWVzLTNmN2VlIiwiYXVkIjoicHZhbGFybWVzLTNmN2VlIiwiYXV0aF90aW1lIjoxNjE5Mjg5MDU1LCJ1c2VyX2lkIjoiQUt0Z2ptdTh4a1JqcjlEQXRlS0RjMDloREI1MiIsInN1YiI6IkFLdGdqbXU4eGtSanI5REF0ZUtEYzA5aERCNTIiLCJpYXQiOjE2MTkyODkwNTUsImV4cCI6MTYxOTI5MjY1NSwiZW1haWwiOiJjb250YXRvQHBvcnRhb3ZpcnR1YWwuY29tLmJyIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbImNvbnRhdG9AcG9ydGFvdmlydHVhbC5jb20uYnIiXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.V0a-fmvewQ5qOsYJYhs7hPHUu9d-ABLGoT1e2-1rW94aUHVpMLEvwOW6sJON-c0u5DTYRZYv6ae4_6S6CYtyL-_dhQwPbH0vE68JOzDvdaBUfOAcGkPubl2M816SV72sMBdg5w7tTYTKXY8nina1AT5xeliLyiKz7ZPiw4RW4safQW9qPchw9qjcHSJhvwgfDt819mlNqmPNWGFDiBD5suCVViDE6MzZqiy8dAYTTjXWRxhzuuw1hXFAiuQpm5COih0LOn7YSJj87ym6-cuN8WjCa8iIEuxtljo_3OjOvjR9HXFSKLtRZWATPF3SR-5ztDFExpIk78oE8KtrBpmgxQ"

#registration_token = [" eyJhbGciOiJSUzI1NiIsImtpZCI6IjJjOGUyYjI5NmM2ZjMyODRlYzMwYjg4NjVkNzI5M2U2MjdmYTJiOGYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcHZhbGFybWVzLTNmN2VlIiwiYXVkIjoicHZhbGFybWVzLTNmN2VlIiwiYXV0aF90aW1lIjoxNjE5Mjg5MDU1LCJ1c2VyX2lkIjoiQUt0Z2ptdTh4a1JqcjlEQXRlS0RjMDloREI1MiIsInN1YiI6IkFLdGdqbXU4eGtSanI5REF0ZUtEYzA5aERCNTIiLCJpYXQiOjE2MTkyODkwNTUsImV4cCI6MTYxOTI5MjY1NSwiZW1haWwiOiJjb250YXRvQHBvcnRhb3ZpcnR1YWwuY29tLmJyIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbImNvbnRhdG9AcG9ydGFvdmlydHVhbC5jb20uYnIiXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.V0a-fmvewQ5qOsYJYhs7hPHUu9d-ABLGoT1e2-1rW94aUHVpMLEvwOW6sJON-c0u5DTYRZYv6ae4_6S6CYtyL-_dhQwPbH0vE68JOzDvdaBUfOAcGkPubl2M816SV72sMBdg5w7tTYTKXY8nina1AT5xeliLyiKz7ZPiw4RW4safQW9qPchw9qjcHSJhvwgfDt819mlNqmPNWGFDiBD5suCVViDE6MzZqiy8dAYTTjXWRxhzuuw1hXFAiuQpm5COih0LOn7YSJj87ym6-cuN8WjCa8iIEuxtljo_3OjOvjR9HXFSKLtRZWATPF3SR-5ztDFExpIk78oE8KtrBpmgxQ"]

topic = "contato.portaovirtual.com.br"

message = messaging.Message (    
    
    android = messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=messaging.AndroidNotification(
                icon='stock_ticker_update',
                color='#f45342',
                title='PV - Alarme',     
                body= ' Pessoa na rua -  Detectado em 17:23:52 - 24/Abr/2021',          
                
            ),
            
    ),
    
    notification = messaging.Notification(
        title= 'PV - Alarme', 
        body= ' Carro na rua -  Detectado em 17:23:52 - 22/Maio/2021',
        image= 'https://firebasestorage.googleapis.com/v0/b/pvalarmes-3f7ee.appspot.com/o/foto_alerta.jpg?alt=media&token=755e0108-33f2-4cf2-8646-26c4498a37dc',
        
    ), 
    data = {
        'cameraName': 'Cam_Garagem', 
        'regionName': 'garagem', 
        'urlImageFirebase': 'https://firebasestorage.googleapis.com/v0/b/pvalarmes-3f7ee.appspot.com/o/foto_alerta.jpg?alt=media&token=755e0108-33f2-4cf2-8646-26c4498a37dc',
        'urlImageDownload': 'https://storage.googleapis.com/pvalarmes-3f7ee.appspot.com/foto_alerta.jpg',
         'id': '24-05-2021-14-20-01', 
         'date': '24/05/2021', 
         'hour': '09:06:01', 
         'click_action': 'FLUTTER_NOTIFICATION_CLICK', 
         'objectDetected': 'Carro',
         },
    topic=topic,
    
        
)


# Send a message to the device corresponding to the provided

# registration token.
try:
    response = messaging.send(message)
except error as e:
    print('Error: {}'.format(e))
else:
    print('Successfully sent message:', response)

