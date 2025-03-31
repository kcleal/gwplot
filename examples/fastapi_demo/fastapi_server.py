"""
This is a demo of using gwplot with FastAPI.

>>> uvicorn fastapi_server:app --reload

Or:

granian --interface asgi --workers 4 --runtime-threads 4 fastapi_server:app

"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Cookie, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
import threading
from gwplot import Gw, GLFW


@dataclass
class GwInstance:
    plot: object
    log: list
    position: str
    last_access: int


# Global variables
gw_instances = defaultdict(GwInstance)
instance_lock = threading.Lock()
root = os.path.abspath(os.path.dirname(__file__)).replace("/examples/fastapi_demo", "")

# Template setup
templates = Jinja2Templates(directory="templates")


def flush_gw_log(session_id):
    if session_id in gw_instances:
        log_output = gw_instances[session_id].plot.flush_log()
        if log_output:
            with instance_lock:
                gw_instances[session_id].log.append(log_output + "\n")


def create_gw_instance(root, width, height):
    """Create a new Gw instance with the provided arguments"""
    fa = root + "/tests/ref.fa"
    plot = Gw(fa, canvas_width=width, canvas_height=height, theme="slate", threads=1)
    plot.add_bam(root + "/tests/small.bam")
    plot.add_track(root + "/tests/test.gff3")
    plot.add_region("chr1", 1, 20000)
    return plot


def cleanup_old_sessions(max_age=3600):
    current_time = time.time()
    to_remove = []
    with instance_lock:
        for session_id, instance in gw_instances.items():
            if current_time - instance.last_access > max_age:
                to_remove.append(session_id)
        for session_id in to_remove:
            if session_id in gw_instances:
                del gw_instances[session_id]


def cleanup_task():
    while True:
        time.sleep(300)
        cleanup_old_sessions()


# Define key mappings to send to GW
keys = {
    'ArrowRight': (GLFW.KEY_RIGHT, GLFW.get_key_scancode(GLFW.KEY_RIGHT), GLFW.PRESS, 0),
    'ArrowLeft': (GLFW.KEY_LEFT, GLFW.get_key_scancode(GLFW.KEY_LEFT), GLFW.PRESS, 0),
    'ArrowUp': (GLFW.KEY_UP, GLFW.get_key_scancode(GLFW.KEY_UP), GLFW.PRESS, 0),
    'ArrowDown': (GLFW.KEY_DOWN, GLFW.get_key_scancode(GLFW.KEY_DOWN), GLFW.PRESS, 0),
    'PageUp': (GLFW.KEY_PAGE_UP, GLFW.get_key_scancode(GLFW.KEY_PAGE_UP), GLFW.PRESS, 0),
    'PageDown': (GLFW.KEY_PAGE_DOWN, GLFW.get_key_scancode(GLFW.KEY_PAGE_DOWN), GLFW.PRESS, 0),
    'left': GLFW.MOUSE_BUTTON_LEFT,
    'right': GLFW.MOUSE_BUTTON_RIGHT,
    'press': GLFW.PRESS,
    'release': GLFW.RELEASE,
    'wheel_down': GLFW.KEY_UP,
    'wheel_up': GLFW.KEY_DOWN,
}


def get_or_create_gw_instance(sid, width=800, height=500):
    """Get existing Gw instance or create a new one for the current websocket session"""
    with instance_lock:
        if sid not in gw_instances:
            plot = create_gw_instance(root, width, height)
            gw_instances[sid] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
        gw_instances[sid].last_access = time.time()
        return gw_instances[sid]


def get_image(sid, quality=80):
    """Generate image and return as base64 data URL"""
    if sid not in gw_instances:
        return None
    plot = gw_instances[sid].plot
    plot.draw()
    flush_gw_log(sid)
    img_data = plot.encode_as_jpeg(quality=quality)
    # img_data = plot.encode_as_png(compression_level=6)
    return img_data


# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()


# Pydantic models for request data
class CanvasSizeUpdate(BaseModel):
    width: int = 800
    height: int = 500
    dpr: float = 1.0


class CommandRequest(BaseModel):
    command: str = ""


class KeyEvent(BaseModel):
    key: str


class MouseEvent(BaseModel):
    x: float
    y: float
    button: str
    action: str = "press"


# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Define response headers middleware for no caching
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Helper function to get or create session ID
async def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    version = int(time.time())
    return templates.TemplateResponse("index.html", {"request": request, "version": version})


@app.post("/update-canvas-size")
async def update_canvas_size(data: CanvasSizeUpdate, session_id: str = Depends(get_session_id)):
    if session_id not in gw_instances:
        plot = create_gw_instance(root)
        gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
    else:
        plot = gw_instances[session_id].plot

    width, height, dpr = data.width, data.height, data.dpr

    # Set the physical pixel dimensions based on container dimensions and DPR
    physical_width = int(width * dpr)
    physical_height = int(height * dpr)

    if dpr > 1.0:
        font_size = min(int(12 * min(dpr, 2.0)), 24)
        plot.set_font_size(font_size)

    # Use the physical dimensions for the actual canvas rendering
    plot.set_canvas_size(physical_width, physical_height)
    flush_gw_log(session_id)
    plot.apply_command("refresh")

    response = JSONResponse({
        "message": "Canvas size updated successfully",
        "width": physical_width,
        "height": physical_height,
        "dpr": dpr
    })

    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/get-output")
async def get_output(session_id: str = Depends(get_session_id)):
    if session_id not in gw_instances:
        plot = create_gw_instance(root)
        gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())

    output = ""
    if session_id in gw_instances:
        with instance_lock:
            output = "".join(gw_instances[session_id].log)

    response = JSONResponse({"output": output})
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.post("/clear-output")
async def clear_output(session_id: str = Depends(get_session_id)):
    if session_id not in gw_instances:
        plot = create_gw_instance(root)
        gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())

    if session_id in gw_instances:
        with instance_lock:
            gw_instances[session_id].log.clear()

    response = JSONResponse({"success": True})
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/session-info")
async def session_info(session_id: str = Depends(get_session_id)):
    """Debug endpoint to view session information"""
    active_sessions = len(gw_instances)

    response = JSONResponse({
        "session_id": session_id,
        "active_sessions": active_sessions
    })

    response.set_cookie(key="session_id", value=session_id)
    return response


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_binary(self, client_id: str, data: bytes, json_data: Dict[str, Any] = None):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_bytes(data)
            if json_data:
                await self.active_connections[client_id].send_json(json_data)

    async def send_json(self, client_id: str, data: Dict[str, Any]):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(data)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    try:
        # Initialize instance and send first image
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            if event_type == "dpr":
                width = data.get("width", 800)
                height = data.get("height", 500)
                dpr = data.get("dpr", 1.0)
                instance = get_or_create_gw_instance(client_id, width * dpr, height * dpr)
                if dpr > 1.0:
                    font_size = min(int(12 * min(dpr, 2.0)), 24)
                    instance.plot.set_font_size(font_size)

                image_data = get_image(client_id)
                await manager.send_binary(client_id, image_data)
                await manager.send_json(client_id, {"log": "".join(instance.log)})

            elif event_type == "key_event":
                key = data.get("key")
                if key in keys:
                    instance = get_or_create_gw_instance(client_id)
                    instance.plot.key_press(*keys[key])
                    flush_gw_log(client_id)
                    if instance.plot.clear_buffer or instance.plot.redraw:
                        image_data = get_image(client_id)
                        await manager.send_binary(client_id, image_data)
                        await manager.send_json(client_id, {"log": "".join(instance.log)})

            elif event_type == "mouse_event":
                x_pos = data.get("x")
                y_pos = data.get("y")
                button = data.get("button")
                action = data.get("action", "press")

                if button in keys and action in keys:
                    instance = get_or_create_gw_instance(client_id)
                    instance.plot.mouse_event(x_pos, y_pos, keys[button], keys[action])
                    flush_gw_log(client_id)

                    if keys[action] == GLFW.RELEASE and (instance.plot.clear_buffer or instance.plot.redraw):
                        image_data = get_image(client_id)
                        await manager.send_binary(client_id, image_data)
                        await manager.send_json(client_id, {"log": "".join(instance.log)})

            elif event_type == "update_canvas_size":
                width = data.get("width", 800)
                height = data.get("height", 500)
                dpr = data.get("dpr", 1.0)
                instance = get_or_create_gw_instance(client_id)
                # Calculate physical dimensions
                physical_width = int(width * dpr)
                physical_height = int(height * dpr)
                if dpr > 1.0:
                    font_size = min(int(12 * min(dpr, 2.0)), 24)
                    instance.plot.set_font_size(font_size)

                # Set the physical dimensions for the actual canvas
                instance.plot.set_canvas_size(physical_width, physical_height)
                flush_gw_log(client_id)
                instance.plot.apply_command("refresh")
                image_data = get_image(client_id)
                await manager.send_binary(client_id, image_data)
                await manager.send_json(client_id, {"log": "".join(instance.log)})

            elif event_type == "command":
                user_input = data.get("command", "")
                instance = get_or_create_gw_instance(client_id)
                instance.plot.apply_command(user_input)
                flush_gw_log(client_id)

                if instance.plot.clear_buffer or instance.plot.redraw:
                    image_data = get_image(client_id)
                    await manager.send_binary(client_id, image_data)
                    await manager.send_json(client_id, {"log": "".join(instance.log)})
                else:
                    await manager.send_json(client_id, {"log": "".join(instance.log)})

            elif event_type == "clear_output":
                instance = get_or_create_gw_instance(client_id)
                with instance_lock:
                    instance.log.clear()
                await manager.send_json(client_id, {"log": ""})

            elif event_type == "refresh_image":
                instance = get_or_create_gw_instance(client_id)
                image_data = get_image(client_id)
                await manager.send_binary(client_id, image_data)
                await manager.send_json(client_id, {"log": "".join(instance.log)})

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)


if __name__ == "__main__":
    pass
