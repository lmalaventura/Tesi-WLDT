# Selezione delle API candidate

## Obiettivo

Ridurre il numero di operazioni fornite al modello LLM, selezionando
preventivamente quelle maggiormente coerenti con la richiesta espressa
dall'utente.

La selezione non determina ancora la chiamata definitiva. Produce una lista
ordinata di candidati che verrà successivamente inserita nel prompt del
modello.

## Origine delle operazioni

Le operazioni non vengono definite manualmente nell'Agent Service.

Il componente utilizza il catalogo costruito a partire dalla specifica OpenAPI
esposta dal Persistence Service. Per ogni operazione vengono considerate le
seguenti informazioni:

- metodo HTTP;
- path;
- operationId;
- summary;
- description;
- tag;
- parametri obbligatori;
- presenza del request body.

Questo permette alla selezione di adattarsi agli aggiornamenti della
specifica senza mantenere un elenco statico degli endpoint.

## Normalizzazione della richiesta

La richiesta dell'utente viene:

1. convertita in minuscolo;
2. normalizzata rispetto agli accenti;
3. suddivisa in termini;
4. privata delle parole poco informative;
5. ampliata tramite un piccolo lessico specifico del dominio.

Il lessico collega alcuni termini italiani alle parole tecniche utilizzate
nell'OpenAPI. Per esempio, “corrente” viene associato a “snapshot”, mentre
“statistiche” viene associato a “stats” e “statistics”.

## Calcolo del punteggio

Ogni operazione riceve un punteggio in base alla corrispondenza tra i termini
della richiesta e i metadati OpenAPI.

Path e operationId hanno un peso maggiore rispetto alla descrizione, perché
rappresentano segnali generalmente più specifici.

Sono inoltre previsti alcuni incrementi di punteggio per intenzioni
riconoscibili, come:

- elenco dei Digital Twin;
- recupero dello snapshot corrente;
- confronto tra proprietà;
- statistiche;
- interrogazioni storiche;
- interrogazioni limitate a un intervallo temporale.

## Output

Il componente restituisce un numero limitato di candidati. Per ogni candidato
vengono mantenuti:

- operazione OpenAPI;
- punteggio;
- termini che hanno contribuito alla selezione.

Queste informazioni permettono di verificare il comportamento del selettore e
di costruire un prompt più ristretto per il modello LLM.

## Limiti

La selezione corrente è lessicale e deterministica.

Non utilizza embedding o un secondo modello semantico. La qualità dipende
quindi anche dalla presenza di operationId, summary e descrizioni informative
nella specifica OpenAPI.

La selezione non sostituisce il modello LLM: riduce soltanto lo spazio delle
possibili operazioni e rende il passaggio successivo più controllabile.