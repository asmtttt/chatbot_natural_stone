
#pip install jellyfish==0.8.2 -qqqq

# rule based greeting and bye chatbot
import pandas as pd
import jellyfish
import datetime
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

import re
import time
import pytz
from pytz import timezone
from datetime import datetime

import sqlite3 as sqlite

import turkishnlp
from turkishnlp import detector

objTurkishNLP = detector.TurkishNLP()
objTurkishNLP.download()
objTurkishNLP.create_word_set()

connection = sqlite.connect("app/joblibsAndDB/ChatobotCarettaDatabase.db") # Tabloya bağlanıyoruz.
cursor = connection.cursor()

def answer_greet_or_bye(message_type):
  utc_now = datetime.utcnow()
  utc = pytz.timezone('UTC')
  aware_date = utc.localize(utc_now)
  turkey = timezone('Europe/Istanbul')
  now_turkey = aware_date.astimezone(turkey)
  hour = now_turkey.hour
  minute = now_turkey.minute
  second = now_turkey.second
  
  if message_type == "greeting" and (hour >= 18):

    text = '''Merhaba iyi akşamlar, hoş geldiniz. size yardımcı olmak için buradayım. 

Firmamızın ürünleri hakkındaki fiyat, özellik, kargo, teslimat, 
kampanyalar ve ödeme koşulları kategorileri dahilinde soracağınız soruları yanıtlamaya çalışacağım.

Size nasıl yardımcı olabilirim?'''

    return text

  if message_type == "greeting" and (12 <= hour < 18):

    text = '''İyi günler, hoş geldiniz. size yardımcı olmak için buradayım. 

Firmamızın ürünleri hakkındaki fiyat, özellik, kargo, teslimat, 
kampanyalar ve ödeme koşulları kategorileri dahilinde soracağınız soruları yanıtlamaya çalışacağım.

Size nasıl yardımcı olabilirim?'''

    return text

  if message_type == "greeting" and (hour < 12):

    text = '''Günaydın, hoş geldiniz. size yardımcı olmak için buradayım. 

Firmamızın ürünleri hakkındaki fiyat, özellik, kargo, teslimat, 
kampanyalar ve ödeme koşulları kategorileri dahilinde soracağınız soruları yanıtlamaya çalışacağım.

Size nasıl yardımcı olabilirim?'''

    return text

  if message_type == "bye" and (hour >= 18):
    
    text = '''İyi akşamlar, bizi tercih ettiğiniz için teşekkür ederim. 
Aynı şekilde başka bir sorunuz olursa ben yine burada olacağım, hoşçakalın :)'''

    return text

  if message_type == "bye" and (12 <= hour < 18):

    text = '''İyi günler, bizi tercih ettiğiniz için teşekkür ederim. 
Aynı şekilde başka bir sorunuz olursa ben yine burada olacağım, hoşçakalın :)'''

    return text

  if message_type == "bye" and (hour < 12):

    text = '''İyi günler, bizi tercih ettiğiniz için teşekkür ederim. 
Aynı şekilde başka bir sorunuz olursa ben yine burada olacağım, hoşçakalın :)'''
    return text


def convert_data_to_list(dataset):
  questions = []
  for question in dataset["Question"]:
    questions.append(question)
  return questions


def calculate_similarity_text(sentence1, sentence2):
  result_similarity = jellyfish.jaro_distance(sentence1, sentence2)
  return result_similarity
  #jellyfish.damerau_levenshtein_distance(u'jellyfish', u'jellyfihs')


def is_greet_or_bye(message, greeting, bye):
  greeting_dataset = greeting
  bye_dataset = bye
  greet_sentences = convert_data_to_list(greeting_dataset)
  bye_sentences = convert_data_to_list(bye_dataset)

  greet_similarity_list = []
  bye_similarity_list = []

  message_is_greet = False
  message_is_bye = False

  for sentence in greet_sentences:
    greet_similarity_list.append(calculate_similarity_text(message, sentence))

  for sentence in bye_sentences:
    bye_similarity_list.append(calculate_similarity_text(message, sentence))
  
  for greet_similarity in greet_similarity_list:
    if greet_similarity >= 0.80:
      message_is_greet = True

  if message_is_greet == True:
    #return answer_greet_or_bye("greeting")
    return 1

  else:

    for bye_similarity in bye_similarity_list:
      if bye_similarity >= 0.80:
        message_is_bye = True

    if message_is_bye == True:
      #return answer_greet_or_bye("bye")
      return 0
      exit()

    else:
      # buraya machine learning gelecek
      #return "\n+ Sorunuzu algılayamadım daha basit şekilde ifade edebilir misiniz? :)"
      return -1


def merge_two_string_in_message(message, word1, word2):
  message_list = message.split()
  all_indexes_word1 = [] # 5-7-10
  for i in range(0, len(message_list)) : 
    if message_list[i] == word1: 
        all_indexes_word1.append(i)

  all_indexes_word2 = [] # 5-7-10
  for i in range(0, len(message_list)) : 
    if message_list[i] == word2: 
        all_indexes_word2.append(i)

  size_index_list_word1 = len(all_indexes_word1)
  size_index_list_word2 = len(all_indexes_word2)

  if size_index_list_word1 > size_index_list_word2:
    for i in all_indexes_word1:
      for c in all_indexes_word2:
        if c-i == 1:
          merge_words = ""
          merge_words += message_list[i]
          merge_words += message_list[c]
          message_list.append(merge_words)
        
        else:
          pass
      
  if size_index_list_word1 < size_index_list_word2:
    for i in all_indexes_word2:
      for c in all_indexes_word1:
        if i-c == 1:
          merge_words = ""
          merge_words += message_list[c]
          merge_words += message_list[i]
          message_list.append(merge_words)
        
        else:
          pass
    

  if size_index_list_word1 == size_index_list_word2:
    for i in all_indexes_word1:
      for c in all_indexes_word2:
        if c-i == 1:
          merge_words = ""
          merge_words += message_list[i]
          merge_words += message_list[c]
          message_list.append(merge_words)
        
        else:
          pass

  message = " ".join(message_list)
  return message


