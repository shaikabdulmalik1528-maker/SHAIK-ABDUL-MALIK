import os
import sys
import requests

# Set the path to a valid image in your ASL dataset to test
# Update this path if your directory structure or test image filename is different
 # Update this line in scripts/test_api_prediction.py
TEST_IMAGE_PATH = "datasets/asl_alphabet/asl_alphabet_train/A/A1.jpg"
API_URL = "http://127.0.0.1:8000/predict/"

def test_api():
    # 1. Check if the test image exists locally
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Error: Test image not found at: {TEST_IMAGE_PATH}")
        print("Please modify 'TEST_IMAGE_PATH' in this script to point to a valid image.")
        sys.exit(1)

    print(f"🚀 Sending {TEST_IMAGE_PATH} to FastAPI server at {API_URL}...")
    
    # 2. Open the image in binary mode and send a multipart POST request
    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {
            "file": (os.path.basename(TEST_IMAGE_PATH), f, "image/jpeg")
        }
        try:
            response = requests.post(API_URL, files=files)
            
            # 3. Check and display response
            if response.status_code == 200:
                print("\n🎉 Success! API returned a valid response:")
                import json
                print(json.dumps(response.json(), indent=4))
            else:
                print(f"\n❌ Server Error (Status Code: {response.status_code})")
                print("Response detail:", response.text)
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to the server.")
            print("Make sure your FastAPI backend is running (e.g., uvicorn app.main:app --reload)")

if __name__ == "__main__":
    test_api()
    