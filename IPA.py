import mwapi
import requests_oauthlib
from credentials import credsdsds
import time


def pronun_to_IPA(word: str):
    result = ""
    word = word.replace('au', '1').replace('ou', '2').replace('eu', '3').replace('ch', '4').replace('dž', '5')
    mapping = {
        'a': 'a',
        'á': 'aː',
        'b': 'b',
        'c': 't͡s',
        'č': 't͡ʃ',
        'd': 'd',
        'ď': 'ɟ',
        'e': 'ɛ',
        'é': 'ɛː',
        'f': 'f',
        'g': 'g',
        'h': 'ɦ',
        'i': 'ɪ',
        'í': 'iː',
        'j': 'j',
        'k': 'k',
        'l': 'l',
        'm': 'm',
        'n': 'n',
        'ň': 'ɲ',
        'o': 'o',
        'ó': 'oː',
        'p': 'p',
        'r': 'r',
        'ř': 'r̝',
        's': 's',
        'š': 'ʃ',
        't': 't',
        'ť': 'c',
        'u': 'ʊ',
        'ú': 'uː',
        'v': 'v',
        'z': 'z',
        'ž': 'ʒ',
        '1': 'aʊ̯̯',
        '2': 'oʊ̯',
        '3': 'ɛʊ̯',
        '4': 'x',
        '5': 'd͡ʒ',
    }
    for letter in word:
        result += mapping[letter]
    return result


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

lexemeID = input("Enter ID of the lexeme (ensure all forms have single P7243-pronunciation): ")  # L204262

token = session.get(action='query', meta='tokens')['query']['tokens']['csrftoken']
claims = [x['claims']['P7243'][0]
          for x in
          session.get(action="wbgetentities", ids=lexemeID)["entities"][lexemeID]["forms"]
          if
          'qualifiers' not in x['claims']['P7243'][0].keys()]

claim_texts = list(dict.fromkeys([x["mainsnak"]['datavalue']['value']['text'] for x in claims]))

for word in claim_texts:
    ipa = pronun_to_IPA(word)
    uncertain = False
    for x in "mncřrlm":
        if x in word:
            uncertain = True
    while input(f'Is [{word}] transcribed as /{ipa}/? {"Doubtful." if uncertain else ""} (Y/N) ') != "Y":
        ipa = input("What is the correct form then? : ")

    for claim in claims:
        if word == claim["mainsnak"]['datavalue']['value']['text']:
            millis = int(round(time.time() * 1000))
            session.post(action='wbsetqualifier', claim=claim['id'], property="P898", value=f'"{ipa}"',
                         snaktype='value', token=token)
            print(f"Submitted one, took {int(round(time.time() * 1000)) - millis} milliseconds.")
