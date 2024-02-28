#!/usr/bin/python3

# Copyright (c) 2023 LALAL.AI
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


import cgi
import json
import os
import sys
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from urllib.parse import quote, unquote, urlencode
from urllib.request import urlopen, Request
import logging

logging.basicConfig(level=logging.INFO)

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
URL_API = "https://www.lalal.ai/api/"


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
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist")
    
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


def split_file(file_id, license, stem, filter_type, splitter):
    print(f"Split file {file_id}")
    url_for_split = URL_API + "split/"
    headers = {
        "Authorization": f"license {license}",
    }

    query_args = {'id': file_id, 'stem': stem, 'filter': filter_type, 'splitter': splitter}
    encoded_args = urlencode(query_args).encode('utf-8')
    request = Request(url_for_split, encoded_args, headers=headers)
    with urlopen(request) as response:
        split_result = json.load(response)
        if split_result["status"] == "error":
            raise RuntimeError(split_result["error"])


def batch_split_files(files_ids, license, stem, filter_type, splitter):
    print(f"split multiple files {files_ids}")
    url_for_split = URL_API + "split/"
    headers = {
        "Authorization": f"license {license}",
    }
    query_array = []
    for file_id in files_ids:
        query_array.append({"id": file_id, "stem": stem, "filter": filter_type, "splitter": splitter})

    query_args = {"params":json.dumps(query_array)}
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

        if task_state == "error":
            raise RuntimeError(check_result["task"]["error"])

        if task_state == "progress":
            progress = int(check_result["task"]["progress"])
            if progress == 0 and not is_queueup:
                print("Queue up...")
                is_queueup = True
            elif progress > 0:
                update_percent(f"Progress: {progress}%")

        if task_state == "success":
            update_percent("Progress: 100%\n")
            stem_track_url = check_result["split"]["stem_track"]
            back_track_url = check_result["split"]["back_track"]
            return stem_track_url, back_track_url

        time.sleep(15)


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


def batch_process_for_file(license, input_path, output_path, stem, filter_type, splitter):
    try:
        print(f'Uploading the file "{input_path}"...')
        file_id = upload_file(file_path=input_path, license=license)
        print(f'The file "{input_path}" has been successfully uploaded (file id: {file_id})')

        print(f'Processing the file "{input_path}"...')
        split_file(file_id, license, stem, filter_type, splitter)
        stem_track_url, back_track_url = check_file(file_id)

        print(f'Downloading the stem track file "{stem_track_url}"...')
        downloaded_file = download_file(stem_track_url, output_path)
        print(f'The stem track file has been downloaded to "{downloaded_file}"')

        print(f'Downloading the back track file "{back_track_url}"...')
        downloaded_file = download_file(back_track_url, output_path)
        print(f'The back track file has been downloaded to "{downloaded_file}"')

        print(f'The file "{input_path}" has been successfully split')
    except Exception as err:
        print(f'Cannot process the file "{input_path}": {err}')


def batch_process(license, input_path, output_path, stem, filter_type, splitter):
    if os.path.isfile(input_path):
        batch_process_for_file(license, input_path, output_path, stem, filter_type, splitter)
    else:
        for path in os.listdir(input_path):
            path = os.path.join(input_path, path)
            if os.path.isfile(path):
                batch_process_for_file(license, path, output_path, stem, filter_type, splitter)


def check_multiple_files(check_list, license):
    url_for_check = URL_API + "check/"
    headers = {
        "Authorization": f"license {license}",
    }

    query_args = {'id': ",".join(check_list.keys())}
    encoded_args = urlencode(query_args).encode('utf-8')

    request = Request(url_for_check, encoded_args, headers=headers)

    with urlopen(request) as response:
        check_result = json.load(response)

    if check_result["status"] == "error":
        raise RuntimeError(check_result["error"])

    for file_id, file_result in check_result["result"].items():
        if file_id not in check_list:
            continue
        try:
            task_state = file_result["task"]["state"]
            if task_state == "error":
                print(f"Error for file {file_id}")
                check_list[file_id]["state"] = "error"
                check_list[file_id]["finished"] = True

            if task_state == "success":
                if not check_list[file_id]["finished"]:
                    print(f"Progress: 100% for file {file_id}")
                    check_list[file_id]["end_time"] = time.perf_counter()
                    check_list[file_id]["state"] = "success"
                    check_list[file_id]["finished"] = True
                    check_list[file_id]["stem_track_url"] = file_result["split"]["stem_track"]
                    check_list[file_id]["back_track_url"] = file_result["split"]["back_track"]
                    check_list[file_id]["duration"] = file_result["split"]["duration"]
        except:
            check_list[file_id]["state"] = "error"
            check_list[file_id]["message"] = "unexpected error"
            pass


