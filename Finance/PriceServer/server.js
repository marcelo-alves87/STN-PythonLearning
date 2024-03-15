import express from "express";
import fs from "fs";
import { default as mongodb } from 'mongodb';

let MongoClient = mongodb.MongoClient;
const client = new MongoClient('mongodb://localhost:27017/mongodb')
await client.connect()
const db = client.db()

const path = 'btc-181123_2006-181124_0105.json'
const app = express();
const port = 3000;





app.get('/*.json', (req, res) => {
	
  // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', false);
    res.setHeader('Content-Type', 'application/json');
	
	// Connect to collection 
	const collection = db.collection("prices"); 
	
	// Count the total documents
	/*collection.countDocuments({ ativo : req.query.ativo, time: { $gt : Number(req.query.time) }  }).then((count_documents) => {
		console.log(count_documents);
	}).catch((err) => {
		console.log(err.Message);
	})*/
	collection.find({ ativo : req.query.ativo, time: { $gt : new Date(req.query.time) }  }).sort({time: 1}).toArray().then((data) => {
		res.end(JSON.stringify(data));
	}).catch((err) => {
		console.log(err.Message);	
	});
	
	
    /*fs.readFile(path, 'utf8', (err, file) => {

		// check for any errors
		if (err) {
			console.error('Error while reading the file:', err)
			return
		}
		try {
			var data = JSON.parse(file);								
			res.end(JSON.stringify(data));
			
		} catch(err) {
			res.end();
		}	
	})*/
  
  //res.send('Welcome to my server!');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});


