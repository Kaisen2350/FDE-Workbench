"""Enterprise platform adapters for agent specifications."""

from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.adapters.gemini_adapter import GeminiEnterpriseAdapter
from fde_workbench.domain.adapters.openai_adapter import OpenAIAdapter
from fde_workbench.domain.adapters.microsoft_adapter import MicrosoftAdapter
from fde_workbench.domain.adapters.databricks_adapter import DatabricksAdapter

_gemini = GeminiEnterpriseAdapter()
_openai = OpenAIAdapter()
_microsoft = MicrosoftAdapter()
_databricks = DatabricksAdapter()

ADAPTERS = {
    "gemini": _gemini,
    "gemini_enterprise": _gemini,
    "openai": _openai,
    "openai_assistants": _openai,
    "microsoft": _microsoft,
    "azure": _microsoft,
    "microsoft_azure_ai_foundry": _microsoft,
    "databricks": _databricks,
    "databricks_mosaic_ai": _databricks,
}

__all__ = [
    "PlatformAdapter",
    "GeminiEnterpriseAdapter",
    "OpenAIAdapter",
    "MicrosoftAdapter",
    "DatabricksAdapter",
    "ADAPTERS",
]
