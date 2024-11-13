import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { throwError } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class ErrorService {

  constructor() { }

  handleError(error: HttpErrorResponse, err: any) {
    if(error.error instanceof ErrorEvent) {
      return throwError(() => new Error(error.error.message));
    } else {
      return throwError(() => new Error(`Error Header: ${ error.headers } \n Error code: ${ error.status } \nMessage: ${ error.message }`));
    }

  }
}

