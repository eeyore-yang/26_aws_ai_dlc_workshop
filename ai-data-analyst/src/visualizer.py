"""chart_type 기반 Plotly 차트 생성."""
from typing import Literal
import pandas as pd, plotly.graph_objects as go

ChartType = Literal["bar", "line", "pie"]

def build_chart(df: pd.DataFrame, chart_type: ChartType) -> go.Figure:
    raise NotImplementedError

def _build_bar(df: pd.DataFrame) -> go.Figure:
    raise NotImplementedError

def _build_line(df: pd.DataFrame) -> go.Figure:
    raise NotImplementedError

def _build_pie(df: pd.DataFrame) -> go.Figure:
    raise NotImplementedError
