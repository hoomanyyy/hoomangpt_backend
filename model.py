import requests


MODAL_URL = "https://hoomankhodadadi91--qwen-notefinder-summarize.modal.run"



def generate_response(text):

    try:

        response = requests.post(
            MODAL_URL,
            json={
                "text": text
            },
            timeout=300
        )


        if response.status_code != 200:
            print(
                "Modal error:",
                response.text
            )
            return None



        data = response.json()


        return data.get(
            "summary"
        )



    except Exception as e:

        print(
            "AI ERROR:",
            e
        )

        return None





def generate_normal_response(text):

    try:

        response = requests.post(
            MODAL_URL,
            json={
                "text": text
            },
            timeout=300
        )


        data = response.json()


        return data.get(
            "summary"
        )


    except Exception as e:

        print(
            "AI ERROR:",
            e
        )

        return None