# Metodologia di valutazione

## Benchmark completi

Gli esperimenti E002, E003, E004, E005, E006 ed E009 utilizzano cinque
richieste e vengono valutati su 50 punti. Per ogni richiesta sono assegnati da
0 a 2 punti a ciascuna delle seguenti voci:

1. metodo HTTP;
2. endpoint;
3. struttura dell'input;
4. fedeltà alla specifica OpenAPI;
5. gestione delle informazioni mancanti.

Il punteggio valuta la risposta prodotta in una singola esecuzione. Non misura
la variabilità tra esecuzioni dello stesso modello.

## Esperimenti diagnostici

E007 ed E008 misurano soltanto la selezione dell'endpoint:

- E007: un caso su un solo endpoint, punteggio 10/10;
- E008: cinque casi su cinque descrizioni sintetiche, accuratezza 5/5.

Questi risultati non sono confrontabili direttamente con i punteggi su 50 dei
benchmark completi.

## Distinzione tra contratto e implementazione

Il prompt dei benchmark imponeva di utilizzare esclusivamente l'OpenAPI. Le
valutazioni storiche devono quindi essere interpretate rispetto al contratto
disponibile al momento dell'esecuzione.

L'analisi successiva del codice Kotlin ha evidenziato che
`POST /query/event/values/history` usa soltanto `hdtId` e `propertyName`,
ignorando `from` e `to`. Per uno storico limitato a un intervallo, il percorso
implementato è `POST /query/event/values/valuesByName`.

Questa incongruenza non rende inutili i benchmark precedenti, ma impedisce di
usare senza correzioni la loro ground truth come specifica dell'integrazione
finale.

## Limiti

- una sola esecuzione per configurazione;
- tempi non raccolti in modo uniforme per tutti i modelli;
- confronto tra un servizio cloud e modelli locali non controllato sul piano
  hardware e della versione esatta del modello;
- benchmark ristretto a cinque richieste;
- punteggi assegnati manualmente sulla base della rubrica sopra descritta.

I risultati devono quindi essere presentati come esplorativi e come supporto
alle decisioni progettuali, non come valutazione generale dei modelli.
