export interface SearchResultModel {
    title: string;
    created: string;
    dataSource: string;
    dataSourceImagePath?: string;
    previewText: string;
    fullText: string;
    link?: string;
    additionalProps?: Record<string, any>;
    source?: Record<string, any>;
}
