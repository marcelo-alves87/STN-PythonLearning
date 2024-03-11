import express from "express";
import fs from "fs";

const path = 'btc-181123_2006-181124_0105.json'
const app = express();
const port = 3000;

app.get('/btc-181123_2006-181124_0105.json', (req, res) => {
  // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Content-Type', 'application/json');
    fs.readFile(path, 'utf8', (err, file) => {

		// check for any errors
		if (err) {
			console.error('Error while reading the file:', err)
			return
		}
		try {
			const data = JSON.parse(file)
			res.end(JSON.stringify(data));
			// output the parsed data
			//console.log(data)
		} catch (err) {
			console.error('Error while parsing JSON data:', err)
		}
	})
  
  //res.send('Welcome to my server!');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});


