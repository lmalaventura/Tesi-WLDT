# Confronto tra gli approcci

Il confronto è riferito ai requisiti della prima integrazione WLDT e non alla
completezza generale dei framework.

| Aspetto | LangChain | smolagents | Pipeline personalizzata |
|---|---|---|---|
| Invocazione di modelli LLM | supportata | supportata | implementata tramite client Ollama |
| Strumenti o chiamate esterne | supportati tramite tools | supportati tramite tools | gestiti esplicitamente dal servizio |
| Output strutturato | supportato | realizzabile nel flusso dell'agente | implementato con JSON Schema di Ollama |
| Ciclo agentico multi-step | disponibile | elemento centrale | non previsto nella prima versione |
| Selezione delle operazioni WLDT | da configurare | da configurare come insieme di tool | componente specifico del progetto |
| Validazione sulla OpenAPI aggiornata | da integrare | da integrare | requisito esplicito dell'architettura |
| Controllo dell'ordine delle fasi | mediato dalle astrazioni adottate | mediato dal ciclo dell'agente | ordine deterministico nel codice |
| Dipendenze di orchestrazione | framework LangChain | libreria smolagents | nessun framework agentico generalista |

## Interpretazione

Tutti e tre gli approcci possono essere adattati al caso d'uso. La scelta non
si basa sull'impossibilità dei framework esistenti di svolgere il compito, né
su un vantaggio prestazionale già dimostrato.

La pipeline personalizzata è più aderente allo scope attuale perché:

- usa una sola invocazione LLM per richiesta;
- limita il modello a un insieme di operazioni candidate;
- mantiene separati generazione, validazione ed esecuzione;
- consente di usare la stessa OpenAPI aggiornata come fonte per catalogo e
  validazione;
- evita di introdurre funzioni agentiche che al momento non sono richieste.

## Limite del confronto

E010 non include un'implementazione equivalente nei tre approcci. Non è quindi
possibile concludere che una soluzione sia più veloce o più accurata delle
altre. Un eventuale confronto empirico richiederebbe la stessa suite di casi,
lo stesso modello e la stessa configurazione per tutte le implementazioni.
