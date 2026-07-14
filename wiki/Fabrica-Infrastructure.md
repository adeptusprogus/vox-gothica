# Fabrica (Infrastructure)

**Fabricae** are infrastructure manifests that transpile to **Terraform JSON**.

```vg
AVE OMNISSIAH.
FABRICA "servitores".

FOEDUS "aws" {
    regio = "us-east-1"
}

EXSTRUATUR servitor "alpha" {
    genus = "aws_instance"
    imago = "ami-0c55b159cbfafe1f0"
    magnitudo = "t3.micro"
}
```

## Key keywords

| Keyword | Role |
|---------|------|
| `FOEDUS` | Provider configuration |
| `SEDES` | State backend |
| `EXSTRUATUR` | Resource declaration |
| `SCRUTOR` | Data source |
| `POSTULO` | Input variable |
| `PROFITEOR` | Output value |
| `ARCANUM` | Sensitive marker |

## Workflow

```bash
# Emit JSON for review / GitOps
gothica scribe-solum fabrica.vg

# Plan
gothica auguro fabrica.vg

# Apply (interactive FIAT confirmation)
gothica consecro fabrica.vg

# Destroy (EXTERMINATUS confirmation, no skip)
gothica exterminatus fabrica.vg
```

## POSTULO values

Supply at consecration time:
```bash
gothica consecro fabrica.vg -postulatum regio=us-west-2
# or
export GOTHICA_POSTULATUM_REGIO=us-west-2
```

## Docker image

The repo includes a Docker image with `gothica` + `terraform`:

```bash
docker build -t vox-gothica vox-gothica/
docker run --rm -v "$PWD:/opus" -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
  vox-gothica consecro /opus/fabrica.vg --fiat
```

## Rules

- `EXSTRUATUR` in a CANTICUM is **heresy** (`fabrica_in_cantico`)
- Imperative code runs **before** Terraform sees anything
- Terraform receives only static JSON
- Deferred references (`servitor.id`) compile to `${...}` template strings

Full spec: [Fabrica (Ch. X)](https://adeptusprogus.github.io/vox-gothica/10-fabrica.html)
