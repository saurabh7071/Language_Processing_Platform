import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

# text = """ Laila Boonyasak (Thai: ไลลา บุญยศักดิ์, RTGS: Laila Bunyasak), or formerly Chermarn Boonyasak (Thai: เฌอมาลย์ บุญยศักดิ์, RTGS: Choeman Bunyasak), nickname Ploy (Thai: พลอย, RTGS: Phloi), is a Thai film and television actress[1] and model. She is well known for her role as June/Tang in the movie The Love of Siam.[2][3] Her other film roles have included the title ghost character in director Yuthlert Sippapak's horror-comedies Buppah Rahtree and Buppah Rahtree Phase 2: Rahtree Returns. She was also featured in Pen-Ek Ratanaruang's Last Life in the Universe,[2][4] in which she portrayed the younger sister of the character played by her real-life older sister, Daran Boonyasak.[5]"""

def summarizer(rawdocs):
    stopwords = list(STOP_WORDS)    
    # print(stopwords)

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(rawdocs)
    # print(doc)
    tokens = [token.text for token in doc]
    # print(tokens)
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq.keys():
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1
                
    # print(word_freq)

    max_freq = max(word_freq.values())
    # print(max_freq)

    for word in word_freq.keys():
        word_freq[word] = word_freq[word]/max_freq
        
    # print(word_freq)

    sent_tokens = [sent for sent in doc.sents]
    # print(sent_tokens)

    sent_scores = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq.keys():
                if sent not in sent_scores.keys():
                    sent_scores[sent] = word_freq[word.text]
                else:
                    sent_scores[sent] += word_freq[word.text]
                    
    # print(sent_scores)

    select_len = int(len(sent_tokens) * 0.3)
    # print(select_len)
    summary = nlargest(select_len, sent_scores, key = sent_scores.get)
    # print(summary)
    final_summary = [word.text for word in summary] 
    # final_summary = ['#' + sent.text.strip() + '#' for sent in summary] 
    summary = ' '.join(final_summary)
    # print(text)
    # print(summary)
    # print("Length of original text : ",len(text.split(' ')))
    # print("Length of summary text : ",len(summary.split(' ')))
    
    return summary, doc, len(rawdocs.split(' ')), len(summary.split(' '))


        