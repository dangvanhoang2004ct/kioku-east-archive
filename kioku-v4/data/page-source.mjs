import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export const publicPages = [
  'index.html',
  'collection.html',
  'finder.html',
  'work.html',
  'condition-guide.html',
  'journal.html',
  'about.html',
];

const root = resolve(import.meta.dirname, '..');
const components = new Map(
  ['site-header', 'site-footer', 'search-dialog'].map(name => [
    name,
    readFileSync(resolve(root, 'components', name + '.html'), 'utf8').trimEnd(),
  ]),
);

export function readPageSource(page) {
  if (!publicPages.includes(page)) throw new Error('Unknown KIOKU page: ' + page);

  return readFileSync(resolve(root, 'pages', page), 'utf8').replace(
    /^( *)<kioku-include name="([a-z-]+)"><\/kioku-include>$/gm,
    (_, indent, name) => {
      const component = components.get(name);
      if (!component) throw new Error('Unknown KIOKU component: ' + name);
      let html = component;
      if (name === 'site-header') {
        html = html.replace('{{header-logo}}', page === 'index.html' ? '-light' : '');
        html = html.replace('<a href="./' + page + '">', '<a href="./' + page + '" aria-current="page">');
      }
      return html.split('\n').map(line => indent + line).join('\n');
    },
  );
}
