# Note E008 — Qwen3 8B con descrizione sintetica dei path

## Esecuzione

- Thinking visualizzato: sì.
- Velocità percepita: superiore rispetto all'esecuzione con OpenAPI completa.
- Problemi tecnici: il file ottenuto dal terminale contiene sequenze di
  controllo dovute alla visualizzazione progressiva dell'output.

`output_raw.txt` conserva il contenuto originale. `risposta.md` contiene una
copia leggibile, ripulita dalle sequenze di controllo senza modificare il
contenuto semantico.

## Variabile modificata

È stato fornito un frammento costruito per il test, contenente i cinque path e
una breve descrizione delle operazioni. `components` e `schemas` sono stati
rimossi.
L'esperimento verifica soltanto la selezione dell'endpoint e non la costruzione
completa di metodo, parametri e body.
