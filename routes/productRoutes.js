const express = require('express');
const router = express.Router();
const Product = require('../models/Product');
const { protect, adminOnly } = require('./authRoutes');

// @route   GET /api/products
// @desc    Fetch products with optional search and category filters
router.get('/', async (req, res) => {
  try {
    const { search, category } = req.query;
    let query = {};

    if (search) {
      query.title = { $regex: search, $options: 'i' };
    }

    if (category && category !== 'all') {
      query.category = category;
    }

    const products = await Product.find(query);
    res.json(products);
  } catch (error) {
    res.status(500).json({ message: 'Catalog retrieval error: ' + error.message });
  }
});

// @route   GET /api/products/:id
// @desc    Fetch a single product by its custom string ID
router.get('/:id', async (req, res) => {
  try {
    const product = await Product.findOne({ id: req.params.id });
    if (product) {
      res.json(product);
    } else {
      res.status(404).json({ message: 'Product not found in inventory' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Database query error: ' + error.message });
  }
});

// @route   POST /api/products
// @desc    Create a product (Admin only)
router.post('/', protect, adminOnly, async (req, res) => {
  const { id, title, price, description, image, spectrum, sensors, category, countInStock } = req.body;

  try {
    const productExists = await Product.findOne({ id });
    if (productExists) {
      return res.status(400).json({ message: 'Product code already registered' });
    }

    const product = await Product.create({
      id, title, price, description, image, spectrum, sensors, category, countInStock
    });

    res.status(201).json(product);
  } catch (error) {
    res.status(500).json({ message: 'Error registering product: ' + error.message });
  }
});

// @route   PUT /api/products/:id
// @desc    Update a product (Admin only)
router.put('/:id', protect, adminOnly, async (req, res) => {
  try {
    const product = await Product.findOne({ id: req.params.id });

    if (product) {
      product.title = req.body.title || product.title;
      product.price = req.body.price !== undefined ? req.body.price : product.price;
      product.description = req.body.description || product.description;
      product.spectrum = req.body.spectrum || product.spectrum;
      product.sensors = req.body.sensors || product.sensors;
      product.category = req.body.category || product.category;
      product.countInStock = req.body.countInStock !== undefined ? req.body.countInStock : product.countInStock;

      const updatedProduct = await product.save();
      res.json(updatedProduct);
    } else {
      res.status(404).json({ message: 'Product not found in catalog' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Error updating product: ' + error.message });
  }
});

// @route   DELETE /api/products/:id
// @desc    Remove a product from inventory (Admin only)
router.delete('/:id', protect, adminOnly, async (req, res) => {
  try {
    const result = await Product.deleteOne({ id: req.params.id });
    if (result.deletedCount > 0) {
      res.json({ message: 'Product removed successfully' });
    } else {
      res.status(404).json({ message: 'Product not found' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Error deleting product: ' + error.message });
  }
});

module.exports = router;
