from langchain_community.vectorstores import Qdrant
from langchain_core.embeddings import Embeddings

from lfx.base.vectorstores.model import LCVectorStoreComponent, check_cached_vector_store
from lfx.field_typing import VectorStore
from lfx.io import DropdownInput, HandleInput, IntInput, SecretStrInput, StrInput, Output
from lfx.schema.data import Data


class QdrantVectorStoreOutputComponent(LCVectorStoreComponent):
    display_name = "Qdrant Vector Store"
    description = "Qdrant Vector Store output component"
    documentation = "https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/qdrant"
    icon = "Qdrant"
    name = "QdrantVectorStoreOutput"

    inputs = [
        StrInput(name="collection_name", display_name="Collection Name", required=True),
        StrInput(name="host", display_name="Host", value="localhost", advanced=True),
        IntInput(name="port", display_name="Port", value=6333, advanced=True),
        IntInput(name="grpc_port", display_name="gRPC Port", value=6334, advanced=True),
        SecretStrInput(name="api_key", display_name="Qdrant API Key", advanced=True),
        StrInput(name="prefix", display_name="Prefix", advanced=True),
        IntInput(name="timeout", display_name="Timeout", advanced=True),
        StrInput(name="path", display_name="Path", advanced=True),
        StrInput(name="url", display_name="URL", advanced=True),
        DropdownInput(
            name="distance_func",
            display_name="Distance Function",
            options=["Cosine", "Euclidean", "Dot Product"],
            value="Cosine",
            advanced=True,
        ),
        StrInput(name="content_payload_key", display_name="Content Payload Key", value="page_content", advanced=True),
        StrInput(name="metadata_payload_key", display_name="Metadata Payload Key", value="metadata", advanced=True),
        *LCVectorStoreComponent.inputs,
        HandleInput(name="embedding", display_name="Embedding", input_types=["Embeddings"]),
    ]

    outputs = [
        Output(
            name="vector_store",
            display_name="Vector Store",
            method="build_vector_store",
            output_types=["VectorStore"],
        ),
    ]

    @check_cached_vector_store
    def build_vector_store(self) -> VectorStore:
        qdrant_kwargs = {
            "collection_name": self.collection_name,
            "content_payload_key": self.content_payload_key,
            "metadata_payload_key": self.metadata_payload_key,
        }

        url = self.url or None
        server_kwargs = {
            "host": None if url else (self.host or None),
            "port": None if url else int(self.port),
            "grpc_port": None if url else int(self.grpc_port),
            "api_key": self.api_key,
            "prefix": self.prefix,
            "timeout": int(self.timeout) if self.timeout else None,
            "path": self.path or None,
            "url": url,
        }

        server_kwargs = {k: v for k, v in server_kwargs.items() if v is not None}

        self.ingest_data = self._prepare_ingest_data()

        documents = []
        for _input in self.ingest_data or []:
            if isinstance(_input, Data):
                documents.append(_input.to_lc_document())
            else:
                documents.append(_input)

        if not isinstance(self.embedding, Embeddings):
            msg = "Invalid embedding object"
            raise TypeError(msg)

        if documents:
            qdrant = Qdrant.from_documents(
                documents, embedding=self.embedding, **qdrant_kwargs, **server_kwargs
            )
        else:
            from qdrant_client import QdrantClient

            client = QdrantClient(**server_kwargs)
            qdrant = Qdrant(embeddings=self.embedding, client=client, **qdrant_kwargs)

        return qdrant
