require("dotenv").config();

const express = require("express");
const cors = require("cors");
const app = express();
const axios = require("axios");

app.use(express.json());
app.use(cors());

const { ELASTICSEARCH_URL, API_KEY } = process.env;

// Handle all _search requests
app.post("/api/:index/_search", async (req, res) => {
  try {
    const response = await axios.post(
      `${ELASTICSEARCH_URL}/${req.params.index}/_search`,
      req.body,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `ApiKey ${API_KEY}`,
        },
      }
    );
    res.json(response.data);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: error.message });
  }
});

// Handle all _completion requests
app.post("/api/completion", async (req, res) => {
  try {
    const response = await axios.post(
      `${ELASTICSEARCH_URL}/_inference/completion/summaries-completion`,
      req.body,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `ApiKey ${API_KEY}`,
        },
      }
    );
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start the server
const PORT = process.env.PORT || 1337;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
