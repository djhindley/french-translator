from flask import Flask, render_template, request, send_from_directory
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory, LangDetectException
import os

LANGUAGE_NAMES = {
"en": "English",
"fr": "French",
"de": "German",
"es": "Spanish",
"it": "Italian",
"nl": "Dutch",
"pt": "Portuguese",
}

SUPPORTED_LANGS = {
    "fr": "fr",
    "de": "de",
    "es": "es",
    "it": "it",
    "nl": "nl",
    "pt": "pt",
    "sv": "sv",
    "pl": "pl",
    "en": "en"
}



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

        # 1️⃣ Read form inputs
        text = request.form["text"]
        base_lang = request.form.get("base_lang", "en")
        learning_lang = request.form.get("learning_lang", "fr")
        mode = request.form.get("mode", "mode1")

        # 2️⃣ TRANSLATION LOGIC (THIS IS STEP 3.3)
        english = None
        back_translation = None
        original_text = text

        if mode == "mode1":
            # Learning → Base → Learning
            base_text = GoogleTranslator(
                source=learning_lang,
                target=base_lang
            ).translate(text)

            back_translation = GoogleTranslator(
                source=base_lang,
                target=learning_lang
            ).translate(base_text)

            english = base_text

        elif mode == "mode2":
            # Base → Learning
            learning_text = GoogleTranslator(
                source=base_lang,
                target=learning_lang
            ).translate(text)

            english = learning_text

        # 3️⃣ Return HTML
        print("DEBUG MODE =", mode)

        return render_template(
            "index.html",
            original=original_text,
            english=english,
            back_translation=back_translation,
            base_lang_name=LANGUAGE_NAMES.get(base_lang),
            learning_lang_name=LANGUAGE_NAMES.get(learning_lang),
            mode=mode
        )

    # GET request (initial page load)
    return render_template(
        "index.html",
        base_lang_name=LANGUAGE_NAMES.get("en"),
        learning_lang_name=LANGUAGE_NAMES.get("fr"),
        mode="mode1"
    )


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(app.root_path), 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(os.path.join(app.root_path), 'service-worker.js')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

