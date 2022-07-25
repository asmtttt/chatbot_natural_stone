import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  // Http Options
  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  }

  constructor(private http: HttpClient) { }

  getData(url) {
    return this.http.get<any>(`${environment.apiUrl}${url}`, this.httpOptions);
  }

  postData(url, body) {
    return this.http.post<any>(`${environment.apiUrl}${url}`, body, this.httpOptions);
  }

}
