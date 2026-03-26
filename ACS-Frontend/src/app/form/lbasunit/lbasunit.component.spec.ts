import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';

import { LBASUnitComponent } from './lbasunit.component';

describe('LBASUnitComponent', () => {
  let component: LBASUnitComponent;
  let fixture: ComponentFixture<LBASUnitComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [ LBASUnitComponent ]
    });
    TestBed.overrideTemplate(LBASUnitComponent, '');
    TestBed.compileComponents();
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
