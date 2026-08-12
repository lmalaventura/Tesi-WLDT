# Benchmark controllato della pipeline

Questa cartella contiene il benchmark utilizzato per verificare in maniera
controllata la pipeline completa dell'Agent Service.

## Contenuto

```text
cases.json
mock_persistence.py
run_benchmark.py
results_20260810_201100.json
```

### `cases.json`

Contiene i cinque casi funzionali e la relativa ground truth utilizzata per lo
scoring.

### `mock_persistence.py`

Implementa un Persistence Service simulato utilizzato durante il benchmark.
Il mock espone:

- la specifica OpenAPI sperimentale;
- gli endpoint necessari a verificare che una chiamata validata raggiunga
  effettivamente il livello di esecuzione.

Non sostituisce i successivi test di integrazione effettuati contro il
Persistence Service WLDT reale.

### `run_benchmark.py`

Esegue la pipeline dell'Agent Service sui casi definiti in `cases.json` e
registra:

- operazione prodotta;
- argomenti;
- correttezza semantica;
- esito della validazione;
- esito dell'esecuzione;
- successo end-to-end;
- tempi di esecuzione.

## Risultato congelato

Il risultato utilizzato nella documentazione della tesi è:

```text
results_20260810_201100.json
```

Data:

```text
10/08/2026
```

Configurazione:

```text
5 casi
3 ripetizioni per caso
15 esecuzioni complessive
```

Risultati aggregati:

```text
Operation accuracy:      80%
Arguments accuracy:      60%
Semantic accuracy:       60%
Validation pass rate:    80%
Execution success rate:  80%
End-to-end success rate: 60%
Average wall time:       25.731 s
```

L'analisi è disponibile in:

```text
03_risultati/benchmark_pipeline_finale.md
```

## Interpretazione

I cinque casi sono stati utilizzati anche durante lo sviluppo e la diagnostica
della pipeline.
Il risultato deve quindi essere considerato un benchmark controllato e
regressivo, non una valutazione indipendente della capacità del sistema su
richieste arbitrarie.
Le esecuzioni intermedie utilizzate durante lo sviluppo non vengono mantenute
nella versione corrente della cartella, poiché non costituiscono risultati
ufficiali del benchmark. Rimangono comunque recuperabili attraverso la
cronologia Git.

## Conservazione del risultato

`results_20260810_201100.json` viene mantenuto invariato.
Eventuali valutazioni successive devono produrre nuovi file e non sovrascrivere
il risultato congelato del 10/08/2026.