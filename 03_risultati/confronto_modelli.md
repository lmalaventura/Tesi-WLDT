# Confronto tra gli esperimenti

Il documento riassume le esecuzioni svolte nella fase preliminare. I benchmark
completi e gli esperimenti diagnostici sono separati perché misurano compiti
differenti.

## Benchmark completi NL → chiamata API

| Esperimento | Modello | Contesto | Punteggio |
|---|---|---|---:|
| E002 | ChatGPT | OpenAPI completa | 49/50 |
| E003 | Qwen3 4B | OpenAPI completa | 9/50 |
| E004 | Qwen3 8B | OpenAPI completa | 10/50 |
| E005 | Llama 3.1 8B | OpenAPI completa | 15/50 |
| E006 | Qwen3 8B | OpenAPI minimale con schemi | 14/50 |
| E009 | Qwen3 14B | OpenAPI completa | 9/50 |

## Esperimenti diagnostici sulla selezione dell'endpoint

| Esperimento | Modello | Contesto | Risultato |
|---|---|---|---:|
| E007 | Qwen3 8B | un solo endpoint | 10/10 |
| E008 | Qwen3 8B | cinque descrizioni sintetiche | 5/5 |

## Osservazioni

Nei benchmark completi i modelli locali hanno spesso riconosciuto concetti e
nomi di schemi senza collegarli ai path reali. La riduzione dell'OpenAPI ai
cinque endpoint rilevanti, mantenendo gli schemi, non ha risolto il problema.
Nelle due esecuzioni diagnostiche, la presentazione isolata o sintetica dei
path ha invece consentito a Qwen3 8B di scegliere gli endpoint attesi. Questo
risultato ha motivato l'introduzione di una fase preliminare di selezione delle
operazioni candidate. Poiché E007 ed E008 non valutano la costruzione completa
dei parametri e non sono stati ripetuti, il risultato non deve essere descritto
come prova definitiva di superiorità.
Qwen3 14B ha completato il benchmark in circa 12 minuti, usando circa 14 GB di
RAM e con utilizzo della GPU osservato come molto basso. Non ha migliorato il
punteggio ottenuto con l'OpenAPI completa, per cui non è stato scelto per il
prototipo sull'hardware disponibile.

## Nota sull'interpretazione

I punteggi sono riferiti al benchmark OpenAPI-only originario. La successiva
analisi dell'implementazione del Persistence Service ha rilevato una differenza
semantica sull'endpoint storico con intervallo temporale. Per i dettagli e i
limiti del confronto si rimanda a `metodologia_valutazione.md`.
