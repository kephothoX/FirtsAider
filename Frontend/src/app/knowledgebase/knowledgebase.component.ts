import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { ReactiveFormsModule, FormGroup, FormControl  } from '@angular/forms';
import { AppService } from '../app.service';

import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select'
import { MatCardModule } from '@angular/material/card';
import { MatRadioModule } from '@angular/material/radio';
import { MatStepperModule } from '@angular/material/stepper';
import { MatProgressBar } from '@angular/material/progress-bar';
import { MatListModule } from '@angular/material/list';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';


@Component({
  selector: 'app-knowledgebase',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatCardModule,
    MatStepperModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBar,
    MatSelectModule,
    MatListModule,
    MatDialogModule,
    MatSnackBarModule,
    MatTabsModule
  ],
  templateUrl: './knowledgebase.component.html',
  styleUrl: './knowledgebase.component.css'
})
export class KnowledgebaseComponent {
  formData = new FormData();
  Response: any;



  constructor (
    private _appService: AppService,
    private _router: Router,
    public _matSnackBar: MatSnackBar
  ) {}


  newPdfLoaderForm = new FormGroup({
    filePath: new FormControl()
  });

  newWebLoaderForm = new FormGroup({
    link: new FormControl()
  });


  async ngSubmitDocument() {
    this.formData.append('fileType', `${ window.localStorage.getItem('FileExt') }`);
    this.formData.append('filePath', this.newPdfLoaderForm.value.filePath)

    console.log(this.formData.get('file'));
    console.log(`${ window.localStorage.getItem('FileExt') }`);

    await fetch(`${ this._appService.API_URL }/pdf-loader`, {
      method: 'POST',
      headers: new Headers({
        
      }),
      body: this.formData
    })
     .then(async (response: any) => {
      const fetchResponse = await response.json();
      this.Response = fetchResponse.response;

      this._matSnackBar.open(`${ fetchResponse.response }`, 'Dismiss');
      if (fetchResponse.response) {
        window.location.reload();
      }
    });
  }


  async ngSubmitLink() {
    this.formData.append('link', `${ this.newWebLoaderForm.value.link }`);

    await fetch(`${ this._appService.API_URL }/web-loader`, {
      method: 'POST',
      headers: new Headers({
        
      }),
      body: this.formData
    })
     .then(async (response: any) => {

      const fetchResponse = await response.json();
      this.Response = fetchResponse.response;

      this._matSnackBar.open(`${ fetchResponse.response }`, 'Dismiss');
      if (fetchResponse.response) {
        window.location.reload();
      }
    });
  }



  onFileChange(event: any) {
    if (event.target.files && event.target.files.length) {
      const file = event.target.files[0];

        this.getFileExtension(`${ file.name }`);
        this.formData.append('file', file);

    }
  }

  getFileExtension(file: any) {
    const ext = file.substring(file.lastIndexOf('.') + 1, file.length);

    window.localStorage.setItem('FileExt', ext);
    return ext;
  }
}
