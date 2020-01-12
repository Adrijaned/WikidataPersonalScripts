import mwapi
import requests_oauthlib
from credentials import credsdsds
import time

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
claims = session.get(action="wbgetentities", ids=lexemeID)["entities"][lexemeID]['claims']['P5831']

sentence = input("Please enter the sentence: ")

claim_texts = list(dict.fromkeys([x["mainsnak"]['datavalue']['value']['text'] for x in claims]))
if sentence in [x['mainsnak']['datavalue']['value']['text'] for x in claims]:
    print("Sentence already present, aborting.")
    exit(1)

approved = False
while not approved:
    formIndex = int(input("Enter form number: "))
    form = f'{lexemeID}-F{formIndex}'
    sense = f'{lexemeID}-S{input("Enter sense number: ")}'
    with open("czechAdjectiveFormDescriptions", 'r') as whatever:
        approved = input(f'{whatever.readlines()[formIndex - 1]} (Y/N) ') == 'Y'
approved = False
while not approved:
    URL = input("Reference URL: ").strip()
    URL_of_imported = input("URL of imported revision: ").strip()
    title = input("Enter the title of source work: ")
    published_in = input("Enter QID of source work: ")
    chapter = input("Enter book chapter (empty for none): ")
    chapter_json = (f', "P792": [{{"property": "P792", "snaktype":"value", "datavalue": {{"value": "{chapter}", '
                    f'"type": "string"}}, "datatype": "string"}}]' if chapter != '' else '')
    approved = input("Submit? (Y/N) ") == "Y"

millis = int(round(time.time() * 1000))
session.post(action='wbeditentity', id=lexemeID, summary="Added usage example", token=token,
             data=f'{{"claims": [{{"mainsnak": {{"snaktype": "value", "property": "P5831", "datavalue": {{"value": '
                  f'{{"language": "cs", "text": "{sentence}"}}, "type": "monolingualtext"}}}}, "type": "statement", '
                  f'"rank": "normal", "qualifiers": [{{"property": "P5830", "snaktype": "value", "datavalue":{{"value":'
                  f'{{"entity-type": "form", "id":"{form}"}},"type":"wikibase-entityid"}},"datatype":"wikibase-form"}},'
                  f'{{"property": "P6072", "snaktype": "value", "datavalue": {{"value": {{"entity-type": "sense","id":'
                  f'"{sense}"}},"type":"wikibase-entityid"}},"datatype": "wikibase-sense"}}], "references": [{{"snaks":'
                  f'{{"P854":[{{"property":"P854","snaktype":"value","datavalue":{{"value":"{URL}", "type": "string"}},'
                  f'"datatype": "url"}}], "P4656": [{{"property": "P4656", "snaktype": "value", "datavalue": {{"value":'
                  f'"{URL_of_imported}", "type": "string"}}, "datatype": "url"}}], "P1476": [{{"property": "P1476",'
                  f'"snaktype": "value", "datavalue": {{"value": {{"text": "{title}", "language": "cs"}}, "type":'
                  f'"monolingualtext"}}, "datatype": "monolingualtext"}}], "P1433": [{{"property": "P1433", "snaktype":'
                  f'"value", "datavalue": {{"value": {{"numeric-id": "'
                  f'{published_in if published_in[0] != "Q" else published_in[1:]}", "entity-type": "item"}}, "type":'
                  f'"wikibase-entityid"}}, "datatype": "wikibase-item"}}]{chapter_json}}}}}]}}]}}')
print(f"Submitted one, took {int(round(time.time() * 1000)) - millis} milliseconds.")
