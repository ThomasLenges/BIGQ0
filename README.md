# UNO Q development in VS Code - Commands

Use the following commands to manage apps on the Arduino UNO Q from the Linux terminal.

## Connect through SSH to terminal (see IP address on AppLab > Settings (at the very bottom)

```bash
ssh arduino@192.168.1.251
```

or

```bash
ssh arduino@172.20.10.4
```

## Connect through SSH to VSC (see IP address on AppLab > Settings (at the very bottom)

```bash
CTRL+SHIFT+P > Remote-SSH: Open SSH Configuration File... > /.ssh/config > HostName PutYourUNOQIPAddress
```

## List available apps

```bash
arduino-app-cli app list
```

## Start an app

```bash
arduino-app-cli app start ~/Thomas/apps/helloworld
```

## Stop an app

```bash
arduino-app-cli app stop ~/Thomas/apps/helloworld
```

## Get python logs

```bash
arduino-app-cli app logs ~/Thomas/apps/helloworld
```

## Docker

### List containers
```bash
docker ps -a
```
`-a` affiche tous les conteneurs, y compris ceux qui sont arrêtés.

### Start a container
```bash
docker start 
```

### Run a Python script in a container
```bash
docker exec  python main.py
```
## Import Python libraries
```bash
in AppName/python/ add a file called "requirements.txt"
```

## Trouble shooting tips

1. Do not forget to update `app.yaml` with the brick configuration and `sketch.yaml` with the required MCU libraries.
