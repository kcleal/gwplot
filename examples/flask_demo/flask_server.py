"""
This is a Flask server hosting GW with individual sessions for each user
>>> python3 flask_server.py

A reference and bam(s) can be supplied as optional arguments:
>>> python3 flask_server.py ref.fa a.bam b.bam

Then open a browser and goto http://127.0.0.1:5000/
"""

from flask import Flask, request, render_template, jsonify, session, send_file
import io
import os
from gwplot import Gw, GLFW
import threading
import sys
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass

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


def create_gw_instance(root, args):
    """Create a new Gw instance with the provided arguments"""
    t0 = time.time()
    if args:
        fa = args[0]
        plot = Gw(fa, canvas_width=1900, canvas_height=600)
        for bam in args[1:]:
            plot.add_bam(bam)
    else:
        fa = root + "/tests/ref.fa"
        plot = Gw(fa, canvas_width=1900, canvas_height=600)
        plot.add_bam(root + "/tests/small.bam")
        plot.add_track(root + "/tests/test.gff3")
        plot.add_region("chr1", 1, 20000)
    print("Initialize time", time.time() - t0)
    return plot


def cleanup_old_sessions(max_age=3600):  # 1 hour timeout to cleanup old sessions
    current_time = time.time()
    to_remove = []
    with instance_lock:
        for session_id, instance in gw_instances.items():
            if current_time - instance.last_access > max_age:
                to_remove.append(session_id)
        for session_id in to_remove:
            if session_id in gw_instances:
                del gw_instances[session_id]


# Schedule cleanup to run periodically
def cleanup_task():
    while True:
        time.sleep(300)  # Check every 5 minutes
        cleanup_old_sessions()


def create_app():
    app = Flask(__name__)
    app.config['VERSION'] = int(time.time())
    app.config['SECRET_KEY'] = os.urandom(24)  # Needed for sessions

    args = sys.argv[1:]

    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

    # Define key mappings to send to GW. Other keys will be handled by the browser
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

    def get_or_create_gw_instance():
        """Get existing Gw instance or create a new one for the current session"""
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        with instance_lock:
            if session_id not in gw_instances:
                plot = create_gw_instance(root, args)
                gw_instances[session_id] = GwInstance(plot=plot, log=[], position="", last_access=time.time())

            return session_id, gw_instances[session_id]

    @app.after_request
    def add_no_cache_headers(response):  # Try to disable caching
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.route('/')
    def home():
        # Initialize session
        get_or_create_gw_instance()
        return render_template('index.html', version=app.config['VERSION'])

    def display_image(session_id):
        t0 = time.time()
        if session_id not in gw_instances:
            return jsonify({"error": "Session not found"})

        plot = gw_instances[session_id].plot
        plot.draw_interactive()
        print("Draw time", time.time() - t0)
        flush_gw_log(session_id)

        img_data = plot.encode_as_png()
        # img_data = plot.encode_as_jpeg(quality=80)  # faster but lower quality

        img_size_kb = len(img_data) / 1024
        img_io = io.BytesIO(img_data)
        img_io.seek(0)
        print("Display time (direct encoding)", time.time() - t0, img_size_kb)
        return send_file(img_io, mimetype='image/png', as_attachment=False)


    @app.route('/display_image')
    def get_display_image():
        session_id, _ = get_or_create_gw_instance()
        return display_image(session_id)

    @app.route('/submit', methods=['POST'])
    def submit():
        session_id, instance = get_or_create_gw_instance()
        plot = instance.plot
        user_input = request.form['user_input']
        plot.apply_command(user_input)
        flush_gw_log(session_id)
        print(f"Session {session_id}: Command entered: {user_input}")
        if plot.clear_buffer or plot.redraw:
            return display_image(session_id)
        return jsonify({'success': True, 'image': None})

    @app.route('/key-event', methods=['POST'])
    def key_event():
        session_id, instance = get_or_create_gw_instance()
        plot = instance.plot
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
        session_id, instance = get_or_create_gw_instance()
        plot = instance.plot
        mouse_data = request.get_json()
        x_pos = mouse_data.get('x')
        y_pos = mouse_data.get('y')
        button = mouse_data.get('button')
        action = mouse_data.get('action', 'press')  # Default to 'press' for backward compatibility
        if button not in keys or action not in keys:
            return jsonify({"error": "Invalid key"})
        plot.mouse_event(x_pos, y_pos, keys[button], keys[action])
        flush_gw_log(session_id)
        if keys[action] == GLFW.RELEASE and (plot.clear_buffer or plot.redraw):
            return display_image(session_id)
        return jsonify({'success': True, 'image': None})

    @app.route('/update-canvas-size', methods=['POST'])
    def update_canvas_size():
        session_id, instance = get_or_create_gw_instance()
        plot = instance.plot
        data = request.get_json()
        width = data.get('width', 800)
        height = data.get('height', 500)
        dpr = data.get('dpr', 1.0)
        if dpr > 1.0:  # Adjust font size based on DPR for high resolution displays
            font_size = min(int(12 * min(dpr, 2.0)), 24)  # Cap at 24pt font
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
        session_id, _ = get_or_create_gw_instance()
        if session_id in gw_instances:
            with instance_lock:
                output = "".join(gw_instances[session_id].log)
            return jsonify({"output": output})
        return jsonify({"output": ""})

    @app.route('/clear-output', methods=['POST'])
    def clear_output():
        session_id, _ = get_or_create_gw_instance()
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
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, threaded=True)
