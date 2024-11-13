import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MongodbChatComponent } from './mongodb-chat.component';

describe('MongodbChatComponent', () => {
  let component: MongodbChatComponent;
  let fixture: ComponentFixture<MongodbChatComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MongodbChatComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MongodbChatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
