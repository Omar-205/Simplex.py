export interface Constraint {
  coefficients: number[];
  sign: '<=' | '>=' | '=';
  rhs: number;
}

export interface LpProblem {
  n: number;
  m: number;
  objective: 'MAXIMIZE' | 'MINIMIZE';
  objectiveCoeffs: number[];
  constraints: Constraint[];
  variableRestrictions: boolean[];
}

export interface TableauRow {
  basis: string;
  values: number[];
  isZRow?: boolean;
  isPivotRow?: boolean;
}

export interface Tableau {
  headers: string[];
  rows: TableauRow[];
  pivotCol?: number;
  pivotRow?: number;
}

export interface Snapshot {
  label?: string;
  tableau: Tableau;
  analysis: string;
  entering?: string;
  leaving?: string;
  pivot?: number;
  currentZ: number;
}

export interface SolveResponse {
  status: 'optimal' | 'infeasible' | 'unbounded';
  snapshots: Snapshot[];
  isTwoPhase?: boolean;
  optimalValue: number;
  solution: { [key: string]: number };
}
