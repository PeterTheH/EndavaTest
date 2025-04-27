import requests
BASE_URL = "https://reqres.in/api/users"
API_KEY = "reqres-free-v1"

def sort_users(users):
    sorted_users = sorted(users, key=lambda user: user["first_name"].lower())
    return sorted_users

def list_users():
    params = {"page": 1, "api_key": API_KEY}
    response = requests.get(BASE_URL, params=params)
    assert "data" in response.json()
    assert response.json()["total"] == 12
    users = response.json()["data"]
    return users

def extract_single_user(users):
    user = users[0]
    assert "id" in user and "email" in user
    return {"id": user["id"],"email": user["email"]}

def get_user_details(user_id):
    url_single_user = f"{BASE_URL}/{user_id}"
    params_single_user = {"api_key": API_KEY}
    response = requests.get(url_single_user, params=params_single_user)
    assert "data" in response.json()
    data_single_user = response.json()["data"]
    assert data_single_user["id"] == 1
    assert data_single_user["first_name"] == "George"
    # return data_single_user

def get_non_existing_user():
    url_not_existing_user = f"{BASE_URL}/999"
    params_not_existing_user = {"api_key": API_KEY}
    response = requests.get(url_not_existing_user, params=params_not_existing_user)
    assert response.status_code == 404, f"Expected error code 404, got {response.status_code}"

# Не сме оторизирани да добавяме към тестовия сайт, но ще го симулираме
def create_new_user():
    new_user_data = {
        "id": 2003,
        "email": "testEmail",
        "first_name": "testFirstName",
        "last_name": "testLastName",
    }
    response_new_user = requests.post(BASE_URL, json=new_user_data)
    assert response_new_user.status_code == 401, f"Expected error code 401 (not authorized), got {response_new_user.status_code}"
    # assert "data" in response_new_user.json()
    # assert response_new_user.json()["id"] == 2003
    # assert response_new_user.json()["email"] == "testEmail"
    # assert response_new_user.json()["first_name"] == "testFirstName"
    return new_user_data["id"]

# Не сме оторизирани да трием, но ще го симулираме
def delete_user(user_id):
    url_delete = f"{BASE_URL}/{user_id}"
    response_del = requests.delete(url_delete)
    assert response_del.status_code == 401, f"Expected error code 401 (not authorized), got {response_del.status_code}"

if __name__ == '__main__':
    users = list_users()
    print(f"sorted_users: {sort_users(users)}")
    single_user = extract_single_user(users)
    get_user_details(single_user["id"])
    get_non_existing_user()
    new_user_id = create_new_user()
    delete_user(new_user_id)


