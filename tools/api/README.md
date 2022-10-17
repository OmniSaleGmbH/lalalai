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
                                'acoustic_guitar', 'synthesizer', 'voice']
                            Stem option. Phoenix is currenlty works only with stems: 
                            vocals, drum, bass, voice, electric_guitar, acoustic_guitar. Choose Cassiopeia network for the rest
                      --filter <post-processing filter> \
                            default: 1
                            choices:
                                [0, 1, 2]
                            0: mild, 1: normal, 2: aggressive
                      --splitter <splitter type>
                            default: 'phoenix'
                            choices: 
                                ['phoenix', 'cassiopeia']
                            The type of neural network used to split audio
```
