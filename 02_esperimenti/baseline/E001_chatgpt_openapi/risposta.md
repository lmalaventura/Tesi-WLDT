# Risposta E001

Data: 28/07/2026
Modello: ChatGPT

## Versione del contratto

- OpenAPI: v0.2.0
- File: 00_materiali/openapi.yaml

## Output

Ho analizzato direttamente openapi.yaml. Il file descrive una persistence API per Human Digital Twin, con endpoint sia per struttura/configurazione dei Twin sia per interrogare proprietà e osservazioni.

La parte più interessante per interrogazioni sui dati è concentrata in /hdts/{id}/snapshot e soprattutto in /query/....

1. Endpoint che permettono di interrogare i dati dei Digital Twin
Lettura diretta di un HDT
Metodo	Endpoint	Scopo
GET	/hdts	Restituisce tutti gli Human Digital Twin.
GET	/hdts/{id}	Restituisce uno specifico HDT tramite ID.
GET	/hdts/{id}/models	Restituisce tutti i modelli associati a un HDT.
GET	/hdts/{id}/properties	Restituisce le specifiche delle proprietà dell'HDT; opzionalmente filtrabili per modelId.
GET	/hdts/{id}/observations	Restituisce tutte le osservazioni dello specifico HDT.
GET	/hdts/{id}/spec	Ricostruisce la specifica completa dell'HDT combinando HDT, modelli e proprietà.
GET	/hdts/{id}/snapshot	Restituisce il valore corrente di ogni proprietà: ultima osservazione disponibile oppure initialValue.
GET	/hdts/{id}/snapshot/by-task	Restituisce l'ultima osservazione per coppia (property, task).

Il comportamento di observations, spec e snapshot è esplicitamente descritto nel file OpenAPI alle righe 139–231.

Esistono inoltre:

GET /properties/names: restituisce i nomi distinti delle proprietà presenti nel sistema.
POST /query/property: ricerca le specifiche delle proprietà attraverso predicati sui tag.
POST /views/{name}/execute: esegue una View precedentemente salvata contro uno o più HDT.
Endpoint specificamente dedicati alle query sui valori

Questi sono probabilmente i più rilevanti:

Metodo	Endpoint	Scopo dichiarato
POST	/query/event/values/valuesById	Query Observations by Id
POST	/query/event/values/valuesByName	Query Observations by Name
POST	/query/event/values/history	Query Observation history for a certain HDT
POST	/query/event/stats	Query Aggregate Stats
POST	/query/event/comparison	Query Observations by comparisons
POST	/query/cohort	Query per confronti con valori/statistiche per DT e statistiche di popolazione

Sono definiti alle righe 504–591 e 712–743 del file.

2. Recuperare un valore di una proprietà
Soluzione esplicitamente prevista per il valore corrente
GET /hdts/{id}/snapshot

È l'endpoint più chiaro per questo scopo.

Il file dice esplicitamente:

Returns current value per property — latest observation or initialValue fallback

Quindi restituisce per ogni proprietà:

propertyId
propertyName
value
timestamp
source

dove source può essere:

observation
initial_value
Input
GET /hdts/{id}/snapshot

Parametro:

id: string

obbligatorio nel path.

Non c'è body.

Importante: non esiste in questo endpoint un parametro propertyId o propertyName.

Quindi, se l'obiettivo è:

«Dammi il valore corrente della proprietà temperatura dell'HDT X»

l'API permette sicuramente di ottenere lo snapshot dell'HDT, ma la selezione della singola proprietà deve essere fatta sul risultato restituito.

(openapi(1).yaml, righe 208–231 e 1441–1464)

Variante per task
GET /hdts/{id}/snapshot/by-task

Restituisce l'ultima osservazione per ogni combinazione proprietà/task.

Input:

id: string

nel path.

(openapi(1).yaml, righe 183–207)

POST /query/event/values/valuesById

È un'altra possibilità per interrogare valori, ma il file la descrive soltanto come:

Query Observations by Id

Input: array di PropertyValuesRequest.

La struttura ammessa è:

[
  {
    "hdtId": "<string>",
    "modelId": "<string>",
    "propertyId": "<string>",
    "propertyName": "<string>",
    "from": "<date-time oppure null>",
    "to": "<date-time oppure null>"
  }
]

(openapi(1).yaml, righe 504–526 e 1490–1511)

