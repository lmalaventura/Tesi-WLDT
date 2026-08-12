# Validazione e affidabilità — bozza

## Limiti dell'output strutturato

La generazione strutturata permette di imporre una forma generale alla risposta del modello linguistico. Nell'implementazione sviluppata, Qwen3 8B produce un oggetto compatibile con `GeneratedApiCall`, contenente metodo HTTP, endpoint, parametri, eventuale request body e informazioni mancanti. Questa rappresentazione elimina la necessità di estrarre manualmente una chiamata REST da una risposta discorsiva e permette a Pydantic di verificare la struttura generale dell'oggetto ricevuto. Non è tuttavia sufficiente a stabilire che la chiamata possa essere eseguita correttamente.
Il problema è particolarmente evidente nel campo relativo al request body. La struttura generale deve essere sufficientemente flessibile da rappresentare body differenti, poiché le operazioni del Persistence Service non condividono tutte lo stesso schema. Di conseguenza, la validità del modello `GeneratedApiCall` non implica automaticamente che il contenuto del body rispetti lo schema previsto dall'endpoint selezionato.
Durante i test è stato ad esempio osservato un caso nel quale il modello aveva individuato l'operazione relativa a una richiesta storica, ma aveva costruito gli argomenti utilizzando una struttura non conforme a quella richiesta. L'output risultava quindi leggibile dal programma, ma non direttamente eseguibile come chiamata valida. Questa distinzione ha portato a separare esplicitamente due livelli di controllo: la validità strutturale generale dell'output del modello e la conformità della chiamata rispetto alla specifica OpenAPI.

## Validazione rispetto alla specifica OpenAPI

Prima di eseguire una chiamata REST, l'Agent Service utilizza un validatore deterministico basato sulla specifica OpenAPI corrente.
Il primo controllo riguarda la combinazione tra metodo HTTP ed endpoint proposta dal modello. Nell'implementazione corrente l'operazione deve corrispondere a una delle candidate incluse nel prompt. Una volta individuata l'operazione, viene recuperata la relativa definizione OpenAPI e vengono verificati i parametri previsti dal contratto. La validazione controlla la presenza dei path parameter e dei query parameter obbligatori e impedisce l'utilizzo di parametri non definiti per l'operazione selezionata. Quando è previsto un request body, il contenuto viene confrontato con lo schema associato. Il controllo prende in considerazione strutture a oggetti e array, tipi primitivi, proprietà obbligatorie, valori enumerati e formati temporali.
Per interpretare correttamente gli schemi, il validatore risolve inoltre i riferimenti locali `$ref` verso le definizioni presenti nella sezione `components` della specifica.
A questi controlli strutturali si aggiungono alcune verifiche semantiche specifiche per operazioni nelle quali la sola correttezza dello schema non è sufficiente a distinguere argomenti concettualmente differenti. Un esempio riguarda le varianti che interrogano una proprietà per nome o per identificatore, per le quali vengono controllati rispettivamente `propertyName` e `propertyId`. La validazione costituisce quindi un livello deterministico posto tra l'output probabilistico del modello e l'esecuzione della richiesta.

## Gestione delle informazioni mancanti e degli errori

La pipeline distingue il caso in cui la richiesta dell'utente non contenga informazioni sufficienti dal caso in cui il modello produca una chiamata incompatibile con il contratto API.
Il formato di output prevede il campo `missingInformation`, attraverso il quale il modello può indicare gli elementi che non possono essere determinati dalla richiesta ricevuta. Quando tale insieme non è vuoto, l'Agent Service interrompe l'elaborazione prima della validazione e restituisce una risposta HTTP 422 contenente le informazioni necessarie per completare la richiesta.
Se invece viene prodotta una chiamata completa ma il validatore rileva una violazione della specifica OpenAPI, l'esecuzione viene bloccata e l'Agent Service restituisce una risposta HTTP 502 insieme a una descrizione strutturata dei problemi individuati.
La scelta progettuale è di non correggere automaticamente e silenziosamente una chiamata non valida. Una modifica automatica potrebbe infatti alterare l'intenzione interpretata dal modello e rendere meno osservabili gli errori durante la valutazione del sistema. Il fallimento viene quindi reso esplicito e la richiesta non raggiunge il Persistence Service.

## Preparazione ed esecuzione della richiesta

Solo dopo il superamento della validazione la chiamata viene affidata ad `ApiRequestPreparer`.
Il componente sostituisce i placeholder presenti nel percorso con i relativi valori, applica la codifica necessaria, combina l'endpoint con il base URL configurato e prepara i query parameter e l'eventuale request body. Il risultato è una rappresentazione completa della richiesta HTTP da eseguire. La richiesta viene quindi inviata dal `RestClient` al Persistence Service. La risposta del servizio viene infine restituita dal percorso `/query` insieme alle informazioni relative alla chiamata generata, alla validazione e alla richiesta effettivamente eseguita.
Questa separazione consente di mantenere distinti i principali livelli della pipeline:

1. interpretazione della richiesta tramite LLM;
2. validazione deterministica rispetto al contratto OpenAPI;
3. preparazione della richiesta;
4. esecuzione sul Persistence Service.