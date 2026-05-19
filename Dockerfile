FROM python:3.12-slim

WORKDIR /app

COPY setup.py setup.cfg MANIFEST.in README.md LICENSE ./
COPY phply/ phply/
COPY tests/ tests/
COPY tools/ tools/

RUN pip install --no-cache-dir -e ".[test]"

RUN python -c "from phply.phpparse import make_parser; make_parser()"

RUN pytest tests/ -q

ENTRYPOINT ["phply8"]
CMD ["--help"]
