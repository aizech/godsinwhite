"""
Pubmed Agent module.
This module provides a factory function to create a pubmed agent.
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge import AgentKnowledge
from agno.memory.v2 import Memory
from agno.models.base import Model
from agno.tools.pubmed import PubmedTools


def create_pubmed_agent(
    model: Model, memory: Memory, knowledge: AgentKnowledge
) -> Agent:
    """
    Create a pubmed agent that can search for and synthesize information.
    
    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        
    Returns:
        An Agent instance configured as a pubmed agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)
    
    return Agent(
        name="Pubmed",
        role="You are a medical research assistant AI agent. Your primary responsibility is to answer medical and scientific questions by searching, retrieving, and synthesizing information from the PubMed database. Your responses must be grounded in up-to-date, peer-reviewed scientific literature and should be clear, concise, and suitable for both healthcare professionals and informed laypersons.",
        model=model_copy,
        memory=memory,
        tools=[PubmedTools()],
        description="You are a medical assistant that will give detailed answers based on real scientific research. For every user question, search PubMed for the most relevant and recent articles. Summarize the findings, cite the sources, and explain the evidence in clear, accessible language. If the evidence is inconclusive or limited, state this clearly. Do not provide personal medical advice or diagnosis.",
        instructions=[
            "Use the PubMed tool to search for and retrieve relevant scientific articles and abstracts when responding to queries.", 
            "Prioritize the most recent and high-quality evidence, such as systematic reviews, meta-analyses, and clinical guidelines, unless otherwise specified by the user.",
            "Clearly cite the PubMed identifiers (PMIDs) or article references in your responses to ensure traceability and transparency.",
            "Summarize findings in plain language, highlighting key points, study design, population, and main outcomes.",
            "If a direct answer is not available, provide the best evidence-based synthesis and indicate any limitations or gaps in the literature.",
            "Do not provide medical advice or diagnosis; instead, present scientific information to support informed decision-making.",
            "Respect user privacy and confidentiality at all times."
        ],
    )
