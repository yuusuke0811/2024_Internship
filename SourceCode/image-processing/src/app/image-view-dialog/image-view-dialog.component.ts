import { Component, Inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose } from '@angular/material/dialog';
import { WebsocketService } from '../service/websocket.service';


@Component({
  selector: 'app-image-view-dialog',
  standalone: true,
  imports: [
    MatButtonModule,
    MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose,
  ],
  templateUrl: './image-view-dialog.component.html',
  styleUrl: './image-view-dialog.component.scss'
})

export class ImageViewDialogComponent {
  protected imageData: string ="";
  
  private canvas: HTMLCanvasElement;
  private context: any;

  constructor (private dialogRef: MatDialogRef<ImageViewDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
    this.canvas = document.getElementById("canvas") as HTMLCanvasElement;
    this.context = this.canvas.getContext('2d');

    this.canvas.width = 320;
    this.canvas.height = 240;
    
    this.timerCallback();

  }

  timerCallback(): void{
    setTimeout(() => {
      this.timerCallback();
    }, 0);
  }

  onClose(): void{
    this.dialogRef.close();
  }
}
