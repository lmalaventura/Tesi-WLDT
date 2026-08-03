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
