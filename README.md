# minknow_exporter

## Description

Metrics exporter from Oxford Nanopore sequencer. Exported metrics include: pore states, voltage, temperature, etc.

## Getting Started

### Dependencies

* Golang
* Python3

### Compiling

To build the exporter you should clone the repository, enter to specified dir and compile the project:
```
git clone https://github.com/wkusmirek/minknow_exporter.git
cd minknow_exporter
make
```

### Executing program

To run the exporter on the default port, run compiled binary app:
```
cd minknow_exporter
./minknow_exporter
```
To check if exporter is running properly, please curl the port in the another terminal:
```
curl localhost:9309/metrics
```
Note that MinKNOW software must be launching to see the metrics on the console screen.

### Executing program via docker

To run the exporter without building the binaries, you can use docker image:
```
docker pull wkusmirek/minknow-exporter:latest
```

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the Apache License 2.0 License - see the LICENSE file for details
