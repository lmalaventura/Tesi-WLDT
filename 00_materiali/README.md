# Materiali di riferimento

Questa cartella contiene specifiche e documenti utilizzati durante le diverse
fasi sperimentali della tesi.

## `openapi.yaml`

Il file:

```text
00_materiali/openapi.yaml
```

rappresenta lo snapshot della specifica OpenAPI utilizzato negli esperimenti
iniziali e nel benchmark controllato della pipeline eseguito il 10/08/2026.
Lo snapshot contiene:

```text
OpenAPI 3.1.1
info.version: v0.2.0
25 path
36 operazioni HTTP
```

Il file viene mantenuto invariato per preservare la riproducibilità degli
esperimenti già eseguiti.
Durante la successiva integrazione con il Persistence Service reale, l'Agent
Service ha invece recuperato dinamicamente la specifica esposta dal servizio
in esecuzione. Nel test dell'11–12/08/2026 tale specifica conteneva 26 path e
37 operazioni.
La differenza non viene corretta retroattivamente nello snapshot sperimentale:
gli esperimenti storici restano associati alla specifica con cui sono stati
effettivamente eseguiti.

## `openapi_minimal.yaml`

Il file:

```text
00_materiali/openapi_minimal.yaml
```

è una versione ridotta preparata esclusivamente per gli esperimenti dedicati
all'effetto della dimensione e della rappresentazione del contesto OpenAPI.
Non rappresenta il contratto completo del Persistence Service.

## Utilizzo corrente dell'OpenAPI

L'Agent Service definitivo non utilizza questi file come sorgente operativa.
Durante l'esecuzione recupera la specifica OpenAPI corrente tramite la variabile:

```text
OPENAPI_SPEC_URL
```

In questo modo la generazione e la validazione vengono riferite al contratto
effettivamente esposto dal Persistence Service in esecuzione.