from flask import Flask, render_template, request
from google.cloud import vision
import os
import requests

app = Flask(__name__)

# Définir la variable d'environnement GOOGLE_APPLICATION_CREDENTIALS dans le code
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\RUBENS\\beauvoir\\service_account_key.json"

# Initialiser le client Google Cloud Vision
client = vision.ImageAnnotatorClient()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/appointment')
def appointment():
    return render_template('appointment.html')

@app.route('/legal')
def legal():
    return render_template('legal.html')

@app.route('/formulaire_tally')
def formulaire_tally():
    return render_template('formulaire_tally.html')

@app.route('/bird_recognition', methods=['GET', 'POST'])
def bird_recognition():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('bird_recognition.html', error="Pas de fichier fourni")

        file = request.files['file']
        content = file.read()

        # Créer une image pour Google Vision
        image = vision.Image(content=content)

        # Utiliser l'API pour détecter les labels
        try:
            response = client.label_detection(image=image)
            labels = response.label_annotations
        except Exception as e:
            print("Erreur lors de la détection des labels :", e)
            return render_template('bird_recognition.html', error="Erreur lors de l'utilisation de l'API Vision.")

        # Extraire le nom de l'oiseau
        bird_name = None
        for label in labels:
            if "bird" in label.description.lower():
                bird_name = label.description
                break

        if bird_name:
            # Rechercher le chant de l'oiseau sur Xeno-canto
            try:
                response = requests.get(f'https://www.xeno-canto.org/api/2/recordings?query={bird_name}')
                if response.status_code == 200:
                    data = response.json()
                    if data['recordings']:
                        bird_info = data['recordings'][0]
                        bird_song_url = bird_info['file']
                        bird_common_name = bird_info.get('en', 'Nom commun non disponible')
                        bird_scientific_name = bird_info.get('gen', '') + " " + bird_info.get('sp', '')
                        bird_location = bird_info.get('loc', 'Localisation non disponible')

                        return render_template(
                            'bird_recognition.html',
                            bird_name=bird_common_name,
                            scientific_name=bird_scientific_name,
                            song_url=bird_song_url,
                            location=bird_location
                        )
                    else:
                        return render_template('bird_recognition.html', bird_name=bird_name, error="Aucun enregistrement trouvé pour cet oiseau.")
                else:
                    print("Erreur de requête Xeno-canto :", response.status_code)
                    return render_template('bird_recognition.html', error="Erreur lors de la recherche sur Xeno-canto.")
            except requests.RequestException as e:
                print("Erreur de connexion à Xeno-canto :", e)
                return render_template('bird_recognition.html', error="Erreur de connexion à Xeno-canto.")
        else:
            return render_template('bird_recognition.html', error="Aucun oiseau détecté dans l'image.")

    # Affiche le formulaire pour la méthode GET
    return render_template('bird_recognition.html')

if __name__ == "__main__":
    app.run(debug=True)
