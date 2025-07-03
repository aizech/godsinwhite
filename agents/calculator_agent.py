"""
Calculator Agent module.
This module provides a factory function to create a calculator agent.
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge import AgentKnowledge
from agno.memory.v2 import Memory
from agno.models.base import Model
from agno.tools.calculator import CalculatorTools


def create_calculator_agent(
    model: Model, memory: Memory, knowledge: AgentKnowledge
) -> Agent:
    """
    Create a calculator agent that can perform mathematical operations.
    
    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        
    Returns:
        An Agent instance configured as a calculator agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)
    
    return Agent(
        name="Calculator",
        role="Answer mathematical questions and perform precise calculations",
        model=model_copy,
        memory=memory,
        tools=[CalculatorTools(enable_all=True)],
        description="You are a precise and comprehensive calculator agent. Your goal is to solve mathematical problems with accuracy and explain your methodology clearly to users.",
        instructions=[
            "Always use the calculator tools for mathematical operations to ensure precision.",
            "Present answers in a clear format with appropriate units and significant figures.",
            "Show step-by-step workings for complex calculations to help users understand the process.",
            "Ask clarifying questions if the user's request is ambiguous or incomplete.",
            "For financial calculations, specify assumptions regarding interest rates, time periods, etc.",
        ],
    )
