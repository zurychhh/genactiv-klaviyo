FROM node:18-slim

# Install Python and uv (required for Klaviyo MCP)
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package runner — required for Klaviyo MCP)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Python MCP packages
RUN pip3 install --break-system-packages meta-ads-mcp analytics-mcp

WORKDIR /app

# Google Ads MCP (Python venv with dependencies)
COPY google-ads-mcp/google-ads-mcp-server/requirements.txt ./google-ads-mcp/google-ads-mcp-server/
RUN python3 -m venv google-ads-mcp/google-ads-mcp-server/venv && \
    google-ads-mcp/google-ads-mcp-server/venv/bin/pip install --no-cache-dir \
    -r google-ads-mcp/google-ads-mcp-server/requirements.txt
COPY google-ads-mcp/google-ads-mcp-server/ ./google-ads-mcp/google-ads-mcp-server/

# Shopify Extended MCP (build TypeScript)
COPY shopify-mcp-extended/package*.json ./shopify-mcp-extended/
RUN cd shopify-mcp-extended && npm ci
COPY shopify-mcp-extended/ ./shopify-mcp-extended/
RUN cd shopify-mcp-extended && npm run build
RUN cd shopify-mcp-extended && npm prune --production

# Main application
COPY genactiv-online/package*.json ./genactiv-online/
RUN cd genactiv-online && npm ci --production
COPY genactiv-online/ ./genactiv-online/

WORKDIR /app/genactiv-online

EXPOSE 3000

CMD ["node", "server/index.js"]
