# Blazor Elasticsearch Search Application

This Blazor application integrates with Elasticsearch to perform searches and display results with facets. It leverages Elasticsearch's powerful search capabilities to provide a flexible search experience. 

## Tutorial

This application was created based on the following tutorial:
- [Blazor Intro Tutorial](https://dotnet.microsoft.com/en-us/learn/aspnet/blazor-tutorial/intro)

## Dataset

The dataset used in this application is a collection of books extracted from a practice notebook on Kaggle:
- [Kaggle Dataset](https://www.kaggle.com/code/prathammalvia/books-data-analysis-json-data)

The raw dataset can be found here:
- [Books Dataset](https://raw.githubusercontent.com/ozlerhakan/mongodb-json-files/master/datasets/books.json)

For this project, I cleaned and transformed some fields to enhance readability and improve the search experience.

## Installation

To set up and run this application locally, follow these steps:

### 1. Install Dependencies

Ensure you have [.NET 8.0 SDK](https://dotnet.microsoft.com/es-es/download/dotnet/8.0) installed. Then, run the following command:

```bash
dotnet restore
```

### 2. Configure Elasticsearch

Ensure that Elasticsearch is running and accessible. Create a `secrets.json` file in the root of the project with the following content:

```json
{
  "ElasticsearchCloudId": "your-cloud-id",
  "ElasticsearchApiKey": "your-api-key"
}
```

Initialize user secrets by running:

```bash
dotnet user-secrets init
```
Then, set the secrets with:

```bash
cat ./secrets.json | dotnet user-secrets set
```

## Running the Application
   
To run the application locally, use the following command:

```bash
dotnet run
```

The application will start and be accessible at http://localhost:5128 or as specified in the `launchSettings.json` file.

## Application Structure
- [ElasticsearchServices.cs:](./Services/ElasticsearchService.cs) The core of the application, containing the logic for interacting with Elasticsearch.
- Components:
  - [Facet:](./Components/Elasticsearch/Facet.razor) Component for displaying and interacting with search facets. 
  - [Results:](./Components/Elasticsearch/Results.razor) Component for displaying search results.
  - [SearchBar:](./Components/Elasticsearch/SearchBar.razor) Component for the search input bar.