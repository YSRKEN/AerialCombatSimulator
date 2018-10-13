import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ServiceWorkerModule } from '@angular/service-worker';
import { environment } from '../environments/environment';
import { RouterModule } from '@angular/router';
import { MainComponent } from './main/main.component';
import { NotFoundComponent } from './error/not-found/not-found.component';
import { SaveDataService } from './service/save-data.service';
import { EnemyDataComponent } from './form/enemy-data/enemy-data.component';
import { LBASDataComponent } from './form/lbasdata/lbasdata.component';
import { OwnDataComponent } from './form/own-data/own-data.component';
import { SimulationResultComponent } from './form/simulation-result/simulation-result.component';
import { FormsModule } from "@angular/forms";
import { LBASUnitComponent } from './form/lbasunit/lbasunit.component';
import { OwnUnitComponent } from './form/own-unit/own-unit.component';
import { WeaponSelectorComponent } from './control/weapon-selector/weapon-selector.component';

@NgModule({
  declarations: [
    AppComponent,
    MainComponent,
    NotFoundComponent,
    EnemyDataComponent,
    LBASDataComponent,
    OwnDataComponent,
    SimulationResultComponent,
    LBASUnitComponent,
    OwnUnitComponent,
    WeaponSelectorComponent
  ],
  imports: [
    BrowserModule.withServerTransition({ appId: 'serverApp' }),
    AppRoutingModule,
    ServiceWorkerModule.register('/ngsw-worker.js', { enabled: environment.production }),
    RouterModule,
    FormsModule
  ],
  providers: [SaveDataService],
  bootstrap: [AppComponent]
})
export class AppModule { }
