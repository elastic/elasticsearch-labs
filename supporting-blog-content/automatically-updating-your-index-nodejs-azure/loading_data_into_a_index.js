// Load environment variables from a .env file into process.env
require('dotenv').config();

// Import necessary modules
const { Client } = require('@elastic/elasticsearch');
const axios = require('axios');

// Retrieve environment variables for Elasticsearch and NASA API keys
const elasticsearchEndpoint = process.env.ELASTICSEARCH_ENDPOINT;
const elasticsearchApiKey = process.env.ELASTICSEARCH_API_KEY;
const nasaApiKey = process.env.NASA_API_KEY;

// Initialize Elasticsearch client with endpoint and API key authentication
const client = new Client({
  node: elasticsearchEndpoint,
  auth: {
    apiKey: elasticsearchApiKey
  }
});

// Function to fetch data from NASA API
async function fetchNasaData() {
  const url = "https://api.nasa.gov/neo/rest/v1/feed";
  
  // Get today's date and the date one week ago
  const today = new Date();
  const lastWeek = new Date(today);
  lastWeek.setDate(today.getDate() - 7);

  // Format dates as YYYY-MM-DD
  const startDate = lastWeek.toISOString().split('T')[0];
  const endDate = today.toISOString().split('T')[0];
  
  // Set parameters for NASA API request
  const params = {
    api_key: nasaApiKey,
    start_date: startDate,
    end_date: endDate,
  };

  try {
    // Make GET request to NASA API
    const response = await axios.get(url, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching data from NASA:', error);
    return null;
  }
}

// Function to transform raw NASA data into a structured format suitable for Elasticsearch
function createStructuredData(response) {
  const allObjects = [];
  const nearEarthObjects = response.near_earth_objects;

  // Iterate over each date's near-earth objects
  Object.keys(nearEarthObjects).forEach(date => {
    nearEarthObjects[date].forEach(obj => {
      // Simplify object structure
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

// Function to check for an index's existence in Elasticsearch and index data
async function indexDataIntoElasticsearch(data) {
  // Check if the index exists
  const indexExists = await client.indices.exists({ index: 'nasa-node-js' });
  if (!indexExists.body) {
    // Create the index with mappings if it does not exist
    await client.indices.create({
      index: 'nasa-node-js',
      body: {
        mappings: {
          properties: {
            close_approach_date: { type: 'date' },
            name: { type: 'text' },
            miss_distance_km: { type: 'float' },
          },
        },
      },
    });
  }

  // Prepare bulk request body
  const body = data.flatMap(doc => [{ index: { _index: 'nasa-node-js', _id: doc.id } }, doc]);
  
  // Index data into Elasticsearch
  await client.bulk({ refresh: false, body });
}

// Main function to run the data fetching, transformation, and indexing
async function run() {
  // Fetch raw data from NASA API
  const rawData = await fetchNasaData();
  
  if (rawData) {
    // Transform raw data into structured format
    const structuredData = createStructuredData(rawData);
    console.log(`Number of records being uploaded: ${structuredData.length}`);
    
    // Index data if there are records to upload
    if (structuredData.length > 0) {
      await indexDataIntoElasticsearch(structuredData);
      console.log('Data indexed successfully.');
    } else {
      console.log('No data to index.');
    }
  } else {
    console.log('Failed to fetch data from NASA.');
  }
}

// Execute the main function and catch any errors
run().catch(console.error);
