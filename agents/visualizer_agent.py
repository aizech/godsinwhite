"""
Visualizer Agent module.
This module provides a factory function to create a data visualization agent.
https://docs.agno.com/tools/visualization
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge import AgentKnowledge
from agno.memory.v2 import Memory
from agno.models.base import Model
from agno.tools.visualization import VisualizationTools


def create_visualizer_agent(
    model: Model, memory: Memory, knowledge: AgentKnowledge
) -> Agent:
    """
    Create a Visualizer agent that can create various types of charts and data visualizations.
    
    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        
    Returns:
        An Agent instance configured as a Visualizer agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)
    
    return Agent(
        name="Visualizer",
        role="Create data visualizations including bar charts, line charts, pie charts, scatter plots, and histograms.",
        model=model_copy,
        memory=memory,
        knowledge=knowledge,
        tools=[VisualizationTools(enable_all=True, output_dir="dashboard_charts")],
        description="You are a data visualization agent. Create clear, informative charts and graphs from data.",
        instructions=[
            "Always provide clear and descriptive titles for your charts",
            "Use appropriate chart types based on the data structure and analysis needs",
            "Include proper axis labels and legends when necessary",
            "Save charts with meaningful filenames that reflect their content",
            "Provide insights about the data patterns shown in the visualizations",
            "After creating any chart, display it in your response using markdown image syntax with 50% width: ![Chart Description](file_path){width=50%}",
            "Always show the created visualization in your response so users can see the chart immediately",
        ],
    )