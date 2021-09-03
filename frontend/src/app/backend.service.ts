import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BackendService {
  private API = 'http://127.0.0.1:5000/'
  constructor(private httpClient: HttpClient) { }

  public getPrediction(index:any, period:any){
    return this.httpClient.get(this.API+'/Predict/'+index+'/'+period);
  }

  public getGraph(index:any, period:any, prediction:any){
    return this.httpClient.get(this.API+'/Project/'+index+'/'+period+'/'+prediction);
  }
  public getOptions(index:any, period:any){
    return this.httpClient.get(this.API+'/Options/'+index+'/'+period);
  }
}
