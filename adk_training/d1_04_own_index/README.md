# D1.4: Własny indeks – bucket → datastore → app → agent

Ten sam agent RAG co w [d1_03_rag_vertex_search](../d1_03_rag_vertex_search/), ale podpięty
pod **Twój** indeks. Kod się nie zmienia, zmienia się tylko `.env`, a w `adk web` masz
oba agenty obok siebie: indeks prowadzącego (d1_03) i własny (d1_04).

## Część 1 (przed Blokiem 4, ok. 15 min)

1. **Cloud Storage** → utwórz bucket (region dowolny) i wgraj kilka własnych plików PDF/MD.
   Gdy pojawi się „Unable to create your bucket”, spróbuj ponownie.
2. **AI Applications** → *Data Stores* → *Create* → źródło: Cloud Storage → wskaż bucket.
   Lokalizacja: **global**.
3. **AI Applications** → *Apps* → *Create* → typ *Search* → podłącz datastore z kroku 2.
4. **Start importu.** Indeksowanie trwa kilka–kilkanaście minut, w tym czasie robimy D1.5.

## Część 2 (po D1.5, ok. 15 min)

```powershell
cd adk_training\d1_04_own_index
copy .env.template .env      # wpisz GOOGLE_CLOUD_PROJECT i ID SWOJEGO engine
cd ..
adk web --reload_agents
```

`SEARCH_ENGINE_ID` ma format:
`projects/<PROJEKT>/locations/global/collections/default_collection/engines/<ENGINE_ID>`

Zadaj to samo pytanie agentowi `d1_03_rag_vertex_search` i `d1_04_own_index`, a potem porównaj odpowiedzi i źródła w zakładce Events.

## Pułapki

- Brak wyników zwykle oznacza, że indeks jeszcze się buduje (sprawdź status importu w konsoli).
- `404 DataStore not found`: ID spoza `locations/global` albo literówka.

**Wniosek:** pipeline wiedzy (źródło → indeks → agent) aktualizujesz bez zmiany kodu.
