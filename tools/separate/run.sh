#!/usr/bin/env bash

LALALAI_CONTAINER_NAME='lalalai-separator'
LALALAI_IMAGE_NAME='lalalai/separator'


replace_long_args() {
  args=( )

  for arg; do
    case "$arg" in
      --help)         args+=( -h ) ;;
      --input_files)  args+=( -i ) ;;
      --out_dir)      args+=( -o ) ;;
      --duration)     args+=( -d ) ;;
      --source)       args+=( -s ) ;;
      --mode)         args+=( -m ) ;;
      --device)       args+=( -e ) ;;
      --license_key)  args+=( -l ) ;;
      *)              args+=( "$arg" ) ;;
    esac
  done
}


show_usage() {
  USAGE=$(cat <<-END
Music Source Separation Tool
============================

Description
-----------
This script is to be used with the lalal.ai original separation tool image. It runs a container, passes all the
specified parameters to it, captures the separation tool's output, and saves all the results to a specified directory.
If you have issues using it, please consider contacting the lalal.ai support team. Thank you for being with us.

Usage
-----
./run.sh [-h] -i MIX_PATH [MIX_PATH ...] -o DIR_PATH -l LICENSE_KEY [-d FLOAT_VAL] [-s {vocals,drum,bass,piano,electric_guitar}] [-m {mild,normal,aggressive}] [-e DEVICE]

### Required arguments
-i/--input_files MIX_PATH [MIX_PATH ...]
    Path to an input audio file (or several paths, separated by a whitespace.) Note: all the file must exist.
-o/--out_dir DIR_PATH
    Path to an output directory to put the results to. It will be created if not exists.
-l/--license_key LICENSE_KEY
    Your license key.

### Optional arguments
-d/--duration FLOAT_VAL
    Max duration of audio to process (in seconds). If specified, the input audio(s) will be stripped to that duration
    silently. Must be greater than 0. By default the separator will process all the track.
-s/--source {vocals,drum,bass,piano,electric_guitar}
    Source to extract. Use this, to pick which stem (+ its residual) you want to extract. Only one source can be
    specified at a time. Default: vocals.
-m/--mode {mild,normal,aggressive}
    Separation mode. Works only for vocals source. For other sources ignored. Default: normal.
-e/--device {auto,cpu,gpu[:<gpu_id>]}
    The device to run separator on. gpu_id is an integer, starting from 0. For single-gpu machines you can pass auto
    (gpu will be selected if it is available), gpu or gpu:0. For multi-gpu machines auto will choose the first gpu,
    that is gpu:0. Default: auto.
END
)
  echo "$USAGE"
}

check_duplicated_option() {
  if [[ "$1" == "true" ]]; then
    echo 'Please, remove all the duplicated arguments and try again.'
    exit 2
  fi
}


invalid_argument() {
  echo "Unknown argument: $OPTION with value ${OPTARG}. Please, use -h/--help option to get supported arguments. " \
        "If you've provided only supported arguments, check if the arguments are specified without error. "        \
        "There's no whitespaces in the arguments' values and the command is properly formatted."
  exit 2
}


parse_input_paths() {
  IFS=',' read -ra input_paths <<< "$OPTARG"
  input_files=( )

  for path in "${input_paths[@]}"; do
    input_files+=( "$(realpath "$path")" )
  done
}


parse_arg() {
  case $OPTION in
    h)
      show_usage
      exit 0
      ;;
    i)
      check_duplicated_option "$input_files_arg_seen"
      input_files_arg_seen="true"
      parse_input_paths
      ;;
    o)
      check_duplicated_option "$out_dir_arg_seen"
      out_dir_arg_seen="true"
      out_dir="$(realpath "$OPTARG")"
      ;;
    d)
      check_duplicated_option "$duration_arg_seen"
      duration_arg_seen="true"
      duration="$OPTARG"
      ;;
    s)
      check_duplicated_option "$source_arg_seen"
      source_arg_seen="true"
      source="$OPTARG"
      ;;
    m)
      check_duplicated_option "$mode_arg_seen"
      mode_arg_seen="true"
      mode="$OPTARG"
      ;;
    e)
      check_duplicated_option "$device_arg_seen"
      device_arg_seen="true"
      device="$OPTARG"
      ;;
    l)
      check_duplicated_option "$license_key_arg_seen"
      license_key_arg_seen="true"
      license_key="$OPTARG"
      ;;
    *) invalid_argument ;;
  esac
}


