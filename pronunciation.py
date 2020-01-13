import mwapi
import requests_oauthlib
from credentials import credsdsds
from IPA import pronun_to_IPA

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

whatever = []
for word in forms_texts:
    approved = False
    while not approved:
        pronunciation = input(f'Input pronunciation for {word}: ')
        approved = input(f"Is \"{pronunciation}\" correct? (Y/N) ").upper() == "Y"
    ipa = pronun_to_IPA(pronunciation)
    uncertain = False
    for x in "mncřrlm":
        if x in pronunciation:
            uncertain = True
    while input(f'Is [{pronunciation}] transcribed as /{ipa}/? {"Doubtful." if uncertain else ""} (Y/N) ').upper() != "Y":
        ipa = input("What is the correct form then? : ")
    for form in forms_new:
        if word == form["representations"]["cs"]["value"]:
            whatever.append(f'{{"id":"{form["id"]}","claims":[{{"mainsnak": {{"snaktype": "value", "property": "P7243",'
                            f' "datavalue": {{"value": {{"language": "cs", "text": "{pronunciation}"}}, "type": '
                            '"monolingualtext"}}, "type": "statement", "rank": "normal", "qualifiers":['
                            '{"property":"P898","snaktype":"value","datavalue":{"type":"string","value":"'
                            f'{ipa}'
                            '"}},{"property":"P443","snaktype":"value","datavalue":{"type":"string","value":"'
                            f'Cs-{word}.ogg'
                            '"}}]}]}')
            # session.post(action="wbcreateclaim", entity=form['id'], snaktype='value', property="P7243",
            #              value='{"text":"' + pronunciation + '","language":"cs"}', token=token)
session.post(action='wbeditentity', id=lexemeID, summary="Added pronunciation data", token=token,
             data='{"forms":[' + ','.join(whatever) + ']}')
