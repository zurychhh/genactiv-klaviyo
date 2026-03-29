FROM node:18-slim

# Install Python and uv (required for Klaviyo MCP)
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package runner — required for Klaviyo MCP)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install meta-ads-mcp (Python package)
RUN pip3 install --break-system-packages meta-ads-mcp

WORKDIR /app

# Shopify Extended MCP (build it)
COPY shopify-mcp-extended/package*.json ./shopify-mcp-extended/
RUN cd shopify-mcp-extended && npm ci --production
COPY shopify-mcp-extended/ ./shopify-mcp-extended/
RUN cd shopify-mcp-extended && npm run build

# Main application
COPY genactiv-online/package*.json ./genactiv-online/
RUN cd genactiv-online && npm ci --production
COPY genactiv-online/ ./genactiv-online/

WORKDIR /app/genactiv-online

EXPOSE 3000

CMD ["node", "server/index.js"]
