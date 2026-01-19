import requests
import json

session = requests.Session()

# Login
login_data = {
    'email': 'testuser123@example.com',
    'password': '123456'
}
session.post('http://localhost:5000/login', data=login_data)

# API'den frame'leri al
response = session.get('http://localhost:5000/api/profile/frames')
if response.status_code == 200:
    frames = response.json()
    print("FRAMES API RESPONSE:")
    for frame in frames[:3]:
        print(f"  {frame}")
else:
    print(f"Error: {response.status_code}")

# API'den badge'leri al
response = session.get('http://localhost:5000/api/profile/badges')
if response.status_code == 200:
    badges = response.json()
    print("\nBADGES API RESPONSE:")
    for badge in badges[:3]:
        print(f"  {badge}")
else:
    print(f"Error: {response.status_code}")
