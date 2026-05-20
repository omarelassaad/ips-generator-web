# pull official base image
FROM python:3.12-slim-trixie

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

# Install gnupg2 first, then add Microsoft repo 
# Install ODBC Driver 18 
RUN apt-get update \ 
  && apt-get install -y gnupg2 curl ca-certificates \ 
  && update-ca-certificates \ 
  && curl -fsSL --insecure https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.asc \ 
  && gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg /tmp/microsoft.asc \ 
  && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \ 
  && echo 'Acquire::https::Verify-Peer "false";' >> /etc/apt/apt.conf.d/99insecure \ 
  && echo 'Acquire::https::Verify-Host "false";' >> /etc/apt/apt.conf.d/99insecure \ 
  && apt-get update \ 
  && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 mssql-tools18 unixodbc-dev \ 
  && rm /etc/apt/apt.conf.d/99insecure \ 
  && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bash_profile \ 
  && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc 




# install GTK3
RUN echo "Installing GTK3 binaries"
RUN apt-get -qq -y install libgtk-3-0

# install dependencies
RUN pip install --upgrade pip
COPY ./app/requirements.txt .
RUN pip install -r requirements.txt

# Create a non-root user under which to run
RUN useradd --user-group --system --create-home --no-log-init app

# copy project
COPY ./app .
COPY .env /usr/src/app/ips_generator/.env

RUN chown app /usr/src/app/ -R
RUN chmod +x /usr/src/app/start.sh

# Run as user
USER app

# Entrypoint: start.sh
ENTRYPOINT ["/bin/sh", "-c", "/usr/src/app/start.sh"]