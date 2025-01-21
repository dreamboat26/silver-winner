# Presenter 🎦

### Introducing **Presenter**: A Multi-Agent AI Tool that can:

- [x] **Create beautiful presentations** for any given topic 🔥
- [x] **Render intuitive & visually appealing diagrams** 🖼️ for slides when needed (using Mermaid)
- [x] **Write scripts** for every slide 📜
- [x] **Render & View interactive presentations in HTML** 💻 (using markdown-slides & reveal.js)
- [x] **Intuitive speaker view with scripts** (reveal.js)
- [x] **Export presentations to PDF** 🖨️ (using DeckTape)
- [x] **Generate audio narrations** from scripts 🎙️ (using ElevenLabs)
- [x] **Render full video presentations** 🎥 with all the slides and voiceover (using FFmpeg)

## Video Demo with overview of the multi-agent setup

[![Presenter](https://img.youtube.com/vi/q8PAD9IS3Ig/maxresdefault.jpg)](https://www.youtube.com/watch?v=q8PAD9IS3Ig)

## Tools Used

- [LlamaIndex](https://www.llamaindex.ai/) Workflows to orchestrate the entire multi-agent setup
- [markdown-slides](https://github.com/dadoomer/markdown-slides) and reveal.js for rendering & viewing the presentation
- [Mermaid](https://github.com/mermaid-js/mermaid) to render the diagrams
- [DeckTape](https://github.com/astefanutti/decktape) to export the presentation to PDF
- [ElevenLabs](https://elevenlabs.io/) API to create audio narration for the slides
- [FFmpeg](https://www.ffmpeg.org/) to render the full presentation with voiceover

## How to use

- First install the necessary tools

```bash
python -m pip install git+https://gitlab.com/da_doomer/markdown-slides.git
npm install -g @mermaid-js/mermaid-cli
npm install -g decktape
npm install -g puppeteer
puppeteer browsers install chrome
```

- Install FFmpeg for your operating system from [here](https://www.ffmpeg.org/download.html)

- Clone the repo

```bash
git clone https://github.com/rsrohan99/presenter.git
cd presenter
```

- Install dependencies

```bash
pip install -r requirements.txt
```

- Create `.env` file and add `OPENAI_API_KEY` and `ELEVENLABS_API_KEY`

```bash
cp .env.example .env
```

- Run the workflow with the topic to create the presentation on

```bash
python run.py "observer design pattern"
```

- Add `--export-video` argument to generate a full video of the presentation with voiceover.

```bash
python run.py "observer design pattern" --export-video
```

- After running the workflow, it'll put all the files (slides, video, pdf etc.) inside the `presentations` folder
- There be a folder for each presentation generated
- The interactive HTML for the presentation will be at `presentations/<presentation_folder>/output/index.html`
- The extracted PDF of the presentation will be at `presentations/<presentation_folder>/presentation.pdf`
- The rendered video with voiceover of the presentation will be at `presentations/<presentation_folder>/presentation.mp4`
