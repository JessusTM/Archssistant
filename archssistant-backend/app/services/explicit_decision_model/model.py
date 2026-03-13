"""Explicit Decision Model.

This component instantiates a decision table for a given case. It does not
score or rank architectures; it only fills the table with values.
"""

from typing import Any

from app.services.explicit_decision_model.architecture_catalog import architectures


class ExplicitDecisionModel:
    """Instantiates a decision table from inferred criteria and explicit knowledge."""

    def instantiate(self, inferred_criteria: dict[str, str]) -> dict[str, Any]:
        """Build a decision table instance with values filled.

        The table includes only the criteria that were inferred for the user.
        """

        criteria_keys = list(inferred_criteria.keys())

        rows: list[dict[str, Any]] = []
        for arch in architectures:
            criteria_values: dict[str, str] = {}
            for key in criteria_keys:
                value = arch.get(key)
                if value is not None:
                    criteria_values[key] = value

            rows.append(
                {
                    "architecture_name": arch["name"],
                    "criteria_values": criteria_values,
                    "score": None,
                    "architecture": arch,
                }
            )

        return {"inferred_criteria": inferred_criteria, "rows": rows}
