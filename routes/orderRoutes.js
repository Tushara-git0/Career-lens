const express = require('express');
const router = express.Router();
const Order = require('../models/Order');
const Product = require('../models/Product');
const { protect, adminOnly } = require('./authRoutes');

// @route   POST /api/orders
// @desc    Submit a new order and decrement product stock levels
router.post('/', protect, async (req, res) => {
  const { orderItems, totalPrice } = req.body;

  if (!orderItems || orderItems.length === 0) {
    return res.status(400).json({ message: 'No item protocols in order payload' });
  }

  try {
    // Verify stock and decrement values
    for (const item of orderItems) {
      const product = await Product.findOne({ id: item.product });
      if (!product) {
        return res.status(404).json({ message: `Product ${item.title} not found in inventory` });
      }
      if (product.countInStock < item.quantity) {
        return res.status(400).json({ message: `Insufficient inventory for ${item.title}` });
      }
      
      // Decrement stock
      product.countInStock -= item.quantity;
      await product.save();
    }

    const order = new Order({
      user: req.user._id,
      orderItems,
      totalPrice
    });

    const createdOrder = await order.save();
    res.status(201).json(createdOrder);
  } catch (error) {
    res.status(500).json({ message: 'Order processing failed: ' + error.message });
  }
});

// @route   GET /api/orders/myorders
// @desc    Retrieve logged-in user's orders
router.get('/myorders', protect, async (req, res) => {
  try {
    const orders = await Order.find({ user: req.user._id }).sort({ createdAt: -1 });
    res.json(orders);
  } catch (error) {
    res.status(500).json({ message: 'Failed to retrieve user orders: ' + error.message });
  }
});

// @route   GET /api/orders/all
// @desc    Get all orders (Admin only)
router.get('/all', protect, adminOnly, async (req, res) => {
  try {
    const orders = await Order.find({}).populate('user', 'name email').sort({ createdAt: -1 });
    res.json(orders);
  } catch (error) {
    res.status(500).json({ message: 'Failed to retrieve administrative order log: ' + error.message });
  }
});

// @route   PUT /api/orders/:id/status
// @desc    Update shipping status of an order (Admin only)
router.put('/:id/status', protect, adminOnly, async (req, res) => {
  const { status } = req.body;

  try {
    const order = await Order.findById(req.params.id);
    if (order) {
      order.status = status || order.status;
      const updatedOrder = await order.save();
      res.json(updatedOrder);
    } else {
      res.status(404).json({ message: 'Order record not found' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Status update failed: ' + error.message });
  }
});

module.exports = router;
