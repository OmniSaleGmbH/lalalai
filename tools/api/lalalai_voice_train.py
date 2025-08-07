#!/usr/bin/python3

# Copyright (c) 2025 LALAL.AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys

if sys.version_info >= (3, 13):
    raise RuntimeError("This script requires Python 3.12 or earlier. Actual version is: ", sys.version_info)

import json
import os
import glob
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
from urllib.parse import quote, urlencode
from urllib.request import urlopen, Request

URL_API = "https://www.lalal.ai/api/"


def _make_content_disposition(filename, disposition='attachment'):
    try:
        filename.encode('ascii')
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f'{disposition}; {file_expr}'


def upload_file(file_path, license):
    """Upload a single file and return its ID"""
    url_for_upload = URL_API + "upload/"
    _, filename = os.path.split(file_path)
    headers = {
        "Content-Disposition": _make_content_disposition(filename),
        "Authorization": f"license {license}",
    }
    with open(file_path, 'rb') as f:
        request = Request(url_for_upload, f, headers)
        with urlopen(request) as response:
            upload_result = json.load(response)
            if upload_result["status"] == "success":
                return upload_result["id"]
            else:
                raise RuntimeError(upload_result["error"])


def upload_files(file_paths: list[str], license: str) -> list[str]:
    """Upload multiple files and return list of their IDs"""
    uploaded_ids = []

    for file_path in file_paths:
        print(f'Uploading file: "{file_path}"...')
        file_id = upload_file(file_path, license)
        uploaded_ids.append(file_id)
        print(f'Successfully uploaded "{file_path}" (ID: {file_id})')

    return uploaded_ids


def start_voice_pack_training(file_ids: list[str], pack_name: str, license: str):
    """Start voice pack training with uploaded file IDs"""
    url = URL_API + "voice_packs/train/start/"

    headers = {
        "Authorization": f"license {license}",
    }
    # Prepare form data
    query_args = {
        "id": ",".join(file_ids),
        "pack_name": pack_name,
    }

    body = urlencode(query_args).encode('utf-8')
    request = Request(url, body, headers)

    with urlopen(request) as response:
        result = json.load(response)
        if result["status"] == "error":
            print(f"Error starting training: {locals()}")
            raise RuntimeError(result["error"])
        return result


def check_training_status(train_id: str, license: str):
    """Check training status and wait for completion"""
    url = URL_API + "voice_packs/train/check/"
    headers = {
        "Authorization": f"license {license}",
    }

    print(f"\nMonitoring training progress for train_id: {train_id}")
    print("Training may take from 10 minutes to several hours, please be patient.")
    print("Checking every 60 seconds...")
    minutes_passed = 0

    while True:
        if minutes_passed > 60 * 6:
            raise RuntimeError("Training check timeout exceeded (6 hours). Please contact support.")
        minutes_passed += 1
        print(f"\nChecking status... (Elapsed time: {minutes_passed} minutes)")
        try:
            # this should be a POST request
            # change to GET if receive error 405 method not allowed
            request = Request(url, data=b'', headers=headers)
            with urlopen(request) as response:
                result = json.load(response)

                if result.get("status") == "error":
                    raise RuntimeError(result.get("error", "Unknown error"))

                # Find our specific training in the voice_packs
                voice_packs = result.get("voice_packs", {})

                if train_id not in voice_packs:
                    print(f"Warning: train_id {train_id} not found in active trainings")
                    print("This might mean training has completed or failed.")
                    return None  # Return None instead of break

                pack_info = voice_packs[train_id]
                state = pack_info.get("state")
                progress = pack_info.get("progress", 0)
                pack_name = pack_info.get("pack_name", "Unknown")

                if "progress" in pack_info:
                    print(f"Pack: {pack_name} | State: {state} | Progress: {progress}%")
                else:
                    print(f"Pack: {pack_name} | State: {state} | Queue up for training")

                if state == "success":
                    voice_pack_id = pack_info.get("pack_id")
                    print("\n Training completed successfully!")
                    print(f"Voice pack '{pack_name}' is ready to use.")
                    print(f"Voice pack ID: {voice_pack_id}")
                    return voice_pack_id  # Return voice_pack_id instead of True
                elif state == "error":
                    print(f"\n Training failed with state: {state}")
                    return None  # Return None instead of False

                # Wait 60 seconds before next check
                time.sleep(60)

        except Exception as err:
            print(f"Error checking training status: {err}")
            print("Retrying in 60 seconds...")
            time.sleep(60)


def activate_voice_pack(voice_pack_id: str, license: str):
    url = URL_API + "voice_packs/activate/"
    headers = {
        "Authorization": f"license {license}",
    }

    query_args = {
        'id': voice_pack_id,
    }
    body = urlencode(query_args).encode('utf-8')

    request = Request(url, body, headers)

    with urlopen(request) as response:
        result = json.load(response)
        if result["status"] == "error":
            raise RuntimeError(result["error"])


