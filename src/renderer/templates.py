# src/renderer/templates.py

from .bullet import render_bullet_layout
from .flow_horizontal import render_flow_horizontal
from .table import render_table_layout
from .split import render_split_layout
from .composite import render_composite_layout
from .warning_bullet import render_warning_bullet
from .timeline import render_timeline
from .bullet_diagram import render_bullet_diagram   # 이거 추가

LAYOUT_RENDERERS = {
    # 기본 불릿 (세로 step 구조)
    "bullet_layout": render_bullet_layout,

    # 좌→우 흐름
    "flow_horizontal": render_flow_horizontal,

    # 표 비교
    "table_layout": render_table_layout,

    # 좌/우 분할
    "split_layout": render_split_layout,

    # 기여/한계/미래 연구 (3개 병렬)
    "composite_layout": render_composite_layout,
    "composite": render_composite_layout,  # alias

    # 경고 불릿
    "warning_bullet": render_warning_bullet,

    # 타임라인
    "timeline": render_timeline,

    # 불릿 + 다이어그램
    "bullet_diagram": render_bullet_diagram,   # 이거 추가
}



def render_section(section, out_path):
    """
    섹션 dict를 받아서 알맞은 renderer 호출
    section 예시:
    {
      "layout": "bullet_layout",
      "slide_title": "YOLO의 핵심 아이디어",
      "slots": {
        "Step1": "문제점",
        "Step2": "아이디어",
        "Step3": "해결방안"
      }
    }
    """
    layout = section.get("layout", "bullet_layout")
    renderer = LAYOUT_RENDERERS.get(layout)

    if not renderer:
        raise ValueError(f"Unknown layout: {layout}. Available: {list(LAYOUT_RENDERERS.keys())}")

    renderer(section, out_path)