def answer_logistic_1(message):
  answer = "Tüm ürünlerimizde kargo hizmetleri ücretlidir."
  answer2 = '''Aras Kargo için Ücret: 18.99        
Yurtiçi Kargo için Ücret: 14.99        
Mng Kargo için Ücret: 30.00
Sürat Kargo için Ücret: 11.99
Ups için Ücret: 35.99'''

  kargo_keyword1_1 = ["kargo","teslimat", "lojistik","gonderi"]
  kargo_keyword1_2 = ["ücretsiz", "ücret", "ücret", "ucret", "fiyat", "bedel", "ucretlimi","ucretsiz"]
  kargo_keyword1_3 = ["mi", "mı", "mu", "mü", "musunuz", "mısınız", "misiniz"]

  k11 = False
  k12 = False
  k13 = False
 
  for key1_1 in kargo_keyword1_1:
    if key1_1 in message:
      k11 = True

  for key1_2 in kargo_keyword1_2:
    if key1_2 in message:
      k12 = True

  for key1_3 in kargo_keyword1_3:
    if key1_3 in message:
      k13 = True

  if (k11 == True and k12 == True and k13 == True):
    return answer + "\nAnlaşmalı olduğumuz kargo firmaları için ücret tutarları;\n\n" + answer2

  else:
    return False


def answer_logistic_2(message):
  answer = '''Anlaşmalı olduğumuz kargo firmaları için ücret tutarları;\n
Aras Kargo için Ücret: 18.99        
Yurtiçi Kargo için Ücret: 14.99        
Mng Kargo için Ücret: 30.00
Sürat Kargo için Ücret: 11.99
Ups için Ücret: 35.99'''

  kargo_keyword2_1 = ["kargo","teslimat", "lojistik","gonderi", "aras kargo", "surat kargo", "mng kargo","yurtici kargo","ups", "UPS", "sürat kargo", "yurtiçi kargo"]
  kargo_keyword2_2 = ["ücretsiz", "ücret", "ücretli", "fiyat", "bedel", "ucret", "ucretsiz", "ucretli", "tutar", "miktar"]
  kargo_keyword2_3 = ["mi", "mı", "mu", "mü", "", "musunuz", "mısınız", "misiniz", "nekadar", "nedir", "ne"]
  # ne kadar - kadar kelımesının ındexını bul ve ondan oncekı kelımenın ne olup olmadıgını sorgula

  message = merge_two_string_in_message(message, "ne", "kadar")

  k21 = False
  k22 = False
  k23 = False
 
  for key2_1 in kargo_keyword2_1:
    if key2_1 in message:
      k21 = True

  for key2_2 in kargo_keyword2_2:
    if key2_2 in message:
      k22 = True

  for key2_3 in kargo_keyword2_3:
    if key2_3 in message:
      k23 = True

  if (k21 and k22 and k23) == True:
    return answer

  else:
    return False


def answer_logistic_3(message):
  answer = "Anlaşmalı olduğumuz tüm kargo şirketleri 1 ile 3 iş günü içerisinde teslimat sürecini tamamlamaktadır."
  kargo_keyword3_1 = ["kargo","teslimat", "lojistik","gonderi", "sipariş", "ürün", "urun","gönderi","paket"]
  kargo_keyword3_2 = ["teslim", "ulaşacak", "iletim", "iletilecek", "getir", "yolla", "bırak", "ver", "gel", "edil","ulaş"]
  kargo_keyword3_3 = ["aynıgün", "zaman", "süre", "nezaman", "kacgun", "kaçgün", "kaçgünde", "kacgunde"]

  message = merge_two_string_in_message(message, "kac", "gun")
  message = merge_two_string_in_message(message, "kaç", "gün")
  message = merge_two_string_in_message(message, "kaç", "günde")
  message = merge_two_string_in_message(message, "kac", "gunde")
  message = merge_two_string_in_message(message, "ne", "zaman")
  message = merge_two_string_in_message(message, "aynı", "gün")
  message = merge_two_string_in_message(message, "aynı", "gun")

  k31 = False
  k32 = False
  k33 = False

  for key3_1 in kargo_keyword3_1:
    if key3_1 in message:
      k31 = True

  for key3_2 in kargo_keyword3_2:
    if key3_2 in message:
      k32 = True

  for key3_3 in kargo_keyword3_3:
    if key3_3 in message:
      k33 = True

  if (k31 and k32 and k33) == True:
    return answer

  else:
    return False


def answer_logistic_4(message):
  answer = "Sipariş takip işlemi anlaşmalı olduğumuz kargo şirketlerine ait internet adresleri tarafından gerçekleştirilmektedir."
  answer2 = '''Aras Kargo Sipariş takip için: https://kargomnerede.co/kargolar/aras-kargo
Yurtiçi Kargo Sipariş takip için: https://www.yurticikargo.com/       
Mng Kargo Sipariş takip için: https://www.mngkargo.com.tr/gonderitakip
Sürat Kargo Sipariş takip için: https://suratkargo.com.tr/KargoTakip/
Ups Sipariş takip için: https://www.ups.com/track?loc=tr_TR&requester=ST/'''

  kargo_keyword4_1 = ["kargo","teslimat", "lojistik", "gonderi", "sipariş", "ürün", "urun", "gönderi", "paket", "pakedimi"]
  kargo_keyword4_2 = ["incele", "izle", "görebil", "gör", "bakabil", "bak", "öğren", "takip", "ulaş", "eriş"]
  kargo_keyword4_3 = ["nasıl", "nereden", "hangiadres", "hangi adresten", "hangi yolla", "hangi siteden", "adres", "internetadresinden", "var mı", "varmı", "mu", "mü"]

  message = merge_two_string_in_message(message, "hangi", "adresten")
  message = merge_two_string_in_message(message, "hangi", "yolla")
  message = merge_two_string_in_message(message, "hangi", "adres")
  message = merge_two_string_in_message(message, "hangi", "siteden")
  message = merge_two_string_in_message(message, "internet", "adresinden")


  k41 = False
  k42 = False
  k43 = False

  for key4_1 in kargo_keyword4_1:
    if key4_1 in message:
      k41 = True

  for key4_2 in kargo_keyword4_2:
    if key4_2 in message:
      k42 = True

  for key4_3 in kargo_keyword4_3:
    if key4_3 in message:
      k43 = True

  if (k41 and k42 and k43) == True:
    return answer + "\n\nAşağıdaki linklerden internet adreslerine kolayca erişebilirsiniz:\n\n" + answer2

  else:
    return False


