const { Client } = require('@elastic/elasticsearch');
const axios = require('axios');

// Retrieve environment variables
const elasticsearchEndpoint = process.env.ELASTICSEARCH_ENDPOINT;
const elasticsearchApiKey = process.env.ELASTICSEARCH_API_KEY;
const nasaApiKey = process.env.NASA_API_KEY;

// Authenticate to Elasticsearch
const client = new Client({
  node: elasticsearchEndpoint,
  auth: {
    apiKey: elasticsearchApiKey
  }
});

// Function to get the last update date from Elasticsearch
async function getLastUpdateDate() {
  try {
    const response = await client.search({
      index: 'nasa-node-js',
      body: {
        size: 1,
        sort: [{ close_approach_date: { order: 'desc' } }],
        _source: ['close_approach_date']
      }
    });

    if (response.body && response.body.hits && response.body.hits.hits.length > 0) {
      return response.body.hits.hits[0]._source.close_approach_date;
    } else {
      // Default to one day ago if no records found
      const today = new Date();
      const lastWeek = new Date(today);
      lastWeek.setDate(today.getDate() - 1);
      return lastWeek.toISOString().split('T')[0];
    }
  } catch (error) {
    console.error('Error fetching last update date from Elasticsearch:', error);
    throw error;
  }
}

// Asynchronously fetch data from NASA's NEO (Near Earth Object) Web Service
async function fetchNasaData(startDate) {
  // Define the base URL for the NASA API request
  const url = "https://api.nasa.gov/neo/rest/v1/feed";
  const today = new Date();

  // Format dates as YYYY-MM-DD for the API request
  const endDate = today.toISOString().split('T')[0];

  // Setup the query parameters including the API key and date range
  const params = {
    api_key: nasaApiKey,
    start_date: startDate,
    end_date: endDate,
  };

  try {
    // Perform the GET request to the NASA API with query parameters
    const response = await axios.get(url, { params });
    return response.data;
  } catch (error) {
    // Log any errors encountered during the request
    console.error('Error fetching data from NASA:', error);
    return null;
  }
}

// Transform the raw data from NASA into a structured format for Elasticsearch
function createStructuredData(response) {
  const allObjects = [];
  const nearEarthObjects = response.near_earth_objects;

  // Iterate over each date's objects to extract and structure necessary information
  Object.keys(nearEarthObjects).forEach(date => {
    nearEarthObjects[date].forEach(obj => {
      const simplifiedObject = {
        close_approach_date: date,
        name: obj.name,
        id: obj.id,
        miss_distance_km: obj.close_approach_data.length > 0 ? obj.close_approach_data[0].miss_distance.kilometers : null,
      };

      allObjects.push(simplifiedObject);
    });
  });

  return allObjects;
}

// Asynchronously index data into Elasticsearch
async function indexDataIntoElasticsearch(data) {
  const body = data.flatMap(doc => [{ index: { _index: 'nasa-node-js', _id: doc.id } }, doc]);
  // Execute the bulk indexing operation
  await client.bulk({ refresh: false, body });
}

// Azure Function entry point
module.exports = async function (context, myTimer) {
  try {
    // Get the last update date from Elasticsearch
    const lastUpdateDate = await getLastUpdateDate();
    context.log(`Last update date from Elasticsearch: ${lastUpdateDate}`);

    // Fetch data from NASA starting from the last update date
    const rawData = await fetchNasaData(lastUpdateDate);
    if (rawData) {
      // Structure the fetched data
      const structuredData = createStructuredData(rawData);
      // Print the number of records
      context.log(`Number of records being uploaded: ${structuredData.length}`);
      
      if (structuredData.length > 0) {
        // Store data in a variable and log it (instead of writing to a file)
        const flatFileData = JSON.stringify(structuredData, null, 2);
        context.log('Flat file data:', flatFileData);

        // Index the structured data into Elasticsearch
        await indexDataIntoElasticsearch(structuredData);
        context.log('Data indexed successfully.');
      } else {
        context.log('No data to index.');
      }
    } else {
      context.log('Failed to fetch data from NASA.');
    }
  } catch (error) {
    context.log('Error in run process:', error);
  }
};
