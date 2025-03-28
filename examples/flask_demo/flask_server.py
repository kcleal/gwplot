# Modified Flask server with WebSockets - Complete version
from flask import Flask, request, render_template, jsonify, session, send_file
from flask_socketio import SocketIO, emit
import io
import os
from gwplot import Gw, GLFW
import threading
import sys
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
import base64

@dataclass
class GwInstance:
    plot: object
    log: list
    position: str
    last_access: int


gw_instances = defaultdict(GwInstance)
instance_lock = threading.Lock()
root = os.path.abspath(os.path.dirname(__file__)).replace("/examples/flask_demo", "")


def flush_gw_log(session_id):
    if session_id in gw_instances:
        log_output = gw_instances[session_id].plot.flush_log()
        if log_output:
            with instance_lock:
                gw_instances[session_id].log.append(log_output + "\n")


def create_gw_instance(root):
    """Create a new Gw instance with the provided arguments"""
    fa = root + "/tests/ref.fa"
    plot = Gw(fa, canvas_width=1900, canvas_height=600, theme="igv")
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


def create_app():
    app = Flask(__name__)
    
    # Create SocketIO instance with threading mode (more compatible than eventlet for testing)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    app.config['VERSION'] = int(time.time())
    app.config['SECRET_KEY'] = os.urandom(24)

    args = sys.argv[1:]

    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

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

    def get_or_create_gw_instance(sid):
        """Get existing Gw instance or create a new one for the current websocket session"""
        with instance_lock:
            if sid not in gw_instances:
                plot = create_gw_instance(root)
                gw_instances[sid] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
            gw_instances[sid].last_access = time.time()
            return gw_instances[sid]

    @app.after_request
    def add_no_cache_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.route('/')
    def home():
        return render_template('index.html', version=app.config['VERSION'])

    def get_image_as_base64(sid, quality=80):
        """Generate image and return as base64 data URL"""
        if sid not in gw_instances:
            return None
        
        plot = gw_instances[sid].plot
        plot.draw()
        flush_gw_log(sid)
        
        # Use JPEG for better network performance
        # try:
        #     img_data = plot.encode_as_jpeg(quality=quality)
        #     img_type = "jpeg"
        # except AttributeError:
        #     # Fallback to PNG if JPEG encoding isn't available
        #     img_data = plot.encode_as_png()
        #     img_type = "png"
        img_data = plot.encode_as_jpeg(quality=quality)
        img_type = "jpeg"
            
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        return f"data:image/{img_type};base64,{img_base64}"

    # Original HTTP endpoints for backward compatibility
    def display_image(session_id):
        t0 = time.time()
        if session_id not in gw_instances:
            return jsonify({"error": "Session not found"})
        plot = gw_instances[session_id].plot
        plot.draw()
        flush_gw_log(session_id)
        
        # Try to use JPEG for better performance
        try:
            img_data = plot.encode_as_jpeg(quality=80)
            mimetype = 'image/jpeg'
        except AttributeError:
            img_data = plot.encode_as_png()
            mimetype = 'image/png'
            
        img_size_kb = len(img_data) / 1024
        img_io = io.BytesIO(img_data)
        img_io.seek(0)
        return send_file(img_io, mimetype=mimetype, as_attachment=False)

    @app.route('/display_image')
    def get_display_image():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        with instance_lock:
            if session_id not in gw_instances:
                plot = create_gw_instance(root)
                gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
        return display_image(session_id)

    @app.route('/submit', methods=['POST'])
    def submit():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        if session_id not in gw_instances:
            plot = create_gw_instance(root)
            gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
        else:
            plot = gw_instances[session_id].plot
            
        user_input = request.form['user_input']
        plot.apply_command(user_input)
        flush_gw_log(session_id)
        print(f"Session {session_id}: Command entered: {user_input}")
        if plot.clear_buffer or plot.redraw:
            return display_image(session_id)
        return jsonify({'success': True, 'image': None})

    @app.route('/key-event', methods=['POST'])
    def key_event():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        if session_id not in gw_instances:
            plot = create_gw_instance(root)
            gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
        else:
            plot = gw_instances[session_id].plot
            
        key_data = request.get_json()
        if key_data['key'] not in keys:
            return jsonify({"error": "Invalid key"})
        plot.key_press(*keys[key_data['key']])
        flush_gw_log(session_id)
        if plot.clear_buffer or plot.redraw:
            return display_image(session_id)
        return jsonify({'success': True, 'image': None})

    @app.route('/mouse-event', methods=['POST'])
    def mouse_event():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        if session_id not in gw_instances:
            plot = create_gw_instance(root)
            gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
        else:
            plot = gw_instances[session_id].plot
            
        mouse_data = request.get_json()
        x_pos = mouse_data.get('x')
        y_pos = mouse_data.get('y')
        button = mouse_data.get('button')
        action = mouse_data.get('action', 'press')
        if button not in keys or action not in keys:
            return jsonify({"error": "Invalid key"})
        plot.mouse_event(x_pos, y_pos, keys[button], keys[action])
        flush_gw_log(session_id)
        if keys[action] == GLFW.RELEASE and (plot.clear_buffer or plot.redraw):
            return display_image(session_id)
        return jsonify({'success': True, 'image': None})

    @app.route('/update-canvas-size', methods=['POST'])
    def update_canvas_size():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        if session_id not in gw_instances:
            plot = create_gw_instance(root)
            gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
        else:
            plot = gw_instances[session_id].plot
            
        data = request.get_json()
        width = data.get('width', 800)
        height = data.get('height', 500)
        dpr = data.get('dpr', 1.0)
        if dpr > 1.0:
            font_size = min(int(12 * min(dpr, 2.0)), 24)
            plot.set_font_size(font_size)
        plot.set_canvas_size(int(width), int(height))
        flush_gw_log(session_id)
        plot.apply_command("refresh")
        return jsonify({
            "message": "Canvas size updated successfully",
            "width": width,
            "height": height,
            "dpr": dpr
        })

    @app.route('/get-output')
    def get_output():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        if session_id not in gw_instances:
            plot = create_gw_instance(root)
            gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
            
        if session_id in gw_instances:
            with instance_lock:
                output = "".join(gw_instances[session_id].log)
            return jsonify({"output": output})
        return jsonify({"output": ""})

    @app.route('/clear-output', methods=['POST'])
    def clear_output():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        if session_id not in gw_instances:
            plot = create_gw_instance(root)
            gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())
            
        if session_id in gw_instances:
            with instance_lock:
                gw_instances[session_id].log.clear()
        return jsonify({"success": True})

    @app.route('/session-info')
    def session_info():
        """Debug endpoint to view session information"""
        session_id = session.get('session_id', 'No session')
        active_sessions = len(gw_instances)
        return jsonify({
            "session_id": session_id,
            "active_sessions": active_sessions
        })
        
    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        sid = request.sid
        instance = get_or_create_gw_instance(sid)
        # Send initial image
        image_data = get_image_as_base64(sid)
        emit('image_update', {'image': image_data, 'log': "".join(instance.log)})

    @socketio.on('key_event')
    def handle_key_event(data):
        sid = request.sid
        instance = get_or_create_gw_instance(sid)
        plot = instance.plot
        
        key = data.get('key')
        if key not in keys:
            return
        
        plot.key_press(*keys[key])
        flush_gw_log(sid)
        
        if plot.clear_buffer or plot.redraw:
            # Determine quality based on interaction state
            quality = 60 if data.get('is_interacting', False) else 80
            image_data = get_image_as_base64(sid, quality)
            emit('image_update', {
                'image': image_data, 
                'log': "".join(instance.log),
                'requestId': data.get('requestId')
            })

    @socketio.on('mouse_event')
    def handle_mouse_event(data):
        sid = request.sid
        instance = get_or_create_gw_instance(sid)
        plot = instance.plot
        
        x_pos = data.get('x')
        y_pos = data.get('y')
        button = data.get('button')
        action = data.get('action', 'press')
        
        if button not in keys or action not in keys:
            return
            
        plot.mouse_event(x_pos, y_pos, keys[button], keys[action])
        flush_gw_log(sid)
        
        is_interacting = data.get('is_interacting', False)
        quality = 60 if is_interacting else 80
        
        if keys[action] == GLFW.RELEASE and (plot.clear_buffer or plot.redraw):
            image_data = get_image_as_base64(sid, quality)
            emit('image_update', {
                'image': image_data, 
                'log': "".join(instance.log),
                'requestId': data.get('requestId')
            })

    @socketio.on('update_canvas_size')
    def handle_canvas_resize(data):
        sid = request.sid
        instance = get_or_create_gw_instance(sid)
        plot = instance.plot
        
        width = data.get('width', 800)
        height = data.get('height', 500)
        dpr = data.get('dpr', 1.0)
        
        if dpr > 1.0:
            font_size = min(int(12 * min(dpr, 2.0)), 24)
            plot.set_font_size(font_size)
            
        plot.set_canvas_size(int(width), int(height))
        flush_gw_log(sid)
        plot.apply_command("refresh")
        
        image_data = get_image_as_base64(sid)
        emit('image_update', {'image': image_data, 'log': "".join(instance.log)})

    @socketio.on('command')
    def handle_command(data):
        sid = request.sid
        instance = get_or_create_gw_instance(sid)
        plot = instance.plot
        
        user_input = data.get('command', '')
        plot.apply_command(user_input)
        flush_gw_log(sid)
        
        if plot.clear_buffer or plot.redraw:
            image_data = get_image_as_base64(sid)
            emit('image_update', {'image': image_data, 'log': "".join(instance.log)})
        else:
            emit('log_update', {'log': "".join(instance.log)})
            
    @socketio.on('clear_output')
    def handle_clear_output():
        sid = request.sid
        if sid in gw_instances:
            with instance_lock:
                gw_instances[sid].log.clear()
            emit('log_update', {'log': ""})
            
    @socketio.on('refresh_image')
    def handle_refresh_image():
        sid = request.sid
        instance = get_or_create_gw_instance(sid)
        image_data = get_image_as_base64(sid)
        emit('image_update', {'image': image_data, 'log': "".join(instance.log)})

    return app, socketio


# This needs to go here if using gunicorn
app, socketio = create_app()

if __name__ == '__main__':
    # Run with threading mode for development
    socketio.run(app, debug=False)