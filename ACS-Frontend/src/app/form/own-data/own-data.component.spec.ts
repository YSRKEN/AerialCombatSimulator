import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OwnDataComponent } from './own-data.component';

describe('OwnDataComponent', () => {
  let component: OwnDataComponent;
  let fixture: ComponentFixture<OwnDataComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OwnDataComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OwnDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
