# Note E006 — Qwen3 8B con OpenAPI minimale

## Esecuzione

- Thinking visualizzato: sì.
- Velocità percepita: simile a E004.
- Problemi tecnici: il file ottenuto dal terminale contiene sequenze di
  controllo dovute alla visualizzazione progressiva dell'output.

`output_raw.txt` conserva il contenuto originale. `risposta.md` contiene una
copia leggibile, ripulita dalle sequenze di controllo senza modificare il
contenuto semantico.

## Variabile modificata

Rispetto a E004 sono rimasti invariati modello, prompt, benchmark e modalità
di esecuzione. L'OpenAPI completa è stata sostituita con una versione che
mantiene i cinque endpoint rilevanti e gli schemi da essi referenziati.