def answer_logistic_5(message):
  answer = "Kargo hizmetleri ile ilgili şikayet ve önerilerinizi anlaşmalı olduğumuz kargo şirketlerine iletmeniz gerekmektedir."
  answer2 = '''Aras Kargo: 444 25 52
Yurtiçi Kargo: 444 99 99
Mng Kargo: 0(850) 222 06 06
Sürat Kargo: 0(850) 202 02 02
Ups: 0(850) 255 00 66'''

  kargo_keyword5_1 = ["kargo","teslimat", "lojistik", "sipariş", "ürün", "urun", "paket", "pakedimi"] # kim
  kargo_keyword5_2 = ["teslimedil", "gel",  "bakabil", "bak", "öğren", "takip", "ulaş", "eriş", "gonderil"] # ne
  kargo_keyword5_3 = ["hasarli", "hasarlı", "gec", "geç", "eksik","yarim yamalak", "yarım yamalak", "bozuk","hatali", "hatalı", "yanlis adres", "yirtik","kirilmis","kirik", "yırtık", "kırık", "kırılmış"] # nasil
  kargo_keyword5_4 = ["neden", "niye", "nicin", "hangi sebeple", "hangi nedenden", "ne olduda", "niçin"] # soru kalibi

  message = merge_two_string_in_message(message, "teslim", "edil")
  message = merge_two_string_in_message(message, "hangi", "sebeple")
  message = merge_two_string_in_message(message, "hangi", "nedenden")
  message = merge_two_string_in_message(message, "ne", "olduda")
  message = merge_two_string_in_message(message, "yanlis", "adres")
  message = merge_two_string_in_message(message, "yanlış", "adres")
  message = merge_two_string_in_message(message, "yarim", "yamalak")
  message = merge_two_string_in_message(message, "yarım", "yamalak")

  k51 = False
  k52 = False
  k53 = False
  k54 = False

  for key5_1 in kargo_keyword5_1:
    if key5_1 in message:
      k51 = True

  for key5_2 in kargo_keyword5_2:
    if key5_2 in message:
      k52 = True

  for key5_3 in kargo_keyword5_3:
    if key5_3 in message:
      k53 = True

  for key5_4 in kargo_keyword5_4:
    if key5_4 in message:
      k54 = True

  if (k51 == True and k52 == True and k53 == True or k54 == True):
    return answer + "\n\nAşağıdaki iletişim adreslerinden kolayca erişebilirsiniz:\n\n" + answer2

  else:
    return False
  

def answer_logistic(message):
  answer1 = answer_logistic_1(message)
  if answer1 == False:
    answer2 = answer_logistic_2(message)
    if answer2 == False:
      answer3 = answer_logistic_3(message)
      if answer3 == False:
        answer4 = answer_logistic_4(message)
        if answer4 == False:  
          answer5 = answer_logistic_5(message)
          if answer5 == False:  
            return "Maalesef sorunuzu algılayamadım :( Lütfen daha kolay anlayabilmem için mesajınızı, yazdığınız metnin doğruluğundan emin olarak giriniz!"

          else:
            return answer5
        else:
          return answer4
      else:
        return answer3
      
    else:
      return answer2

  else:
    return answer1


def answer_price(message):
  pass

def check_not_stonks(ram_in_not_stocks, ssd_in_not_stocks):
  if ram_in_not_stocks != 0 and ssd_in_not_stocks == 0:
    return "Maalesef stoklarımızda belirtmiş olduğunuz türde bir Ram (Bellek) bulunmamaktadır."

  if ram_in_not_stocks == 0 and ssd_in_not_stocks != 0:
    return "Maalesef stoklarımızda belirtmiş olduğunuz türde bir SSD (Hafıza) bulunmamaktadır."

  if ram_in_not_stocks != 0 and ssd_in_not_stocks != 0:
    return "Maalesef stoklarımızda belirtmiş olduğunuz türde bir Ram (bellek) ve SSD (Hafıza) bulunmamaktadır."

  else:
    return True


def convert_true_to_text(key1, text):
  if key1 == True:
    return text
  
  else:
    return False


def convert_true_to_text_on_all(ram_8, ram_16,  
           nvidia3050, ti3050, IntelUHD, Mx330, nvidia1650, ti1650, Iris, 
           w11pro, w10pro, ubuntu, w10home, w11home, freedos, 
           i7core, ryzen5, i3core, i5core, ryzen7,
           ssd_256, ssd_512, ssd_1024):
  
  ram_8 = convert_true_to_text(ram_8, "8.0")
  ram_16 = convert_true_to_text(ram_16, "16.0")
  nvidia3050 = convert_true_to_text(nvidia3050, "Nvidia GeForce RTX 3050")
  ti3050 = convert_true_to_text(ti3050, "Nvidia GeForce RTX 3050 Ti")
  IntelUHD = convert_true_to_text(IntelUHD, "Intel UHD Graphics")
  Mx330 = convert_true_to_text(Mx330, "Nvidia GeForce MX330")
  nvidia1650 = convert_true_to_text(nvidia1650, "Nvidia GeForce GTX 1650")
  ti1650 = convert_true_to_text(ti1650, "Nvidia GeForce GTX 1650 Ti")
  Iris = convert_true_to_text(Iris, "Intel Iris Xe Graphics")
  w11pro = convert_true_to_text(w11pro, "Windows 11 Pro")
  w10pro = convert_true_to_text(w10pro, "Windows 10 Pro")
  ubuntu = convert_true_to_text(ubuntu, "Ubuntu")
  w10home = convert_true_to_text(w10home, "Windows10 Home")
  w11home = convert_true_to_text(w11home, "Windows11 Home")
  freedos = convert_true_to_text(freedos, "Yok (Free-Dos)")
  i7core = convert_true_to_text(i7core, "Intel Core İ7")
  ryzen5 = convert_true_to_text(ryzen5, "AMD Ryzen 5")
  i3core = convert_true_to_text(i3core, "Intel Core İ3")
  i5core = convert_true_to_text(i5core, "Intel Core İ5")
  ryzen7 = convert_true_to_text(ryzen7, "AMD Ryzen 7")
  ssd_256 = convert_true_to_text(ssd_256, "256.0")
  ssd_512 = convert_true_to_text(ssd_512, "512.0")
  ssd_1024 = convert_true_to_text(ssd_1024, "1024.0")

  liste = [[ram_8, ram_16],  
           [nvidia3050, ti3050, IntelUHD, Mx330, nvidia1650, ti1650, Iris], 
           [w11pro, w10pro, ubuntu, w10home, w11home, freedos], 
           [i7core, ryzen5, i3core, i5core, ryzen7],
           [ssd_256, ssd_512, ssd_1024]]

  return liste


