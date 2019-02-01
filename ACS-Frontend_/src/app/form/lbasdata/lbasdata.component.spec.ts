import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LBASDataComponent } from './lbasdata.component';

describe('LBASDataComponent', () => {
  let component: LBASDataComponent;
  let fixture: ComponentFixture<LBASDataComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LBASDataComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LBASDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
