# Use the specified Python image as the base
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Copy the application files
COPY . .

# Download and install 'uv'
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod 755 /install.sh && /install.sh && echo "uv installation completed"

# Add 'uv' to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies using 'uv' (pyproject.toml is already in the root)
RUN uv pip install --system .

# Set environment variable if needed (e.g., for .env loading libraries like dotenv)
ENV PYTHONUNBUFFERED=1

#port
EXPOSE 4000
# Run the main application
CMD ["python", "main.py"]
