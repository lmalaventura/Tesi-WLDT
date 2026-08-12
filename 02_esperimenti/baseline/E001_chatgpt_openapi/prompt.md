# E001 — Comprensione OpenAPI tramite LLM

## Modello
ChatGPT

## Input
File: openapi.yaml

## Prompt

Analizza il file OpenAPI allegato.
Il tuo compito è comprendere quali operazioni possono essere eseguite attraverso questa API.
Non inventare endpoint, parametri o strutture non presenti nel file.

1. Identifica gli endpoint che permettono di interrogare i dati dei Digital Twin.
2. Spiega brevemente lo scopo di ciascuno.
3. Individua gli endpoint che potrebbero essere utilizzati per:
   - recuperare un valore di una proprietà;
   - recuperare lo storico di una proprietà;
   - effettuare confronti su valori;
   - ottenere statistiche.
4. Per ciascun caso indica metodo HTTP, endpoint e struttura dell'input richiesta.

Quando un'informazione non è determinabile dal file OpenAPI, dichiaralo esplicitamente.