def batch_check(batch_status, license):
    while True:
        check_multiple_files(batch_status, license)
        not_finished = False
        for _, value in batch_status.items():
            if not value["finished"]:
                not_finished = True

        if not not_finished:
            break

        time.sleep(1)

    print("All files done")
    total_duration = 0.0
    max_time = 0.0
    for key, value in batch_status.items():
        if value["finished"] == True:
            elapsed_time_ms = value["end_time"] - value["start_time"]
            total_duration = total_duration + value["duration"]
            if elapsed_time_ms > max_time:
                max_time = elapsed_time_ms
            speed = elapsed_time_ms / value["duration"]
            print(f'time for item {key}: {elapsed_time_ms:.2f} sec, duration {value["duration"]}:  speed: {speed:.4f}')

    print(f'max process time: {max_time}, total_duration: {total_duration}, avg speed: {max_time/total_duration if total_duration > 0 else "undef"}')


def download_track(track_url, output_path, track_type):
    logging.info(f'Downloading the {track_type} "{track_url}"...')
    downloaded_file = download_file(track_url, output_path)
    logging.info(f'The {track_type} has been downloaded to "{downloaded_file}"')
    

def batch_download(batch_status, output_path):
    for _, value in batch_status.items():
        stem_track_url = value.get("stem_track_url")
        back_track_url = value.get("back_track_url")

        if stem_track_url:
            try:
                download_track(stem_track_url, output_path, "stem track file")
            except Exception as e:
                logging.error(f"Failed to download stem track from {stem_track_url}. Error: {e}")

        if back_track_url:
            try:
                download_track(back_track_url, output_path, "back track file")
            except Exception as e:
                logging.error(f"Failed to download back track from {back_track_url}. Error: {e}")


def batch_split_async(license, input_files_ids, output_path, stem, filter_type, splitter):
    batch_status = dict()
    batch_split_files(input_files_ids, license, stem, filter_type, splitter)
    for file_id in input_files_ids:
        batch_status[file_id] = {"start_time":time.perf_counter(), "finished": False }

    batch_check(batch_status, license)
    batch_download(batch_status, output_path)


def upload_and_get_file_id(file_path, license):
    print(f'Uploading the file "{file_path}"...')
    file_id = upload_file(file_path=file_path, license=license)
    print(f'The file "{file_path}" has been successfully uploaded (file id: {file_id})')
    return file_id


def batch_process_async(license, input_path, output_path, stem, filter_type, splitter):
    if os.path.isfile(input_path):
        batch_process_for_file(license, input_path, output_path, stem, filter_type, splitter)
        return
    
    files_in_dir = [os.path.join(input_path, file) for file in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, file))]
    files_ids = []    

    for file_path in files_in_dir:
        try:
            file_id = upload_and_get_file_id(file_path, license)
            files_ids.append(file_id)
        except Exception as err:
            print(f'Cannot upload the file "{file_path}": {err}')

    batch_split_async(license, files_ids, output_path, stem, filter_type, splitter)  

def create_parser():
    parser = ArgumentParser(description='Lalalai splitter', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--license', type=str, required=True, help='License key')
    parser.add_argument('--input', type=str, required=True, help='Input directory or a file')
    parser.add_argument('--output', type=str, default=CURRENT_DIR_PATH, help='Output directory')
    parser.add_argument('--stem', type=str, default='vocals', choices=['vocals', 'drum', 'bass', 'piano', 'electric_guitar', 'acoustic_guitar', 'synthesizer', 'voice', 'strings', 'wind'],
                        help='Stem selection option. Note: the stems "vocal" and "voice" support the fourth generation of the neural network named "Orion" (see also the --splitter option)')
    
    parser.add_argument('--filter', type=int, default=1, choices=[0, 1, 2], help='0 (mild), 1 (normal), 2 (aggressive)')
    parser.add_argument('--splitter', type=str, default='phoenix', choices=['orion', 'phoenix'],
                        help='Neural network selection option. Currently, the "Orion" neural network only supports the stems "vocal" and "voice".')

    parser.add_argument('--asyncmode', action='store_true', help="batch mode")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if not args.asyncmode:
        batch_process(args.license, args.input, args.output, args.stem, args.filter, args.splitter)
    else:
        print("Batch mode")
        batch_process_async(args.license, args.input, args.output, args.stem, args.filter, args.splitter)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(err)
