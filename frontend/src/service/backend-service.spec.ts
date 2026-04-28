import { TestBed } from '@angular/core/testing';

import { LpStateService } from './backend-service';

describe('LpStateService', () => {
  let service: LpStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LpStateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
