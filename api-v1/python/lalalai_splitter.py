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

# Stem definitions for /split/voice_clean/ endpoint
_voice_clean_stems = ("voice",)
# Stem definitions for /split/demuser/ endpoint
_demuser_stems = ("music",)
# Stem definitions for /split/stem_separator/ endpoint
_stem_separator_stems = (
    "vocals",
    "drum",
    "piano",
    "bass",
    "electric_guitar",
    "acoustic_guitar",
    "synthesizer",
    "strings",
    "wind",
)


@dataclass
class VoiceCleanParams:
    """Parameters for /split/voice_clean/ endpoint."""

    source_id: str
    noise_cancelling_level: int  # 0, 1, or 2
    dereverb_enabled: bool = False
    splitter: str | None = None  # orion, perseus, phoenix, andromeda


@dataclass
class DemuserParams:
    """Parameters for /split/demuser/ endpoint."""

    source_id: str
    dereverb_enabled: bool = False


@dataclass
class StemSeparatorParams:
    """Parameters for /split/stem_separator/ endpoint."""

    source_id: str
    stem: str  # vocals, drum, piano, etc.
    extraction_level: str  # deep_extraction or clear_cut
    dereverb_enabled: bool = False
    multivocal: str | None = None  # lead_back for vocals
    splitter: str | None = None  # orion, perseus, phoenix, andromeda


def _update_percent(pct):
    pct = str(pct)
    sys.stdout.write("\b" * len(pct))
    sys.stdout.write(" " * len(pct))
    sys.stdout.write("\b" * len(pct))
    sys.stdout.write(pct)
    sys.stdout.flush()


def make_content_disposition(filename, disposition="attachment"):
    try:
        filename.encode("ascii")
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f"{disposition}; {file_expr}"


