import { Component, OnInit, ElementRef, AfterViewInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
    title = 'app XX';


    private imageId: string ='2';
    private imageSrc: string;

    private imageTypes: string[] = ['start', 'mid', 'finish', 'none'];
    private imageTypeValue: string;
    private componentsType: string[] = ['text input', 'checkbox', 'radio', 'next button', 'scrolling', 'show more', 'back button', 'check text', 'select', 'select-list'];
    private colors: string[] = ['black', 'blue', 'brown', 'red', 'green', 'MediumSeaGreen'];
    private currentComponent: string;
    private rLeft: number;
    private rTop: number;
    private imageLoaded: boolean = false;

    @ViewChild('paintbox') 
    public canvas: ElementRef;
    private cx: CanvasRenderingContext2D;  
  
  
    private left() {
        console.log('<<<<');
        this.imageId = (parseInt(this.imageId)-1).toString();
        this.retriveClass(this.imageId);
    }
    private right() {
        console.log('>>>>');
        this.imageId = (parseInt(this.imageId)+1).toString();
        this.retriveClass(this.imageId);
    }
    private goto() {
        console.log(`go ${this.imageId}`);
        this.retriveClass(this.imageId);
    }

    constructor(private http: HttpClient) { }
    ngOnInit() {
        this.http.get('/api/screen-number')
            .subscribe(data => {
                this.imageId = data.toString();
                this.retriveClass(this.imageId);
                }
            );
    }

    private setClass(type: string) {
        this.http.post(`/api/image/${this.imageId}/class?class=${type}`, {})
            .subscribe(data => console.log(data));
    }

    private retriveClass(id) {
        this.imageLoaded = false;
        this.cx.clearRect(0,0,1024,768);
        this.http.get(`/api/image/${id}/info`)
            .subscribe(data => {
                console.log(data);
                this.imageTypeValue = data['class']||'none';
                console.log('class is', this.imageTypeValue);
                if(data['input']){
                    this.paintImgs(JSON.parse(data['input']));
                    this.imageLoaded = true;
                    console.log('loaded')
                }
            })
    }

    private paintImgs(li: any[]) {
        if(!li) {
            return;
        }
        for (let l of li) {
                this.cx.fillStyle = this.getColor(l.component);
                if (l.l && l.t && l.w && l.h) {
                    this.cx.fillRect(l.l, l.t, l.w, l.h);
                    
                }else if (l.x && l.y && l.w && l.h) {
                    this.cx.fillRect(+l.x+ l.w/2- +l.w, +l.y+ l.h/2- +l.h, l.w, l.h);
                }

                if(l.x && l.y) {
                    this.cx.fillStyle = 'black';
                    this.cx.fillRect(l.x-3, l.y-3, 7,7);
                    // this.cx.arc(l.x, l.y, 3, 0, 3*Math.PI);
                    // this.cx.strokeStyle='black';
                    // this.cx.stroke();
                }
        }

    }
    // get latestNumber(): string {
    //     return this.http.get('/api/screen-number');
    // }

    private dummy(x: any) {

    }

    private getColor(component: string): string {
        // return 'red';
        return this.colors[this.componentsType.indexOf(component)];
    }

    private eventHandlerClick(s: MouseEvent) {


    }

    private mouseDownHandler(s: MouseEvent) {
        // console.log(`+++ Click ${s.offsetX} ${s.offsetY} ${this.currentComponent}`);
        this.rLeft = s.offsetX;
        this.rTop = s.offsetY;
    }
    private mouseUpHandler(s: MouseEvent) {
        // console.log(`+++ Click ${s.offsetX} ${s.offsetY} ${this.currentComponent}`);
        // if(!this.currentComponent) {
        //     return;
        // }

        let l=Math.min(this.rLeft, s.offsetX);
        let t=Math.min(this.rTop, s.offsetY);
        let w=Math.abs(s.offsetX-this.rLeft);
        let h=Math.abs(s.offsetY-this.rTop);

        var params;

        if (['checkbox', 'radio'].includes(this.currentComponent)) {
            var dim = Math.max(w,h)
            params = {x: this.rLeft, y: this.rTop, w: 2*dim+1, h: 2*dim+1, component: this.currentComponent};
        }
        else {
            if (w>5 || h>5){
                params = {l: l, t: t, w: w+1, h: h+1, component: this.currentComponent};
                
            }
            else
            {
                params = {x: this.rLeft, y: this.rTop};
            }
            
        }

        this.http.post(`/api/image/${this.imageId}/input`, params)
            .subscribe(data => {
                this.cx.fillStyle = this.getColor(this.currentComponent);
                this.cx.fillRect(l, t, w, h);
            });
    }



    private eraseLast() {
        this.http.delete(`/api/image/${this.imageId}/input`)
            .subscribe(data => {
                console.log("deleted");
            });

    }
    public ngAfterViewInit() {
        // get the context
        const canvasEl: HTMLCanvasElement = this.canvas.nativeElement;
        this.cx = canvasEl.getContext('2d');
        // this.cx.fillStyle = 'rgb(200,0,0)';
    }
}
