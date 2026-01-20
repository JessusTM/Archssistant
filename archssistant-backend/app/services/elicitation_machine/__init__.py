"""Elicitation Machine component.

Responsible for inferring (eliciting) variables from the user via LLM:
- Interpret a user's answer for a target parameter
- Generate the next best question (or clarification)
"""

from .elicitation_machine import ElicitationMachine

__all__ = ["ElicitationMachine"]