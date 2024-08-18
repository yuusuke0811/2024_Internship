import { Component, Inject } from '@angular/core';
import { Subject } from "rxjs";
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef, MatDialogContent, MatDialogActions, MatDialogTitle, MatDialogClose, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-unsubscribe-camera-dialog',
  standalone: true,
  imports: [
    MatButtonModule,
    MatDialogContent, MatDialogActions, MatDialogTitle, MatDialogClose,
  ],
  templateUrl: './unsubscribe-camera-dialog.component.html',
  styleUrl: './unsubscribe-camera-dialog.component.scss'
})
export class UnsubscribeCameraDialogComponent {
  private subject$: Subject<string> = new Subject<string>();

  constructor(private dialogRef: MatDialogRef<UnsubscribeCameraDialogComponent>, @Inject(MAT_DIALOG_DATA) private data: any) {}

/**
 * 解除ボタンイベント
 */
onConfirm(): void {

}

/**
 * 閉じるボタンイベント
 */
  onClose(): void{
    this.dialogRef.close();
  }
}
