import { Component, OnInit } from '@angular/core';
import { FormControl } from "@angular/forms";
import { FormGroup } from "@angular/forms";
import { FormBuilder } from "@angular/forms";
import { Validators } from "@angular/forms";
interface Index{
  value: string;
  viewValue: string;
}
@Component({
  selector: 'app-stepper',
  templateUrl: './stepper.component.html',
  styleUrls: ['./stepper.component.sass']
})
export class StepperComponent implements OnInit {
  firstFormGroup: FormGroup;
  secondFormGroup: FormGroup;
  isEditable = false;
  indices: Index[] = [ 
    {value: "DJIA", viewValue:"Dow Jones"},
    {value: "SPX", viewValue:"S&P 500"},
    {value: "IXIC", viewValue:"Nasdaq"},
    {value: "XAX", viewValue:"NYSE"},
    {value: "UKX", viewValue:"FTSE 100"},
    {value: "DAX", viewValue:"DAX"},
    {value: "NIK2", viewValue:"Nikkei 225"},
    {value: "LFG9", viewValue:"Russel 2000"},
    {value: "ESTX", viewValue:"EuroStoxx 50"}
  ];
  constructor(private _formBuilder: FormBuilder) {}

  ngOnInit() {
    this.firstFormGroup = this._formBuilder.group({
      firstCtrl: ['', Validators.required]
    });
    this.secondFormGroup = this._formBuilder.group({
      secondCtrl: ['', Validators.required]
    });
  }
}
