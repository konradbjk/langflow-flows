# Custom Langflow Components

This folder contains custom Langflow components built with the `lfx` API.

**Contents**
- `groq_model_provider.py` — Groq model provider component.
- `multi_query_retriever.py` — Multi-query retriever component (uses the custom Qdrant retriever).
- `pinecone_vector_store.py` — Pinecone vector store component.
- `qdrant_vector_store.py` — Qdrant vector store component.
- `qdrant_vector_store_output.py` — Qdrant vector store output component and custom retriever.
- `recursive_text_splitter.py` — Recursive text splitter component.

**Notes**
- `multi_query_retriever.py` depends on the custom Qdrant retriever defined in `qdrant_vector_store_output.py`.
- These components are designed for the `lfx` import paths, not legacy `langflow.*`.

**Usage**
- In Langflow Desktop, manually add this folder as a custom components path.
- In other installs (Python package or Docker), configure the custom components path to point at `custom_nodes/`.
