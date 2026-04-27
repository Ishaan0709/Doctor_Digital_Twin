# CardioTwin AI

CardioTwin AI scales the reasoning of elite cardiologists using a digital twin of Dr. Vimlesh Pandey.

## Stack
Python, Streamlit, FastAPI, OpenAI, Pandas, NumPy, FAISS, NetworkX, Plotly, python-dotenv

## Install
pip install -r requirements.txt

## Setup env
1. Copy `.env.example` to `.env`
2. Add `OPENAI_API_KEY`

## Run backend
uvicorn backend.app:app --reload

## Run frontend
streamlit run frontend/streamlit_app.py

## Pages
1. Home / Landing
2. Patient Intake
3. Generic GPT Consultation
4. Dr. Vimlesh Pandey AI Twin
5. Historical Case Intelligence
6. Graph Intelligence
7. Comparison Insights
8. Why This Recommendation
9. Admin / Dataset

## Note
This is clinical decision support. It does not replace licensed medical care.
