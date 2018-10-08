import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EnemyDataComponent } from './enemy-data.component';

describe('EnemyDataComponent', () => {
  let component: EnemyDataComponent;
  let fixture: ComponentFixture<EnemyDataComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EnemyDataComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EnemyDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
