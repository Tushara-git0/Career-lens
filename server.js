/**
 * Aetheris Labs D2C - Express Server Entry Point
 * Connects to MongoDB and mounts all API routes.
 */

'use strict';

const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
require('dotenv').config();

// ── Validate required environment variables ──────────────────────────────────
const REQUIRED_ENV = ['MONGO_URI', 'JWT_SECRET'];
const missing = REQUIRED_ENV.filter((key) => !process.env[key]);
if (missing.length > 0) {
  console.error(`[FATAL] Missing required environment variables: ${missing.join(', ')}`);
  console.error('Copy .env.example to .env and fill in the values.');
  process.exit(1);
}

const PORT = parseInt(process.env.PORT || '3000', 10);
const MONGO_URI = process.env.MONGO_URI;

// ── App Setup ────────────────────────────────────────────────────────────────
const app = express();

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static frontend from /public
app.use(express.static(path.join(__dirname, 'public')));

// ── Routes ───────────────────────────────────────────────────────────────────
const { router: authRouter } = require('./routes/authRoutes');
const productRouter = require('./routes/productRoutes');
const orderRouter = require('./routes/orderRoutes');

app.use('/api/auth', authRouter);
app.use('/api/products', productRouter);
app.use('/api/orders', orderRouter);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', service: 'Aetheris Labs D2C', timestamp: new Date().toISOString() });
});

// Serve frontend SPA for all unmatched routes (client-side routing support)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ── Global error handler ─────────────────────────────────────────────────────
app.use((err, req, res, next) => {
  console.error('[ERROR]', err.message);
  res.status(err.status || 500).json({ message: err.message || 'Internal Server Error' });
});

// ── MongoDB Connection + Server Start ────────────────────────────────────────
mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('='.repeat(60));
    console.log('  Aetheris Labs D2C - E-Commerce Server');
    console.log(`  MongoDB connected`);
    console.log(`  Server running at: http://localhost:${PORT}`);
    console.log('='.repeat(60));
    app.listen(PORT);
  })
  .catch((err) => {
    console.error('[FATAL] MongoDB connection failed:', err.message);
    process.exit(1);
  });
