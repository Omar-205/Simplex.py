import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { LpProblem, SolveResponse } from '../models/model';
import { LpMapperService } from './lp-mapper-service';

@Injectable({ providedIn: 'root' })
export class LpStateService {
  private readonly API_URL = 'http://localhost:8000/solve'; // TODO: update to real URL

  private problemSubject = new BehaviorSubject<LpProblem>({
    n: 2,
    m: 2,
    objective: 'MAXIMIZE',
    objectiveCoeffs: [],
    constraints: [],
    variableRestrictions: [],
  });
  private resultSubject = new BehaviorSubject<SolveResponse | null>(null);
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private errorSubject = new BehaviorSubject<string | null>(null);
  private isSolvedSubject = new BehaviorSubject<boolean>(false);

  problem$ = this.problemSubject.asObservable();
  result$ = this.resultSubject.asObservable();
  loading$ = this.loadingSubject.asObservable();
  error$ = this.errorSubject.asObservable();
  isSolved$ = this.isSolvedSubject.asObservable();

  get problem(): LpProblem {
    return this.problemSubject.value;
  }
  get result(): SolveResponse | null {
    return this.resultSubject.value;
  }

  constructor(
    private http: HttpClient,
    private mapper: LpMapperService,
  ) {}

  updateProblem(partial: Partial<LpProblem>) {
    const updatedProblem = { ...this.problemSubject.value, ...partial };
    this.problemSubject.next(updatedProblem);
    this.resultSubject.next(null);
    this.isSolvedSubject.next(false);
    this.errorSubject.next(null);
  }

  solve(problem: LpProblem): Observable<SolveResponse> {
    this.loadingSubject.next(true);
    this.errorSubject.next(null);

    // const result = of(MOCK_BACKEND_RESPONSE);

    const result = this.http.post<any>(this.API_URL, problem);

    return result.pipe(
      map((raw) => this.mapper.mapSolveResponse(raw)),
      tap((result) => {
        this.resultSubject.next(result);
        this.isSolvedSubject.next(result.status === 'optimal');
        this.loadingSubject.next(false);
      }),
      catchError((err) => {
        this.errorSubject.next(err?.error?.message ?? 'Failed to reach the solver backend.');
        this.loadingSubject.next(false);
        throw err;
      }),
    );
  }

  reset() {
    this.problemSubject = new BehaviorSubject<LpProblem>({
      n: 2,
      m: 2,
      objective: 'MAXIMIZE',
      objectiveCoeffs: [],
      constraints: [],
      variableRestrictions: [],
    });
    this.resultSubject.next(null);
    this.isSolvedSubject.next(false);
    this.errorSubject.next(null);
    this.loadingSubject.next(false);
  }
}

const MOCK_BACKEND_RESPONSE = {
  status: 'optimal' as const,
  solution: { x1: 4, x2: 0, s1: 0, s2: 2 },
  optimalValue: 12,
  snapshots: [
    {
      matrix: [
        [1, 1, 1, 0, 4],
        [1, 2, 0, 1, 6],
      ],
      z: [-3, -2, 0, 0, 0],
      varMap: ['X1', 'X2', 'S1', 'S2'],
      slackStart: 2,
      surplusStart: 4,
      artStart: 4,
      rowIdx: null,
      colIdx: null,
      pivot: null,
      enteringVar: null,
      leavingVar: null,
      basicVars: ['s1', 's2'],
    },
    {
      matrix: [
        [1, 1, 1, 0, 4],
        [1, 2, 0, 1, 6],
      ],
      z: [-3, -2, 0, 0, 0],
      varMap: ['X1', 'X2', 'S1', 'S2'],
      slackStart: 2,
      surplusStart: 4,
      artStart: 4,
      rowIdx: 0,
      colIdx: 0,
      pivot: 1,
      enteringVar: 'x1',
      leavingVar: 's1',
      basicVars: ['s1', 's2'],
    },
    {
      matrix: [
        [1, 1, 1, 0, 4],
        [0, 1, -1, 1, 2],
      ],
      z: [0, 1, 3, 0, 12],
      varMap: ['X1', 'X2', 'S1', 'S2'],
      slackStart: 2,
      surplusStart: 4,
      artStart: 4,
      rowIdx: null,
      colIdx: null,
      pivot: null,
      enteringVar: null,
      leavingVar: null,
      basicVars: ['x1', 's2'],
    },
  ],
};