def upload_file(file_path, license):
    """Upload file to LALAL.AI v1 API and return source_id."""
    url_for_upload = URL_API + "upload/"
    _, filename = os.path.split(file_path)
    headers = {
        "Content-Disposition": make_content_disposition(filename),
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


def split_voice_clean(params: VoiceCleanParams, license: str) -> str:
    """Start voice cleaning task using v1 API and return task_id."""
    url = URL_API + "split/voice_clean/"
    headers = {"X-License-Key": license}

    presets = {
        "stem": "voice",
        "noise_cancelling_level": params.noise_cancelling_level,
    }
    if params.dereverb_enabled:
        presets["dereverb_enabled"] = True
    if params.splitter:
        presets["splitter"] = params.splitter

    split_params = {
        "source_id": params.source_id,
        "presets": presets,
    }

    print("Split task request body:", split_params)

    response = requests.post(url, json=split_params, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Split failed: {response.status_code} - {response.text}")
    return response.json()["task_id"]


def split_demuser(params: DemuserParams, license: str) -> str:
    """Start music removal task using v1 API and return task_id."""
    url = URL_API + "split/demuser/"
    headers = {"X-License-Key": license}

    presets = {
        "stem": "music",
    }
    if params.dereverb_enabled:
        presets["dereverb_enabled"] = True

    split_params = {
        "source_id": params.source_id,
        "presets": presets,
    }

    print("Split task request body:", split_params)

    response = requests.post(url, json=split_params, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Split failed: {response.status_code} - {response.text}")
    return response.json()["task_id"]


def split_stem_separator(params: StemSeparatorParams, license: str) -> str:
    """Start stem separation task using v1 API and return task_id."""
    url = URL_API + "split/stem_separator/"
    headers = {"X-License-Key": license}

    presets = {
        "stem": params.stem,
        "extraction_level": params.extraction_level,
    }
    if params.dereverb_enabled:
        presets["dereverb_enabled"] = True
    if params.multivocal and params.stem == "vocals":
        presets["multivocal"] = params.multivocal
    if params.splitter:
        presets["splitter"] = params.splitter

    split_params = {
        "source_id": params.source_id,
        "presets": presets,
    }

    print("Split task request body:", split_params)

    response = requests.post(url, json=split_params, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Split failed: {response.status_code} - {response.text}")
    return response.json()["task_id"]


def split_file(
    params: VoiceCleanParams | DemuserParams | StemSeparatorParams, license: str
) -> str:
    """Start split task using v1 API and return task_id."""
    if isinstance(params, VoiceCleanParams):
        return split_voice_clean(params, license)
    elif isinstance(params, DemuserParams):
        return split_demuser(params, license)
    elif isinstance(params, StemSeparatorParams):
        return split_stem_separator(params, license)
    else:
        raise ValueError(f"Unsupported params type: {type(params)}")


def check_task(task_id, license):
    """Check task status using v1 API and wait until completion."""
    url_for_check = URL_API + "check/"
    headers = {
        "X-License-Key": license,
    }
    check_body = {"task_ids": [task_id]}

    is_queued = False

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
            print("Using settings:", task_status.get("presets"))
            return task_status["result"]

        elif status == "cancelled":
            raise RuntimeError("Task was cancelled")

        elif status == "progress":
            progress = int(task_status.get("progress", 0))
            if progress == 0 and not is_queued:
                print("Task queued, processing...")
                print("Using settings:", task_status.get("presets"))
                is_queued = True
            elif progress > 0:
                _update_percent(f"Progress: {progress}%")

        else:
            raise RuntimeError(f"Unknown task status: {status}")

        time.sleep(5)


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


def get_filename_from_content_disposition(header):
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


def download_file(url_for_download, output_path):
    """Download file from URL and save to output_path."""
    response = requests.get(url_for_download, stream=True, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Download failed: {response.status_code}")

    filename = get_filename_from_content_disposition(
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


def build_split_params(
    source_id: str,
    stem: str,
    noise_cancelling: int,
    dereverb_enabled: bool,
    extraction_level: str,
    multivocal: str | None,
    splitter: str | None,
) -> VoiceCleanParams | DemuserParams | StemSeparatorParams:
    """Build appropriate params object based on stem type."""
    if stem == "voice":
        return VoiceCleanParams(
            source_id=source_id,
            noise_cancelling_level=noise_cancelling,
            dereverb_enabled=dereverb_enabled,
            splitter=splitter,
        )
    elif stem == "music":
        return DemuserParams(
            source_id=source_id,
            dereverb_enabled=dereverb_enabled,
        )
    else:
        return StemSeparatorParams(
            source_id=source_id,
            stem=stem,
            extraction_level=extraction_level,
            dereverb_enabled=dereverb_enabled,
            multivocal=multivocal,
            splitter=splitter,
        )


def batch_process_for_file(
    license,
    input_path,
    output_path,
    stem,
    noise_cancelling,
    dereverb_enabled,
    extraction_level,
    multivocal,
    delete,
    splitter,
):
    """Process a single file through upload, split, check, and download."""
    try:
        print(f'Uploading the file "{input_path}"...')
        source_id = upload_file(file_path=input_path, license=license)
        print(
            f'The file "{input_path}" has been successfully uploaded (source_id: {source_id})'
        )

        print(f'Processing the file "{input_path}"...')
        params = build_split_params(
            source_id,
            stem,
            noise_cancelling,
            dereverb_enabled,
            extraction_level,
            multivocal,
            splitter,
        )
        task_id = split_file(params, license)
        print(f"Task started (task_id: {task_id})")

        split_result = check_task(task_id, license)

        # Download all tracks from result
        for track in split_result["tracks"]:
            url = track["url"]
            track_label = track["label"]
            print(f'Downloading the {track_label} track from "{url}"...')
            downloaded_file = download_file(url, output_path)
            print(f'The {track_label} track has been downloaded to "{downloaded_file}"')

        print(f'The file "{input_path}" has been successfully split')

        # This is optional step and could be skipped if you want to keep files on LALAL.AI storage
        if delete:
            print(f"Deleting source file and resulting tracks from lalalai storage (source_id: {source_id})...")
            delete_tracks(source_id, license)
            print("Files deleted from storage")
    except Exception as err:
        print(f'Cannot process the file "{input_path}": {err}')


def batch_process(
    license,
    input_path,
    output_path,
    stem,
    noise_cancelling,
    dereverb_enabled,
    extraction_level,
    multivocal,
    delete,
    splitter,
):
    """Process file(s) - supports single file or directory."""
    if os.path.isfile(input_path):
        batch_process_for_file(
            license,
            input_path,
            output_path,
            stem,
            noise_cancelling,
            dereverb_enabled,
            extraction_level,
            multivocal,
            delete,
            splitter,
        )
    else:
        print("Check documentation for 'Batch Split', it could help you run multiple splits at one request.")
        for path in os.listdir(input_path):
            full_path = os.path.join(input_path, path)
            if os.path.isfile(full_path):
                batch_process_for_file(
                    license,
                    full_path,
                    output_path,
                    stem,
                    noise_cancelling,
                    dereverb_enabled,
                    extraction_level,
                    multivocal,
                    delete,
                    splitter,
                )


def _validate_stem(stem):
    """Validate stem is supported by v1 API."""
    valid_stems = _voice_clean_stems + _demuser_stems + _stem_separator_stems
    if stem not in valid_stems:
        raise ValueError(f'Unsupported stem "{stem}". Must be one of {valid_stems}')


def _validate_multivocal(stem, multivocal):
    # multivocal is only for vocals stem
    if multivocal and stem != "vocals":
        raise ValueError(
            f'--multivocal parameter is only supported for "vocals" stem, not "{stem}"'
        )


def main():
    parser = ArgumentParser(
        description="LALAL.AI splitter - v1 API example",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--license",
        required=True,
        type=str,
        default=SUPPRESS,
        help="License key (X-License-Key header)",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=str,
        default=SUPPRESS,
        help="Input directory or a file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.dirname(os.path.realpath(__file__)),
        help="Output directory",
    )
    parser.add_argument(
        "--stem",
        type=str,
        default="vocals",
        choices=list(_voice_clean_stems + _demuser_stems + _stem_separator_stems),
        help='Stem to extract. Use "voice" for voice cleaning, "music" for music removal, or any instrumental stem',
    )
    parser.add_argument(
        "--noise-cancelling",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help='Noise cancelling level for "voice" stem: (0: mild, 1: normal, 2: aggressive)',
    )
    parser.add_argument(
        "--dereverb-enabled",
        type=lambda x: bool(_strtobool(x)),
        default=False,
        choices=[True, False],
        help="Remove echo (reverb removal)",
    )
    parser.add_argument(
        "--extraction-level",
        type=str,
        default="deep_extraction",
        choices=["deep_extraction", "clear_cut"],
        help='Extraction level for stem_separator: "deep_extraction" (more details, may bleed) or "clear_cut" (cleaner, less detail)',
    )
    parser.add_argument(
        "--multivocal",
        type=str,
        default=None,
        choices=["lead_back"],
        help='For "vocals" stem: use "lead_back" to separate lead and backing vocals',
    )
    parser.add_argument(
        "--splitter",
        type=str,
        default=None,
        choices=["orion", "perseus", "phoenix", "andromeda"],
        help="Splitter model to use. If None - the latest available model for the selected stems will be used.",
    )
    parser.add_argument(
        "--delete",
        type=lambda x: bool(_strtobool(x)),
        default=False,
        choices=[True, False],
        help="Delete source file and tracks from LALAL.AI storage after download",
    )

    args = parser.parse_args()

    _validate_stem(args.stem)
    _validate_multivocal(args.stem, args.multivocal)

    # Set noise_cancelling to None for non-voice stems
    noise_cancelling = args.noise_cancelling if args.stem == "voice" else None

    os.makedirs(args.output, exist_ok=True)
    batch_process(
        args.license,
        args.input,
        args.output,
        args.stem,
        noise_cancelling,
        args.dereverb_enabled,
        args.extraction_level,
        args.multivocal,
        args.delete,
        args.splitter,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
