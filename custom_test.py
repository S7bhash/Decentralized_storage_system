import requests

print("SignUp page...!")
r=requests.get("http://127.0.0.1:5000/signup")
print("Response Status Code -- ",r.status_code)
