import asyncio
import os
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from config import config
from agno.team import Team
from agno.utils.log import logger
from halo import HaloConfig, create_halo, halo_memory, show_scotty
from utils import (
    about,
    add_message,
    display_tool_calls,
    example_inputs,
    initialize_session_state,
    knowledge_widget,
    selected_agents,
    selected_model,
    selected_tools,
    session_selector,
    show_user_memories,
    utilities_widget,
)

# Must precede any llm module imports
#from langtrace_python_sdk import langtrace
#from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

load_dotenv(override=True)

#langtrace.init()

nest_asyncio.apply()
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
    #initial_sidebar_state="collapsed",
    menu_items=config.MENU_ITEMS
)

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH
)


async def header():
    one_cola = st.columns([1])[0]
    with one_cola:
        col1a, col2a = st.columns([1, 5])

        with col1a:
            #image_path = os.path.join(config.ASSETS_DIR, "masteragent.png")
            image_path = config.MASTER_AGENT_ICON
            st.image(image_path, width=200)
        with col2a:
            st.markdown(
                f"<h1>{config.APP_NAME}</h1>", unsafe_allow_html=True
            )
            st.markdown(
                f"<p>{config.APP_DESCRIPTION}</p>",
                unsafe_allow_html=True,
            )
    

async def body() -> None:
    ####################################################################
    # Initialize User and Session State
    ####################################################################
    # Get Windows username automatically
    import os
    windows_username = "Ava"  # Default fallback
    try:
        windows_username = os.getlogin()
    except Exception:
        pass
        
    # Initialize persistent tool calls storage if not already present
    if "persistent_tool_calls" not in st.session_state:
        st.session_state["persistent_tool_calls"] = {}
    
    st.sidebar.markdown("# :material/co_present: User Id")
    user_id = st.sidebar.text_input("Username", value=windows_username)

    ####################################################################
    # Select Model
    ####################################################################
    model_id = await selected_model()

    ####################################################################
    # Select Tools
    ####################################################################
    tools = await selected_tools()

    ####################################################################
    # Select Team Members
    ####################################################################
    agents = await selected_agents()

    ####################################################################
    # Create HALO
    ####################################################################
    halo_config = HaloConfig(
        user_id=user_id, model_id=model_id, tools=tools, agents=agents
    )

    # Check if HALO instance should be recreated
    recreate_halo = (
        "halo" not in st.session_state
        or st.session_state.get("halo") is None
        or st.session_state.get("halo_config") != halo_config
    )

    # Create HALO instance if it doesn't exist or configuration has changed
    halo: Team
    if recreate_halo:
        logger.info("---*--- Creating HALO instance ---*---")
        halo = create_halo(halo_config)
        st.session_state["halo"] = halo
        st.session_state["halo_config"] = halo_config
        logger.info(f"---*--- HALO instance created ---*---")
    else:
        halo = st.session_state["halo"]
        logger.info(f"---*--- HALO instance exists ---*---")

    ####################################################################
    # Load Agent Session from the database
    ####################################################################
    try:
        logger.info(f"---*--- Loading HALO session ---*---")
        st.session_state["session_id"] = halo.load_session()
    except Exception:
        st.warning("Could not create HALO session, is the database running?")
        return
    logger.info(f"---*--- HALO session: {st.session_state.get('session_id')} ---*---")

    ####################################################################
    # Load agent runs (i.e. chat history) from memory if messages is not empty
    ####################################################################
    chat_history = halo.get_messages_for_session()
    if len(chat_history) > 0:
        logger.info("Loading messages")
        # Clear existing messages
        st.session_state["messages"] = []
        # Loop through the runs and add the messages to the messages list
        for message in chat_history:
            if message.role == "user":
                await add_message(message.role, str(message.content))
            if message.role == "assistant":
                await add_message("assistant", str(message.content), message.tool_calls)

    ####################################################################
    # Get user input
    ####################################################################
    if prompt := st.chat_input("✨ How can I help you?"):
        await add_message("user", prompt)

    ####################################################################
    # Show example inputs
    ####################################################################
    await example_inputs()

    ####################################################################
    # Show user memories
    ####################################################################
    await show_user_memories(halo_memory, user_id)

    ####################################################################
    # Display agent messages
    ####################################################################
    for message in st.session_state["messages"]:
        avatar = None
        if message["role"] == "user":
            avatar = "👤"
        elif message["role"] == "assistant":
            avatar = "🤖"
        if message["role"] in ["user", "assistant"]:
            _content = message["content"]
            #if _content is not None:
            # Skip messages with None or empty content
            if _content is not None and _content.strip() != "" and _content.strip().lower() != "none":
                with st.chat_message(message["role"], avatar=avatar):
                        # Generate a unique key for this message based on its content and role
                    message_key = f"{message['role']}_{hash(message['content'])}"
                    
                    # Store tool calls in persistent session state if they exist
                    if "tool_calls" in message and message["tool_calls"]:
                        # Store the tool calls in the persistent storage
                        st.session_state["persistent_tool_calls"][message_key] = message["tool_calls"]
                    
                    # Display tool calls if they exist in the persistent storage
                    if message_key in st.session_state["persistent_tool_calls"]:
                        # Create a dedicated container with a stable key
                        with st.container():
                            # Display the tool calls from the persistent storage
                            display_tool_calls(st.empty(), st.session_state["persistent_tool_calls"][message_key])
                    
                    # Check for image links in the content
                    import re
                    import os
                    from PIL import Image
                    
                    # Display the message content
                    st.markdown(_content)
                    
                    # Check for sandbox image links
                    sandbox_pattern = r'\[.*?\]\(sandbox:/mnt/data/([a-f0-9\-]+\.(?:png|jpg|jpeg|gif))\)'
                    sandbox_matches = re.findall(sandbox_pattern, _content)
                    
                    # Check for local file image links
                    file_pattern = r'\[.*?\]\(file:///(.*?\.(?:png|jpg|jpeg|gif))\)'
                    file_matches = re.findall(file_pattern, _content)
                    
                    # Display sandbox images if found
                    for img_filename in sandbox_matches:
                        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images", img_filename)
                        if os.path.exists(img_path):
                            try:
                                img = Image.open(img_path)
                                # Calculate 50% of the container width
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.image(img, caption=f"Generated Image: {img_filename}", use_container_width=True)
                            except Exception as e:
                                st.error(f"Error displaying image: {e}")
                    
                    # Display local file images if found
                    for img_path in file_matches:
                        if os.path.exists(img_path):
                            try:
                                img = Image.open(img_path)
                                # Calculate 50% of the container width
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.image(img, caption=f"Generated Image: {os.path.basename(img_path)}", use_container_width=True)
                            except Exception as e:
                                st.error(f"Error displaying image: {e}")
                    

    ####################################################################
    # Generate response for user message
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        user_message = last_message["content"]
        logger.info(f"Responding to message: {user_message}")
        with st.chat_message("assistant", avatar="🤖"):
            # Create container for tool calls
            tool_calls_container = st.empty()
            resp_container = st.empty()
            with st.spinner(":material/cognition: Thinking..."):
                response = ""
                try:
                    # Run the agent and stream the response
                    run_response = await halo.arun(
                        user_message, stream=True, stream_intermediate_steps=True
                    )
                    async for resp_chunk in run_response:
                        # Display tool calls if available and store them for later use
                        if resp_chunk.tools and len(resp_chunk.tools) > 0:
                            # Store the tools in the session state for this response
                            if "current_tool_calls" not in st.session_state:
                                st.session_state["current_tool_calls"] = []
                            # Add new tools to the list, avoiding duplicates
                            for tool in resp_chunk.tools:
                                # Get tool identifier (name or id)
                                tool_id = None
                                if hasattr(tool, 'get'):
                                    tool_id = tool.get("name") or tool.get("tool_name")
                                else:
                                    tool_id = getattr(tool, "name", None) or getattr(tool, "tool_name", None)
                                 
                                # Only add if not already in the list
                                is_duplicate = False
                                for t in st.session_state["current_tool_calls"]:
                                    # Get the name from the existing tool using the appropriate method
                                    existing_tool_id = None
                                    if hasattr(t, 'get'):
                                        existing_tool_id = t.get("name") or t.get("tool_name")
                                    else:
                                        existing_tool_id = getattr(t, "name", None) or getattr(t, "tool_name", None)
                                    
                                    # Compare with the current tool's ID
                                    if existing_tool_id == tool_id:
                                        is_duplicate = True
                                        break
                                        
                                # Add the tool if it's not a duplicate
                                if tool_id and not is_duplicate:
                                    st.session_state["current_tool_calls"].append(tool)
                            
                            # Display all accumulated tools
                            display_tool_calls(tool_calls_container, st.session_state["current_tool_calls"])

                        # Display response if available and event is RunResponse
                        if (
                            resp_chunk.event == "RunResponse"
                            and resp_chunk.content is not None
                        ):
                            response += resp_chunk.content
                            resp_container.markdown(response)
                            
                            # Check for image links in the streamed response
                            import re
                            import os
                            from PIL import Image
                            
                            # Check for sandbox image links
                            sandbox_pattern = r'\[.*?\]\(sandbox:/mnt/data/([a-f0-9\-]+\.(?:png|jpg|jpeg|gif))\)'
                            sandbox_matches = re.findall(sandbox_pattern, response)
                            
                            # Display sandbox images if found
                            for img_filename in sandbox_matches:
                                img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images", img_filename)
                                if os.path.exists(img_path):
                                    try:
                                        img = Image.open(img_path)
                                        # Calculate 50% of the container width
                                        col1, col2 = st.columns([1, 1])
                                        with col1:
                                            st.image(img, caption=f"Generated Image: {img_filename}", use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Error displaying image: {e}")
                            

                    # Add the response to the messages with the accumulated tool calls
                    message_key = f"assistant_{hash(response)}"
                    
                    # Determine which tool calls to use
                    tool_calls_to_use = None
                    if "current_tool_calls" in st.session_state and st.session_state["current_tool_calls"]:
                        # Use the accumulated tool calls from the session state
                        tool_calls_to_use = st.session_state["current_tool_calls"]
                        # Store in persistent storage
                        st.session_state["persistent_tool_calls"][message_key] = tool_calls_to_use
                        # Add the message with tool calls
                        await add_message("assistant", response, tool_calls_to_use)
                        # Clear the current tool calls for the next response
                        st.session_state["current_tool_calls"] = []
                    elif halo.run_response is not None and halo.run_response.tools:
                        # Fallback to using tools from the run_response
                        tool_calls_to_use = halo.run_response.tools
                        # Store in persistent storage
                        st.session_state["persistent_tool_calls"][message_key] = tool_calls_to_use
                        # Add the message with tool calls
                        await add_message("assistant", response, tool_calls_to_use)
                    else:
                        # No tool calls to add
                        await add_message("assistant", response)
                except Exception as e:
                    logger.error(f"Error during agent run: {str(e)}", exc_info=True)
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    await add_message("assistant", error_message)
                    st.error(error_message)

    ####################################################################
    # Knowledge widget
    ####################################################################
    await knowledge_widget(halo)

    ####################################################################
    # Session selector
    ####################################################################
    await session_selector(halo, halo_config)

    ####################################################################
    # About section
    ####################################################################
    await utilities_widget(halo)


async def main():
    await initialize_session_state()
    await header()
    await body()
    await about()
    #await show_scotty()



if __name__ == "__main__":
    asyncio.run(main())

# Footer
st.sidebar.markdown(" ")
st.sidebar.markdown(f"© {config.APP_NAME} | Made with :material/favorite: by [{config.COMPANY}]({config.COMPANY_URL})")
