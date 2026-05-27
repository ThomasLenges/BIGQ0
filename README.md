# UNO Q development in VS Code - Commands

Use the following commands to manage apps on the Arduino UNO Q from the Linux terminal.

## Connect through SSH to terminal (see IP address on AppLab > Settings (at the very bottom)

```bash
ssh arduino@192.168.1.251
```
172.20.10.4

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
arduino-app-cli app start ~/Thomas/apps/YourAppName
```

## Stop an app

```bash
arduino-app-cli app stop ~/Thomas/apps/YourAppName
```

## Get python logs

```bash
arduino-app-cli app logs ~/Thomas/apps/YourAppName
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
in YourAppName/python/ add a file called "requirements.txt"
```
May need to clear cache if changed requirements.txt

```bash
rm -rf ~/Thomas/apps/YourAppName/.cache
```

## EdgeImpulse
```bash
Once a model is ready to install on the board => AppLab => Bricks => Object Detection (Example) => AI models and click on install
```

```bash
Once back on VSC. Add: EI_OBJ_DETECTION_MODEL: /home/arduino/.arduino-bricks/models/custom-ei/ei-model-1003932-3/model.eim under - id: arduino:video_object_detection
  model_configuration:. Otherwise, it fully bugs the system into picking a default legacy model!
```

```bash
Go to Object Detection on EI to visualize all key metrics
```

## Trouble shooting tips

1. Do not forget to update `app.yaml` with the brick configuration and `sketch.yaml` with the required MCU libraries.
