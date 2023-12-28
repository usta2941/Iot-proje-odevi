
import requests
import os
import glob
import cv2
import time
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account 

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE ='C:/Users/usta1/Desktop/iot_proje/service_account.json'
PARENT_FOLDER_ID = "1z3P0nqq-0Wj17j2SZFI_A90qrxDiM7qO"

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)
    return creds

def upload_photo(file_path):
    creds = authenticate()
    service = build('drive','v3',credentials=creds)

    file_metadata = {
        'name' : os.path.basename(file_path),
        'parents' : [PARENT_FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype='image/jpeg')

    file = service.files().create(
        body = file_metadata,
        media_body=media,
        fields = "id"
    ).execute()



def find_first_png_in_directory(directory):
    # Belirtilen dizindeki tüm .png dosyalarını bul
    png_files = glob.glob(os.path.join(directory, '*.png'))

    # Eğer .png dosyası varsa, ilkini döndür
    if png_files:
        return png_files[0]
    else:
        return None
    

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"{file_path} deleted successfully.")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

def find_latest_image(directory, file_extensions=["*.jpg", "*.png"]):
    # Belirtilen dizindeki tüm dosyaları bul
    files = []
    for extension in file_extensions:
        files.extend(glob.glob(os.path.join(directory, extension)))

    # Dosyaları son değiştirilme zamanına göre sırala
    files.sort(key=os.path.getmtime, reverse=True)

    # Eğer dosya varsa, en yenisi (listenin başı) döndür
    if files:
        return files[0]
    else:
        return None











def detect_and_save_human(camera_index=0, project_directory="C:/Users/usta1/Desktop/iot_proje", save_prefix="detected_human"):
    bot_token = "6411178732:AAEZ8aezDONs-Qs_-aoteJ-z_zv9BcbjA8o"
    chat_id = "778970874"
    directory_path = "C:/Users/usta1/Desktop/iot_proje"
    # Kamera başlatma
    cap = cv2.VideoCapture(camera_index)

    # Haarcascades sınıflandırıcılarını yükleme
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

    while True:
        # Kameradan bir kare al
        ret, frame = cap.read()

        # Gri tona çevir
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Yüz tespiti
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Yüzü çerçeve içine al
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # İnsan görüntüsünü kaydet
            save_path = os.path.join(project_directory, f"{save_prefix}_{int(time.time())}.jpg")
            cv2.imwrite(save_path, frame)

            print(f"Human detected and saved: {save_path}")

            upload_photo(save_path)
            

            text = "Biri içeri giriş yapti!"
            message = {'text': text}
            requests.post("https://api.telegram.org/bot" + bot_token +"/sendMessage?chat_id=" + chat_id ,data=message)

            image_path = find_latest_image(directory_path, ["*.jpg", "*.png"])
            myimage = open(image_path, "rb")
            image = {"photo": myimage}
            requests.post("https://api.telegram.org/bot" + bot_token +"/sendPhoto?chat_id=" + chat_id ,files=image)

            

        # Görüntüyü ekranda göster
        cv2.imshow('Human Detection', frame)

        # 'q' tuşuna basıldığında döngüyü kır
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kamera ve pencereyi serbest bırak
    cap.release()
    cv2.destroyAllWindows()



# Kullanım
detect_and_save_human(camera_index=1)
