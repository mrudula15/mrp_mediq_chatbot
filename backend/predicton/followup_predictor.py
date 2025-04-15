import joblib
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Define path to model files
models_dir = Path(__file__).resolve().parent / "models"

# ✅ Load the trained model, label encoder, and question map
clf = joblib.load(models_dir / "followup_model.pkl")
label_encoder = joblib.load(models_dir / "label_encoder.pkl")
question_map = joblib.load(models_dir / "question_map.pkl")

# ✅ Load the sentence transformer model (used for encoding the question text)
model = SentenceTransformer('all-MiniLM-L6-v2')


def suggest_followups(current_question_text, top_k=3):
    """
    Given the current question (natural language), suggest top-k follow-up questions
    based on a trained classification model.

    Parameters:
        current_question_text (str): The question asked by the user
        top_k (int): Number of follow-up suggestions to return

    Returns:
        List[str]: Top-k recommended follow-up questions
    """

    # 🔢 Encode current question into vector
    vector = model.encode([current_question_text])

    # 📊 Predict probabilities for each label (question ID)
    probs = clf.predict_proba(vector)[0]

    # 🏅 Get indices of top-k predicted question IDs
    top_indices = probs.argsort()[-top_k:][::-1]
    next_q_ids = label_encoder.inverse_transform(top_indices)

    # 🧠 Map question IDs back to full questions
    return [question_map[qid] for qid in next_q_ids]
