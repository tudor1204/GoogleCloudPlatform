#!/usr/bin/env python3

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.10-alpine

ARG PORT=8050
ENV PORT=${PORT}

WORKDIR /app

COPY requirements.txt /app
COPY src/ /app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD exec gunicorn wsgi:server --bind "0.0.0.0:${PORT}"

EXPOSE ${PORT}
