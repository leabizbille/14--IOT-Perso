import requests
import json
from dotenv import load_dotenv
import os

def envoyer_message_webhook(url_webhook: str, message: str) -> None:
    """
    Envoie un message à un webhook Discord.

    Args:
        url_webhook (str): L'URL du webhook Discord.
        message (str): Le message à envoyer.

    Returns:
        None: Aucun résultat n'est retourné.

    Raises:
        ValueError: Si l'URL du webhook n'est pas valide.
        requests.exceptions.HTTPError: Si une erreur HTTP est rencontrée lors de l'envoi du message.
    """
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url_webhook, data=json.dumps(data), headers=headers)
    if response.status_code == 204:
        print("Message envoyé avec succès au webhook.")
    else:
        raise requests.exceptions.HTTPError(
            f"Échec de l'envoi du message. Code d'état HTTP : {response.status_code}"
        )

# URL du webhook Discord
load_dotenv()
url_webhook = os.environ['DISCORD_WEBHOOK_URL']
envoyer_message_webhook(url_webhook, ' Message envoyé avec succès :-)')