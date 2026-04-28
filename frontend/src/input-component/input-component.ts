import {
  Component,
  Input,
  Output,
  OnChanges,
  SimpleChanges,
  OnInit,
  EventEmitter,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { LpStateService } from '../service/backend-service';
import { LpProblem } from '../models/model';

@Component({
  selector: 'app-input-component',
  imports: [CommonModule, FormsModule, MatIconModule],
  templateUrl: './input-component.html',
  styleUrl: './input-component.css',
})
export class InputComponent implements OnChanges, OnInit {
  @Input() n = 2;
  @Input() m = 2;
  @Input() objective: 'MAXIMIZE' | 'MINIMIZE' = 'MAXIMIZE';
  @Output() solved = new EventEmitter<void>();

  objectiveCoeffs: number[] = [];
  constraints: Array<{
    coefficients: number[];
    sign: '<=' | '>=' | '=';
    rhs: number;
  }> = [];
  variableRestrictions: boolean[] = [];

  activeView: 'matrix' | 'whiteboard' = 'matrix';
  isSolving = false;

  constructor(private service: LpStateService) {}

  ngOnInit() {
    this.initializeProblem();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['n'] || changes['m']) {
      this.initializeProblem();
    }
  }

  initializeProblem() {
    // Preserve existing values when resizing
    const oldCoeffs = this.objectiveCoeffs.slice();
    const oldConstraints = this.constraints.map((c) => ({
      ...c,
      coefficients: [...c.coefficients],
    }));
    const oldRestrictions = this.variableRestrictions.slice();

    this.objectiveCoeffs = Array.from({ length: this.n }, (_, i) => oldCoeffs[i] ?? 0);
    this.variableRestrictions = Array.from(
      { length: this.n },
      (_, i) => oldRestrictions[i] ?? true,
    );

    this.constraints = Array.from({ length: this.m }, (_, i) => ({
      coefficients: Array.from(
        { length: this.n },
        (_, j) => oldConstraints[i]?.coefficients[j] ?? 0,
      ),
      sign: (oldConstraints[i]?.sign ?? '<=') as '<=' | '>=' | '=',
      rhs: oldConstraints[i]?.rhs ?? 0,
    }));
  }

  getVarName(i: number): string {
    return `x${i + 1}`;
  }
  getSlackName(i: number): string {
    return `s${i + 1}`;
  }

  getStandardFormStr(): string {
    let first = true;
    return (
      this.objectiveCoeffs

        .map((c, i) => {
          if (c === 0) return '';

          const sign = !first && c > 0 ? '+' : ''; // checking if i>0 to avoid adding '+' for the first variable
          first = false;
          const coeff =
            Math.abs(c) === 1 ? (c < 0 ? '-' : '') : `${c === Math.floor(c) ? c : c.toFixed(2)}`;
          return `${sign}${coeff}x<sub>${i + 1}</sub>`;
        })
        .filter((s) => s !== '')
        .join('') || '0'
    );
  }

  getConstraintStr(ci: number): string {
    let first = true;
    return (
      this.constraints[ci].coefficients
        .map((c, i) => {
          if (c === 0) return '';
          const sign = !first && c > 0 ? '+' : '';
          first = false;
          const coeff =
            Math.abs(c) === 1 ? (c < 0 ? '-' : '') : `${c === Math.floor(c) ? c : c.toFixed(2)}`;
          return `${sign}${coeff}x<sub>${i + 1}</sub>`;
        })
        .filter((s) => s !== '')
        .join('') || '0'
    );
  }

  getStandardConstraint(ci: number): string {
    const base = this.getConstraintStr(ci);
    const slack =
      `+s<sub>${ci + 1}</sub>` +
      (this.constraints[ci].sign === '>=' ? `-s<sub>${ci + 1}</sub>` : '');
    return `${base}${slack}`;
  }
  needsSlack(ci: number): boolean {
    return this.constraints[ci].sign === '<=';
  }
  needsSurplus(ci: number): boolean {
    return this.constraints[ci].sign === '>=';
  }
  needsArtificial(ci: number): boolean {
    return this.constraints[ci].sign === '>=' || this.constraints[ci].sign === '=';
  }

  getNonNegativityStr(): string {
    const decisionVars: string[] = [];
    const slackVars: string[] = [];
    const surplusVars: string[] = [];
    const artificialVars: string[] = [];

    this.objectiveCoeffs.forEach((_, i) => {
      if (this.variableRestrictions[i] === true) {
        decisionVars.push(`x<sub>${i + 1}</sub>`);
      }
    });

    this.constraints.forEach((con, i) => {
      const idx = i + 1;
      if (this.needsSlack(i)) slackVars.push(`s<sub>${idx}</sub>`);
      if (this.needsSurplus(i)) surplusVars.push(`e<sub>${idx}</sub>`);
      if (this.needsArtificial(i)) artificialVars.push(`u<sub>${idx}</sub>`);
    });
    const allVars = [...decisionVars, ...slackVars, ...surplusVars, ...artificialVars];
    return allVars.join(', ') + ' ≥ 0';
  }

  cycleMSign(ci: number) {
    const order: ('<=' | '>=' | '=')[] = ['<=', '>=', '='];
    const curr = order.indexOf(this.constraints[ci].sign);
    this.constraints[ci].sign = order[(curr + 1) % order.length];
  }
  async solve() {
    const problem: LpProblem = {
      n: this.n,
      m: this.m,
      objective: this.objective,
      objectiveCoeffs: [...this.objectiveCoeffs],
      constraints: this.constraints.map((c) => ({
        coefficients: [...c.coefficients],
        sign: c.sign,
        rhs: c.rhs,
      })),
      variableRestrictions: [...this.variableRestrictions],
    };

    this.service.solve(problem).subscribe({
      next: (result) => {
        console.log('Solve successful! Tabs will update automatically.');
        this.solved.emit();
      },
      error: (err) => {
        console.error('Error solving LP:', err);
      },
    });
  }
}
