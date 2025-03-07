from flask import Flask, render_template, request
from googletrans import Translator, LANGUAGES
from textSummary import summarizer
from gramformer import Gramformer
import torch
from gtts import gTTS
import os
from datetime import datetime
import nltk 
from nltk.tokenize import sent_tokenize

app = Flask(__name__)

# ====================== Set up Gramformer ========================= 
def set_seed(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(1212)

gf = Gramformer(models=1, use_gpu=False) 


@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ""
    original_text = ""
    len_orig_text = 0
    len_summary = 0
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        summary, original_text, len_orig_text, len_summary = summarizer(rawtext)
    return render_template('index.html', summary=summary, original_text=original_text, len_orig_text=len_orig_text, len_summary=len_summary)

# ====================== Translation ========================= 

@app.route('/translator', methods=['GET', 'POST'])
def translator():
    rawtext = ""
    translated_paragraph = ""
    target_language = ""
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        target_language = request.form['target_language']
        if target_language:
            translated_paragraph = translate_text(rawtext, target_language)
    return render_template('translator.html', rawtext=rawtext, translated_paragraph=translated_paragraph, target_language=target_language, LANGUAGES=LANGUAGES)




def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text

# ====================== Grammer Checker ========================= 

@app.route('/grammerChecker', methods=['GET', 'POST'])
def grammerChecker():
    rawtext = ""
    corrected_paragraph = ""  # Initialize with an empty string
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        corrected_paragraph = correct_grammar(rawtext)
        print("Corrected Paragraph:", corrected_paragraph)
    return render_template('grammerChecker.html', rawtext=request.form.get('rawtext', ''), corrected_paragraph = corrected_paragraph )

# def correct_grammar(text):
#     corrected_paragraph = ""
#     sentences = text.split('.')
#     for sentence in sentences:
#         corrected_sentences = gf.correct(sentence.strip(), max_candidates=1)
#         corrected_paragraph += " ".join(corrected_sentences) + ". "
#     return corrected_paragraph

# def correct_grammar(text):
#     highlighted_paragraph = ""
#     sentences = text.split('.')
#     for i, sentence in enumerate(sentences):
#         corrected_sentences = gf.correct(sentence.strip(), max_candidates=1)
#         corrected_sentence = next(iter(corrected_sentences)) if corrected_sentences else sentence
#         original_words = sentence.split()
#         corrected_words = corrected_sentence.split()

#         for original_word, corrected_word in zip(original_words, corrected_words):
#             if original_word != corrected_word:
#                 highlighted_paragraph += f'<span class="highlight">{corrected_word}</span> '
#             else:
#                 highlighted_paragraph += corrected_word + ' '

#         # Append period only if there's another sentence following
#         if i < len(sentences) - 1:
#             highlighted_paragraph += ". "

#     return highlighted_paragraph.strip()

# def correct_grammar(text):
#     highlighted_paragraph = ""
#     sentences = text.split('.')
#     for i, sentence in enumerate(sentences):
#         corrected_sentences = gf.correct(sentence.strip(), max_candidates=1)
#         corrected_sentence = next(iter(corrected_sentences)) if corrected_sentences else sentence
#         original_words = sentence.split()
#         corrected_words = corrected_sentence.split()

#         for original_word, corrected_word in zip(original_words, corrected_words):
#             if original_word != corrected_word:
#                 highlighted_paragraph += f'<span class="highlight">{corrected_word}</span> '
#             else:
#                 highlighted_paragraph += corrected_word + ' '

#         # Append period and the last word of the sentence
#         if i < len(sentences) - 1:
#             highlighted_paragraph += ". "
#         else:
#             highlighted_paragraph += corrected_words[-1] if corrected_words else ""

#     return highlighted_paragraph.strip()

def correct_grammar(text):
    highlighted_paragraph = ""
    sentences = text.split('.')
    for i, sentence in enumerate(sentences):
        corrected_sentences = gf.correct(sentence.strip(), max_candidates=1)
        corrected_sentence = next(iter(corrected_sentences)) if corrected_sentences else sentence
        original_words = sentence.split()
        corrected_words = corrected_sentence.split()

        for original_word, corrected_word in zip(original_words, corrected_words):
            if original_word != corrected_word:
                highlighted_paragraph += f'<span>{corrected_word}</span> '
            else:
                highlighted_paragraph += corrected_word + ' '

        # Append period if it's not the last sentence
        if i < len(sentences) - 1:
            highlighted_paragraph += ". "

    # Append the last word of the last sentence
    if corrected_words:
        highlighted_paragraph += corrected_words[-1]

    return highlighted_paragraph.strip()


# ====================== Text To Speech ========================= 

@app.route('/textTospeech', methods=['GET', 'POST'])
def textToSpeech():
    rawtext = ""
    audio_file = None
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        tts = gTTS(text=rawtext, lang='en', slow=False)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        audio_file = f"output_{timestamp}.mp3"
        tts.save(os.path.join("static", audio_file))
    return render_template('textTospeech.html', audio_file=audio_file , rawtext=rawtext)


if __name__ == "__main__":
    app.run(debug = True)
