# Use Microsoft's official Playwright image (includes the heavy browser binaries)
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Set up the working directory inside the container
ARG FUNCTION_DIR="/var/task"
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}

# Copy your code and the requirements file into the container
COPY . ${FUNCTION_DIR}

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Tell AWS Lambda how to execute the code
ENTRYPOINT [ "/usr/bin/python", "-m", "awslambdaric" ]
CMD [ "main.lambda_handler" ]