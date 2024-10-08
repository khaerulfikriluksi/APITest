const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');
const axios = require('axios');

//const { spawn } = require('child_process');

//const pythonProcess = spawn('python3', ['bot.py']);

// pythonProcess.stdout.on('data', (data) => {
//     console.log(`stdout: ${data}`);
// });

// pythonProcess.stderr.on('data', (data) => {
//     console.error(`stderr: ${data}`);
// });

// pythonProcess.on('close', (code) => {
//     console.log(`child process exited with code ${code}`);
// });

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const dbConfig = {
  host: '153.92.15.3',
  user: 'u357102271_OTP',
  password: 'FikriLuksi321@@@',
  database: 'u357102271_OTP',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

const pool = mysql.createPool(dbConfig);

const stored_api_key = 'FikriLuksi321@@@'

// Helper function to build WHERE clause
const buildWhereClause = (params) => {
  return Object.keys(params).map(key => `${key} = ${mysql.escape(params[key])}`).join(' AND ');
};

app.get('/webhook', async (req, res) => {
  const api_key = req.query.api_key;
  if (stored_api_key !== api_key) {
      return res.status(401).json({ error: 'unauthorized' });
  }
  
  const query = `
      SELECT A.id as order_id,A.*, B.cost, C.*
      FROM tbl_order AS A
      LEFT JOIN tbl_application AS B ON B.application = A.application
      JOIN tbl_config AS C
      WHERE A.order_status = 'Ongoing' ORDER BY A.id ASC
  `;
  
  try {
      const connection = await pool.getConnection();
      const [results] = await connection.execute(query);
      connection.release();  // Ensure connection is released back to the pool
      
      let affected = 0;
      await Promise.all(results.map(async (row) => {
          try {
              const url = `${row.url_getmessage}?apikey=${row.api_key}&id=${row.order_id}`;
              const response = await axios.get(url, { timeout: 5000 });
              if (response.status == 200) {
                  const responseData = response.data;
                  if(responseData.status == "success") {
                    if (responseData.data.status == 3) {
                      affected += await updateOrder('Done', 'Success', responseData.data.inbox, 'Unread', row.order_id);
                      const url2 = `${row.url_cancel}?apikey=${row.api_key}&id=${row.order_id}&status=1`;
                      await axios.get(url2, { timeout: 5000 });
                    } else if (responseData.data.status == 0) {
                      affected += await updateOrder('Canceled', 'Timeout', '', 'Read', row.order_id);
                    } else if (responseData.data.status == 1) {
                      affected += await updateOrder('Done', 'Success', responseData.data.inbox, 'Unread', row.order_id);
                    }
                  }                  
              } else {
                  console.error(`Failed GET request Webhook status code: ${response.status}`);
              }
          } catch (error) {
              console.error(`Error making GET request Webhook:`, error.message);
          }
      }));
    return res.status(200).json({
      "status":"success",
      "data":affected,
      "message":"Webhook executed successfully"
    });
  } catch (error) {
      console.error('Error executing query:', error);
      return res.status(200).json({
        "status":"error",
        "data":0,
        "message":"Webhook executed failed"
      });
  }
});

app.get('/cancel-order', async(req, res) => {
  const order_id = req.query.order_id;
  const query = `
      SELECT A.id as order_id,A.*, B.cost, C.*
      FROM tbl_order AS A
      LEFT JOIN tbl_application AS B ON B.application = A.application
      JOIN tbl_config AS C
      WHERE  A.id = '${order_id}' AND A.order_status = 'Ongoing'
  `;
  
  try {
      const connection = await pool.getConnection();
      const [results] = await connection.execute(query);
      connection.release();

      if(results.length == 0) {
        return res.status(200).json({
          "status":"error",
          "message":"Order tidak ditemukan"
        });
      }

      const row = results[0];

      console.log(`'${row.username}' canceling '${row.application}' with number '${row.number}'`);

      const url = `${row.url_getmessage}?apikey=${row.api_key}&id=${row.order_id}`;
        const response = await axios.get(url, { timeout: 5000 });
        if (response.status === 200) {
            const responseData = response.data;
            if(responseData.status == "success") {
              if (responseData.data.status == 3) {
                console.log(`'${row.username}' canceling '${row.application}' with number '${row.number}' Success`);
                return res.status(200).json({
                  "status":"success",
                  "message":"Order tidak dibatalkan, OTP sudah diterima"
                });
              } else {
                const url2 = `${row.url_cancel}?apikey=${row.api_key}&id=${row.order_id}&status=0`;
                await axios.get(url2, { timeout: 5000 });
                console.log(`'${row.username}' canceling '${row.application}' with number '${row.number}' Success`);
                return res.status(200).json({
                  "status":"success",
                  "message":"Order berhasil dibatalkan"
                });
              }
            }                  
        } else {
          const url2 = `${row.url_cancel}?apikey=${row.api_key}&id=${row.order_id}&status=0`;
          await axios.get(url2, { timeout: 5000 });
          console.log(`'${row.username}' canceling '${row.application}' with number '${row.number}' Success`);
          return res.status(200).json({
            "status":"success",
            "message":"Order berhasil dibatalkan"
          });
        }
  } catch (error) {
      console.error('Error executing query:', error);
      // console.log(`'${row.username}' canceling '${row.application}' with number '${row.number}' Failed`);
      return res.status(200).json({
        "status":"error",
        "message":"Order gagal, silahkan coba beberapa saat lagi."
      });
  }
});

app.post('/create-order', async (req, res) => {
  const { application_id, username } = req.body;

  try {
    const connection = await pool.getConnection();
    const [resQ] = await connection.execute(`SELECT A.*,A.id as app_id,B.*,C.quota FROM tbl_application AS A JOIN tbl_config AS B JOIN tbl_customer AS C WHERE A.id='${application_id}'`);
    connection.release();
    if (resQ.length == 0) {
      return res.status(200).json({
        "status":"error",
        "message":"Application not found"
      });
    }

    const row = resQ[0];

    if (row.quota < row.cost) {
      return res.status(200).json({
        "status":"error",
        "message":"Order gagal, silahkan coba beberapa saat lagi."
      });
    }

    const currentDateTime = new Date(new Date().getTime() + (7 * 60 * 60 * 1000)).toISOString().replace('T', ' ').substring(0, 19);

    //SendAPI timeout 5 detik
    try {
      const response = await axios.get(`${row.url_order}?apikey=${row.api_key}&service=${application_id}&operator=${row.operator}&country=${row.country_id}`, {timeout: 10000});
      if (response.status === 200) {
          const responseData = response.data;
          if(responseData.status == "success") {
            try {
              console.log(`'${username}' Order '${row.application}' with number '${responseData.number}'`);
              const query_insert = `INSERT INTO tbl_order (id, username, application, order_time, number, status, order_status, read_status) 
                            VALUES ('${responseData.id}','${username}', '${row.application}', '${currentDateTime}', '${responseData.number}', 'Waiting Sms', 'Ongoing', 'New')`;
              const connection = await pool.getConnection();
              const [insert_status] = await connection.execute(query_insert);
              connection.release();
              if(insert_status) {            
                return res.status(200).json(responseData);
              } else {
                return res.status(200).json({
                  "status":"error",
                  "message":"Order gagal, silahkan coba beberapa saat lagi."
                });
              }
            } catch (error) {
              console.log(`'${username}' Order Failed`);
                console.error('Error executing query:', error);
                return res.status(200).json({
                  "status":"error",
                  "message":"Order gagal, silahkan coba beberapa saat lagi."
                });
            }
          } else {
            if(responseData.message == "saldo tidak mencukupi") {
              console.log(`'${username}' Order Failed, out of balance`);
              return res.status(200).json({
                "status":"error",
                "message":"Order gagal, Stock kartu habis, silahkan hubungi CS terkait kendala ini."
              });
            } else {
              return res.status(200).json(responseData);
            }
          }                 
      } else {
        console.log(`'${username}' Order Failed, Respond server != 200`);
          console.error(`Failed GET request Webhook status code: ${response.status}`);
          return res.status(200).json({
            "status":"error",
            "message":"Order gagal, silahkan coba beberapa saat lagi."
          });
      } 
    } catch (error) {
      console.log(`'${username}' Order Failed, Error Send GET ${error}`);
      console.error('Error Send GET:', error);
      return res.status(200).json({
        "status":"error",
        "message":"Order gagal, silahkan coba beberapa saat lagi."
      });
    }
  } catch (error) {
    console.error('Error getting connection:', error);
    return res.status(200).json({
      "status":"error",
      "message":"Order gagal, silahkan coba beberapa saat lagi."
    });
  }
});

const updateOrder = async (order_status, status, message, read_status, id) => {
  const query = `UPDATE tbl_order SET order_status = ?, status = ?, message = ?, read_status = ? WHERE id = ?`;
  try {
      const connection = await pool.getConnection();
      const [results] = await connection.execute(query, [order_status, status, message, read_status, id]);
      connection.release();
      return results.affectedRows;
  } catch (err) {
      console.error('Error updating order:', err);
      return 0
  }
};

// Route 1
app.get('/show-orders', async (req, res) => {
  const params = req.query;
  const whereClause = buildWhereClause(params);
  const query = `SELECT A.*, B.cost, C.email FROM tbl_order AS A LEFT JOIN tbl_application AS B ON B.application = A.application LEFT JOIN tbl_customer AS C ON C.username = A.username WHERE ${whereClause} ORDER BY A.id DESC`;
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query);
    connection.release();
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
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query);
    connection.release();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 3
app.get('/applications', async (req, res) => {
  const query = 'SELECT * FROM tbl_application';
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query);
    connection.release();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route 5
app.put('/update-markread', async (req, res) => {
  const id = req.body.id;
  const query = `UPDATE tbl_order SET read_status = 'Read' WHERE id = '${id}' AND order_status = 'Done'`;
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query);
    connection.release();
    if(results) {
      return res.status(200).json({
        "status":"success",
        "message":"Mark as read success"
      });  
    } else {
      return res.status(200).json({
        "status":"error",
        "message":"Mark as read failed, please try again later."
      });
    }    
  } catch (err) {
    return res.status(200).json({
      "status":"error",
      "message":"Mark as read failed, please try again later."
    });
  }
});

