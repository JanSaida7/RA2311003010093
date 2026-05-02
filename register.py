import requests

registration_url = "http://20.207.122.201/evaluation-service/register"

# Using your verified details
registration_data = {
    "email": "jansaidasyed743@gmail.com",
    "name": "Syed Jan Saida",
    "mobileNo": "9391314853",
    "githubUsername": "JanSaida7",
    "rollNo": "RA2311003010093", 
    "accessCode": "QkbpxH"
}

response = requests.post(registration_url, json=registration_data)

if response.status_code == 200:
    creds = response.json()
    print("Registration Successful!")
    print(f"ClientID: {creds.get('clientID')}")
    print(f"ClientSecret: {creds.get('clientSecret')}")
    print("\nCRITICAL: Copy and save these now! You cannot retrieve them later.")
else:
    print(f"Registration Failed: {response.status_code}")
    print(response.text)