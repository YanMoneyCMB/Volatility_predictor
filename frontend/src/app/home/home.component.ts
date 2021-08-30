import { Component, OnInit } from '@angular/core';
import { StepperComponent } from './stepper/stepper.component';
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass'],

})
export class HomeComponent implements OnInit {
  showInput: boolean = true;
  showPredictions: boolean = false;

  constructor() { }

  ngOnInit(): void {
  }
  displayPredictions(inputs: any) : void{
    this.showPredictions = true;
    this.showInput = false;
    
  }
}
