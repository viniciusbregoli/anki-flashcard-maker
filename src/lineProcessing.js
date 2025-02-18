import fs from "fs"; // File system module, used to read and write files
import Reverso from "reverso-api"; // Reverso API module, used to translate words
import { downloadPronunciation } from "./downloadAudio.js";
const writeStream = fs.createWriteStream("./src/output.txt");
let cards = [];
const reverso = new Reverso();

// Function to process each line
export async function processLines(linesArray) {
    for (let i = 0; i < linesArray.length; i++) {
        await processLine(capitalizeString(linesArray[i]), i); // Await each line processing to ensure it's synchronous
    }

    cards.forEach((card) => {
        // Check if the context array has at least one element
        if (card.context.length > 0) {
            writeStream.write(
                `[sound:${card.source.replace(/\s+/g, "_")}_pronunciation.mp3] ${card.source} <br> <i>${
                    card.context[0]["german"]
                }</i>; ${card.translation.join(", ")} <br> <i>${card.context[0]["english"]}</i> ` + "\n"
            );
        } else {
            writeStream.write(
                `[sound:${card.source.replace(/\s+/g, "_")}_pronunciation.mp3] ${card.source} <br> ${card.translation.join(", ")} ` + "\n"
            );
        }
    });
}

async function processLine(line, index) {
    let context = [];
    let translation = [];
    let attempt = 0;
    let maxRetries = 5;
    let success = false;

    while (attempt < maxRetries && !success) {
        try {
            const response = await reverso.getTranslation(line.toLowerCase(), "german", "english");
            await downloadPronunciation(line.replace(/\s+/g, "_"), "de", index);
            if (!response.translations) {
                console.error(`Invalid response for line ${(index, line)}: missing translations, trying again...`);
                attempt++;
                continue;
            } else {
                translation.push(...response.translations.slice(1, 4));
                console.log(`Successfull translation for word ${line}`);
                success = true;
            }

            if (response.context && response.context.examples) {
                for (let j = 0; j < 3; j++) {
                    if (response.context.examples[j]) {
                        context.push({
                            english: response.context.examples[j]["target"].replace(/;/g, ","),
                            german: response.context.examples[j]["source"].replace(/;/g, ","),
                        });
                    }
                }
                let newCard = {
                    id: index,
                    source: line,
                    translation: translation,
                    context: context,
                };
                cards.push(newCard);
            } else {
                console.error(`Invalid response for line ${index}: missing examples`);
                continue;
            }
        } catch (error) {
            console.error(`Error processing line ${index}:`, error);
            attempt++;
        }
    }
}

function capitalizeString(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}
