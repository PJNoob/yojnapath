# Yojna _Path

<div align="center">
    <img src="assets/Yojanaपथ.png" alt="Yojanaपथ" />
</div>

## About

Yojna_Path is a revolutionary telephony-based platform designed to bridge the gap between rural citizens and government schemes. It combines voice, text, and AI-driven support to deliver personalized multilingual assistance in a user-friendly manner. By leveraging advanced LLMs, speech-to-text, and text-to-speech technologies, Yojna_Path ensures inclusivity, accessibility, and ease of use across familiar platforms like WhatsApp and SMS.
## System Architecture
<div align="center">
    <img src="assets/ey_1.drawio (2).png" alt="Yojanaपथ Architecture" />
</div>

## Vision

To create an inclusive, multilingual telephony platform that empowers underserved communities by simplifying access to government schemes. Yojna_Path aims to:

- Provide step-by-step guidance for document preparation and submission.
- Maintain secure document management with GCloud integration.
- Ensure users are informed via WhatsApp or SMS notifications.
- Utilize AI agents to analyze user conversations, recommend relevant schemes, and guide users through the application process.
- Support rural users with local language interaction using AI4Bharat Bhashini APIs for speech recognition and synthesis.

This cost-effective and advanced platform aims to bridge the digital divide and foster equitable access to government resources.

## Executive Summary

### Personalized Multilingual Voice Support on Telephony System

**Holistic Technological Solution:**

- **Document Validation and Assistance:**
  - Guides users to prepare and upload required documents through Google Forms integrated into a WhatsApp interface.
  - Maintains documents securely on Google Sheets with GCloud integration, ensuring privacy.
  - Sends SMS or WhatsApp notifications to keep users informed.

- **Streamlined User Onboarding:**
  - Uses LLM agents to analyze conversations, extract tags, and register users for tailored scheme recommendations.
  - Focuses on eligibility criteria, benefits, and application steps.

- **Accessible and Inclusive Platform:**
  - Combines voice, text, and AI-driven telephony support.
  - Bridges gaps between rural citizens and government schemes via familiar platforms like WhatsApp and SMS.

- **Advanced Multilingual Support:**
  - Enables rural users to interact with voice agents in their local language using speech-to-text and text-to-speech models.
  - Supports dialects using AI4Bharat Bhashini STT and TTS APIs by SarvamAI.

## Getting Started

### Setting Up the Environment

1. **Create a Virtual Environment**  
   Navigate to your project directory and create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Requirements**  
   Install the necessary packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the application, run the following command:

```bash
python3 twilio_service/main.py
```

In another terminal, make your localhost public using `ngrok` with the following command:

```bash
ngrok http 8000
```

### Setting Environment Variables

Export the following environment variables:

- `ELEVENLABS_API_KEY`
- `AGENT_ID`

You can do this in your terminal:

```bash
export ELEVENLABS_API_KEY='your_api_key_here'
export AGENT_ID='your_agent_id_here'
```

### Calling Yojna_Path

Connect the `ngrok` public webhook to a Twilio number via the Twilio Console. Dial the number to connect to the Yojna_Path agent.



### Setting Environment Variables

You need to export the following environment variables:

- `ELEVENLABS_API_KEY`
- `AGENT_ID`

You can do this in your terminal:

```bash
export ELEVENLABS_API_KEY='your_api_key_here'
export AGENT_ID='your_agent_id_here'
```
### Calling Yojna_Path
Connect the ngrock public Webhook to twilio number in twilio console.Then by dialing the number connects to Yojna_Path Agent
