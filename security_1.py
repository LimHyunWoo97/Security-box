import picamera
import RPi.GPIO as GPIO
import smtplib
import threading
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

source_mail = 'imhw1997@gmail.com'

#for camera
camera = picamera.PiCamera()
file_path = '/home/hyunwoo/Downloads/'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#for LED, BUZZER, HC-SR04
BUZZER = 12
LED = 4
TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

##for mail
#client = Client(account_sid,auth_token)

##semaphore 객체 생성
#sem = threading.Semaphore()

def save_moive():
    cur_time = time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))
    file_name=cur_time+'.h264'
    camera.start_recording(file_name)
    camera.wait_recording(5)
    camera.stop_recording()
    return file_name
    
def send_mail(title,message,dest,send_file):
    smtp = smtplib.SMTP('smtp.gmail.com' ,587)
    smtp.starttls()
    smtp.login('imhw1997@gmail.com','mthpbozodrtddsbj') #수신용 메일과 앱 비밀번호 로그인
    msg = MIMEMultipart()
    msg['Subject'] = title
    msg['To'] = dest
    text = MIMEText(message)
    msg.attach(text)    
    with open(send_file, 'rb')as file_FD:
        etcPart = MIMEApplication(file_FD.read())
        etcPart.add_header('Content-Disposition','attachment',filename = send_file)
        msg.attach(etcPart)
    smtp.sendmail('imhw1997@gmail.com','imhw1997@naver.com',msg.as_string())
    smtp.quit()

#초음파센서 감지 함수

GPIO.output(TRIG, False)
print("초음파 출력 초기화")
time.sleep(2)

try:
   while True:
            GPIO.output(TRIG, True)
            time.sleep(0.00001) #10us Pulse delay
            GPIO.output(TRIG, False)
            
            while GPIO.input(ECHO)==0:
                start = time.time() #Echo pin save value of raise time
            while GPIO.input(ECHO)==1:
                stop = time.time() #Echo pin save value of falling time
                
            check_time = stop - start
            distance = check_time * 34300/2
            print("Distance : %.1f cm" % distance)
            time.sleep(0.4)
            try:
                if distance > 23:
                    print("warning! detected stranger!")
                    pwm = GPIO.PWM(BUZZER, 262)
                    pwm.start(50.0)
                    time.sleep(5)
                    GPIO.output(LED, True)
                    time.sleep(1)
                    GPIO.output(LED, False)
                    time.sleep(1)
                    
                    pwm.stop()
                    
                    send_file = save_moive()
                    cur_time = time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))
                    title = '경고: 금고에 침입이 발생하였습니다'
                    send_mail(title,cur_time+'에 촬영된 영상입니다', 'imhw1997@naver.com', send_file)
                    print("메일 전송 완료")
                 
            
            except KeyboardInterrupt:
                print("error")     
                       
                    
except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()
