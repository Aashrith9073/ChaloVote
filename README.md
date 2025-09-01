# ChaloVote - AI-Powered Group Travel Planning ✈️

Stop the endless group chat debates! ChaloVote is an open-source web application that simplifies group travel planning. It uses AI to suggest personalized travel destinations based on everyone's preferences and a fair, ranked-choice voting system to pick the perfect spot for your next adventure.

---

## How it Works 🗺️

ChaloVote streamlines the decision-making process into a few simple steps:

1.  **Create a Trip**: The organizer starts by giving the trip a name and adding participants' contact information (email or phone number).
2.  **Collect Preferences**: Each participant receives a unique link to a survey where they can input their travel preferences, such as budget, interests, and dates.
3.  **AI-Powered Recommendations**: ChaloVote aggregates the group's preferences and uses an open-source Large Language Model (via Hugging Face) to generate a personalized list of travel destinations.
4.  **Ranked-Choice Voting**: Everyone receives a link to a voting page where they can rank the AI-generated recommendations in their order of preference.
5.  **Declare a Winner!** 🏆 The app uses an instant-runoff algorithm to tally the votes and determine the winning destination that best satisfies the entire group.

---

## Features ✨

-   **Group Trip Creation & Management**: Easily set up trips and invite friends.
-   **AI-Powered Destination Recommendations**: Get suggestions tailored to your group's collective tastes, powered by modern open-source LLMs.
-   **Personalized Preference Surveys**: Each member's voice is heard through a simple survey.
-   **Fair Decision Making**: A robust **Ranked-Choice Voting System** ensures the final destination is the one with the broadest appeal, not just the one with the most first-place votes.
-   **Automated Notifications**: Participants are kept in the loop with SMS/Email notifications (powered by Twilio & SendGrid).
-   **RESTful API**: A clean, interactive API built with FastAPI.

---

## Tech Stack 🛠️

-   **Backend**: FastAPI, Python 3.10, Uvicorn
-   **Database**: SQLAlchemy ORM, SQLite (for local development)
-   **AI**: LiteLLM (as a gateway to Hugging Face models), Docker
-   **Notifications**: Twilio (for SMS), SendGrid (for Email)
-   **Deployment**: Vercel

---

## Getting Started (Local Development) 🚀

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

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
    -   Copy the contents of `.env.example` (see below) into your new `.env` file.
    -   Fill in your secret keys from services like Hugging Face, Twilio, and SendGrid.

    ***.env.example***
    ```ini
    # Hugging Face API Token for AI Recommendations
    HUGGINGFACE_API_TOKEN="hf_..."

    # SendGrid API Key for Email Notifications
    SENDGRID_API_KEY="SG..."
    SENDER_EMAIL="your-verified-email@example.com"

    # Twilio Credentials for SMS Notifications
    TWILIO_ACCOUNT_SID="AC..."
    TWILIO_AUTH_TOKEN="..."
    TWILIO_PHONE_NUMBER="+1..."
    ```

5.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

6.  **Access the application:**
    -   The API will be running at http://127.0.0.1:8000.
    -   Access the interactive API documentation (powered by Swagger UI) at http://127.0.0.1:8000/docs.