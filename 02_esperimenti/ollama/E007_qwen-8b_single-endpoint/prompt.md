# E007 — Riconoscimento di un singolo endpoint

## Modello

Qwen3 8B

## Input

- frammento OpenAPI contenente un solo endpoint;
- una richiesta in linguaggio naturale.

## Prompt

Utilizza esclusivamente il frammento OpenAPI riportato sopra.

Determina quale chiamata API deve essere eseguita per soddisfare la
richiesta seguente.

Non inventare endpoint o parametri.

Restituisci esclusivamente:

1. metodo HTTP;
2. endpoint;
3. parametri necessari;
4. breve motivazione.

Richiesta:

Mostrami tutti i Digital Twin disponibili.