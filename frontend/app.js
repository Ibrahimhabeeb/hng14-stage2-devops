const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const API_URL = process.env.API_URL;
if (!API_URL) {
  throw new Error('API_URL environment variable is required');
}

const HOST = process.env.FRONTEND_HOST || '0.0.0.0';
const PORT = parseInt(process.env.FRONTEND_PORT || '3000', 10);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

app.get('/health', (_req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'something went wrong' });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    console.error(`Error occured while calling req with id: ${id}`)
    res.status(500).json({ error: 'something went wrong' });
  }
});

app.listen(PORT, HOST, () => {
  console.log(`Frontend listening on ${HOST}:${PORT}`);
});
