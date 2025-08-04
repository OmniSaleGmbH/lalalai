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


URL_API = "https://www.lalal.ai/api/"

_perseus_stems = ('vocals', 'voice', 'drum', 'piano', 'bass', 'electric_guitar', 'acoustic_guitar')
_orion_stems = ('vocals', 'voice', 'drum', 'piano', 'bass', 'electric_guitar', 'acoustic_guitar')
_phoenix_stems = ('vocals', 'voice', 'drum', 'piano', 'bass', 'electric_guitar', 'acoustic_guitar', 'synthesizer', 'strings', 'wind')


def update_percent(pct):
    pct = str(pct)
    sys.stdout.write("\b" * len(pct))
    sys.stdout.write(" " * len(pct))
    sys.stdout.write("\b" * len(pct))
    sys.stdout.write(pct)
    sys.stdout.flush()


def make_content_disposition(filename, disposition='attachment'):
    try:
        filename.encode('ascii')
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f'{disposition}; {file_expr}'


def upload_file(file_path, license):
    url_for_upload = URL_API + "upload/"
    _, filename = os.path.split(file_path)
    headers = {
        "Content-Disposition": make_content_disposition(filename),
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


def split_file(file_id, license, stem, splitter, enhanced_processing, noise_cancelling, dereverb_enabled):
    url_for_split = URL_API + "split/"
    headers = {
        "Authorization": f"license {license}",
    }
    query_args = {
        'id': file_id,
        'stem': stem,
        'splitter': splitter,
        'dereverb_enabled': dereverb_enabled,
    }

    if enhanced_processing is not None:
        query_args['enhanced_processing_enabled'] = enhanced_processing
    if noise_cancelling is not None:
        query_args['noise_cancelling_level'] = noise_cancelling

    # What you send to server
    print("Split task request body:", query_args)

    encoded_args = urlencode(query_args).encode('utf-8')
    request = Request(url_for_split, encoded_args, headers=headers)
    with urlopen(request) as response:
        split_result = json.load(response)
        if split_result["status"] == "error":
            raise RuntimeError(split_result["error"])


def check_file(file_id):
    url_for_check = URL_API + "check/?"
    query_args = {'id': file_id}
    encoded_args = urlencode(query_args)

    is_queueup = False

    while True:
        with urlopen(url_for_check + encoded_args) as response:
            check_result = json.load(response)

        if check_result["status"] == "error":
            raise RuntimeError(check_result["error"])

        task_state = check_result["task"]["state"]

        if task_state == "success":
            update_percent("Progress: 100%\n")
            return check_result["split"]

        elif task_state == "error":
            raise RuntimeError(check_result["task"]["error"])

        elif task_state == "progress":
            progress = int(check_result["task"]["progress"])
            if progress == 0 and not is_queueup:
                if 'presets' in check_result and 'split' in check_result['presets']:
                    # Settings extracted by server
                    print("Using settings", check_result['presets']['split'])
                print("Queue up...")
                is_queueup = True
            elif progress > 0:
                update_percent(f"Progress: {progress}%")

        else:
            raise NotImplementedError('Unknown track state', task_state)

        time.sleep(15)


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


def get_filename_from_content_disposition(header):
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


def download_file(url_for_download, output_path):
    with urlopen(url_for_download) as response:
        filename = get_filename_from_content_disposition(response.headers["Content-Disposition"])
        file_path = os.path.join(output_path, filename)
        with open(file_path, 'wb') as f:
            while (chunk := response.read(8196)):
                f.write(chunk)
    return file_path


def batch_process_for_file(license, input_path, output_path, stem, splitter, enhanced_processing, noise_cancelling, dereverb_enabled):
    try:
        print(f'Uploading the file "{input_path}"...')
        file_id = upload_file(file_path=input_path, license=license)
        print(f'The file "{input_path}" has been successfully uploaded (file id: {file_id})')

        print(f'Processing the file "{input_path}"...')
        split_file(file_id, license, stem, splitter, enhanced_processing, noise_cancelling, dereverb_enabled)
        split_result = check_file(file_id)

        for url in (split_result['stem_track'], split_result['back_track']):
            print(f'Downloading the track file "{url}"...')
            downloaded_file = download_file(url, output_path)
            print(f'The track file has been downloaded to "{downloaded_file}"')

        print(f'The file "{input_path}" has been successfully split')
    except Exception as err:
        print(f'Cannot process the file "{input_path}": {err}')


def batch_process(license, input_path, output_path, stem, splitter, enhanced_processing, noise_cancelling, dereverb_enabled):
    if os.path.isfile(input_path):
        batch_process_for_file(license, input_path, output_path, stem, splitter, enhanced_processing, noise_cancelling, dereverb_enabled)
    else:
        for path in os.listdir(input_path):
            full_path = os.path.join(input_path, path)
            if os.path.isfile(full_path):
                batch_process_for_file(license, full_path, output_path, stem, splitter, enhanced_processing, noise_cancelling, dereverb_enabled)


def _validate_stem(args):
    if args.splitter == 'perseus' and args.stem not in _perseus_stems:
        raise ValueError(f'{args.splitter} splitter does not support stem "{args.stem}". Should be one of {_perseus_stems}')
    if args.splitter == 'orion' and args.stem not in _orion_stems:
        raise ValueError(f'{args.splitter} splitter does not support stem "{args.stem}". Should be one of {_orion_stems}')
    if args.splitter == 'phoenix' and args.stem not in _phoenix_stems:
        raise ValueError(f'{args.splitter} splitter does not support stem "{args.stem}". Should be one of {_phoenix_stems}')


def _get_latest_available_splitter(stem):
    if stem in _perseus_stems:
        return 'perseus'
    if stem in _orion_stems:
        return 'orion'
    return 'phoenix'


splitter_help = f'''
The type of neural network used to split audio.
Possible values are 'phoenix', 'orion' or 'perseus'.
If parameter is not provided - automatically choose most effective splitter for selected stem.
Perseus stems: {_perseus_stems}.
Orion stems: {_orion_stems}.
Phoenix stems: {_phoenix_stems}.'''


def main():
    parser = ArgumentParser(description='Lalalai splitter', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--license', required=True, type=str, default=SUPPRESS, help='license key')
    parser.add_argument('--input', required=True, type=str, default=SUPPRESS, help='input directory or a file')
    parser.add_argument('--output', type=str, default=os.path.dirname(os.path.realpath(__file__)), help='output directory')
    parser.add_argument('--splitter', type=str, choices=['phoenix', 'orion','perseus'], help=splitter_help)
    parser.add_argument('--stem', type=str, default='vocals', help='List of comma-separated stem options. One of ("vocals", "voice", "drum", "bass", "piano", "electric_guitar, "acoustic_guitar", "synthesizer", "strings", "wind")')
    parser.add_argument('--enhanced-processing', type=lambda x: bool(_strtobool(x)), default=False, choices=[True, False], help='all stems, except "voice"')
    parser.add_argument('--noise-cancelling', type=int, default=1, choices=[0, 1, 2], help='noise cancelling level for "voice" stem: (0: mild, 1: normal, 2: aggressive)')
    parser.add_argument('--dereverb_enabled', type=lambda x: bool(_strtobool(x)), default=False, choices=[True, False], help='remove echo')

    args = parser.parse_args()

    _validate_stem(args)
    args.splitter = args.splitter or _get_latest_available_splitter(args.stem)

    if args.stem == 'voice':
        args.enhanced_processing = None
    else:
        args.noise_cancelling = None

    os.makedirs(args.output, exist_ok=True)
    batch_process(args.license, args.input, args.output, args.stem, args.splitter, args.enhanced_processing, args.noise_cancelling, args.dereverb_enabled)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(err)
