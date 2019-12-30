import mwapi
import requests_oauthlib
from credentials import credsdsds

session = mwapi.Session(
    host='https://www.wikidata.org',
    auth=requests_oauthlib.OAuth1(
        client_key=credsdsds[0],
        client_secret=credsdsds[1],
        resource_owner_key=credsdsds[2],
        resource_owner_secret=credsdsds[3],
    ),
    user_agent="Adrijaned_custom_script"
)

lexemeID = input("Enter ID of the lexeme: ")  # L204262

token = session.get(action='query', meta='tokens')['query']['tokens']['csrftoken']
forms = session.get(action="wbgetentities", ids=lexemeID)["entities"][lexemeID]["forms"]

forms_new = [x for x in forms if x["claims"] == [] or "P7243" not in x["claims"].keys()]

forms_texts = [x["representations"]["cs"]["value"] for x in forms_new]
forms_texts = list(dict.fromkeys(forms_texts))

for word in forms_texts:
    approved = False
    while not approved:
        pronunciation = input(f'Input pronunciation for {word}: ')
        approved = input(f"Is \"{pronunciation}\" correct? (Y/N) ") == "Y"
    for form in forms_new:
        if word == form["representations"]["cs"]["value"]:
            session.post(action="wbcreateclaim", entity=form['id'], snaktype='value', property="P7243",
                         value='{"text":"' + pronunciation + '","language":"cs"}', token=token)
