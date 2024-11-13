import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { ErrorService } from './error.service';
import { Observable, catchError, of} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AppService {

  API_URL = "https://5000-idx-mongovarsity-1731094466375.cluster-4ezwrnmkojawstf2k7vqy36oe6.cloudworkstations.dev/api/v1"

  constructor(
    private _httpClient: HttpClient,
    private _errorService: ErrorService
  ) { }

  ping(): Observable<any> {
    return this._httpClient.get(`${ this.API_URL }/`).pipe(catchError(this._errorService.handleError));
  }


  prompt(data: any): Observable<any>{
    return this._httpClient.post(`${ this.API_URL }/prompt`, data).pipe(catchError(this._errorService.handleError));
  }

}
