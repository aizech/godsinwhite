"""
BI Agent module.
This module provides a factory function to create a business intellgience agent.
https://docs.agno.com/tools/visualization
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge import AgentKnowledge
from agno.memory.v2 import Memory
from agno.models.base import Model
from agno.tools.visualization import VisualizationTools


def create_bi_agent(
    model: Model, memory: Memory, knowledge: AgentKnowledge
) -> Agent:
    """
    Create a BI agent that can analyze data and create various types of charts and data visualizations.
    
    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        
    Returns:
        An Agent instance configured as a BI agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)
    
    return Agent(
        name="BI",
        role="Analyze data and create various types of charts and data visualizations.",
        model=model_copy,
        memory=memory,
        knowledge=knowledge,
        tools=[VisualizationTools(enable_all=True, output_dir="dashboard_charts")],
        description="You are a Business Intelligence agent. Analyze data and create clear, informative charts and graphs from data.",
        instructions=[
            "You are a Business Intelligence analyst.",
            "Create comprehensive visualizations for executive dashboards.",
            "Provide actionable insights and recommendations.",
            "Use appropriate chart types for different data scenarios.",
            "Always explain what the data reveals about business performance.",
        ],
    )
