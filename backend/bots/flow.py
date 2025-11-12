"""Flow-based bot implementation for ITM Help Desk."""

from functools import partial
from typing import Dict
import sys
import uuid
import random

from dotenv import load_dotenv
from loguru import logger

from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIProcessor
from pipecat_flows import FlowArgs, FlowManager, FlowResult
from pipecat_flows.types import ContextStrategy, ContextStrategyConfig

from bots.base_bot import BaseBot
from config.bot import BotConfig
from prompts import (
    get_greeting_and_consent_prompt,
    get_identification_prompt,
    get_problem_description_prompt,
    get_ticket_result_prompt,
    get_close_call_prompt,
)

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


# ==============================================================================
# Node Configurations
# ==============================================================================


def create_greeting_and_consent_node() -> Dict:
    """# Node 1: Greeting and Recording Consent Node"""
    return {
        **get_greeting_and_consent_prompt(),
        "functions": [
            {
                "function_declarations": [
                    {
                        "name": "collect_recording_consent",
                        "description": "Registrar si el usuario consiente que se grabe la llamada",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recording_consent": {
                                    "type": "boolean",
                                    "description": "True if the user consents to being recorded, False otherwise",
                                }
                            },
                            "required": ["recording_consent"],
                        },
                        "handler": collect_recording_consent,
                        "transition_callback": handle_recording_consent,
                    }
                ]
            }
        ],
    }


def create_identification_node() -> Dict:
    """# Node 2: Collect Name and ID Node"""
    return {
        **get_identification_prompt(),
        "functions": [
            {
                "function_declarations": [
                    {
                        "name": "collect_identification",
                        "description": "Recopilar el nombre completo y el número de documento del usuario",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "id_number": {"type": "string"},
                            },
                            "required": ["name", "id_number"],
                        },
                        "handler": collect_identification,
                        "transition_callback": handle_identification,
                    }
                ]
            }
        ],
    }


def create_problem_description_node(user_name: str = None) -> Dict:
    """# Node 3: Problem Description Node"""
    return {
        **get_problem_description_prompt(user_name),
        "functions": [
            {
                "function_declarations": [
                    {
                        "name": "offer_ticket_creation",
                        "handler": offer_ticket_creation,
                        "description": "Ofrecer la creación de un ticket de soporte después de escuchar el problema del usuario",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "problem_description": {"type": "string"},
                            },
                            "required": ["problem_description"],
                        },
                        "transition_callback": handle_problem_description,
                    }
                ]
            }
        ],
    }

def create_ticket_result_node(user_name: str = None) -> Dict:
    """# Node 4: Ticket Creation Result Node"""
    return {
        **get_ticket_result_prompt(user_name),
        "functions": [
            {
                "function_declarations": [
                    {
                        "name": "confirm_ticket_creation",
                        "handler": confirm_ticket_creation,
                        "description": "Confirmar si el usuario desea crear un ticket y generar un número de ticket si es así.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "create_ticket": {"type": "boolean"},
                            },
                            "required": ["create_ticket"],
                        },
                        "transition_callback": handle_ticket_result,
                    }
                ]
            }
        ],
    }


def create_close_call_node(user_name: str = None) -> Dict:
    """# Node 5: Final Close Node"""
    return {
        **get_close_call_prompt(user_name),
        "functions": [],
        "post_actions": [{"type": "end_conversation"}],
    }


# ==============================================================================
# Function Handlers
# ==============================================================================


async def collect_recording_consent(args: FlowArgs) -> FlowResult:
    """Process recording consent collection."""
    return {"recording_consent": args["recording_consent"]}


async def collect_identification(args: FlowArgs) -> FlowResult:
    """Collect user's name and ID number."""
    return {"name": args.get("name"), "id_number": args.get("id_number")}


async def offer_ticket_creation(args: FlowArgs) -> FlowResult:
    """Process problem description."""
    return {"problem_description": args.get("problem_description")}

async def confirm_ticket_creation(args: FlowArgs) -> FlowResult:
    """Process ticket creation confirmation."""
    if args.get("create_ticket"):
        ticket_number = random.randint(10000, 99999)
        return {"create_ticket": True, "ticket_number": ticket_number}
    return {"create_ticket": False}


# ==============================================================================
# Transition Callbacks
# ==============================================================================


async def handle_recording_consent(args: Dict, flow_manager: FlowManager):
    """Handle transition after collecting recording consent."""
    flow_manager.state.update(args)
    if args["recording_consent"]:
        await flow_manager.set_node("identification", create_identification_node())
    else:
        await flow_manager.set_node("close_call", create_close_call_node())


async def handle_identification(args: Dict, flow_manager: FlowManager):
    """Handle transition after collecting user's name and ID."""
    flow_manager.state.update(args)
    name = flow_manager.state.get("name")
    await flow_manager.set_node("problem_description", create_problem_description_node(name))


async def handle_problem_description(args: Dict, flow_manager: FlowManager):
    """Handle transition after collecting problem description."""
    flow_manager.state.update(args)
    name = flow_manager.state.get("name")
    await flow_manager.set_node("ticket_result", create_ticket_result_node(name))

async def handle_ticket_result(args: Dict, flow_manager: FlowManager):
    """Handle transition after ticket creation result."""
    flow_manager.state.update(args)
    name = flow_manager.state.get("name")
    await flow_manager.set_node("close_call", create_close_call_node(name))


# ==============================================================================
# Bot Implementation
# ==============================================================================


class FlowBot(BaseBot):
    """Flow-based bot implementation for ITM Help Desk."""

    def __init__(self, config: BotConfig):
        super().__init__(config)
        self.flow_manager = None

    async def _handle_first_participant(self):
        """Handle first participant by initializing flow manager."""
        self.flow_manager = FlowManager(
            task=self.task,
            llm=self.llm,
            tts=self.tts,
            context_aggregator=self.context_aggregator,
            context_strategy=ContextStrategyConfig(strategy=ContextStrategy.RESET),
        )

        # Initialize flow
        await self.flow_manager.initialize()
        await self.flow_manager.set_node("greeting_and_consent", create_greeting_and_consent_node())