import {Component, HostListener, OnInit} from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'app';

  events: Event[] = [];

  ngOnInit(): void {
    console.log('>', new Date().getMilliseconds());
  }

  submit() {
  	console.log(`collected`, this.events.length);
  	if(this.events.length>0) {
  	  console.log(`took ${Math.round(this.events[this.events.length-1].timeStamp - this.events[0].timeStamp)/1000}`);
    }
  	this.events = [];
  }

  @HostListener('document:keypress', ['$event'])
  @HostListener('document:mousemove', ['$event'])
  @HostListener('document:mouseup', ['$event'])
  @HostListener('document:mousedown', ['$event'])
  handleEvents(event: Event) {
    this.events.push(event);
  }
}
