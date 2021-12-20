from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt
import hat
import hat

setScreenColor(0x111111)

#senzor
hat_pir0 = hat.get(hat.PIR)

#používané proměnné
cisloSenzoru = None




#timer obsahující hlavní část kódu
@timerSch.event('hlavni')
def thlavni():
  global cisloSenzoru
  lcd.clear()
  lcd.font(lcd.FONT_DejaVu72) #nastavení fontu displeje
  lcd.print((hat_pir0.state), 20, 50, 0xffffff) #vypsat stav senzoru na displej
  if (hat_pir0.state) == 1: #když je pohyb...
    m5mqtt.publish(str('kolman'),str(((str('PohybNaSenzoru') + str(cisloSenzoru))))) #odeslat zprávu, že je pohyb na tomto senzoru (pro dashboard)
    m5mqtt.publish(str('kolman'),str('PohybNaSenzoru')) #odeslat zprávu, že je pohyb na nějakém senzoru (pro řídící jednotku)
  else:
    m5mqtt.publish(str('kolman'),str(((str('KlidNaSenzoru') + str(cisloSenzoru))))) #odeslat zprávu, že je klid na tomto senzoru (pro dashboard)
    m5mqtt.publish(str('kolman'),str('KlidNaSenzoru')) #odeslat zprávu, že je klid na nějakém senzoru (pro řídící jednotku)
  pass


#setup
cisloSenzoru = 1 #každý senzor musí mít své číslo (pro každý senzor jiné od 1 do nekonečna)
m5mqtt = M5mqtt('senzor1-kolman', 'broker.mqttdashboard.com', 1883, '', '', 300) #nastavení MQTT
m5mqtt.start() #spuštění MQTT
timerSch.setTimer('hlavni', 1000, 0x00) #nastavení timeru
timerSch.run('hlavni', 1000, 0x00) #spuštění timeru
