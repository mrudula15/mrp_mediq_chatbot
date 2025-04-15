import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

# Your predefined Q1–Q23 question mapping
question_map = {
    "Q1": "What are the demographic proportions (race and gender) of patients visiting the hospital?",
    "Q2": "What are the top 5 busiest hospital locations?",
    "Q3": "How does the average age of a patient visiting the hospital vary according to their race?",
    "Q4": "How does the average age of a patient visiting the hospital vary according to their gender?",
    "Q5": "How do the average healthcare expenses and coverage of patients belonging to different races compare with their average incomes?",
    "Q6": "Show me the list of counties recorded with more obese cases.",
    "Q7": "Show me the list of counties with more patients suffering from stress.",
    "Q8": "Show me the list of counties recorded with more cases of sepsis.",
    "Q9": "List the top 10 locations of patients diagnosed with chronic conditions. (use condition_duration_days)",
    "Q10": "Give me the list of patient encounter types and their respective percentages.",
    "Q11": "Which zip codes have the highest emergency visit rates?",
    "Q12": "What is the average duration for each encounter class?",
    "Q13": "Which providers have the longest average encounter durations?",
    "Q14": "Which department has the longest average encounter duration?",
    "Q15": "What is the average encounter duration and out-of-pocket cost for private, government, and uninsured patients?",
    "Q16": "What is the average out-of-pocket cost and insurance coverage ratio across different age groups?",
    "Q17": "Which encounter classes brought in higher average claim profit margins?",
    "Q18": "Which regions are bringing the higher claim profit margins?",
    "Q19": "Which regions are bringing the lower claim profit margins?",
    "Q20": "What is the average cost coverage ratio for each insurer, grouped by private and government ownership?",
    "Q21": "Which regions have the highest number of uninsured patients based on payer data?",
    "Q22": "Which departments have the highest average claim profit margin?",
    "Q23": "Which departments see the most uninsured patients?"
}

print("✅ Loaded keys from question_map:", list(question_map.keys())[:5])

# Load training transitions
df = pd.read_csv('training_data.csv')

print("✅ Unique values in training CSV:", df['current_question'].unique())

model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode questions to embeddings
valid_questions = []
for q in df['current_question']:
    key = q.strip()
    if key in question_map:
        valid_questions.append(question_map[key])
    else:
        print(f"❌ Not found in question_map: {key}")

X = model.encode(valid_questions)
y = df['next_question']

# Encode labels (Q1 → 0, Q2 → 1, ...)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train logistic regression
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

# Make sure directory exists
os.makedirs("models", exist_ok=True)

# Save files
joblib.dump(clf, "models/followup_model.pkl")
joblib.dump(label_encoder, "models/label_encoder.pkl")
joblib.dump(question_map, "models/question_map.pkl")
print("✅ Model trained and saved.")
