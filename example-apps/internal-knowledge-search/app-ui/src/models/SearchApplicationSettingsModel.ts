import {FilterModel} from "./FilterModel";

export interface SearchApplicationSettingsModel {
    appName: string;
    indices: string[];
    searchEndpoint: string;
    searchPersona: string;
    searchPersonaAPIKey: string;
}
