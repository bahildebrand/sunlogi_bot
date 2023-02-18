FROM python:3.11.2-slim-buster

RUN apt update && apt install -y libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /sunbot
COPY . /sunbot
COPY pyproject.toml /sunbot
WORKDIR /sunbot
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

ENTRYPOINT [ "poetry", "run", "sunbot" ]