from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from joblib import load
from pydantic import BaseModel
from a2wsgi import ASGIMiddleware
from .rule_base import *

app = FastAPI(title="Chatbot Natural Stone")

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


class get_review(BaseModel):
    review: str


@app.post("/answer", response_description="Answer of question.")
async def get_answer(gr: get_review):
    languages = convert_txt_to_list("backend/app/languages/language.txt")
    greeting_dataset = pd.read_excel("backend/app/keyword_datasets/Chatbot_Greeting_Dataset.xlsx")
    bye_dataset = pd.read_excel("backend/app/keyword_datasets/Chatbot_Bye_Dataset.xlsx")

    sifa_dataset = pd.read_excel("backend/app/keyword_datasets/sifa.xlsx")
    cinsiyet_dataset = pd.read_excel("backend/app/keyword_datasets/cinsiyet.xlsx")
    burc_dataset = pd.read_excel("backend/app/keyword_datasets/burc.xlsx")
    bakim_dataset = pd.read_excel("backend/app/keyword_datasets/bakim.xlsx")
    kullanim_dataset = pd.read_excel("backend/app/keyword_datasets/kullanim.xlsx")
    sertifika_orijinal_dataset = pd.read_excel("backend/app/keyword_datasets/sertifika_orijinal.xlsx")
    dataset_by_stone = pd.read_excel("backend/app/answers_datasets/dataset_by_stone.xlsx")

    hastalik_dataset = pd.read_excel("backend/app/keyword_datasets/hastalik.xlsx")
    dataset_by_disease = pd.read_excel("backend/app/answers_datasets/dataset_by_disease.xlsx")

    birthday_zodiac_dataset = pd.read_excel("backend/app/keyword_datasets/birthday_zodiac.xlsx")
    dataset_by_zodiac = pd.read_excel("backend/app/answers_datasets/dataset_by_zodiac.xlsx")

    urun_sorgu_dataset = pd.read_excel("backend/app/keyword_datasets/urun_sorgu.xlsx")
    dataset_by_product_query = pd.read_excel("backend/app/answers_datasets/dataset_by_product_query.xlsx")


    message = gr.review

    #size_languages_list = len(languages)
    this_language_message = lang_detect(message).lang

    all_answer = {"answer": ""}

    if this_language_message in languages:
        if this_language_message == "tr":
            label = is_greet_or_bye(message, greeting_dataset, bye_dataset, "Question", 0.80)
            if label == 1:
                answer = answer_greet_or_bye("greeting")
                all_answer["answer"] = answer
                print(all_answer)
                return all_answer

            if label == 0:
                answer = answer_greet_or_bye("bye")
                all_answer["answer"] = answer
                print(all_answer)
                return all_answer

            if label == -1:
                message = convert_to_lowercase(message)

                keywords_stone_datasets_list = [sifa_dataset, cinsiyet_dataset, burc_dataset,
                                                bakim_dataset, kullanim_dataset, sertifika_orijinal_dataset]
                answer_by_stone_column_list = list(dataset_by_stone.columns)
                answer_by_stone_column_list.pop(0)
                # print(answer_column_list)
                answer = answer_by_stone(message, keywords_stone_datasets_list, dataset_by_stone, "stone",
                                         answer_by_stone_column_list)

                if answer != False:
                    all_answer["answer"] = answer
                    print(all_answer)
                    return all_answer

                else:
                    keywords_disease_datasets_list = [hastalik_dataset]
                    answer_by_disease_column_list = list(dataset_by_disease.columns)
                    answer_by_disease_column_list.pop(0)
                    answer = answer_by_disease(message, keywords_disease_datasets_list, dataset_by_disease, "disease",
                                               answer_by_disease_column_list)

                    if answer != False:
                        text = "Aramış olduğunuz hastalığa iyi gelecek olan taşlar: "
                        answer = text + answer
                        all_answer["answer"] = answer
                        print(all_answer)
                        return all_answer

                    else:
                        keywords_zodiac_datasets_list = [birthday_zodiac_dataset]
                        answer_by_zodiac_column_list = list(dataset_by_zodiac.columns)
                        answer_by_zodiac_column_list.pop(0)
                        answer = answer_by_zodiac(message, keywords_zodiac_datasets_list, dataset_by_zodiac,
                                                  "birthday_zodiac", answer_by_zodiac_column_list)

                        if answer != False:
                            text = "Belirtmiş olduğunuz burca uygun taşlar: "
                            answer = text + answer
                            all_answer["answer"] = answer
                            print(all_answer)
                            return all_answer

                        else:
                            keywords_product_query_datasets_list = [urun_sorgu_dataset]
                            answer_by_product_query_column_list = list(dataset_by_product_query.columns)
                            answer_by_product_query_column_list.pop(0)
                            answer = answer_by_product_query(message, keywords_product_query_datasets_list,
                                                             dataset_by_product_query, "stone",
                                                             answer_by_product_query_column_list)
                            # suan buradasin unutma

                            if answer != False:
                                all_answer["answer"] = answer
                                print(all_answer)
                                return all_answer

                            else:
                                answer = "Maalesef mesajınızı algılayamadım"
                                all_answer["answer"] = answer
                                print(all_answer)
                                return all_answer

        else:
            turkish_message = translator(message, this_language_message, "tr")
            turkish_message = convert_to_lowercase(turkish_message)
            print('Orijinal Mesaj: ', message)
            print('Çevrilen Mesaj: ', turkish_message)
            label = is_greet_or_bye(turkish_message, greeting_dataset, bye_dataset, "Question", 0.80)

            if label == 1:
                answer_message = answer_greet_or_bye("greeting")
                orginal_language_message = translator(answer_message, "tr", this_language_message)
                orginal_language_message = orginal_language_message.capitalize()
                all_answer["answer"] = orginal_language_message
                print(all_answer)
                return all_answer

            if label == 0:
                answer_message = answer_greet_or_bye("bye")
                orginal_language_message = translator(answer_message, "tr", this_language_message)
                orginal_language_message = orginal_language_message.capitalize()
                all_answer["answer"] = orginal_language_message
                print(all_answer)
                return all_answer


            if label == -1:
                keywords_datasets_list = [sifa_dataset, cinsiyet_dataset, burc_dataset,
                                          bakim_dataset, kullanim_dataset, sertifika_orijinal_dataset]
                answer_column_list = dataset_by_stone.columns
                answer_column_list = list(dataset_by_stone.columns)
                answer_column_list.pop(0)
                answer = answer_by_stone(turkish_message, keywords_datasets_list, dataset_by_stone, "stone",
                                         answer_column_list)

                if answer != False:
                    orginal_language_message = translator(answer, "tr", this_language_message)
                    orginal_language_message = orginal_language_message.capitalize()
                    all_answer["answer"] = orginal_language_message
                    print(all_answer)
                    return all_answer

                else:
                    keywords_disease_datasets_list = [hastalik_dataset]
                    answer_by_disease_column_list = list(dataset_by_disease.columns)
                    answer_by_disease_column_list.pop(0)
                    answer = answer_by_disease(turkish_message, keywords_disease_datasets_list, dataset_by_disease,
                                               "disease", answer_by_disease_column_list)

                    if answer != False:
                        text = "Aramış olduğunuz hastalığa iyi gelecek olan taşlar: "
                        answer = text + answer
                        orginal_language_message = translator(answer, "tr", this_language_message)
                        orginal_language_message = orginal_language_message.capitalize()
                        all_answer["answer"] = orginal_language_message
                        print(all_answer)
                        return all_answer

                    else:
                        keywords_zodiac_datasets_list = [birthday_zodiac_dataset]
                        answer_by_zodiac_column_list = list(dataset_by_zodiac.columns)
                        answer_by_zodiac_column_list.pop(0)
                        answer = answer_by_zodiac(turkish_message, keywords_zodiac_datasets_list, dataset_by_zodiac,
                                                  "birthday_zodiac", answer_by_zodiac_column_list)

                        if answer != False:
                            text = "Belirtmiş olduğunuz burca uygun taşlar: "
                            answer = text + answer
                            orginal_language_message = translator(answer, "tr", this_language_message)
                            orginal_language_message = orginal_language_message.capitalize()
                            all_answer["answer"] = orginal_language_message
                            print(all_answer)
                            return all_answer

                        else:
                            keywords_product_query_datasets_list = [urun_sorgu_dataset]
                            answer_by_product_query_column_list = list(dataset_by_product_query.columns)
                            answer_by_product_query_column_list.pop(0)
                            answer = answer_by_product_query(turkish_message, keywords_product_query_datasets_list,
                                                             dataset_by_product_query, "stone",
                                                             answer_by_product_query_column_list)
                            # suan buradasin unutma

                            if answer != False:
                                orginal_language_message = translator(answer, "tr", this_language_message)
                                orginal_language_message = orginal_language_message.capitalize()
                                all_answer["answer"] = orginal_language_message
                                print(all_answer)
                                return all_answer

                            else:
                                answer = "Maalesef mesajınızı algılayamadım"
                                orginal_language_message = translator(answer, "tr", this_language_message)
                                orginal_language_message = orginal_language_message.capitalize()
                                all_answer["answer"] = orginal_language_message
                                print(all_answer)
                                return all_answer

    else:
        answer = "Maalesef dilinizi algılayamıyorum!"
        orginal_language_message = translator(answer, "tr", "en")
        answer = "Türkçe: " + answer + " \n" + "English: " + orginal_language_message
        all_answer["answer"] = orginal_language_message
        print(all_answer)
        return all_answer
