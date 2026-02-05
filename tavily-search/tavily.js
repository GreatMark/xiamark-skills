#!/usr/bin/env node

/**
 * Tavily Search Script
 * Usage: ./tavily.js "<query>" [search_depth: basic|advanced] [include_answer: true|false]
 */

const https = require('https');

const fs = require('fs');
const path = require('path');

let API_KEY = process.env.TAVILY_API_KEY;

if (!API_KEY) {
  try {
    const secretsPath = path.join(__dirname, 'secrets.json');
    if (fs.existsSync(secretsPath)) {
      const secrets = JSON.parse(fs.readFileSync(secretsPath, 'utf8'));
      API_KEY = secrets.api_key;
    }
  } catch (e) {
    // ignore
  }
}

if (!API_KEY) {
  console.error('Error: TAVILY_API_KEY environment variable is not set and secrets.json not found.');
  process.exit(1);
}

const query = process.argv[2];
if (!query) {
  console.error('Usage: tavily.js <query> [search_depth] [include_answer]');
  process.exit(1);
}

const search_depth = process.argv[3] || 'basic';
const include_answer = process.argv[4] === 'true';

const postData = JSON.stringify({
  api_key: API_KEY,
  query: query,
  search_depth: search_depth,
  include_answer: include_answer,
  max_results: 5
});

const options = {
  hostname: 'api.tavily.com',
  port: 443,
  path: '/search',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': postData.length
  }
};

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      try {
        const json = JSON.parse(data);
        console.log(JSON.stringify(json, null, 2));
      } catch (e) {
        console.error('Error parsing JSON response:', e);
        console.log(data);
      }
    } else {
      console.error(`API Error: ${res.statusCode}`);
      console.log(data);
      process.exit(1);
    }
  });
});

req.on('error', (e) => {
  console.error(`Request error: ${e.message}`);
  process.exit(1);
});

req.write(postData);
req.end();