def get_price(liste_text_false, cursor):
  ram = [x for x in liste_text_false[0] if x != False]
  ekranKarti = [x for x in liste_text_false[1] if x != False]
  os = [x for x in liste_text_false[2] if x != False]
  islemci = [x for x in liste_text_false[3] if x != False]
  ssd = [x for x in liste_text_false[4] if x != False]

  elements = [ram, ekranKarti, os, islemci, ssd]

  ramStr, ekranStr, isletimStr, islemciStr, ssdStr = ["ram", 0],["ekrankarti", 0],["isletimsistemi", 0],["islemci", 0],["ssd", 0]

  if (len(ram) != 0):
    ramStr[1] = ram[0]
  if (len(ekranKarti) != 0):
    ekranStr[1] = ekranKarti[0]
  if (len(os) != 0):
    isletimStr[1] = os[0]
  if (len(islemci) != 0):
    islemciStr[1] = islemci[0]
  if (len(ssd) != 0):
    ssdStr[1] = ssd[0]

  strList = [ramStr, ekranStr, isletimStr, islemciStr, ssdStr]

  newstrList = []
  for i in range(len(strList)):
    if (strList[i][1] != 0):
      newstrList.append(strList[i])

  strList = newstrList
  length = len(strList)

  if length == 5:    
    cursor.execute("SELECT DISTINCT marka, model, ram, ekrankarti, isletimsistemi, islemci, ssd, fiyatnakit FROM product WHERE ram = ? and ekrankarti = ? and isletimsistemi = ? and islemci = ? and ssd = ?", (ram[0],ekranKarti[0],os[0], islemci[0], ssd[0]))
    data = cursor.fetchall()

    if (len(data) == 0):
      return "product_in_not_stocks"
    else:
      return data

  elif length == 4:  
    query = "SELECT DISTINCT marka, model, ram, ekrankarti, isletimsistemi, islemci, ssd, fiyatnakit FROM product WHERE {} = ? and {} = ? and {} = ? and {} = ?".format(strList[0][0], strList[1][0], strList[2][0], strList[3][0])
    cursor.execute(query,(strList[0][1], strList[1][1], strList[2][1], strList[3][1]))
    data = cursor.fetchall()
    if (len(data) == 0):
      return "product_in_not_stocks"
    else:
      return data
  
  elif length == 3:
    query = "SELECT DISTINCT marka, model, ram, ekrankarti, isletimsistemi, islemci, ssd, fiyatnakit FROM product WHERE {} = ? and {} = ? and {} = ?".format(strList[0][0], strList[1][0], strList[2][0])
    cursor.execute(query,(strList[0][1], strList[1][1], strList[2][1]))
    data = cursor.fetchall()
    if (len(data) == 0):
      return "product_in_not_stocks"
    else:
      return data

  elif length == 2:
    query = "SELECT DISTINCT marka, model, ram, ekrankarti, isletimsistemi, islemci, ssd, fiyatnakit FROM product WHERE {} = ? and {} = ?".format(strList[0][0], strList[1][0])
    cursor.execute(query,(strList[0][1], strList[1][1]))
    data = cursor.fetchall()
    if (len(data) == 0):
      return "product_in_not_stocks"
    else:
      return data
    
  elif length == 1:
    query = "SELECT DISTINCT marka, model, ram, ekrankarti, isletimsistemi, islemci, ssd, fiyatnakit FROM product WHERE {} = ?".format(strList[0][0])
    cursor.execute(query,(strList[0][1],))
    data = cursor.fetchall()
    if (len(data) == 0):
      return "product_in_not_stocks"
    else:
      return data

  else:
    return "product_in_not_stocks"


