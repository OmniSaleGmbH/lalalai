# LALAL.AI API Examples

This directory contains examples of interacting with the LALAL.AI API as described in [https://www.lalal.ai/api/help/](https://www.lalal.ai/api/help/)

## Scripts

- `lalalai_splitter.py` - Audio source separation using various stems and neural networks
- `lalalai_voice_converter.py` - Voice conversion using different voice packs

## lalalai_splitter.py Usage

```bash
% python3 lalalai_splitter.py --license <user license> \
                             --input <input directory or file> \
                             [--output <output directory>] \
                             [--stem <stem option>] \
                             [--filter <post-processing filter>] \
                             [--splitter <splitter type>] \
                             [--enhanced-processing <true/false>] \
                             [--noise-cancelling <level>]

Parameters:
    --license              User license key (required)
    --input                Input directory or file (required)
    --output               Output directory (default: current script directory)
    --stem                 Stem to extract (default: "vocals")
                          choices: vocals, drum, bass, piano, electric_guitar, 
                                  acoustic_guitar, synthesizer, voice, strings, wind
                          Note: Different neural networks support different sets of stems
    --filter               Post-processing filter intensity (default: 1)
                          choices: 0 (mild), 1 (normal), 2 (aggressive)
    --splitter             Neural network type (default: auto - selects most effective for stem)
                          choices: phoenix, orion, perseus
                          Auto selection priority: Perseus > Orion > Phoenix
                          - Perseus: vocals, voice, drum, piano, bass, electric_guitar, acoustic_guitar
                          - Orion: vocals, voice, drum, piano, bass, electric_guitar, acoustic_guitar  
                          - Phoenix: vocals, voice, drum, piano, bass, electric_guitar, acoustic_guitar, synthesizer, strings, wind
    --enhanced-processing  Enable enhanced processing (default: false)
                          Available for all stems except "voice"
    --noise-cancelling     Noise cancelling level for "voice" stem only (default: 1)
                          choices: 0 (mild), 1 (normal), 2 (aggressive)
```

## lalalai_voice_converter.py Usage

```bash
% python3 lalalai_voice_converter.py --license <user license> \
                                   [--input <input directory or file>] \
                                   [--uploaded_file_id <file id>] \
                                   [--output <output directory>] \
                                   [--voice_pack_id <voice pack id>] \
                                   [--accent_enhance <true/false>] \
                                   [--pitch_shifting <true/false>] \
                                   [--dereverb_enabled <true/false>]

Parameters:
    --license              User license key (required)
    --input                Input directory or file (optional if using --uploaded_file_id)
    --uploaded_file_id     Previously uploaded file ID (optional)
    --output               Output directory (default: current script directory)
    --voice_pack_id        Voice pack ID (default: "ALEX_KAYE")
                          Available voice packs: https://www.lalal.ai/api/voice_packs/list/
    --accent_enhance       Accent processing (default: true)
                          true: Match target voice accent
                          false: Keep original accent
    --pitch_shifting       Tonality/pitch processing (default: true)
                          true: Match target voice tonality
                          false: Keep original tone
    --dereverb_enabled     Echo/reverb processing (default: false)
                          true: Remove echo/reverb from audio
                          false: Restore original echo/reverb
```
