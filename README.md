# Tesi WLDT — agente LLM per richieste NL → REST

Repository di lavoro per la tesi dedicata alla traduzione di richieste in
linguaggio naturale nelle chiamate REST esposte dal Persistence Service WLDT.

## Stato al 3 agosto 2026

Sono stati completati:

- analisi del contratto OpenAPI v0.2.0;
- definizione di un benchmark con cinque richieste;
- confronto esplorativo tra ChatGPT, Qwen3 e Llama 3.1;
- esperimenti sulla rappresentazione del contesto API;
- prototipo locale della pipeline;
- progettazione dell'integrazione con il sistema WLDT.

Il prototipo corrente dimostra la sequenza selezione API → costruzione del
prompt → invocazione di Ollama → output JSON → validazione preliminare →
preparazione della richiesta HTTP. Non costituisce ancora l'Agent Service
integrato e presenta limiti documentati nel relativo README.

## Struttura

- `00_materiali/`: specifiche OpenAPI e repository di riferimento;
- `01_appunti/`: diario e registro delle decisioni tecniche;
- `02_esperimenti/`: prompt, output e valutazioni dei benchmark;
- `03_risultati/`: sintesi, criteri di valutazione e limiti metodologici;
- `04_progettazione/`: architettura, validazione e proposta di integrazione;
- `05_codice/agent/`: prototipo Python e test automatici;
- `06_tesi/materiale_capitoli/`: raccordo tra documentazione e futura stesura.

## Test del prototipo

Dalla cartella `05_codice/agent`:

```bash
python -m unittest discover -s tests -v
```

Nello stato revisionato risultano presenti 18 test sui componenti
deterministici e la suite viene completata senza errori. Le chiamate a Ollama
e al Persistence Service non fanno parte della suite unitaria.

## Repository WLDT analizzate

La lista delle repository attualmente disponibili è riportata in
`00_materiali/lista_repository.md`.
