# Reverso Anki

Reverso Anki is a Node.js application that processes a list of German words, translates them to English using the Reverso API, and downloads their pronunciation. The results are written to an output file in a format suitable for Anki flashcards.

## Table of Contents

- [Reverso Anki](#reverso-anki)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/viniciusbregoli/reverso-anki.git
    cd reverso-anki
    ```

2. Install the dependencies:
    ```sh
    npm install
    ```

3. Create a `.env` file in the root directory and add your API key:
    ```env
    API_KEY=your_api_key_here
    ```

## Usage

1. Prepare your input file:
    - Create a file named `input.txt` in the `src` directory.
    - Add the German words you want to process, each on a new line.

2. Run the application:
    ```sh
    node src/reverso.js
    ```

3. Check the `output.txt` file in the `src` directory for the results.

## Configuration

- **API Key**: The application uses the Forvo API to download pronunciations. You need to provide your API key in the `.env` file.
- **Input File**: The input file (`input.txt`) should be placed in the `src` directory and contain the German words to be processed.
- **Output File**: The results will be written to `output.txt` in the `src` directory.

