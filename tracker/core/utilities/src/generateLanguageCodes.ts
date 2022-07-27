/*
 * Copyright 2022 Objectiv B.V.
 */

import axios from 'axios';
import cheerio from 'cheerio';
import fs from 'fs';

/**
 * Script to fetch, parse and generate language codes definitions for LocaleContext Plugin.
 * Execute with `yarn generate:language-codes`. This will compile the script to JS first, then run it.
 */

export const LANGUAGE_CODES_PAGE = 'https://www.loc.gov/standards/iso639-2/php/code_list.php';
export const DESTINATION_FILENAME = '../../plugins/locale-context/src/generated/LanguageCodes.ts';

try {
  axios({
    method: 'GET',
    url: LANGUAGE_CODES_PAGE,
  }).then(({ data }) => {
    const $ = cheerio.load(data);

    // Get the `th` of the `td`s we are interested in
    const tableHeader = $('th:contains("ISO 639-1 Code")');

    // Store its index, so we may use it later to retrieve the correct `td`s
    const columnIndex = tableHeader.index();

    // Get the closest `table`. This is safer then just using `parent`, because we may have a `thead` in the middle
    const parentTable = tableHeader.closest('table');

    // Get all `td`s of the parent `table` with the right index
    const tableCells = parentTable.find(`td:nth-child(${columnIndex + 1})`);

    // Get `td`s contents and start cleaning them up
    const languageCodes = tableCells
      // Get `td` text and trim it
      .map((_, td) => $(td).text().trim())
      // Convert resulting list of values to an array
      .toArray()
      // Filter out empty values
      .filter((languageCode) => languageCode);

    // Sort alphabetically and filter out duplicates
    const filteredAndSortedLanguageCodes = [...new Set(languageCodes.filter((languageCode) => languageCode).sort())];

    fs.writeFileSync(DESTINATION_FILENAME, `/*\n * Copyright ${new Date().getFullYear()} Objectiv B.V.\n */\n\n`);

    fs.appendFileSync(
      DESTINATION_FILENAME,
      `/**\n * Do not edit this module.\n * Run its generator utility instead: core/utilities/src/generateLanguageCodes.ts.\n */\n\n`
    );

    fs.appendFileSync(
      DESTINATION_FILENAME,
      `export const LanguageCodes = [\n  '${filteredAndSortedLanguageCodes.join(`',\n  '`)}'\n];\n`
    );

    console.log(`Language Codes saved to ${DESTINATION_FILENAME}.`);
  });
} catch (err) {
  console.log(`Could not generate Language Codes.`);
  console.error(err);
}
