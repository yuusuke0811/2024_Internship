import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RegistCameraDialogComponent } from './regist-camera-dialog.component';

describe('RegistCameraDialogComponent', () => {
  let component: RegistCameraDialogComponent;
  let fixture: ComponentFixture<RegistCameraDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegistCameraDialogComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(RegistCameraDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
