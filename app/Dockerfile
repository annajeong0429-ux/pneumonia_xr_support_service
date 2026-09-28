FROM python:3.13-slim

# uv 바이너리를 공식 이미지에서 그대로 복사 (pip install보다 빠르고 가벼움)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 정의 파일만 먼저 복사해서 별도 레이어로 캐싱
# -> pyproject.toml/uv.lock이 안 바뀌면 소스 코드만 바뀌어도 이 레이어는 재사용됨
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 나머지 소스 코드 복사 후 프로젝트 자체를 설치
COPY . .
RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

