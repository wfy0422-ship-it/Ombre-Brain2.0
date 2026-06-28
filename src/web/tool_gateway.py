"""
薄网关：让 Node.js 中间层通过 /api/tool 调用 MCP 工具
只做三件事：鉴权、参数校验、调 dispatch
"""
import logging
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request
from web._shared import require_auth

from tools import (
    hold as _t_hold,
    breath as _t_breath,
    trace as _t_trace,
    dream as _t_dream,
    anchor as _t_anchor,
    plan as _t_plan,
    i as _t_i,
    grow as _t_grow,
)

logger = logging.getLogger("ombre_brain")

TOOL_MAP = {
    "hold": _t_hold.dispatch,
    "breath": _t_breath.dispatch,
    "trace": _t_trace.dispatch,
    "dream": _t_dream.dispatch,
    "anchor": _t_anchor.anchor_set,
    "release": _t_anchor.anchor_release,
    "pulse": _t_anchor.pulse,
    "plan": _t_plan.plan_create,
    "letter_write": _t_plan.letter_write,
    "letter_read": _t_plan.letter_read,
    "I": _t_i.dispatch,
    "grow": _t_grow.dispatch,
}

@require_auth
async def _api_tool(request: Request):
    try:
        body = await request.json()
    except:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    name = body.get("name") or body.get("tool")
    args = body.get("arguments") or body.get("args") or {}

    if not name:
        return JSONResponse({"error": "Missing 'name'"}, status_code=400)

    # 断言 + 日志（方便未来排错）
    assert name in TOOL_MAP, f"未知工具: {name}"
    logger.info(f"[tool] 调用 {name}, args: {list(args.keys())}")

    func = TOOL_MAP[name]
    try:
        result = await func(**args)
    except Exception as e:
        logger.error(f"[tool] {name} 执行失败: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"result": result})

def register(mcp):
    app = getattr(mcp, "_app", None) or getattr(mcp, "app", None)
    if app is None:
        raise RuntimeError("无法获取 MCP app")
    app.routes.append(Route("/api/tool", _api_tool, methods=["POST"]))
    print("✅ [tool_gateway] /api/tool 已挂载")