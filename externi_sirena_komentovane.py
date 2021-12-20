from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt
import unit

setScreenColor(0x222222)

#relé
relay_0 = unit.get(unit.RELAY, unit.PORTB)





#odběr z MQTT
def fun_kolman_(topic_data):
  # global params
  if topic_data == 'PoplachAktivni': #když přijde zpráva, že poplach je aktivní...
    lcd.clear()
    lcd.print('Poplach aktivni', 0, 0, 0xffffff) #vypíše, že poplach je aktivní
    speaker.tone(1800, 450) #pípnutí (opakuje se vždy když dostanu zprávu z řídící jednotky - perioda závidí na timeru řídící jednotky (2s))
    relay_0.on() #sepne se relé na kterém může být připojena siréna, světlo...
  if topic_data == 'PoplachNeaktivni': #když je poplach neaktivní...
    lcd.clear()
    lcd.print('Poplach neaktivni', 0, 0, 0xffffff) #vypíše, že poplach je neaktivní
    relay_0.off() #rozepne relé na kterém může být připojena siréna, světlo...
  pass

#setup
m5mqtt = M5mqtt('sirena-kolman', 'broker.mqttdashboard.com', 1883, '', '', 300) #nastavení MQTT
m5mqtt.subscribe(str('kolman'), fun_kolman_) #odebíraný topic
m5mqtt.start() #spuštění MQTT