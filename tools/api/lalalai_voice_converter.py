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
    raise RuntimeError("This script requires Python 3.12 or earlier for cgi module compatibility. Actual version is: ", sys.version_info)

import cgi
import json
import os

import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
from urllib.parse import quote, unquote, urlencode
from urllib.request import urlopen, Request

from dataclasses import dataclass

URL_API = "https://www.lalal.ai/api/"

@dataclass
class VoiceChangeParameters:
    voice_pack_id: str
    accent_enhance: float
    pitch_shifting: int
    dereverb_enabled: bool


def upload_file(file_path, license):
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


def change_voice(file_id, license, params: VoiceChangeParameters):
    url = URL_API + "change_voice/"
    headers = {
        "Authorization": f"license {license}",
    }

    query_args = {
        'id': file_id,
        'voice': params.voice_pack_id,
        'accent_enhance': params.accent_enhance,
        'pitch_shifting': params.pitch_shifting,
        'dereverb_enabled': params.dereverb_enabled
    }
    print("Voice convert request body:", query_args)

    encoded_args = urlencode(query_args).encode('utf-8')
    request = Request(url, encoded_args, headers=headers)
    with urlopen(request) as response:
        split_result = json.load(response)
        if split_result["status"] == "error":
            raise RuntimeError(split_result["error"])
        print(f"Start Voice convert task {split_result['task_id']}")


def check_file(file_id):
    url_for_check = URL_API + "check/?"
    query_args = {'id': file_id}
    encoded_args = urlencode(query_args)

    preparation_phase = True

    while True:
        with urlopen(url_for_check + encoded_args) as response:
            check_result = json.load(response)

        if check_result["status"] == "error":
            raise RuntimeError(check_result["error"])

        task_state = check_result["task"]["state"]

        if task_state == "success":
            _update_percent("Progress: 100%\n")
            return check_result["split"]

        elif task_state == "error":
            raise RuntimeError(check_result["task"]["error"])

        elif task_state == "progress":
            progress = int(check_result["task"]["progress"])
            if progress == 0 and preparation_phase:
                if 'presets' in check_result and 'split' in check_result['presets']:
                    print("Using settings", check_result['presets']['split'])
                print("Queue up...")
                preparation_phase = False
            elif progress > 0:
                _update_percent(f"Progress: {progress}%")

        else:
            raise NotImplementedError('Unknown track state', task_state)

        time.sleep(15)


def download_file(url_for_download, output_path):
    with urlopen(url_for_download) as response:
        filename = _get_filename_from_content_disposition(response.headers["Content-Disposition"])
        file_path = os.path.join(output_path, filename)
        with open(file_path, 'wb') as f:
            while (chunk := response.read(8196)):
                f.write(chunk)
    return file_path


def process_file(license, file_id, output_path, params: VoiceChangeParameters):
    try:
        print(f'Processing the file "{file_id}"...')
        change_voice(file_id, license, params)
        processing_result = check_file(file_id)

        print(f'Downloading the converted file "{processing_result['back_track']}"...')
        downloaded_file = download_file(processing_result['back_track'], output_path)
        print(f'The track file has been downloaded to "{downloaded_file}"')
    except Exception as err:
        print(f'Cannot process the file "{file_id}": {err}')
        raise


def list_voice_packs(license):
    """List available voice packs for the user"""
    url = URL_API + "voice_packs/list/"
    headers = {
        "Authorization": f"license {license}",
    }

    request = Request(url, headers=headers)
    with urlopen(request) as response:
        result = json.load(response)
        if result["status"] == "error":
            raise RuntimeError(result["error"])

        # Filter only ready_to_use packs
        ready_packs = [pack for pack in result["packs"] if pack["ready_to_use"]]

        # Print table header
        print(f"{'pack_id':<50} {'name':<50}")
        print("-" * 105)

        # Print each pack
        for pack in ready_packs:
            pack_id = pack["pack_id"]
            name = pack["name"]

            print(f"{pack_id:<50} {name:<50}")


def _update_percent(pct):
    pct = str(pct)
    sys.stdout.write("\b" * len(pct))
    sys.stdout.write(" " * len(pct))
    sys.stdout.write("\b" * len(pct))
    sys.stdout.write(pct)
    sys.stdout.flush()


def _make_content_disposition(filename, disposition='attachment'):
    try:
        filename.encode('ascii')
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f'{disposition}; {file_expr}'


def _strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"invalid bool value {val!r}")


def _get_filename_from_content_disposition(header):
    _, params = cgi.parse_header(header)
    filename = params.get('filename')
    if filename:
        return filename
    filename = params.get('filename*')
    if filename:
        encoding, quoted = filename.split("''")
        unquoted = unquote(quoted, encoding)
        return unquoted
    raise ValueError('Invalid header Content-Disposition')


def main():
    parser = ArgumentParser(description='Lalalai voice changer', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--license', required=True, type=str, default=SUPPRESS, help='license key')
    parser.add_argument('--input', required=False, type=str, default=None, help='input directory or a file')
    parser.add_argument('--uploaded_file_id', required=False, type=str, default=None, help='uploaded file id')
    parser.add_argument('--output', type=str, default=os.path.dirname(os.path.realpath(__file__)), help='output directory')
    parser.add_argument('--voice_pack_id', type=str, default="ALEX_KAYE", help='pack_id in status "ready_to_use", choose from https://www.lalal.ai/api/voice_packs/list/ (must be logged in)')
    parser.add_argument('--accent_enhance', type=float, default=1, help='enable accent enhance (0.0-1.0, 1.0 by default)')
    parser.add_argument('--pitch_shifting', type=lambda x: bool(_strtobool(x)), default=True, choices=[True, False],)
    parser.add_argument('--dereverb_enabled', type=lambda x: bool(_strtobool(x)), default=False, choices=[True, False], help='remove echo')
    parser.add_argument('--list', action='store_true', help='list available voice packs and exit')

    args = parser.parse_args()

    # Handle list command first
    if args.list:
        list_voice_packs(args.license)
        return

    if args.uploaded_file_id and args.input:
        raise ValueError("You cannot specify both --uploaded_file_id and --input. Use one of them.")
    if not args.uploaded_file_id and not args.input:
        raise ValueError("You must specify either --uploaded_file_id or --input.")

    if args.input:
        print('Uploading the file', args.input)
        file_id = upload_file(file_path=args.input, license=args.license)
        print(f'The file "{args.input}" has been successfully uploaded (file id: {file_id})')
    else:
        print('Use uploaded file', args.uploaded_file_id)
        file_id = args.uploaded_file_id

    params = VoiceChangeParameters(
        voice_pack_id=args.voice_pack_id,
        accent_enhance=args.accent_enhance,
        pitch_shifting=args.pitch_shifting,
        dereverb_enabled=args.dereverb_enabled
    )

    os.makedirs(args.output, exist_ok=True)
    process_file(args.license, file_id, args.output, params)


if __name__ == '__main__':
    main()
