import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Required for ngModel (N and M inputs)
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonToggleModule } from '@angular/material/button-toggle'; // For MAX/MIN toggle
import { InputComponent } from '../input-component/input-component';
import { StepsComponent } from '../steps-component/steps-component';
import { SolutionComponent } from '../solution-component/solution-component';
import { LpStateService } from '../service/backend-service';
import { SolveResponse } from '../models/model';

@Component({
  selector: 'app-root',
  imports: [
    MatTabsModule,
    MatToolbarModule,
    MatButtonModule,
    InputComponent,
    StepsComponent,
    SolutionComponent,
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonToggleModule,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('SimplexSolverUI');
  result: SolveResponse | null = null;
  service = inject(LpStateService);
  n = 2;
  m = 2;
  objective: 'MAXIMIZE' | 'MINIMIZE' = 'MAXIMIZE';
  solved = false;
  selectedTabIndex = 0;
  solutionStatus = '';

  onNChange(delta: number) {
    const newN = Math.max(1, this.n + delta); // to prevent having a value less than 1
    this.n = newN;
    this.service.updateProblem({ n: newN, m: this.m, objective: this.objective });
  }

  onMChange(delta: number) {
    const newM = Math.max(1, this.m + delta); // to prevent having a value less than 1
    this.m = newM;
    this.service.updateProblem({ n: this.n, m: newM, objective: this.objective });
  }

  onObjectiveChange(val: 'MAXIMIZE' | 'MINIMIZE') {
    this.objective = val;
    this.service.updateProblem({ n: this.n, m: this.m, objective: val });
  }

  reset() {
    this.n = 2;
    this.m = 2;
    this.objective = 'MAXIMIZE';
    this.selectedTabIndex = 0;
    this.service.reset();
  }

  onTabChange(index: number) {
    this.selectedTabIndex = index;
  }

  onProblemSolved() {
    console.log('Event received in Parent! Switching tabs...');
    this.solved = true;
    this.selectedTabIndex = 1; // Switch to steps tab
    this.result = this.service.result;
    this.solutionStatus = this.result?.status || '';
  }
  getBadgeClass(): string {
    if (this.solutionStatus === 'unbounded') {
      return 'tab-badge tab-badge-yellow';
    } else if (this.solutionStatus === 'infeasible') {
      return 'tab-badge tab-badge-red';
    }
    return 'tab-badge tab-badge-green';
  }
}
