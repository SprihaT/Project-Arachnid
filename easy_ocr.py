import cv2
import easyocr
from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

reader = easyocr.Reader(['en', 'fr', 'es'])  # English, French, Spanish

latest_text = ""

# Defining keywords commonly found on road signs
road_sign_keywords = ['STOP', 'YIELD', 'SPEED', 'LIMIT', 'EXIT', 'PARKING', 'DO NOT', 'TURN', 'ONE WAY']

def ocr_loop():
    global latest_text
    cap = cv2.VideoCapture(0)  # Accessing webcam

    if not cap.isOpened():
        print("Cannot open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = reader.readtext(gray)

        words = [item[1] for item in result]
        flat_text = " ".join(words).replace("\n", " ")

        # Checking for road sign words
        detected_signs = [word for word in words if any(keyword in word.upper() for keyword in road_sign_keywords)]
        if detected_signs:
            latest_text = f"Road Sign Detected: {' '.join(detected_signs)}"
        else:
            latest_text = flat_text

        time.sleep(1)

@app.route("/text")
def get_text():
    return jsonify(latest_text)

threading.Thread(target=ocr_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
