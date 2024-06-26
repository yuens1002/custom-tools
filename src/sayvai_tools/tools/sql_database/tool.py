from typing import Any, Optional

from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools import BaseTool
from proto import Field
from sqlalchemy.engine import Engine

from sayvai_tools.tools.sql_database.prompt import PROMPT, SQL_PROMPTS
from sayvai_tools.utils.database.dbbase import SQLDatabase
from sayvai_tools.utils.database.dbchain import SQLDatabaseChain
from sayvai_tools.utils.exception import deprecated

# @deprecated()
# class DatabaseSchema(BaseModel):
#     llm: BaseLanguageModel = Field(
#         ...,
#         description="Language model to use for generating SQL queries.",
#     )
#     engine: Engine = Field(
#         ...,
#         description="SQLAlchemy engine to use for querying the database.",
#     )
#     prompt: Optional[BasePromptTemplate] = Field(
#         None,
#         description="Prompt template to use for generating SQL queries.",
#     )
#     verbose: bool = Field(
#         False,
#         description="Whether to print verbose output.",
#     )
#     k: int = Field(
#         5,
#         description="Number of results to return.",
#     )


@deprecated(
    message="Use langchain tool instead, Database will be removed from sayvai-tools 0.0.5"
)
class Database:
    """Tool that queries vector database."""

    name = "Database"
    description = (
        "Useful for when you need to access sql database"
        "Input should be a natural language"
    )

    def __init__(
        self,
        llm: BaseLanguageModel,
        engine: Engine,
        prompt: Optional[BasePromptTemplate] = None,
        verbose: bool = False,
        k: int = 5,
    ):
        self.llm = llm
        self.engine = engine
        self.prompt = prompt
        self.verbose = verbose
        self.k = k

    @classmethod
    def create(cls, **kwargs) -> "Database":
        return cls(
            llm=kwargs["llm"],
            engine=kwargs["engine"],
            prompt=kwargs.get("prompt"),
            verbose=kwargs.get("verbose", False),
            k=kwargs.get("k", 5),
        )

    def _run(self, query: str) -> str:
        db = SQLDatabase(engine=self.engine)

        if self.prompt is not None:
            prompt_to_use = self.prompt
        elif db.dialect in SQL_PROMPTS:
            prompt_to_use = SQL_PROMPTS[db.dialect]
        else:
            prompt_to_use = PROMPT
        inputs = {
            "input": lambda x: x["question"] + "\nSQLQuery: ",
            "top_k": lambda _: self.k,
            "table_info": lambda x: db.get_table_info(
                table_names=x.get("table_names_to_use")
            ),
        }
        if "dialect" in prompt_to_use.input_variables:
            inputs["dialect"] = lambda _: (db.dialect, prompt_to_use)

        sql_db_chain = SQLDatabaseChain.from_llm(
            llm=self.llm, db=db, prompt=prompt_to_use, verbose=self.verbose
        )

        return sql_db_chain.run(query)

    async def _arun(self, query: str):
        raise NotImplementedError("SQL database async not implemented")
