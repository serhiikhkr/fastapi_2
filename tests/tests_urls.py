import requests

mock_contact_data = {
    "first_name": "JJJJ",
    "last_name": "SSS",
    "email": "try@example.com"
}


def test_create_contact_successful():
    response = requests.post("http://127.0.0.1:8000/contacts", json=mock_contact_data)

    assert response.status_code == 201

    contact = response.json()
    assert contact["first_name"] == "John"
    assert contact["last_name"] == "Doe"
    assert contact["email"] == "john@example.com"


def test_create_contact_rate_limit_exceeded():
    response = None
    for i in range(11):
        response = requests.post("http://127.0.0.1:8000/contacts", json=mock_contact_data)

    assert response.status_code == 429
