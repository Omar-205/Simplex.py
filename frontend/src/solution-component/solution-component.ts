import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LpStateService } from '../service/backend-service';
import { LpProblem } from '../models/model';
import { SolveResponse } from '../models/model';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-solution-component',
  imports: [CommonModule, MatIconModule],
  templateUrl: './solution-component.html',
  styleUrl: './solution-component.css',
})
export class SolutionComponent implements OnInit {
  result: SolveResponse | null = null;
  problem: LpProblem = {
    n: 2,
    m: 2,
    objective: 'MAXIMIZE',
    objectiveCoeffs: [],
    constraints: [],
    variableRestrictions: [],
  };

  constructor(private lpState: LpStateService) {}

  ngOnInit() {
    this.lpState.result$.subscribe((r) => (this.result = r));
    this.lpState.problem$.subscribe((c) => (this.problem = c));
  }

  get isOptimal(): boolean {
    return this.result?.status === 'optimal';
  }
  get isInfeasible(): boolean {
    return this.result?.status === 'infeasible';
  }
  get isUnbounded(): boolean {
    return this.result?.status === 'unbounded';
  }

  get objectiveValue(): number {
    return this.result?.optimalValue ?? 0;
  }

  get decisionVars(): Array<{ name: string; value: number; isBasic: boolean }> {
    if (!this.result) return [];
    return Array.from({ length: this.problem.n }, (_, i) => {
      const key = `x${i + 1}`;
      const value = this.result!.solution[key] ?? 0;
      return {
        name: key,
        value,
        isBasic: Math.abs(value) > 1e-9,
      };
    });
  }

  get slackVars(): Array<{ name: string; value: number; isBasic: boolean }> {
    if (!this.result) return [];
    return Array.from({ length: this.problem.m }, (_, i) => {
      const key = `s${i + 1}`;
      const value = this.result!.solution[key] ?? 0;
      return { name: key, value, isBasic: Math.abs(value) > 1e-9 };
    });
  }

  get solutionRepresentation(): string {
    if (!this.result) return '';
    const vars = this.decisionVars.map((v) => `${v.name} = ${this.formatVal(v.value)}`).join(', ');
    return `(${vars})`;
  }

  formatVal(v: number): string {
    if (Math.abs(v) < 1e-9) return '0';
    if (Number.isInteger(v)) return v.toString();
    return (+v.toFixed(4)).toString();
  }

  get iterationsCount(): number {
    return this.result?.snapshots.length ?? 0;
  }
}
