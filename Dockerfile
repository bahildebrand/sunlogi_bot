FROM python:3.11.2-slim-buster

RUN apt update && apt install -y libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /sunbot
ADD pyproject.toml /sunbot/pyproject.toml
ADD poetry.lock /sunbot/poetry.lock
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
ADD . /sunbot

ENTRYPOINT [ "poetry", "run", "sunbot" ]