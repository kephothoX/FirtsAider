import { Routes } from '@angular/router';

import { MongodbChatComponent } from './mongodb-chat/mongodb-chat.component';
import { KnowledgebaseComponent } from './knowledgebase/knowledgebase.component';

export const routes: Routes = [
    { path: '', redirectTo: '/chat', pathMatch: 'full' },
    { path: 'chat', title: 'Mongo Varsity Chat', component: MongodbChatComponent },
    { path: 'knowledgebase', title: 'Add Knowledgebase', component: KnowledgebaseComponent }
];
