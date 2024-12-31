from flask_cors import CORS
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import schedule
import time
from threading import Thread
import pymysql
import os

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'trainings'
}

def load_data_from_db():
    """MySQL'den verileri yükler ve bir DataFrame döndürür."""
    try:
        conn = pymysql.connect(**db_config)
        query = "SELECT * FROM courses"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except pymysql.Error as e:
        print(f"Veritabanı hatası: {e}")
        return pd.DataFrame()

def update_model():
    df = load_data_from_db()  
    if not df.empty:
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform(df['keywords'])

        with open('model.pkl', 'wb') as f:
            pickle.dump((vectorizer, X, df), f)
        print("Model güncellendi.")
    else:
        print("Model güncellemesi için yeterli veri yok.")

def load_model():
    if not os.path.exists('model.pkl'):
        raise FileNotFoundError("Model dosyası bulunamadı.")

    with open('model.pkl', 'rb') as f:
        vectorizer, X, df = pickle.load(f)
    return vectorizer, X, df

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    keyword = data.get('keyword', '').lower().strip()

    try:
        vectorizer, X, df = load_model()
    except Exception as e:
        return jsonify({"message": f"Model yüklenirken hata oluştu: {str(e)}"})

    query_vector = vectorizer.transform([keyword])
    similarities = cosine_similarity(query_vector, X).flatten()

    if similarities.max() == 0:
        return jsonify({"message": "Uygun eğitim bulunamadı."})

    top_indices = similarities.argsort()[-5:][::-1]
    matched_courses = df.iloc[top_indices]

    if matched_courses.empty:
        return jsonify({"message": "Uygun eğitim bulunamadı."})

    return jsonify({
        "response": "Anahtar kelimenizle en yakın eğitimler:",
        "courses": matched_courses.to_dict(orient='records')
    })

def daily_update():
    update_model()
    print("Veriler günlük olarak güncellendi.")

schedule.every().day.at("00:00").do(daily_update)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    app.run(debug=True, use_reloader=False)
