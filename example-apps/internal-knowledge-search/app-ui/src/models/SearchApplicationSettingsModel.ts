import {FilterModel} from "./FilterModel";

export interface SearchApplicationSettingsModel {
    appName: string;
    appUser: string;
    appPassword: string;
    searchEndpoint: string;

    searchPersona: string;
}