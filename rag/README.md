# Overview

Large language models are impressive, but they have fundamental limitations: they only know what they learned during training, they can confidently make things up, and they have no access to your proprietary data. Retrieval-Augmented Generation (RAG) solves all three problems.

```text
Retrieval Augmented Generation

Retrieval  → find relevant information from your documents
Augmented  → add that information to the prompt
Generation → LLM generates answer based on that information

```

*RAG is the solution — your model will stop making things up and start answering from your own documents instead.*

## Problems Solved:

- **Hallucinations:** Without external grounding, LLMs can fabricate incorrect or misleading information. RAG anchors the generated text in factual, retrieved data, significantly minimizing inconsistencies and false claims.
- **Knowledge Cutoff:** Because models rely on static training data with strict cut-off dates, they cannot naturally access current events. RAG allows systems to pull up-to-date market data, news, or live metrics on the fly without needing to retrain the model.
- **No Access to Private Data**: Public LLMs do not inherently know an enterprise's private or niche information. Connecting the AI to customized knowledge bases enables it to deliver highly specific answers based on proprietary company documents, legal statutes, or internal APIs.
- **High operational costs:** Continuously fine-tuning an LLM to teach it new information is computationally expensive and complex. RAG offers a cost-effective alternative because engineers only need to update the external database to keep the AI's knowledge current.
- **Information opacity:** Standard models act as black boxes, making it difficult to trace where a specific fact originated. RAG provides transparency by allowing the AI to explicitly cite its retrieved sources, enabling users to independently verify the generated claims.

# How RAG Works: The Complete Pipeline

## Phase 1: Indexing Your Knowledge Base

The process of indexing knowledge base

### Step 1: Gather Documents

Start by collecting the documents you want the system to reference.

### Step 2: Chunk the Documents

LLMs have limited context windows (even with modern models supporting 1M tokens, you can’t dump your entire knowledge base into every prompt). Documents are split into smaller chunks — typically 200–1000 tokens each.

Chunking strategies matter. Common approaches include:

- Fixed-size chunks: Split every N tokens with some overlap
- Semantic chunking: Split at natural boundaries like paragraphs or sections
- Recursive chunking: Try larger chunks first, recursively split if needed

### Step 3: Generate Embeddings

Each chunk is passed through an embedding model — a neural network that converts text into a dense numerical vector (typically 768–1536 dimensions). These vectors capture semantic meaning: chunks about similar topics will have similar vectors, even if they use different words.

Popular embedding models include:

- OpenAI’s text-embedding-3-large
- Cohere’s embed-v3
- Voyage AI’s voyage-large-2
- Open-source options like BGE, E5, and GTE

### Step 4: Store in a Vector Database

The embeddings are stored in a specialized vector database optimized for similarity search. Unlike traditional databases that match exact values, vector databases find the most similar vectors to a query vector.

Common vector databases include:

- Pinecone: Fully managed, scales to billions of vectors
- Weaviate: Open-source with hybrid search capabilities
- Qdrant: Open-source, Rust-based, high performance
- Chroma: Lightweight, developer-friendly, good for prototyping
- pgvector: PostgreSQL extension for teams already using Postgres
- Milvus: Open-source, designed for large-scale production

## Phase 2: Query Time Retrieval



### Step 1: Embed the Query

When a user asks a question, it’s converted to an embedding using the same embedding model used for indexing. This ensures the query vector lives in the same semantic space as the document vectors.

### Step 2: K-Nearest Neighbors Search

The vector database performs a k-nearest neighbors (k-NN) search to find the K document chunks most similar to the query embedding.

Similarity is typically measured using:

- Cosine similarity: Measures the angle between vectors (most common)
- Euclidean distance: Measures straight-line distance
- Dot product: Fast computation, works well for normalized vectors

### Step 3: Construct the Prompt

The retrieved chunks are inserted into the prompt, typically in a format like:

```
Use the following context to answer the user's question.
If the context doesn't contain enough information, say so.
```

```
Context:
[Retrieved Chunk 1]
[Retrieved Chunk 2]
[Retrieved Chunk 3]
...
User Question: [Original Query]
```

### Step 4: Generate the Response

The LLM receives the augmented prompt and generates a response grounded in the retrieved context. Good RAG implementations also ask the model to cite which sources it used, enabling verification and trust.

## Mapping

```text
Step 1: Take your 1000 page document
        → Document Loaders
          (PyPDFLoader, WebBaseLoader, CSVLoader)

Step 2: Split into small chunks
        → Text Splitters
          (RecursiveCharacterTextSplitter)

Step 3: Convert each chunk into a vector
        → Embeddings
          (OllamaEmbeddings, OpenAIEmbeddings)

Step 4: Store all vectors in a database
        → Vector Stores
          (FAISS, Chroma)

Step 5: User asks a question
        → just a string input from user

Step 6: Convert question into a vector
        → same Embeddings model used in Step 3

Step 7: Find chunks with smallest distance
        → Retriever
          (vectorstore.as_retriever())

Step 8: Send those chunks + question to LLM
        → ChatPromptTemplate + ChatOllama
          (components you already know!)

Step 9: LLM generates accurate answer
        → StrOutputParser
          (component you already know!)

```