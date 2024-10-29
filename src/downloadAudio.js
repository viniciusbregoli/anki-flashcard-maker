import fetch from "node-fetch";
import fs from "fs";
import path from "path";
import { parseStringPromise } from "xml2js";
import dotenv from "dotenv";
dotenv.config();
const apiKey = process.env.API_KEY;

const startDirectory = "C:\\";
let folderPath = findFolder(startDirectory, "collection.media");
if (folderPath) {
    folderPath = folderPath.replace(/\\/g, "/"); // Replace backslashes with forward slashes
} else {
    console.log('Folder "collection.media" not found.');
}
console.log(`Path to collection.media: ${folderPath}`);

// Function to download MP3 pronunciation for a given word
export async function downloadPronunciation(word, language = "de", id) {
    try {
        // Define the API endpoint with dynamic word and language
        const apiUrl = `https://apifree.forvo.com/key/${apiKey}/format/xml/action/standard-pronunciation/word/${word}/language/${language}`;

        // Fetch the XML response
        const response = await fetch(apiUrl);
        const xmlString = await response.text();

        // Parse the XML data
        const result = await parseStringPromise(xmlString);

        // Extract the first pathmp3 element
        const pathMp3 = result.items.item[0].pathmp3[0];

        // Fetch the MP3 file
        const mp3Response = await fetch(pathMp3);
        const data = await mp3Response.arrayBuffer();

        // Write the MP3 file to the local filesystem
        fs.writeFileSync(`${folderPath}/${word}_pronunciation.mp3`, Buffer.from(data));

        console.log(`MP3 file for card ${id} downloaded successfully!`);
    } catch (error) {
        console.error("Error downloading pronunciation, no audio available");
    }
}

function findFolder(dir, folderName) {
    try {
        const files = fs.readdirSync(dir, { withFileTypes: true });
        for (const file of files) {
            const fullPath = path.join(dir, file.name);
            if (file.isDirectory()) {
                if (file.name === folderName) {
                    console.log(`Folder found at: ${fullPath}`);
                    return fullPath; // Exit the function once the folder is found
                }
                // Recursively search in subdirectories
                const result = findFolder(fullPath, folderName);
                if (result) return result; // Stop if folder is found
            }
        }
    } catch (err) {
        // Handle permission errors or other read issues silently
    }
    return null; // Return null if the folder is not found in this path
}
