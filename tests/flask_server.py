from flask import Flask, send_file, request, render_template_string
from PIL import Image
import io
import os
from gwplot import Gw, GwPaint


app = Flask(__name__)


root = os.path.abspath(os.path.dirname(__file__))
fa = root + "/ref.fa"
plot = Gw(fa, width=1000, height=500)
plot.add_bam(root + "/small.bam")
plot.add_region("chr1", 1, 20000)


@app.route('/')
def home():
    # HTML template for displaying the image and the form
    html = '''
    <img src="{{ url_for('display_image') }}" alt="Genome Plot">
    <form action="/submit" method="post">
        <input type="text" name="user_input" placeholder="Enter your text here">
        <input type="submit" value="Submit">
    </form>
    '''
    return render_template_string(html)


@app.route('/display_image')
def display_image():
    plot.draw()
    image = Image.fromarray(plot.array())  # Ensure this conversion is correct
    img_io = io.BytesIO()
    image.save(img_io, 'PNG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']
    plot.apply_command(user_input)
    return home()


if __name__ == '__main__':
    app.run(debug=True)