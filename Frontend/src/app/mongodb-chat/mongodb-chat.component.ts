import { Component, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormGroup, FormControl }  from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { AppService } from '../app.service';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select'
import { MatCardModule } from '@angular/material/card';
import { MatStepperModule } from '@angular/material/stepper';
import { MatProgressBar } from '@angular/material/progress-bar';
import { MatListModule } from '@angular/material/list';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-mongodb-chat',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatCardModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBar,
    MatSelectModule,
    MatListModule,
    MatDialogModule,
    MatSnackBarModule
  ],
  templateUrl: './mongodb-chat.component.html',
  styleUrl: './mongodb-chat.component.css'
})
export class MongodbChatComponent implements OnInit {
  formData = new FormData()
  PromptQuery: any;
  PromptResponse: any;
  SummaryResponse: any;

  constructor (
    private _appService: AppService,
    private _router: Router,
    public _matSnackBar: MatSnackBar
  ) {}


  ngOnInit(): void {

    /*if (Boolean(window.sessionStorage.getItem('isAuthenticated'))) {
        this._matSnackBar.open('Logged In....', 'Dismiss');
    } else {
       this._router.navigate(['/authn/login']);
    }*/

  }

  promptForm = new FormGroup({
    prompt: new FormControl()
  })

  resetPromptForm(): void {
    this.promptForm.reset();
  }


  async ngOnSubmit() {
    this.formData.append('prompt', this.promptForm.value.prompt);
    this.PromptQuery = prompt;

    this.resetPromptForm();

    const chatBox = document.getElementById("ChatBox");

     await fetch(`${ this._appService.API_URL }/prompt`, {
      method: 'POST',
      headers: new Headers({
      }),
      body: this.formData
     })
    .then(async (response: any) => {
      const res  = await response.json();

      this.formData.delete('prompt');

      this.PromptResponse = res
      this.PromptQuery = '';

      if (chatBox) {
        const queryBox = document.createElement('div');
      queryBox.setAttribute('class', 'alert alert-secondary text-wrap align-left float-start queryBox p-1 m-1 mat-elevation-z2');
      queryBox.setAttribute('role', 'alert');

      const query = document.createElement("p");
      query.setAttribute('class', 'text-start font-monospace p-1');
      query.innerHTML = `${ res.Input }`;

      const icon_q = document.createElement('mat-icon');
      icon_q.setAttribute('class', 'float-start m-1')
      const avatar_q = document.createElement('img');
      avatar_q.setAttribute('class', 'mat-card-img-sm brand2-pic mat-elevation-z2')
      avatar_q.src = 'FAUser.png';

      icon_q.append(avatar_q);
      queryBox.append(icon_q);
      queryBox.append(query);
      chatBox.append(queryBox);


        const resBox = document.createElement('div');
        resBox.setAttribute('class', 'alert alert-danger text-wrap align-right float-end resBox p-1 m-1 mat-elevation-z2');
        resBox.setAttribute('role', 'alert');

        const resp = document.createElement("p");
        resp.setAttribute('class', 'text-end fw-medium');
        resp.innerHTML = `${ res.Answer }`;

     
        const icon = document.createElement('mat-icon');
        icon.setAttribute('class', 'float-end m-1')
        const avatar = document.createElement('img');
        avatar.setAttribute('class', 'mat-card-img-sm brand2-pic mat-elevation-z2')
        avatar.src =`FAChat.png`;

        icon.append(avatar);
        resBox.append(icon);
        resBox.append(resp);
        chatBox.append(resBox);

      }

    })
    .then((data: any) => {
    })
    .catch((err: any) => {
      this._matSnackBar.open(JSON.stringify(err), 'Dismiss');
    });  


  }

}




