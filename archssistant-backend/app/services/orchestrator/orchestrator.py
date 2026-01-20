"""Orchestrator: controls the end-to-end conversational flow.

Responsibilities:
- Derive and persist conversation state from the message history
- Ask the ElicitationMachine for interpretations and next questions
- Request recommendations from the DecisionMaker (symbolic evaluation)
- Request explanations from the RecommendationExplainer (LLM generated)
"""

from __future__ import annotations

from typing import Any, Optional

from app.core import get_logger
from app.services.decision_maker import DecisionMaker
from app.services.elicitation_machine import ElicitationMachine
from app.services.recommendation_explainer import RecommendationExplainer


class Orchestrator:
    """Coordinates the 5-component backend flow (excluding UI)."""

    ALL_PARAMETERS = [
        "complexity",
        "scalability",
        "teamExperience",
        "dataVolume",
        "teamSize",
        "availability",
        "maintainability",
        "interoperability",
    ]

    def __init__(
        self,
        elicitation_machine     : Optional[ElicitationMachine] = None,
        decision_maker          : Optional[DecisionMaker] = None,
        recommendation_explainer: Optional[RecommendationExplainer] = None,
    ) -> None:
        self.elicitation_machine        = elicitation_machine or ElicitationMachine()
        self.decision_maker             = decision_maker or DecisionMaker()
        self.recommendation_explainer   = recommendation_explainer or RecommendationExplainer()
        self.logger                     = get_logger(__name__)

    def get_conversation_state(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        last_assistant_message: dict[str, Any] | None = None
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                last_assistant_message = msg
                break

        if last_assistant_message:
            return last_assistant_message.get(
                "state",
                {
                    "inferredParams": {}, 
                    "lastQuestion"  : None, 
                    "isClarifying"  : False, 
                    "status"        : "interviewing"
                },
            )

        return {
            "inferredParams": {}, 
            "lastQuestion"  : None, 
            "isClarifying"  : False, 
            "status"        : "interviewing"
        }

    def handle_message(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        project_description = self._extract_project_description(history)
        self._ensure_user_description(history)

        state               = self.get_conversation_state(history)
        interview_result    = self._process_interview_phase(history, state)
        if interview_result is not None:
            return interview_result

        if state["status"] == "recommending":
            recommendation_result = self._process_recommendation_phase(
                history             = history,
                state               = state,
                project_description = project_description,
            )
            return recommendation_result

        final_response  = self._build_final_response()
        result          = {
            "response": final_response, 
            "state": state
        }
        return result

    def _extract_project_description(self, history: list[dict[str, Any]]) -> str:
        for msg in history:
            if msg.get("role") == "user_description":
                return msg.get("content", "")
        return history[0].get("content", "")

    def _ensure_user_description(self, history: list[dict[str, Any]]) -> None:
        if len(history) == 1:
            history[0]["role"] = "user_description"

    def _process_interview_phase(self, history: list[dict[str, Any]], state: dict[str, Any]) -> Optional[dict[str, Any]]:
        if state["status"] != "interviewing":
            return None

        interpretation_result = None
        if state.get("lastQuestion"):
            interpretation_result = self._interpret_last_answer(history, state)

        inferred_count = len(state["inferredParams"])
        if inferred_count >= 5:
            state["status"] = "recommending"
            return None

        next_question   = self._generate_next_question(history, state, interpretation_result)
        response        = {
            "role": "assistant", 
            "content": next_question.get("full_response_text")
        }
        result          = {
            "response": response, 
            "state": state
        }
        return result

    def _interpret_last_answer(self, history: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, Any]:
        user_message        = history[-1]
        parameter_to_infer  = state["lastQuestion"].get("parameter_to_infer")
        question_text       = state["lastQuestion"].get("question_text")

        interpretation_result = self.elicitation_machine.interpret_user_answer(
            question_text,
            user_message.get("content"),
            parameter_to_infer,
        )

        if interpretation_result.get("classification") == "UNCERTAIN":
            state["isClarifying"] = True
        else:
            state["inferredParams"][parameter_to_infer] = interpretation_result.get("classification")
            state["isClarifying"] = False
        return interpretation_result

    def _generate_next_question(
        self,
        history                 : list[dict[str, Any]],
        state                   : dict[str, Any],
        interpretation_result   : Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        remaining_params: list[str] = []
        for parameter_name in self.ALL_PARAMETERS:
            if parameter_name not in state["inferredParams"]:
                remaining_params.append(parameter_name)

        next_question = self.elicitation_machine.generate_next_question(
            history                 = history,
            remaining_params        = remaining_params,
            last_interpretation     = interpretation_result,
            is_clarification_needed = state["isClarifying"],
        )

        next_param_to_infer = (
            state["lastQuestion"]["parameter_to_infer"]
            if state["isClarifying"]
            else next_question.get("parameter_to_infer")
        )

        state["lastQuestion"] = {
            "parameter_to_infer": next_param_to_infer,
            "question_text"     : next_question.get("question_for_user"),
        }
        return next_question

    def _process_recommendation_phase(
        self,
        history             : list[dict[str, Any]],
        state               : dict[str, Any],
        project_description : str,
    ) -> dict[str, Any]:
        recommendations = self.decision_maker.get_recommendation(state["inferredParams"])
        if not recommendations:
            empty_response = {
                "role"      : "assistant",
                "content"   : "I couldn't determine a recommendation with the provided data.",
            }
            state["status"] = "finished"
            result = {"response": empty_response, "state": state}
            return result

        self.logger.debug(
            f"Generating descriptions for {len(recommendations)} architectures: {[r['name'] for r in recommendations]}"
        )

        descriptions = self.recommendation_explainer.generate_final_descriptions(
            project_description = project_description,
            recommendations     = recommendations,
            history             = history,
        )

        enriched_recommendations = self._enrich_recommendations(recommendations, descriptions)
        response = {
            "role"          : "assistant",
            "content"       : "Thank you! I have analyzed your responses.",
            "recommendation": enriched_recommendations,
        }
        state["status"] = "finished"
        result = {"response": response, "state": state}
        return result

    def _enrich_recommendations(
        self,
        recommendations : list[dict[str, Any]],
        descriptions    : dict[str, dict[str, str]],
    ) -> list[dict[str, Any]]:
        enriched_list: list[dict[str, Any]] = []
        for rec in recommendations:
            arch_name = rec["name"]
            desc_data = descriptions.get(arch_name)

            if not desc_data:
                for key in descriptions.keys():
                    if key.lower() == arch_name.lower():
                        desc_data = descriptions[key]
                        break

            if not desc_data:
                self.logger.warning(f"No description found for '{arch_name}'")
                desc_data = {}

            enriched_list.append(
                {
                    **rec,
                    "description": desc_data.get("description", "Description not available."),
                    "justification": desc_data.get("justification", "Justification not available."),
                }
            )
        return enriched_list

    def _build_final_response(self) -> dict[str, str]:
        final_message = {
            "role"      : "assistant",
            "content"   : "If you have another project to analyze, simply reload the page.",
        }
        return final_message