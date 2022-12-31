#pip3 install googletrans==4.0.0-rc1
#pip3 install nltk
#pip3 install jellyfish==0.8.2 -qqqq
#pip install jellyfish==0.8.2 -qqqq

import googletrans
from googletrans import Translator

import re

import nltk
from nltk.corpus import *
#nltk.download("all")

import jellyfish
import pandas as pd

import time
import pytz
from pytz import timezone
from datetime import datetime
import pandas as pd
from math import nan, isnan


def convert_txt_to_list(file):
  list_txt = ""
  new_file = open(file, "r")
  for data in new_file:
    list_txt += data

  list_txt = list_txt.split(",")  # metni virgullerden ayirarak listeye atiyorum
  list_txt = re.sub(r"\s+", "", str(list_txt))
  return list_txt


#print(convert_txt_to_list("/content/language.txt"))


def lang_detect(message):
  translator = Translator()
  language = translator.detect(message)
  return language


def translator(text, sourceLanguage, targetLanguage):
  translator = Translator()
  result = translator.translate(text, src=sourceLanguage, dest=targetLanguage)
  return result.text


def convert_data_to_list(dataset, feature):
  questions = []
  for question in dataset[feature]:
    questions.append(question)
  return questions


def calculate_similarity_text(sentence1, sentence2):
  result_similarity = jellyfish.jaro_distance(sentence1, sentence2)
  return result_similarity


def is_greet_or_bye(message, greeting, bye, feature, min_base):
  greeting_dataset = greeting
  bye_dataset = bye
  greet_sentences = convert_data_to_list(greeting_dataset, feature)
  bye_sentences = convert_data_to_list(bye_dataset, feature)

  greet_similarity_list = []
  bye_similarity_list = []

  message_is_greet = False
  message_is_bye = False

  for sentence in greet_sentences: greet_similarity_list.append(calculate_similarity_text(message, sentence))
  for sentence in bye_sentences: bye_similarity_list.append(calculate_similarity_text(message, sentence))

  for greet_similarity in greet_similarity_list:
    if greet_similarity >= min_base:
      message_is_greet = True

  if message_is_greet == True:
    # return answer_greet_or_bye("greeting")
    return 1

  else:

    for bye_similarity in bye_similarity_list:
      if bye_similarity >= min_base:
        message_is_bye = True

    if message_is_bye == True:
      # return answer_greet_or_bye("bye")
      return 0


    else:
      # buraya machine learning gelecek
      # return "\n+ Sorunuzu algılayamadım daha basit şekilde ifade edebilir misiniz? :)"
      return -1


def get_now_time():
  utc_now = datetime.utcnow()
  utc = pytz.timezone('UTC')
  aware_date = utc.localize(utc_now)
  turkey = timezone('Europe/Istanbul')
  now_turkey = aware_date.astimezone(turkey)
  hour = now_turkey.hour
  minute = now_turkey.minute
  second = now_turkey.second

  return [hour, minute, second]


def answer_greet_or_bye(message_type):
  time = get_now_time()
  hour = time[0]

  if message_type == "greeting" and (hour >= 18):
    return "İyi akşamlar, hoş geldiniz."

  if message_type == "greeting" and (12 <= hour < 18):
    return "İyi günler, hoş geldiniz."

  if message_type == "greeting" and (hour < 12):
    return "Günaydın, hoş geldiniz."

  if message_type == "bye" and (hour >= 18):
    return "İyi akşamlar, hoşçakalın."

  if message_type == "bye" and (12 <= hour < 18):
    return "İyi günler, hoşçakalın."

  if message_type == "bye" and (hour < 12):
    return "İyi günler, hoşçakalın."


##################################################################################################

def convert_datasetcolumns_to_dict(keyword_dataset):
  # keyword_dataset = pd.read_excel(keyword_dataset)
  keyword_dataset_columns = keyword_dataset.columns

  column_dict = {}
  for column in range(len(keyword_dataset_columns)):
    column_dict[keyword_dataset_columns[column]] = [[], False]
    for data in keyword_dataset.iloc[:, column]:
      column_dict[keyword_dataset_columns[column]][0].append(data)
      column_dict[keyword_dataset_columns[column]][0] = [x for x in column_dict[keyword_dataset_columns[column]][0] if
                                                         str(x) != 'nan']

  return column_dict


