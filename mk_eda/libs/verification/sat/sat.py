from typing import Optional

from pyeda.boolalg.expr import Expression, Variable, exprvar  # type: ignore

from mk_eda.libs.common.logger import get_logger
from mk_eda.libs.graph.graph import InverterGraph

logger = get_logger(__name__)


class Sat(InverterGraph):
    """Class representing a boolean satisfiability problem."""

    def __init__(self):
        super().__init__()
        self.input_vars: dict[str, Variable] = {input_var: exprvar(input_var) for input_var in self.inputs}

    @staticmethod
    def find_unequal_set(circuit1: Expression, circuit2: Expression) -> Optional[dict[Variable, int]]:
        """Find a satisfying assignment where the two circuits are not equivalent."""
        try:
            equivalence_formula = circuit1 ^ circuit2  # type: ignore
            return equivalence_formula.satisfy_one()  # type: ignore
        except Exception as e:
            logger.error("Equivalence check failed. Error: %s", str(e))
            raise e
