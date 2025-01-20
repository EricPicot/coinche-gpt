module.exports = {
  allowedHosts: [
    'localhost',
    '.localhost',
    '127.0.0.1'
  ],
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization'
  },
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      pathRewrite: { '^/api': '' },
      secure: false,
      changeOrigin: true
    }
  }
}; 