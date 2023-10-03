# lalalai_splitter.py

lalalai_splitter.py is an example of interacting with the LALAL.AI API as described in [https://www.lalal.ai/api/help/](https://www.lalal.ai/api/help/)

## Usage

```bash
% python3 lalalai_splitter.py --input <input directory or a file> \
                      --license <user license> \
                      --output <output directory> \
                      --stem <stem option> \
                            default: 'vocals'
                            choices: 
                                ['vocals', 'drum', 'bass',
                                 'piano', 'electric_guitar', 
                                'acoustic_guitar', 'synthesizer', 'voice',
                                'strings', 'wind']
                            Stem selection option.
                            Note: the stems "vocal" and "voice" support the fourth generation of
                            the neural network named "Orion" (see also the --splitter option)
                      --filter <post-processing filter> \
                            default: 1
                            choices:
                                [0, 1, 2]
                            0: mild, 1: normal, 2: aggressive
                      --splitter <splitter type>
                            default: 'phoenix'
                            choices: 
                                ['phoenix', 'orion']
                            Neural network selection option. Currently, the "Orion" neural
                            network only supports the stems "vocal" and "voice".
```
