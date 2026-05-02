import requests

auth_url = "http://20.207.122.201/evaluation-service/auth"

# Using the credentials you just received
auth_data = {
    "email": "jansaidasyed743@gmail.com",
    "name": "Syed Jan Saida",
    "rollNo": "RA2311003010093",
    "accessCode": "QkbpxH",
    "clientID": "8b9078f6-7fcc-4bfc-9543-1cd90ed63c28",
    "clientSecret": "nzPWAFBCNhbWMMmB"
}

print("Requesting Authorization Token...")
response = requests.post(auth_url, json=auth_data)

if response.status_code == 200:
    token_data = response.json()
    print("--- Authentication Successful! ---")
    print("Copy the token below (it's long):")
    print(token_data.get('access_token'))
else:
    print(f"Auth Failed: {response.status_code}")
    print(response.text)