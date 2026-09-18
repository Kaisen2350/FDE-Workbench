"""Enterprise platform adapters for agent specifications."""

from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.adapters.gemini_adapter import GeminiEnterpriseAdapter
from fde_workbench.domain.adapters.openai_adapter import OpenAIAdapter
from fde_workbench.domain.adapters.microsoft_adapter import MicrosoftAdapter
from fde_workbench.domain.adapters.databricks_adapter import DatabricksAdapter

ADAPTERS = {
    "gemini": GeminiEnterpriseAdapter(),
    "openai": OpenAIAdapter(),
    "microsoft": MicrosoftAdapter(),
    "databricks": DatabricksAdapter(),
}

__all__ = [
    "PlatformAdapter",
    "GeminiEnterpriseAdapter",
    "OpenAIAdapter",
    "MicrosoftAdapter",
    "DatabricksAdapter",
    "ADAPTERS",
]
