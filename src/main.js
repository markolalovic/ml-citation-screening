const rowsPerPage = 9; // number of rows per page

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
  'newArticles': 'Estimated Relevance for New Articles from April 17, 2020 until February 2, 2021.',
  'falseNegatives': 'Estimated Relevance for False Negatives until April 17, 2020 included in the Risk-Benefit Analysis but not classified as relevant.',
  'falsePositives': 'Estimated Relevance for False Positives until April 17, 2020 classified as relevant but not included in the Risk-Benefit Analysis.'
};

const tableId = { 'newArticles': 1, 'falseNegatives': 2, 'falsePositives': 3 };

initialize();
addTime();

console.log(`Window height: ${window.innerHeight}`); // 1054 in window or 1200 in full screen