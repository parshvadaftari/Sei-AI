# SeiAI Voicebot Project

## Overview

This project is designed to create a voicebot that leverages various technologies to provide assistance with Wise financial transactions and payments. The voicebot integrates with LiveKit for real-time communication, Deepgram for speech-to-text, OpenAI for language models, and Cartesia for text-to-speech. The system also includes scripts to crawl the data from websites and store the same into ChromaDB, manage inbound SIP trunks, dispatch rules, and handle FAQs using vector embeddings.

### Sample Video
<video width="640" height="360" controls>
  <source src="https://github.com/parshvadaftari/Sei-AI/raw/main/assets/sample_video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## Setup

### Prerequisites

- Python 3.9+
- LiveKit account
- Deepgram account
- OpenAI account
- Cartesia account
- Twilio account (for SIP trunks)

### Installation

1. Clone the repository and move to the folder:
   ```sh
   cd SeiAI
   ```

2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - Create a `.env` file in the project root.
   - Copy the contents of `.env.example` into `.env`.
   - Fill in the required environment variables with your account details.
   - Ensure that the `.env` file contains the following variables:
        - `LIVEKIT_URL`
        - `LIVEKIT_API_KEY`
        - `LIVEKIT_API_SECRET`
        - `DEEPGRAM_API_KEY`
        - `OPENAI_API_KEY`
        - `CARTESIA_API_KEY`

### Running the Voicebot

1. **Create the inbound SIP trunk**:
- Create an inbound SIP trunk using Livekit's API in order to handle the incoming calls.
   ```sh
   python inbound_trunk.py
   ```
- Alternatively, you can use Livekit's CLI to make the inbound SIP trunk.
- Make sure to configure the `inbound_trunk.json` file with the correct details.
   ```sh
   lk sip in create inbound_trunk.json
   ```

2. **Set up the dispatch rule**:
- Create a dispatch rule using Livekit's API in order to route the incoming calls to the voicebot.
   ```sh
   python dispatch_rule.py
   ```
- Alternatively, you can use Livekit's CLI to make the dispatch rule.
- Make sure to configure the `dispatch_rule.json` file with the correct details.
    ```sh
    lk sip dispatch create dispatch_rule.json
    ```

3. **Store FAQ data**:
- `store_data.py` script is used to crawl the data from the website links and then store that crawled data in the database.
- Make sure to recheck the links in the file before running it.
   ```sh
   python store_data.py
   ```
   - As we are using Craw4AI to crawl the data from websites, it will throw an dependency error.
   - Make sure to downgrade the `psutill` package to version 5.9.3 and the `protobuf` package to version 5.29.3. After you run the `store_data.py` script. 
4. **Start the voicebot**:
- Run the `sei_simple_voicebot.py` script to start the voicebot.
    ```sh
    python sei_simple_voicebot.py dev
    ```

### JSON Configuration Files

- `inbound_trunk.json`: Configure the inbound SIP trunk details.
- `dispatch_rule.json`: Configure the dispatch rule for routing calls.