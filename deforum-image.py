from time import sleep
import requests
import os
import argparse
import base64
import json

server = os.environ.get('DEFORUM_STUDIO_SERVER', "https://deforum.studio")
api_url = f'{server}/api/public/v1/image'
DEFORUM_STUDIO_API_KEY = os.environ.get('DEFORUM_STUDIO_API_KEY')

if not DEFORUM_STUDIO_API_KEY:
    print(f"DEFORUM_STUDIO_API_KEY is not set. Please obtain your API key from {server}/settings, and assign it to enviroment variable DEFORUM_STUDIO_API_KEY.")
    exit(1)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DEFORUM_STUDIO_API_KEY}"
}


def main():
    parser = argparse.ArgumentParser(description="Deforum Studio animation API example.")
    parser.add_argument("--prompt", "-p", help="text prompt for your animation", type=str, required=True, action="store")
    args = parser.parse_args()

    print("Submitting job...")
    response = requests.post(api_url, headers=headers, json={
        "prompt": args.prompt,
        # --- optional args: ---
        # negativePrompt: 'blurry, nsfw',
        # batch: 2,
        # steps: 18,
        # cfg: 4,
        # width: 1024,
        # height: 1024,
    })

    if response.status_code != 201:
        print(f"Error submitting job: {response.status_code} - {response.text}")
        exit(3)

    data = response.json()
    print(json.dumps(data, indent=2))

    tracking_url = f"{server}{data['links']['image']}"

    print(f"Job submitted successfully. Tracking URL: {tracking_url}")

    # Wait for job to complete. Poll status every 10s.
    while True:
        response = requests.get(f"{tracking_url}", headers=headers)
        if response.status_code != 200:
            print(f"Error getting job status: {response.text}")
            exit(4)

        tracking_data = response.json()
        if tracking_data['status'] in ['canceled', 'failed', 'succeeded']:
            break

        print(f"Job status: {tracking_data['status']}. Waiting for completion...")
        sleep(10)

    # Job has completed.
    if tracking_data['status'] != 'succeeded':
        print(f"Job ended with status: {tracking_data['status']}")
    else:
        print(f"Job succeeded. Access the result here: {tracking_data['links']['outputUrls']}")


def file_to_base64(filepath):
    with open(filepath, "rb") as file:
        file_data = file.read()
        base64_encoded_data = base64.b64encode(file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        return base64_message


if __name__ == "__main__":
    main()
