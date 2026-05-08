# Overview

![chuvnk_overview](https://miro.medium.com/v2/resize:fit:720/format:webp/1*OYL7apslvHVec9RVxHGHeA.jpeg)

Chunking is the process of splitting large documents into smaller pieces, or *chunks*, before storing them in a vector database for retrieval by an LLM during question answering or generation tasks.

```
Chunking = breaking large documents into smaller pieces (“chunks”) before adding them to a retrieval store.
```

## Why Chunking is so hard
If chunks are too small, it lose context and retrieval becomes incomplete. If chunks are too large, then embeddings become noisy. If chunks have wrong boundaries then it breaks semantic meaning. So chunks should always be meaningful, complete and focused.

# Key Chunking strategies

## Fixed-size chunking
Split text into uniformly sized chunks based on tokens, words, or characters. Simple and efficient, but may break sentences mid-way, losing important meaning, or mix unrelated points together.​
This is mainly used when data is unstructured and we want a quick baseline.

```bash
from langchain.text_splitter import CharacterTextSplitter

        text_splitter = CharacterTextSplitter(
        separator="\n", # Here we are separating line by line
        chunk_size=500,
        chunk_overlap=0
)

docs = text_splitter.split_documents(raw_documents)
```
*You can separate the document by charatcter, words, lines and prargraph.*

* characters -> "" 
* lines -> "\n"  
* words -> "_"  
* paragraph -> "\n\n"

## Sliding windows/Overlapping chunks
Also called **Fixed-Size Chunking with overlapping**. Slightly overlap each chunk with the previous one to preserve context, especially near chunk boundaries. This helps maintain coherence but increases index size and retrieval redundancy.​
This is minimum standard for production.

```bash
from langchain.text_splitter import CharacterTextSplitter

        text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100
)

docs = text_splitter.split_documents(raw_documents)
```

## Recursive/hierarchical chunking
Break down texts at logical structure points (like headings, paragraphs, or sentences). If large, split further at finer boundaries to respect natural divisions and semantic topics.​
Each chunk includes metadata of its headers, which helps in better retrieval. It does not consider chunk size and does not recursively split large sections. Best used when working with well-structured docs like README files, blogs, or documentation.

```bash
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ]

text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
)

docs = text_splitter.split_text(markdown_text)
```

## Semantic chunking
The key idea here is to try the largest meaningful unit first and only goes smaller if needed. Priority order of splitting is paragraph, line, sentence, and word. So it first split the document as paragraph and check if each chunk is less than chunk size. If yes, then it keeps paragraph-level chunks. If not then it do line split and combine lines until reaching ~ chunk size. If the single line itself is bigger than chunk size then it split by sentence and then by word. Chunk overlap ensures context continuity.

```bash
from langchain.text_splitter import RecursiveCharacterTextSplitter

        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
        )

docs = text_splitter.split_documents(raw_documents)
```

## Layout-aware/structure-preserving chunking
Leverage explicit markup or document structure (like HTML headings, tables, or sections) for more robust chunking in technical or formatted documents.

## Dynamic/context-adaptive chunking
Adapt the chunking approach based on document characteristics or user queries, and optimize chunk size or structure automatically.​

