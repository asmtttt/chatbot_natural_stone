import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {

  predictionForm = this.formBuilder.group({
    textForPrediction: ''
  });
  predictionResult: string;
  predictionResultIsString: boolean;
  

  constructor(private formBuilder: FormBuilder, private apiService: ApiService) { }

  ngOnInit() {
  }


  predictionFormOnSubmit() {
    let review = {
      review: this.predictionForm.get("textForPrediction").value.trim()
    }

    this.apiService.postData("/answer", review).subscribe({
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
