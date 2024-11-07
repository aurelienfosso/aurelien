from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import hashlib
import time
import threading

app = Flask(__name__)

# Détails de l'API et de Telegram
payload_template = {'api_key': 'fcacf98ba7d123c9113e0003b86764cb'}
TOKEN = '8081483069:AAFIRDDL-TUgC0R7Hb3P5kLYdK85DwZV0_U'
CHAT_ID = '-1002278042953'

# URLs des sessions d'examen
url_centre = [
    ['TCF-CANADA', 'Douala', 'https://douala.ifc-tests-examens.com/examens-session/10-test-de-connaissance-du-franais-pour-le-canada'],
    ['TEF-Canada', 'Douala', 'https://douala.ifc-tests-examens.com/examens-session/17-test-d-valuation-de-franais-pour-le-canada'],
    ['TCF-CANADA', 'Yaounde', 'https://yaounde.ifc-tests-examens.com/examens-session/10-test-de-connaissance-du-franais-pour-le-canada'],
    ['TEF Canada', 'Yaounde', 'https://yaounde.ifc-tests-examens.com/examens-session/15-test-d-evaluation-de-franais-pour-le-canada'],
]

derniers_hashes = {url[2]: None for url in url_centre}

# Fonction pour envoyer une notification sur Telegram
def envoyer_notification(message):
    url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    requests.post(url_telegram, data=payload)

# Fonction pour calculer le hash de la page
def obtenir_page(url):
    payload = payload_template.copy()
    payload['url'] = url
    response = requests.get('https://api.scraperapi.com/', params=payload)
    return BeautifulSoup(response.text, 'html.parser')

# Fonction pour surveiller les pages et détecter les changements
def surveiller_pages():
    while True:
        for nom_examen, ville, url in url_centre:
            soup = obtenir_page(url)
            contenu = soup.text
            hash_actuel = hashlib.md5(contenu.encode('utf-8')).hexdigest()
            if derniers_hashes[url] is None:
                derniers_hashes[url] = hash_actuel
                envoyer_notification(f"Surveillance activée pour {nom_examen} à {ville}.")
            elif hash_actuel != derniers_hashes[url]:
                envoyer_notification(f"😊Changement détecté")
                derniers_hashes[url] = hash_actuel  # Mettre à jour le hash
                aucun_examen = soup.find('span', class_='btn btn-danger')
                aucune_session = soup.find("span", class_="text text-danger")
                if aucun_examen:
                    message = f"{nom_examen} à {ville} : {aucun_examen.text.strip()}"
                elif aucune_session and aucune_session.text == '(Cette session est complète)':
                    message = f"💡Fausse alert: {nom_examen} à {ville} : {aucune_session.text.strip()}"
                    envoyer_notification(message)
                else:
                    message = f"🍀🎉{nom_examen} à {ville} : un examen programmer : {url}"
                    envoyer_notification(message)

        time.sleep(60)  # Attendre 1 minute avant de revérifie


@app.route('/')
def home():
    return "Le serveur est en marche!"

if __name__ == '__main__':
    # Démarrer la surveillance dans un thread au lancemen
    thread = threading.Thread(target=surveiller_pages)
    thread.daemon = True
    thread.start()
    
    app.run(host='0.0.0.0', port=5000)
