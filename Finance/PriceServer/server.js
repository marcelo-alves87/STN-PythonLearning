import express from "express";
import fs from "fs";
import { default as mongodb } from 'mongodb';
let MongoClient = mongodb.MongoClient;
const client = new MongoClient('mongodb://localhost:27017/mongodb')
await client.connect()
const db = client.db()
import { execFile } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

let isRunning = false;


function deleteLayoutFiles() {
    const directory = 'C:\\Users\\marce\\Downloads\\';
    const regex = /^SBSP3_layout_(?:\s?\(\d+\))?\.json$/;

    fs.readdir(directory, (err, files) => {
        if (err) {
            console.error('Error reading directory:', err);
            return;
        }

        files.forEach(file => {
            if (regex.test(file)) {
                const filePath = path.join(directory, file);
                fs.unlink(filePath, (err) => {
                    if (err) {
                        console.error(`Error deleting file ${file}:`, err);
                    } else {
                        //console.log(`Deleted file: ${file}`);
                    }
                });
            }
        });
    });
}


deleteLayoutFiles();


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

// New endpoint to fetch data from 'prices_interpretation' collection based on labels
app.get('/interpretation', (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
    res.setHeader('Access-Control-Allow-Credentials', false);
	res.setHeader('Content-Type', 'application/json; charset=utf-8');
	
	if (isRunning) {
		res.status(429).send({ error: "Interpreter is busy. Please try again shortly." });
		return;
	}

    const { DensitySpread_Label, Liquidity_Label, Pressure_Label, AgentImbalance_Label } = req.query;

    if (!DensitySpread_Label || !Liquidity_Label || !Pressure_Label || !AgentImbalance_Label) {
        res.status(400).send({ error: "Missing required query parameters." });
        return;
    }

    const args = [
        path.join(__dirname, "..", "ChatGPTDetails.py"),
        `"${DensitySpread_Label}"`,
		`"${Liquidity_Label}"`,
		`"${Pressure_Label}"`,
		`"${AgentImbalance_Label}"`
    ];
	
	isRunning = true; // 🔒 trava

    execFile("python", args, { cwd: process.cwd(), encoding: "utf8" }, (error, stdout, stderr) => {
		isRunning = false; // 🔓 destrava quando terminar
		
        if (error) {
            console.error("❌ Python exec error:", error);
            res.status(500).send({ error: "Failed to execute Python script." });
            return;
        }

        try {
            const parsed = JSON.parse(stdout);  // ensure it's a valid object
			const result = JSON.stringify(parsed);
            res.end(result);
        } catch (e) {
            console.error("❌ Failed to parse Python output:", stdout);
            res.status(500).send({ error: "Invalid response from Python script." });
        }
    });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});


