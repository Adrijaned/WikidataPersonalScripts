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
thing = session.get(action="wbgetentities", ids=lexemeID)
forms = thing["entities"][lexemeID]["forms"]

forms_new = [x for x in forms if x["claims"] == [] or "P5279" not in x["claims"].keys()]
print(forms_new)

forms_texts = [x["representations"]["cs"]["value"] for x in forms_new]
# print(f"len = {len(forms_texts)}; contents = {forms_texts}")
forms_texts = list(dict.fromkeys(forms_texts))
# print(f"len = {len(forms_texts)}; contents = {forms_texts}")

for word in forms_texts:
    approved = False
    while not approved:
        holes = input(f'Input division points for {word}: ')
        holes = holes.split(sep=' ')
        holes = [int(x) for x in holes]
        syllables = []
        last_cut = 0
        for hole in holes:
            syllables = syllables + [word[last_cut:hole]]
            last_cut = hole
        syllables.append(word[last_cut:])
        # print(f"{word}, {syllables}")
        deravyslovo = ("‧".join(syllables))
        approved = input(f"Is \"{deravyslovo}\" correct? Y/N") == "Y"
    for form in forms_new:
        if word == form["representations"]["cs"]["value"]:
            session.post(action="wbcreateclaim", entity=form['id'], snaktype='value', property="P5279",
                         value=f'"{deravyslovo}"', token=token)