def answer_price1(message):
  message_list = message.split()

  price_keyword_ram_8_16 = ["8","16"] # 16 gb ram
  price_keyword_ram = ["ram","bellek","RAM","BELLEK"] # 16 gb ram

  price_keyword_ekran_karti_3050Ti = ["nvidia geforce rtx 3050 ti", "nvidiageforcertx3050ti", "nvidia geforce rtx 3050ti", "nvidia geforce rtx3050 ti", "nvidia 3050 ti", "nvidia 3050ti", "3050ti", "3050 ti", "rtx3050ti", "rtx3050 ti", "rtx 3050ti", "rtx 3050 ti", "geforce 3050ti", "geforce 3050 ti", "geforce rtx 3050ti", "geforce rtx 3050 ti"] # ne
  price_keyword_ekran_karti_3050 = ["nvidia geforce rtx 3050", "nvidiageforcertx3050", "nvidia geforce rtx3050", "nvidia3050", "nvidia 3050", "3050", "rtx3050", "rtx 3050", "geforce 3050", "geforce rtx 3050", "geforce rtx3050", "geforcertx 3050"] # metin de 3050 varsa sadece 3050 3050 ti varsa ti sadece ti varsa metnin icinde 3650 mi yoksa 1650 var diye kontrol et
  price_keyword_ekran_karti_IntelUHDGraphics = ["uhd","intel uhd graphics", "intel uhd", "uhd graphics","uhd ekran karti", "inteluhd", "uhdgrafik", "uhd grafik", "uhdgrafik"]
  price_keyword_ekran_karti_MX330 = ["mx330", "nvidia geforce mx330", "mx 330", "geforce mx330", "geforcemx330", "geforcemx 330", "nvidia geforce mx 330", "geforce mx 330", "nvidia mx330", "nvidia mx 330", "330", "nvidia 330"]
  price_keyword_ekran_karti_1650Ti = ["nvidia geforce rtx 1650 ti", "nvidiageforcertx1650ti", "nvidia geforce rtx 1650ti", "nvidia geforce rtx1650 ti", "nvidia 1650 ti", "nvidia 1650ti", "1650ti", "1650 ti", "rtx1650ti", "rtx1650 ti", "rtx 1650ti", "rtx 1650 ti", "geforce 1650ti", "geforce 1650 ti", "geforce rtx 1650ti", "geforce rtx 1650 ti"]
  price_keyword_ekran_karti_1650 = ["nvidia geforce rtx 1650", "nvidiageforcertx1650", "nvidia geforce rtx1650", "nvidia1650", "nvidia 1650", "1650", "rtx1650", "rtx 1650", "geforce 1650", "geforce rtx 1650", "geforce rtx1650", "geforcertx 1650"]
  price_keyword_ekran_karti_IntelIris = ["intel iris", "iris", "iris xe", "iris grafik", "iris grafik karti", "irisxe", "intel iris grafik karti", "iris ekran karti"]

  price_keyword_w11pro = ["w11pro", "w11 pro", "w 11 pro", "win11pro", "win 11 pro", "win11 pro", "win 11pro", "windows11pro", "windows 11 pro", "windows 11pro", "windows11 pro"]
  price_keyword_w10pro = ["w10pro", "w10 pro", "w 10 pro", "win10pro", "win 10 pro", "win10 pro", "win 10pro", "windows10pro", "windows 10 pro", "windows 10pro", "windows10 pro"]
  price_keyword_ubuntu = ["ubuntu"]
  price_keyword_w10home = ["w10home", "w10 home", "w 10 home", "win10home", "win 10 home", "win10 home", "win 10home", "windows10home", "windows 10 home", "windows 10home", "windows10 home"]
  price_keyword_w11home = ["w11home", "w11 home", "w 11 home", "win11home", "win 11 home", "win11 home", "win 11home", "windows11home", "windows 11 home", "windows 11home", "windows11 home"]
  price_keyword_freedos = ["freedos", "free dos", "yok (freedos)", "yok freedos", "işletim sistemi yok", "free"]

  price_keyword_core_i7 = ["intel core i7", "intelcore i7", "intel corei7", "intel i7", "core i7", "i7", "corei7", "i 7", "i7 işlemci", "i7işlemci"]
  price_keyword_ryzen5 = ["amd ryzen 5", "amdryzen5", "amd ryzen5", "amdryzen 5", "ryzen5", "ryzen 5", "amd 5", "amd5", "ryzen5 işlemci"]
  price_keyword_core_i3 = ["intel core i3", "intelcore i3", "intel corei3", "intel i3", "core i3", "i3", "corei3", "i 3", "i3 işlemci", "i3işlemci"]
  price_keyword_core_i5 = ["intel core i5", "intelcore i5", "intel corei5", "intel i5", "core i5", "i5", "corei5", "i 5", "i5 işlemci", "i5işlemci"]
  price_keyword_ryzen7 = ["amd ryzen 7", "amdryzen7", "amd ryzen7", "amdryzen 7", "ryzen7", "ryzen 7", "amd 7", "amd7", "ryzen7 işlemci"]

  price_keyword_ssd_size = ["256", "512", "1024"]  
  price_keyword_ssd = ["ssd","SSD","hafıza","kapasite"]

  ram_8 = False
  ram_16 = False
  nvidia3050 = False
  ti3050 = False
  IntelUHD = False
  Mx330 = False
  nvidia1650 = False
  ti1650 = False
  Iris = False
  w11pro = False
  w10pro = False
  ubuntu = False
  w10home = False
  w11home = False
  freedos = False
  i7core = False
  ryzen5 = False
  i3core = False
  i5core = False
  ryzen7 = False
  ssd_256 = False
  ssd_512 = False
  ssd_1024 = False


  ram_in_not_stocks = 0
  ssd_in_not_stocks = 0

  # for ram
  for word in message_list: # MERHABA 8 GB RAM BILGISAYAR FIYATLARI NEDIR
    if word in price_keyword_ram:
       index_word = message_list.index(word)
       if message_list[index_word - 1] == "8" or message_list[index_word - 2] == "8":
         ram_8 = True

       if message_list[index_word - 1] == "16" or message_list[index_word - 2] == "16":
         ram_16 = True

       else:
          ram_in_not_stocks += 1

    else:
      pass

  # for ekran karti
  for word in message_list: # MERHABA Iris ekran karti BILGISAYAR FIYATLARI NEDIR
    if word in price_keyword_ekran_karti_3050Ti:
      ti3050 = True
      break
    
    if word in price_keyword_ekran_karti_3050:
      if word == "3050":
        index_word_3050 = message_list.index(word)
        if message_list[index_word_3050 + 1] == "ti":

          ti3050 = True
          break

        else:
          nvidia3050 = True
          break  
      else:
        nvidia3050 = True
        break

    if word in price_keyword_ekran_karti_IntelUHDGraphics:
      IntelUHD = True
      break

    if word in price_keyword_ekran_karti_MX330:
      Mx330 = True
      break

    if word in price_keyword_ekran_karti_1650Ti:
      ti1650 = True
      break

    if word in price_keyword_ekran_karti_1650:
      if word == "1650":
        index_word_1650 = message_list.index(word)
        if message_list[index_word_1650 + 1] == "ti":

          ti1650 = True
          break

        else:
          nvidia1650 = True
          break  
      else:
        nvidia1650 = True
        break

    if word in price_keyword_ekran_karti_IntelIris:
      Iris = True
      break

    else:
      pass

  # işletim sistemi
  for keyword in price_keyword_w11pro:
    if keyword in message:
      w11pro = True
  
  for keyword in price_keyword_w10pro:
    if keyword in message:
      w10pro = True

  for keyword in price_keyword_ubuntu:
    if keyword in message:
      ubuntu = True

  for keyword in price_keyword_w10home:
    if keyword in message:
      w10home = True

  for keyword in price_keyword_w11home:
    if keyword in message:
      w11home = True
    
  for keyword in price_keyword_freedos:
    if keyword in message:
      freedos = True

  # for işlemci

  for keyword in price_keyword_core_i7:
    if keyword in message:
       i7core = True

  for keyword in price_keyword_ryzen5:
    if keyword in message:
       ryzen5 = True

  for keyword in price_keyword_core_i3:
      if keyword in message:
        i3core = True
  
  for keyword in price_keyword_core_i5:
    if keyword in message:
       i5core = True

  for keyword in price_keyword_ryzen7:
    if keyword in message:
       ryzen7 = True

  # for ssd
  for word in message_list: # MERHABA 8 GB RAM BILGISAYAR FIYATLARI NEDIR
    if word in price_keyword_ssd:
       index_word_ssd = message_list.index(word)
       if message_list[index_word_ssd - 1] == "256":
         ssd_256 = True

       if message_list[index_word_ssd - 1] == "512" :
         ssd_512 = True

       if message_list[index_word_ssd - 1] == "1024" :
         ssd_1024 = True 

       else:
          ssd_in_not_stocks += 1

    else:
      pass
  
  liste_text_false = convert_true_to_text_on_all(ram_8, ram_16,  
           nvidia3050, ti3050, IntelUHD, Mx330, nvidia1650, ti1650, Iris, 
           w11pro, w10pro, ubuntu, w10home, w11home, freedos, 
           i7core, ryzen5, i3core, i5core, ryzen7,
           ssd_256, ssd_512, ssd_1024)
  
  data = get_price(liste_text_false, cursor)
  #state_of_stock = check_not_stonks(ram_in_not_stocks, ssd_in_not_stocks)
  
  return data


