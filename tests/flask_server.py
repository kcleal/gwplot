"""
This is a small demo of how to set up a Flask server hosting GW

A reference and bam(s) can be supplied as optional arguments:

    python3 flask_server.py ref.fa a.bam b.bam

Then open a browser and goto http://127.0.0.1:5000/
"""

from flask import Flask, send_file, request, render_template_string, jsonify
from PIL import Image
import io
import os
import sys
import base64
from gwplot import Gw, GwPaint
import glfw

if not glfw.init():
    raise ValueError('Failed to initialize GLFW')


app = Flask(__name__)


root = os.path.abspath(os.path.dirname(__file__))
args = sys.argv[1:]
if args:
    fa = args[0]
    plot = Gw(fa, width=1900, height=600)
    for bam in args[1:]:
        plot.add_bam(bam)

else:
    fa = root + "/ref.fa"
    plot = Gw(fa, width=1900, height=600)
    plot.add_bam(root + "/small.bam")
    plot.add_region("chr1", 1, 20000)


keys = {'ArrowRight': (glfw.KEY_RIGHT, glfw.get_key_scancode(glfw.KEY_RIGHT), glfw.PRESS, 0),
        'ArrowLeft': (glfw.KEY_LEFT, glfw.get_key_scancode(glfw.KEY_LEFT), glfw.PRESS, 0),
        'ArrowUp': (glfw.KEY_UP, glfw.get_key_scancode(glfw.KEY_DOWN), glfw.PRESS, 0),
        'ArrowDown': (glfw.KEY_DOWN, glfw.get_key_scancode(glfw.KEY_DOWN), glfw.PRESS, 0)
        }


@app.route('/')
def home():
    # HTML and JavaScript should be well-formed and correctly embedded
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GW server demo</title>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.body.style.backgroundColor = "black";
        });
    </script>
    </head>
    
    <body>
    
    <canvas id="genomePlot" width="950" height="300"></canvas>
    <form id="commandForm">
        <input type="text" name="user_input" placeholder="Enter GW command here" value="chr1">
        <input type="submit" value="Submit">
    </form>
    <script>
        
        document.getElementById('commandForm').onsubmit = function(event) {
            event.preventDefault();
            var userInput = document.getElementsByName('user_input')[0].value;
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'user_input=' + encodeURIComponent(userInput)
            })
            .then(response => response.json())
            .then(data => {
                updateCanvas(data.image);
            })
            .catch(error => console.error('Error:', error));
        };
        
        function resizeCanvas() {
            console.log(window.innerWidth);
            var canvas = document.getElementById('genomePlot');
            canvas.width = window.innerWidth - 10;
            canvas.height = 500;
            updateCanvas();
        }
    
        function loadImage() {
            fetch('/display_image')
                .then(response => response.json())
                .then(data => {
                    updateCanvas(data.image);
                })
                .catch(error => console.error('Error loading initial image:', error));
        }
    
        function updateCanvas(imageData) {

            var canvas = document.getElementById('genomePlot');
            
            canvas.style.imageRendering = 'pixelated';
            var ctx = canvas.getContext('2d');
            ctx.imageSmoothingEnabled = false;
            ctx.mozImageSmoothingEnabled = false;    // For older Firefox versions
            ctx.webkitImageSmoothingEnabled = false; // For older Safari/Chrome versions
            ctx.msImageSmoothingEnabled = false;

            var img = new Image();
            img.onload = function() {
                ctx.clearRect(0, 0, img.width, img.height);
                ctx.drawImage(img, 0, 0, img.width, img.height);
            };
            img.onerror = function(e) {
                console.error("Error loading image onto canvas:", e);
            };
            if (imageData) {
                img.src = imageData;
            } else {
                console.log("No image data provided to updateCanvas.");
            }
        }
    
        document.addEventListener('DOMContentLoaded', function() {

            //loadImage();
            
            const canvas = document.getElementById('genomePlot');
            const resizeCanvas = () => {
                canvas.width = window.innerWidth - 15;
                canvas.height = 500;
                sendCanvasSizeToServer(canvas.width, canvas.height);
            };
        
            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();
        
            function sendCanvasSizeToServer(width, height) {
                fetch('/update-canvas-size', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ width: width, height: height })
                })
                .then(response => response.json())
                .then(data => console.log('Server responded:', data))
                .catch(error => console.error('Error sending canvas size:', error));
            }
        });
        
        // window.addEventListener('resize', resizeCanvas);
        
        let lastTimeKeyPressed = 0;
        const throttleDuration = 100; // Minimum time between events in milliseconds
        
        document.addEventListener('keydown', function(event) {
            const now = new Date().getTime();
            if (now - lastTimeKeyPressed >= throttleDuration) {
                lastTimeKeyPressed = now;
                const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
                if (arrowKeys.includes(event.key)) {
                    console.log("Arrow key pressed:", event.key);
                    sendKeyToServer(event.key);
                }
            }
        });
        
        function sendKeyToServer(key) {
            fetch('/key-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key: key })
            })
            .then(response => response.json())
            .then(data => {
                if (data.image && data.image !== '') {
                    updateCanvas(data.image);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    </script>
    
    </body>
    </html>
    '''
    return render_template_string(html)


def display_image():
    plot.draw()
    image = Image.fromarray(plot.array())
    img_io = io.BytesIO()
    image.save(img_io, 'PNG', quality=50)
    img_io.seek(0)
    img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return jsonify(image=f'data:image/png;base64,{img_data}')


@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']
    plot.apply_command(user_input)
    return display_image()


@app.route('/key-event', methods=['POST'])
def key_event():
    key_data = request.get_json()
    if key_data['key'] in keys:
        plot.key_press(*keys[key_data['key']])
        return display_image()
    return ""

@app.route('/update-canvas-size', methods=['POST'])
def update_canvas_size():
    data = request.get_json()
    width = data['width']
    height = data['height']
    print('update window size ', width, height)
    plot.set_canvas_width(int(width))
    plot.set_canvas_height(int(height))
    return jsonify({"message": "Canvas size updated successfully"})


if __name__ == '__main__':
    app.run(debug=True)
