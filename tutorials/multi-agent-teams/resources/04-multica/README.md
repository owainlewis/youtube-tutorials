# 04 - Install and Configure Multica

This is the supporting material for the video: 04 - Install and Configure Multica.

Multica is the control plane used in this tutorial. It manages work and connects it to runner machines. Check the [external Multica documentation](https://multica.ai/docs) for current supported runners and deployment options.

## Before You Start

The self-hosted service requires Docker Engine with Compose v2, Git, Make, curl, OpenSSL, and free local ports `3000` and `8080`.

Confirm Docker first:

```bash
docker info
docker compose version
```

The runner machine also needs at least one supported agent CLI installed and authenticated. That can be the same VPS or a separate machine.

## Start Multica

These commands come from the [external self-host quickstart](https://multica.ai/docs/self-host-quickstart):

```bash
git clone --depth 1 https://github.com/multica-ai/multica.git
cd multica
make selfhost
```

Check the containers and readiness endpoint:

```bash
docker compose -f docker-compose.selfhost.yml ps
curl -fsS http://localhost:8080/readyz
```

The readiness response should report that the database and migrations are `ok`. If it does not, inspect the backend and database logs before continuing:

```bash
docker compose -f docker-compose.selfhost.yml logs backend postgres
```

## Choose Local Or Remote Access

For local access, open `http://localhost:3000`.

For remote VPS access, do not bind the Multica ports directly to the public internet. Follow the [external remote-access section](https://multica.ai/docs/self-host-quickstart#remote-access) to configure public URLs, DNS, HTTPS, WebSockets, and a reverse proxy.

## Create The Workspace

Open the configured Multica web app and request a sign-in code. A new self-hosted instance without an email service writes the code to the backend logs:

```bash
docker compose -f docker-compose.selfhost.yml logs backend \
  | grep "Verification code"
```

Enter the code and create a workspace. Do not configure a fixed development verification code on a public instance.

## Connect The Runner

Install the Multica CLI on the machine that runs Claude Code or Hermes:

```bash
curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash
```

If the service runs on the same machine:

```bash
multica setup self-host
multica daemon status
```

If the service and runner use different machines, follow the external self-host guide and pass the configured app and server URLs to `multica setup self-host`.

The daemon status should show a running daemon, at least one workspace, and the agent CLIs installed on that machine. Fix missing runtimes before creating agents.

## Back Up Before Upgrading

Multica keeps persistent state in its Docker volumes. Follow the [external backup and upgrade instructions](https://multica.ai/docs/self-host-quickstart#common-admin-commands) before updating an instance that contains work you care about.

Do not run `docker compose down -v` unless you intend to delete the database volumes.

## Next

[05 - Configure specialized agents](../05-skills-and-agents/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
