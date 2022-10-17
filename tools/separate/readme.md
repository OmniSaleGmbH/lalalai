# Music Source Separation Tool


## Install

Download the [run.sh](https://github.com/openmediaco/lalalai/tree/master/tools/separate/run.sh) and give it execute permission.


## Description

This script is to be used with the [LALAL.AI](https://www.lalal.ai) original separation tool image.
It runs a container, passes all the
specified parameters to it, captures the separation tool's output, and saves all the results to a specified directory.

If you have issues using it, please consider contacting the [lalal.ai support team](mailto:support@lalal.ai).


## Usage
```bash
$ run.sh [-h] -i MIX_PATH [MIX_PATH ...] -o DIR_PATH -l LICENSE_KEY [-d FLOAT_VAL] [-s {vocals,drum,bass,piano,electric_guitar}] [-m {mild,normal,aggressive}] [-e DEVICE]
```

| Required arguments | Description |
| ------------- | ------------- |
| `-i/--input_files MIX_PATH [MIX_PATH ...]` | Path to an input audio file (or several paths, separated by a whitespace.) Note: all the file must exist |
| `-o/--out_dir DIR_PATH` | Path to an output directory to put the results to. It will be created if not exists |
| `-l/--license_key LICENSE_KEY` | Your license key |

| Optional arguments | Description |
| ------------- | ------------- |
| `-d/--duration FLOAT_VAL` | Max duration of audio to process (in seconds). If specified, the input audio(s) will be stripped to that duration silently. Must be greater than 0. By default the separator will process all the track |
| `-s/--source {vocals,drum,bass,piano,electric_guitar}` | Source to extract. Use this, to pick which stem (+ its residual) you want to extract. Only one source can be specified at a time. Default: vocals. |
| `-m/--mode {mild,normal,aggressive}` | Separation mode. Works only for vocals source. For other sources ignored. Default: normal |
| `-e/--device {auto,cpu,gpu[:<gpu_id>]}` | The device to run separator on. gpu_id is an integer, starting from 0. For single-gpu machines you can pass auto (gpu will be selected if it is available), gpu or gpu:0. For multi-gpu machines auto will choose the first gpu, that is gpu:0. Default: auto. |

Thank you for being with us.