def answer_properties_1(message):
  answer = '''Tüm ürünlerimizde harici olarak ram (bellek) takılabilmektedir'''

  properties_keyword1_1 = ["urun", "ürün", "bilgisayar", "pc","computer", "makine", "cihaz", "bilgesayar", "b.sayar"]
  properties_keyword1_2 = ["ram", "rem", "bellek", "harici ram", "harici", "bellek", "ek ram", "ek rem", "harici rem", "ram takviyesi", "slot",]
  properties_keyword1_3 = ["takmak", "takilabil", "takar", "takılabiliyor", "takılabilir", 
                           "takabilir","koyabil", "yapabil", "koyul", "takıl", "takabil", "yapıl", "yapılabil", "edil",  
                           "ilaveetmek", "monteetmek", "yapılabiliyor", "eklen", "yükselt", "arttır",
                           "ilaveedilebilir", "monteedilebilir", "ilaveedilebiliyor", "monteedilebiliyor",
                           "ilaveedebilir", "monteedebilir", "ilaveedebiliyor", "monteedebiliyor",
                           "ilaveeder", "monteeder", "ilaveedilebilirmi", "monteedilebilirmi", 
                           "ilaveedilebiliyormu", "monteedilebiliyormu", "ilaveedilebilirmi", "monteedilebilirmi", 
                           "ilaveedebilirmi", "monteedebilirmi", "ilaveedebilirmisiniz", "monteedebilirmiyiz",
                           "ilaveedebiliyormu", "monteedebiliyormu",
                           "ilaveedebiliyormuyuz", "ilaveedebiliyormuyum", "ilaveedebiliyormusunuz",
                           "monteedebiliyormuyuz", "monteedebiliyormuyum", "monteedebiliyormusunuz",
                           "ilaveedermi", "monteedermi", "olur", "oluyor", "olacak", "varmı", "mevcutmu",
                           "bulun"]

  message = merge_two_string_in_message(message, "olur", "mu")
  message = merge_two_string_in_message(message, "oluyor", "mu")
  message = merge_two_string_in_message(message, "olacak", "mı")

  message = merge_two_string_in_message(message, "var", "mı")
  message = merge_two_string_in_message(message, "mevcut", "mu")

  message = merge_two_string_in_message(message, "takılabilir", "mi")
  message = merge_two_string_in_message(message, "takılabiliyor", "mu")
  message = merge_two_string_in_message(message, "takabilir", "miyim")
  message = merge_two_string_in_message(message, "takabilir", "misiniz")
  message = merge_two_string_in_message(message, "takabilir", "miyiz")
  message = merge_two_string_in_message(message, "takabiliyor", "musunuz")
  message = merge_two_string_in_message(message, "takabiliyor", "muyum")
  message = merge_two_string_in_message(message, "takabiliyor", "muyuz")
  message = merge_two_string_in_message(message, "takar", "mısınız")
  message = merge_two_string_in_message(message, "takar", "mısın")
  
  message = merge_two_string_in_message(message, "edilebiliyor", "mu")
  message = merge_two_string_in_message(message, "edebilir", "miyiz")
  message = merge_two_string_in_message(message, "edebilir", "mi")
  message = merge_two_string_in_message(message, "edebilir", "misiniz")
  message = merge_two_string_in_message(message, "edilebilir", "mi")
  message = merge_two_string_in_message(message, "edebiliyor", "mu")
  message = merge_two_string_in_message(message, "edebiliyor", "musunuz")
  message = merge_two_string_in_message(message, "edebiliyor", "muyuz")
  message = merge_two_string_in_message(message, "eder", "mi")
  message = merge_two_string_in_message(message, "eder", "misiniz")

  message = merge_two_string_in_message(message, "ilave", "etmek")
  message = merge_two_string_in_message(message, "ilave", "edilebilirmi")
  message = merge_two_string_in_message(message, "ilave", "edilebiliyormu")
  message = merge_two_string_in_message(message, "ilave", "edebilirmiyiz")
  message = merge_two_string_in_message(message, "ilave", "edebilirmisiniz")
  message = merge_two_string_in_message(message, "ilave", "edebilirmi")
  message = merge_two_string_in_message(message, "ilave", "edebiliyormu")
  message = merge_two_string_in_message(message, "ilave", "edebiliyormuyuz")
  message = merge_two_string_in_message(message, "ilave", "edebiliyormusunuz")
  message = merge_two_string_in_message(message, "ilave", "edermi")

  message = merge_two_string_in_message(message, "monte", "etmek")
  message = merge_two_string_in_message(message, "monte", "edilebilirmi")
  message = merge_two_string_in_message(message, "monte", "edilebiliyormu")
  message = merge_two_string_in_message(message, "monte", "edebilirmiyiz")
  message = merge_two_string_in_message(message, "monte", "edebilirmisiniz")
  message = merge_two_string_in_message(message, "monte", "edebilirmi")
  message = merge_two_string_in_message(message, "monte", "edebiliyormu")
  message = merge_two_string_in_message(message, "monte", "edebiliyormuyuz")
  message = merge_two_string_in_message(message, "monte", "edebiliyormusunuz")
  message = merge_two_string_in_message(message, "moonte", "edermi")

  message = merge_two_string_in_message(message, "ilaveedilebilir", "mi")
  message = merge_two_string_in_message(message, "ilaveedilebiliyor", "mu")
  message = merge_two_string_in_message(message, "ilaveedebilir", "miyim")
  message = merge_two_string_in_message(message, "ilaveedebilir", "miyiz")
  message = merge_two_string_in_message(message, "ilaveedebilir", "misiniz")
  message = merge_two_string_in_message(message, "ilaveedebiliyor", "muyum")
  message = merge_two_string_in_message(message, "ilaveedebiliyor", "musunuz")
  message = merge_two_string_in_message(message, "ilaveedebiliyor", "muyuz")
  message = merge_two_string_in_message(message, "ilaveeder", "misiniz")
  message = merge_two_string_in_message(message, "ilaveeder", "mi")

  message = merge_two_string_in_message(message, "ilave", "etmek")
  message = merge_two_string_in_message(message, "ilave", "edilebilir")
  message = merge_two_string_in_message(message, "ilave", "edilebiliyor")
  message = merge_two_string_in_message(message, "ilave", "edebilir")
  message = merge_two_string_in_message(message, "ilave", "edebiliyor")
  message = merge_two_string_in_message(message, "ilave", "edermisiniz")
  message = merge_two_string_in_message(message, "ilaveedilebilir", "mi")
  message = merge_two_string_in_message(message, "ilaveedilebiliyor", "mu")
  message = merge_two_string_in_message(message, "ilaveedebilir", "miyim")
  message = merge_two_string_in_message(message, "ilaveedebilir", "miyiz")
  message = merge_two_string_in_message(message, "ilaveedebilir", "misiniz")
  message = merge_two_string_in_message(message, "ilaveedebiliyor", "muyum")
  message = merge_two_string_in_message(message, "ilaveedebiliyor", "musunuz")
  message = merge_two_string_in_message(message, "ilaveedebiliyor", "muyuz")
  message = merge_two_string_in_message(message, "ilaveeder", "misiniz")
  message = merge_two_string_in_message(message, "ilaveeder", "mi")
  
  message = merge_two_string_in_message(message, "monte", "etmek")
  message = merge_two_string_in_message(message, "monte", "edilebilir")
  message = merge_two_string_in_message(message, "monte", "edilebiliyor")
  message = merge_two_string_in_message(message, "monte", "edebilir")
  message = merge_two_string_in_message(message, "monte", "edebiliyor")
  message = merge_two_string_in_message(message, "monte", "eder")
  message = merge_two_string_in_message(message, "monteedilebilir", "mi")
  message = merge_two_string_in_message(message, "monteedilebiliyor", "mu")
  message = merge_two_string_in_message(message, "monteedebilir", "miyim")
  message = merge_two_string_in_message(message, "monteedebilir", "miyiz")
  message = merge_two_string_in_message(message, "monteedebilir", "misiniz")
  message = merge_two_string_in_message(message, "monteedebiliyor", "muyum")
  message = merge_two_string_in_message(message, "monteedebiliyor", "musunuz")
  message = merge_two_string_in_message(message, "monteedebiliyor", "muyuz")
  message = merge_two_string_in_message(message, "monteeder", "misiniz")
  message = merge_two_string_in_message(message, "monteeder", "mi")

  p11 = False
  p12 = False
  p13 = False
 
  for key1_1 in properties_keyword1_1:
    if key1_1 in message:
      p11 = True

  for key1_2 in properties_keyword1_2:
    if key1_2 in message:
      p12 = True

  for key1_3 in properties_keyword1_3:
    if key1_3 in message:
      p13 = True

  if (p11 and p12 and p13) == True:
    return answer

  else:
    return False


