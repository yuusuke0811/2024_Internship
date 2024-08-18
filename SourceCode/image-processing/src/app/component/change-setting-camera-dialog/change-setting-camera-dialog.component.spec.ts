import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChangeSettingCameraDialogComponent } from './change-setting-camera-dialog.component';

describe('ChangeSettingCameraDialogComponent', () => {
  let component: ChangeSettingCameraDialogComponent;
  let fixture: ComponentFixture<ChangeSettingCameraDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChangeSettingCameraDialogComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChangeSettingCameraDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
