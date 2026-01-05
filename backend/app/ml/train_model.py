import pandas as pd
import numpy as np
import xgboost as xgb
import joblib

def generate_strict_btech_data(n_samples=10000):
    """
    Generates data that follows Strict JNTU/College Rules.
    No more random guessing.
    """
    np.random.seed(42)
    data = []

    for _ in range(n_samples):
        # --- INPUTS ---
        overall_attendance = np.random.uniform(60.0, 99.0) # Float for precision
        
        # 0=Elective (English/Library), 1=Core (DSA/OS/AIML)
        is_core_subject = np.random.choice([0, 1], p=[0.3, 0.7])
        
        days_to_exam = np.random.randint(0, 40) # 0 means exam is today/tomorrow
        
        # 0=Start, 1=Mid, 2=End
        semester_phase = np.random.choice([0, 1, 2])
        
        # --- STRICT LOGIC RULES (The "Teacher" Brain) ---
        safe_to_bunk = 0 # Default NO

        # RULE 1: The "Detention" Line
        if overall_attendance < 75.0:
            safe_to_bunk = 0 # Danger Zone! Never bunk.
        
        # RULE 2: The "Exam Panic"
        elif days_to_exam <= 2:
            safe_to_bunk = 0 # Exam is near! Study!
            
        # RULE 3: The "Safe Zone" (75% - 85%)
        elif 75.0 <= overall_attendance < 85.0:
            if is_core_subject == 1:
                safe_to_bunk = 0 # Don't miss core subjects in this range
            else:
                safe_to_bunk = 1 # English? Okay to skip.

        # RULE 4: The "Luxury Zone" (85%+)
        else: # > 85%
            if days_to_exam < 5 and is_core_subject == 1:
                 safe_to_bunk = 0 # Keep attendance high for exams
            else:
                 safe_to_bunk = 1 # You are the king. Sleep at home.

        data.append([
            overall_attendance, is_core_subject, days_to_exam, semester_phase, safe_to_bunk
        ])

    columns = ['overall_attendance', 'is_core_subject', 'days_to_exam', 'semester_phase', 'target']
    return pd.DataFrame(data, columns=columns)

def train_and_save():
    print("🧠 Training Strict B.Tech Model...")
    df = generate_strict_btech_data()
    
    X = df.drop('target', axis=1)
    y = df['target']
    
    # We use a deeper tree (max_depth=6) to capture these strict IF-ELSE rules
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6, 
        learning_rate=0.1,
        use_label_encoder=False, 
        eval_metric='logloss'
    )
    model.fit(X, y)
    
    save_path = "app/ml/model_pipeline.pkl"
    joblib.dump(model, save_path)
    print(f"✅ Model saved to {save_path}")
    print("   -> Logic: <75% = DETENTION RISK detected.")

if __name__ == "__main__":
    train_and_save()