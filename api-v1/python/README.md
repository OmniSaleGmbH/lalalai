# LALAL.AI API v1 - Python Examples

This directory contains Python examples for interacting with the LALAL.AI API v1 as described in [https://www.lalal.ai/api/v1/docs/](https://www.lalal.ai/api/v1/docs/)

## Requirements

```bash
pip install requests
```

## Scripts

- `lalalai_splitter.py` - Audio source separation using various stems (voice, vocals, music, and instruments)
- `lalalai_voice_converter.py` - Voice conversion using different voice packs
- `lalalai_demuser.py` - Remove background music from voice recordings

## lalalai_splitter.py Usage

```bash
python3 lalalai_splitter.py --license <user license> \
                            --input <input directory or file> \
                            [--output <output directory>] \
                            [--stem <stem option>] \
                            [--noise-cancelling <level>] \
                            [--dereverb-enabled <true/false>] \
                            [--extraction-level <level>] \
                            [--multivocal <option>] \
                            [--splitter <model>] \
                            [--delete <true/false>]

Parameters:
    --license              User license key (required)
    --input                Input directory or file (required)
    --output               Output directory (default: current script directory)
    --stem                 Stem to extract (default: "vocals")
                          choices: voice, music, vocals, drum, bass, piano, 
                                  electric_guitar, acoustic_guitar, synthesizer, 
                                  strings, wind
                          Note: 
                          - "voice" uses /split/voice_clean/ endpoint (for voice cleaning)
                          - "music" uses /split/demuser/ endpoint (removes music from voice)
                          - All others use /split/stem_separator/ endpoint
    --noise-cancelling     Noise cancelling level for "voice" stem only (default: 1)
                          choices: 0 (mild), 1 (normal), 2 (aggressive)
    --dereverb-enabled     Remove echo/reverb from audio (default: false)
                          choices: true, false
    --extraction-level     Extraction quality for stem_separator stems (default: deep_extraction)
                          choices: deep_extraction (more details, may bleed), 
                                  clear_cut (cleaner, less detail)
    --multivocal           For "vocals" stem only - separate lead and backing vocals
                          choices: lead_back (splits into lead and backing)
    --splitter             Splitter model to use (default: auto-select latest)
                          choices: orion, perseus, phoenix, andromeda
    --delete               Delete files from LALAL.AI storage after download (default: false)
                          choices: true, false
```

**API Endpoints Used:**
- `/api/v1/split/voice_clean/` - For "voice" stem (voice cleaning with noise cancellation)
- `/api/v1/split/demuser/` - For "music" stem (background music removal)
- `/api/v1/split/stem_separator/` - For all instrumental stems (vocals, drum, bass, piano, guitars, etc.)

## lalalai_voice_converter.py Usage

```bash
python3 lalalai_voice_converter.py --license <user license> \
                                   [--input <input directory or file>] \
                                   [--uploaded_file_id <file id>] \
                                   [--output <output directory>] \
                                   [--voice_pack_id <voice pack id>] \
                                   [--accent <0.0-1.0>] \
                                   [--tonality-reference <source_file/voice_pack>] \
                                   [--dereverb-enabled <true/false>] \
                                   [--splitter <model>] \
                                   [--delete <true/false>] \
                                   [--list]

Parameters:
    --license              User license key (required)
    --input                Input directory or file (optional if using --uploaded_file_id)
    --uploaded_file_id     Previously uploaded file source_id (optional, but required if skips upload)
    --output               Output directory (default: current script directory)
    --voice_pack_id        Voice pack ID (default: "ALEX_KAYE")
                          Use --list to see available voice packs
    --accent               Accent processing strength (default: 1.0)
                          Range: 0.0-1.0
                          0.0 = keep original accent
                          1.0 = match target voice accent
    --tonality-reference   Tonality/pitch processing (default: source_file)
                          source_file: Keep original pitch
                          voice_pack: Match target voice pitch
    --dereverb-enabled     Echo/reverb removal (default: false)
                          true: Remove echo/reverb from audio
                          false: Keep original reverb
    --splitter             Splitter model to use (default: auto-select latest)
                          choices: orion, perseus, phoenix, andromeda
    --delete               Delete files from LALAL.AI storage after download (default: false)
                          choices: true, false
    --list                 List available voice packs and exit
```

**API Endpoints Used:**
- `/api/v1/upload/` - Upload audio file (returns source_id)
- `/api/v1/change_voice/` - Start voice conversion task
- `/api/v1/check/` - Check task status and get results
- `/api/v1/voice_packs/list/` - Get available voice packs

## lalalai_demuser.py Usage

```bash
python3 lalalai_demuser.py --license <user license> \
                           --input <input directory or file> \
                           [--output <output directory>] \
                           [--dereverb-enabled <true/false>] \
                           [--delete <true/false>]

Parameters:
    --license              User license key (required)
    --input                Input directory or file (required)
    --output               Output directory (default: current script directory)
    --dereverb-enabled     Remove echo/reverb from audio (default: false)
                          choices: true, false
    --delete               Delete files from LALAL.AI storage after download (default: false)
                          choices: true, false
```

**API Endpoints Used:**
- `/api/v1/upload/` - Upload audio file
- `/api/v1/split/demuser/` - Remove background music from voice (extracts "music" stem)
- `/api/v1/check/` - Check task status
- `/api/v1/delete/` - Clean up files from LALAL.AI storage

## API v1 Workflow

All scripts follow this pattern:

1. **Upload** - Upload file via `/api/v1/upload/` endpoint (returns `source_id`)
2. **Process** - Start processing task (split or voice conversion) using the `source_id`
3. **Check** - Poll `/api/v1/check/` endpoint until task completes
4. **Download** - Download result files from provided URLs
5. **Delete** (optional) - Clean up files from LALAL.AI storage

## Notes

- All endpoints use `X-License-Key` header for authentication
- Processing is asynchronous - use `/api/v1/check/` to poll for completion
- Results include direct download URLs for output tracks
