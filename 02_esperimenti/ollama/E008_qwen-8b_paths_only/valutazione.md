# Valutazione E008

## Esperimento

**Nome:** E008 – Qwen3 8B con descrizione sintetica delle API

## Obiettivo

Verificare se una rappresentazione sintetica degli endpoint, priva degli
schemi OpenAPI completi, migliori la capacità del modello di selezionare la
chiamata API corretta.

## Esito

Q1: corretta
Q2: corretta
Q3: corretta
Q4: corretta
Q5: corretta

## Risultato

Accuratezza nella selezione degli endpoint: **5/5**

Il benchmark non valuta la costruzione completa della richiesta REST,
poiché al modello è stata fornita esclusivamente una rappresentazione
sintetica delle API.

Di conseguenza il risultato non è confrontabile con i benchmark
E002–E006.

## Conclusioni

Il modello individua correttamente tutti gli endpoint.

In questa esecuzione la rappresentazione sintetica delle API produce una
selezione degli endpoint migliore rispetto alle esecuzioni con OpenAPI completa.

L'esperimento motiva la scelta progettuale di fornire al modello una
descrizione compatta delle operazioni candidate. Il risultato deve essere
confermato con test ripetuti sulla pipeline integrata.

## Nota metodologica

Questo esperimento è stato progettato come benchmark diagnostico.

L'obiettivo non è valutare la traduzione completa di una richiesta in una
chiamata API conforme all'OpenAPI, ma verificare la capacità del modello di
selezionare l'endpoint corretto quando le API vengono rappresentate in forma
compatta.

Per questo motivo il risultato deve essere interpretato separatamente
rispetto ai benchmark completi.