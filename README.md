# ChaloVote ✈️

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![HTMX](https://img.shields.io/badge/HTMX-1.9.10-blueviolet?style=for-the-badge&logo=htmx)](https://htmx.org/)
[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/)

Stop the endless group chat debates! ChaloVote is an AI-powered web application that simplifies group travel planning. It uses AI to suggest personalized travel destinations based on everyone's preferences and a fair, ranked-choice voting system to pick the perfect spot for your next adventure.

---

## 🚀 Live Demo 
https://chalo-vote.vercel.app/

---

## ✨ Features

-   **AI-Powered Recommendations**: Leverages powerful LLMs (via Cohere) to generate travel suggestions tailored to the group's collective interests and budget.
-   **Ranked-Choice Voting**: Implements a fair instant-runoff voting algorithm to find the destination with the broadest appeal.
-   **Dynamic UI**: A modern, responsive interface built with HTMX and Tailwind CSS that provides a smooth user experience without full page reloads.
-   **Personalized Surveys**: Gathers individual preferences from each participant through a unique survey link.
-   **Automated Notifications**: Keeps participants in the loop with SMS (Twilio) and Email (SendGrid) notifications.
-   **Trip Dashboards**: A central status page for each trip to track survey submissions, view AI recommendations, and monitor voting progress.
-   **FastAPI**: A clean, interactive, and fully documented API built with FastAPI.

---

## 🗺️ How It Works

ChaloVote streamlines the decision-making process into a few simple steps:

1.  **Create a Trip**: The organizer starts a new trip, gives it a name, and adds participants' contact info (email or phone).
2.  **Collect Preferences**: Each participant receives a unique link to a survey to input their travel preferences.
3.  **Generate Recommendations**: On the trip dashboard, the organizer triggers the AI, which aggregates the group's survey data and generates a personalized list of destinations.
4.  **Vote on Options**: The dashboard updates to show the recommendations and unique voting links. Each participant ranks the options in order of preference.
5.  **Declare a Winner!**: Once everyone has voted, a button appears to tally the votes and reveal the winning destination.

---

## 🛠️ Tech Stack

-   **Backend**: FastAPI, Python 3.10, Uvicorn
-   **Database**: SQLAlchemy ORM, SQLite (for local development)
-   **Frontend**: Jinja2 Templating, HTMX, Tailwind CSS
-   **AI Gateway**: LiteLLM
-   **AI Provider**: Cohere
-   **Notifications**: Twilio (SMS), SendGrid (Email)
-   **Deployment**: Vercel
-   **Containerization**: Docker

---

## 🚀 Getting Started (Local Development)

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python 3.10 or higher
-   Git

### Installation

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
    -   Copy the contents below into your new `.env` file.
    -   Fill in your secret keys from the required services.

    ***`.env` Template***
    ```ini
    # The base URL of your running application
    BASE_URL="[http://127.0.0.1:8000](http://127.0.0.1:8000)"

    # Cohere API Key for AI Recommendations
    COHERE_API_KEY="Your-Cohere-Api-Key"

    # SendGrid API Key for Email Notifications
    SENDGRID_API_KEY="SG..."
    SENDER_EMAIL="your-verified-email@example.com"

    # Twilio Credentials for SMS Notifications
    TWILIO_ACCOUNT_SID="AC..."
    TWILIO_AUTH_TOKEN="..."
    TWILIO_PHONE_NUMBER="+1..."

    # Google Project ID (if using Vertex AI)
    GOOGLE_PROJECT_ID=""
    ```

5.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

6.  **Access the application:**
    -   The website will be running at `http://127.0.0.1:8000`.
    -   Access the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

## ☁️ Deployment

This application is configured for easy deployment on **Vercel**.

1.  Push your code to a GitHub repository.
2.  Import the repository on Vercel.
3.  In the Vercel project settings, go to **Settings > Environment Variables** and add all the keys from your `.env` file.

---

## 🛣️ Future Roadmap

-   **Real-time Agent**: Implement the agent service to fetch live flight and hotel pricing.
-   **Comprehensive Test Suite**: Build out a full suite of integration and unit tests using `pytest`.