# AGENTS.md

This file captures practical guidance for building Langflow custom components in this repo, based on what works in the current environment and the edge cases we hit during troubleshooting.

## Purpose
Use this guide when creating or updating custom Langflow components so they:
- Build without errors.
- Connect to other components reliably.
- Produce outputs in formats that downstream nodes (like Parser) can consume.

## Environment Notes
- This workspace uses the `lfx` API (not legacy `langflow` imports).
- Components live under `custom_nodes/` in this repo.

## Core Patterns
### 1. Base Classes and Imports
Prefer current `lfx` imports.

Common bases:
- `LCVectorStoreComponent` for vector stores / retrievers.
- `LCModelComponent` for model providers.
- `CustomComponent` or `Component` for generic nodes.

Common imports:
- `from lfx.base.vectorstores.model import LCVectorStoreComponent, check_cached_vector_store`
- `from lfx.io import ...` for inputs/outputs.
- `from lfx.schema.data import Data`
- `from lfx.schema.dataframe import DataFrame`
- `from lfx.field_typing import VectorStore` for output typing.

Avoid legacy paths like:
- `langflow.base.*`
- `langflow.schema.*`

These break in this repo because the environment expects `lfx.*`.

### 2. Inputs and Outputs
Define inputs and outputs on the component class.

Example output definition:
```python
outputs = [
    Output(
        name="results",
        display_name="Results",
        method="search_documents",
        output_types=["DataFrame"],
    )
]
```

Notes:
- `output_types` is critical for wiring in the UI.
- If you return a vector store handle, use `output_types=["VectorStore"]`.
- If you return data for a Parser, use `DataFrame` or `Data`, not `list[Data]`.

### 3. Vector Store Components
Use the `LCVectorStoreComponent` base class and `@check_cached_vector_store`.

Pattern:
```python
class MyStore(LCVectorStoreComponent):
    inputs = [
        ...
        *LCVectorStoreComponent.inputs,
        HandleInput(name="embedding", input_types=["Embeddings"]),
    ]

    @check_cached_vector_store
    def build_vector_store(self):
        ...
```

### 4. Vector Store Output Components
If a component outputs a vector store handle, return a `VectorStore` type and expose it via output.

Key points:
- Return type hint should be `VectorStore`.
- Output should include `output_types=["VectorStore"]`.
- If `url` is provided, ignore `host` and `port` when building server kwargs.

Example behavior:
```python
url = self.url or None
server_kwargs = {
    "host": None if url else (self.host or None),
    "port": None if url else int(self.port),
    "grpc_port": None if url else int(self.grpc_port),
    "url": url,
}
```

### 5. Retriever Outputs and Parser Compatibility
The Parser component only accepts:
- `DataFrame`
- `Data`
- A dict in the shape of a DataFrame or Data

It **does not** accept `list[Data]`.

If you produce a list of `Data` objects, the Parser will error with:
```
List of Data objects is not supported.
```

**Fix**: wrap results into a `DataFrame`.

Example:
```python
data = docs_to_data(unique_docs)  # returns list[Data]
rows = [item.data if isinstance(item, Data) else item for item in data]
df = DataFrame(data=rows)
return df
```

### 6. Multi-Query Retriever
Use `MultiQueryRetriever.from_llm(...)` and call `get_relevant_documents(query)`.

If you add custom query generation, note that some LangChain versions require a `run_manager` when calling `generate_queries()` directly. If that happens:
- Use `get_relevant_documents()` only.
- Or run the `llm_chain` directly and parse the output.

We reverted to the stable path:
```python
multi_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=self.llm,
    prompt=prompt,
    include_original=self.include_original,
)

docs = multi_retriever.get_relevant_documents(self.query)
```

### 7. DataFrame Outputs
A DataFrame output is the safest for downstream parsers. Use a row-per-document pattern:

```python
rows = [item.data if isinstance(item, Data) else item for item in data]
return DataFrame(data=rows)
```

Include a `text` field in your `Data` objects if downstream templates expect `{text}`.

## Known Edge Cases (and Fixes)
### A. Build Crash on Old Imports
Symptoms:
- Component crashes during build with missing module errors.

Fix:
- Replace `langflow.*` imports with `lfx.*`.

### B. Output Type Mismatch (Vector Store)
Symptoms:
- Node output won’t connect to a retriever input.

Fix:
- Ensure `Output(..., output_types=["VectorStore"])`.
- Ensure return type is `VectorStore` (type hint and actual object).

### C. Parser Error: List of Data objects
Symptoms:
- Parser throws `List of Data objects is not supported.`

Fix:
- Return a `DataFrame` or `Data` instead of `list[Data]`.

### D. MultiQueryRetriever.generate_queries Requires run_manager
Symptoms:
- Error: `missing 1 required positional argument: 'run_manager'`.

Fix:
- Avoid calling `generate_queries()` directly.
- Use `get_relevant_documents()`.

## Quick Checklist Before You Commit
- All imports use `lfx.*`.
- Outputs declare `output_types`.
- Parser-facing outputs return `DataFrame` or `Data`.
- Vector store outputs use `VectorStore` type.
- If `url` is set for Qdrant, ignore `host/port/grpc_port`.

## Current Custom Nodes in This Repo
- `custom_nodes/qdrant_vector_store.py`
- `custom_nodes/qdrant_vector_store_output.py`
- `custom_nodes/pinecone_vector_store.py`
- `custom_nodes/groq_model_provider.py`
- `custom_nodes/multi_query_retriever.py`
