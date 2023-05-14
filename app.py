from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from datetime import datetime
import pickle
import pandas as pd
import psycopg2.pool

DATABASE_HOST = "arjuna.db.elephantsql.com"
DATABASE_NAME = "yqfvqfie"
DATABASE_USER = "yqfvqfie"
DATABASE_PASSWORD = "FOPYHfFC3pRVH7gWg4sC1eCX7Xgnp-lq"

conn = psycopg2.connect(
    host=DATABASE_HOST,
    dbname=DATABASE_NAME,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD
)

app = Flask(__name__)
CORS(app, origins=['http:localhost:3000'])

model = pickle.load(open('model.pkl', 'rb'))

@app.route('/api/predict', methods=["POST"])
@cross_origin()
def predict():
    try:
        user_input = request.json

        date_str = user_input["date"]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        with conn.cursor() as cur:
            cur.execute("""
                SELECT stops, minutes
                FROM durations
                WHERE source LIKE %s AND destination LIKE %s
                LIMIT 1
            """, ('%' + user_input["source"] + '%', '%' + user_input["destination"] + '%'))
            result = cur.fetchone()

        if result is None:
            final_response = { "status": 400, "message": "No data found for the given source and destination." }
            return jsonify(final_response)

        stops, minutes = result

        formatted_user_input = {
            "Airline": user_input["airline"],
            "Source": user_input["source"],
            "Destination": user_input["destination"],
            "Total_Stops": stops,
            "Date": date_obj.day,
            "Month": date_obj.month,
            "Year": date_obj.year,
            "Duration_minutes": minutes
        }

        dataFrames = pd.DataFrame(data=formatted_user_input, index=[0])

        predictions = model.predict(dataFrames)

        with conn.cursor() as cur:
            cur.execute("INSERT INTO graph_data (price, created_at, updated_at) VALUES (%s, NOW(), NOW())", (predictions[0],))
            conn.commit()

        response = {
            "status": 200,
            "predicted_price_in_dollar": predictions[0],
            "predicted_price_in_ngultrum": predictions[0] * 82
        }

        final_response = {**response, **formatted_user_input}
    except ValueError as e:
        final_response = { "status": 400, "message": str(e) }

    return jsonify(final_response)


@app.route('/api/v1/predictions')
@cross_origin()
def predictions():
    cur = conn.cursor()
    cur.execute("""
        SELECT DATE_TRUNC('month', created_at) AS month,
               AVG(price) AS avg_price
        FROM graph_data
        GROUP BY month
        ORDER BY month ASC;
    """)

    results = cur.fetchall()
    cur.close()

    avg_prices = []
    for result in results:
        avg_prices.append({
            "month": result[0].strftime("%b"),
            "price": float(result[1])
        })

    return jsonify(avg_prices)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')