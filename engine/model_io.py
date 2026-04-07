import requests

def llm(messages):
    response = requests.post(
        "http://localhost:8080/v1/chat/completions",
        json={
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]
