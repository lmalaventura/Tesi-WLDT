# Note E009 — Qwen3 14B

## Ambiente

- Modello: Qwen3 14B.
- Runtime: Ollama.
- RAM di sistema: 16 GB.
- GPU: NVIDIA GeForce GTX 1660 SUPER.
- VRAM dedicata: 6 GB.

## Esecuzione

- Thinking visualizzato: sì.
- Tempo totale del benchmark: circa 12 minuti.
- Velocità percepita: molto lenta.
- RAM osservata: circa 14 GB.
- Utilizzo GPU osservato: molto basso.
- Utilizzo CPU: non misurato sistematicamente.
- Usabilità del computer: fortemente ridotta, senza blocco completo del
  sistema.

Una prova preliminare con il solo messaggio «Ciao» è stata completata in circa
43 secondi, includendo thinking e risposta finale. La prova serve soltanto a
verificare che il modello sia eseguibile e non è confrontabile con il
benchmark completo.

## Output conservato

`output_raw.txt` conserva il file ottenuto dal terminale, comprese sequenze di
controllo e caratteri danneggiati dalla codifica. `risposta.md` contiene la
versione leggibile, ottenuta rimuovendo le sequenze e correggendo soltanto i
caratteri di codifica.

## Osservazione

Il modello è eseguibile sull'hardware disponibile, ma il benchmark completo ha
richiesto tempi non adatti a un'interazione normale. L'aumento di dimensione
rispetto a Qwen3 8B non ha migliorato il punteggio sul benchmark con OpenAPI
completa.