def answer_properties_2(message):
  answer = '''Tüm ürünlerimizde 2 yıl garanti desteği sağlanmaktadır'''
  properties_keyword2_1 = ["urun", "ürün", "bilgisayar", "pc","computer", "makine", "cihaz", "bilgesayar", "b.sayar"]
  properties_keyword2_2 = ["garanti", "garantidesteği", "garantihizmeti", "kasko", "koruma", "kaskohizmeti", "garantiçalışması", "korumadesteği", "garanti süresi", "garantilimi"]
  properties_keyword2_3 = ["var mı", "veriyormusunuz", "sunuyormusunuz", "verirmisiniz", "sunarmısınız", 
                           "sağlarmısınız", "sağlıyormusunuz", "sunacakmısınız", "verecekmisiniz", "sağlayacakmısınız", 
                           "olacakmı", "yapılacakmı", "yapacakmısınız", "koyacakmısınız", "olurmu", "koyarmısınız",
                           "koyulacakmı", "yaparmısınız", "yapıyormusunuz", "yaparsınız dimi", "yaparsınız herhalde", 
                           "yapılacakmı", "verir", "yapıl", "yap", "koyar", "koyul", "sağlan", "sunul" , "nekadar",
                           "bilgi al", "bilgial" , "info" , "bilgial" , "kaç ay", "kaç yıl", "garantilimi"]

  message = merge_two_string_in_message(message, "garanti", "desteği")
  message = merge_two_string_in_message(message, "garanti", "hizmeti")
  message = merge_two_string_in_message(message, "garanti", "çalışması")
  message = merge_two_string_in_message(message, "kasko", "desteği")
  message = merge_two_string_in_message(message, "kasko", "hizmeti")
  message = merge_two_string_in_message(message, "koruma", "desteği")
  message = merge_two_string_in_message(message, "ne", "kadar")

  message = merge_two_string_in_message(message, "garantili", "mi")
  message = merge_two_string_in_message(message, "var", "mı")
  message = merge_two_string_in_message(message, "olur", "mu")
  message = merge_two_string_in_message(message, "olacak", "mı")
  
  message = merge_two_string_in_message(message, "verir", "misiniz")
  message = merge_two_string_in_message(message, "verecek", "misiniz")
  message = merge_two_string_in_message(message, "veriyor", "musunuz")
  message = merge_two_string_in_message(message, "verilecek", "mi")
  message = merge_two_string_in_message(message, "verirsiniz", "dimi")
  message = merge_two_string_in_message(message, "verirsiniz", "herhalde")


  message = merge_two_string_in_message(message, "sunuyor", "musunuz")
  message = merge_two_string_in_message(message, "sunar", "mısınız")
  message = merge_two_string_in_message(message, "sunacak", "mısınız")
  message = merge_two_string_in_message(message, "sunulacak", "mı")
  message = merge_two_string_in_message(message, "sunarsınız", "dimi")
  message = merge_two_string_in_message(message, "sunarsınız", "herhalde")

  message = merge_two_string_in_message(message, "sağlıyor", "musunuz")
  message = merge_two_string_in_message(message, "sağlar", "mısınız")
  message = merge_two_string_in_message(message, "sağlayacak", "mısınız")
  message = merge_two_string_in_message(message, "sağlanacak", "mı")
  message = merge_two_string_in_message(message, "sağlarsınız", "dimi")
  message = merge_two_string_in_message(message, "sağlarsınız", "herhalde")

  message = merge_two_string_in_message(message, "yapılacak", "mı")
  message = merge_two_string_in_message(message, "yapar", "mısınız")
  message = merge_two_string_in_message(message, "yapıyor", "musunuz")
  message = merge_two_string_in_message(message, "yapacak", "mısınız")
  message = merge_two_string_in_message(message, "yaparsınız", "dimi")
  message = merge_two_string_in_message(message, "yaparsınız", "herhalde")

  message = merge_two_string_in_message(message, "koyacak", "mısınız")
  message = merge_two_string_in_message(message, "koyar", "mısınız")
  message = merge_two_string_in_message(message, "koyuyor", "musunuz")
  message = merge_two_string_in_message(message, "koyulacak", "mı")
  message = merge_two_string_in_message(message, "koyarsınız", "dimi")
  message = merge_two_string_in_message(message, "koyarsınız", "herhalde")

  p21 = False
  p22 = False
  p23 = False
 
  for key2_1 in properties_keyword2_1:
    if key2_1 in message:
      p21 = True

  for key2_2 in properties_keyword2_2:
    if key2_2 in message:
      p22 = True

  for key2_3 in properties_keyword2_3:
    if key2_3 in message:
      p23 = True

  if (p21 and p22 and p23) == True:
    return answer

  else:
    return False


