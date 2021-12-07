# Zabezpečovací systém M5Stack
Fakulta aplikovaných věd Západočeské univerzity v Plzni

Katedra informatiky a výpočetní techniky - Základy programování pro IoT

## Zadání
Zabezpečovací zařízení detekuje pohyb pomocí PIR čidla, zapne sirénu, rozsvítí světla nebo sepne další zařízení pomocí relé a odešle zprávu přes MQTT.

## Popis
Základní set se skládá z jedné řídící jednotky, jednoho PIR senzoru a jedné jednotky pro ovládání relé. Dále je možné celý systém intuitivně ovládat přes dashboard v Node-REDu.

Systém je v tuto chvíli naprogramovaný pro dva PIR senzory ale je možné ho jednoduše rozšířit pro neomezené množství PIR senzorů. Jednotek s relé je možné připojit také neomezené množství bez nutnosti jakkoliv zásadně měnit kód. Tato jednotka při poplachu píská a zároveň sepne relé, na které je možné napojit jakékoliv zařízení, např. žárovku nebo externí sirénu. Jedinou podmínkou pro rozšiřování je, že každé zařízení musí mít své jedinečné ID v MQTT a pro identifikaci stavu v Node-REDu.

Při spuštění se systém načte a připojí se k MQTT brokeru, následně začnou PIR čidla odesílat pravidelně svůj stav a hlavní řídící jednotka spustí cyklus kontrolující stav všech proměnných. Po načtení e zobrazí na displeji stav systému NEAKTIVNÍ a tlačítko B je označeno popiskem ZAPNOUT. Stisknutím B se systém aktivuje, vypíše na hlavní jednotce stav systému AKTIVNÍ a začne hlídat pohyb na všech senzorech. Pokud detekuje pohyb, spustí sirénu na hlavní jednotce i na jednotce s relé a sepne relé. Tlačítka A, B a C se označí popisky 1, 2, 3 v tomto pořadí. Zadáním správného PINu systém vypne sirény, rozepne relé a deaktivuje se.

Node-RED obsahuje tabulku Status, zobrazující kontrolku komunikace s hlavní řídící jednotkou, stav systému, stav poplachu a stav senzorů. Při neaktivním alarmu se zobrazuje tabulka s tlačítkem pro aktivování alarmu. Při aktivním alarmu se zobrazuje klávesnice pro zadání PINu, tlačítkem pro odeslání PINu a tlačítkem pro smazání zadaného PINu. Pro testování je přes záložku Nastavení\Zobrazit ladění možné zobrazit další tabulku pro ruční odeslání jakéhokoliv příkazu do MQTT. Toto zobrazení je ve výchozím stavu skryto.

## Vlastní řešení
### Simulátor
Pro testování jsem si v C# .NET Windows Forms vytvořil simulátor, na kterém jsem si mohl vyzkoušet vymyšlený algoritmus. Poté stačilo přepsat kód do Pythonu nebo do Blockly pro M5Stack. Mohl jsem tak celý program vytvořit bez nutnosti mít u sebe M5Stack. Když byl program hotový, nahrál jsem ho fyzicky do M5Stacku, otestoval funkčnost a doladil chyby.

### Potřebná zařízení
- 2x M5Stack (1 hlavní, 1 externí siréna)
- 1x/2x M5Stick (senzory)
- 1x/2x PIR hat
- 1x Relay
- NodeRed

#### Hlavní řídící jednotka
- M5Stack
- Řídí celý systém
- Tři zobrazení
  - Načítání
    - Popisek stavu systému (Načítání…)
  - Neaktivní alarm (automaticky po načtení)
    - Stav alarmu (NEAKTIVNÍ)
    - Popisek tlačítka B (ZAPNOUT)
  - Aktivní alarm
    - Stav alarmu (AKTIVNÍ)
    - Popisek tlačítka A (1)
    - Popisek tlačítka B (2)
    - Popisek tlačítka C (3)
    - Aktuálně zadaný PIN
- Pokud chceme alarm ovládat přes M5Stack, musí se heslo skládat z číslic 1, 2 a 3 (→omezené množství tlačítek), při ovládání přes Node-RED je možné jakkoliv dlouhé heslo složené z číslic 0-9 (nutné přeprogramování výchozího PINu)
- Hlavní jednotka vždy přijímá stav senzorů ale jen při aktivním alarmu stavy vyhodnocuje
- Pro vypnutí alarmu zadejte heslo (defaultně 123)
  - Po zadání chybného hesla o délce >=3 se zadané heslo smaže
  - Po zadání správného hesla se alarm deaktivuje a vypíše stav (to může trvat až 2 s → podle nastavení hlavního opakování cyklu řídící jednotky)

##### Přidání další řídící jednotky
Přidání další řídící jednotky do systému není možné. Tato jednotka může být v systému pouze jedna.
Pokud chcete využívat de/aktivování systému z více míst, můžete například použít Raspberry Pi, na kterém bude spuštěn Node-RED s dashboardem

#### Externí siréna
- M5Stack
- Přijímá stav poplachu, pokud je poplach aktivní, začne pískat, pokud bude alarm následně deaktivován (=poplach se vypne), přestane pískat i tato externí siréna
- Dále je zde možné připojit na port B relé, které může sepnout další hardwarovou sirénu, rozsvítit světlo atd. v případě poplachu, po skončení poplachu se relé rozepne
- Tato jednotka není nutná pro fungování systému

