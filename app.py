from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Make langdetect deterministic (important!)
DetectorFactory.seed = 0

app = Flask(__name__)

def detect_language(text):
    try:
        lang_code = detect(text)
        if lang_code == "fr":
            return "French"
        elif lang_code == "en":
            return "English"
        else:
            return f"Other ({lang_code})"
    except:
        return "Unknown"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]

        # Detect language (offline, free)
        detected_lang = detect_language(text)

        # Always translate to English first
        english = GoogleTranslator(source="auto", target="en").translate(text)

        # Back-translate English → French
        french_back = GoogleTranslator(source="en", target="fr").translate(english)

        return render_template(
            "index.html",
            original=text,
            english=english,
            french_back=french_back,
            detected=detected_lang
        )

    return render_template("index.html")


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True)
