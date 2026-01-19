# 🎬 Movie Pitch Generator Backend

A FastAPI backend that uses popular LLMs to generate creative movie pitches from random genre, character, location, and filmmaker combinations.

## ✨ Features

- **AI-Powered Pitches** - Generates unique movie titles, taglines, and plot summaries using LLMs
- **Structured Output** - Uses Pydantic AI for reliable, typed responses
- **Rate Limited** - Protects against abuse (10 requests/minute per IP)
- **Input Validated** - Prevents prompt injection and excessive input sizes
- **CORS Configured** - Secure cross-origin request handling

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework
- **[Pydantic AI](https://ai.pydantic.dev/)** - Type-safe AI agent framework
- **[OpenAI API](https://openai.com/)** - Language model for generation (Can use other LLMs with Pydantic AI)
- **[SlowAPI](https://github.com/laurentS/slowapi)** - Rate limiting middleware

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/movie-pitch-backend.git
cd movie-pitch-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API (or preferred LLM) key
```

### Running the Server

```bash
python main.py
```

The API will be available at `http://127.0.0.1:8000`

## 📡 API Reference

### Generate Movie Pitch

**POST** `/generate-pitch`

Generate a movie pitch from input parameters.

**Request Body:**
```json
{
  "characters": ["Robot", "Detective"],
  "locations": ["Tokyo", "Space Station"],
  "genres": ["Noir", "Sci-Fi"],
  "creatives": ["Ridley Scott", "Studio Ghibli"]
}
```

**Response:**
```json
{
  "title": "Neon Shadows",
  "tagline": "In space, every shadow hides a secret.",
  "pitch": "A retired android detective is pulled back into service when a murder aboard a Tokyo-styled space station reveals a conspiracy that threatens both human and machine alike."
}
```

**Validation Rules:**
- Each list must have 1-5 items
- Each item must be 1-100 characters
- No empty or whitespace-only items

### Health Check

**GET** `/health`

Returns `{"status": "healthy"}` when the server is running.

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI (or preferred LLM) API key | *Required* |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:3000,http://127.0.0.1:3000` |
| `HOST` | Server bind address | `127.0.0.1` |
| `PORT` | Server port | `8000` |

## 🍓 Raspberry Pi Deployment

This section covers deploying the backend on a Raspberry Pi running Raspbian, alongside a portfolio website and frontend.

### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ (Raspbian Bullseye+ includes Python 3.9)
sudo apt install python3 python3-pip python3-venv git -y
```

### Installation on Pi

```bash
# Clone to your preferred location
cd /home/pi
git clone https://github.com/yourusername/movie-pitch-backend.git
cd movie-pitch-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OpenAI API key and configure ALLOWED_ORIGINS
```

### Configure for LAN Access

Edit your `.env` to allow connections from other devices on your network:

```env
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://raspberrypi.local:3000
```

> **Note:** Replace `raspberrypi.local` with your Pi's actual hostname or IP address.

### Create Systemd Service

Create a service file to run the backend automatically on boot:

```bash
sudo nano /etc/systemd/system/movie-backend.service
```

Add the following content:

```ini
[Unit]
Description=Movie Pitch Generator Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/movie-pitch-backend
Environment=PATH=/home/pi/movie-pitch-backend/venv/bin
ExecStart=/home/pi/movie-pitch-backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable movie-backend
sudo systemctl start movie-backend

# Check status
sudo systemctl status movie-backend

# View logs
sudo journalctl -u movie-backend -f
```

### Firewall Configuration (Optional)

If you have UFW enabled:

```bash
sudo ufw allow 8000/tcp
```

### Nginx Reverse Proxy (Optional)

If you want to serve the backend through Nginx (useful for SSL or unified domain):

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/movie-backend
```

Add:

```nginx
server {
    listen 80;
    server_name api.yourdomain.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/movie-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
