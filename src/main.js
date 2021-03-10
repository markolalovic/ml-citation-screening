const rowsPerPage = 10; // number of rows per page

const data = {
  'newArticles': newArticles,
  'falseNegatives': falseNegatives,
  'falsePositives': falsePositives
};

const captionsTable = {
  'newArticles': '1',
  'falseNegatives': '2',
  'falsePositives': '3'
};

const captionsText = {
  'newArticles': 'Estimated Relevance for New Articles from 17. April, 2020 until 2. February, 2021.',
  'falseNegatives': 'Estimated Relevance for False Negatives until 17. April, 2020 included in the Risk-Benefit Analysis but not classified as relevant.',
  'falsePositives': 'Estimated Relevance for False Positives until 17. April, 2020 classified as relevant but not included in the Risk-Benefit Analysis.'
};

const tableId = { 'newArticles': 1, 'falseNegatives': 2, 'falsePositives': 3 };

initialize();

console.log(`Window height: ${window.innerHeight}`); // 1054 in window or 1200 in full screen