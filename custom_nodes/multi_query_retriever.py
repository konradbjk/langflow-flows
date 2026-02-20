from typing import Iterable

from langchain.prompts import PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.documents import Document

from lfx.base.vectorstores.model import LCVectorStoreComponent, check_cached_vector_store
from lfx.helpers.data import docs_to_data
from lfx.io import BoolInput, HandleInput, IntInput, MessageTextInput, MultilineInput, Output
from lfx.log.logger import logger
from lfx.schema.data import Data
from lfx.schema.dataframe import DataFrame


DEFAULT_PROMPT = (
    "You are an expert at generating alternative search queries for a vector database.\n"
    "Given the user question, produce {n_queries} diverse, concise search queries "
    "that preserve the original intent. Output one query per line.\n\n"
    "User question: {question}"
)


class MultiQueryVectorSearchComponent(LCVectorStoreComponent):
    display_name = "Multi-Query Vector Search"
    description = (
        "Generate multiple reformulations of a user query with an LLM, search a vector store for each, "
        "and return de-duplicated results."
    )
    icon = "Search"
    name = "MultiQueryVectorSearch"

    inputs = [
        HandleInput(
            name="llm",
            display_name="Language Model",
            input_types=["LanguageModel"],
            required=True,
        ),
        HandleInput(
            name="vector_store",
            display_name="Vector Store",
            input_types=["VectorStore"],
            required=True,
        ),
        *LCVectorStoreComponent.inputs,
        MessageTextInput(
            name="query",
            display_name="User Query",
            info="The user question to expand into multiple search queries.",
            required=True,
        ),
        MultilineInput(
            name="prompt",
            display_name="Multi-Query Prompt",
            info=(
                "Prompt used to generate alternate queries. Use {question} as the placeholder for the user query."
            ),
            value=DEFAULT_PROMPT,
            advanced=True,
        ),
        IntInput(
            name="number_of_queries",
            display_name="Number of Queries",
            info="How many alternative queries to generate.",
            value=3,
            advanced=True,
        ),
        IntInput(
            name="number_of_results",
            display_name="Results Per Query",
            info="How many results to retrieve per query.",
            value=4,
            advanced=True,
        ),
        BoolInput(
            name="include_original",
            display_name="Include Original Query",
            info="If true, run the original query in addition to generated queries.",
            value=True,
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            name="results",
            display_name="Results",
            method="search_documents",
            output_types=["DataFrame"],
        )
    ]

    @check_cached_vector_store
    def build_vector_store(self):
        if self.vector_store is None:
            msg = "Vector store is required."
            raise TypeError(msg)
        return self.vector_store

    def _build_prompt(self) -> PromptTemplate:
        template = (self.prompt or "").strip() or DEFAULT_PROMPT
        if "{question}" not in template:
            template = f"{template}\n\nUser question: {{question}}"
        n_queries = self.number_of_queries or 3
        return PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={"n_queries": str(n_queries)},
        )

    def _dedupe_documents(self, docs: Iterable[Document]) -> list[Document]:
        seen: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
        unique_docs: list[Document] = []
        for doc in docs:
            metadata_items = tuple(sorted((str(k), str(v)) for k, v in (doc.metadata or {}).items()))
            key = (doc.page_content, metadata_items)
            if key in seen:
                continue
            seen.add(key)
            unique_docs.append(doc)
        return unique_docs

    def search_documents(self) -> DataFrame:
        if not self.query or not isinstance(self.query, str) or not self.query.strip():
            return DataFrame(data=[])

        vector_store = self.build_vector_store()
        if not hasattr(vector_store, "as_retriever"):
            msg = "Vector store does not support retrieval. Expected an object with as_retriever()."
            raise TypeError(msg)

        retriever = vector_store.as_retriever(
            search_kwargs={"k": int(self.number_of_results or 4)}
        )
        prompt = self._build_prompt()

        try:
            multi_retriever = MultiQueryRetriever.from_llm(
                retriever=retriever,
                llm=self.llm,
                prompt=prompt,
                include_original=self.include_original,
            )
            docs = multi_retriever.get_relevant_documents(self.query)
        except Exception as e:
            logger.exception(f"Multi-query retrieval failed: {e}")
            raise

        unique_docs = self._dedupe_documents(docs)
        data = docs_to_data(unique_docs)
        rows = [item.data if isinstance(item, Data) else item for item in data]
        df = DataFrame(data=rows)
        self.status = df
        return df
