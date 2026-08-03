# Tecnologie e componenti

## Componenti WLDT esistenti

- frontend: Next.js e React;
- Persistence Service: Kotlin con Ktor;
- persistenza: MongoDB;
- contratto: OpenAPI v0.2.0;
- ambiente locale completo: Docker, repository da acquisire.

Questi componenti costituiscono l'ambiente a cui l'Agent Service deve
adattarsi.

## Agent Service

### Python

Python è stato scelto per realizzare un servizio separato dal frontend
TypeScript e dal backend Kotlin. La prima pipeline è già stata prototipata in
questo linguaggio e usa soltanto interfacce HTTP verso Ollama e il Persistence
Service.

### Framework HTTP previsto

FastAPI è previsto per esporre `GET /health` e `POST /query`. La scelta verrà
registrata definitivamente dopo la creazione e il test dello scheletro del
servizio.

### Librerie previste

- Pydantic per i modelli di richiesta, risposta e configurazione;
- HTTPX per le comunicazioni HTTP;
- PyYAML o parser equivalente per leggere la specifica OpenAPI;
- pytest per i test del nuovo servizio.

L'elenco definitivo dipenderà dall'implementazione; le dipendenze non ancora
utilizzate non devono essere aggiunte preventivamente.

## Runtime LLM

Ollama espone il modello locale tramite API HTTP e supporta l'output vincolato
da JSON Schema. Il prototipo utilizza Qwen3 8B con temperatura zero e thinking
disabilitato nella chiamata applicativa.

Qwen3 4B, Qwen3 14B e Llama 3.1 8B sono stati usati nella fase sperimentale ma
non sono componenti obbligatori dell'architettura finale.

## Orchestrazione

La prima versione usa una pipeline personalizzata. LangChain e smolagents sono
stati analizzati come alternative, ma non sono dipendenze del progetto nello
stato corrente. La motivazione è riportata in
`02_esperimenti/framework/E010_framework_agentici/decisione.md`.

## Specifica OpenAPI

La specifica non viene trattata come file statico del solo Agent Service. La
versione aggiornata deve essere recuperata dal Persistence Service tramite
`GET /openapi.yaml` e usata per catalogo, prompt e validazione.
