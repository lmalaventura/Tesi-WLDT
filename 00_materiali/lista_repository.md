# Repository WLDT utilizzate

Documento di riferimento per le repository esterne coinvolte nello sviluppo e
nell'integrazione della tesi.

## Repository principale della tesi

- Repository: `lmalaventura/Tesi-WLDT`
- URL: `https://github.com/lmalaventura/Tesi-WLDT`
- Contenuto: esperimenti, risultati, progettazione, Agent Service,
  documentazione tecnica e materiali per la stesura.

## WHDT Monitor Frontend

Repository ufficiale:

- Repository: `Whitelabel-Human-Digital-Twin/whdt-monitor-frontend`
- URL: `https://github.com/Whitelabel-Human-Digital-Twin/whdt-monitor-frontend`
- Tecnologia principale: Next.js e TypeScript
- Utilizzo nella tesi: integrazione della modalità Natural Language nel Query
  Workbench.

Le modifiche sviluppate per la tesi sono conservate anche nel repository
personale:

- Repository: `lmalaventura/whdt-monitor-frontend`
- Branch: `tesi/Natural-Language-Agent`
- URL:
  `https://github.com/lmalaventura/whdt-monitor-frontend/tree/tesi/Natural-Language-Agent`

## Persistence Service

- Repository: `Whitelabel-Human-Digital-Twin/persistence-service`
- URL: `https://github.com/Whitelabel-Human-Digital-Twin/persistence-service`
- Tecnologia principale: Kotlin e Ktor
- Utilizzo nella tesi:
  - sorgente della specifica OpenAPI;
  - destinazione delle chiamate REST generate;
  - integrazione con i dati persistiti in MongoDB.

Il Persistence Service non è stato modificato per introdurre la logica LLM.

## HDT Creation Service

- Repository: `Whitelabel-Human-Digital-Twin/hdt-creation-service`
- Utilizzo nella tesi: componente dello stack WLDT development utilizzato
  durante i test di integrazione.

La tesi non introduce modifiche funzionali specifiche in questo servizio.

## WHDT Monitor Infrastructure

Repository ufficiale:

- Repository: `Whitelabel-Human-Digital-Twin/whdt-monitor-infra`
- URL: `https://github.com/Whitelabel-Human-Digital-Twin/whdt-monitor-infra`
- Utilizzo nella tesi: avvio dello stack Docker development e integrazione
  dell'Agent Service nella rete dei servizi WLDT.

Le modifiche sviluppate per la tesi sono conservate anche nel repository
personale:

- Repository: `lmalaventura/whdt-monitor-infra`
- Branch: `tesi/Agent-Service-Integration`
- URL:
  `https://github.com/lmalaventura/whdt-monitor-infra/tree/tesi/Agent-Service-Integration`

## Organizzazione locale utilizzata per l'integrazione

Durante i test finali le repository WLDT sono state mantenute come directory
sorelle, mentre la repository della tesi è stata mantenuta separatamente:

```text
Desktop/
├── Tesi-WLDT/
└── WLDT-dev/
    ├── whdt-monitor-frontend/
    ├── persistence-service/
    ├── hdt-creation-service/
    └── whdt-monitor-infra/
```

Il file `docker-compose.dev.yml` dell'infrastruttura utilizza come build
context dell'Agent Service:

```text
../../Tesi-WLDT/05_codice/agent_service
```

Questa organizzazione permette di sviluppare localmente il servizio Python
senza pubblicare preventivamente un'immagine Docker separata.
