
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    message: Annotated[str, "Pergunta do usuário"]
    answer: Annotated[str, "Resposta"]
    user_id: Annotated[str, "Identificador do usuario"]
    flag_use_tool:Annotated[bool, "Flag que indica a necessidade de usar uma ferramenta"]
    tool_type: Annotated[str, "Qual ferrementa será usada"]
    valid_params: Annotated[bool, "Flag que indica se os parametros estão corretos"]