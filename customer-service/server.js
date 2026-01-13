const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/customer_db')
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.log(err));

// Customer Schema
const customerSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  phone: { type: String, required: true },
  address: String,
  created_at: { type: Date, default: Date.now }
});

const Customer = mongoose.model('Customer', customerSchema);

// Routes
// Get all customers
app.get('/api/customers', async (req, res) => {
  try {
    const customers = await Customer.find();
    res.json({ success: true, data: customers });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get customer by ID
app.get('/api/customers/:id', async (req, res) => {
  try {
    const customer = await Customer.findById(req.params.id);
    if (!customer) {
      return res.status(404).json({ success: false, message: 'Customer not found' });
    }
    res.json({ success: true, data: customer });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Create customer
app.post('/api/customers', async (req, res) => {
  try {
    const customer = new Customer(req.body);
    await customer.save();
    res.status(201).json({ success: true, data: customer });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

// Update customer
app.put('/api/customers/:id', async (req, res) => {
  try {
    const customer = await Customer.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!customer) {
      return res.status(404).json({ success: false, message: 'Customer not found' });
    }
    res.json({ success: true, data: customer });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

// Delete customer
app.delete('/api/customers/:id', async (req, res) => {
  try {
    const customer = await Customer.findByIdAndDelete(req.params.id);
    if (!customer) {
      return res.status(404).json({ success: false, message: 'Customer not found' });
    }
    res.json({ success: true, message: 'Customer deleted' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'Customer Service is running' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Customer Service running on port ${PORT}`);
});