def answer_properties(message):
  answer1 = answer_properties_1(message)
  if answer1 == False:
    answer2 = answer_properties_2(message)
    if answer2 == False:
      return "Maalesef sorunuzu algılayamadım :( Lütfen daha kolay anlayabilmem için mesajınızı, yazdığınız metnin doğruluğundan emin olarak giriniz!"

    else:
      return answer2

  else:
    return answer1


def print_answer1_data(data):
  if data == "product_in_not_stocks":
    text = "Maalesef stoklarımızda aradığınız kriterlere uygun bir ürün bulunmamaktadır.\nLütfen daha kolay anlayabilmem için mesajınızı, yazdığınız metnin doğruluğundan emin olarak giriniz :)"
    #print("CarettaBot: Maalesef stoklarımızda aradığınız kriterlere uygun bir ürün bulunmamaktadır.\nLütfen daha kolay anlayabilmem için mesajınızı, yazdığınız metnin doğruluğundan emin olarak giriniz :)")
    return text 
  
  else:
    #text_data = "CarettaBot: Sizin için aradığınız kriterlere uygun bilgisayar özellik ve fiyat listesini çıkarttım, buyurun:\n Marka: {0}\n Model: {1}\n Ram:   {2}\n Ekran Kartı: {3}\n İşletim Sistemi: {4}\n İşlemci: {5}\n SSD: {6}\n Nakit Fiyat: {7}\n *******************************************".format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
    print("Sizin için aradığınız kriterlere uygun bilgisayar özellik ve fiyat listesini çıkarttım, buyurun:\n")  
    for i in data:
      print(" Marka: {0}\n Model: {1}\n Ram:   {2} GB\n Ekran Kartı: {3}\n İşletim Sistemi: {4}\n İşlemci: {5}\n SSD: {6} GB\n Nakit Fiyat: {7} Türk Lirası\n\n *******************************************\n".format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))

def convert_to_lowercase(sentence):
  sentence = re.sub('I', 'i', str(sentence))
  sentence = sentence.lower()
  return sentence

def autocorrect_turkish(sentence):
  list_words = objTurkishNLP.list_words(sentence)
  corrected_words = objTurkishNLP.auto_correct(list_words)
  corrected_sentence = " ".join(corrected_words)
  return corrected_sentence
