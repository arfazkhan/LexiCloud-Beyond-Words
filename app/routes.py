from flask import Blueprint, render_template, request
from wordcloud import WordCloud
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
import nltk
from PIL import Image
import numpy as np
import os

main = Blueprint('main', __name__)

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    color_map = request.form.get('color', 'random')
    if color_map == 'rainbow':
        return f"hsl({np.random.randint(0, 360)}, 100%, 50%)"
    elif color_map == 'heat':
        return f"hsl(0, 100%, {100 - font_size / 4}%)"
    elif color_map == 'earth':
        return f"hsl({np.random.randint(90, 150)}, 50%, 50%)"
    elif color_map == 'random':
        # Return a random color for each word
        return f"hsl({np.random.randint(0, 360)}, {np.random.randint(50, 100)}%, {np.random.randint(30, 70)}%)"
    return None

def cluster_func(wordcloud):
    X = list(wordcloud.words_.keys())
    word_vectors = [wordcloud.words_[word] for word in X]

    if len(X) <= 2:
        return {0: X}  # Return all words in one cluster if there are fewer than or equal to 2 words

    kmeans = KMeans(n_clusters=2)  # You can adjust the number of clusters
    word_vectors_reshaped = np.array(word_vectors).reshape(-1, 1)
    kmeans.fit(word_vectors_reshaped)

    clustered_words = {}
    for i, label in enumerate(kmeans.labels_):
        if label not in clustered_words:
            clustered_words[label] = []
        clustered_words[label].append(X[i])

    return clustered_words

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        font = request.form.get('font', 'sans-serif')
        font_path = os.path.join('app', 'static', 'fonts', 'Orbitron-VariableFont_wght.ttf') if font == 'serif' else None

        shape = request.form.get('shape', 'default')
        mask = np.array(Image.open(os.path.join('app', 'static', 'mask', f'{shape}.png'))) if shape in ['circle', 'star'] else None

        wordcloud = WordCloud(stopwords=set(nltk.corpus.stopwords.words('english')),
                              background_color='white',
                              font_path=font_path,
                              color_func=color_func,
                              mask=mask).generate(text)

        clustered_words = cluster_func(wordcloud)

        img = wordcloud.to_image()
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        img_url = base64.b64encode(img_byte_array.read()).decode()
        return render_template('index.html', img_url=img_url)
    return render_template('index.html')
