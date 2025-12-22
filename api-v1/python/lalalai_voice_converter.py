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

import os
import sys
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.parse import quote, unquote

try:
    import requests
except ImportError:
    print("ERROR: requests library is required. Install it with: pip install requests")
    sys.exit(1)


URL_API = "https://www.lalal.ai/api/v1/"


@dataclass
class VoiceChangeParameters:
    voice_pack_id: str
    accent: float
    tonality_reference: str  # "source_file" or "voice_pack"
    dereverb_enabled: bool
    splitter: str | None = None  # orion, perseus, phoenix, andromeda


def upload_file(file_path, license):
    """Upload file to LALAL.AI v1 API and return source_id."""
    url_for_upload = URL_API + "upload/"
    _, filename = os.path.split(file_path)
    headers = {
        "Content-Disposition": _make_content_disposition(filename),
        "X-License-Key": license,
    }
    with open(file_path, "rb") as f:
        response = requests.post(url_for_upload, data=f, headers=headers, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"Upload failed: {response.status_code} - {response.text}"
            )
        upload_result = response.json()
        return upload_result["id"]


def change_voice(source_id, license, params: VoiceChangeParameters):
    """Start voice change task using v1 API and return task_id."""
    url = URL_API + "change_voice/"
    headers = {
        "X-License-Key": license,
    }

    voice_change_params = {
        "source_id": source_id,
        "presets": {
            "voice_pack_id": params.voice_pack_id,
            "accent": params.accent,
            "tonality_reference": params.tonality_reference,
            "dereverb_enabled": params.dereverb_enabled,
        },
    }
    if params.splitter:
        voice_change_params["presets"]["splitter"] = params.splitter

    print("Voice convert request body:", voice_change_params)

    response = requests.post(url, json=voice_change_params, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Voice change failed: {response.status_code} - {response.text}"
        )
    result = response.json()
    task_id = result["task_id"]
    print(f"Start Voice convert task {task_id}")
    return task_id


def check_task(task_id, license):
    """Check task status using v1 API and wait until completion."""
    url_for_check = URL_API + "check/"
    headers = {
        "X-License-Key": license,
    }
    check_body = {"task_ids": [task_id]}

    preparation_phase = True

    while True:
        response = requests.post(
            url_for_check, json=check_body, headers=headers, timeout=30
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Check failed: {response.status_code} - {response.text}"
            )
        check_result = response.json()

        if task_id not in check_result["result"]:
            raise RuntimeError(f"Task {task_id} not found in response")

        task_status = check_result["result"][task_id]
        status = task_status.get("status")

        if status == "success":
            _update_percent("Progress: 100%\n")
            return task_status["result"]

        elif status == "cancelled":
            raise RuntimeError("Task was cancelled")

        elif status == "progress":
            progress = int(task_status["progress"])
            if progress == 0 and preparation_phase:
                print("Queue up...")
                preparation_phase = False
            elif progress > 0:
                _update_percent(f"Progress: {progress}%")

        else:
            raise RuntimeError(f"Unknown task status: {status}")

        time.sleep(5)


