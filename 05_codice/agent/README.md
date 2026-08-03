# Prototipo locale dell'agente WLDT

Questa cartella contiene il prototipo sviluppato prima dell'Agent Service. Il
codice serve a verificare il flusso selezione → prompt → Ollama → validazione →
preparazione HTTP e viene conservato come evidenza della fase progettuale.

Non è ancora il servizio integrato nel sistema WLDT.

## Funzioni implementate

- selezione deterministica tra cinque operazioni codificate manualmente;
- costruzione di un prompt limitato agli endpoint selezionati;
- invocazione di Qwen3 8B tramite API di Ollama;
- output JSON vincolato con JSON Schema;
- validazione preliminare;
- costruzione di URL, header e body della richiesta REST;
- test unitari dei componenti deterministici.

## Componenti

- `models.py`: modelli interni;
- `api_selector.py`: catalogo e selezione lessicale;
- `prompt_builder.py`: prompt e schema dell'output;
- `ollama_client.py`: comunicazione con Ollama;
- `validator.py`: controlli preliminari;
- `rest_client.py`: preparazione, non esecuzione, della richiesta;
- `main.py`: interfaccia da terminale;
- `tests/`: test unitari.

## Avvio del prototipo

Con Ollama attivo e `qwen3:8b` installato:

```bash
cd 05_codice/agent
python main.py
```

## Test

```bash
cd 05_codice/agent
python -m unittest discover -s tests -v
```

Al checkpoint del 3 agosto 2026 la suite contiene 18 test e viene completata
senza errori.

## Limiti noti

1. Il catalogo delle API non deriva dalla OpenAPI.
2. La regola per lo storico associa sempre la richiesta a
   `/query/event/values/history`; nell'implementazione reale un intervallo
   temporale richiede `/query/event/values/valuesByName`.
3. Il validatore richiede valori per gli array di filtro di
   `/query/event/stats`, mentre il backend accetta array vuoti come assenza del
   filtro.
4. La validazione dei body copre soltanto alcune regole hard-coded.
5. Lo schema vincola separatamente l'insieme dei metodi e quello degli
   endpoint; la coppia viene controllata soltanto dal validatore successivo.
6. `RestClient` usa come default `http://localhost:8080`, mentre il Persistence
   Service analizzato usa normalmente la porta `8081`.
7. `RestClient` prepara la richiesta ma non la invia.
8. Non esistono endpoint HTTP dell'agente, caricamento dinamico della OpenAPI,
   gestione centralizzata della configurazione o integrazione con il frontend.

Questi limiti verranno corretti nel nuovo `agent_service` invece di trasformare
retroattivamente il prototipo sperimentale.
