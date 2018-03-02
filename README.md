# openbookscanner

Hier entsteht ein offener Buchscanner.
Das Projekt basiert auf dem [mäqädat](https://www.bookscanner.de/der-buchscanner/)-Projekt. Dieses wiederum ist an die Arbeit von [Dany Qumsiyeh](http://www.prismscanner.org/ "www.prismscanner.org") angelehnt, der den von ihm erfundenen Buchscanner ([US Patent 8711448](https://www.google.com/patents/US8711448 "https://www.google.com/patents/US8711448")) zum Nachbau oder für Veränderungen freigegeben hat.
Wir möchten die Dokumentation des mäqädat-Scanners vervollständigen und ihn zu einem vollständigen Open Source Hardware System weiterentwickeln. Aktuell ist der einfache Nachbau des mäqädat leider nicht möglich. Es fehlt eine genaue Dokumentation und die Software für die Ansteuerung des Scanners.

## Architektur

Der Buchscanner besteht aus mehreren Teilen.
- **Das Gestell**  
  Das Gestell kann man nach Bauplan zusammenbauen.
- **Hardware**  
  Die Hardware umfasst Scanner, Sensorik, das Gebläse und die Motoren.
- **Arduino**  
  Der Arduino ist für die Echtzeitansteuerung der Komponenten zuständig.
- **Raspberry-Pi**  
  Der Raspberry-Pi umfasst die Nutzerintraktion sowie komplexere Aufgaben.

[![Architektur][architektur]][architektur]


[architektur]: architektur.svg