def download_file(url_for_download, output_path):
    """Download file from URL and save to output_path."""
    response = requests.get(url_for_download, stream=True, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Download failed: {response.status_code}")

    filename = _get_filename_from_content_disposition(
        response.headers.get("Content-Disposition", "")
    )
    file_path = os.path.join(output_path, filename)

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return file_path


def delete_tracks(source_id: str, license: str):
    """Delete source file and all resulting tracks from storage."""
    url_for_delete = URL_API + "delete/"
    headers = {
        "X-License-Key": license,
    }
    delete_body = {"source_id": source_id}

    response = requests.post(url_for_delete, json=delete_body, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Delete failed: {response.status_code} - {response.text}")


def process_file(license, source_id, output_path, params: VoiceChangeParameters, delete: bool):
    """Process a file through voice change, check, and download."""
    try:
        print(f'Processing the file "{source_id}"...')
        task_id = change_voice(source_id, license, params)

        processing_result = check_task(task_id, license)

        # Download the converted track (label: "converted_mix")
        downloaded_file = None
        for track in processing_result["tracks"]:
            if track["label"] == "converted_mix":
                url = track["url"]
                print(f'Downloading the converted file "{url}"...')
                downloaded_file = download_file(url, output_path)
                print(f'The track file has been downloaded to "{downloaded_file}"')

        if not downloaded_file:
            raise RuntimeError("Converted track not found in result")

        # This is optional step and could be skipped if you want to keep files on LALAL.AI storage
        if delete:
            print(f"Deleting source file and resulting tracks from lalalai storage (source_id: {source_id})...")
            delete_tracks(source_id, license)
            print("Files deleted from storage")
    except Exception as err:
        print(f'Cannot process the file "{source_id}": {err}')
        raise


def list_voice_packs(license):
    """List available voice packs for the user."""
    url = URL_API + "voice_packs/list/"
    headers = {
        "X-License-Key": license,
    }

    response = requests.post(url, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to list voice packs: {response.status_code} - {response.text}"
        )

    result = response.json()

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


def _make_content_disposition(filename, disposition="attachment"):
    try:
        filename.encode("ascii")
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f"{disposition}; {file_expr}"


def _strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid bool value {val!r}")


def _get_filename_from_content_disposition(header):
    """Parse Content-Disposition header to extract filename."""
    msg = EmailMessage()
    msg["content-disposition"] = header
    filename = msg.get_filename()
    if filename:
        return filename

    # Fallback: manual parsing for RFC 5987 encoded filenames
    if "filename*=" in header:
        for raw_segment in header.split(";"):
            segment = raw_segment.strip()
            if segment.startswith("filename*="):
                encoded = segment.split("=", 1)[1]
                if "''" in encoded:
                    encoding, quoted = encoded.split("''", 1)
                    return unquote(quoted, encoding)

    raise ValueError("Invalid header Content-Disposition")


def main():
    parser = ArgumentParser(
        description="LALAL.AI voice changer - v1 API example",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--license", required=True, type=str, default=SUPPRESS, help="license key"
    )
    parser.add_argument(
        "--input",
        required=False,
        type=str,
        default=None,
        help="input directory or a file",
    )
    parser.add_argument(
        "--uploaded_file_id",
        required=False,
        type=str,
        default=None,
        help="uploaded file id",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.dirname(os.path.realpath(__file__)),
        help="output directory",
    )
    parser.add_argument(
        "--voice_pack_id",
        type=str,
        default="ALEX_KAYE",
        help='pack_id in status "ready_to_use", choose from /voice_packs/list/',
    )
    parser.add_argument(
        "--accent",
        type=float,
        default=1.0,
        help="accent intensity (0.0-1.0, 1.0 by default). 0.0 preserves source accent, 1.0 applies voice pack accent",
    )
    parser.add_argument(
        "--tonality-reference",
        type=str,
        default="source_file",
        choices=["source_file", "voice_pack"],
        help='tonality reference: "source_file" preserves original pitch, "voice_pack" applies voice pack pitch',
    )
    parser.add_argument(
        "--dereverb-enabled",
        type=lambda x: bool(_strtobool(x)),
        default=False,
        choices=[True, False],
        help="remove echo",
    )
    parser.add_argument(
        "--splitter",
        type=str,
        default=None,
        choices=["orion", "perseus", "phoenix", "andromeda"],
        help="Splitter model to use. If None - the latest available model will be used.",
    )
    parser.add_argument(
        "--delete",
        type=lambda x: bool(_strtobool(x)),
        default=False,
        choices=[True, False],
        help="Delete source file and tracks from LALAL.AI storage after download",
    )
    parser.add_argument(
        "--list", action="store_true", help="list available voice packs and exit"
    )

    args = parser.parse_args()

    # Handle list command first
    if args.list:
        list_voice_packs(args.license)
        return

    if args.uploaded_file_id and args.input:
        raise ValueError(
            "You cannot specify both --uploaded_file_id and --input. Use one of them."
        )
    if not args.uploaded_file_id and not args.input:
        raise ValueError("You must specify either --uploaded_file_id or --input.")

    if args.input:
        print("Uploading the file", args.input)
        source_id = upload_file(file_path=args.input, license=args.license)
        print(
            f'The file "{args.input}" has been successfully uploaded (source_id: {source_id})'
        )
    else:
        print("Use uploaded file", args.uploaded_file_id)
        source_id = args.uploaded_file_id

    params = VoiceChangeParameters(
        voice_pack_id=args.voice_pack_id,
        accent=args.accent,
        tonality_reference=args.tonality_reference,
        dereverb_enabled=args.dereverb_enabled,
        splitter=args.splitter,
    )

    os.makedirs(args.output, exist_ok=True)
    process_file(args.license, source_id, args.output, params, args.delete)


if __name__ == "__main__":
    main()
