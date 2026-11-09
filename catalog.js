export const repo = 'DanishAliSyed/Danish_Profile';
export const branch = 'master';
export const github = `https://github.com/${repo}/blob/${branch}/projects/`;
export const raw = `https://raw.githubusercontent.com/${repo}/${branch}/projects/`;

export const metadata = {
  'loan-portfolio-power-bi': { topic: 'Finance', tools: ['Power BI'], featured: 1, artifact: ['PowerBI_Report_Danish.pdf', 'Dashboard PDF'], description: 'Follow requested funding through approval and disbursement, then review recoveries separately. Includes the original dashboard export and a synthetic walkthrough.' },
  'retail-profitability-tableau': { topic: 'Retail & customers', tools: ['Tableau'], featured: 2, image: ['dashboard-1.png', 'Original Tableau dashboard thumbnail with a state profit map and category sales'], artifact: ['retail-profitability.twb', 'Tableau workbook'], description: 'See where sales and profit tell different stories. Includes both original Tableau dashboard previews and the workbook.' },
  'supply-chain-sql': { topic: 'Supply chain & operations', tools: ['SQL', 'MySQL'], featured: 3 },
  'bitcoin-network-activity': { topic: 'Finance', tools: ['PySpark', 'Spark SQL', 'Python'], featured: 4, image: ['dashboard.png', 'Bitcoin confirmations and fees over five UTC days'] },
  'namma-yatri-power-bi': { topic: 'Supply chain & operations', tools: ['Power BI'], featured: 5, artifact: ['dashboard.pdf', 'Dashboard PDF'] },
  'credit-default': { topic: 'Finance', tools: ['Python', 'Machine learning'], featured: 6 },
  'media-viewership-forecasting': { topic: 'Forecasting & modelling', tools: ['Python', 'Forecasting'] },
  'telecom-churn': { topic: 'Retail & customers', tools: ['Python', 'Machine learning'] },
  'retail-orders-spark': { topic: 'Retail & customers', tools: ['Spark SQL', 'PySpark'] },
  'customer-retention-ab-test': { topic: 'Retail & customers', tools: ['SQL', 'Python', 'A/B testing'] },
  'nz-export-recovery': { topic: 'Supply chain & operations', tools: ['Power BI'] },
  'bank-campaign-analytics': { topic: 'Finance', tools: ['SQL', 'Python'] },
  'crop-insurance-mysql': { topic: 'Finance', tools: ['SQL', 'MySQL'] },
  'nyc-taxi-analysis': { topic: 'Supply chain & operations', tools: ['Python', 'EDA'] },
  'employee-retention': { topic: 'Forecasting & modelling', tools: ['Python', 'Machine learning'] },
  'delivery-time-estimation': { topic: 'Supply chain & operations', tools: ['Python', 'Regression'] },
  'customer-behaviour-spark': { topic: 'Retail & customers', tools: ['PySpark', 'RFM'] },
  'retail-customer-clustering': { topic: 'Retail & customers', tools: ['Python', 'Clustering'] },
  'multiple-linear-regression': { topic: 'Forecasting & modelling', tools: ['Python', 'Regression'] },
  'simple-linear-regression': { topic: 'Forecasting & modelling', tools: ['Python', 'Regression'] },
  'spark-sql': { topic: 'Data engineering', tools: ['PySpark', 'Spark SQL'] }
};

export function parseCatalog(markdown) {
  const projects = new Map();
  for (const line of markdown.split(/\r?\n/)) {
    const row = /^\|\s*\[([^\]]+)\]\(([a-z0-9][a-z0-9-]*)\/README\.md\)\s*\|\s*(.*?)\s*\|\s*$/.exec(line);
    if (!row) continue;
    const [, title, slug, description] = row;
    const details = Object.hasOwn(metadata, slug) ? metadata[slug] : {};
    if (!projects.has(slug)) projects.set(slug, {
      slug, title: title.replaceAll('\\|', '|'), description, topic: 'Other projects', tools: [],
      ...details,
    });
  }
  return [...projects.values()];
}

export function selectProjects(projects, {query, topic, sort}) {
  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  const results = projects.filter(p => {
    const haystack = [p.title, p.description, p.topic, ...p.tools].join(' ').toLowerCase();
    return (!topic || p.topic === topic) && terms.every(term => haystack.includes(term));
  });
  if (sort === 'az') results.sort((a, b) => a.title.localeCompare(b.title));
  if (sort === 'featured') results.sort((a,b) => (a.featured ?? Infinity) - (b.featured ?? Infinity));
  return results;
}
