import { Injectable } from '@angular/core';
import { Constraint, Snapshot, SolveResponse, Tableau, TableauRow } from '../models/model';
type BackendOperator = '<=' | '>=' | '==';

interface BackendConstraint {
  coefficients: number[];
  sign: BackendOperator;
  rhs: number;
}

interface BackendSnapshot {
  matrix: number[][];
  z: number[];

  varMap: string[];
  slackStart: number;
  surplusStart: number;
  artStart: number;

  rowIdx: number | null;
  colIdx: number | null;
  pivot: number | null;

  enteringVar: string | null;
  leavingVar: string | null;

  basicVars: string[];
  phase: 1 | 2;
}

interface BackendSolveResponse {
  status: 'optimal' | 'infeasible' | 'unbounded';
  snapshots: BackendSnapshot[];
  optimalValue: number | null;
  solution: Record<string, number> | null;
}

// ─────────────────────────────────────────────────────────────────────────────
// Mapper
// ─────────────────────────────────────────────────────────────────────────────

@Injectable({ providedIn: 'root' })
export class LpMapperService {
  isTwoPhase: boolean = true;
  currentPhase: 1 | 2 = 1;

  mapSolveResponse(raw: BackendSolveResponse): SolveResponse {
    return {
      status: raw.status,
      optimalValue: raw.optimalValue ?? 0,
      solution: raw.solution ?? {},
      snapshots: raw.snapshots.map((s, i) => this.mapSnapshot(s, i, raw.snapshots.length)),
      isTwoPhase: this.isTwoPhase,
    };
  }

  private mapSnapshot(raw: BackendSnapshot, index: number, total: number): Snapshot {
    if (index === 0 && raw.phase === 2) this.isTwoPhase = false; // if first snapshot is from phase 2, then it's not a two-phase problem
    if (index > 0 && raw.phase == 2 && this.isTwoPhase) {
      this.currentPhase = 2;
    }

    const tableau = this.buildTableau(raw);
    const currentZ = raw.z[raw.z.length - 1]; // last entry of z-row is the RHS (objective value)
    return {
      label: this.formLabel(index),
      tableau,
      currentZ,
      entering: raw.enteringVar ?? undefined,
      leaving: raw.leavingVar ?? undefined,
      pivot: raw.pivot ?? undefined,
      // analysis: this.deriveAnalysis(raw, index, total, currentZ),
      analysis: '',
    };
  }
  private buildTableau(raw: BackendSnapshot): Tableau {
    const headers = ['BASIS', ...raw.varMap];

    const constraintRows: TableauRow[] = raw.matrix.map((row, rowIndex) => ({
      basis: raw.basicVars[rowIndex] ?? `r${rowIndex}`,
      values: row,
      isPivotRow: raw.rowIdx !== null && raw.rowIdx === rowIndex,
    }));

    const zRow: TableauRow = {
      basis: 'Z',
      values: raw.z,
      isZRow: true,
    };

    return {
      headers,
      rows: [...constraintRows, zRow],
      pivotCol: raw.colIdx ?? undefined,
      pivotRow: raw.rowIdx ?? undefined,
    };
  }

  // private deriveAnalysis(
  //   raw: BackendSnapshot,
  //   index: number,
  //   total: number,
  //   currentZ: number,
  // ): string {
  //   if (index === total - 1) {
  //     if (raw.enteringVar == null && raw.leavingVar == null) {
  //       return (
  //         `Optimal solution found! All coefficients in the Z-row are non-negative, ` +
  //         `indicating we have reached the optimal solution. Z = ${currentZ}.`
  //       );
  //     }
  //   }

  //   if (index === 0) {
  //     const basisList = raw.basicVars.join(', ');
  //     return (
  //       `Initial simplex tableau. Basic variables are (${basisList}). ` +
  //       `We look for negative coefficients in the Z-row to identify the entering variable.`
  //     );
  //   }

  //   if (raw.enteringVar && raw.leavingVar && raw.colIdx !== null && raw.rowIdx !== null) {
  //     return (
  //       `Step ${index}: Most negative Z-row coefficient is at column ${raw.colIdx + 1} ` +
  //       `(${raw.enteringVar}). Minimum-ratio test selects row ${raw.rowIdx + 1}. ` +
  //       `Pivot element: ${raw.pivot?.toFixed(2) ?? '?'}. ` +
  //       `${raw.enteringVar} enters, ${raw.leavingVar} leaves the basis.`
  //     );
  //   }

  //   return `Iteration ${index}.`;
  // }

  formLabel(index: number): string {
    if (index === 0) {
      return this.isTwoPhase ? `Initial Tableau - Phase ${this.currentPhase}` : 'Initial Tableau';
    }
    return `Iteration ${index + 1} - Phase ${this.currentPhase}`;
  }
}
