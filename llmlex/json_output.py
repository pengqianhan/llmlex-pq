"""
使用结构化输出生成混合自动机 JSON
使用 Pydantic 模型定义 JSON schema，让 LLM 生成符合 json_readme.md 格式的输出
"""
import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any
import json

load_dotenv()

# ============ Pydantic 模型定义（符合 json_readme.md 格式）============

class ModeDefinition(BaseModel):
    """Define a single mode"""
    id: int = Field(description="Mode ID, integer")
    eq: str = Field(description="ODE of each variable in the mode, separated by commas. Example: 'x1[1] = 1, x2[2] = -3 * x2[1] - 25 * x2[0] + 25'. The left side of the equal sign is the highest order derivative, the right side is the expression")

class EdgeTransition(BaseModel):
    """Define transition edges between modes (no reset field)"""
    direction: str = Field(description="Transition direction, format 'u -> v', from mode u to mode v")
    condition: str = Field(description="Transition condition (guard), cannot contain variables not defined in var. Example: 'x1 >= 5'")

class AutomationStructure(BaseModel):
    """Core structure of the hybrid automaton (Note: key name is 'automation' not 'automaton')"""
    var: str = Field(description="Variable list, separated by commas, example: 'x1, x2'")
    input: str = Field(description="Input variable list, separated by commas, example: 'u1, u2'")
    mode: List[ModeDefinition] = Field(description="List of automaton modes")
    edge: List[EdgeTransition] = Field(description="List of transition edges between modes")

class ConfigSettings(BaseModel):
    """Configuration parameters for fitting the difference equation"""
    dt: float = Field(default=0.001, description="Discrete time, default 0.001")
    total_time: float = Field(default=10.0, description="Sampling total time, default 10")
    dim: int = Field(default=3, description="Dimension of the difference equation, default 3")
    # window_size: int = Field(default=10, description="Sliding window size, default 10")
    # clustering_method: str = Field(default="fit", description="Clustering method, default fit, options are fit and dis")
    # minus: bool = Field(default=False, description="Whether to minimize order, default false")
    # need_bias: bool = Field(default=True, description="Whether to include constant term, default true")
    # kernel: str = Field(default="linear", description="SVM kernel function, default linear")
    # other_items: str = Field(default="", description="Other nonlinear or cross terms for the difference equation, default empty")

class HybridAutomatonJSON(BaseModel):
    """Complete hybrid automaton JSON structure"""
    automation: AutomationStructure = Field(description="Automaton structure")
    init_state: List[Dict[str, Any]] = Field(description="Initial state list, each state contains mode and initial values of each variable")
    config: ConfigSettings = Field(description="Configuration parameters for fitting the difference equation")

# __all__ = ['HybridAutomatonJSON']