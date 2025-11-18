import requests

def gtranslate(text, target):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": target,
        "dt": "t",
        "q": text
    }

    response = requests.get(url, params=params)
    result = response.json()[0][0][0]
    return result

#print(gtranslate("hello", "tr"))