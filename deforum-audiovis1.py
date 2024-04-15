from time import sleep
import requests
import os
import argparse
import base64
import json

server = "https://deforum.studio"
api_url = f'{server}/api/public/v1/audiovis1'
DEFORUM_STUDIO_API_KEY = os.environ.get('DEFORUM_STUDIO_API_KEY')

if not DEFORUM_STUDIO_API_KEY:
    print(f"DEFORUM_STUDIO_API_KEY is not set. Please obtain your API key from {server}/settings, and assign it to enviroment variable DEFORUM_STUDIO_API_KEY.")
    exit(1)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DEFORUM_STUDIO_API_KEY}"
}


def main():
    parser = argparse.ArgumentParser(description="Deforum Studio simple audio visualisation API example.")
    parser.add_argument("audio_file", help="path to the audio file to visualise", type=str,)
    args = parser.parse_args()

    if not os.path.exists(args.audio_file):
        print(f"Error: file {args.audio_file} does not exist.")
        exit(2)

    print("Submitting job...")
    response = requests.post(api_url, headers=headers, json={
        "audioData": file_to_base64(args.audio_file)
        # --- optional args: ---
        # presetName: '__[RANDOM]__',
        # width: 1024,
        # height: 1024,
        # fps: 30,
        # crf: 23,
        # beatSensitivity: 2.0,
    })

    if response.status_code != 201:
        print(f"Error submitting job: {response.status_code} - {response.text}")
        exit(3)

    data = response.json()
    print(json.dumps(data, indent=2))

    tracking_url = f"{server}{data['links']['audiovis1']}"

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
        print(f"Job succeeded. Access the result here: {tracking_data['links']['outputUrls'][0]}")


def file_to_base64(filepath):
    with open(filepath, "rb") as file:
        file_data = file.read()
        base64_encoded_data = base64.b64encode(file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        return base64_message


if __name__ == "__main__":
    main()
