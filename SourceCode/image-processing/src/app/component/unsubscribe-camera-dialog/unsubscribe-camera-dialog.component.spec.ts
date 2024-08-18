import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UnsubscribeCameraDialogComponent } from './unsubscribe-camera-dialog.component';

describe('UnsubscribeCameraDialogComponent', () => {
  let component: UnsubscribeCameraDialogComponent;
  let fixture: ComponentFixture<UnsubscribeCameraDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UnsubscribeCameraDialogComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(UnsubscribeCameraDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
