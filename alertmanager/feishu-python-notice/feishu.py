import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, urllib.request
import logging
from logging import basicConfig
basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S', stream=sys.stdout)

WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/a2407264-7ceb-454e-aca0-60fa5d502ac6"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))

        alerts = body.get('alerts', [])
        logging.info(alerts)
        lines = []
        for a in alerts:
            labels = a.get('labels', {})
            ann = a.get('annotations', {})
            lines.append(f"告警: {labels.get('alertname')}")
            lines.append(f"级别: {labels.get('severity')}")
            lines.append(f"实例: {labels.get('instance')}")
            lines.append(f"描述: {ann.get('description', ann.get('summary', ''))}")
            lines.append("---")

        text = "Prometheus 告警\n" + "\n".join(lines)
        feishu_body = json.dumps({
            "msg_type": "text",
            "content": {"text": text}
        }).encode()

        req = urllib.request.Request(WEBHOOK, data=feishu_body,
                                     headers={'Content-Type': 'application/json'})
        try:
            resp = urllib.request.urlopen(req).read()
            print("Feishu response:", resp.decode(), flush=True)
        except Exception as e:
            print("Feishu error:", e, flush=True)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')


HTTPServer(('0.0.0.0', 8060), Handler).serve_forever()
