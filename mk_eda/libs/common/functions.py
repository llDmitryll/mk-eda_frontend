from typing import Callable, Union

from pyeda.boolalg.expr import And, Expression, Implies, Majority, Not, Or, Variable, Xor  # type: ignore

BooleanFunction = Union[Variable, Expression]

FUNCTIONS: dict[str, Callable[..., BooleanFunction]] = {
    "not": Not,
    "and": And,
    "or": Or,
    "xor": Xor,
    "implies": Implies,
    "majority": Majority,
}
