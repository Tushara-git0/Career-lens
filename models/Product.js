const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  title: {
    type: String,
    required: true
  },
  price: {
    type: Number,
    required: true,
    default: 0.0
  },
  description: {
    type: String,
    required: true
  },
  image: {
    type: String,
    required: true
  },
  spectrum: {
    type: String
  },
  sensors: {
    type: String
  },
  category: {
    type: String,
    required: true,
    enum: ['circadian', 'cellular', 'cognitive']
  },
  countInStock: {
    type: Number,
    required: true,
    default: 0
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Product', productSchema);
