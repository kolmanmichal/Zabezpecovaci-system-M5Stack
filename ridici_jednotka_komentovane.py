from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt

setScreenColor(0x222222)

#používané proměnné
alarm = None
zadanyPIN = None
senzor = None
zadatPIN = None
poplach = None
PIN = None




#odběr z MQTT
def fun_kolman_(topic_data):
  global alarm, zadanyPIN, senzor, zadatPIN, poplach, PIN
  if topic_data == 'PohybNaSenzoru': #když je pohyb na senzoru
    if alarm == True and poplach == False: #a zároven je alarm zapnutý a poplach ještě nění spuštěný
      senzor = True #uloží se do proměnné senzor, že je někde pohyb, následně se v timeru spustí poplach
  if topic_data == 'AktivovatAlarm': #když z dashboardu dostanu příkaz pro spuštění alarmu
    alarm = True #alarm se aktivuje
  if topic_data == PIN: #když z dashboardu přijde něco, co neznám (za běžného provozu to může být jedině výstup z klávesnice) a to něco je shodné se správným pinem...
    zadanyPIN = PIN #...do zadaného pinu se zapíše příchozí číslo a následně se v timeru vypne alarm a případně i poplach
  pass

#tlačítko B (spuštění alarmu a zadání 2)
def buttonB_wasPressed():
  global alarm, zadanyPIN, senzor, zadatPIN, poplach, PIN
  if zadatPIN == False: #když je zadávání pinu neaktivní, slouží B pro spuštění alarmu
    alarm = True #spuštění alarmu
    m5mqtt.publish(str('kolman'),str('AlarmAktivni'))#publikuje stav alarmu
  if zadatPIN == True: #když je zadávání pinu aktivní, slouží B pro zadání 2
    zadanyPIN = (str(zadanyPIN) + str('2')) #přidat do zadaného pinu znak 2
    lcd.print(zadanyPIN, 20, 140, 0xffffff) #vypíše zadaný pin
  pass
btnB.wasPressed(buttonB_wasPressed)

#tlačítko A (zadání 1)
def buttonA_wasPressed():
  global alarm, zadanyPIN, senzor, zadatPIN, poplach, PIN
  if zadatPIN == True:#když je zadávání pinu aktivní, slouží A pro zadání 1
    zadanyPIN = (str(zadanyPIN) + str('1'))#přidat do zadaného pinu znak 1
    lcd.print(zadanyPIN, 20, 140, 0xffffff) #vypíše zadaný pin
  pass
btnA.wasPressed(buttonA_wasPressed)

#tlačítko C (zadání 3)
def buttonC_wasPressed():
  global alarm, zadanyPIN, senzor, zadatPIN, poplach, PIN
  if zadatPIN == True:#když je zadávání pinu aktivní, slouží C pro zadání 3
    zadanyPIN = (str(zadanyPIN) + str('3'))#přidat do zadaného pinu znak 3
    lcd.print(zadanyPIN, 20, 140, 0xffffff) #vypíše zadaný pin
  pass
btnC.wasPressed(buttonC_wasPressed)

#timer obsahující hlavní část kódu
@timerSch.event('hlavni')
def thlavni():
  global alarm, zadanyPIN, senzor, zadatPIN, poplach, PIN
  m5mqtt.publish(str('kolman'),str('Test'))#každé 2s odesílá do MQTT Test, dashboard pak signalizuje, že komunikace probíhá OK
  lcd.print('aktualizace', 0, 0, 0xffffff)
  lcd.clear()
  if alarm == True: #když je alarm aktivní...
    m5mqtt.publish(str('kolman'),str('AlarmAktivni'))#publikuje stav alarmu (pro dashboard)
    lcd.clear()
    lcd.print('Zabezpeceno', 85, 50, 0x33ff33)#zobrazuje stav alarmu
    lcd.print('1', 65, 200, 0xffffff)#label pro tlačítko A
    lcd.print('2', 155, 200, 0xffffff)#label pro tlačítko B
    lcd.print('3', 245, 200, 0xffffff)#label pro tlačítko C
    lcd.print(zadanyPIN, 20, 140, 0xffffff)#vypisuje aktuálně zadaný pin
    zadatPIN = True #když je alarm aktivní, je možné zadávat pin (B je pro zadání 2 a ne pro spuštění alarmu)
    if PIN == zadanyPIN: #když se zadaný pin shoduje se správným pinem
      poplach = False #vypnout poplach
      m5mqtt.publish(str('kolman'),str('PoplachNeaktivni')) #publikovat stav poplachu (pro dashboard a externí sirénu)
      alarm = False #vypnout alarm
      m5mqtt.publish(str('kolman'),str('AlarmNeaktivni')) #publikovat stav alarmu (pro dashboard)
      zadatPIN = False #zadání pinu deaktivováno
      senzor = False #na žádném senzoru není pohyb
      zadanyPIN = '' #vyprázdnit zadaný pin
    if len(PIN) >= 3 and zadanyPIN != PIN: #když je zadaný pin >=3 (délka správného pinu - v případě změny pinu aktualizovat délku) a zároveň se pin neshoduje se správným pinem...
      zadanyPIN = ''#...tak zadaný pin vyprázdnit
    if senzor == True: #když je na nějakém senzoru pohyb...
      poplach = True #...tak spustit alarm
      m5mqtt.publish(str('kolman'),str('PoplachAktivni')) #publikovat stav poplachu (pro dashboard a externí sirénu)
      if poplach == True: #když je poplach aktivní, začít pípat
        speaker.tone(1800, 500)
        speaker.tone(1000, 500)
  else: #když je alarm vypnutý (nehlídá se objekt)...
    zadatPIN = False #zadávání pinu je zakázáno, B slouží pro spuštění
    lcd.clear()
    lcd.print('Nezabezpeceno', 80, 50, 0xff0000) #vypsat stav alarmu
    lcd.print('ZAPNOUT', 110, 200, 0xffffff) #label pro tlačítko B
  pass

#setup
lcd.print('Nacitani...', 0, 0, 0xffffff)#sysém se při spuštění dlouho načítá, takže aby bylo videt, že se něco deje
m5mqtt = M5mqtt('main-kolman', 'broker.mqttdashboard.com', 1883, '', '', 300) #nastavení MQTT
m5mqtt.subscribe(str('kolman'), fun_kolman_)#odebíraný topic
m5mqtt.start() #spuštění mqtt
senzor = False #žádný pohyb na senzorech
alarm = False #alarm vypnutý
m5mqtt.publish(str('kolman'),str('AlarmNeaktivni')) #publikuje stav alarmu
poplach = False #poplach vypnutý
m5mqtt.publish(str('kolman'),str('PoplachNeaktivni')) #publikuje stav poplachu
PIN = '123' #správný pin
zadanyPIN = '' #zadaný pin
zadatPIN = False #zadávání pinu je vypnuté, B slouží pro zapnutí alarmu
timerSch.setTimer('hlavni', 2000, 0x00) #nastavit timer s hlavním kódem
timerSch.run('hlavni', 2000, 0x00) #spustit timer s hlavním kódem
