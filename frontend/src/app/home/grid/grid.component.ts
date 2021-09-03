import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { BackendService } from '../../backend.service';
import { SimpleChanges } from '@angular/core';
import { NONE_TYPE } from '@angular/compiler';

export interface Chain{
  strike: number,
  lastPrice: number,
  impliedVolatility: number,
  inTheMoney: String
}

@Component({
  selector: 'app-grid',
  templateUrl: './grid.component.html',
  styleUrls: ['./grid.component.sass']
})
export class GridComponent implements OnInit {
  @Input() prediction: any;
  @Input() index:any;
  @Input() period:any;

  graph_data:any;
  graph_prices:any;
  graph_dates:any;
  graph_min:any;
  graph_max:any;
  puts:Chain[];
  calls:Chain[];
  options_date:any;
  table_cols:any;

  constructor(private apiService: BackendService) { }

  ngOnInit(): void {
  }
  ngOnChanges(changes: SimpleChanges) {
    for (const propName in changes) {
      if (changes.hasOwnProperty(propName)) {
        switch (propName) {
          case 'prediction': {
            this.apiService.getGraph(this.index,this.period, this.prediction).subscribe((data: any)=>{
              console.log(data);
              this.graph_prices = data['data'];
              this.graph_dates= data['dates'];
              this.graph_min = data['minimum'];
              this.graph_max = data['maximum'];
              this.construct_graph();
            });
            this.apiService.getOptions(this.index,this.period).subscribe((data: any)=>{
              if(data['resp']=="True"){
                this.puts = JSON.parse(data['puts']);
                this.calls = JSON.parse(data['calls']);
                console.log(this.calls);
                this.options_date=data['date'];
                this.table_cols= data['columns'];
                console.log(this.table_cols);

                console.log(this.calls[0].strike)

                
              }

            });
          }
        }
      }
    }
  }


  construct_graph(){
    this.graph_data=[
      { x: this.graph_dates, y: this.graph_prices, type: 'scatter', mode: 'lines+points', marker: {color: 'black'}},
      { x: this.graph_dates, y: this.graph_prices.concat(this.graph_min), type: 'scatter', mode: 'points', marker: {color: 'black'}},
      { x: this.graph_dates, y: this.graph_prices.concat(this.graph_max), type: 'scatter', mode: 'points', marker: {color: 'black'}}
    ]
  }
}
