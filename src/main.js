import fs from "fs"; // File system module, used to read and write files
import { processLines } from "./lineProcessing.js";

let linesArray = [];

// read the input file
try {
    const data = fs.readFileSync("./src/input.txt", "utf8");
    linesArray = data.split("\n");
    console.log(linesArray);
} catch (err) {
    console.error(err);
}

// process each line
processLines(linesArray).catch((error) => {
    console.error("Error processing cards:", error);
});
