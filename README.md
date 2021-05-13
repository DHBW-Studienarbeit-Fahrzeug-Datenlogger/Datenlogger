![DHBW Logo](https://it.dhbw-stuttgart.de/DHermine/dh-logo.gif)

# Studienarbeit: Fahrzeug-Datenlogger
Innerhalb des Studienprojektes wurde ein Datenlogger-System aufgebaut. Dieses ermöglicht die Aufnahme verschiedener Daten mithilfe eines GPS-Sensors, eines Temperatur-Sensors und eines OBD-Loggers, mit welchem mehrere unterstützte Fahrzeugsignale ausgelesen werden können. OBD steht für On-Board Diagnosis und stellt verschiedene essenzielle Fahrzeugdaten zur Verfügung. Diese Daten werden automatisch an einen Server übertragen und innerhalb einer Datenbank abgespeichert, sobald das Fahrzeug innerhalb der Reichweite des Netzwerks abgestellt wird, in welchem sich auch der Server befindet.
<br/>

---

# Bedienungsanleitung
</br>

## Webanwendung

Um den Server Raspberry Pi hochfahren zu können, muss die Stromversorgung aller enthaltener Module durch Einstecken eines Kabels hergestellt werden.

Die Webanwendung wird automatisch gestartet, sobald der Server Raspberry Pi hochgefahren wird. Falls die Webanwendung abstürzt, kann sie wieder gestartet werden, indem die Befehle im Quellcode 1 ausgeführt werden.


	cd
	cd Studienarbeit_OBD_Datenlogger/web-application/
	node www


Soll die Webanwendung abgebrochen und dann neu gestartet werden, muss zunächst der Befehl wie in Quellcode 2 ausgeführt werden.


	cd
	cd Studienarbeit_OBD_Datenlogger/web-application/
	sudo kill -9 $(sudo lsof -t -i:3000)
	node www


Die Webanwendung wird über den lokalen Port 3000 im selben Netzwerk erreicht, in welchem sich der Server Raspberry Pi befindet.
</br>
Wird die Webanwendung aufgerufen, muss zunächst eine Registrierung erfolgen. Das Interface dazu ist in Abbildung 2 dargestellt. Wird keine E-Mail erhalten, welche den Link zur Bestätigung des Accounts enthält, kann es sein, dass die Webanwendung nicht auf das Gmail-Konto zugreifen kann. Um das Problem zu lösen, muss im Gmail-Konto eingetragen sein, dass der Zugriff auch durch andere Apps als Gmail zugelassen ist. Zudem muss vor dem Registrierungsprozess der Captcha-Test ausgesetzt werden, welcher meist automatisch durch eine Veränderung des Netzwerks bzw. des Standorts vorgeschaltet wird: [How to disable captcha](https://www.dailytechtuts.com/2620/clear-captcha-imap/).

Ist die Registrierung samt Bestätigung des Accounts abgeschlossen, kann eine Anmeldung innerhalb der Webanwendung erfolgen und das Dashboard wird angezeigt. Standardmäßig wird zunächst das Interface zur Auswahl von Routen dargestellt, welche innerhalb der Kartendarstellung angezeigt werden sollen. Über die Sidebar kann zwischen diesem Interface und dem Interface zur Simulation einer Plug-In Fahrt gewechselt werden. Der Wechsel erfolgt durch einen Klick auf die jeweilige Bezeichnung.
<br/>
Sollen eine oder mehrere Routen in der Kartendarstellung betrachtet werden, kann die Auswahl innerhalb des Interface *View drive cycles* eingestellt werden. Dabei kann zunächst ausgewählt werden, ob reale, aufgenommene oder simulierte Routen betrachtet werden sollen. Danach wird die Eingrenzung der anzuzeigenden Routen vorgenommen. Dabei kann eine der Optionen ausgewählt werden, anschließend wird entweder ein Schwellwert für die Optionen *Minimum of route length* und *Minimum of energy consumption* oder ein exakter Wert für die Optionen *VIN* und *ID* im Textfeld eingegeben.

Die vorgenommenen Einstellungen werden mit dem Submit-Button bestätigt. Bei der Option *VIN* ist die Fahrzeugidentifikationsnummer des bei der Fahrt verwendeten Fahrzeugs anzugeben. Die bereits aufgenommenen Fahrten sind unter der VIN **12345** in der Datenbank abgespeichert, um den Zugriff zu erleichtern.

Nach der Bestätigung der Einstellungen wird die Kartendarstellung innerhalb des Dashboards dargestellt. Bis die Routen vollständig eingezeichnet sind, wird eine gewisse Zeit benötigt. Die erste Karte enthält alle Routen, die den eingegebenen Eingrenzungen entsprechen. Wird auf eine Route geklickt, erscheint über dieser ein Pop-Up Fenster, welches die ID der Route enthält. Handelt es sich um eine simulierte Route, wird zudem der Energieverbrauch für die Temperatur, den reinen Fahrtprozess sowie die verbrauchte Gesamtenergie angezeigt.
</br>
In der zweiten Karte werden die Wartezeiten zwischen den Routen dargestellt. Die eingezeichneten Markierungen entsprechen dabei dem Endpunkt einer Fahrt. Beim Klicken auf eine Markierung erscheint ein kleines Pop-Up Fenster über der Markierung, welche die Wartezeit an dieser Stelle anzeigt. Unterhalb der Karte kann eine von mehreren Ladevarianten ausgewählt werden.

Zudem kann über einen Schieberegler ausgewählt, welche Aufladung mindestens erfolgen soll. Wird die Auswahl über den Submit-Button bestätigt, werden nur noch die Wartepunkte angezeigt, deren Wartezeit mit der gegebenen Ladevariante ausreicht, um die Mindestaufladung zu erfüllen. Bei Klick auf eine Markierung wird im Pop-Up Fenster zusätzlich die mögliche Aufladung angezeigt.
</br>
In der dritten Karte können detailliert die Fahrten eines ausgewählten Tages betrachtet werden. Dazu wird links von der Karte ein Datum ausgewählt.
Die Fahrten des ausgewählten Tages werden in der Karte eingezeichnet. Zudem wird unter der Karte für jede dargestellte Fahrt ein Diagramm angezeigt, welches die Motordrehzahl sowie die Geschwindigkeit enthält und ein Diagramm, welches das Höhenprofil der Fahrt darstellt. Links von der Karte kann durch Klicken auf die jeweilige Fahrtanzeige eine Fahrt ab- oder angewählt werden. Wird auf die Route innerhalb der Karte geklickt, erscheint ein Pop-Up Fenster mit dem gleichen Inhalt wie bei der ersten Karte.

Direkt unterhalb der dritten Karte kann eine farbige Markierung der Strecke anhand von Fahrteigenschaften ausgewählt werden. Bisher implementiert ist die Geschwindigkeit, anhand welcher die Streckenabschnitte eingefärbt werden. In der linken unteren Ecke der Karte befindet sich eine Legende mit der Bedeutung der Farben.
</br>
Als Alternative zum Interface für die Auswahl der darzustellenden Routen kann auch das Interface zur Simulation einer Plug-In Fahrt angezeigt werden.

Um die Simulation durchzuführen, wird eine aufgenommene Strecke anhand ihrer ID sowie ein Fahrzeug aus der Datenbank anhand seiner Bezeichnung ausgewählt. Bisher wurden nur für den Citroen C4 Picasso alle erforderlichen Parameter eingetragen, daher ist nur dieses Fahrzeug zur Simulation geeignet. Die Auswahl wird mit dem Submit-Button bestätigt und nach einer gewissen Zeit wird die simulierte Strecke in der Kartenansicht des Dashboards angezeigt.
</br>
Über die Schaltfläche *Welches E-Auto passt zu mir?* kann ein Pop-Up Fenster aufgerufen werden, welches dazu dient, ein passendes Fahrzeug anhand verschiedener Parameter auszuwählen. Dazu kann innerhalb des Fensters der gewünschte Fahrzeugtyp sowie der Fahrstil ausgewählt werden.

Wird die Auswahl bestätigt, erfolgt ein Vorschlag für ein passendes elektrisches Automobil aus der Datenbank. Das Fahrzeug verfügt dabei über eine Reichweite, welche knapp über der durchschnittlichen Routenlänge liegt. Befindet sich in der Fahrzeugkategorie kein Fahrzeug mit ausreichender Reichweite, wird dasjenige mit der höchsten Reichweite vorgeschlagen.
</br>
Über die Schaltfläche *Logout* erfolgt die Abmeldung aus der Webanwendung.
</br>
## OBD Datenlogger - Datenaufnahme

### Schritt 1: Vorbereitung des Datenloggers
Der erste Schritt ist die Vorbereitung des Datenloggers. Hierfür muss die neueste Software Version auf den Raspberry Pi geladen werden. Diese ist zu finden über den [Datenlogger GitHub](https://github.com/DHBW-Studienarbeit-Fahrzeug-Datenlogger/Studienarbeit_OBD_Datenlogger). Nachdem die neuste Softwareversion vorhanden ist, muss der OBD Datenlogger ordnungsgemäß heruntergefahren werden, damit Ausschalt- und Einschaltprotokolle wie erwartet abgearbeitet werden können. Falls die neueste Version der Software bereits auf dem Logger vorhanden ist,  ist Schritt 1 optional.
</br>
### Schritt 2: Vorbereitung des Fahrzeugs
In dem zweiten Schritt wird das Fahrzeug vorbereitet.
Hierfür muss die OBD-2 Schnittstelle im Fahrzeug freigelegt und der OBD-2 Dongle eingesteckt werden. Die Schnittstelle befindet sich je nach Fahrzeughersteller an unterschiedlichen Stellen und ist der Fahrzeugbedienungsanleitung zu entnehmen. Üblicherweise ist die Schnittstelle in der Nähe der elektrischen Sicherungen angebracht. Ob der Dongle korrekt eingesteckt ist, kann an einer LED am Dongle erkannt werden, die bei aktivierter Zündung aufleuchtet.

Zur Stromversorgung des Loggers eignet sich ein 5 Volt Micro-USB Ladegerät, das an eine 12 Volt Fahrzeugsteckdose angeschlossen wird. Alternativ kann auch eine 5V / 2A Powerbank die Stromversorgung übernehmen. Der Logger kann schon vor dem Fahrzeugstart angeschlossen werden. Vor Fahrbeginn muss eine klimaneutrale und gesicherte \linebreak Position definiert werden. Aufgrund der lokalen Temperaturmessung sollte eine Position direkt an einem der Klimaauslässe vermieden werden. Der Logger sollte soweit befestigt sein, dass er während keines Fahrmanövers seine Position verändert und in einer Unfallsituation kein gefährliches Flugobjekt sein kann.
</br>
### Schritt 3: Start der Datenaufnahme
Nach gestarteter Zündung wird mit einem Knopfdruck der Datenlogger aktiviert. Der Knopf befindet sich in der zweiten Platinenebene überhalb des HDMI Anschlusses.
Ab jetzt kann der Loggingstatus an den RGB LEDs auf der dritten Platinenebene abgelesen werden.

Farbe | Leuchttyp | Bedeutung
------------ | ------------- | -------------
Grün | Blinken | Verbindung zum OBD-2 Dongle wird hergestellt
Rot | Blinken | GPS Verbindung wird hergestellt
Blau | Dauerleuchten | Datenlogging im GPS-Only Modus
Pink | Dauerleuchten | Datenlogging mit OBD Verbindung

Für den Fall, dass keine OBD Verbindung aufgebaut werden konnte, kann zurück zu Schritt 2 gesprungen und der Prozess wiederholt werden. Es ist darauf zu achten, dass der Logger vollkommen heruntergefahren und der OBD Dongle neu eingesteckt ist, bevor ein erneuter Versuch gestartet wird.
</br>
### Schritt 4: Stopp der Datenaufnahme
Die Datenaufnahme wird gestoppt durch Unterbrechung der Stromversorgung. In diesem Fall wird das Stoppprotokoll ausgeführt und die Daten gespeichert. Wenn zu diesem Zeitpunkt der Logger eine WLAN Verbindung hat, werden die Daten direkt an den Server übermittelt.

Für den Fall, dass keine WLAN Verbindung besteht, werden die Daten nur lokal abgelegt. Die Daten können an den Server übermittelt werden durch erneutes Herunterfahren mit bestehender Internetverbindung.
