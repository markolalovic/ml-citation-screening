const data = {
  'newArticles': newArticles,
  'falseNegatives': falseNegatives,
  'falsePositives': falsePositives
};

const captions = {
  'newArticles': 'Estimated Relevance for New Articles from April 17, 2020 until February 2, 2021.',
  'falseNegatives': 'Estimated Relevance for False Negatives until April 17, 2020 included in the Risk-Benefit Analysis but not classified as relevant.',
  'falsePositives': 'Estimated Relevance for False Positives until April 17, 2020 classified as relevant but not included in the Risk-Benefit Analysis.'
};

let selected = 'newArticles'; // default table selected

document.getElementById("defaultOpen").click();

console.log(`Window height: ${window.innerHeight}`); // 1054 in window or 1200 in full screen