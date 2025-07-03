from flask import Flask, render_template_string, request, redirect, Response, url_for
import cv2
import serial
import serial.tools.list_ports
import threading

try:
    from robot_hat import Motor, PWM, Pin
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False

app = Flask(__name__)

# ==========================
# Camera Feed
# ==========================
def gen_frames():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise ValueError("Camera not accessible")
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\nCamera not accessible: ' + str(e).encode() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ==========================
# Serial Port
# ==========================
@app.route('/serial', methods=['GET', 'POST'])
def serial_terminal():
    output = ""
    if request.method == 'POST':
        port = request.form['port']
        baud = int(request.form['baudrate'])
        try:
            with serial.Serial(port, baud, timeout=1) as ser:
                ser.write(b'Test\r\n')
                output = ser.readline().decode(errors='ignore')
        except Exception as e:
            output = f"[!] Error: {str(e)}"
    ports = serial.tools.list_ports.comports()
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Serial Terminal</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
        </head>
        <body class="container mt-5">
            <h2>Serial Terminal</h2>
            <form method='POST' class="mb-3">
                <div class="mb-3">
                    <label class="form-label">Port:</label>
                    <select name='port' class="form-select">
                    {% for p in ports %}
                        <option value='{{ p.device }}'>{{ p.device }} - {{ p.description }}</option>
                    {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Baudrate:</label>
                    <input type='text' name='baudrate' value='115200' class="form-control">
                </div>
                <button type='submit' class="btn btn-primary">Connect</button>
                <a href='/' class="btn btn-secondary">Back</a>
            </form>
            <pre>{{ output }}</pre>
        </body>
        </html>
    """, ports=ports, output=output)

# ==========================
# Motor Control
# ==========================
if MOTOR_AVAILABLE:
    motor_right = Motor(PWM('P12'), Pin('D4'))
    motor_left = Motor(PWM('P13'), Pin('D5'))

    def move(forward=True):
        motor_right.speed(50 if forward else -50)
        motor_left.speed(-50 if forward else 50)

    def turn(right=True):
        motor_right.speed(-50 if right else 50)
        motor_left.speed(-50 if right else 50)

    def stop():
        motor_right.speed(0)
        motor_left.speed(0)

@app.route('/motor/<action>')
def motor_control(action):
    if not MOTOR_AVAILABLE:
        return "Motor control unavailable"
    if action == 'forward':
        move(True)
    elif action == 'backward':
        move(False)
    elif action == 'left':
        turn(False)
    elif action == 'right':
        turn(True)
    elif action == 'stop':
        stop()
    return redirect(url_for('index'))

# ==========================
# Home Page
# ==========================
@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tengu Vanguard Operator Control</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
        </head>
        <body class="bg-light">
            <div class="container py-4">
                <h1 class="mb-4">Tengu Vanguard Operator Control</h1>

                <h3>Camera Feed</h3>
                <img src="{{ url_for('video_feed') }}" class="img-fluid border" width="640" height="480"><br><br>

                <h3>Motor Control</h3>
                {% if motor %}
                    <div class="btn-group mb-4" role="group">
                        <a href='/motor/forward' class="btn btn-success">Forward</a>
                        <a href='/motor/backward' class="btn btn-danger">Backward</a>
                        <a href='/motor/left' class="btn btn-warning">Left</a>
                        <a href='/motor/right' class="btn btn-warning">Right</a>
                        <a href='/motor/stop' class="btn btn-secondary">Stop</a>
                    </div>
                {% else %}
                    <p class="text-danger">[!] Motor Hat not detected.</p>
                {% endif %}

                <h3>Serial Tools</h3>
                <a href='/serial' class="btn btn-info">Open Serial Terminal</a>
            </div>
        </body>
        </html>
    """, motor=MOTOR_AVAILABLE)

# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
# This will run the Flask app on all interfaces at port 5000
# Make sure to run this script with appropriate permissions to access the camera and serial ports.