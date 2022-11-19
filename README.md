# Luminance

Pull/Push tracker for gitea instances.

## Requirements

Python 3.10+, pip, gitea instance running on the same machine.
Gitea should also have [access logs enabled](https://docs.gitea.io/en-us/logging-configuration/#the-access-logger).

## Installation

1. Clone the repository and cd into it

```bash
https://github.com/SuperSlumberParty/Luminance; cd Luminance
```
2. [OPTIONAL] Create a virtual environment for Luminance and activate it
```bash
python -m venv virtualenv;source virtualenv/bin/activate
```
3. Install required dependencies

```bash
python -m pip install -r requirements.txt
```

4. Edit `conf.ini.example` and save as `conf.ini`.

## Configuation
Located in `conf.ini.example`, should be saved as `conf.ini`

| Category | Key | Type | Description |
|---|---|---|---|
| GITEA | URL | string | Gitea's instance URL |
| GITEA | AcessLog | string | Gitea's access.log absolute path |
| DISCORD | WebhookURL | string | Discord Webhook URL for logging |
| REPOSITORY | RelativeUrl | bool | Show event notifications for 'UserOrg/RepositoryName' only. |
| REPOSITORY | UserOrg | string | Show event notifications for this organisation or user only |
| REPOSITORY | RepositoryName | string | Show event notifications for this repository name only |

## Usage

Start `app.py`
```bash
python app.py
```

