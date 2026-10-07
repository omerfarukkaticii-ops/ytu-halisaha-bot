FROM python:3.11-slim

# Chrome için gerekli sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome kurulumu
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY bot.py .
COPY hedef.json .

# Chrome'un headless modda ve sandbox olmadan çalışması için
ENV DISPLAY=:99

CMD ["python", "bot.py"]
