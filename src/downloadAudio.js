import fetch from "node-fetch";
import fs from "fs";
import path from "path";
import { parseStringPromise } from "xml2js";
import dotenv from "dotenv";
dotenv.config();
const apiKey = process.env.API_KEY;

// Function to download MP3 pronunciation for a given word
export async function downloadPronunciation(word, language = "de", id) {
    const folderPath = "/home/bregoli/.local/share/Anki2/User 1/collection.media";
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
