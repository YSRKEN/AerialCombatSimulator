import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LBASUnitComponent } from './lbasunit.component';

describe('LBASUnitComponent', () => {
  let component: LBASUnitComponent;
  let fixture: ComponentFixture<LBASUnitComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LBASUnitComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LBASUnitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
