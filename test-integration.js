

const https = require('https');
const http = require('http');

// Test endpoints
const tests = [
  {
    name: 'Node.js Backend Health',
    url: 'http://localhost:4444/health',
    expected: 'health'
  },
  {
    name: 'OCR Backend Health', 
    url: 'http://localhost:5000/health',
    expected: 'OCR Backend'
  },
  {
    name: 'OCR Debug Endpoint',
    url: 'http://localhost:5000/api/v1/invoice/debug',
    expected: 'model_status'
  },
  {
    name: 'OCR Supported Formats',
    url: 'http://localhost:5000/api/v1/invoice/supported-formats',
    expected: 'supported_formats'
  },
  {
    name: 'Frontend (React)',
    url: 'http://localhost:5173',
    expected: 'html'
  }
];

console.log('🧪 Integration Test Suite');
console.log('========================');

async function testEndpoint(test) {
  return new Promise((resolve) => {
    const client = test.url.startsWith('https') ? https : http;
    
    const timeout = setTimeout(() => {
      console.log(`❌ ${test.name} - TIMEOUT`);
      resolve({ success: false, error: 'timeout' });
    }, 5000);

    client.get(test.url, (res) => {
      clearTimeout(timeout);
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const success = data.toLowerCase().includes(test.expected.toLowerCase());
          if (success) {
            console.log(`✅ ${test.name} - OK`);
            resolve({ success: true, status: res.statusCode });
          } else {
            console.log(`❌ ${test.name} - Content mismatch`);
            resolve({ success: false, error: 'content mismatch' });
          }
        } catch (error) {
          console.log(`❌ ${test.name} - Parse error`);
          resolve({ success: false, error: error.message });
        }
      });
    }).on('error', (error) => {
      clearTimeout(timeout);
      console.log(`❌ ${test.name} - ${error.code || error.message}`);
      resolve({ success: false, error: error.message });
    });
  });
}

async function runTests() {
  console.log('Starting tests...\n');
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    const result = await testEndpoint(test);
    if (result.success) {
      passed++;
    } else {
      failed++;
    }
    
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  console.log('\n📊 Test Results:');
  console.log(`   ✅ Passed: ${passed}`);
  console.log(`   ❌ Failed: ${failed}`);
  console.log(`   📈 Success Rate: ${((passed / tests.length) * 100).toFixed(1)}%`);
  
  if (failed === 0) {
    console.log('\n🎉 All services are running correctly!');
    console.log('📝 You can now:');
    console.log('   1. Open http://localhost:5173 for the frontend');
    console.log('   2. Test OCR at http://localhost:5173 (OCR section)');
    console.log('   3. Check API docs at http://localhost:5000/docs/');
  } else {
    console.log('\n⚠️  Some services are not responding.');
    console.log('🔧 Make sure all services are started:');
    console.log('   • Frontend: npm run dev (in frontend folder)');
    console.log('   • Node Backend: npm start (in backend folder)'); 
    console.log('   • OCR Backend: python run.py (in backend-ocr folder)');
  }
}

// Start tests
runTests().catch(console.error);