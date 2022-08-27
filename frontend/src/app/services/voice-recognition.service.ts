import { compileClassMetadata } from '@angular/compiler';
import { Injectable } from '@angular/core';
import { AvatarComponent } from '../pages/avatar/avatar.component';
declare var webkitSpeechRecognition: any;

@Injectable({
  providedIn: 'root'
})
export class VoiceRecognitionService {

  recognition = new webkitSpeechRecognition();
  isListening = false;
  public text = '';
  public tempWords: any;
  public transcript_arr = [];
  public confidence_arr = [];
  public languages = ["Türkçe", "İngilizce", "İspanyolca", "Fransızca"];
  public languagesCode = ["tr", "en-US", "es-ES", "fr-FR"];

  constructor() {}

  getTranscriptValue() {
    return this.transcript_arr;
  }
  getConfidenceValue() {
    return this.confidence_arr;
  }
  init() {
    //console.log("mylang: ", this.comp.req.languageCode);

    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = "tr";
    console.log("mylang: ", this.recognition.lang)

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
}

