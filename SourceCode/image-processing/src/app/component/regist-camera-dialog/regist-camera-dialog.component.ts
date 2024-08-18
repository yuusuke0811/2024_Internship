import { Component, Inject, ViewChild, AfterViewInit } from '@angular/core';
import { Subject } from "rxjs";
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef, MatDialogContent, MatDialogActions, MatDialogTitle, MatDialogClose, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatPaginator } from '@angular/material/paginator';
import { UnregisteredCameraInfoInterface } from '../../interface/unregistered-camera-info.interface';

@Component({
  selector: 'app-regist-camera-dialog',
  standalone: true,
  imports: [
    MatButtonModule,
    MatTableModule,
    MatPaginator,
    MatDialogTitle, MatDialogContent, MatDialogActions, MatDialogClose,
    MatInputModule,
  ],
  templateUrl: './regist-camera-dialog.component.html',
  styleUrl: './regist-camera-dialog.component.scss'
})
export class RegistCameraDialogComponent implements AfterViewInit  {
  private subject$: Subject<string> = new Subject<string>();

  protected displayedColumns: string[] = ['hostname', 'ipAddress'];
  protected clickRowData:UnregisteredCameraInfoInterface | undefined = undefined;

  public dataSource = new MatTableDataSource<UnregisteredCameraInfoInterface>([]);

  @ViewChild('paginator') paginator!: MatPaginator;
  
  constructor (private dialogRef: MatDialogRef<RegistCameraDialogComponent>, @Inject(MAT_DIALOG_DATA) private data: any) {
    // 未登録カメラ一覧情報要求
    let dataSource = [
      { 'hostname': 'aaa', 'ipAddress': '192.168.130.1'},
      { 'hostname': 'bbb', 'ipAddress': '192.168.130.2'},
      { 'hostname': 'ccc', 'ipAddress': '192.168.130.3'},
      { 'hostname': 'ddd', 'ipAddress': '192.168.130.4'},
      { 'hostname': 'eee', 'ipAddress': '192.168.130.5'},
      { 'hostname': 'fff', 'ipAddress': '192.168.130.6'}
    ];

    this.subject$ = this.data.subject;
    this.dataSource = new MatTableDataSource(dataSource); 
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
  }

  /**
   * 行クリックイベント
   * @param row 行データ
   */
  onClickRow(row: any): void {
    // 同じ行をクリックしたら解除
    this.clickRowData = this.clickRowData == row ? undefined : row;
  }

  /**
   * 登録ボタンイベント
   */
  onRegist(): void {
    // カメラ登要求
    this.subject$.next(JSON.stringify({
      'transmissionType': 16,
    }))

    this.dialogRef.close();
  }

  /**
   * 閉じるボタンイベント
   */
  onClose(): void {
    this.dialogRef.close();
  }
}
