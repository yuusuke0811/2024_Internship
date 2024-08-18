import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageViewDialogComponent } from './image-view-dialog.component';

describe('ImageViewDialogComponent', () => {
  let component: ImageViewDialogComponent;
  let fixture: ComponentFixture<ImageViewDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImageViewDialogComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ImageViewDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
