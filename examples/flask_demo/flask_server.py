"""
This is a small demo of how to set up a Flask server hosting GW
>>> python3 flask_server.py

A reference and bam(s) can be supplied as optional arguments:
>>> python3 flask_server.py ref.fa a.bam b.bam

Then open a browser and goto http://127.0.0.1:5000/

If restarting this server, and you find a white screen, either
1. wait a few minutes 2. re-build gwplot 3. use an incognito window
"""

from flask import Flask, request, render_template, jsonify
from PIL import Image
import io
import os
import base64
from gwplot import Gw, GLFW
import threading
import sys
import time


def flush_gw_log(plot, log_lock, log_buffer):
    log_output = plot.flush_log()
    if log_output:
        formatted_log = log_output + "\n"
        with log_lock:
            log_buffer.append(formatted_log)


def create_app():
    app = Flask(__name__)
    app.config['VERSION'] = int(time.time())
    if not GLFW.init():
        raise ValueError('Failed to initialize GLFW')

    # Create a buffer to store log messages
    log_buffer = []
    log_lock = threading.Lock()

    # Initialize Gw plot
    root = os.path.abspath(os.path.dirname(__file__))
    args = sys.argv[1:]
    if args:
        fa = args[0]
        plot = Gw(fa, canvas_width=1900, canvas_height=600)
        for bam in args[1:]:
            plot.add_bam(bam)
    else:
        fa = root + "/../../tests/ref.fa"
        # fa = "hg38"
        plot = Gw(fa, canvas_width=1900, canvas_height=600)
        plot.add_bam(root + "/../../tests/small.bam")
        plot.add_track(root + "/../../tests/test.gff3")
        # plot.add_bam("https://downloads.pacbcloud.com/public/2024Q4/Vega/HG002/Human-WGS-variant-pipeline/HiFi-human-WGS-WDL_v2.0.0-rc4/m21009_241011_231051.GRCh38.haplotagged.bam")
        plot.add_region("chr1", 1, 20000)

    plot.glfw_init()  # Needed for interactivity via keyboard/mouse
    flush_gw_log(plot, log_lock, log_buffer)

    # Define key mappings to send to GW. Other keys will be handled by the browser
    keys = {
        'ArrowRight': (GLFW.KEY_RIGHT, GLFW.get_key_scancode(GLFW.KEY_RIGHT), GLFW.PRESS, 0),
        'ArrowLeft': (GLFW.KEY_LEFT, GLFW.get_key_scancode(GLFW.KEY_LEFT), GLFW.PRESS, 0),
        'ArrowUp': (GLFW.KEY_UP, GLFW.get_key_scancode(GLFW.KEY_UP), GLFW.PRESS, 0),
        'ArrowDown': (GLFW.KEY_DOWN, GLFW.get_key_scancode(GLFW.KEY_DOWN), GLFW.PRESS, 0),
        'PageUp': (GLFW.KEY_PAGE_UP, GLFW.get_key_scancode(GLFW.KEY_PAGE_UP), GLFW.PRESS, 0),
        'PageDown': (GLFW.KEY_PAGE_DOWN, GLFW.get_key_scancode(GLFW.KEY_PAGE_DOWN), GLFW.PRESS, 0)
    }

    @app.route('/')
    def home():
        return render_template('index.html', version=app.config['VERSION'])

    def display_image(clear_buffer=False):
        plot.draw(clear_buffer)
        flush_gw_log(plot, log_lock, log_buffer)
        image = Image.fromarray(plot.array())
        img_io = io.BytesIO()
        image.save(img_io, 'PNG', quality=50)
        img_io.seek(0)
        img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return jsonify(image=f'data:image/png;base64,{img_data}')

    @app.route('/display_image')
    def get_display_image():
        response = display_image()
        return response

    @app.route('/submit', methods=['POST'])
    def submit():
        user_input = request.form['user_input']
        clear_buffer, redraw = plot.apply_command(user_input)
        flush_gw_log(plot, log_lock, log_buffer)
        print("Command entered:", clear_buffer, redraw)
        if clear_buffer or redraw:
            return display_image(clear_buffer)
        else:
            return jsonify({'success': True, 'image': None})

    @app.route('/key-event', methods=['POST'])
    def key_event():
        key_data = request.get_json()
        if key_data['key'] in keys:
            plot.key_press(*keys[key_data['key']])
            flush_gw_log(plot, log_lock, log_buffer)
            return display_image()
        return jsonify({"error": "Invalid key"})

    @app.route('/mouse-event', methods=['POST'])
    def mouse_event():
        mouse_data = request.get_json()
        x_pos = mouse_data.get('x')
        y_pos = mouse_data.get('y')
        button = mouse_data.get('button')
        plot.mouse_event(x_pos, y_pos, button)
        flush_gw_log(plot, log_lock, log_buffer)
        return display_image(clear_buffer=False)

    @app.route('/update-canvas-size', methods=['POST'])
    def update_canvas_size():
        data = request.get_json()
        width = data.get('width', 800)
        height = data.get('height', 500)
        dpr = data.get('dpr', 1.0)
        if dpr > 1.0:  # Adjust font size based on DPR for high resolution displays
            font_size = min(int(12 * min(dpr, 2.0)), 24)  # Cap at 24pt font
            plot.set_font_size(font_size)
        plot.set_canvas_size(int(width), int(height))
        flush_gw_log(plot, log_lock, log_buffer)
        return jsonify({
            "message": "Canvas size updated successfully",
            "width": width,
            "height": height,
            "dpr": dpr
        })

    @app.route('/get-output')
    def get_output():
        with log_lock:
            output = "".join(log_buffer)
        return jsonify({"output": output})

    @app.route('/clear-output', methods=['POST'])
    def clear_output():
        with log_lock:
            log_buffer.clear()
        return jsonify({"success": True})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
    GLFW.terminate()
