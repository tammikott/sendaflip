FROM python:3.9-slim

# Loo mitte-root kasutaja
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Kopeeri requirements esmalt
COPY --chown=appuser:appuser requirements.txt .

# Installi sõltuvused
RUN pip install --no-cache-dir -r requirements.txt

# Kopeeri rakenduse failid
COPY --chown=appuser:appuser . .

# Loo demo fail
RUN touch demo_critical.txt && \
    echo "Demo fail konteineris" > demo_critical.txt && \
    chown appuser:appuser demo_critical.txt

# Vaheta kasutajat
USER appuser

# Ava port
EXPOSE 5000

# Käivita rakendus
CMD ["python", "app.py"]