C'è un dettaglio importante: nello schema PropertyValuesRequest non compare alcun required.

Quindi OpenAPI non dichiara formalmente obbligatorio nessuno tra:

hdtId
modelId
propertyId
propertyName
from
to

La richiesta HTTP, invece, deve avere un body e viene documentata una risposta 400 nel caso di richiesta vuota.

[Non verificato] Dal solo OpenAPI non è possibile stabilire se valuesById restituisca esclusivamente l'ultimo valore oppure tutte le osservazioni compatibili con la richiesta. La risposta è semplicemente un array di PropertyObservationDocument.

POST /query/event/values/valuesByName

Stessa struttura:

[
  {
    "hdtId": "<string>",
    "modelId": "<string>",
    "propertyId": "<string>",
    "propertyName": "<string>",
    "from": "<date-time oppure null>",
    "to": "<date-time oppure null>"
  }
]

Endpoint:

POST /query/event/values/valuesByName

(openapi(1).yaml, righe 527–549)

[Non verificato] Il nome valuesByName suggerisce naturalmente un'interrogazione tramite propertyName, mentre valuesById suggerisce l'utilizzo degli ID. Tuttavia lo schema OpenAPI non stabilisce quali campi debbano essere presenti nei due casi, perché entrambi usano esattamente PropertyValuesRequest e nessuno dei suoi campi è marcato come obbligatorio.

3. Recuperare lo storico di una proprietà

L'endpoint esplicitamente dedicato è:

POST /query/event/values/history

Summary OpenAPI:

Query Observation history for a certain HDT

Input

Body obbligatorio, costituito da un array di:

[
  {
    "hdtId": "<string>",
    "modelId": "<string>",
    "propertyId": "<string>",
    "propertyName": "<string>",
    "from": "<date-time oppure null>",
    "to": "<date-time oppure null>"
  }
]

from e to sono timestamp date-time.

(openapi(1).yaml, righe 550–572 e 1490–1511)

Output:

PropertyObservationDocument[]

Ogni osservazione contiene:

metaField
timeField
value
metadata

e metaField identifica:

hdtId
modelId
modelName
propertyName
propertyId

Quindi questo è chiaramente l'endpoint specifico per interrogazioni storiche.

Alternativa più grezza

Esiste anche:

GET /hdts/{id}/observations

Input:

id: string

nel path.

Restituisce tutte le osservazioni dell'HDT.

Non sono previsti parametri per:

proprietà;
modello;
from;
to.

Quindi è meno selettivo di /query/event/values/history.

4. Effettuare confronti su valori

L'endpoint specifico è:

POST /query/event/comparison

Summary:

Query Observations by comparisons

Struttura dell'input

Il body utilizza:

PropertiesByComparisonsRequestDto

con questa struttura:

{
  "comparisons": [
    {
      "propertyName": "<string>",
      "comparison": "<operatore>",
      "value": "<number | string | boolean>"
    }
  ],
  "modelNames": [
    "<string>"
  ],
  "from": "<date-time>",
  "to": "<date-time>",
  "metadataFilters": {
    "<chiave>": [
      "<string>"
    ]
  }
}

Solo:

comparisons

è obbligatorio nello schema.

Ogni confronto richiede invece obbligatoriamente:

propertyName
comparison
value
Operatori disponibili

Il file definisce esclusivamente:

GT
GTE
LT
LTE
EQ

cioè:

GT  → maggiore di
GTE → maggiore o uguale
LT  → minore di
LTE → minore o uguale
EQ  → uguale

Non sono definiti operatori come:

NEQ
LIKE
BETWEEN
CONTAINS

quindi non vanno presupposti.

(openapi(1).yaml, righe 712–727 e 834–879)

Un esempio strutturale, senza assumere valori reali dell'API, sarebbe quindi:

{
  "comparisons": [
    {
      "propertyName": "<nome proprietà>",
      "comparison": "GT",
      "value": 0
    }
  ]
}

Il value può essere esclusivamente:

number
string
boolean

secondo questo DTO.

Output

La risposta è un:

ComparisonSearchResult

contenente:

matches
populationStats

I match sono organizzati per hdtId e contengono:

matchedProperties
matchedEvents

Quindi l'endpoint può essere utilizzato, ad esempio, per trovare gli HDT che hanno osservazioni che soddisfano determinati confronti.

5. Ottenere statistiche