def check_voice_pack_status(voice_pack_id: str, license: str):
    """Check if voice pack is ready to use"""
    url = URL_API + "voice_packs/list/"
    headers = {
        "Authorization": f"license {license}",
    }

    try:
        request = Request(url, headers=headers)
        with urlopen(request) as response:
            result = json.load(response)

            if result.get("status") == "error":
                raise RuntimeError(result.get("error", "Unknown error"))

            # Find our specific voice pack in the packs
            packs = result.get("packs", [])

            for pack in packs:
                if pack.get("pack_id") == voice_pack_id:
                    pack_name = pack.get("name", "Unknown")
                    ready_to_use = pack.get("ready_to_use", False)

                    print("\nVoice pack status:")
                    print(f"Pack ID: {voice_pack_id}")
                    print(f"Pack Name: {pack_name}")
                    print(f"Ready to use: {ready_to_use}")

                    if ready_to_use:
                        print(f"(V) Voice pack '{pack_name}' is ready to use!")
                        return True
                    else:
                        print(f"(?) Voice pack '{pack_name}' is not yet ready to use.")
                        return False

            print(f"(!!!) Voice pack with ID {voice_pack_id} not found in your voice packs list.")
            return False

    except Exception as err:
        raise RuntimeError(f"Failed to check voice pack status: {err}") from err


def collect_audio_files(input_paths: list[str]) -> list[str]:
    """Collect audio files from input paths (files or directories)"""
    audio_extensions = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
    collected_files = []

    for input_path in input_paths:
        if os.path.isfile(input_path):
            # Single file
            _, ext = os.path.splitext(input_path.lower())
            if ext in audio_extensions:
                collected_files.append(input_path)
            else:
                print(f'Warning: "{input_path}" is not a supported audio file format')
        elif os.path.isdir(input_path):
            # Directory - find all audio files
            for ext in audio_extensions:
                pattern = os.path.join(input_path, f'*{ext}')
                found_files = glob.glob(pattern)
                collected_files.extend(found_files)
        else:
            print(f'Warning: "{input_path}" does not exist')

    return sorted(set(collected_files))  # Remove duplicates and sort


def _make_content_disposition(filename, disposition='attachment'):
    try:
        filename.encode('ascii')
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f'{disposition}; {file_expr}'


def main():
    parser = ArgumentParser(description='LALAL.AI voice training', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--license', required=True, type=str, default=SUPPRESS, help='license key')
    parser.add_argument('--input', required=True, nargs='+', help='input files or directories (can specify multiple)')
    parser.add_argument('--pack-name', required=True, type=str, help='name for the voice pack to be created')

    args = parser.parse_args()

    # Collect all audio files from input paths
    print("Collecting audio files...")
    audio_files = collect_audio_files(args.input)

    if not audio_files:
        print("No audio files found in the specified input paths.")
        return

    print(f"Found {len(audio_files)} audio files:")
    for file_path in audio_files:
        print(f"  - {file_path}")

    # Upload all files
    print(f"\nUploading {len(audio_files)} files...")
    uploaded_ids = upload_files(audio_files, args.license)

    print(f"\nSuccessfully uploaded {len(uploaded_ids)} files:")
    for i, (file_path, file_id) in enumerate(zip(audio_files, uploaded_ids, strict=False), 1):
        print(f"  {i}. {os.path.basename(file_path)} -> {file_id}")

    # Start voice pack training
    print("\nStarting voice pack training...")
    print(f"Pack name: {args.pack_name}")
    print(f"Using {len(uploaded_ids)} uploaded files")

    training_result = start_voice_pack_training(
        file_ids=uploaded_ids,
        pack_name=args.pack_name,
        license=args.license,
    )

    print("\nVoice pack training started successfully!")

    # Extract train_id
    train_id = training_result.get("train_id")
    if not train_id:
        print("\n(!!!) Error: No train_id received from training start request")
        print(f"Training result: {json.dumps(training_result, indent=2)}")
        return 1

    print(f"Training ID: {train_id}")

    print("\nWaiting for training to complete...")
    voice_pack_id = check_training_status(train_id, args.license)

    if not voice_pack_id:
        print(f"\n(!!!) Voice pack '{args.pack_name}' training failed.")
        return 1

    print(f"\n(V) Voice pack '{args.pack_name}' training completed successfully!")
    print(f"Voice pack ID: {voice_pack_id}")

    print("\nActivating voice pack...")
    try:
        activate_voice_pack(voice_pack_id, args.license)

        # Check if voice pack is ready to use
        print("\nChecking voice pack status...")
        is_ready = check_voice_pack_status(voice_pack_id, args.license)

        if is_ready:
            print("(V) Voice pack is fully ready for voice conversion!")
        else:
            raise RuntimeError("Voice pack is not ready yet. Please contact support.")

        print(f"\nProcess completed successfully! Use {voice_pack_id=} for voice conversion.")
    except Exception as err:
        print(f"Warning: Failed to purchase voice pack {voice_pack_id=}: {err}")
        print("Voice pack training completed, but manual purchase may be required.")


if __name__ == '__main__':
    main()
