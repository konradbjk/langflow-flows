from langchain_text_splitters import RecursiveCharacterTextSplitter

from lfx.custom.custom_component.component import Component
from lfx.io import HandleInput, IntInput, MessageTextInput, Output
from lfx.schema.data import Data
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message


class RecursiveCharacterTextSplitterComponent(Component):
    display_name: str = "Recursive Character Text Splitter"
    description: str = "Split text trying to keep all related text together."
    documentation: str = "https://docs.langflow.org/components/text-splitters#recursivecharactertextsplitter"
    icon = "scissors-line-dashed"
    name = "RecursiveCharacterTextSplitter"

    inputs = [
        HandleInput(
            name="data_inputs",
            display_name="Input",
            info="The data with texts to split in chunks.",
            input_types=["Data", "DataFrame", "Message"],
            required=True,
        ),
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info="The maximum length of each chunk.",
            value=1000,
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="The amount of overlap between chunks.",
            value=200,
        ),
        MessageTextInput(
            name="text_key",
            display_name="Text Key",
            info="The key to use for the text column.",
            value="text",
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Chunks",
            name="dataframe",
            method="split_text",
            output_types=["DataFrame"],
        ),
    ]

    def _docs_to_data(self, docs) -> list[Data]:
        return [Data(text=doc.page_content, data=doc.metadata) for doc in docs]

    def split_text_base(self):
        if isinstance(self.data_inputs, DataFrame):
            if not len(self.data_inputs):
                msg = "DataFrame is empty"
                raise TypeError(msg)

            self.data_inputs.text_key = self.text_key
            try:
                documents = self.data_inputs.to_lc_documents()
            except Exception as e:
                msg = f"Error converting DataFrame to documents: {e}"
                raise TypeError(msg) from e
        elif isinstance(self.data_inputs, Message):
            self.data_inputs = [self.data_inputs.to_data()]
            return self.split_text_base()
        else:
            if not self.data_inputs:
                msg = "No data inputs provided"
                raise TypeError(msg)

            documents = []
            if isinstance(self.data_inputs, Data):
                self.data_inputs.text_key = self.text_key
                documents = [self.data_inputs.to_lc_document()]
            else:
                try:
                    documents = [input_.to_lc_document() for input_ in self.data_inputs if isinstance(input_, Data)]
                    if not documents:
                        msg = f"No valid Data inputs found in {type(self.data_inputs)}"
                        raise TypeError(msg)
                except AttributeError as e:
                    msg = f"Invalid input type in collection: {e}"
                    raise TypeError(msg) from e

        try:
            splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", " "],
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            return splitter.split_documents(documents)
        except Exception as e:
            msg = f"Error splitting text: {e}"
            raise TypeError(msg) from e

    def split_text(self) -> DataFrame:
        return DataFrame(self._docs_to_data(self.split_text_base()))
