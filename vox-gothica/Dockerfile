# Vox Gothica — fabrica execution image.
# Build:   docker build -t vox-gothica .
# Plan:    docker run --rm -v "$PWD:/opus" vox-gothica auguro /opus/fabrica.vg
# Apply:   docker run --rm -it -v "$PWD:/opus" -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
#              vox-gothica consecro /opus/fabrica.vg --fiat

# --- stage 1: borrow the terraform binary from the official image ---
FROM hashicorp/terraform:1.9 AS terraformum

# --- stage 2: slim python runtime ---
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="Vox Gothica" \
      org.opencontainers.image.description="High Gothic language toolchain + terraform, for consecrating fabricae" \
      org.opencontainers.image.licenses="MIT"

COPY --from=terraformum /bin/terraform /usr/local/bin/terraform

# git: required by many terraform providers/modules; openssh for git+ssh litaniae
RUN apk add --no-cache git openssh-client ca-certificates

WORKDIR /srv/gothica
COPY pyproject.toml README.md ./
COPY gothica ./gothica
RUN pip install --no-cache-dir . && rm -rf /root/.cache

# unprivileged servitor
RUN adduser -D -h /opus servitor
USER servitor
WORKDIR /opus

ENTRYPOINT ["gothica"]
CMD ["versio"]
