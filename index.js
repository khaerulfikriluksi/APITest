const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');

const app = express();
app.use(bodyParser.json());

const dbConfig = {
  host: '153.92.15.3',
  user: 'u357102271_OTP',
  password: 'FikriLuksi321@@@',
  database: 'u357102271_OTP'
};

// Helper function to build WHERE clause
const buildWhereClause = (params) => {
  return Object.keys(params).map(key => `${key} = ${mysql.escape(params[key])}`).join(' AND ');
};

// Route 1
app.get('/orders', async (req, res) => {
  const params = req.query;
  const whereClause = buildWhereClause(params);
  const query = `SELECT A.*, B.cost, C.email FROM tbl_order AS A LEFT JOIN tbl_application AS B ON B.application = A.application LEFT JOIN tbl_customer AS C ON C.username = A.username WHERE ${whereClause}`;
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [results] = await connection.execute(query);
    await connection.end();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 2
app.get('/customers-config', async (req, res) => {
  const params = req.query;
  const whereClause = buildWhereClause(params);
  const query = `SELECT A.*, B.* FROM tbl_customer AS A JOIN tbl_config AS B WHERE ${whereClause}`;
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [results] = await connection.execute(query);
    await connection.end();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 3
app.get('/applications', async (req, res) => {
  const query = 'SELECT * FROM tbl_application';
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [results] = await connection.execute(query);
    await connection.end();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 4
app.post('/order', async (req, res) => {
  const { id, username, application, order_time, number, status, order_status, read_status } = req.body;
  const query = 'INSERT INTO tbl_order (id, username, application, order_time, number, status, order_status, read_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)';
  const values = [id, username, application, order_time, number, status, order_status, read_status];
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [results] = await connection.execute(query, values);
    await connection.end();
    res.json({ success: true, results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 5
app.put('/order', async (req, res) => {
  const { data, id } = req.body;
  const setClause = Object.keys(data).map(key => `${key} = ${mysql.escape(data[key])}`).join(', ');
  const query = `UPDATE tbl_order SET ${setClause} WHERE id = ${mysql.escape(id)}`;
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [results] = await connection.execute(query);
    await connection.end();
    res.json({ success: true, results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 6
app.post('/customer', async (req, res) => {
  const { username, password, quota, email } = req.body;
  const query = 'INSERT INTO tbl_customer (username, password, quota, email) VALUES (?, ?, ?, ?)';
  const values = [username, password, quota, email];
  
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [results] = await connection.execute(query, values);
    await connection.end();
    res.json({ success: true, results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
