const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');

const app = express();
app.use(cors());
app.use(bodyParser.json());

/* ================================
   CONNECT MONGODB
================================ */
mongoose.connect(
  process.env.MONGO_URI || 'mongodb://localhost:27017/customer_db',
  { useNewUrlParser: true, useUnifiedTopology: true }
)
.then(() => console.log('MongoDB Connected'))
.catch(err => console.error(err));

/* ================================
   CUSTOMER SCHEMA
================================ */
const customerSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  role: { type: String, default: 'user' },
  address: { type: String },
  password: { type: String, required: true },
  created_at: { type: Date, default: Date.now }
});

/* HASH PASSWORD */
customerSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
  next();
});

const Customer = mongoose.model('Customer', customerSchema);

/* ================================
   REGISTER
================================ */
app.post('/api/customers', async (req, res) => {
  try {
    const { name, email, role, address, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Name, Email, dan Password wajib diisi'
      });
    }

    const customer = new Customer({
      name,
      email,
      role: role || 'user',
      address,
      password
    });

    await customer.save();

    res.status(201).json({
      success: true,
      message: 'Registrasi berhasil',
      data: {
        id: customer._id,
        name: customer.name,
        email: customer.email,
        role: customer.role
      }
    });
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({
        success: false,
        message: 'Email sudah terdaftar'
      });
    }

    res.status(400).json({
      success: false,
      message: error.message
    });
  }
});

/* ================================
   LOGIN
================================ */
app.post('/api/customers/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Email dan Password wajib diisi'
      });
    }

    const customer = await Customer.findOne({ email });
    if (!customer) {
      return res.status(401).json({
        success: false,
        message: 'Email atau Password salah'
      });
    }

    const isMatch = await bcrypt.compare(password, customer.password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Email atau Password salah'
      });
    }

    res.json({
      success: true,
      message: 'Login berhasil',
      data: {
        id: customer._id,
        name: customer.name,
        email: customer.email,
        role: customer.role
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

/* ================================
   GET ALL CUSTOMERS
================================ */
app.get('/api/customers', async (req, res) => {
  try {
    const customers = await Customer.find().select('-password');
    res.json({
      success: true,
      data: customers
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

/* ================================
   GET CUSTOMER BY ID
================================ */
app.get('/api/customers/:id', async (req, res) => {
  try {
    const customer = await Customer.findById(req.params.id).select('-password');

    if (!customer) {
      return res.status(404).json({
        success: false,
        message: 'Customer tidak ditemukan'
      });
    }

    res.json({
      success: true,
      data: customer
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: 'ID tidak valid'
    });
  }
});

/* ================================
   UPDATE CUSTOMER
================================ */
app.put('/api/customers/:id', async (req, res) => {
  try {
    const { name, email, role, address } = req.body;

    const customer = await Customer.findByIdAndUpdate(
      req.params.id,
      { name, email, role, address },
      { new: true, runValidators: true }
    ).select('-password');

    if (!customer) {
      return res.status(404).json({
        success: false,
        message: 'Customer tidak ditemukan'
      });
    }

    res.json({
      success: true,
      message: 'Customer berhasil diupdate',
      data: customer
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message
    });
  }
});

/* ================================
   DELETE CUSTOMER
================================ */
app.delete('/api/customers/:id', async (req, res) => {
  try {
    const customer = await Customer.findByIdAndDelete(req.params.id);

    if (!customer) {
      return res.status(404).json({
        success: false,
        message: 'Customer tidak ditemukan'
      });
    }

    res.json({
      success: true,
      message: 'Customer berhasil dihapus'
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: 'ID tidak valid'
    });
  }
});

/* ================================
   RUN SERVER
================================ */
const PORT = process.env.PORT || 3001;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
});