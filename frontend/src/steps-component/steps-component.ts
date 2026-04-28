import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LpStateService } from '../service/backend-service';
import { SolveResponse, Snapshot } from '../models/model';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-steps-component',
  imports: [MatIconModule, FormsModule, CommonModule],
  templateUrl: './steps-component.html',
  styleUrl: './steps-component.css',
})
export class StepsComponent implements OnInit {
  result: SolveResponse | null = null;

  constructor(private lpState: LpStateService) {}

  ngOnInit() {
    this.lpState.result$.subscribe((result) => {
      this.result = result;
    });
  }

  get snapshots(): Snapshot[] {
    return this.result?.snapshots ?? [];
  }

  get totalSteps(): number {
    return this.result?.snapshots.length ?? 0;
  }

  getCellClass(step: Snapshot, rowIdx: number, colIdx: number): string {
    const row = step.tableau.rows[rowIdx];
    const pivotCol = step.tableau.pivotCol;
    const pivotRow = step.tableau.pivotRow;
    const isZRow = row.isZRow;

    // col index in values array: 0 = basis label, 1..n = values, last = RHS
    // colIdx here is index into values (0-based, excluding basis column)
    const varIdx = colIdx; // 0-based index into values array

    if (row.isPivotRow && pivotCol !== undefined && varIdx === pivotCol) {
      return 'cell-pivot'; // pivot element
    }
    if (pivotCol !== undefined && varIdx === pivotCol && !isZRow) {
      return 'cell-pivot-col';
    }
    if (row.isPivotRow) {
      return 'cell-pivot-row';
    }
    if (isZRow) {
      return 'cell-z-row';
    }
    return '';
  }

  getEnteringHeader(step: Snapshot, colIdx: number): boolean {
    return step.tableau.pivotCol !== undefined && colIdx === step.tableau.pivotCol;
  }

  formatValue(v: number): string {
    if (Math.abs(v) < 1e-9) return '0';
    if (Number.isInteger(v)) return v.toString();
    return +v.toFixed(4) + '';
  }
}
