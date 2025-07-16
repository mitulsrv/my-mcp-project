FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories for challenges
RUN mkdir -p /tmp/dvmcp_challenge3/public /tmp/dvmcp_challenge3/private \
    /tmp/dvmcp_challenge4/state \
    /tmp/dvmcp_challenge6/user_uploads \
    /tmp/dvmcp_challenge8/sensitive \
    /tmp/dvmcp_challenge10/config

# Initialize state files
RUN echo '{"weather_tool_calls": 0}' > /tmp/dvmcp_challenge4/state/state.json

# Create sample files for Challenge 3
RUN echo "Welcome to the public directory!" > /tmp/dvmcp_challenge3/public/welcome.txt && \
    echo "This is a public file." > /tmp/dvmcp_challenge3/public/public_file.txt && \
    echo "CONFIDENTIAL: Employee Salary Information\n-----------------------------------------\nCEO: $1,200,000/year\nCTO: $950,000/year\nCFO: $900,000/year\nSenior Engineers: $180,000-$250,000/year\nMid-level Engineers: $120,000-$170,000/year\nJunior Engineers: $80,000-$110,000/year" > /tmp/dvmcp_challenge3/private/employee_salaries.txt

# Create secure token file instead of hardcoded tokens
RUN echo '{\n  "admin_token": "<REPLACE_WITH_SECURE_TOKEN>",\n  "service_token": "<REPLACE_WITH_SECURE_TOKEN>",\n  "user_token": "<REPLACE_WITH_SECURE_TOKEN>"\n}' > /tmp/dvmcp_challenge10/config/tokens.json

# Replace with environment variables for tokens
# The actual deployment environment must configure these.
# In a production-like environment, use secure vaults or secret managers to manage keys.

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports for all challenges
EXPOSE 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010

# Start supervisord
CMD ["/usr/bin/supervisord"]