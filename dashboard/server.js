import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicDir = path.join(path.dirname(fileURLToPath(import.meta.url)), 'public');
const reportPath = path.join(root, 'source-data', 'impact-summary.json');
const port = Number(process.env.PORT || 3000);

const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
};

function safeAssetPath(urlPath) {
  const requested = urlPath === '/' ? '/index.html' : urlPath;
  const resolved = path.resolve(publicDir, `.${requested}`);
  return resolved.startsWith(publicDir) ? resolved : null;
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.url === '/api/report') {
      const data = await readFile(reportPath, 'utf8');
      res.writeHead(200, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
      res.end(data);
      return;
    }

    const assetPath = safeAssetPath(new URL(req.url, 'http://localhost').pathname);
    if (!assetPath) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }
    const body = await readFile(assetPath);
    const type = contentTypes[path.extname(assetPath)] || 'application/octet-stream';
    res.writeHead(200, { 'content-type': type, 'cache-control': 'no-cache' });
    res.end(body);
  } catch (error) {
    if (error.code === 'ENOENT') {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    console.error(error);
    res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
    res.end('Internal server error');
  }
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  server.listen(port, '0.0.0.0', () => {
    console.log(`Black Tech Week impact dashboard listening on http://0.0.0.0:${port}`);
  });
}

export { server, safeAssetPath };
