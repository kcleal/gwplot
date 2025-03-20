"""
This is a small demo of how to set up a Flask server hosting GW

A reference and bam(s) can be supplied as optional arguments:

    python3 flask_server.py ref.fa a.bam b.bam

Then open a browser and goto http://127.0.0.1:5000/
"""

from flask import Flask, request, render_template, jsonify
from PIL import Image
import io
import os
import sys
import base64
from gwplot import Gw, GwPaint
import glfw
import threading


def create_app():
    # Initialize Flask
    app = Flask(__name__)

    if not glfw.init():
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

    # Get any initial log output
    initial_log = plot.flush_log()
    if initial_log:
        with log_lock:
            log_buffer.append(initial_log + "\n")

    # Define key mappings
    keys = {
        'ArrowRight': (glfw.KEY_RIGHT, glfw.get_key_scancode(glfw.KEY_RIGHT), glfw.PRESS, 0),
        'ArrowLeft': (glfw.KEY_LEFT, glfw.get_key_scancode(glfw.KEY_LEFT), glfw.PRESS, 0),
        'ArrowUp': (glfw.KEY_UP, glfw.get_key_scancode(glfw.KEY_DOWN), glfw.PRESS, 0),
        'ArrowDown': (glfw.KEY_DOWN, glfw.get_key_scancode(glfw.KEY_DOWN), glfw.PRESS, 0)
    }


    @app.route('/')
    def home():
        return render_template('index.html')


    def display_image(clear_buffer=True):
        plot.draw(clear_buffer)
        # Capture any log output generated during draw
        log_output = plot.flush_log()
        if log_output:
            formatted_log = log_output + "\n"
            with log_lock:
                log_buffer.append(formatted_log)
                # Keep buffer at a reasonable size
                while len(''.join(log_buffer)) > 10000:  # Limit to ~10KB
                    log_buffer.pop(0)

        image = Image.fromarray(plot.array())
        img_io = io.BytesIO()
        image.save(img_io, 'PNG', quality=50)
        img_io.seek(0)
        img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return jsonify(image=f'data:image/png;base64,{img_data}')


    @app.route('/display_image')
    def get_display_image():
        return display_image()


    @app.route('/submit', methods=['POST'])
    def submit():
        user_input = request.form['user_input']
        plot.apply_command(user_input)
        # Capture log output from the command
        log_output = plot.flush_log()
        if log_output:
            formatted_log = log_output + "\n"
            with log_lock:
                log_buffer.append(formatted_log)
        return display_image()


    @app.route('/key-event', methods=['POST'])
    def key_event():
        key_data = request.get_json()
        if key_data['key'] in keys:
            plot.key_press(*keys[key_data['key']])
            # Capture log output from the key press
            log_output = plot.flush_log()
            if log_output:
                formatted_log = log_output  + "\n"
                with log_lock:
                    log_buffer.append(formatted_log)
            return display_image()
        return jsonify({"error": "Invalid key"})


    @app.route('/update-canvas-size', methods=['POST'])
    def update_canvas_size():
        data = request.get_json()
        width = data.get('width', 800)
        height = data.get('height', 500)
        dpr = data.get('dpr', 1.0)

        # Adjust font size based on DPR for high resolution displays
        if dpr > 1.0:
            font_size = min(int(12 * min(dpr, 2.0)), 24)  # Cap at 24pt font
            plot.set_font_size(font_size)
            print(f'Setting font size to {font_size} for DPR {dpr}')

        # Log info about the canvas size request
        print(f'Update canvas size: {width}x{height}, DPR: {dpr}')

        # Set canvas size on the plot object
        plot.set_canvas_size(int(width), int(height))

        # Capture any log output
        log_output = plot.flush_log()
        if log_output:
            formatted_log = log_output + "\n"
            with log_lock:
                log_buffer.append(formatted_log)

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


    @app.route('/mouse-event', methods=['POST'])
    def mouse_event():
        mouse_data = request.get_json()
        x_pos = mouse_data.get('x')
        y_pos = mouse_data.get('y')
        button = mouse_data.get('button')

        # Log the mouse event for debugging
        print(f'Mouse event: x={x_pos}, y={y_pos}, button={button}')

        # Call the mouse_event function in gwplot
        plot.mouse_event(x_pos, y_pos, button)

        # Capture log output from the mouse event
        log_output = plot.flush_log()
        if log_output:
            formatted_log = log_output + "\n"
            with log_lock:
                log_buffer.append(formatted_log)

        return display_image(clear_buffer=False)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
    glfw.terminate()
