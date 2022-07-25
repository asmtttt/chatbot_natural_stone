import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {

  algorithms = [
    { value: 1, name: "Logistic Regression", accuracy: 94 },
    { value: 2, name: "Support Vector Machine", accuracy: 92 },
    { value: 3, name: "Naive Bayes", accuracy: 95 },
    { value: 4, name: "Random Forest", accuracy: 92 },
    { value: 5, name: "Decision Tree", accuracy: 89 },
    { value: 6, name: "Multi-Layer Perceptron", accuracy: 95 }
  ];
  predictionForm = this.formBuilder.group({
    algorithm: 1,
    textForPrediction: ''
  });
  predictionResult: string;
  predictionResultIsString: boolean;
  algorithmAccuracy: number;
  selectedValue: number;

  constructor(private formBuilder: FormBuilder, private apiService: ApiService) { }

  ngOnInit() {
    this.getAlgorithm();
  }

  getAlgorithm() {
    this.selectedValue = this.predictionForm.get("algorithm").value;
    this.algorithmAccuracy = this.algorithms[this.selectedValue - 1].accuracy;

    this.apiService.getData(`/algorithm/${this.selectedValue}`).subscribe({
      next: data => {

      },
      error: error => {

      }
    });
  }

  changeAlgorithm() {
    for (let item of this.algorithms) {
      if (this.selectedValue == item.value) {
        this.algorithmAccuracy = item.accuracy
      }
    }

    this.getAlgorithm();
  }

  predictionFormOnSubmit() {
    let review = {
      review: this.predictionForm.get("textForPrediction").value.trim()
    }

    this.apiService.postData("/prediction", review).subscribe({
      next: data => {
        this.predictionResult = data.answer;
        if (typeof this.predictionResult == "string")
          this.predictionResultIsString = true
        else
          this.predictionResultIsString = false
      },
      error: error => {
        
      }
    });
  }

}
