import nltk
import random
import json
import pickle
import os
import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, request, jsonify
from flask_cors import CORS  # Importa CORS


# Inicializamos el lematizador
lemmatizer = WordNetLemmatizer()

# Cargamos el archivo JSON con los intents
with open('intents.json') as file:
    intents = json.load(file)

# Inicializamos listas vacías para las palabras, clases y documentos
words = []
classes = []
documents = []
ignore_letters = ['?', '!', '¿', '.', ',']

# Verificamos si los archivos del modelo existen, si no, lo entrenamos
if os.path.exists('chatbot_model.pkl') and os.path.exists('vectorizer.pkl') and os.path.exists('words.pkl') and os.path.exists('classes.pkl'):
    # Si los archivos existen, cargamos el modelo y el vectorizador
    with open('chatbot_model.pkl', 'rb') as f:
        model = pickle.load(f)

    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

    with open('words.pkl', 'rb') as f:
        words = pickle.load(f)

    with open('classes.pkl', 'rb') as f:
        classes = pickle.load(f)

    print("Modelo cargado exitosamente.")
else:
    # Si no existen, entrenamos el modelo

    # Clasificamos los patrones y las categorías
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent["tag"]))
            if intent["tag"] not in classes:
                classes.append(intent["tag"])

    # Lematizamos las palabras y las limpiamos
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
    words = sorted(set(words))  # Eliminamos duplicados

    # Guardamos las palabras y las clases usando pickle
    with open('words.pkl', 'wb') as f:
        pickle.dump(words, f)

    with open('classes.pkl', 'wb') as f:
        pickle.dump(classes, f)

    # Preparamos los datos de entrenamiento
    training_sentences = []
    training_labels = []

    for document in documents:
        training_sentences.append(" ".join(document[0]))  # Unimos las palabras para cada patrón
        training_labels.append(document[1])  # Guardamos la etiqueta (clase)

    # Creamos el CountVectorizer (bag of words)
    vectorizer = CountVectorizer(tokenizer=nltk.word_tokenize, stop_words=None)

    # Ajustamos el vectorizador a los datos
    X_train = vectorizer.fit_transform(training_sentences).toarray()
    y_train = [classes.index(label) for label in training_labels]  # Convertimos las clases a índices

    # Creamos el modelo de Naive Bayes
    model = MultinomialNB()

    # Entrenamos el modelo
    model.fit(X_train, y_train)

    # Guardamos el modelo y el vectorizador con pickle
    with open('chatbot_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    print("¡Entrenamiento completado y el modelo ha sido guardado!")

# Función para predecir la clase de una entrada
def predict_class(text):
    # Convertimos el texto en un vector de características usando el vectorizador
    text_vector = vectorizer.transform([text]).toarray()

    # Usamos el modelo para predecir la clase
    prediction = model.predict(text_vector)[0]

    return classes[prediction]

# Función para obtener una respuesta
def get_response(tag):
    for intent in intents['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])

# Crear la aplicación Flask
app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app)

# Definir el endpoint de la API
@app.route('/chat', methods=['POST'])
def chat():
    # Obtener el mensaje del cuerpo de la solicitud
    user_message = request.json['message']
    print(f"Mensaje recibido: {user_message}")
    
    # Predecir la clase del mensaje
    predicted_tag = predict_class(user_message)
    
    # Obtener una respuesta para la clase predicha
    response = get_response(predicted_tag)
    
    return jsonify({'response': response})

# Iniciar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
