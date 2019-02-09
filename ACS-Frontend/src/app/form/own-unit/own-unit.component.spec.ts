import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OwnUnitComponent } from './own-unit.component';

describe('OwnUnitComponent', () => {
  let component: OwnUnitComponent;
  let fixture: ComponentFixture<OwnUnitComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OwnUnitComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OwnUnitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
