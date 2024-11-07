import requests
from bs4 import BeautifulSoup
import hashlib
import time

# Détails de l'API et de Telegram
payload_template = { 'api_key': 'fcacf98ba7d123c9113e0003b86764cb' }
TOKEN = '8081483069:AAFIRDDL-TUgC0R7Hb3P5kLYdK85DwZV0_U'
CHAT_ID = '-1002278042953'

# URLs des sessions d'examen
url_centre = [
    ['TCF-CANADA', 'Douala', 'https://douala.ifc-tests-examens.com/examens-session/10-test-de-connaissance-du-franais-pour-le-canada'],
    ['TEF-Canada', 'Douala', 'https://douala.ifc-tests-examens.com/examens-session/17-test-d-valuation-de-franais-pour-le-canada'],
    ['TCF-CANADA', 'Yaounde', 'https://yaounde.ifc-tests-examens.com/examens-session/10-test-de-connaissance-du-franais-pour-le-canada'],
    ['TEF Canada', 'Yaounde', 'https://yaounde.ifc-tests-examens.com/examens-session/15-test-d-evaluation-de-franais-pour-le-canada'],
]
url_yaounde = [
    ['TCF QUEBEC', 'https://yaounde.ifc-tests-examens.com/examens-session/2-test-de-connaissance-du-franais-pour-le-quebec'],
    ['TCF TOUT PUBLIC', 'https://yaounde.ifc-tests-examens.com/examens-session/3-test-de-connaissance-du-franais-tout-public'],
   
    ['TCF-IRN', 'https://yaounde.ifc-tests-examens.com/examens-session/12-test-de-connaissance-de-franais-pour-intgration-rsidence-et-nationalit'],
    ['TEF IRN', 'https://yaounde.ifc-tests-examens.com/examens-session/7-test-d-evaluation-de-franais-intgration-rsidence-nationalit'],
    ['TEFAQb', 'https://yaounde.ifc-tests-examens.com/examens-session/6-test-d-evaluation-de-franais-adapt-au-qubec'],
    
    ['TEF-Complet', 'https://yaounde.ifc-tests-examens.com/examens-session/11-test-d-valuation-de-franais-complet']
]




# Fonction pour envoyer une notification sur Telegram
def envoyer_notification(message):
    url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    requests.post(url_telegram, data=payload)



# Fonction pour calculer le hash de la page
def obtenir_page(url):
    payload = payload_template.copy()
    payload['url'] = url
    
    # Effectuer la requête via ScraperAPI
    response = requests.get('https://api.scraperapi.com/', params=payload)
     
    
    return BeautifulSoup(response.text, 'html.parser')

# Dictionnaire pour stocker les derniers hashes des pages
derniers_hashes = {url[2]: None for url in url_centre}

# Boucle infinie pour vérifier régulièrement les modifications
while True:
    for nom_examen, ville, url in url_centre:
        soup = obtenir_page(url)
        contenu = soup.text
        hash_actuel = hashlib.md5(contenu.encode('utf-8')).hexdigest()
        
        # Comparaison avec le dernier hash connu
        if derniers_hashes[url] is None:
            # Première exécution, initialisation du hash
            derniers_hashes[url] = hash_actuel
            envoyer_notification(f"Surveillance activée pour {nom_examen} à {ville}.")
        elif hash_actuel != derniers_hashes[url]:
            # Changement détecté
            envoyer_notification(f"Changement détecté pour {nom_examen} à {ville} : {url}")
            derniers_hashes[url] = hash_actuel  # Mettre à jour le hash
            aucun_examen = soup.find('span', class_='btn btn-danger')
            aucune_session = soup.find("span", class_="text text-danger")
            if aucun_examen:
                message = f"{nom_examen} à {ville} : {aucun_examen.text.strip()}"
            elif titre.text == '(Cette session est complète)':
                message = f"{nom_examen} à {ville} : {titre.text.strip()}"
            else:
                message = f"{nom_examen} à {ville} : un examen programmer : {url}"
                envoyer_notification(message)
    
   


    # Attendre avant de revérifier
    time.sleep(60)  # Vérifie toutes les 5 minutes
