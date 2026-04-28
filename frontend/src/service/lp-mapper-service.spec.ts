import { TestBed } from '@angular/core/testing';

import { LpMapperService } from './lp-mapper-service';

describe('LpMapperService', () => {
  let service: LpMapperService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LpMapperService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
