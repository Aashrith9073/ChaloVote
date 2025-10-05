# ChaloVote ✈️

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud)](https://cloud.google.com/)
[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/)

Stop the endless group chat debates! ChaloVote is an AI-powered web application that simplifies group travel planning for friends. It uses a multi-step AI agent to research and suggest personalized travel destinations, complete with real-time data, and a fair voting system to pick the perfect spot for your next adventure.

---

## ✨ Key Features

-   **Multi-Step AI Agent**: A sophisticated agent that brainstorms ideas, conducts research using tools, and synthesizes a final, detailed recommendation.
-   **Real-time Data Enrichment**: The agent uses external tools to fetch:
    -   Driving routes and times via **Google Maps API**.
    -   Estimated fuel costs by getting live **petrol prices via Gemini**.
    -   Budget hotel and flight price estimates.
-   **Ranked-Choice Voting**: Implements a fair instant-runoff voting algorithm to find the destination with the broadest appeal.
-   **Automated Notifications**: Keeps participants in the loop with SMS (Twilio) and Email (SendGrid) notifications.
-   **Embedded Maps**: Displays personalized route maps for each participant directly in the UI.

---

## 🤖 The AI Pipeline

The core of ChaloVote is a multi-step agentic workflow powered by **Google Gemini**.

1.  **Ideation**: Based on the group's aggregated survey preferences (locations, interests, budget), the agent asks Gemini to brainstorm a list of 5 suitable destinations in India.

2.  **Enrichment (Tool Use)**: For each destination idea, the agent acts as a researcher and uses a series of "tools" to gather live data:
    -   It asks Gemini to find **top budget hotels** and their ratings.
    -   It calls the **Google Maps API** to get route distance and duration from each participant's starting location.
    -   It asks Gemini for the **current petrol price** in each participant's city to calculate fuel costs.
    -   It asks Gemini for **estimated flight prices**.

3.  **Synthesis**: The agent bundles all of this research data and presents it to Gemini one last time. It asks the AI to act as a travel expert and write a final, compelling summary, including a total estimated cost and a list of top stays for each destination.

---

## 🛠️ Tech Stack & Packages

-   **Backend**: FastAPI, Python 3.10, Uvicorn
-   **Database**: SQLAlchemy ORM, SQLite (local)
-   **AI**: LiteLLM, Google Gemini (`gemini-2.5-flash`)
-   **External APIs**: Google Maps Platform (Directions, Geocoding, Embed), Twilio, SendGrid, RapidAPI (for flights/hotels)
-   **Frontend**: Jinja2 Templating, HTMX, Tailwind CSS
-   **Key Packages**: `fastapi`, `uvicorn`, `sqlalchemy`, `litellm`, `google-cloud-aiplatform`, `requests`, `pydantic-settings`, `jinja2`
-   **Deployment**: Vercel

---

## 🚀 Getting Started (Local Development)

### Prerequisites

-   Python 3.10 or higher
-   Git
-   Google Cloud SDK installed and authenticated (`gcloud auth application-default login`)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/ChaloVote.git](https://github.com/your-username/ChaloVote.git)
    cd ChaloVote
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment variables:**
    -   Create a file named `.env` in the root of the project.
    -   Copy the contents below and fill in your own secret API keys.

    ***`.env` Template***
    ```ini
    # App Config
    BASE_URL="[http://127.0.0.1:8000](http://127.0.0.1:8000)"

    # Google Cloud & AI
    GEMINI_API_KEY="your-google-ai-studio-key"
    GOOGLE_PROJECT_ID="your-google-cloud-project-id"
    GOOGLE_MAPS_API_KEY="your-google-maps-platform-key"

    # RapidAPI (for flights/hotels)
    RAPIDAPI_KEY="your-rapidapi-key"

    # Notifications
    SENDGRID_API_KEY="SG..."
    SENDER_EMAIL="your-verified-email@example.com"
    TWILIO_ACCOUNT_SID="AC..."
    TWILIO_AUTH_TOKEN="..."
    TWILIO_PHONE_NUMBER="+1..."
    ```

5.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    - The API will be running at `http://127.0.0.1:8000`.
    - Access the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

## ☁️ Deployment on Vercel

This application is ready for deployment on Vercel.
1.  Connect your GitHub repository to Vercel.
2.  In the Vercel project settings, go to **Settings > Environment Variables** and add all the keys from your `.env` file.
3.  **Important**: For a live deployment, you must switch from SQLite to a cloud-hosted PostgreSQL database (like [Neon](https://neon.tech/)) and add its connection string as a `DATABASE_URL` environment variable.