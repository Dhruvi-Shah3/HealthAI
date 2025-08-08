from django.shortcuts import render,redirect
import os
import pandas as pd
from django.conf import settings 
import joblib
from .models import PredictionHistory
import random
import numpy as np
import json
# Create your views here.
def home(request):
    return render(request, 'home.html')

def predict(request):
    csv_path = os.path.join(settings.BASE_DIR, 'app', 'data', 'symptom.csv')
    df = pd.read_csv(csv_path)

    # Validate CSV structure
    if 'Symptom' not in df.columns or df.empty:
        return render(request, 'error.html', {'message': 'CSV missing or malformed'})

    # === Step 2: Handle GET (start session) ===
    if request.method == 'GET':
        symptoms = df.sort_values(by='weight', ascending=False)['Symptom'].dropna().tolist()

        # Pick 10 random symptoms and store in session
        top_symptoms = random.sample(symptoms, 10)
        request.session['top_symptoms'] = top_symptoms
        request.session['responses'] = {}

        return render(request, 'predict.html', {
            'symptom': top_symptoms[0].replace('_', ' '),
            'current_index': 0,
            'is_last': False,
            'total_questions': len(top_symptoms)
        })

    # === Step 3: Handle POST (collect responses) ===
    elif request.method == 'POST':
        top_symptoms = request.session.get('top_symptoms', [])
        if not top_symptoms:
            return render(request, 'error.html', {'message': 'Session expired. Please start again.'})

        current_index = int(request.POST['current_index'])
        answer = request.POST['answer']  
        symptom = request.POST['symptom']

        # Save response in session
        responses = request.session.get('responses', {})
        responses[symptom] = answer
        request.session['responses'] = responses

        # Move to next symptom or predict
        next_index = current_index + 1
        if next_index >= len(top_symptoms):
            return redirect('additional_symptoms')

        return render(request, 'predict.html', {
            'symptom': top_symptoms[next_index].replace('_', ' '),
            'current_index': next_index,
            'is_last': (next_index == len(top_symptoms) - 1),
            'total_questions': len(top_symptoms)
        })


def additional_symptoms(request):
    if request.method == 'POST':
        extra = request.POST.get('extra_symptoms', '')
        request.session['extra_symptoms'] = extra
        return redirect('predict_result')

    return render(request, 'additional_symptoms.html')

# Load model and symptom order once
MODEL_PATH = os.path.join(settings.BASE_DIR, 'app', 'model', 'model.pkl')
SYMPTOM_LIST_PATH = os.path.join(settings.BASE_DIR, 'app', 'model', 'symptom_list.pkl')

model = joblib.load(MODEL_PATH)
all_symptoms = joblib.load(SYMPTOM_LIST_PATH)  # Ensure same order as training

def predict_result(request):
    responses = request.session.get('responses', {})
    extra = request.session.get('extra_symptoms', '')
    predicted_disease = ""

    # Normalize extra symptoms
    extra_symptoms_list = [sym.strip().lower().replace(' ', '_') for sym in extra.split(',') if sym.strip()]

    # Create input vector
    input_vector = []
    for symptom in all_symptoms:
        if responses.get(symptom.replace('_', ' ')) == 'yes' or symptom in extra_symptoms_list:
            input_vector.append(1)
        else:
            input_vector.append(0)

    # Handle empty input
    if sum(input_vector) == 0:
        predicted_disease = "Cannot predict disease: no known symptoms were provided."
        return render(request, 'predict_result.html', {
            'disease': predicted_disease,
            'extra_symptoms': extra
        })

    # Make prediction
    probas = model.predict_proba([input_vector])[0]
    top_indices = np.argsort(probas)[::-1][:3]
    top_diseases = [(model.classes_[i], round(probas[i] * 100, 2)) for i in top_indices]

    # Store top-1 as main prediction
    predicted_disease = top_diseases[0][0].replace('_', ' ').title()
    request.session['predicted_disease'] = predicted_disease

    # Save history
    PredictionHistory.objects.create(
        symptoms=json.dumps(responses),
        extra_symptoms=extra,
        predicted_disease=predicted_disease
    )

    return render(request, 'predict_result.html', {
        'disease': predicted_disease,
        'top_diseases': top_diseases,
        'extra_symptoms': extra
    })

def show_precaution(request):
    disease = request.session.get('predicted_disease', None)

    if not disease:
        return redirect('symptom_step')  # If no prediction yet

    # Load CSV
    csv_path = os.path.join(settings.BASE_DIR, 'app', 'data', 'precaution.csv')
    df = pd.read_csv(csv_path)

    # Find matching row
    row = df[df['Disease'].str.lower() == disease.lower()]

    if not row.empty:
        precautions = row.iloc[0].drop('Disease').dropna().tolist()
    else:
        precautions = ["No precautions found for this disease."]

    return render(request, 'precaution.html', {
        'disease': disease,
        'precautions': precautions
    })

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')