# print(convert_datasetcolumns_to_dict("ne_ise_yarar.xlsx"))

def answer_by_keywords(message, keyword_dataset, answer_dataset, query_column, answer_column):
  # answer_question_dataset_stone = pd.read_excel("answer_question_dataset_stone.xlsx")
  keyword_dict = convert_datasetcolumns_to_dict(keyword_dataset)

  boolean_list = []
  for keyword in keyword_dict.values():
    for key in keyword[0]:
      if key in message:
        keyword[1] = True
        break

    boolean_list.append(keyword[1])

  # print(boolean_list)
  if False not in boolean_list:
    # answer_dataset = pd.read_excel(answer_dataset)

    for key in answer_dataset.loc[:, query_column]:
      if key in message:
        index = answer_dataset[answer_dataset[query_column] == key].index.values
        answer = answer_dataset.iloc[index]
        answer = answer.loc[:, answer_column]
        answer_text = ""
        for line in answer:
          line = line.replace('\n', "")
          answer_text += line

        return answer_text

      else:
        pass

  else:
    return False


def answer_by_stone(message, keywords_datasets_list, answers_dataset, query_column, answer_column_list):
  answer1 = answer_by_keywords(message, keywords_datasets_list[0], answers_dataset, query_column, answer_column_list[0])
  if answer1 == False:
    answer2 = answer_by_keywords(message, keywords_datasets_list[1], answers_dataset, query_column,
                                 answer_column_list[1])
    if answer2 == False:
      answer3 = answer_by_keywords(message, keywords_datasets_list[2], answers_dataset, query_column,
                                   answer_column_list[2])
      if answer3 == False:
        answer4 = answer_by_keywords(message, keywords_datasets_list[3], answers_dataset, query_column,
                                     answer_column_list[3])
        if answer4 == False:
          answer5 = answer_by_keywords(message, keywords_datasets_list[4], answers_dataset, query_column,
                                       answer_column_list[4])
          if answer5 == False:
            answer6 = answer_by_keywords(message, keywords_datasets_list[5], answers_dataset, query_column,
                                         answer_column_list[5])
            if answer6 == False:
              return False
            else:
              print('sertıfıka orıjınal calıstı')
              return answer6
          else:
            print('kullanım calıstı')
            return answer5
        else:
          print('bakım calıstı')
          return answer4
      else:
        print('burc calıstı')
        text_burc = "Belirtmiş olduğunuz taşa ait burç bilgileri: "
        return text_burc + answer3
    else:
      print('cinsiyet calıstı')
      return answer2
  else:
    print('sıfa calıstı')
    return answer1


def answer_by_disease(message, keywords_datasets_list, answers_dataset, query_column, answer_column_list):
  answer1 = answer_by_keywords(message, keywords_datasets_list[0], answers_dataset, query_column, answer_column_list[0])
  if answer1 == False:
    return False

  else:
    print('Hastalık çalıştı')
    return answer1


def answer_by_zodiac(message, keywords_datasets_list, answers_dataset, query_column, answer_column_list):
  answer1 = answer_by_keywords(message, keywords_datasets_list[0], answers_dataset, query_column, answer_column_list[0])
  if answer1 == False:
    return False

  else:
    print('Burçlara göre fonksiyonu çalıştı')
    return answer1


def answer_by_product_query(message, keywords_datasets_list, answers_dataset, query_column, answer_column_list):
  answer1 = answer_by_keywords(message, keywords_datasets_list[0], answers_dataset, query_column, answer_column_list[0])
  if answer1 == False:
    return False

  else:
    print('Urun sorgu fonksiyonu çalıştı')
    return answer1


def convert_to_lowercase(sentence):
  sentence = re.sub('I', 'ı', sentence)
  sentence = re.sub('İ', 'i', sentence)
  sentence = sentence.lower()
  return sentence

