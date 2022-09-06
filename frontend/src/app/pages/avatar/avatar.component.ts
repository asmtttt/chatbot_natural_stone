import { Component, OnInit } from '@angular/core';
import { VoiceRecognitionService } from 'src/app/services/voice-recognition.service';
import { compileClassMetadata } from '@angular/compiler';
import { ApiService } from 'src/app/services/api.service';
import { SelectMultipleControlValueAccessor } from '@angular/forms';

declare var webkitSpeechRecognition: any;
declare var SDK: any;
declare var SDKConnection: any;
declare var WebAvatar: any;

@Component({
  selector: 'app-avatar',
  templateUrl: './avatar.component.html',
  styleUrls: ['./avatar.component.scss'],
})

export class AvatarComponent implements OnInit {
  recognition = new webkitSpeechRecognition();
  isListening = false;
  public text = '';
  public tempWords: any;
  public transcript_arr = [];
  public confidence_arr = [];
  public languages = ["Türkçe", "İngilizce", "İspanyolca", "Fransızca"];
  public languagesCode = ["tr", "en-US", "es-ES", "fr-FR"];

  is_open_microphone: boolean = false;

  req = {
    language: "Türkçe",
    languageCode: "tr"
  }

  predictionResult: string;
  predictionResultIsString: boolean;

  avatarSDK: any;
  webAvatar: any;

  constructor(private apiService: ApiService) {
    
  }

  ngOnInit() {
    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = this.req.languageCode;
    console.log("mylang: ", this.recognition.lang);

    this.recognition.addEventListener('result', (e: any) => {
      let last = e.results.length - 1;
      let temp_trans = e.results[last][0].transcript;
      let confidence = e.results[last][0].confidence;
      this.confidence_arr.push(confidence);
      this.transcript_arr.push(temp_trans);
      const transcript = Array.from(e.results)
        .map((result: any) => result[0])
        .map((result) => result.transcript)
        .join('');
      this.tempWords = transcript;
    });

    this.initAvatarSDK();
  }

  initAvatarSDK() {
    SDK.applicationId = "6105974131766205942";
    SDK.body = function () {
      var body = document.getElementById("img-div");
      return body;
    };

    this.avatarSDK = new SDKConnection();
    this.webAvatar = new WebAvatar();
    
    this.webAvatar.version = 8.5;
    this.webAvatar.connection = this.avatarSDK;
    this.webAvatar.avatar = "13974700";
    this.webAvatar.voice = "dfki-ot";
    this.webAvatar.voiceMod = "default";
    this.webAvatar.width = "350";

    this.webAvatar.createBox();
    this.textToSpeechAvatar("selam nasılsın hoş geldin");
  }

  textToSpeechAvatar(text: string) {
    console.log("textToSpeechAvatar");
    this.webAvatar.addMessage(text, "", "", "");
    this.webAvatar.processMessages();
  }

  getTranscriptValue() {
    return this.transcript_arr;
  }

  getConfidenceValue() {
    return this.confidence_arr;
  }

  speechToTextAnswer() {
    let review = {
      review: this.text
    }

    this.apiService.postData("/answer", review).subscribe({
      next: data => {
        this.predictionResult = data.answer;
        if (typeof this.predictionResult == "string")
          this.predictionResultIsString = true
        else
          this.predictionResultIsString = false

        console.log("apiservis içindeki answer: ", this.predictionResult);
        this.textToSpeechAvatar(this.predictionResult);
      },
      error: error => {

      }
    });
  }

  start() {
    if (this.isListening == false) {
      this.isListening = true;
      this.recognition.start();
    }

    this.recognition.addEventListener('end', (condition: any) => {
      if (!this.isListening) {
        this.recognition.stop();
      } else {
        this.wordConcat();
        this.recognition.start();
      }
    });
  }

  stop() {
    this.isListening = false;
    this.wordConcat();
    this.recognition.stop();
    this.recognition.stop();
  }

  reinit() {
    this.transcript_arr = [];
    this.confidence_arr = [];
    this.tempWords = '';
    this.text = '';
  }

  wordConcat() {
    console.log("oncesi text: ", this.text);
    this.text = this.tempWords + '.';
    console.log("sonrası text: ", this.text);
    this.tempWords = '';
  }

  startService() {
    this.start();
    this.is_open_microphone = true;
    console.log("mylang: ", this.recognition.lang);
  }

  stopService() {
    this.is_open_microphone = false;
    setTimeout(() => 
      {
        this.stop();
        this.speechToTextAnswer();},
      2000);
  }

  onLanguageChange(ev) {
    var index = this.languages.indexOf(this.req.language);
    this.req.languageCode = this.languagesCode[index];
    console.log("dil: ", this.req.language);
    console.log("dil kodu: ", this.req.languageCode);
    this.recognition.lang = this.req.languageCode;
    console.log("reclang: ", this.req.languageCode);

  }

}

