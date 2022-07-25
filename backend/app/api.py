from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from pydantic import BaseModel
from a2wsgi import ASGIMiddleware
from .rule_base import *

app = FastAPI(title="Caretta Chatbot")

# for ASGI Handler
wsgi_app = ASGIMiddleware(app)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to chatbot app!."}

# for machine learning
model = None
vector = load("app/joblibsAndDB/count_vect.joblib")

# for machine learning
class get_review(BaseModel):
    review: str

# for machine learning (selecting algorithm)
@app.get("/algorithm/{algorithm}")
async def get_algorithm(algorithm: int):
    print(algorithm, "algorithm")
    global model
    algorithmValues = [
        {"value": 1, "file": "lr_model.joblib"},
        {"value": 2, "file": "svm_model.joblib"},
        {"value": 3, "file": "nb_model.joblib"},
        {"value": 4, "file": "random_forrest_model.joblib"},
        {"value": 5, "file": "decision_tree_model.joblib"},
        {"value": 6, "file": "mlp_model.joblib"}
    ]

    for item in algorithmValues:
        if algorithm == item["value"]:
            model = load("app/joblibsAndDB/" + item["file"])
            break

# for machine learning
"""@app.post("/prediction", response_description="Prediction of text.")
async def get_prediction(gr: get_review):
    text = [gr.review]
    vec = vector.transform(text)
    print(model, "model")
    prediction = model.predict(vec)
    print("predict: ", prediction)

    prediction_object = {"prediction_id": 0, "sentence": gr.review, "prediction": prediction[0], "answer": ""}
    predictionsList = ["kargo", "fiyat", "ozellik"]

    for index, item in enumerate(predictionsList):
        if prediction[0] == item:
            prediction_object["prediction_id"] = index + 1
            break
    
    return prediction_object"""

# for machine learning
@app.post("/prediction", response_description="Prediction of text.")
async def get_prediction(gr: get_review):
    greeting_dataset = pd.read_excel("app/joblibsAndDB/Chatbot_Greeting_Dataset.xlsx")
    bye_dataset = pd.read_excel("app/joblibsAndDB/Chatbot_Bye_Dataset.xlsx")
    
    text = gr.review
    text = convert_to_lowercase(text)

    """print("öncesi:", text)
    text = autocorrect_turkish(text)
    print("sonrası:", text)"""

    result = is_greet_or_bye(text, greeting_dataset, bye_dataset)

    print("resultum:", result)

    greetbyeAnswer = {"answer": ""}

    if result == 1:
        answer = answer_greet_or_bye("greeting")
        print("merhabanın cevabı:", answer)
        print("merhabanın taypı:", type(answer))
        greetbyeAnswer["answer"] = answer
        print(greetbyeAnswer)

        return greetbyeAnswer

    if result == 0:
        answer = answer_greet_or_bye("bye")
        greetbyeAnswer["answer"] = answer
        print(greetbyeAnswer)

        return greetbyeAnswer
    
    if result == -1:
        text = [text]
        vec = vector.transform(text)
        print(model, "model")
        prediction = model.predict(vec)
        print("predict: ", prediction)

        prediction_object = {"prediction_id": 0, "sentence": text[0], "prediction": prediction[0], "answer": ""}
        predictionsList = ["kargo", "fiyat", "ozellik"]

        for index, item in enumerate(predictionsList):
            if prediction[0] == item:
                prediction_object["prediction_id"] = index + 1
                break
        
        if prediction_object["prediction"] == "kargo":
            answer = answer_logistic(autocorrect_turkish(prediction_object["sentence"]))
            prediction_object["answer"] = answer

        if prediction_object["prediction"] == "fiyat":
            answer = answer_price1(prediction_object["sentence"])
            #answer_not_stocks = print_answer1_data(answer)
            if answer == "product_in_not_stocks":
                prediction_object["answer"] = "Maalesef stoklarımızda aradığınız kriterlere uygun bir ürün bulunmamaktadır.\nLütfen daha kolay anlayabilmem için mesajınızı, yazdığınız metnin doğruluğundan emin olarak giriniz :)"
            else:
                prediction_object["answer"] = answer
        
        if prediction_object["prediction"] == "ozellik":
            answer = answer_properties(prediction_object["sentence"])
            prediction_object["answer"] = answer

        print(prediction_object)
        
        return prediction_object