##### Přidání další externí sirény
Pokud chcete přidat další externí sirénu, stačí do dalšího M5Stacku nahrát shodný kód jako pro první sirénu. V kódu pak změňte jedinečné ID pro MQTT na libovolnou hodnotu

#### PIR senzor
- M5Stick + PIR hat
- Snímá pohyb a každou sekundu odesílá informace o svém stavu
- Celý systém je naprogramován pro neomezené množství PIR čidel, ale dashboard zobrazuje jen 2 (není problém rozšíření)
- Při nahrávání kódu do čidla je nutné mu v setupu nastavit vlastní číslo, vždy od 1 (dashboard pracuje s čísly 1 a 2 – možné rozšířit)

##### Přidání dalšího senzoru do systému
- Pokud chcete přidat senzor, stačí v kódu PIR změnit název a ID (např. cisloSenzoru=3, MQTT ID nastavit libovolně). Senzor se pak v systému bude hlásit příkazy PohybNaSenzoru3, KlidNaSenzoru3.
- Pro identifikaci senzoru v Node-REDu:
  - Přidejte node ‚Function‘ → do něj zkopírujte kód z nodu ‚Function‘ „senzor 1“ → v kódu upravte identifikaci senzoru
    - PohybNaSenozru1 změňte na PohybNaSenzoru3
    - KlidNaSenozru1 změňte na KlidNaSenzoru3

    Tuto funkci spojte s nodem ‚Tunel‘ napojeného na MQTT node
  - Dále přidejte node ‚Text‘ čtoucí hodnotu msg.payload a tento node spojte s předchozí funkcí pro senzor 3

#### Node-Red dashboard
- Ovládací panel pro celý systém
  - Možné vzdálené ovládání systému
- Dashboard je rozdělen na 4 části
  - Status
  - Zadání pinu
  - Aktivace alarmu
  - Ladění
- Pokud se spustí poplach, NodeRed odešle mail s textem „Váš objekt byl narušen v {timestamp}“
  - Během jednoho poplachu je odeslán jeden mail bez závislosti na délce trvání poplachu

##### Status
- Status zobrazuje stav alarmu, stav poplachuy stav 2 čidel (možné rozšíření) a komunikace s hlavní řídící jednotkou
  - Zobrazuje se vždy
  - Stav alarmu signalizován ikonou odemčeného a zamčeného zámku
  - Aktivní poplach je signalizován ikonou výstrahy
  - Stav čidel signalizován ikonou panáčka a fajvky
  - Stav komunikace s řídící jednotkou je signalizován červeným a zeleným puntíkem (při každém opakováním hlavního cyklu je odeslán příkaz „Test“, pokud Node-RED tento příkaz přijme, přebarví puntík na zeleno a následně na červeno)
  
##### Zadání pinu
- Zadání pinu slouží k zadání pinu a následné deaktivaci systému
  - Pokud bude v systému použit PIN skládající se z číslice 0 nebo číslic 4-9, je nutné zadávat PIN přes dashboard v Node-REDu
  - Zadejte pin pomocí klávesnice na obrazovce, následně pin odešlete tlačítkem DEAKTIVOVAT, pin lze smazat tlačítkem SMAZAT
  - Zobrazuje se jen v případě, že je alarm aktivní
  
##### Aktivace alarmu
- Aktivace alarmu slouží k aktivaci alarmu
  - Zobrazuje se jen v případě, že je alarm neaktivní
  
##### Ladění
- Ladění slouží k manuálnímu odesílání zpráv do MQTT
  - Defaultně je skryto
  - Pro zobrazení/skrytí ladění je nutné použít inject v prostředí NodeRedu nebo přes Záložku Nastavení, kde použijte tlačítko Zobrazit/Skrýt ladění
  - Jsou zde tlačítka pro odeslání všech zpráv, které se v systému používají
  - Pro smazání výpisu ve statusu použijte tlačítko VYČISTIT STATUS
  - Pro odeslání jiné zprávy použijte řádek v horní části tabulky

### MQTT
#### Použitý MQTT broker
- Využívám MQTT broker HiveMQ
 
    https://www.hivemq.com/public-mqtt-broker/
- Nastavení
  - Server: broker.hivemq.com
  - Port: 1883
  - ID
    - Senzor: senzor1-kolman
    - Hlavní jednotka: main-kolman
    - Externí siréna: sirena-kolman
    - Dashboard: dashboard-kolman
  - Topic: kolman
#### MQTT příkazy
- Stav alarmu
  - AlarmAktivni / AlarmNeaktivni
- Stav poplachu
  - PoplachAktivni / PoplachNeaktivni
- Vzdálené de/aktivování alarmu
  - AktivovatAlarm / 123 (správný PIN)
- Příkaz pro spuštění poplachu ze senzoru
  - PohybNaSenzoru / KlidNaSenzoru
- Zpráva o stavu senzoru pro Node-RED
  - PohybNaSenzoru1 / Klid NaSenzoru1
- Zpráva o stavu komunikace hlavní jednotky s Node-REDem
  - Test
