import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';

import { OwnUnitComponent } from './own-unit.component';

describe('OwnUnitComponent', () => {
  let component: OwnUnitComponent;
  let fixture: ComponentFixture<OwnUnitComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [ OwnUnitComponent ]
    });
    TestBed.overrideTemplate(OwnUnitComponent, '');
    TestBed.compileComponents();
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
