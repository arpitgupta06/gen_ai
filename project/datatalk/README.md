# DataTalk: AI-Powered Text-to-SQL Agent with Data Pipeline Intelligence

A LangGraph-powered agent that lets anyone ask questions in plain English over your data warehouse. It understands your schema, knows your dbt models, ingests streaming data from Kafka, and translates natural language into accurate SQL, then explains the results back.

| Tools | Description |
| --- | --- |
| SQL | Agent generates, validates, and executes SQL |
| Postgres | Primary data warehouse in local dev |
| dbt | Models sit on top of raw data; agent understands lineage |
| Kafka | Streams raw events into Postgres in real time |
| Snowflake | Swap in later as the production warehouse |
| Python | Entire agent codebase |
| LangGraph | Agent orchestration, the brain |
| LangChain RAG | Schema + dbt docs indexed as vector store |
| AWS Bedrock | LLM backend (Phase 2) |

## Tech Stack (Local First)

```text
User Question (Streamlit UI)
        |
        v
  LangGraph Agent
  |-- Schema RAG Tool      -> FAISS vector store (schema + dbt docs)
  |-- SQL Generator Tool   -> LLM generates SQL
  |-- SQL Executor Tool    -> Runs on Postgres
  |-- Result Explainer     -> LLM explains output in plain English
  `-- dbt Lineage Tool     -> Traces where data comes from
        |
        v
   Postgres (data warehouse)
        ^
        |
   Kafka -> Consumer -> Postgres (streaming ingestion)
        ^
        |
   dbt models (transforms raw -> clean tables)
```

## Project Structure

```text
datatalk/
|-- docker-compose.yml          # Postgres + Kafka locally
|-- .env                        # API keys
|
|-- data/                       # Sample dataset (e-commerce orders)
|   `-- seed_data.sql
|
|-- dbt_project/                # dbt models
|   |-- models/
|   |   |-- staging/            # Raw -> clean
|   |   `-- marts/              # Business logic (revenue, churn)
|   `-- dbt_project.yml
|
|-- kafka/
|   |-- producer.py             # Simulates real-time order events
|   `-- consumer.py             # Writes Kafka events -> Postgres
|
|-- rag/
|   |-- schema_indexer.py       # Reads Postgres schema -> FAISS
|   |-- dbt_doc_indexer.py      # Reads dbt docs -> FAISS
|   `-- retriever.py            # Retrieves relevant schema context
|
|-- agent/
|   |-- state.py                # TypedDict state definition
|   |-- tools.py                # SQL executor, schema lookup, dbt lineage
|   |-- nodes.py                # Agent nodes (understand -> retrieve -> generate -> execute -> explain)
|   `-- graph.py                # LangGraph graph assembly
|
`-- ui/
    `-- app.py                  # Streamlit frontend with streaming
```

## Build Phases (Daily Work Plan)

### Phase 1 — Foundation (Days 1–3)

- **Day 1:** Docker setup, Postgres running, seed e-commerce dataset loaded
- **Day 2:** dbt models — staging + marts (revenue, orders, customers)

- **Day 3:** Kafka producer (simulates order events) + consumer (writes to Postgres)

### Phase 2 — RAG Layer (Days 4–5)

- **Day 4:** Schema indexer — reads Postgres tables/columns into FAISS
- **Day 5:** dbt doc indexer — parses dbt model docs into FAISS

### Phase 3 — Agent (Days 6–8)

- **Day 6:** Core LangGraph agent — nodes for schema retrieval + SQL generation + execution
- **Day 7:** Add result explainer node + error recovery (bad SQL retry loop)
- **Day 8:** Add HITL node for dangerous queries (DELETE, UPDATE) + Streamlit UI

### Phase 4 — Production Hardening (Days 9–10)

- **Day 9:** Snowflake integration (swap Postgres connector)
- **Day 10:** AWS Bedrock as LLM backend + README + demo recording