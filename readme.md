# [LALAL.AI](https://www.lalal.ai/)

Extract vocal, accompaniment and various instruments from any audio and video
High-quality stem splitting based on the world's #1 AI-powered technology.

## API

### API V1 (Recommended)
A stable, convenient API with a richer feature set, an OpenAPI specification, and a Swagger-like tool for browsing and trying endpoints.

**Python Examples:**
* [Python tools and scripts](api-v1/python/)

**Documentation:**
* [Human-readable docs](https://www.lalal.ai/api/v1/docs/)
* [OpenAPI Specification](https://www.lalal.ai/api/v1/openapi.json)

### API V0 (Deprecated)
**Code Examples:**
* Legacy API examples and documentation available in [api-v0(deprecated)](api-v0(deprecated)/).

**Documentation:**
* [Human-readable docs](https://www.lalal.ai/api/help/)

## About
We are a team of specialists in the fields of artificial intelligence, machine learning, mathematical optimization, and digital signal processing. **Our goal is to make working with audio and video easier** for musicians, sound producers, music engineers, video bloggers, streamers, transcribers, translators, journalists, and many other professionals and creatives.

In 2020, we developed a unique neural network called **Rocknet** using 20TB of training data to extract instrumentals and voice tracks from songs. In 2021, we created Cassiopeia, a next-generation solution superior to Rocknet that allowed improved splitting results with significantly fewer audio artifacts.

Starting as a 2-stem splitter, LALAL.AI has grown significantly during 2021. In addition to **vocal and instrumental**, the service was enhanced with the capability to extract musical instruments – **drums, bass, acoustic guitar, electric guitar, piano, and synthesizer**. As a result of this upgrade, LALAL.AI became the [world's first 8-stem splitter](https://www.lalal.ai/blog/lalal-ai-adds-the-8th-stem-for-separation-synthesizer/). In the same year, we also presented [business solutions](https://www.lalal.ai/business-solutions/), enabling owners of sites, services and applications to integrate our stem-splitting technology into their environments via API.

Only available in English prior to 2021, LALAL.AI was translated into 7 other languages – Chinese, French, German, Italian, Japanese, Korean, and Spanish. Furthermore, we added new payment methods to make LALAL.AI easier to acquire and more accessible to people worldwide.

In 2022, we created and released [Phoenix](https://www.lalal.ai/blog/phoenix-neural-network-vocal-separation/), a state-of-the-art audio source separation technology. In terms of stem-splitting accuracy, it surpassed not only our previous neural networks but also all other solutions on the market.

Although Phoenix exclusively handled vocal/instrumental isolation at first, its powerful technology allowed us to continually introduce new stems on a regular basis. Throughout the year we trained Phoenix to extract all musical instruments that Cassiopeia supported.

We also added two brand new stems, wind and string instruments, which no other service offered. With that update, LALAL.AI broke the record again and became the [world's first 10-stem splitter](https://www.lalal.ai/blog/wind-string-instruments/).

LALAL.AI's innovative technologies are used not only for stem splitting. In July of 2022, we introduced [Voice Cleaner](https://www.lalal.ai/blog/voice-cleaner/), a noise cancellation solution that removes background music, mic rumble, vocal plosives, and many other types of extraneous noises from video and audio recordings.

At the end of 2022, we created a [desktop version of LALAL.AI](https://www.lalal.ai/blog/lalalai-desktop-app/). The application enabled users to split audio and videos into stems in one convenient place on their Windows, macOS and Linux computers.

In 2023, we developed mobile applications for iOS and Android, making LALAL.AI and all its features readily available on the go. We also trained and released Orion, our fourth-generation neural network that takes a unique approach to audio separation. The network not only extracts stems from the mix but also enhances them in the process, eliminating errors and audible imperfections for the best possible quality results.

In 2024, LALAL.AI continued the trajectory of innovation with several significant updates. We introduced Enhanced Processing and Noise Canceling Level features in March, allowing users greater control over audio separation for vocals and instruments while providing customizable noise reduction options. In April, we launched the Voice Changer, enabling users to transform songs and vocal recordings with various artist and character voice clones. August brought the introduction of the Echo & Reverb Remover, a tool designed to enhance audio clarity by effectively removing unwanted echoes and reverberations from recordings.

By September 2024, we released the highly anticipated Lead & Back Vocal Splitter, simplifying lead and backing vocal isolation. The launch of the Perseus neural network shortly thereafter marked a significant leap in vocal extraction technology. Utilizing advanced transformer models similar to those behind OpenAI's ChatGPT, Perseus offers unprecedented clarity in vocal isolation while minimizing artifacts. Throughout 2024, Perseus was updated to support not only vocal and instrumental isolation but also the extraction of drums and bass.

LALAL.AI remains dedicated to pushing the boundaries of AI-powered audio processing while continuously improving our products. We work hard to create fresh, high-quality solutions, and we always have a lot of ideas and developments in store. Keep your eyes peeled for new possibilities and improvements!

## Core Technology

**Neural Networks:**
- **Andromeda** (2025): Latest neural network for stem separation, raising the bar worldwide and setting new quality benchmarks
- **Perseus** (2024): Advanced transformer-based technology for vocal and instrumental extraction with enhanced processing modes
- **Orion** (2023): Takes a unique approach to audio separation, using an enhanced stem-splitting technique
- **Phoenix** (2022): State-of-the-art audio source separation technology
- **Cassiopeia** (2021): Next-generation solution with reduced audio artifacts
- **Rocknet** (2020): Initial neural network trained on 20TB of data

**Services:**
- Stem Splitter: Up to 10-stem separation including vocals, instrumentals, drums, bass, guitars, piano, synthesizer, wind, and string instruments
- Voice Cloner: Create custom voice clones with API support
- Voice Changer: Accent and tonality control with echo estimation and intelligent routing
- Lead & Back Vocal Splitter: Separate lead and backing vocals
- Echo & Reverb Remover: Remove echo and reverberation from audio
- Voice Cleaner: Remove background noise and unwanted sounds

## Legal Entity
OmniSale GmbH
Rigistrasse 3, 6300, Zug, Switzerland.

**Forks and third party tools** (using deprecated API, not updated for a long time and missing new splitters):
* GUI frontend for Python script. Currently for Mac only https://github.com/lehenbauer/unmixer (by @lehenbauer)
