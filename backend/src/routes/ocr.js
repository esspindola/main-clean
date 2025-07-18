const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { auth } = require('../middleware/auth');

const router = express.Router();

// Configure multer for OCR file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/ocr';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'ocr-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|pdf/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image and PDF files are allowed!'));
    }
  }
});

// Process document with OCR
router.post('/process-document', auth, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // In a real OCR implementation, you would:
    // 1. Send the file to an OCR service (Google Vision, AWS Textract, etc.)
    // 2. Process the results
    // 3. Extract structured data
    
    // For now, simulate OCR processing
    const mockOcrResult = {
      success: true,
      data: {
        documentType: 'invoice',
        vendor: 'Proveedor ABC',
        date: '2024-01-15',
        total: 1250.00,
        items: [
          {
            description: 'Cabinet with Doors',
            quantity: 5,
            unitPrice: 180.00,
            total: 900.00
          },
          {
            description: 'Escritorio Ejecutivo',
            quantity: 2,
            unitPrice: 250.00,
            total: 500.00
          }
        ],
        tax: 187.50,
        subtotal: 1062.50,
        confidence: 0.95
      },
      file: {
        originalName: req.file.originalname,
        filename: req.file.filename,
        path: req.file.path,
        size: req.file.size
      }
    };

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    res.json(mockOcrResult);
  } catch (error) {
    console.error('OCR processing error:', error);
    res.status(500).json({ 
      error: 'Failed to process document',
      details: error.message 
    });
  }
});

// Get OCR processing history
router.get('/history', auth, async (req, res) => {
  try {
    // In a real app, you would store OCR processing history in a database
    const history = [
      {
        id: 1,
        filename: 'invoice-001.pdf',
        documentType: 'invoice',
        processedAt: '2024-01-15T10:30:00Z',
        status: 'completed',
        confidence: 0.95
      },
      {
        id: 2,
        filename: 'receipt-002.jpg',
        documentType: 'receipt',
        processedAt: '2024-01-14T15:45:00Z',
        status: 'completed',
        confidence: 0.88
      }
    ];

    res.json({ history });
  } catch (error) {
    console.error('Get OCR history error:', error);
    res.status(500).json({ error: 'Failed to get OCR history' });
  }
});

// Get OCR processing status
router.get('/status/:jobId', auth, async (req, res) => {
  try {
    const { jobId } = req.params;
    
    // In a real app, you would check the actual processing status
    const status = {
      jobId,
      status: 'completed',
      progress: 100,
      result: {
        documentType: 'invoice',
        vendor: 'Proveedor ABC',
        total: 1250.00
      }
    };

    res.json(status);
  } catch (error) {
    console.error('Get OCR status error:', error);
    res.status(500).json({ error: 'Failed to get OCR status' });
  }
});

// Delete OCR file
router.delete('/file/:filename', auth, async (req, res) => {
  try {
    const { filename } = req.params;
    const filePath = path.join('uploads/ocr', filename);

    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      res.json({ message: 'File deleted successfully' });
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('Delete OCR file error:', error);
    res.status(500).json({ error: 'Failed to delete file' });
  }
});

// Get supported file types
router.get('/supported-types', auth, async (req, res) => {
  try {
    const supportedTypes = {
      images: ['jpeg', 'jpg', 'png', 'gif'],
      documents: ['pdf'],
      maxFileSize: '10MB',
      maxFiles: 1
    };

    res.json(supportedTypes);
  } catch (error) {
    console.error('Get supported types error:', error);
    res.status(500).json({ error: 'Failed to get supported types' });
  }
});

module.exports = router; 