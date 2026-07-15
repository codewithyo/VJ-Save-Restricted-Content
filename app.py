from flask import Flask, Response

app = Flask(__name__)


HOME_PAGE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>HR Save Restricted Bot</title>
    <style>
        :root {
            --bg: #07111f;
            --bg2: #0d1b2a;
            --card: rgba(12, 22, 38, 0.82);
            --border: rgba(255, 255, 255, 0.10);
            --text: #eef4ff;
            --muted: #aebad0;
            --accent: #7dd3fc;
            --accent2: #34d399;
            --warn: #f59e0b;
        }

        * { box-sizing: border-box; }
        html, body {
            margin: 0;
            min-height: 100%;
            background:
                radial-gradient(circle at top left, rgba(125, 211, 252, 0.16), transparent 28%),
                radial-gradient(circle at bottom right, rgba(52, 211, 153, 0.14), transparent 24%),
                linear-gradient(160deg, var(--bg), var(--bg2));
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .wrap {
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 32px 18px;
        }

        .hero {
            width: min(980px, 100%);
            border: 1px solid var(--border);
            border-radius: 28px;
            background: linear-gradient(180deg, rgba(16, 28, 49, 0.88), rgba(9, 17, 31, 0.92));
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
            overflow: hidden;
            position: relative;
        }

        .hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(125, 211, 252, 0.08), transparent 45%, rgba(52, 211, 153, 0.06));
            pointer-events: none;
        }

        .content {
            position: relative;
            padding: 40px;
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 28px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(125, 211, 252, 0.12);
            color: var(--accent);
            font-size: 13px;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            border: 1px solid rgba(125, 211, 252, 0.18);
        }

        h1 {
            margin: 18px 0 14px;
            font-size: clamp(2.4rem, 5vw, 4.8rem);
            line-height: 0.98;
            letter-spacing: -0.05em;
        }

        .lede {
            margin: 0;
            max-width: 62ch;
            color: var(--muted);
            font-size: 1.03rem;
            line-height: 1.7;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 26px;
        }

        .card {
            padding: 16px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .card h2 {
            margin: 0 0 8px;
            font-size: 0.95rem;
            color: #fff;
        }

        .card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
            font-size: 0.95rem;
        }

        .panel {
            display: grid;
            gap: 14px;
            align-content: start;
        }

        .status {
            padding: 18px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .status-label {
            color: var(--muted);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }

        .status-value {
            font-size: 1.5rem;
            margin: 0;
            font-weight: 700;
        }

        .status-sub {
            margin: 8px 0 0;
            color: var(--muted);
            line-height: 1.6;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.09);
            color: var(--text);
            font-size: 0.9rem;
        }

        .pill strong { color: var(--accent2); }

        .footer {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            padding: 0 40px 34px;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .footer a {
            color: var(--accent);
            text-decoration: none;
        }

        @media (max-width: 860px) {
            .content { grid-template-columns: 1fr; padding: 28px; }
            .grid { grid-template-columns: 1fr; }
            .footer { padding: 0 28px 26px; }
        }
    </style>
</head>
<body>
    <main class="wrap">
        <section class="hero" aria-label="HR Save Restricted Bot landing page">
            <div class="content">
                <div>
                    <div class="badge">Telegram Media Saver</div>
                    <h1>Save restricted content with a cleaner, faster experience.</h1>
                    <p class="lede">
                        HR Save Restricted Bot fetches supported Telegram media by post link, keeps the workflow asynchronous,
                        and now includes silent log-channel backups for successful deliveries.
                    </p>

                    <div class="grid" aria-label="Feature highlights">
                        <div class="card">
                            <h2>Private and public links</h2>
                            <p>Handles public posts, private chats, and bot posts with the same input flow.</p>
                        </div>
                        <div class="card">
                            <h2>Media backup</h2>
                            <p>Successful media can be mirrored to a configured log channel without interrupting the user.</p>
                        </div>
                        <div class="card">
                            <h2>Session-based login</h2>
                            <p>Supports string-session login for restricted content access and safer account handling.</p>
                        </div>
                        <div class="card">
                            <h2>Low-friction deployment</h2>
                            <p>Works cleanly with the existing bot worker and keeps the web process lightweight.</p>
                        </div>
                    </div>
                </div>

                <aside class="panel">
                    <div class="status">
                        <div class="status-label">Service Status</div>
                        <p class="status-value">Running</p>
                        <p class="status-sub">If this page loads, the web service is up and the deployment is responding normally.</p>
                    </div>

                    <div class="status">
                        <div class="status-label">Supported Media</div>
                        <div class="pill-row">
                            <span class="pill"><strong>Video</strong></span>
                            <span class="pill"><strong>Photo</strong></span>
                            <span class="pill"><strong>Document</strong></span>
                            <span class="pill"><strong>Audio</strong></span>
                            <span class="pill"><strong>Voice</strong></span>
                            <span class="pill"><strong>GIF</strong></span>
                            <span class="pill"><strong>Sticker</strong></span>
                            <span class="pill"><strong>Video Note</strong></span>
                        </div>
                    </div>

                    <div class="status">
                        <div class="status-label">Primary Commands</div>
                        <p class="status-sub">/start, /help, /login, /logout, /cancel, /broadcast</p>
                    </div>
                </aside>
            </div>

            <div class="footer">
                <span>HR Save Restricted Bot</span>
                <span><a href="https://youtube.com/@Tech_VJ" target="_blank" rel="noreferrer">Tech VJ YouTube</a></span>
            </div>
        </section>
    </main>
</body>
</html>"""


@app.route("/")
def home():
        return Response(HOME_PAGE, mimetype="text/html")


@app.route("/health")
def health():
        return {"status": "ok"}


if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8080)