// Route 6
app.post('/insert-customer', async (req, res) => {
  const { username, password, quota, email } = req.body;
  const query = 'INSERT IGNORE INTO tbl_customer (username, password, quota, email) VALUES (?, ?, ?, ?)';
  const values = [username, password, quota, email];
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query, values);
    connection.release();
    return res.status(200).json({
      "status":"success",
      "message":"Insert success"
    });
  } catch (err) {
    return res.status(200).json({
      "status":"error",
      "message":"Insert customer failed, please try again later."
    });
  }
});

// Route 7
app.put('/update-customer', async (req, res) => {
  const { username, password, quota } = req.body;
  const query = 'UPDATE tbl_customer SET password = ?, quota = ? WHERE username = ?';
  const values = [password, quota, username];
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query, values);
    connection.release();
    
    // Check if any rows were affected (i.e., updated)
    if (results.affectedRows === 0) {
      return res.status(200).json({
        "status": "error",
        "message": "Customer not found"
      });
    }
    return res.status(200).json({
      "status":"success",
      "message":"Update success"
    });
  } catch (err) {
    return res.status(200).json({
      "status":"error",
      "message":"Update customer failed, please try again later."
    });
  }
});

//Route 8
app.get('/all-customer', async (req, res) => {
  const query = 'SELECT * FROM tbl_customer';
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query);
    connection.release();
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

//Route 9
app.delete('/delete-customer', async (req, res) => {
  const { username } = req.body;
  const query = 'DELETE FROM tbl_customer WHERE username = ?';
  const values = [username];
  
  try {
    const connection = await pool.getConnection();
    const [results] = await connection.execute(query, values);
    connection.release();
    
    // Check if any rows were affected (i.e., deleted)
    if (results.affectedRows === 0) {
      return res.status(200).json({
        "status": "error",
        "message": "Customer not found"
      });
    }
    return res.status(200).json({
      "status": "success",
      "message": "Delete success"
    });
  } catch (err) {
    return res.status(200).json({
      "status": "error",
      "message": "Delete customer failed, please try again later."
    });
  }
});


// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    status: 'error',
    message: 'Something went wrong! Please try again later.'
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
