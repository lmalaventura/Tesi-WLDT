# Mappa dei materiali per la tesi

Documento di raccordo tra il lavoro tecnico già svolto e i capitoli da
redigere. Non costituisce ancora testo definitivo da consegnare.

## Questione preliminare sul titolo

Il titolo provvisorio precedente faceva riferimento a query NL → SQL. Il
lavoro approvato e documentato nella repository realizza invece una
trasformazione NL → chiamata REST guidata dalla OpenAPI del Persistence
Service. Il titolo deve quindi essere verificato con coordinatore e relatrice
prima di impostare il frontespizio e l'introduzione definitiva.

## Possibile struttura dei capitoli

### 1. Contesto e obiettivi

Materiali di partenza:

- `01_appunti/architettura_wldt.md`;
- `04_progettazione/integrazione_wldt.md`;
- repository WLDT elencate in `00_materiali/lista_repository.md`.

### 2. Contratto OpenAPI e formulazione del problema

Materiali di partenza:

- `00_materiali/openapi.yaml`;
- `02_esperimenti/baseline/E001_chatgpt_openapi/`;
- `02_esperimenti/benchmark_v1.md` e `benchmark_v2.md`.

### 3. Metodologia sperimentale

Materiali di partenza:

- prompt e output E002–E009;
- `03_risultati/metodologia_valutazione.md`;
- `03_risultati/confronto_modelli.md`.

### 4. Progettazione della pipeline

Materiali di partenza:

- `04_progettazione/architettura_agente.md`;
- `04_progettazione/formato_output_LLM.md`;
- `04_progettazione/validazione.md`;
- E010 sul confronto degli approcci agentici.

### 5. Implementazione

Materiali già disponibili:

- `05_codice/agent/` come prototipo iniziale;
- `01_appunti/decisioni_tecniche.md`.

Da completare con l'Agent Service, i test di integrazione e le modifiche
additive al Query Workbench.

### 6. Valutazione e discussione

Materiali di partenza:

- risultati dei benchmark esplorativi;
- limiti metodologici già documentati;
- futuri test end-to-end e confronto tra chiamata generata e risultato atteso.

### 7. Conclusioni e sviluppi futuri

Da redigere dopo l'integrazione. Dovrà distinguere risultati effettivamente
misurati, limiti dell'hardware locale e possibili estensioni della pipeline.
