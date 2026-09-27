const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const JWT_SECRET = process.env.JWT_SECRET || 'aetheris_laboratory_private_secret_key_123!';

// Middleware to verify JWT and authenticate users
const protect = async (req, res, next) => {
  let token;
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    try {
      token = req.headers.authorization.split(' ')[1];
      const decoded = jwt.verify(token, JWT_SECRET);
      req.user = await User.findById(decoded.id).select('-password');
      if (!req.user) {
        return res.status(401).json({ message: 'User not found in system logs' });
      }
      return next();
    } catch (error) {
      return res.status(401).json({ message: 'Invalid authentication credentials' });
    }
  }

  if (!token) {
    return res.status(401).json({ message: 'No authorization token found' });
  }
};

// Middleware to protect admin paths
const adminOnly = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    res.status(403).json({ message: 'Access denied: Admin credentials required' });
  }
};

// Generate JWT token utility
const generateToken = (id) => {
  return jwt.sign({ id }, JWT_SECRET, { expiresIn: '30d' });
};

// @route   POST /api/auth/signup
// @desc    Register a new user
router.post('/signup', async (req, res) => {
  const { name, email, password } = req.body;

  try {
    const userExists = await User.findOne({ email });
    if (userExists) {
      return res.status(400).json({ message: 'User already registered under this email' });
    }

    const user = await User.create({ name, email, password });
    if (user) {
      res.status(201).json({
        token: generateToken(user._id),
        user: {
          _id: user._id,
          name: user.name,
          email: user.email,
          role: user.role
        }
      });
    } else {
      res.status(400).json({ message: 'Invalid registration parameters' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Server registration error: ' + error.message });
  }
});

// @route   POST /api/auth/login
// @desc    Login user & acquire token
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });
    if (user && (await user.matchPassword(password))) {
      res.json({
        token: generateToken(user._id),
        user: {
          _id: user._id,
          name: user.name,
          email: user.email,
          role: user.role
        }
      });
    } else {
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Server authentication error: ' + error.message });
  }
});

// @route   GET /api/auth/profile
// @desc    Get user profile data
router.get('/profile', protect, async (req, res) => {
  res.json(req.user);
});

module.exports = { router, protect, adminOnly };
