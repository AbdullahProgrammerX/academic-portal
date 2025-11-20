"""Test login and check cookies"""
import requests

url = 'http://127.0.0.1:8000/api/auth/login/'
data = {
    'email': 'user123@test.com',
    'password': 'MyPass123'
}

response = requests.post(url, json=data)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print(f"\nCookies:")
for cookie in response.cookies:
    print(f"  {cookie.name} = {cookie.value}")
    print(f"    httponly: {cookie.has_nonstandard_attr('HttpOnly')}")
    print(f"    secure: {cookie.secure}")
    print(f"    samesite: {cookie.get_nonstandard_attr('SameSite')}")
    print(f"    max-age: {cookie.get_nonstandard_attr('Max-Age')}")

if 'refresh_token' in [c.name for c in response.cookies]:
    print("\n✓ Refresh token cookie SET!")
else:
    print("\n✗ Refresh token cookie NOT SET!")
