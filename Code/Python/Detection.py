# Importer OpenCV, matematik, seriel og YOLO-biblioteket 
import cv2 
import math 
import serial 
from ultralytics import YOLO 
 
#Her downloades modellen efter den er trænet 
model = YOLO("best.pt") 
 
# Her åbnes en seriel-kommunikation med nedenstående port, med de angivne 
#indstillinger 
# Er inspireret af forskellige kodestumper fra internettet og sat sammen til 
#nedenstående 
# Dette stykke kode, virker kun, hvis programmet køres på en linux-computer og 
#der er et device tilknyttet porten 
ser = serial.Serial( 
    port='/dev/ttyACM0',   # Hvilken port der skal åbnes for 
    baudrate=9600,       # Hvilken hastighed de to devices snakker med 
    parity=serial.PARITY_NONE, 
    stopbits=serial.STOPBITS_ONE, 
    bytesize=serial.EIGHTBITS, 
    timeout=1 
) 
 
# I denne funktion bestemmes det hvilken karakter der skal sendes til arduinoen 
#over serielporten 
# Denne karakter bestemmes ud fra hvor på billedet at cigaretskoddet er fundet 
def chooseOutPut(valX): 
    if valX <= 170: 
        ser.write(("L").encode()) 
    if valX > 170 and valX <= 340: 
        ser.write(("M").encode()) 
    if valX > 340 and valX <= 511: 
        ser.write(("R").encode()) 
 
 
#Her åbnes forbindelsen til kameraet der er tilsluttet Raspberry Pi'en 
vid = cv2.VideoCapture(0) 
 
 
while(True): 
 
    # Tages hver "frame" fra kameraet og gemmes i en variabel 
    ret, frame = vid.capturearray 
 
    # Her gemmes alle fundne instanser af cigaretskodder fundet på billedet 
    results = model(frame, stream=True) 
 
    # Her gennemgås all fundne cigaretskodder og der tegnes en kasse rundt om 
    #dem 
    for r in results: 
        kasser = r.boxes 

         for kasse in kasser: 
            #Her udregnes kassens størrelse 
            x1, y1, x2, y2 = kasse.xyxy[0] 
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
 
            # Kassen placeres her på billedet der vises på skærmen 
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3) 
 
            # Her udregnes det, hvor sikker modellen er på dens gæt 
            sikkerhed = math.ceil((kasse.conf[0]*100))/100 
            print("Sikkerhed --->",sikkerhed) 
 
            #Her opsættes lidt information om hvor centrum af skoddet er 
            # Samt hvilken font og farve der skal bruges til kassen 
            centrum = [x1, y1] 
            font = cv2.FONT_HERSHEY_SIMPLEX 
            fontScale = 1 
            farve = (0, 0, 255) 
            tykkelse = 2 
            text = "Person: x=" + str(x1) + ", y=" + str(y1) 
 
            #Her sendes der til arduinoen i hvilken side af billedet skoddet er 
            chooseOutPut(x1) 
 
            # Så skrives teksten på skærmen 
            # Denne del er kun relevant mens der testes, og kan fjernes når der 
            # ikke længere sidder et display til Raspberry Pi'en 
            cv2.putText(frame,text,centrum, font, fontScale, farve, tykkelse) 
 
    # Her tegnes billedet på displayet 
    # Denne del er kun relevant mens der testes, og kan fjernes når der 
    # ikke længere sidder et display til Raspberry Pi'en 
    cv2.imshow('Webcam', frame) 
 
 
 
    # Her sættes det op at man kan trykke på 'q' for at 
    # stoppe programmet. Denne metode er inspreret af 
    # kodestykker pa internettet 
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break 
 
# Her frigives kameraet når programmet lukkes 
vid.release() 
# Her lukkes alle vinduer der er åbnet af programmet 
cv2.destroyAllWindows() 