L'endpoint direttamente dedicato è:

POST /query/event/stats

Summary:

Query Aggregate Stats

Input
{
  "hdtIds": [
    "<string>"
  ],
  "modelIds": [
    "<string>"
  ],
  "modelNames": [
    "<string>"
  ],
  "propertyName": "<string>",
  "from": "<date-time oppure null>",
  "to": "<date-time oppure null>"
}

Qui il file è molto più preciso.

Sono obbligatori:

hdtIds
modelIds
modelNames
propertyName

Sono opzionali:

from
to

(openapi(1).yaml, righe 573–591 e 1512–1544)

Nota: anche gli array hdtIds, modelIds e modelNames sono obbligatori secondo OpenAPI. Il file non specifica però se sia ammesso utilizzarli come array vuoti per indicare «nessun filtro».

Statistiche restituite

Per ogni HDT:

hdtId
count
avg
min
max

hdtId e count sono obbligatori nella risposta; avg, min e max possono essere null.

(openapi(1).yaml, righe 1545–1567)

6. /query/cohort: confronti + statistiche più avanzate

Esiste anche:

POST /query/cohort

che il file descrive come:

Query cohort frame (per-DT values + stats + population summary) by comparisons

Utilizza lo stesso input di /query/event/comparison:

{
  "comparisons": [
    {
      "propertyName": "<string>",
      "comparison": "GT | GTE | LT | LTE | EQ",
      "value": "<number | string | boolean>"
    }
  ],
  "modelNames": [
    "<string>"
  ],
  "from": "<date-time>",
  "to": "<date-time>",
  "metadataFilters": {
    "<key>": [
      "<string>"
    ]
  }
}

La risposta contiene:

rows
populationStats

e le statistiche disponibili nelle strutture di cohort/population comprendono anche:

count
avg
min
max
median
p25
p75

Quindi è più ricco di /query/event/stats, ma ha uno scopo differente: costruisce una coorte filtrata tramite confronti e ne restituisce valori/statistiche.

Riassunto operativo

Per i quattro casi che ti interessano, la mappa più corretta è:

Operazione desiderata	Metodo	Endpoint	Input principale
Valore corrente proprietà	GET	/hdts/{id}/snapshot	id nel path
Valore per proprietà/task	GET	/hdts/{id}/snapshot/by-task	id nel path
Interrogare osservazioni per ID	POST	/query/event/values/valuesById	array PropertyValuesRequest
Interrogare osservazioni per nome	POST	/query/event/values/valuesByName	array PropertyValuesRequest
Storico proprietà	POST	/query/event/values/history	array PropertyValuesRequest
Tutte le osservazioni di un HDT	GET	/hdts/{id}/observations	id nel path
Confronto sui valori	POST	/query/event/comparison	comparisons[] + filtri opzionali
Statistiche aggregate	POST	/query/event/stats	hdtIds, modelIds, modelNames, propertyName, eventuale intervallo
Confronti + statistiche/coorte	POST	/query/cohort	stesso body di /query/event/comparison
Limiti che emergono dal solo OpenAPI

Ci sono alcune cose che non possono essere determinate con certezza dal file:

[Non verificato] Non è specificato quali campi di PropertyValuesRequest siano obbligatori per valuesById, valuesByName e history: lo schema non contiene un blocco required.
[Non verificato] Non è specificato se valuesById e valuesByName restituiscano l'ultimo valore, tutti i valori compatibili o applichino qualche altra logica di selezione. Il file dice solamente Query Observations by Id/Name.
Non è definito un endpoint del tipo:
GET /hdts/{id}/properties/{propertyId}/value

per ottenere direttamente e soltanto il valore corrente di una singola proprietà.

Non è specificato l'ordinamento delle osservazioni storiche, per esempio crescente o decrescente per timestamp.
Non sono presenti nel file parametri di paginazione (limit, offset, page, ecc.) per le query esaminate.
Non è documentata nel file la semantica degli array vuoti in PropertyStatsRequest, quindi non è possibile stabilire dal solo OpenAPI se hdtIds: [], modelIds: [] o modelNames: [] significhino «tutti».

In sostanza, l'API espone già quasi esattamente i quattro mattoni necessari per query in linguaggio naturale sui Digital Twin: snapshot → valore corrente, history → serie storica, comparison → filtri logici sui valori, stats/cohort → aggregazioni statistiche.