validate_args() {
  if [ -z ${input_files+x} ]; then
    echo "-i/--input_files is a required parameter. Please, specify it and try again."
    exit 2
  else
    for path in "${input_files[@]}"; do
      if [ ! -f "$path" ]; then
        echo "Error: file '$path' does not exist. Please, correct the path and try again."
        exit 2
      fi
    done
  fi

  if [ -z ${out_dir+x} ]; then
    echo "-o/--out_dir is a required parameter. Please, specify it and try again. " \
    "You can specify a path to non-existent directory. In that case it will be created."
    exit 2
  fi

  if [ -z ${license_key+x} ]; then
    echo "-l/--license_key is a required parameter. Please, specify it and try again."
    exit 2
  else
    local lk_pat="^[0-9a-fA-F]{8,32}$"
    if [[ ! $license_key =~ $lk_pat ]]; then
      echo "Invalid license key. Please, check it again, fix, and repeat."
      exit 2
    fi
  fi

  if [ -n "${duration+x}" ]; then
    local dur_pat="^[0-9]+.?[0-9]*$"
    if [[ ! $duration =~ $dur_pat ]]; then
      echo "Duration must be a valid floating-point number. Please, retry specifying a proper duration."
      exit 2
    fi
  fi

  if [ -n "${source+x}" ]; then
    local allowed_sources=( "vocals" "bass" "drum" "piano" "electric_guitar" )
    if [[ ! "${allowed_sources[*]}" =~ $source ]]; then
      echo "Source can be one of: {vocals, bass, drum, piano, electric_guitar}. " \
           "Please, specify the right source and try again."
      exit 2
    fi
  fi

  if [ -n "${mode+x}" ]; then
    local allowed_modes=( "mild" "normal" "aggressive" )
    if [[ ! "${allowed_modes[*]}" =~ $mode ]]; then
      echo "Mode can be one of: {mild, normal, aggressive}. Please, specify the right mode and try again."
      exit 2
    fi
  fi

  if [ -n "${device+x}" ]; then
    local allowed_devices=( "auto" "cpu" "gpu" )
    local gpu_pat="^gpu:[0-9]+$"
    if [[ ! "${allowed_devices[*]}" =~ $device && ! $device =~ $gpu_pat ]]; then
      echo "Device can be one of: {cpu, auto, gpu[:<gpu_id>]}. Please, specify the right device and try again."
      exit 2
    fi
  fi
}


parse_args() {
  local args
  replace_long_args "$@"
  set -- "${args[@]}" # actual replace

  while getopts "hi:o:d:s:m:e:l:" OPTION; do
    : "$OPTION" "$OPTARG"
    parse_arg
  done

  validate_args
}

should_run_with_sudo() {
  if groups "$USER" | grep -q '\bdocker\b' || [ "$(id -u)" = 0 ]; then
    return 1 # FALSE
  else
    return 0 # TRUE
  fi
}

add_mount_flags() {
  run_command+=(-v "$out_dir:$out_dir:Z")
  for path in "${input_files[@]}"; do
    local parent_path
    parent_path="$(dirname "$path")"
    run_command+=(-v "$parent_path:$parent_path:Z")
  done
}


join_by() {
  local IFS="$1"
  shift
  echo "$*"
}


add_separator_flags() {
  run_command+=(--input_files "$(join_by ' ' "${input_files[@]}")")
  run_command+=(--out_dir "$out_dir")
  if [ -n "${duration+x}" ]; then run_command+=(--duration "$duration"); fi
  if [ -n "${source+x}" ]; then run_command+=(--source "$source"); fi
  if [ -n "${mode+x}" ]; then run_command+=(--mode "$mode"); fi
  if [ -n "${device+x}" ]; then run_command+=(--device "$device"); fi

  run_command+=(--uid_gid "$(id -u "$USER"):$(id -g "$USER")")
}


compound_run_command() {
  if should_run_with_sudo; then
    run_command=(sudo)
  else
    run_command=( )
  fi

  run_command+=(docker run --tty)
  add_mount_flags
  run_command+=(--cap-add=ALL --gpus all --name "$LALALAI_CONTAINER_NAME")
  run_command+=(--env LALALAI_LICENSE_KEY="$license_key")
  run_command+=("$LALALAI_IMAGE_NAME")
  add_separator_flags
}

parse_args "$@"
mkdir -p "$out_dir"

docker stop $LALALAI_CONTAINER_NAME &> /dev/null
docker rm $LALALAI_CONTAINER_NAME &> /dev/null

compound_run_command
"${run_command[@]}"