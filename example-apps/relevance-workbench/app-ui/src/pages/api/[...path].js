import httpProxy from 'http-proxy';

const API_URL = process.env.NEXT_API_URL || "http://localhost:5000";

const proxy = httpProxy.createProxyServer();

export const config = {
  api: {
    bodyParser: false,
  },
}

// eslint-disable-next-line import/no-anonymous-default-export
export default (req, res) => {
  return new Promise((resolve, reject) => {
    proxy.once("error", reject);
    proxy.web(req, res, { 
      target: API_URL, 
      changeOrigin: true 
    }, (err) => {
      if (err) {
        console.error(err);
        reject(err);
      }

      resolve();
    });
  });
};