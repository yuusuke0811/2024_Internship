import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Subject,BehaviorSubject, Observable } from "rxjs";
import { WebsocketService } from "./service/websocket.service";
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'
import { MatRadioModule } from '@angular/material/radio';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { CdkListbox, CdkOption } from '@angular/cdk/listbox';
import {DataSource} from '@angular/cdk/collections';
import {CdkTableModule} from '@angular/cdk/table';
import {MatDialog} from '@angular/material/dialog'
import {ImageViewDialogComponent} from './image-view-dialog/image-view-dialog.component'

var a = "◎";
var b = "〇";
var c = "△";

const ELEMENT_DATA: any[] = [
  {position: 1, name: 'クラスルーム１', weight: a},
  {position: 2, name: 'クラスルーム２', weight: b},
  {position: 3, name: 'クラスルーム３', weight: c},
]

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    FormsModule,
    ReactiveFormsModule,
    CommonModule,
    MatRadioModule, 
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    CdkListbox, 
    CdkOption,
    CdkTableModule,
    ImageViewDialogComponent,
    ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})

export class AppComponent implements OnInit {
  private readonly CONECT = 0x00;
  private readonly STREAMING = 0x01;
  private readonly VERIFICATION = 0x02;
  private readonly CAMERA_INFO = 0x10;
  private readonly CHANGE_MODEL = 0x11;
  private readonly CHANGE_CAMERA = 0x12;

  private readonly VIEWER = 0x01;

  private readonly DETECTION = 0x00;
  private readonly SEGMENTATION = 0x01;
  private readonly POSE = 0x02;
  private readonly OBB = 0x03;
  private readonly CLASS = 0x04;
  private readonly MOTION = 0xFF;
  protected readonly models: {[key: string] : string} = { 
    [this.DETECTION]: '物体検出',
    [this.SEGMENTATION]: 'セグメンテーション',
    [this.POSE]: '姿勢推定',
    //[this.OBB]: '指向性検出',
    [this.CLASS]: '画像分類',
    //[this.MOTION]: '動体検知'
  };
  
  protected selectedModel: string = this.DETECTION.toString();
  
  private receiveData: string = '';
  private imageData: string = '';

  private canvas: any;
  private context: any;
  private subject$: Subject<string> = new Subject<string>();

  protected host: string = '';
  protected port: string = '';
  protected buttonName: string = '';
  protected isConnect: boolean = false;
  protected isComplete: boolean = false;
  protected cameraList: any[] = [];
  protected selectCamera: string | undefined= undefined;

  protected displayedColumns: string[] = ['position', 'name', 'weight'];
  protected dataSource :any = new BehaviorSubject<any[]>(ELEMENT_DATA);cameraID: any;
;


  constructor(private websocketService: WebsocketService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.host = '192.168.130.17';
    this.port = '54321'
    this.buttonName = 'Websocket接続開始';
    this.isConnect = false;
    this.isComplete = false;
    
    this.websocketOperaion()

    document.addEventListener('DOMContentLoaded', () => {
      this.doLoad();
    });
  }

  doLoad(): void {
    this.canvas = document.getElementById("canvas") as HTMLCanvasElement;
    this.context = this.canvas.getContext('2d');

    this.canvas.width = 320;
    this.canvas.height = 240;
    
    this.timerCallback()
  }
  
  timerCallback(): void {
    let jsonData = {
      'transmissionType': this.CAMERA_INFO,
    }

    this.subject$.next(JSON.stringify(jsonData))

    setTimeout(() => {
      this.timerCallback();
    }, 3000);
  }

  websocketOperaion(): void {
    // Websocket未接続の場合
    if (!this.isConnect) {
      this.subject$ = this.websocketService.connect(this.host, this.port);
      
      this.subject$.subscribe(
        msg => {
          let jsonData = JSON.parse(msg)
          console.log(jsonData)

          // 伝送種別が「接続」の場合
          if (jsonData['transmissionType'] == this.CONECT) {
            jsonData['message'] = '';
            jsonData['clientType'] = this.VIEWER;
            jsonData['selectCameraId'] = -1;
            jsonData['modelType'] = this.SEGMENTATION;

            this.subject$.next(JSON.stringify(jsonData))

            this.buttonName = 'Websocket接続停止';
            this.isConnect = true;

          // 伝送種別が「ストリーミング」の場合
          } else if (jsonData['transmissionType'] == this.STREAMING) {
            this.receiveData += jsonData['data'];
            
            if (jsonData['endPoint']) {
                this.imageData = this.receiveData;
                this.receiveData = '';

                let img = new Image();
                let ctx = this.context;
                
                img.onload = ()=> {
                  ctx.drawImage(img, 0, 0)
                }
                img.src = 'data:image/png;base64,' + this.imageData;
                this.websocketService.ImageData = img.src
                console.log( this.imageData)
            }

          // 伝送種別が「カメラ情報」の場合
          } else if (jsonData['transmissionType'] == this.CAMERA_INFO) {
            this.cameraList = [];

            for (let index in jsonData['data']) {
              let weight = jsonData['data'][index]['count'] / jsonData['data'][index]['capacity']
              
              this.cameraList.push({
                id: jsonData['data'][index]['id'].toString(),
                name: 'aaaa',///jsonData['data'][index]['name'].toString(),
                capacity: jsonData['data'][index]['capacity'],
                count: jsonData['data'][index]['count'],
                weight: weight
              })
            }
          }
        },
        err => {
          console.log(err)
          
          if (this.isComplete) {
            console.log('接続を終了しました。')
          } else {
            console.log('サーバとの接続が切れました。')
          }

          this.isConnect = false;
          this.isComplete = false;
          this.buttonName = 'Websocket接続開始'
        }
      );
    } else {
      this.isComplete = true;
      this.cameraList = [];
      this.selectCamera = undefined;
      this.subject$.complete();
    }
  }

  cheangeSelectModel(): void {
    let jsonData = {
      transmissionType: this.CHANGE_MODEL,
      modelType: Number(this.selectedModel),
    }

    this.subject$.next(JSON.stringify(jsonData))
  }

  cheangeSelectCamera(): void {
    let jsonData = {
      transmissionType: this.CHANGE_CAMERA,
      selectCameraId: Number(this.cameraList[0].id)
    }

    this.subject$.next(JSON.stringify(jsonData))
  }

  openDialog(id: number , name: string): void {
    const dialogRef = this.dialog.open(ImageViewDialogComponent, {
      data: {
        service: this.websocketService,
        name: name
      }
    })

    console.log(id)
    let jsonData = {
      transmissionType: this.CHANGE_CAMERA,
      selectCameraId: id
    }

    this.subject$.next(JSON.stringify(jsonData))

    dialogRef.afterClosed().subscribe(result =>{
      console.log('cloce dialog')
    })
  }
}


export class ExampleDataSource extends DataSource<any> {
  /** Stream of data that is provided to the table. */
  data = new BehaviorSubject<any[]>(ELEMENT_DATA);

  /** Connect function called by the table to retrieve one stream containing the data to render. */
  connect(): Observable<any[]> {
    return this.data;
  }

  disconnect() {}
}
