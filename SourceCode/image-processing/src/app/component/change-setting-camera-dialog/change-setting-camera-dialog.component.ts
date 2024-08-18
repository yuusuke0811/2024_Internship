import { Component, Inject } from '@angular/core';
import { Subject } from "rxjs";
import { FormsModule, } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef, MatDialogContent, MatDialogActions, MatDialogTitle, MatDialogClose, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@Component({
  selector: 'app-change-setting-camera-dialog',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatDialogContent, MatDialogActions, MatDialogTitle, MatDialogClose,
    MatFormFieldModule,
    MatInputModule,
    MatSlideToggleModule,
  ],
  templateUrl: './change-setting-camera-dialog.component.html',
  styleUrl: './change-setting-camera-dialog.component.scss'
})
export class ChangeSettingCameraDialogComponent {
  private subject$: Subject<string> = new Subject<string>();
  
  public name: string = '';
  public isMasking: boolean = false;

  constructor(private dialogRef: MatDialogRef<ChangeSettingCameraDialogComponent>, @Inject(MAT_DIALOG_DATA) private data: any) {
    this.subject$ = this.data.subject
    this.name = this.data.name;
    this.isMasking = this.data.isMasking;
  }

/**
 * 変更ボタンイベント
 */
onConfirm(): void {
  console.log(this.name)
  console.log(this.isMasking);
}

/**
 * 閉じるボタンイベント
 */
  onClose(): void{
    this.dialogRef.close();
  }
}
