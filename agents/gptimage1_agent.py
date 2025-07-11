"""GPTImage1 Agent module.
This module provides a factory function to create a GPTImage1 agent.
"""

import sys
import os
from pathlib import Path
from copy import deepcopy
from textwrap import dedent

from agno.agent import Agent
from agno.memory.v2 import Memory
from agno.knowledge import AgentKnowledge
from agno.models.base import Model
from agno.tools.thinking import ThinkingTools

# Windows-specific event loop policy for asyncio compatibility
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the parent directory to the path to import GPTImage1Tools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import GPTImage1Tools - we'll import it inside the function to avoid pickling issues
# from tools.gptimage1 import GPTImage1Tools

def create_gptimage1_agent(
    model: Model, memory: Memory, knowledge: AgentKnowledge
) -> Agent:
    """
    Create a gptimage1 agent that can generate images.
    
    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        
    Returns:
        An Agent instance configured as a gptimage1 agent
    """
    # Import GPTImage1Tools inside the function to avoid pickling issues
    from tools.gptimage1 import GPTImage1Tools
    
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)
    
    return Agent(
        name="GPTImage1",
        role="Generate images",
        model=model_copy,
        memory=memory,
        knowledge=knowledge,
        tools=[ThinkingTools(), GPTImage1Tools()],
        description=dedent("""\
            You are an experienced AI artist with expertise in various artistic styles,
            from photorealism to abstract art. You have a deep understanding of composition,
            color theory, and visual storytelling.\
        """),
        instructions=dedent("""\
            As an AI artist, follow these guidelines:
            1. Analyze the user's request carefully to understand the desired style and mood
            2. Before generating, enhance the prompt with artistic details like lighting, perspective, and atmosphere
            3. Use the `create_image` tool with detailed, well-crafted prompts
            4. Provide a brief explanation of the artistic choices made
            5. If the request is unclear, ask for clarification about style preferences

            Always aim to create visually striking and meaningful images that capture the user's vision!\
        """),
        )
