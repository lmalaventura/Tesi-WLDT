# E006 — Traduzione NL → API con OpenAPI minimale

## Modello
Qwen3 8B

## Input
- openapi_minimal.yaml
- cinque richieste in linguaggio naturale

## Prompt

Utilizza esclusivamente il file OpenAPI allegato come descrizione delle API disponibili.
Per ciascuna delle richieste in linguaggio naturale riportate sotto, determina quale chiamata API dovrebbe essere eseguita.
Non inventare endpoint, parametri, campi, operatori o strutture non presenti nell'OpenAPI.
Per ogni richiesta restituisci:

1. metodo HTTP;
2. endpoint;
3. path parameter, query parameter e/o body necessario;
4. eventuali informazioni che non possono essere determinate dalla richiesta;
5. una breve motivazione della scelta.

Se la richiesta non può essere tradotta completamente utilizzando il solo OpenAPI, dichiaralo esplicitamente.
NON eseguire realmente nessuna chiamata.

---

Q1:
Mostrami tutti i Digital Twin disponibili.

Q2:
Mostrami il valore corrente delle proprietà del Digital Twin con id "HDT-001".

Q3:
Mostrami lo storico della proprietà "heartRate" del Digital Twin "HDT-001" tra il 1 luglio 2026 e il 7 luglio 2026.

Q4:
Trova i Digital Twin per cui la proprietà "systolicPressure" ha un valore maggiore di 150.

Q5:
Calcola le statistiche della proprietà "heartRate" per i Digital Twin selezionati nell'intervallo dal 1 luglio 2026 al 7 luglio 2026.