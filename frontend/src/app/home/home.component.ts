import { Component, OnInit } from '@angular/core';
import { StepperComponent } from './stepper/stepper.component';
import {GridComponent} from './grid/grid.component'
import { BackendService } from '../backend.service';
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass'],

})
export class HomeComponent implements OnInit {
  showInput: boolean = true;
  showPredictions: boolean = false;
  index: any;
  period: any;
  prediction: any;


  constructor(private apiService: BackendService) { }

  ngOnInit(): void {
  }
  displayPredictions(inputs: any) : void{
    this.showPredictions = true;
    this.showInput = false;
    this.index = inputs[0];
    this.period = inputs[1];
    this.apiService.getPrediction(this.index,this.period).subscribe((data: any)=>{
      console.log(data);
      this.prediction = data;
    });  
  }
}
