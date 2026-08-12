# Limiti noti del prototipo

Il prototipo viene mantenuto per documentare la progressione del lavoro. Non
deve essere usato direttamente come implementazione finale.

## Scostamenti rispetto all'integrazione prevista

- catalogo delle operazioni statico;
- OpenAPI non caricata dal Persistence Service;
- selezione history non distinta tra storico completo e intervallo;
- semantica dei filtri stats troppo restrittiva;
- validazione dei request body parziale;
- richiesta HTTP soltanto preparata;
- base URL predefinito non allineato alla porta 8081;
- nessuna API FastAPI e nessun collegamento al Query Workbench.

La correzione avverrà durante il porting dei componenti nell'Agent Service.

## Stato successivo

I limiti descritti in questo documento appartengono al prototipo storico.
Il successivo Agent Service, disponibile in:

```text
05_codice/agent_service
```

ha introdotto il caricamento dinamico della OpenAPI, la validazione prevista
dal progetto, l'esecuzione HTTP, l'API FastAPI e l'integrazione con il sistema
WLDT.
Il prototipo non viene modificato retroattivamente perché documenta una fase
intermedia dello sviluppo.
